# HRXP - calculates PCI and SAXS images for an XFEL beamline
#
# © Copyright 2022 by Thomas Kluge (t.kluge@hzdr.de)
#
# This file is part of HRXP, the Hibef ReLaX XFEL Propagator.
#
# HRXP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# HRXP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HRXP.  If not, see <http://www.gnu.org/licenses/>.

#includes
###notebook
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, pi
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from scipy.ndimage import affine_transform
from scipy import interpolate
from scipy.ndimage import measurements
from scipy.fftpack import fftshift
from scipy.fftpack import ifftshift
from scipy.fftpack import fftfreq
from scipy.ndimage import shift
import pprint as pp
pprint = pp.PrettyPrinter(indent=4).pprint
parallel = 1

if parallel>1:
    from scipy.fft import fft2 as sc_fft2
    def fft2(x,workers=parallel):
        return sc_fft2(x,workers=workers)
    from scipy.fft import ifft2 as sc_ifft2
    def ifft2(x,workers=parallel):
        return sc_ifft2(x,workers=workers)
else:
    from scipy.fftpack import fft2
    from scipy.fftpack import ifft2

import scipy as sc
from PIL import Image
from scipy.ndimage import rotate
from tqdm import tqdm
from multiprocess import Pool
from scipy import signal
from scipy.ndimage.filters import gaussian_filter
import torch
import torchvision.transforms as T
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from torch.cuda import nvtx
import torchaudio as TA

import sys
sys.path.insert(1, '/home/thiess94/pytorch-optical-diffraction/')
from propagatorsv1 import Propagate



#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#full size jupyter notebook
from IPython.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))

#colored print
from IPython.core.display import display
from IPython.display import HTML as html_print
def cstr(s, color='black', bg="white", weight="normal"):
    return ("<table width=100% style='padding:0'><tr  align='left' style='padding:0;text-align:left;font-weight:{};color:{};background-color:{}'><td align='left' style='padding:0;text-align:left'>{}</td></tr></table>".format(weight,color,bg, s))
def hprint(s,color="black", bg="white", weight="normal"):
    if bg != "white": s="&nbsp;"+s
    return display(html_print(cstr(s, color=color,bg=bg, weight=weight)))

def get_fwhm_width(data):
    fwhm_min = data.shape[0]-np.max((data > np.max(data)/2).astype(float)*np.arange(data.shape[0])[::-1])
    fwhm_max = np.max((data > np.max(data)/2).astype(float)*np.arange(data.shape[0]))
    return fwhm_min, fwhm_max
class control:
    def __init__(self):
        self.list_wire_lineouts_voxel = []
        self.list_wire_lineouts_beamplane = []
        self.list_wire_lineouts_SAXS = []
        self.list_wire_lineouts_infield = []
        self.total_intensity_exit_wave = []
        self.list_transmission = []
c = control()
def oddify(x):
    return 2*int(x/2)+1
    
m = 1e9 # meter in units of base unit (nm)
um=1e3 # micron
mm=1e6 #milimeter
cm=1e7 #cm
nm=1. # base unit for length nanometer
keV=1 # base unit for energy
eV=1e-3
 
def blackman_harris_window(n, a0 = 0.35875, a1 = 0.48829, a2 = 0.14128, a3 = 0.01168):
    x = torch.arange(n).to(device)
    y = a0 - a1*torch.cos(2*pi*x/n) + a2*torch.cos(4*pi*x/n) - a3*torch.cos(6*pi*x/n)
    return y
# Material classes
class Material():
    def __init__(self,name,mat_mu_nm1,mat_mu_nm2,mat_dens,mat_ZA,re=2.818e-6,Na=602.2,verbose="False"):
        self._name=name
        self._re = re  # classical electron radius in nm
        self._Na = Na # Avogadro constant
        self._mat_mu_nm1 = mat_mu_nm1 # mu nm scattering coeff
        self._mat_mu_nm2 = mat_mu_nm2   # mu nm absorption coeff
        self._mat_dens = mat_dens #g/cm3
        self._mat_ZA = mat_ZA  # Z/A
    
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def get_n_refraction_delta(self,photonEnergy=8.2):
        """calculate the Thomson scattering cross-section"""
        #self._set_n_refraction_delta(photonEnergy)
        # the factor 0.933386 below comes from correction to Henke data 
        return 0.933386*self._Na * self._mat_dens * self._mat_ZA * self._re * (2. * np.pi / (2.0e0 * np.pi / (1.239842 / photonEnergy))**2)
        #self._n_refraction_delta
    
    def set_n_refraction_delta(self,photonEnergy=None):
        """store value in class atribute"""
        # Thomson scattering
        self._n_refraction_delta = self.get_n_refraction_delta(photonEnergy=photonEnergy)
        #self._n_refraction_delta = self._Na * self._mat_dens * self._mat_ZA * self._re * (2. * np.pi / (2.0e0 * np.pi / (1.239842 / photonEnergy))**2)
        
    def get_n_refraction_beta(self,photonEnergy=8.2):
        # absorption
        #self._set_n_refraction_beta(photonEnergy=photonEnergy)
        #return self._n_refraction_beta
        return self._mat_mu_nm1 * self._mat_dens/photonEnergy**self._mat_mu_nm2 # 0.5 * self._mat_mu_nm1/photonEnergy**self._mat_mu_nm2 / (2.0e0 * np.pi / (1.239842 / photonEnergy))

    def set_n_refraction_beta(self,photonEnergy=None):
        #self._n_refraction_beta = self._mat_mu_nm1/photonEnergy**self._mat_mu_nm2 # 0.5 * self._mat_mu_nm1/photonEnergy**self._mat_mu_nm2 / (2.0e0 * np.pi / (1.239842 / photonEnergy))        
        self._n_refraction_beta = self.get_n_refraction_beta(photonEnergy=photonEnergy)

    def _get_phase_shift(self,photonEnergy):
        """returns the phase shift when the XFEL propagates through the target"""
        #lambda = 2*pi*c/(E/hbar)=1.239842nm/(E/keV)
        return (2.0e0 * np.pi / (1.239842 / photonEnergy)) * self.get_n_refraction_delta(photonEnergy=photonEnergy)
    def _get_mu(self,photonEnergy):
        """returns the absorption when the XFEL propagates through the target (absorption of FIELD amplitude!!)"""
        mu=self.get_n_refraction_beta(photonEnergy=photonEnergy)*photonEnergy*10
        return mu
        
    def info(self,photonEnergy=8.0):
        print("This is material",self._name)
        print("Density:",self._mat_dens,"g/cm^3")
        print("Z/A:",self._mat_ZA)
        print("Refractive index n = 1 - δ - iβ with δ  =",self.get_n_refraction_delta(photonEnergy=photonEnergy), "and β =",self.get_n_refraction_beta(photonEnergy=photonEnergy)," (at",photonEnergy,"keV)")
        print("Here, δ = Na ρ Z/A re 1.239842^2/(2π (E/keV)^2), β = μ1/(E/keV)^μ2")
        print("μ1 =",self._mat_mu_nm1, " and μ2 =",self._mat_mu_nm2)
        print("μ (1/μm):",self.get_n_refraction_beta(photonEnergy=photonEnergy)*photonEnergy*1e4)
        print("attenuation length (μm):",1/(self.get_n_refraction_beta(photonEnergy=photonEnergy)*photonEnergy*1e4))
        print("https://www.researchgate.net/publication/358444777_Attenuation_Length_and_Penetration_Depth_of_X-rays")
        
class Cu(Material):
    """ this is a sample material class for copper
    it provides material properties such as density, absorption, diffraction coefficients, and the (complex) refractive index"""
    def __init__(self):
        super(Cu,self).__init__(name="copper",
                                mat_mu_nm1 = 0.0001339, #0.014062 # mu nm scattering coeff,
                                mat_mu_nm2 = 3.7, #2.741   # mu nm absorption coeff,
                                mat_dens = 8.96, #g/cm3,
                                mat_ZA = 0.45636
                               )
