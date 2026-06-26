# HRXP - calculates PCI and SAXS images for an XFEL beamline
#
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
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from scipy.ndimage import affine_transform
from scipy import interpolate
from scipy.ndimage import measurements
from scipy.fftpack import fftshift
from scipy.fftpack import ifftshift
from scipy.fftpack import fftfreq
from scipy.ndimage import shift
import scipy.ndimage as ndimage
from PIL import Image
import pprint as pp
from scipy.interpolate import RectBivariateSpline
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
from multiprocessing import Pool

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
    
m = 1e9 # meter in units of base unit (nm)
um=1e3 # micron
mm=1e6 #milimeter
#cm=1e3 #cm
cm=1e7 #cm corrected by Lingen
nm=1. # base unit for length nanometer

keV=1 # base unit for energy
eV=1e-3
 
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
        
    def get_n_refraction_delta(self,photonEnergy=None):
        """calculate the Thomson scattering cross-section"""
        #self._set_n_refraction_delta(photonEnergy)
        # the factor 0.933386 below comes from correction to Henke data 
        return 0.933386*self._Na * self._mat_dens * self._mat_ZA * self._re * (2. * np.pi / (2.0e0 * np.pi / (1.239842 / photonEnergy))**2)
        #return 1.0*self._Na * self._mat_dens * self._mat_ZA * self._re * (2. * np.pi / (2.0e0 * np.pi / (1.239842 / photonEnergy))**2)  #comment by Lingen the correction factor needs to be checked 
        #self._n_refraction_delta
    
    def set_n_refraction_delta(self,photonEnergy=None):
        """store value in class atribute"""
        # Thomson scattering
        self._n_refraction_delta = self.get_n_refraction_delta(photonEnergy=photonEnergy)
        #self._n_refraction_delta = self._Na * self._mat_dens * self._mat_ZA * self._re * (2. * np.pi / (2.0e0 * np.pi / (1.239842 / photonEnergy))**2)
        
    def get_n_refraction_beta(self,photonEnergy=None):
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
        print(f'mu is {mu} [1/um]') # 4.0906e-5 for 8.2 keV
        #mu= 4.3983e-5 # set in imageJ for 8.2 keV commented by Lingen
        
        return mu
# comment by Lingen: photonEnergy has to be hard set here        
    def info(self,photonEnergy=8.2):
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
    def __init__(self,label,category=None,photon_Energy=None,position=None,voxel_size=None,voxel_number=None,rotation=0):
        """ Target parameters """
        # comment by Lingen: photon_Energy is re-defined in the Target class
        self.photon_Energy = photon_Energy
        self._volumes = []
        self._materials = []
        self.voxel_number   = voxel_number             # target world size in VOXELS (4000 are too many! 256GB ram)
        self.voxel_size  = voxel_size                  # target world voxel size in nm
        self.label = label                             # user has to set a label to be able to identify and delete a target later in the XFEL beam path
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
        return np.exp(-0.5*mu) # Transmission of Field, not Intensity, comment by Lingen

    
    def plot(self):
        """show the density, for diagnostic purposes"""
        # comment by Lingen: photon_Energy is re-defined in the Target class
        absorption = 1-self.get_absorption(self.photon_Energy) 
        phase = self.get_phase_shift(self.photon_Energy)

        fig, axs = plt.subplots(2,2,figsize=(6,5), gridspec_kw={'height_ratios': [1, 1]},sharex=True)
        fig.suptitle('Target '+self.label+'\n Field absorption    |    phase shift')
        x = len(self._density1[0,:])*self.voxel_size/1000
        y = len(self._density1[:,0])*self.voxel_size/1000
        axs[0,0].imshow(absorption, interpolation='none',extent=[-x/2,x/2,-y/2,y/2],aspect='auto')
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,0].set_ylabel("y ($\mu$m)")

        x=np.arange(-len(absorption[0,:])/2,len(absorption[0,:])/2)*self.voxel_size/1000
        axs[1,0].plot(x,absorption[int(self.voxel_number/2),:])
        axs[1,0].set_xlabel("x ($\mu$m)")

        x = len(self._density1[0,:])*self.voxel_size/1000
        y = len(self._density1[:,0])*self.voxel_size/1000
        axs[0,1].imshow(phase, interpolation='none',extent=[-x/2,x/2,-y/2,y/2],aspect='auto')
        #axs[0].xlabel("x ($\mu$m)")
        axs[0,1].set_ylabel("y ($\mu$m)")

        x=np.arange(-len(phase[0,:])/2,len(phase[0,:])/2)*self.voxel_size/1000
        axs[1,1].plot(x,phase[int(self.voxel_number/2),:])
        axs[1,1].set_xlabel("x ($\mu$m)")
        plt.tight_layout()
        plt.show()        

