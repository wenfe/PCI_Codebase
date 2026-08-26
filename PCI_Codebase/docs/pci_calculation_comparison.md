# PCI calculation and comparison with `SAXS_PCI_Pointing_Div`

## Summary

[`clean_pci_design.ipynb`](../SAXS_asymmetry/clean_pci_design.ipynb) and
[`SAXS_PCI_Pointing_Div.ipynb`](../SAXS_asymmetry/SAXS_PCI_Pointing_Div.ipynb)
use essentially the same incident Gaussian beam and the same copper-wire
transmission model. They differ after the wire:

- the clean notebook propagates the complex exit field with an exact
  angular-spectrum transfer function over an active distance of 6.31 m;
- `SAXS_PCI_Pointing_Div` reconstructs the exit field in LightPipes and uses
  `LightPipes.Fresnel`, a Fresnel convolution, over an active distance of
  1.31 m.

The current outputs are therefore not directly interchangeable. The clean
notebook is a simplified PCI design, not a numerically identical rewrite of
the legacy PCI calculation.

The two active workflows can be summarized as follows:

```text
Common source and sample stages
    Gaussian source at its waist
        -> evaluate divergent Gaussian field at the wire
        -> calculate projected Cu-wire thickness
        -> apply field absorption and phase delay
        -> complex exit field

clean_pci_design
    complex exit field
        -> exact angular-spectrum propagation, 6.31 m
        -> detector intensity |E|^2
        -> one zero-offset PCI TIFF

SAXS_PCI_Pointing_Div
    complex exit field
        |-> PCI.py single-FFT propagation, 1.31 m -> SAXS image
        `-> reconstruct field in LightPipes
            -> LightPipes Fresnel convolution, 1.31 m
            -> PCI intensity and one TIFF per wire offset