###################################################################################
# target class
class Target():
    """this is the general target parent class
       it provides target rotation, projection etc."""
    def __init__(self, label, category = None, position = None, voxel_size = None, voxel_number = None, rotation = 0, batch_size = 1, device = "cpu"):
        """ Target parameters """
        self._volumes = []
        self._materials = []
        self.voxel_number   = voxel_number             # target world size in VOXELS (4000 are too many! 256GB ram)
        self.voxel_size  = voxel_size                  # target world voxel size in nm
        self.label = label                             # user has to set a label to be able to identify and delete a target later in the XFEL beam path
        self.batch_size = batch_size
        self.device = device
        self._density1 = None
        
        if category is not False:
            self.set_category(category)                # target category defines how XFEL is propagated to the position of the target. Only reason is to be able to account for spatial increase of beam
        if position is not False:
            self.position = position[2]             # target position relative to XFEL focus in z (nm)
            self.position_xy = position[0:2]
        
        self.rotation=rotation
                
    def help(*args):
        print("Sorry, no help here, yet!")
        
    #save handling of class variables - this is not consistently implemented everywhere, yet.
    def set_category(self,category):
        self._category=category
        
    def get_category(self):
        return self._category

    def get_phase_shift(self,photonEnergy):
        for i,material in enumerate(self._materials):
            dPhase = material._get_phase_shift(photonEnergy) * self._get_projection(self._volumes[i])
            try:
                phase += dPhase
            except:
                phase = dPhase
        return phase

    def get_absorption(self,photonEnergy):
        for i,material in enumerate(self._materials):
            dmu = material._get_mu(photonEnergy) * self._get_projection(self._volumes[i])
            try:
                mu += dmu
            except:
                mu = dmu
        #print(torch.max(mu))
        absorption = torch.exp(-0.5*mu)
        #print("min absorption", torch.min(absorption))
        return absorption
    
    def plot(self):
        """show the density, for diagnostic purposes"""
        absorption = 1-self.get_absorption(photonEnergy=8)
        phase = self.get_phase_shift(photonEnergy=8)

        fig, axs = plt.subplots(2,2,figsize=(6,5), gridspec_kw={'height_ratios': [1, 1]},sharex=True)
        fig.suptitle('Target '+self.label+'\n absorption    |    phase shift')
        x = len(self._density1[0,:])*self.voxel_size/1000
        y = len(self._density1[:,0])*self.voxel_size/1000
        axs[0,0].imshow(absorption, interpolation='none',extent=[-x/2,x/2,-y/2,y/2],aspect='auto')
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,0].set_ylabel("y ($\mu$m)")

        x=np.arange(-len(absorption[0,:])/2,len(absorption[0,:])/2)*self.voxel_size/1000
        axs[1,0].plot(x,absorption[0, int(self.voxel_number[0]/2),:])
        axs[1,0].set_xlabel("x ($\mu$m)")

        x = len(self._density1[0,:])*self.voxel_size/1000
        y = len(self._density1[:,0])*self.voxel_size/1000
        axs[0,1].imshow(phase, interpolation='none',extent=[-x/2,x/2,-y/2,y/2],aspect='auto')
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,1].set_ylabel("y ($\mu$m)")

        x=np.arange(-len(phase[0,:])/2,len(phase[0,:])/2)*self.voxel_size/1000
        axs[1,1].plot(x,phase[int(self.voxel_number[0]/2),:])
        axs[1,1].set_xlabel("x ($\mu$m)")
        plt.tight_layout()
        plt.show()        

# Targets
"""The target class is a child of target class and defines the specific target geometry, projection, material composition etc.
   It can also be a multi-material object."""