# Targets
"""The target class is a child of target class and defines the specific target geometry, projection, material composition etc.
   It can also be a multi-material object."""
class wire(Target):
    """This is a sample class demonstrating the usage. We define a cylindrical wire with one material."""
    def __init__(self,label,radius=None,photon_Energy=None,material=None,position=None,voxel_size=None,voxel_number=None, rotation=0):
        self._material1 = material()
        self.photon_Energy = photon_Energy
        self.radius1_nm    = radius           # wire radiuses
# comment by Lingen: photon_Energy is re-defined in the Target class
        super().__init__(label,photon_Energy=photon_Energy,position=position,voxel_size=voxel_size,voxel_number=voxel_number,rotation=rotation)
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

            Y, X = np.ogrid[:h, :w]
            dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)

            mask = dist_from_center <= radius
            return mask

        self._radiusPixel = self.radius1_nm / self.voxel_size
        mask = circular_mask(self.voxel_number, self.voxel_number, center = (self.voxel_number/2,self.voxel_number/2), radius=self._radiusPixel)

        """ Target volume is the 3D representation of the target
            1st index is x axis, 2nd index is y and 3rd index is y """
        volume = np.zeros((self.voxel_number, self.voxel_number, self.voxel_number))

        for i in range(0, self.voxel_number):
            volume[i] = mask * 1.

        return volume
    
    def _get_projection(self, volume):
        """calculates density/material_density*depth(nm)"""

        """1. project the volume density to 2D, in XFEL propagation direction"""
        volume = self._build_volume1()   ## The _build_volume has to be defined in the child class!

        """2.project along the z direction"""
        projection = volume.sum(2) * self.voxel_size   # The VOXELS contain the density, we need to multiply by the voxel length to account for their size
        
        """3. now rotate to match the XFEL direction (the angle is transverse to XFEL direction; longitudinal angle not yet implemented)"""
        projection = rotate(projection,angle=self.rotation)

        projection_s = projection*0
                
        shift(projection,np.asarray(self.position_xy)/self.voxel_size,projection_s, cval=0)
                
        self._density1 = projection_s
        #self._density1 = projection
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
                 photon_energy_bandwidth_sample_width = 0.
                ):
        self._category = ""
        # Express the field as cos(phi) + i*sin(phi)
        self.realPart = []
        self.imagPart = []
                
        # Express the field as A * exp(i*phi)
        self.amplitude = []
        self.phase = []
        
        self._pixel_number = None
        self._pixel_size = None
        
        self._photon_energy=photon_energy
        self._photon_energy_bandwidth = photon_energy_bandwidth
        self._photon_energy_bandwidth_sample_width = photon_energy_bandwidth_sample_width
        
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
        xaxis = np.arange(-pixel_number/2,pixel_number/2) * pixel_size # by Lingen, should be new pixel_size?
        x, y, = np.meshgrid(xaxis, xaxis)
        
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
        
        # saving the intensity data on the detector by Lingen
        
        #intensity_detector = Image.fromarray(I)
        #intensity_detector.save('../PythonData/intensity_detector.tif')
        
        self.intensity_detector = I # added by Lingen output for the PIC/SAXS intensity on the target
        #self.x_plot = x # added by Lingen output for the new x axis
        #self.pixel_size_plot = self._pixel_size # added by Lingen output for the new x axis
        
        #print ('output the the intensiyt for the detector')
        
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
        coarseX = np.arange(-target.voxel_number/2,target.voxel_number/2) * target.voxel_size
        coarseY = np.arange(-target.voxel_number/2,target.voxel_number/2) * target.voxel_size
        coarseXX, coarseYY = np.meshgrid(coarseY, coarseY)
        #interp = interpolate.interp2d(coarseX, coarseY, target_projection)
        # interp = RegularGridInterpolator(
        #     (coarseY, coarseX),
        #     target_projection,
        #     method='linear',
        #     bounds_error=False,
        #     fill_value=0)
        interp = RectBivariateSpline(
            coarseY,
            coarseX,
            target_projection
        )
                

        fineX = np.arange(-self._pixel_number/2,self._pixel_number/2) * self._pixel_size
        fineY = np.arange(-self._pixel_number/2,self._pixel_number/2) * self._pixel_size
        #fineProjection = interp(fineX, fineY)
        fineProjection = interp(fineY, fineX)

        return np.array(fineProjection, dtype=np.float32)
        
    """ Calculate the modified wave at contact position (immediately after the target) """
    def propagate_through_target(self,target,reset=True,field_in=None, photon_energy=None):
        #this takes quite some time, needs to get parallized
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        # Transmission and amplitude
        # with n = 1 - delta + i beta
        # E0 = E * exp(-2*pi/lambda * integral(beta))
        transmission = self._interpolate_target2beam(target.get_absorption(photon_energy),target)#*0+1

        if field_in is None:
            beamFieldReal,beamFieldImag = self.get_field()
        else:
            beamFieldReal = field_in.real
            beamFieldImag = field_in.imag
        E0 = np.sqrt(beamFieldReal**2 + beamFieldImag**2)
        transmitted_E0 = E0 * transmission
        transmitted_I = transmitted_E0**2
        


        # Phase shift
        beamPhase = np.angle(beamFieldReal + beamFieldImag*complex(0,1))
        
        #beamPhase = -beamPhase # commented by Lingen beamPhase to -beamPhase
        #Loading initial beam phase from the input data by Lingen 
        #IJ_IncidentPhase_LH_image = Image.open('../ImageJ/IncidentPhase_LH.tif')
        #IJ_IncidentPhase_LH_image = Image.open('../ImageJ/SAXS/IncidentPhase.tif')
        #IJ_IncidentPhase_LH_image = Image.open('../ImageJ/IncidentPhase.tif')
        #beamPhase = np.array(IJ_IncidentPhase_LH_image)
        #beamPhase = ndimage.gaussian_filter(beamPhase, sigma=100.0, order=0)
        #self.beamPhase_LH = beamPhase
        
        # Output by Lingen before target
        self.intensity_beforetarget = E0**2
        self.phase_beforetarget = beamPhase          
        
        # phase shift afte the target: delta_phi=k * $\delta$ * thickness 
        dPhi = self._interpolate_target2beam(target.get_phase_shift(photon_energy),target)
        
        # Wrapping the phase shift from -pi to pi by Lingen
        #dPhi_LH = np.angle(np.exp(-1j * dPhi))  
        #dPhi = (dPhi + np.pi) % (2 * np.pi) - np.pi
        
        # Output by Lingen after target
        self.intensity_aftertarget = transmitted_I
        self.phase_aftertarget = beamPhase - dPhi
        

        plt.figure(figsize=[6,3])
        plt.subplot(1,2,1)
        plt.title("transmitted intensity")
        plt.imshow(transmitted_I)
        #plt.colorbar()
        
        beamPhase = beamPhase - dPhi
        
        
        # Wrapping the phase from -pi to pi by Lingen
        #beamPhase = np.angle(np.exp(-1j * beamPhase))
        #beamPhase_LH = np.angle(np.exp(-1j * beamPhase))
        #beamPhase = (beamPhase + np.pi) % (2 * np.pi) - np.pi
        
        
        plt.subplot(1,2,2)
        plt.title("transmitted phase")
        plt.imshow(beamPhase)
        #plt.colorbar()
        plt.tight_layout()
        plt.show()
        
        # Construct the wave at contact
        wave_real = np.cos(beamPhase)
        wave_imag = np.sin(beamPhase)
        wave_at_contact = transmitted_E0 * (wave_real + complex(0,1) * wave_imag)

        if reset:
            self._realPart = transmitted_E0 * wave_real
            self._imagPart = transmitted_E0 * wave_imag
        
        return transmitted_E0 *(wave_real + complex(0,1) * wave_imag)

    def propagate_to(self,targets,position=None,detector=None):
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
                                #if target.get_category() == "SAXS":
                                #    self.lorentz_propagate_to_position(position=target_position-XFEL_position, photon_energy=self._photon_energy, field_in=field, reset=reset)
                                #    print("bandwidth not taken into account")
                                #else:
                                self.spectral_propagate_to_position(position=target_position-XFEL_position, photon_energy=photon_energy, field_in=field, reset=reset)
                                XFEL_position = target_position
                            #propagate through target
                            field = self.propagate_through_target(target,field_in=field, photon_energy=photon_energy, reset=reset)
                    #now we are behind the last target
                    if detector is None or detector.get_category() == "PCI":
                        field = self.spectral_propagate_to_position(position=position-XFEL_position, photon_energy=photon_energy, field_in=field, reset=reset)
                        #commented by Lingen, PCI here still use near field propagator 
                        #field = self.lorentz_propagate_to_position(position=position-XFEL_position, photon_energy=self._photon_energy, field_in=field, reset=reset)
                    else:
                        field = self.lorentz_propagate_to_position(position=position-XFEL_position, photon_energy=self._photon_energy, field_in=field)
                        hprint("Sorry, due to the detector type 'SAXS', bandwidth not taken into account in propagation from last target to detector!",color="white",bg="#FF9999")
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
            
        rgb = np.dstack(( np.abs(E_r)**2/np.max(np.abs(E_r)**2) , np.abs(E_g)**2/np.max(np.abs(E_g)**2) , np.abs(E_b)**2/np.max(np.abs(E_b)**2) ))

        self._rgb = rgb
        self._realPart = E_new_tot.real
        self._imagPart = E_new_tot.imag

        if detector is not None:
            detector.set_raw_data(E_new, self._x, self._y, self._pixel_size, self._pixel_number, rgb=rgb)

        return E_new_tot, rgb

    
    def spectral_propagate_to_position(self,position=None,field_in=None,reset=True, photon_energy=None):
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
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
        fft_c = fft2(field_in)
        c = fftshift(fft_c)

        kx = 2*np.pi*fftshift(fftfreq(old_pixel_number, d = old_pixel_size))
        ky = 2*np.pi*fftshift(fftfreq(old_pixel_number, d = old_pixel_size))
        kx, ky = np.meshgrid(kx, ky)

        argument = (2 * np.pi / Lambda) ** 2 - kx ** 2 - ky ** 2

        #Calculate the propagating and the evanescent (complex) modes
        tmp = np.sqrt(np.abs(argument))
        kz = np.where(argument >= 0, tmp, j*tmp)

        # propagate the angular spectrum a distance z
        cc=ifftshift(c * np.exp(j * kz * Z))
        #new_pixel_size = Z * np.pi/(k*old_pixel_number*old_pixel_size)  # by Lingen
        X,Y = self._define_image_scale() # added by Lingen        
        #cc = ifftshift(c * np.exp(1j * (2 * np.pi / Lambda) * Z) * np.exp(-1j * Lambda * np.pi * Z * (X / Lambda / Z)**2 + (Y / Lambda / Z)**2)) #Fresnel approximation by Lingen
        self.new_x_plot = X[0,:]/1e3 # boosted image size added by Lingen 
        self.new_pixel_size = old_pixel_size/1e3 # added by Lingen        
        
        E_new = ifft2(cc)