```

## How PCI is calculated

### 1. Photon wavelength and wavenumber

Both notebooks use a photon energy of 8.2 keV. `PCI.py` uses nanometres as
its base transverse-length unit and defines

\[
\lambda = \frac{hc}{E}, \qquad hc=1.239842\ \mathrm{keV\,nm},
\qquad k=\frac{2\pi}{\lambda}.
\]

At 8.2 keV,

\[
\lambda \simeq 0.151200\ \mathrm{nm}.
\]

The clean notebook wraps the propagation calculation in SI-valued data
classes, but converts to the native `PCI.py` nanometre units at the API
boundary.

### 2. Construct the incident divergent Gaussian beam

The Gaussian waist is at \(z=0\), and the wire is at

\[
z_t=0.25\ \mathrm{m}.
\]

For a Gaussian beam with waist radius \(w_0\),

\[
z_R=\frac{\pi w_0^2}{\lambda},
\qquad
w(z)=w_0\sqrt{1+\left(\frac{z}{z_R}\right)^2}.
\]

The code's intensity FWHM is related to the Gaussian radius by

\[
\mathrm{FWHM}_I(z)=\sqrt{2\ln 2}\,w(z).
\]

The requested target-plane FWHM is 6 micrometres. Defining

\[
w_t=\frac{6\ \mathrm{\mu m}}{\sqrt{2\ln 2}},
\qquad a=\frac{\lambda z_t}{\pi},
\]

the two possible source-waist solutions follow from

\[
w_t^2=w_0^2+\frac{a^2}{w_0^2}.
\]

The clean notebook explicitly selects the smaller, divergent root,

\[
w_0^2=\frac{w_t^2-\sqrt{w_t^4-4a^2}}{2},
\]

which gives

\[
w_0\simeq2.846721\ \mathrm{\mu m},
\qquad z_R\simeq0.168379\ \mathrm{m}.
\]

The legacy notebook hard-codes the rounded value 2.84672 micrometres. In both
cases, `PCI.gaussian_XFEL.initialize_to_position()` evaluates the complex
Gaussian amplitude and curved phase front at the wire plane. Thus the two
incident fields are intended to represent the same divergent branch, apart
from the grid size and the insignificant rounding of the waist.

### 3. Calculate the projected wire thickness

The target is an ideal copper cylinder with radius

\[
R=5\ \mathrm{\mu m}.
\]

Its continuous projected chord would be

\[
t(x)=
\begin{cases}
2\sqrt{R^2-(x-x_0)^2}, & |x-x_0|\le R,\\
0, & |x-x_0|>R.
\end{cases}
\]

The notebooks use a voxelized version with a 20 nm target voxel and 2000
target samples per dimension. At a transverse voxel coordinate \(j\), the
voxel-equivalent chord used by the clean notebook is

\[
t_j=\left(2\left\lfloor
\sqrt{R_{\mathrm{px}}^2-j^2}
\right\rfloor+1\right)\Delta_t,
\]

where \(R_{\mathrm{px}}=R/\Delta_t\) and \(\Delta_t=20\) nm.

The legacy `PCI.wire` constructs a full 2000 by 2000 by 2000 volume and sums
it along the X-ray direction. The clean notebook's `projected_wire` subclass
calculates the equivalent two-dimensional voxel chord directly. This removes
the unused three-dimensional allocation while retaining the legacy voxel
geometry. The resulting target projection is spline-interpolated from the
20 nm target grid to the 8 nm beam grid by `PCI.py`.

For the legacy scan, all 2.5 micrometre offsets are integer multiples of 20
nm, so no fractional target-pixel shift is required. The clean notebook's
50-point diagnostic scan includes fractional target-pixel positions and uses
linear interpolation for those shifts.

### 4. Apply copper absorption and phase delay

The complex refractive index is represented by the decrement \(\delta\) and
absorption term \(\beta\). For projected thickness \(t(x,y)\), the physical
thin-sample form is

\[
E_{\mathrm{exit}}(x,y)
=E_{\mathrm{incident}}(x,y)
\exp\left[-\frac{\mu t(x,y)}{2}\right]
\exp\left[-ik\delta t(x,y)\right].
\]

The factor of one half is required because \(\mu\) describes intensity
attenuation, whereas this exponential acts on field amplitude. Therefore

\[
I_{\mathrm{exit}}
=I_{\mathrm{incident}}\exp[-\mu t].
\]

In the present implementation, `PCI.Cu` supplies \(\delta\) and \(\beta\),
and `PCI.py` uses its empirical copper absorption coefficient

\[
\mu_{\mathrm{code}}=10E_{\mathrm{keV}}\beta
\]

in inverse nanometres. `XFEL.propagate_through_target()` applies both the
amplitude transmission and phase delay and stores diagnostic copies of the
intensity and phase before and after the wire.

The clean `simulate_pci()` function uses the returned complex exit field
directly. The legacy notebook instead reads the stored
`XFEL.intensity_aftertarget` and `XFEL.phase_aftertarget` arrays and rebuilds
the same field using `LightPipes.SubIntensity()` and
`LightPipes.SubPhase()`.

### 5. Propagate the exit field to the PCI detector

#### Clean angular-spectrum calculation

The clean notebook decomposes the exit field into plane waves:

\[
\widetilde E(k_x,k_y)=\mathcal F\{E_{\mathrm{exit}}(x,y)\}.
\]

Each component receives the exact scalar Helmholtz propagation factor

\[
H(k_x,k_y;z)=\exp(ik_z z),
\qquad
k_z=\sqrt{k^2-k_x^2-k_y^2}.
\]

For \(k_x^2+k_y^2>k^2\), the code uses the imaginary root, so evanescent
components decay rather than oscillate. The detector field is

\[
E_D(x,y)=\mathcal F^{-1}
\left\{
\mathcal F[E_{\mathrm{exit}}]H
\right\}.
\]

This method preserves the transverse grid. With the active clean settings,

\[
N=4096, \qquad \Delta x=8\ \mathrm{nm},
\qquad L=N\Delta x=32.768\ \mathrm{\mu m}.
\]

The active sample-to-detector propagation distance is 6.31 m. The constant
`Z_DETECTOR = 1.31 * PCI.m` also appears near the top of the notebook, but it
is not the distance used by `PCIConfig.propagation_distance_m`; the latter is
set from `PCI_DETECTOR_DISTANCE = 6.31 * PCI.m`.

#### Legacy LightPipes calculation

The detector object inside `SAXS_PCI_Pointing_Div` has category `"SAXS"`.
Consequently, `beamline.propagate_XFEL_to()` does **not** create its PCI image;
it creates the SAXS field through `PCI.py`'s rescaling single-FFT propagator.

The legacy PCI image is calculated separately:

```python
F = LP.Begin(size_LP, wavelength_LP, N)
F = LP.SubIntensity(F, XFEL.intensity_aftertarget)
F = LP.SubPhase(F, XFEL.phase_aftertarget)
F_at_Fresnel = LP.Fresnel(F, Z_detector_LP)
I_at_Fresnel = LP.Intensity(F_at_Fresnel)
```

`LightPipes.Fresnel` is a paraxial Fresnel convolution. It preserves the
nominal input-plane field size and sampling, internally zero-pads the
convolution, and returns a cropped array of the original dimensions. With the
active legacy settings,

\[
N=8192, \qquad \Delta x=8\ \mathrm{nm},
\qquad L=65.536\ \mathrm{\mu m},
\qquad z=1.31\ \mathrm{m}.
\]

Although a 6.31 m PCI distance exists as a commented alternative in the
legacy notebook, its active `Z_detector_PCI` value is 1.31 m. The detector's
absolute position relative to the source waist is therefore

\[
z_D=z_t+1.31\ \mathrm{m}=1.56\ \mathrm{m}.
\]

### 6. Calculate and save detector intensity

Both detector calculations finally form

\[
I_D(x,y)=|E_D(x,y)|^2.
\]

The clean notebook currently calls `simulate_pci(PCIConfig())` without a wire
offset, so it propagates only the zero-offset case. It converts the detector
intensity explicitly to `float32` and saves
`SAXS_asymmetry/outputs/clean_pci/clean_pci_detector_intensity.tif` with TIFF deflate compression.

The legacy notebook propagates eight offsets,

\[
-10,-7.5,-5,-2.5,0,2.5,5,7.5\ \mathrm{\mu m},
\]

and saves a `DivPCI_Offset*.tif` image after every LightPipes propagation.
These are accompanied by separate SAXS TIFFs and combined PCI/SAXS figures.

Neither workflow applies a physical detector pixel integration, detector
point-spread function, quantum efficiency, noise, or an absolute calibration
to measured counts. Their intensities remain simulation units inherited from
the arbitrary absolute scale in `PCI.gaussian_XFEL`.

## The clean wire-offset scan is not propagated PCI

`clean_pci_design` also evaluates 50 offsets from -10 to +10 micrometres. For
this calculation it uses

\[
I_{\mathrm{exit}}(x)=I_{\mathrm{incident}}(x)
\exp[-\mu t(x)]
\]

and integrates this target-exit intensity over the left and right
half-planes. The phase term cancels before propagation and no detector
propagator is called inside the scan loop.

Therefore these curves describe an absorption shadow immediately behind the
wire. They are not PCI detector left/right curves, and they do not contain
phase-contrast fringes. The scan is computationally reduced to one dimension
using the separability of the Gaussian and the translational invariance of
the ideal wire along its axis.

The same plot loads
`SAXS_asymmetry/outputs/saxs/tables/DivSAXS_asymmetry_Mark1300_7p5um.dat`.
That SAXS table uses a 7.5 micrometre
beam, whereas the clean PCI exit scan uses a 6 micrometre beam. It is a visual
cross-comparison, not a matched PCI/SAXS calculation.

## Side-by-side comparison

| Component | `clean_pci_design.ipynb` | `SAXS_PCI_Pointing_Div.ipynb` |
|---|---|---|
| Purpose | Isolated, modular PCI calculation | Combined SAXS and PCI pointing scan |
| Photon energy | 8.2 keV | 8.2 keV |
| Target position from waist | 0.25 m | 0.25 m |
| Target-plane intensity FWHM | 6 micrometres | 6 micrometres |
| Source waist used | Analytically solved 2.846721 micrometres | Rounded 2.84672 micrometres |
| Beam grid | 4096 by 4096 | 8192 by 8192 |
| Input pixel | 8 nm | 8 nm |
| Field width | 32.768 micrometres | 65.536 micrometres |
| Wire | Cu, radius 5 micrometres | Same |
| Target discretization | Direct 2-D voxel-equivalent projection | Full 3-D voxel volume followed by projection |
| Target voxel | 20 nm | 20 nm |
| Exit-field implementation | `PCI.py` complex field returned directly | `PCI.py` diagnostics reconstructed in LightPipes |
| PCI propagator | Exact angular spectrum | Paraxial LightPipes Fresnel convolution |
| Active sample-to-detector distance | 6.31 m | 1.31 m |
| Output pixel | 8 nm, preserved | Approximately 8 nm, preserved |
| FFT boundary behavior | Periodic/circular | Zero-padded convolution and crop |
| PCI offsets propagated | Zero only in the executed simulation call | -10 to +7.5 micrometres in 2.5 micrometre steps |
| Offset summary | 50-point target-exit absorption scan | Detector images at eight offsets |
| PCI TIFF | One compressed float32 image | One image per offset |
| SAXS calculation | Not recalculated; an existing 7.5 micrometre table is loaded | Calculated in the same loop for the active 6 micrometre beam |

## Numerical sampling considerations

Angular-spectrum propagation is exact for the sampled scalar field, but its
FFT implementation assumes periodic transverse boundaries. It is reliable
only when the propagated field remains adequately represented inside the
chosen window and the transfer function is adequately sampled.

For the unperturbed 6 micrometre target-plane Gaussian used here, Gaussian
beam geometry predicts approximately:

| Absolute distance from waist | Intensity FWHM |
|---:|---:|
| 1.56 m, corresponding to the active legacy detector | 31.2 micrometres |
| 6.56 m, corresponding to the active clean detector | 130.6 micrometres |

The clean output window is only 32.768 micrometres wide. Thus the expected
unperturbed beam at the clean detector is much wider than the represented
plane. Significant periodic wrap-around or aliasing should be expected at
6.31 m unless the calculation is redesigned with a larger physical field of
view, a scaled propagator, or an explicitly sampled detector plane.

The legacy window is 65.536 micrometres wide at an absolute distance of 1.56
m. It contains substantially more of the expected beam, and LightPipes'
zero-padded convolution reduces circular wrap-around, although cropping and
finite-window effects can still remain.

Consequently, describing the clean propagator as "exact" refers to the
continuous angular-spectrum transfer function. It does not by itself prove
that the current discrete 4096 by 4096, 8 nm, 6.31 m calculation is converged.

## How to make a controlled one-to-one comparison

To test implementation differences rather than parameter differences, both
workflows should use the same:

- `PCI.py` revision and copper constants;
- photon energy and bandwidth;
- Gaussian source waist and target position;
- grid size, pixel size, and physical field of view;
- wire radius, voxel geometry, interpolation, and offsets;
- sample-to-detector propagation distance;
- propagation method and boundary padding;
- detector crop, normalization, and TIFF data type.

For a direct reproduction of the active legacy PCI files, configure the clean
workflow with `N=8192`, an 8 nm pixel, a 1.31 m propagation distance, and the
same eight offsets, then use either the original LightPipes sequence or
`PCI.py`'s `fresnel_convolution_propagate_to_position()` compatibility method.
The clean direct two-dimensional wire projection can be retained for the
legacy integer-voxel offsets.

For a comparison of propagators, first generate one common complex exit field
and pass an unchanged copy to both angular-spectrum and LightPipes Fresnel
propagation. Compare:

1. total intensity retained in the output window;
2. normalized central lineouts;
3. fringe positions and visibility;
4. differences near the transverse boundaries; and
5. convergence as the physical field of view and padding are increased.

Raw values from the current saved TIFFs should not be interpreted as evidence
of a propagator difference, because grid width, detector distance, offset
coverage, boundary handling, and output organization all change at the same
time.

## Conclusion

The common PCI physics is a divergent Gaussian field multiplied by a thin
copper-wire amplitude and phase screen, followed by free-space propagation
and the detector intensity \(|E|^2\). The clean and legacy notebooks agree on
the source and target model but currently answer different numerical
questions:

- clean PCI: one zero-offset, 6.31 m exact angular-spectrum calculation on a
  4096 by 4096 fixed grid, plus a separate absorption-only exit scan;
- legacy PCI: eight offset-dependent, 1.31 m LightPipes Fresnel calculations
  on an 8192 by 8192 fixed grid, embedded in a combined SAXS workflow.

These differences must be removed before their PCI images can be compared
quantitatively.