class wire(Target):
    """This is a sample class demonstrating the usage. We define a cylindrical wire with one material."""
    def __init__(self,label,radius=None,material=None,position=None,voxel_size=None,voxel_number=None, rotation=0, sigma = 0, use_erf = True, batch_size = 1, wire_pixels = None, device = "cpu"):
        
            
        self._material1 = material()
        self.radius1_nm = radius           # wire radiuses
        self.sigma_left_nm = abs(sigma[0])
        self.sigma_right_nm = abs(sigma[1])
        self.use_erf = use_erf
        self.wire_pixels = wire_pixels
        super().__init__(label, position = position, voxel_size = voxel_size, voxel_number = voxel_number, rotation = rotation, batch_size = batch_size, device = device)
        
        """Note: for compound targets, you can build more volumes and materials and register them below."""
        self._materials.append(self._material1)   # important! define a material for this volume!
        self._volumes.append(self._build_volume1)
    
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")
        
    def _build_volume1(self):
        
        def circular_mask(h, w, center=None, radius=None):
            if center is None: # use the middle of the image
                center = (int(w/2), int(h/2))
            if radius is None: # use the smallest distance between the center and image walls
                radius = min(center[0], center[1], w-center[0], h-center[1])

            #Y, X = np.ogrid[:h, :w]
            Y, X = torch.meshgrid(torch.arange(h), torch.arange(w))
            Y, X = Y.to(self.device), X.to(self.device)
            X = X.unsqueeze(0).repeat(self.batch_size, 1, 1)
            Y = Y.unsqueeze(0).repeat(self.batch_size, 1, 1)
            
            dist_from_center = ((X - center[0])**2 + (Y-center[1])**2)

            mask = (dist_from_center <= radius**2).float()
            
            if self._sigmaPixel:
                if self.use_erf:
                    mask = -0.5 * (torch.erf((torch.sqrt((X-center[0])**2+(Y-center[1])**2) - radius) / (sqrt(2) * abs(self._sigmaPixel))) ) + 0.5
                
                else:
                    ksize = oddify(self._sigmaPixel.item()*8)
                    ksize = max(ksize, 3)
                    
                    x, y = torch.meshgrid(torch.arange(ksize), torch.arange(ksize))
                    x = x.to(self.device)*1.0
                    y = y.to(self.device)*1.0
                    kernel = torch.exp(-0.5 * ((x - ksize/2 + 0.5)**2 + (y - ksize/2 + 0.5)**2)/(self._sigmaPixel**2))
                    kernel = kernel/torch.sum(kernel)
                    mask = F.conv2d(mask.unsqueeze(0).unsqueeze(0), kernel.unsqueeze(0).unsqueeze(0), padding = "same")[0,0]
                
            return mask

        self._sigmaPixel = self.sigma_nm / self.voxel_size
        self._radiusPixel = self.radius1_nm / self.voxel_size
        self._pos_y_pixel = self.position_xy[1]/self.voxel_size
        self._pos_x_pixel = self.position_xy[0]/self.voxel_size
        #print(self._pos_x_pixel, self._pos_y_pixel)
        mask = circular_mask(self.voxel_number_y, self.voxel_number_w, center = (self.voxel_number[1]/2 + self._pos_y_pixel,self.voxel_number[0]/2), radius=self._radiusPixel)

        """ Target volume is the 3D representation of the target
            1st index is x axis, 2nd index is y and 3rd index is y """
        volume = torch.zeros((self.voxel_number[0], self.voxel_number[1], self.voxel_number_y)).to(self.device)
        
        for i in range(0, self.voxel_number):
            volume[i] = mask
        
        return volume
    def _build_projection(self):
        self._sigmaPixel = self.sigma_nm / self.voxel_size
        self._radiusPixel = self.radius1_nm / self.voxel_size
        self._pos_y_pixel = self.position_xy[1]/self.voxel_size
        #self._pos_x_pixel = self.position_xy[0]/self.voxel_size
        
        center = self.voxel_number_y/2 + self._pos_y_pixel
        
        #print(self._sigmaPixel, self._radiusPixel, self._pos_y_pixel)
        
        w, h = self.voxel_number[0], self.voxel_number[1]
        Y, X = torch.meshgrid(torch.arange(h), torch.arange(w))
        Y, X = Y.to(self.device), X.to(self.device)
        
        
        pos_0 = (self._radiusPixel**2 - (X - center)**2 == 0)
        #plt.imshow(pos_0.detach().cpu())
        #plt.show()
        #pos_0 = torch.flatten(pos_0)
        
        projection_tmp0 = torch.sqrt(self._radiusPixel**2 - (X - center)**2)
        projection_tmp0 = torch.nan_to_num(projection_tmp0, nan = -1)
        projection_tmp0 = (projection_tmp0+1)*(1-pos_0.float())-1
        
        y_calc = X[projection_tmp0 != -1]
        projection_tmp1 = torch.sqrt(self._radiusPixel**2 - (y_calc - center)**2)
        projection_tmp1 = torch.nan_to_num(projection_tmp1, nan = -1)
        
        projection = torch.zeros(self.voxel_number[0] * self.voxel_number[1]).to(self.device)
        projection_tmp0 = torch.flatten(projection_tmp0)
        
        projection[projection_tmp0 != -1] = projection_tmp1
        
        projection = projection.view(self.voxel_number[0], self.voxel_number[1])
        #projection[pos_0] = projection[pos_0].data
        
        #this will return nan gradients
        #projection = torch.sqrt(self._radiusPixel**2 - (X - (self.voxel_number/2 + self._pos_y_pixel))**2)
        #projection = torch.nan_to_num(projection, nan = 0)
        #plt.plot(projection[100].detach().cpu())
        #plt.show()
        if self._sigmaPixel:
            if self.use_erf:
                projection = -0.5 * (torch.erf(torch.sqrt(self._radiusPixel**2 - (X-center[0])**2)) / (sqrt(2) * self._sigmaPixel))+ 0.5
            else:
                ksize = oddify(self._sigmaPixel.item()*8)
                ksize = max(ksize, 3)
                x, y = torch.meshgrid(torch.arange(ksize), torch.arange(ksize))
                x = x.to(self.device)*1.0
                y = y.to(self.device)*1.0
                kernel = torch.exp(-0.5 * ((x - ksize/2 + 0.5)**2 + (y - ksize/2 + 0.5)**2)/(self._sigmaPixel**2))
                kernel = kernel/torch.sum(kernel)
                projection = F.conv2d(projection.unsqueeze(0).unsqueeze(0), kernel.unsqueeze(0).unsqueeze(0), padding = "same")[0,0]
        #plt.plot(projection[100].detach().cpu())
        #plt.show()
        return projection
    def _build_projection1(self, direct_projection = True):
        self._sigmaPixel_left = self.sigma_left_nm / self.voxel_size
        self._sigmaPixel_right = self.sigma_right_nm / self.voxel_size
        
        
        
        def circular_mask(h, w, center, radius):
            h_arange = torch.arange(h, device = self.device)
            w_arange = torch.arange(w, device = self.device)
            Y, X = torch.meshgrid(h_arange, w_arange)
            X = X.unsqueeze(0).repeat(self.batch_size, 1, 1)
            Y = Y.unsqueeze(0).repeat(self.batch_size, 1, 1)
            
            
        
            
            if direct_projection:
                nvtx.range_push("init mask and _calc")
                
                mask_tmp = (self._radiusPixel[:, 0, :])**2 - (X[:, 0, :] - center[1][:, 0, :]+ 1e-9)**2

                mask_negative = (mask_tmp > 0).detach()
                X_calc = X[:, 0, :][mask_negative]
                radius_calc = self._radiusPixel[:, 0, :][mask_negative]
                center_calc = center[1][:, 0, :][mask_negative]
                mask_calc = (radius_calc)**2 - (X_calc - center_calc+ 1e-9)**2
                mask_calc = torch.sqrt(mask_calc)*2

                mask = torch.zeros(mask_tmp.shape).to(self.device)

                mask[mask_negative] = mask_calc

                ksize = oddify(max(torch.max(self._sigmaPixel_left), torch.max(self._sigmaPixel_right))*6)

                ksize = max(ksize, 3)

                x = torch.arange(ksize, device = self.device)
                x = x.unsqueeze(0).repeat(self._sigmaPixel_left.shape[0], 1)
                nvtx.range_pop()
                
                nvtx.range_push("init kernel and mask (left)")
                
                sigmaPixel_left_tmp = self._sigmaPixel_left.unsqueeze(-1).repeat(1, ksize)
                kernel_left = torch.exp(-0.5 * ((x - ksize/2 + 0.5)**2)/(sigmaPixel_left_tmp**2))

                kernel_left = kernel_left/torch.sum(kernel_left, dim = -1).unsqueeze(-1).repeat(1, kernel_left.shape[1])

                mask_left = torch.empty(mask.shape, device = self.device)
                nvtx.range_pop()
                
                nvtx.range_push("loop of conv1d (left)")
                for i in range(mask.shape[0]):
                    mask_left[i] = F.conv1d(mask[i].unsqueeze(0).unsqueeze(0), kernel_left[i].unsqueeze(0).unsqueeze(0), padding = "same")[:, 0]
                # best way would be torchaudio.transforms.Convolve, but version 0.11.0 of torchaudio doesn't have that. It would need an upgrade of pytorch
                nvtx.range_pop()
                
                nvtx.range_push("init kernel and mask (right)")
                
                sigmaPixel_right_tmp = self._sigmaPixel_right.unsqueeze(-1).repeat(1, ksize)
                kernel_right = torch.exp(-0.5 * ((x - ksize/2 + 0.5)**2)/(sigmaPixel_right_tmp**2))

                kernel_right = kernel_right/torch.sum(kernel_right, dim = -1).unsqueeze(-1).repeat(1, kernel_right.shape[1])
                mask_right = torch.empty(mask.shape, device = self.device)
                nvtx.range_pop()
                
                nvtx.range_push("loop of conv1d (right)")
                
                for i in range(mask.shape[0]):

                    mask_right[i] = F.conv1d(mask[i].unsqueeze(0).unsqueeze(0), kernel_right[i].unsqueeze(0).unsqueeze(0), padding = "same")[:, 0]
                
                nvtx.range_pop()
                
                nvtx.range_push("calc final mask")
                filter_right = (X[:, 0, :] > center[1][:, 0, :]).float()
                mask = mask_left * (1 - filter_right) + mask_right * filter_right
                nvtx.range_pop()
                
                #plt.plot(mask[0].cpu().detach())
                #plt.plot((filter_right[0] * torch.max(mask)).cpu().detach())
                #plt.show()
                
            elif self.use_erf:
                print("we use erf")
                #tmp_mask = -0.5 * (torch.erf((torch.sqrt((X-center[0])**2+(Y-center[1])**2) - radius) / (sqrt(2) * self._sigmaPixel)) ) + 0.5
                #print(X.shape, center[1].shape, radius.shape)
                pos_0 = ((X-center[0])**2+(Y-center[1])**2 - radius != 0)
                #print("count nonzero", torch.count_nonzero(pos_0.float()), pos_0.shape)
                
                new_grid = torch.zeros(X.shape) +0.5
                new_grid = new_grid.to(self.device)
                #print(X.shape, pos_0.shape, center[1].shape, radius.shape)
                x_calc = X[pos_0]
                y_calc = Y[pos_0]
                #print(y_calc.shape)
                center2 = center[1][pos_0]
                radius2 = radius[pos_0]
                sigma2 = sigma[pos_0]
                new_mask = -0.5 * (torch.erf((torch.sqrt((x_calc-center[0])**2+(y_calc-torch.flatten(center2))**2+1e-9) - torch.flatten(radius2)) / (sqrt(2) * torch.flatten(sigma2))) ) + 0.5
                #print("!",x_calc.shape, torch.count_nonzero((x_calc-center[0])**2+(y_calc-center[1])**2- radius) )

                new_grid = torch.flatten(new_grid)
                pos_0 = torch.flatten(pos_0)
                new_grid[pos_0] = new_mask
                mask = new_grid.view(self.batch_size, self.voxel_number[0], self.voxel_number[1])
                mask = -0.5 * (torch.erf((torch.sqrt((X-center[0])**2+(Y-center[1])**2 + 1e-9) - radius) / (sqrt(2) * sigma)) ) + 0.5
                
            else:


                dist_from_center = (X - center[0])**2 + (Y-center[1])**2
                mask = (dist_from_center <= radius**2).float()

                ksize = oddify(self._sigmaPixel.item()*8)

                ksize = max(ksize, 3)

                x, y = torch.meshgrid(torch.arange(ksize), torch.arange(ksize))
                x = x.to(self.device)*1.0
                y = y.to(self.device)*1.0
                kernel = torch.exp(-0.5 * ((x - ksize/2 + 0.5)**2 + (y - ksize/2 + 0.5)**2)/(self._sigmaPixel**2))
                kernel = kernel/torch.sum(kernel)

                mask = F.conv2d(mask.unsqueeze(0).unsqueeze(0), kernel.unsqueeze(0).unsqueeze(0), padding = "same")[0,0]
            
            return mask
        self._radiusPixel = self.radius1_nm / self.voxel_size
        self._pos_y_pixel = self.position_xy[1]/self.voxel_size
        self._pos_x_pixel = self.position_xy[0]/self.voxel_size
        
        self._radiusPixel = self._radiusPixel.unsqueeze(-1).unsqueeze(-1).repeat(1, self.voxel_number[0], self.voxel_number[1])
        self._pos_y_pixel = self._pos_y_pixel.unsqueeze(-1).unsqueeze(-1).repeat(1, self.voxel_number[0], self.voxel_number[1])
        
        mask = circular_mask(self.voxel_number[0], self.voxel_number[1], center = (self.voxel_number[0]/2,self.voxel_number[1]/2 + self._pos_y_pixel), radius=self._radiusPixel)
        if not direct_projection:
            mask = torch.sum(mask, dim = -1)
        
        projection = mask.unsqueeze(1).repeat(1, self.voxel_number[0], 1)
        #del sigma
        del mask
        del self._radiusPixel
        del self._pos_y_pixel
        del self._pos_x_pixel
        del self._sigmaPixel_left
        del self._sigmaPixel_right
        return projection
    def _get_projection(self, volume = None):
        """calculates density/material_density*depth(nm)"""

        """1. project the volume density to 2D, in XFEL propagation direction"""
        #volume = self._build_volume1()   ## The _build_volume has to be defined in the child class!

        """2.project along the z direction"""
        #projection = torch.sum(volume, dim = 2) * self.voxel_size   # The VOXELS contain the density, we need to multiply by the voxel length to account for their size
        
        """3. now rotate to match the XFEL direction (the angle is transverse to XFEL direction; longitudinal angle not yet implemented)"""
        #projection = TF.rotate(projection.unsqueeze(0).unsqueeze(0),angle=self.rotation)[0, 0]

        #shift(projection,torch.tensor(self.position_xy)/self.voxel_size,projection_s, cval=0)       
        #self._density1 = projection_s
        #xy = (torch.tensor(self.position_xy)/self.voxel_size).int()
        #dx, dy = xy
        #self._density1 = torch.roll(projection, (dx, dy), dims = (0, 1))
        if self._density1 is None:
            if self.wire_pixels is None:
                self._density1 = self._build_projection1()*self.voxel_size**1

                #print("density sum",torch.sum(_density1, dim = -1))
            else:
                self._density1 = self.wire_pixels
        
        #self._density1 = self._build_projection()*self.voxel_size*2
        
        #plt.imshow(projection.detach().cpu())
        #plt.colorbar()
        #plt.show()
        #
        #plt.imshow(self._density1.detach().cpu())
        #plt.colorbar()
        #plt.show()
        #
        #plt.imshow(self._density1.detach().cpu() - projection.detach().cpu())
        #plt.colorbar()
        #plt.show()
        
        #if dx >= 0:
        #    self._density1[:dx] = 0
        #else:
        #    self._density1[-dx:] = 0
        #
        #if dy >= 0:
        #    self._density1[:, :dy] = 0
        #else:
        #    self._density1[:, -dy:] = 0
        return self._density1        