#        self._realPartSpectralPropagated = E_new_tot.real
#        self._imagPartSpectralPropagated = E_new_tot.imag

        if reset:
            self._realPart = E_new.real
            self._imagPart = E_new.imag
            
        return E_new
            
        
    def lorentz_propagate_to_position(self,position=None,field_in=None,reset=True, photon_energy=None):           
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        if field_in is None:
            field_in = self._realPart + j*self._imagPart
        # Fresnel diffraction propagator
        # calculate E field at position X, Y, Z=position, where X, Y are on the old coordinates x, y or those defined by new pixel_number and pixel_size
        # E(X,Y,Z) = Eqn. 13
        print (f'The position is {position:0.3f}')
        Lambda = self.get_lambda()
        k=self.get_k()
        Z=position
        j=complex(0,1)
        old_pixel_size = self._pixel_size
        old_pixel_number = self._pixel_number
        #new_pixel_size = Z * np.pi/(k*old_pixel_number*old_pixel_size)  
        new_pixel_size = Z *2* np.pi/(k*old_pixel_number*old_pixel_size)  # Lingen lost of a factor of 2 ? It should be 2*np.pi here?
        
        E = field_in
        E = fft2(E* np.exp(j*(k/(2*Z)*(self._x**2 + self._y**2))))
        X,Y = self._define_image_scale(pixel_size=new_pixel_size,reset=reset)
        R = np.exp(j*k*Z)/(j*Lambda*Z) * np.exp(j * k / ( 2 * Z ) * ( X**2 + Y**2 ) ) # X, Y is the values on the target plane, why? Lingen
        E = R * fftshift(E)
        
        #self._realPartLorentzPropagated = E.real
        #self._imagPartLorentzPropagated = E.imag
        self.new_x_plot = X[0,:]/1e3 # boosted image size added by Lingen 
        self.new_pixel_size = new_pixel_size/1e3 # added by Lingen

        if reset:
            self._realPart = E.real
            self._imagPart = E.imag
            
        return E.real + 1j*E.imag