#class grating(_target):
#class double_grating(_target):

########################################################################################################
# XFEL classes                
class XFEL():
    def __init__(self,
                 pixel_number=None, 
                 pixel_size=None,
                 photon_energy = 8.15*keV,
                 photon_energy_bandwidth = 0.,
                 photon_energy_bandwidth_sample_width = 0.,
                 batch_size = 1,
                 detail_plot = False,
                 spot_shift = None,
                 beam_noise_level = None,
                 device = "cpu"
                ):
        self.batch_size = batch_size
        self.detail_plot = detail_plot
        self._category = ""
        # Express the field as cos(phi) + i*sin(phi)
        self.realPart = []
        self.imagPart = []
                
        # Express the field as A * exp(i*phi)
        self.amplitude = []
        self.phase = []
        
        self._pixel_number = None
        self._pixel_size = None
        self.spot_shift = spot_shift
        self.beam_noise_level = beam_noise_level
        
        self._photon_energy=photon_energy
        self._photon_energy_bandwidth = photon_energy_bandwidth
        self._photon_energy_bandwidth_sample_width = photon_energy_bandwidth_sample_width
        
        self.propagator_name = "lorentz"
        self.device = device
        
        if pixel_number != None:
            self.set_pixel_number(pixel_number)
        if pixel_size != None:
            self.set_pixel_size(pixel_size)
                           
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")
            
    def set_pixel_number(self,pixel_number):
        self._pixel_number = pixel_number
        
        if self._pixel_size is not None:
            self._define_image_scale()

    def set_pixel_size(self,pixel_size):
        self._pixel_size = pixel_size
        if self._pixel_number is not None:
            self._define_image_scale()

    def set_parameters(self,parameters):
        self._parameters=parameters

    def set_parameters(self,parameters):
        self._parameters=parameters
        
    def get_k(self,photon_energy=None,Lambda=None):
        if Lambda is None:
            if photon_energy is None:
                photon_energy=self.get_photon_energy()
            return 5.06773076 * photon_energy
        else:
            2*np.pi/Lambda

    def get_lambda(self, k=None, photon_energy=None):
        if photon_energy is None:
            photon_energy = self.get_photon_energy() 
        if k is None:
            k = self.get_k(photon_energy=photon_energy) 
        return (2*np.pi)/k

    def get_photon_energy(self):
        return self._photon_energy
    
    def get_field(self):
        return self._realPart,self._imagPart
        
        
    def _define_image_scale(self,reset=True, pixel_number=None, pixel_size=None):
        if pixel_number is None:
            pixel_number=self._pixel_number
        if pixel_size is None:
            pixel_size=self._pixel_size
        #xaxis = np.arange(-self._pixel_number/2,self._pixel_number/2) * self._pixel_size
        xaxis = torch.arange(-pixel_number[0]/2,pixel_number[0]/2) * pixel_size
        yaxis = torch.arange(-pixel_number[1]/2,pixel_number[1]/2) * pixel_size
        x, y = torch.meshgrid(xaxis, yaxis)
        x, y = x.to(self.device), y.to(self.device)
        
        x = x.unsqueeze(0).repeat(self.batch_size, 1, 1)
        y = y.unsqueeze(0).repeat(self.batch_size, 1, 1)
        
        if reset:
            self._x = x
            self._y = y
            self._pixel_number=pixel_number
            self._pixel_size=pixel_size
        return x , y
        
    #def get_field(self):
    #    return self._realPart, self._imagPart

    def plot(self):
        try:
            self.get_axis()
        except:
            print("No new axis")
        realPart, imagPart = self.get_field()

        fig, axs = plt.subplots(2,2,figsize=(14,9), gridspec_kw={'height_ratios': [3, 1]},sharex=True)
        fig.suptitle('XFEL field')
        x=self._pixel_number*self._pixel_size/1000
        extent = [-x/2, x/2, -x/2, x/2]
        x=np.arange(-self._pixel_number/2,self._pixel_number/2)*self._pixel_size/1000

        axs[0,0].set_title("real part")
        axs[0,0].imshow(realPart,extent=extent,aspect="auto")
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,0].set_ylabel("y ($\mu$m)")

        axs[1,0].plot(x,realPart[int(len(realPart)/2),:],label="along x (center)")
        axs[1,0].plot(x,realPart[:,int(len(realPart)/2)],label="along y (center)")
        axs[1,0].set_xlabel("x ($\mu$m)")
          
        axs[0,1].set_title("imaginary part")
        axs[0,1].imshow(imagPart,extent=extent,aspect="auto")
        #axs[0].xlabel("x ($\mu$m)")
        #axs[0,1].set_ylabel("y ($\mu$m)")

        axs[1,1].plot(x,imagPart[int(len(realPart)/2),:],label="along x (center)")
        axs[1,1].plot(x,imagPart[:,int(len(realPart)/2)],label="along y (center)")
        axs[1,1].set_xlabel("x ($\mu$m)")
        plt.legend()
            

        fig, axs = plt.subplots(2,2,figsize=(14,9), gridspec_kw={'height_ratios': [3, 1]},sharex=True)
        fig.suptitle('XFEL')
        x=self._pixel_number*self._pixel_size/1000
        extent = [-x/2, x/2, -x/2, x/2]
        x=np.arange(-self._pixel_number/2,self._pixel_number/2)*self._pixel_size/1000

        I=realPart**2+imagPart**2
        axs[0,0].set_title("intensity")
        
        
        if self._category == "SAXS":
            vmin,vmax = np.min(I[int(len(realPart)/2),:]),np.max(I[int(len(realPart)/2),:])
            from matplotlib.colors import LogNorm
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            im = axs[0,0].imshow(I,norm=LogNorm(vmin=vmin,vmax=vmax),extent=extent,aspect="auto",cmap=plt.cm.inferno)

            divider = make_axes_locatable(axs[0,0])
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical')        
        else:
            axs[0,0].imshow(I,extent=extent,aspect="auto",cmap=plt.cm.inferno)
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,0].set_ylabel("y ($\mu$m)")

        if self._category == "SAXS":
            axs[1,0].semilogy(x,I[int(len(realPart)/2),:],label="along x (center)")
            axs[1,0].set_ylim([vmin,vmax])
        else:
            axs[1,0].plot(x,I[int(len(realPart)/2),:],label="along x (center)")
        axs[1,0].plot(x,I[:,int(len(realPart)/2)],label="along y (center)")
        axs[1,0].set_xlabel("x or y ($\mu$m)")
        
        phase = np.arctan2(imagPart,realPart)
        #phase = np.arctan(imagPart/realPart)
        #phase[phase<0]+=np.pi
#        phase[phase>np.pi/2]-=np.pi/2
        axs[0,1].set_title("phase")
        axs[0,1].imshow(phase,extent=extent,aspect="auto",cmap=plt.cm.RdYlBu)
        #axs[0].xlabel("x ($\mu$m)")
        #axs[0,1].set_ylabel("y ($\mu$m)")

        axs[1,1].plot(x,phase[int(len(realPart)/2),:],label="along x (center)")
        axs[1,1].plot(x,phase[:,int(len(realPart)/2)],label="along y (center)")
        axs[1,1].set_xlabel("x or y ($\mu$m)")
        #plt.legend()

        try:
            fig, axs = plt.subplots(2,1,figsize=(7,9), gridspec_kw={'height_ratios': [3, 1]},sharex=True)
            fig.suptitle('XFEL color dispersion')
            x=self._pixel_number*self._pixel_size/1000
            extent = [-x/2, x/2, -x/2, x/2]
            x=np.arange(-self._pixel_number/2,self._pixel_number/2)*self._pixel_size/1000
            I_rgb = self._rgb
            I_rgb = I_rgb/np.max(I_rgb)*255.9999999
            axs[0].imshow(I_rgb.astype(np.uint8),aspect="auto",extent=extent)
        
            def channelSplit(image):
                return np.dsplit(image,image.shape[-1])

            [R,G,B]=channelSplit(I_rgb)

            axs[1].plot(x,B[int(len(realPart)/2),:],color='blue')
            axs[1].plot(x,G[int(len(realPart)/2),:],color='green')
            axs[1].plot(x,R[int(len(realPart)/2),:],color='red')
            axs[1].set_xlabel("x ($\mu$m)")
        except:
            None
        plt.tight_layout()
        plt.show()
        
    """Interpolate the target grid onto the XFEL grid as defined by its pixel number and size"""
    def _interpolate_target2beam(self,target_projection,target):
        #coarseX = np.arange(-target.voxel_number/2,target.voxel_number/2) * target.voxel_size
        #coarseY = np.arange(-target.voxel_number/2,target.voxel_number/2) * target.voxel_size
        #coarseXX, coarseYY = np.meshgrid(coarseY, coarseY)
        #interp = interpolate.interp2d(coarseX, coarseY, target_projection)
        #
        #fineX = np.arange(-self._pixel_number/2,self._pixel_number/2) * self._pixel_size
        #fineY = np.arange(-self._pixel_number/2,self._pixel_number/2) * self._pixel_size
        #fineProjection = interp(fineX, fineY)
        
        pixel_stretch = target.voxel_size/self._pixel_size
        new_pixel_number_x = self._pixel_number[0]#int(round(target.voxel_number[0] * pixel_stretch, 0))
        new_pixel_number_y = self._pixel_number[1]#int(round(target.voxel_number[1] * pixel_stretch, 0))
        interpolated = T.Resize((new_pixel_number_x, new_pixel_number_y))(target_projection.unsqueeze(1))[:, 0]
        diff_edge_x = int((new_pixel_number_x - self._pixel_number[0])/2)
        diff_edge_y = int((new_pixel_number_y - self._pixel_number[1] )/2)
        rest_x = (new_pixel_number_x - self._pixel_number[0])/2
        rest_y = (new_pixel_number_y - self._pixel_number[1])/2
        
        if diff_edge_x > 0 or diff_edge_y > 0:
            #pixel window is smaller than voxel window, we need to crop
            fineProjection = interpolated[:, diff_edge_x:new_pixel_number_x-diff_edge_x, diff_edge_y:new_pixel_number_y-diff_edge_y]
        else:
            #pixel window is bigger than voxel window, we need to pad
            fineProjection = F.pad(interpolated.unsqueeze(1), (-diff_edge_x, -diff_edge_x, -diff_edge_y, -diff_edge_y), mode = "replicate")[:, 0]
        if self.detail_plot:
            c.list_wire_lineouts_beamplane.append(fineProjection[:, int(fineProjection.shape[1]//2)])
            c.list_wire_lineouts_voxel.append(target_projection[:, int(target_projection.shape[1]//2)])
        return fineProjection
        
    """ Calculate the modified wave at contact position (immediately after the target) """
    def propagate_through_target(self,target,reset=True,field_in=None, photon_energy=None, verbose = 0):
        
        #this takes quite some time, needs to get parallized
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        # Transmission and amplitude
        # with n = 1 - delta + i beta
        # E0 = E * exp(-2*pi/lambda * integral(beta))
        
        transmission = self._interpolate_target2beam(target.get_absorption(photon_energy),target)
        
        if field_in is None:
            beamFieldReal,beamFieldImag = self.get_field()
        else:
            beamFieldReal = field_in.real
            beamFieldImag = field_in.imag
            
        E0 = torch.sqrt(beamFieldReal**2 + beamFieldImag**2)
        
        #I0 = np.load("realistic_beamspot.npy")
        #I0 = torch.from_numpy(I0).unsqueeze(0).repeat(transmission.shape[0], 1, 1).to(self.device).float()
        #E0 = torch.sqrt(I0)
        #E0 = E0/torch.max(E0)
        
        
        #x_axis_um = np.linspace(-self._pixel_number[1]/2 * self._pixel_size * 1e-3, self._pixel_number[1]/2 * self._pixel_size * 1e-3, num = self._pixel_number[1])
        #m1, m2 = get_fwhm_width(torch.sum(I0[0], dim = 0).cpu().detach().numpy())
        #print((m2 - m1)*self._pixel_size)
        
        #plt.plot(transmission.cpu().detach()[0, 0])
        transmitted_E0 = E0 * transmission
        transmitted_I = transmitted_E0**2

        #c.list_transmission.append((torch.sum(transmitted_E0**2, dim = (-1, -2)).detach()/torch.sum(E0**2, dim = (-1, -2)).detach()).cpu().numpy())
        
        # Phase shift
        
        beamPhase = torch.angle(beamFieldReal + beamFieldImag*complex(0,1))
        #beamPhase = beamPhase * 0
        #beamPhase[:, :, int(self._pixel_number[1]/2):] = torch.randn(beamPhase[:, :, int(self._pixel_number[1]/2):].shape).to(device)*0.000*np.pi + beamPhase[:, :, int(self._pixel_number[1]/2):]
        #beamPhase = np.array(Image.open("SAXS_IncidentPhase.tif"))
        
        #beamPhase = torch.randn(beamPhase.shape).to(device)*0.01*np.pi + beamPhase
        
        dPhi = self._interpolate_target2beam(target.get_phase_shift(photon_energy),target)
        beamPhase = beamPhase - dPhi
        
        if verbose > 0:
            
            fig, (ax1, ax2) = plt.subplots(figsize=[6,3], ncols = 2)
            ax1.set_title("transmitted intensity")
            
            im1 = ax1.imshow(transmitted_I[0].detach().cpu(), cmap = "inferno")
            divider = make_axes_locatable(ax1)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im1, cax=cax, orientation='vertical')
        
            ax2.set_title("transmitted phase")
            im2 = ax2.imshow(beamPhase[0].detach().cpu(), cmap = "inferno")
            divider = make_axes_locatable(ax2)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im2, cax=cax, orientation='vertical')
            plt.tight_layout()
            plt.show()
            
            plt.plot(transmitted_I[0, int(transmitted_I.shape[0]/2)].detach().cpu())
            plt.show()
            
            plt.plot(beamPhase.detach(F).cpu()[0, int(transmitted_I.shape[0]/2)].detach().cpu())
            plt.show()
        # Construct the wave at contact
        wave_real = torch.cos(beamPhase)
        wave_imag = torch.sin(beamPhase)
        wave_at_contact = transmitted_E0 * (wave_real + complex(0,1) * wave_imag)

        if reset:
            self._realPart = transmitted_E0 * wave_real
            self._imagPart = transmitted_E0 * wave_imag
        return wave_at_contact
    def set_propagator(self, name):
        self.propagator_name = name
    def propagate_to(self,targets,position=None,detector=None, verbose = 0):
        def propagate_one_energy(photon_energy):
            if photon_energy < self._photon_energy: 
                reset = True
            else:
                reset = False
            if targets is not None:
                first_target_position = targets[0].position
                if position < first_target_position:
                    # we just need to propagate through vacuum
                    field = self.initialize_to_position(position, photon_energy=photon_energy)
                    
                else:
                    #loop through all targets and then to the detector
                    for k_, target in enumerate(targets):
                        target_position = target.position
                        if (target_position < position):
                            if k_ == 0:
                                #propagate to first position:
                                field = self.initialize_to_position(target_position, photon_energy=photon_energy, reset=reset)
                                XFEL_position = target_position
                            else:
                                #propagate to next target
                                
                                field = self.spectral_propagate_to_position(position = target_position - XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                                XFEL_position = target_position
                            #propagate through target
                            field = self.propagate_through_target(target,field_in = field, photon_energy = photon_energy, reset = reset, verbose = verbose)
                    #now we are behind the last target
                    if self.propagator_name == "spectral":
                        field = self.spectral_propagate_to_position(position = position - XFEL_position, photon_energy = photon_energy, field_in = field)
                    elif self.propagator_name == "lorentz":
                        field = self.lorentz_propagate_to_position(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                        if verbose > 0:
                            hprint("Sorry, due to the detector type 'SAXS', bandwidth not taken into account in propagation from last target to detector!",color="white",bg="#FF9999")
                    elif self.propagator_name == "fraunhofer":
                        new_propagator = Propagate(pixel_size = self._pixel_size, pixel_number = self._pixel_number, backend = torch)
                        field = new_propagator.fraunhofer(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                    elif self.propagator_name == "rs_spectral":
                        new_propagator = Propagate(pixel_size = self._pixel_size, pixel_number = self._pixel_number, backend = torch)
                        field = new_propagator.rs_spectral(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                    elif self.propagator_name == "fresnel_spectral":
                        new_propagator = Propagate(pixel_size = self._pixel_size, pixel_number = self._pixel_number, backend = torch)
                        field = new_propagator.fresnel_spectral(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                    elif self.propagator_name == "fresnel_onestep":
                        new_propagator = Propagate(pixel_size = self._pixel_size, pixel_number = self._pixel_number, backend = torch)
                        field = new_propagator.fresnel_onestep(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                    elif self.propagator_name == "fresnel_twostep":
                        new_propagator = Propagate(pixel_size = self._pixel_size, pixel_number = self._pixel_number, backend = torch)
                        field = new_propagator.fresnel_twostep(position = position-XFEL_position, photon_energy = photon_energy, field_in = field, reset = reset)
                    else:
                        print("propagator",self.propagator_name,"is not implemented")
            else:
                field = self.initialize_to_position(position, photon_energy=photon_energy, reset=reset)
            
            return field
        
        FWHM = self._photon_energy_bandwidth
        dE = self._photon_energy_bandwidth_sample_width
        
        if detector is not None:
            position = detector.position
            if  detector.get_category() != "PCI":
                dE = 0

        if dE < FWHM*4 and dE>0:
            energies = np.arange(-2*FWHM,2*FWHM,dE) + dE/2 + self._photon_energy
            energy_profile = 0.5**(2*(energies-self._photon_energy)**2/FWHM**2)        
        else:
            energies=np.asarray([self._photon_energy])
            energy_profile = [1]

        max_pool = np.max([len(energies),parallel])
        if max_pool > 1:
            with Pool(max_pool) as p:
                pool_outputs = list(
                    tqdm(
                        p.imap(propagate_one_energy,
                               energies),
                        total=len(energies)
                    )
                )
        else:
            pool_outputs=[]
            for photon_energy in energies:
                pool_outputs.append(propagate_one_energy(photon_energy))

        for i__,photon_energy in enumerate(energies):
            if len(energies) > 1:                
                r_ratio = np.max([1-2*i__/(len(energies)-1),0])
                g_ratio = np.max([(1-np.abs(2*i__/(len(energies)-1)-1)),0])*0.6
                b_ratio = np.max([i__/(len(energies)-1)*2-1,0])
                ratio=r_ratio+g_ratio+b_ratio
                r_ratio/=ratio
                g_ratio/=ratio
                b_ratio/=ratio
            else:
                r_ratio=1./3
                g_ratio=1./3
                b_ratio=1./3
            
            E_new = pool_outputs[i__] * energy_profile[i__]
            
            if i__ > 0:
                E_new_tot += E_new
                E_r += E_new * r_ratio 
                E_g += E_new * g_ratio 
                E_b += E_new * b_ratio
            else:
                E_new_tot = E_new
                E_r = E_new * r_ratio
                E_g = E_new * g_ratio
                E_b = E_new * b_ratio
        E_r_tmp = torch.abs(E_r)**2#/torch.max(torch.abs(E_r)**2, dim = -1, keepdim = True)[0]
        E_g_tmp = torch.abs(E_g)**2#/torch.max(torch.abs(E_g)**2, dim = -1, keepdim = True)[0]
        E_b_tmp = torch.abs(E_b)**2#/torch.max(torch.abs(E_b)**2, dim = -1, keepdim = True)[0]
        rgb = torch.stack((E_r_tmp, E_g_tmp, E_b_tmp), dim = -1)
        self._rgb = rgb
        self._realPart = E_new_tot.real
        self._imagPart = E_new_tot.imag

        if detector is not None:
            detector.set_raw_data(E_new, self._x, self._y, self._pixel_size, self._pixel_number, rgb=rgb)

        return E_new_tot, rgb

    
    def spectral_propagate_to_position(self, position=None, field_in=None, photon_energy=None, has_evanescent = False):
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        #plt.plot(torch.abs(field_in[0, 1].cpu().detach()))
        #plt.show()
        Z=position
        j=complex(0,1)
        old_pixel_size = self._pixel_size
        old_pixel_number = self._pixel_number
        if field_in is None:
            field_in = self._realPart + j*self._imagPart
        E_new = field_in*0

        Lambda = self.get_lambda(photon_energy = photon_energy)
        k=self.get_k(photon_energy = photon_energy)

        # compute angular spectrum
        fft_c = torch.fft.fft2(field_in)
        c = torch.fft.fftshift(fft_c, dim = (-2, -1))

        kx = 2*np.pi*torch.fft.fftshift(torch.fft.fftfreq(old_pixel_number[0], d = old_pixel_size), dim = -1)
        ky = 2*np.pi*torch.fft.fftshift(torch.fft.fftfreq(old_pixel_number[1], d = old_pixel_size), dim = -1) # *1/d
        kx, ky = torch.meshgrid(kx, ky)
        kx = kx.to(self.device)
        ky = ky.to(self.device)
        
        argument = (2 * np.pi / Lambda) ** 2 - kx ** 2 - ky ** 2
        
        #Calculate the propagating and the evanescent (complex) modes
        
        tmp = torch.sqrt(torch.abs(argument))
        choose = (argument >= 0).float()
        if has_evanescent:
            kz = choose * tmp + (1-choose) * j * tmp
        else:
            kz = choose * tmp + (1-choose) * (-1) * tmp
        #kz = torch.where(argument >= 0, tmp, j*tmp)

        # propagate the angular spectrum a distance z
        cc = torch.fft.ifftshift(c * torch.exp(j * kz * Z), dim = (-2, -1))
        E_new = torch.fft.ifft2(cc, dim = (-2, -1))
#        self._realPartSpectralPropagated = E_new_tot.real
#        self._imagPartSpectralPropagated = E_new_tot.imag

        
        
        
        return E_new
            
        
    def lorentz_propagate_to_position(self,position=None,field_in=None,reset=True, photon_energy=None):
        if self.detail_plot:
            c.list_wire_lineouts_infield.append(field_in[:, int(field_in.shape[1]//2)])
        c.total_intensity_exit_wave += torch.sum(torch.abs(field_in[:, int(field_in.shape[1]//2)])**2, dim = -1).cpu().detach().numpy().tolist()
        
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        if field_in is None:
            field_in = self._realPart + j*self._imagPart
        # Fresnel diffraction propagator
        # calculate E field at position X, Y, Z=position, where X, Y are on the old coordinates x, y or those defined by new pixel_number and pixel_size
        # E(X,Y,Z) = Eqn. 13
        Lambda = self.get_lambda()
        k=self.get_k()
        Z=position
        j=complex(0,1)
        old_pixel_size = self._pixel_size
        old_pixel_number = self._pixel_number
        new_pixel_size = Z * 2 * np.pi/(k*old_pixel_number[1]*old_pixel_size)  
        
        E = field_in
        signal = E* torch.exp(j*(k/(2*Z)*(self._x**2 + self._y**2)))
        E = torch.fft.fft2(signal)
        
        X,Y = self._define_image_scale(pixel_size=new_pixel_size,reset=reset)
        R = np.exp(j*k*Z)/(j*Lambda*Z) * torch.exp(j * k / ( 2 * Z ) * ( X**2 + Y**2 ) )
        E = R * torch.fft.fftshift(E, dim = (-2, -1))
        #E = torch.fft.fftshift(torch.fft.fft2(field_in, dim = (-2, -1)), dim = (-2, -1))
        #self._realPartLorentzPropagated = E.real
        #self._imagPartLorentzPropagated = E.imag
        if self.detail_plot:
            c.list_wire_lineouts_SAXS.append(E[:, int(field_in.shape[1]//2)])
        if reset:
            self._realPart = E.real
            self._imagPart = E.imag
        return E

class gaussian_XFEL(XFEL):
    def __init__(self,
                 waist=None,
                 pixel_number=None, 
                 pixel_size=None,
                 photon_energy = 8.15*keV,
                 photon_energy_bandwidth = 0.,
                 photon_energy_bandwidth_sample_width = 0.,
                 batch_size = 1,
                 detail_plot = False,
                 spot_shift = None,
                 beam_noise_level = None,
                 device = "cpu"
                ):
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size,photon_energy=photon_energy,photon_energy_bandwidth=photon_energy_bandwidth,photon_energy_bandwidth_sample_width=photon_energy_bandwidth_sample_width, batch_size = batch_size, detail_plot = detail_plot, spot_shift = spot_shift, beam_noise_level = beam_noise_level, device = device)
        
        if waist is not None:
            self.set_waist(waist)
                            
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")
                          
    def set_waist(self,waist,unit="nm"):
        if unit == "m": self._waist_nm = waist * 1e9
        if unit == "um": self._waist_nm = waist * 1e3
        if unit == "nm": self._waist_nm = waist
            
    def get_waist(self,unit="nm"):
        if unit == "m": return self._waist_nm * 1e-9
        if unit == "um": return self._waist_nm * 1e-3
        if unit == "nm": return self._waist_nm            

    def initialize_to_position(self, position, photon_energy = None, reset = True, pixel_number = None, pixel_size = None):
        
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        # Based on a gaussian propagation
        Lambda = self.get_lambda(photon_energy=photon_energy)
        
        # Calculate the rayleigh length
        self._define_image_scale()
        zr = np.pi * self.get_waist()**2 / Lambda

        #print(self.get_waist(), Lambda)
        #print("Rayleigh distance:", zr[0].item()/1e9, "m")

        
        # Calculate the radius of curvature at the propagation point
        Rz = ((position)**2 + zr**2) / (position)
        
        # Calculate the beam waist
        wz = self.get_waist() * torch.sqrt(1 + (position)**2 / zr**2)

        #print("waist at target:", wz[0].item()/1e3,"um")

        # Calculate the q factor
        qz = 1./Rz - 1j * Lambda / (np.pi * wz**2)
        qz = 1./qz
        qz = qz.unsqueeze(-1).unsqueeze(-1).repeat(1, self._pixel_number[0], self._pixel_number[1])
        
        if self.spot_shift is None:
            beamSpot = 2.3e10*1./qz * torch.exp(-1j*2*np.pi/Lambda*(self._x**2 + self._y**2)/2.*1./qz)
        else:
            spot_shift_tmp = self.spot_shift.unsqueeze(-1).unsqueeze(-1).repeat(1, self._pixel_number[0], self._pixel_number[1])
            beamSpot = 2.3e10*1./qz * torch.exp(-1j*2*np.pi/Lambda*(self._x**2 + (self._y - spot_shift_tmp)**2)/2.*1./qz)
        beamSpot = beamSpot.type(torch.complex64)
        
        if self.beam_noise_level is not None:
            beam_noise_level_tmp = self.beam_noise_level.unsqueeze(-1).unsqueeze(-1).repeat(1, self._pixel_number[0], self._pixel_number[1])
            beamSpot = torch.randn(beamSpot.shape, device = self.device) * beamSpot * beam_noise_level_tmp + beamSpot
        #plt.figure(figsize = (12, 10))
        #plt.title("noisy vs clean beam profile")
        #plt.plot(torch.abs(beamSpot2)[0,0], label = "noisy")
        #plt.plot(torch.abs(beamSpot)[0,0], label = "clean")
        #plt.legend()
        #plt.show()
        #beamSpot = 2.3e10 * np.exp(-1j*2*np.pi/Lambda*(self._x**2 + self._y**2)/2.*1./qz)
        
        if reset:
            self._realPart = beamSpot.real
            self._imagPart = beamSpot.imag
        return beamSpot

    
class plane_XFEL(XFEL):
    def __init__(self,
                 pixel_number=None, 
                 pixel_size=None,
                 photon_energy = 8.15*keV,
                 photon_energy_bandwidth = 0.,
                 photon_energy_bandwidth_sample_width = 0.
                ):
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size,photon_energy=photon_energy,photon_energy_bandwidth=photon_energy_bandwidth,photon_energy_bandwidth_sample_width=photon_energy_bandwidth_sample_width)
        self.set_waist(10*m)
                           
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")

class arbitrary_XFEL(XFEL):
    def __init__(self,
                 initial_field=None, 
                 target=None,
                 pixel_number=None, 
                 pixel_size=None,
                 photon_energy = 8.15*keV,
                 photon_energy_bandwidth = 0.,
                 photon_energy_bandwidth_sample_width = 0.
                ):
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size,photon_energy=photon_energy,photon_energy_bandwidth=photon_energy_bandwidth,photon_energy_bandwidth_sample_width=photon_energy_bandwidth_sample_width)
        if initial_field is not None:
            self.set_initial_field(waist)
                           
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")
        
    def set_initial_field(self,initial_field):
        self._initial_field = initial_field
            
    def get_initial_field(self):
        return self._initial_field

    def initialize_to_position(self,position,photon_energy=None,reset=True):
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        self._define_image_scale()
        beamSpot = self.spectral_propagate_to_position(position=position,photon_energy=photon_energy,reset=reset)
        
# detector class
# for deciding wether to use spectral or Fresnel propagator
# to include possion, background, quantum efficiency, point spread function... not yet implemented
class Detector(XFEL):
    def __init__(self,label,category=None,pixel_number=None, pixel_size=None,XFEL=None,position=None, batch_size = 1, device = "cpu"):
        self.label=label
        self.batch_size = batch_size
        if XFEL is not None:
            self._XFEL = XFEL
            pixel_size = XFEL._pixel_size
            pixel_number = XFEL._pixel_number
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size, device = device)
        if category is not None:
            self.set_category(category)
        if position != None:
            self.position = position[2]
            self.position_xy = position[0:2]
        
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def get_axis(self):
        self._x = self._XFEL._x
        self._y = self._XFEL._y
            
    def set_category(self,category):
        self._category=category
        
    def get_category(self):
        return self._category
    
    def get_field(self):
        return self._field.real, self._field.imag

    def set_raw_data(self,field_in, x, y, pixel_size, pixel_number,rgb=None):
        self._field = field_in
        self._x = x
        self._y = y
        self._pixel_size=pixel_size
        self._pixel_number=pixel_number
        if rgb is not None:
            self._rgb = rgb
            
class jungfrau(Detector):
    def __init__(self,label, category=None, XFEL=None, position=None, batch_size = 1, device = "cpu"):
        self._pixel_size = 40*um
        self._pixel_number = (4000, 4000)
        self.batch_size = batch_size
        super().__init__(label,category=category,pixel_number=self._pixel_number, pixel_size=self._pixel_size,XFEL=XFEL,position=position, batch_size = batch_size, device = device)
        self._define_image_scale()
        
        
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def info(*args):
        print("Sorry, no info here, yet!")
        
        

class Beamline():
    def __init__(self,target=None,XFEL=None,detector=None):
        self._targets = None
        self._sorted_targets=None
        self._detectors = None

        if XFEL is not None:
            self.add_XFEL(XFEL)
        if target is not None:
            self.add_target(target)
        if detector is not None:
            self.add_detector(detector)
            
    def help(*args):
        print("Sorry, no help here, yet!")
        
    def propagate_XFEL_to(self,position=None, detector=None, verbose = 0):
        if type(detector) is type("string"):
            detector = self._detectors[detector]
        
        return self._XFEL.propagate_to(self._sorted_targets, position = position, detector = detector, verbose = verbose)
    
    def propagate_XFEL(self):
        for detector in self._detectors:
            propagate_XFEL_to(detector=detector)

    def add_XFEL(self,XFEL):
        self._XFEL = XFEL
        
    def add_target(self,target):
        if self._targets is None:
            self._targets = {}
        if target.label in self._targets:
            raise ValueError('ERROR! The target ',target.label,' already exists in this XFEL path. Target label must be unique.')
        self._targets[target.label] = target
        labels, self._sorted_targets = zip(*sorted(self._targets.items(), key=lambda x: x[1].position))
        
    def add_detector(self,detector):
        if self._detectors is None:
            self._detectors = {}
        if detector.label in self._detectors:
            raise ValueError('ERROR! The detector ',detector.label,' already exists in this XFEL path. Detector label must be unique.')
        self._detectors[detector.label] = detector
        #labels, self._sorted_dete = zip(*sorted(self._targets.items(), key=lambda x: x[1].position))
        
    def plot_detector(self,detector):
        if isinstance(detector,str):
            self._detectors[detector].plot()
        else:
            detector.plot()
        
    def plot_detectors(self):
        for detector in self._detectors:
            self.plot_detector(detector)

def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses

def wrap_complex(x_complex):
    return np.abs(x_complex) * np.exp(1j * np.angle(x_complex))

def wrap_phase(x_phase):
    return np.angle(np.exp(1j * x_phase))


def help():
    hprint("WELCOME TO THE INLINE HELP",color="white",bg="green",weight="bold")
    print("To setup an experiment, you need a target, XFEL, detector, and a beamline. For each element, there is a class:")
    print("")
    hprint("1. Material",bg="lightgreen",weight="bold")
    print("  Currently, the following preconfigured material children exist:")
    pprint(inheritors(Material))
    print("  You can get more information about a material by 'PCI.<material child>.info()'")
    print("  You can get more help about the Material class, e.g. to create your own material, via 'PCI.Material.help()'")
    print("")
    hprint("2. Targets",bg="lightgreen",weight="bold")
    print("  Currently, the following target children exist:")
    pprint(inheritors(Target))
    print("  You can get more information about a target by 'PCI.<material child>.info()'")
    print("  You can get more help about the Target class, e.g. to create your own target, via 'PCI.Material.help()'")
    print("")
    print("  Example to use a target:")
    print("  target = PCI.wire(")
    print("      \"wire\",                 # arbitrary but unique label")
    print("      radius=5000*PCI.nm,       # radius in nm")
    print("      material=PCI.Cu,          # a pointer to a material class")
    print("      rotation = 90,            # rotation of target, in deg")
    print("      position=[0,0,0.1*PCI.nm],# a position (z is XFEL direction)")
    print("      voxel_size=40*PCI.nm,     # size to which you want to resolve the volume (needs to be small for SAXS!)")
    print("      voxel_number = 400        # box size for the simulation")
    print("  )")
    print("")
    print("  * You can add more than one target!")
    print("")
    hprint("3. XFEL",bg="lightgreen",weight="bold")
    print("  Currently, the following XFEL children exist:")
    pprint(inheritors(XFEL))
    print("  You can get more information about an XFEL by 'PCI.<XFEL child>.info()'")
    print("  You can get more help about the XFEL class, e.g. to create your own XFEL, via 'PCI.XFEL.help()'")
    print("")
    print("  Example to use an XFEL:")
    print("  XFEL = PCI.gaussian_XFEL(")
    print("      waist = 43*um,")
    print("      pixel_number = 500,")
    print("      pixel_size = 430*PCI.nm,")
    print("      photon_energy = 8.15*PCI.keV,")
    print("      photon_energy_bandwidth = 0*eV,             # default is 0")
    print("      photon_energy_bandwidth_sample_width = 0*eV # default is 0")
    print("  )")
    print("")
    hprint("4. Detector",bg="lightgreen",weight="bold")
    print("  Currently, the following Detector children exist:")
    pprint(inheritors(XFEL))
    print("  You can get more information about a detector by 'PCI.<XFEL child>.info()'")
    print("  You can get more help about the Detector class, e.g. to create your own target, via 'PCI.XFEL.help()'")
    print("")
    print("  Example to use a detector:")
    print("  zyla = PCI.jungfrau(")
    print("      \"Zyla\",             # unique identifer")
    print("      category = \"SAXS\",  # PCI (spectral propagator) or SAXS (Lorentz propagator - not conserving the pixel size!)")
    print("      XFEL=XFEL,            # initial pixel sizes and numbers are set to those of the XFEL")
    print("      position=[0,0,3*m]    # position relative to XFEL focus")
    print(")")
    print("")
    hprint("5. Beamline",bg="lightgreen",weight="bold")
    print("  You can get more help about the beamline class via 'PCI.XFEL.help()'")
    print("")
    print("  Example to use the beamline:")
    print("  #set up beamline")
    print("  bl = PCI.beamline()")
    print("  bl.add_target(target)")
    print("  #bl.add_target(target2)")
    print("  bl.add_XFEL(XFEL)")
    print("  bl.add_detector(zyla)")
    print("  # propagate XFEL")
    print("  bl.propagate_XFEL_to(detector = zyla)")
    print("  ")
    print("  #also possible:")
    print("  #bl.propagate_XFEL_to(detector = zyla)")
    print("  #bl.propagate_XFEL_to(position = target.get_position())")
    print("  #bl.propagate_to(position = 5*m)")
    print("  #bl.propagate_to(detector = \"zyla\")")
    print("  ")
    print("  #Everything can be plotted: detector, target, XFEL:")
    print("  bl.plot_detectors()\n\n")
    hprint("© Copyright 2022 by Thomas Kluge (t.kluge@hzdr.de)",color="white",bg="green",weight="bold")

hprint("PCI successfully compiled. You can get more help by typing 'PCI.help()'",color="black",bg="lightgreen")
print("  This module is part of HRXP, Copyright (C) 2022 Thomas Kluge")
print("  This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
print("  This is free software, and you are welcome to redistribute it")
print("  under certain conditions; type `show c' for details.")