class gaussian_XFEL(XFEL):
    def __init__(self,
                 waist=None,
                 pixel_number=None, 
                 pixel_size=None,
                 photon_energy = 8.15*keV,
                 photon_energy_bandwidth = 0.,
                 photon_energy_bandwidth_sample_width = 0.
                ):
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size,photon_energy=photon_energy,photon_energy_bandwidth=photon_energy_bandwidth,photon_energy_bandwidth_sample_width=photon_energy_bandwidth_sample_width)
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

    def initialize_to_position(self,position,photon_energy=None,reset=True,pixel_number=None, pixel_size=None):
        if photon_energy is None:
            photon_energy = self.get_photon_energy()
        # Based on a gaussian propagation
        Lambda = self.get_lambda(photon_energy=photon_energy)
        # Calculate the rayleigh length
        self._define_image_scale()
        zr = np.pi * self.get_waist()**2 / Lambda
        print("Rayleigh [m]: ",zr*1e-9)              
        # Calculate the radius of curvature at the propagation point
        Rz = ((position)**2 + zr**2) / (position)
        print("Radius [um]: ",Rz*1e-3,Lambda)
        #print("Fresnel: ",self._parameters["ri_nm"]**2/position/Lambda)
        
        # Calculate the beam waist
        wz = self.get_waist() * np.sqrt(1 + (position)**2 / zr**2)
        
        self.FWHM_target = wz/1e3*1.177410023 # added by Lingen beam waist at the target plane
        
        print(f'the beam waist on the target plane is  {wz/1e3:0.3f} um') 
        print(f'the FWHM beam waist on the target plane is  {self.FWHM_target:0.3f} um') 
        #print(f'radius of curvature at the propagation point is  {Rz:0.3f} nm')
        
        
        # Calculate the q factor
        qz = 1./Rz - 1j * Lambda / (np.pi * wz**2)
        # comment by Lingen, is the sign of 1/Rz right?
        #qz = -1./Rz - 1j * Lambda / (np.pi * wz**2)
        #qz1 = -1./Rz - 1j * Lambda / (np.pi * wz**2)
        qz = 1./qz
        #qz1 = 1./qz1
        
        beamSpot = 2.3e10*1./qz * np.exp(-1j*2*np.pi/Lambda*(self._x**2 + self._y**2)/2.*1./qz)
        #beamSpot = 2.3e10*1./qz * np.exp(-1j*2*np.pi/Lambda*(self._x**2 + self._y**2)/2.*1./qz)/1.4142# normalized to 1?
        # comment by Lingen, what is the factor of 2.3e10 coming from?
        #beamSpot_LH = 2.3e10*1 * np.exp(-1j*2*np.pi/Lambda*(self._x**2 + self._y**2)/2.*1./qz)
        
        #x_target = self._x
        #y_target = self._y
        
        print(f'the target postion is {position/1e9:0.3f} m') 
        print(f'complex q parameter is {qz}') 
        #print(f'complex q1 parameter is {qz1}') 
        
        # Output by Lingen        
        self.beamSpot_test = beamSpot
        #self.beamSpot_LH = beamSpot_LH
        
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
    def __init__(self,label,category=None,pixel_number=None, pixel_size=None,XFEL=None,position=None):
        self.label=label
        if XFEL is not None:
            self._XFEL = XFEL
            pixel_size = XFEL._pixel_size
            pixel_number = XFEL._pixel_number
        super().__init__(pixel_number=pixel_number, pixel_size=pixel_size)
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
                
        #self.intensity_detector = self._field.real**2+self._field.imag**2 # added by Lingen output for the PIC/SAXS intensity on the target
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
    def __init__(self,label, category=None, XFEL=None, position=None):
        self._pixel_size = 40*um
        self._pixel_number = 4000
        self._define_image_scale()
        super().__init__(label,category=category,pixel_number=self._pixel_number, pixel_size=self._pixel_size,XFEL=XFEL,position=position)

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
        
    def propagate_XFEL_to(self,position=None, detector=None):
        if type(detector) is type("string"):
            detector = self._detectors[detector]
        return self._XFEL.propagate_to(self._sorted_targets,position=position,detector=detector)
    
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


hprint("PCI successfully compiled. You can get more help by typing 'PCI.help()'",color="black",bg="lightgreen")

print("  This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
print("  This is free software, and you are welcome to redistribute it")
print("  under certain conditions; type `show c' for details.")