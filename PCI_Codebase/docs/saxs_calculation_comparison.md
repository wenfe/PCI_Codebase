# SAXS calculation and comparison with `SAXS_PCI_Pointing_Div`

## Summary

[`clean_saxs_design.ipynb`](../SAXS_asymmetry/clean_saxs_design.ipynb) and
[`SAXS_PCI_Pointing_Div.ipynb`](../SAXS_asymmetry/SAXS_PCI_Pointing_Div.ipynb)
use the same underlying SAXS forward model in
[`PCI.py`](../SAXS_asymmetry/PCI.py): a Gaussian XFEL beam illuminates a copper
wire, the wire applies absorption and phase shift to the complex field, and the
field is propagated to the far-field detector with the SAXS Fresnel-FFT
propagator. The detector signal is the squared magnitude of the propagated
field.

They are therefore the same **physical workflow**, but they are not identical
**numerical workflows** in their current form. In particular, they use
different beam-grid sizes and active target-plane beam sizes, and their output
and post-processing steps are organized differently.

## How SAXS is calculated

### 1. Define the photon wavelength

Both notebooks use a photon energy of 8.2 keV. `PCI.py` represents transverse
lengths in nanometres and calculates

\[
k = 5.06773076 E_{\mathrm{keV}},
\qquad
\lambda = \frac{2\pi}{k}.
\]

For 8.2 keV,

\[
\lambda \simeq 0.15120\ \mathrm{nm}.
\]

### 2. Construct the incident Gaussian beam

The beam waist is at \(z=0\), and the wire is at

\[
z_t=0.25\ \mathrm{m}.
\]

For a Gaussian beam with waist radius \(w_0\),

\[
z_R = \frac{\pi w_0^2}{\lambda},
\qquad
w(z) = w_0\sqrt{1+\left(\frac{z}{z_R}\right)^2}.
\]

The intensity FWHM used by this code is

\[
\mathrm{FWHM}(z)=\sqrt{2\ln 2}\,w(z).
\]

`clean_saxs_design.ipynb` solves this relation for the smaller, divergent
waist that produces a 7.5 micrometre FWHM at the target. The resulting source
waist is approximately

\[
w_0=1.98823\ \mathrm{micrometres}.
\]

`PCI.gaussian_XFEL.initialize_to_position()` evaluates the beam amplitude and
curved phase front at the wire plane.

### 3. Calculate the projected Cu-wire thickness

The wire radius is 5 micrometres. For an ideal cylinder displaced by \(x_0\),
the projected thickness along the X-ray direction is

\[
t(x)=
\begin{cases}
2\sqrt{R^2-(x-x_0)^2}, & |x-x_0|\leq R,\\
0, & |x-x_0|>R.
\end{cases}
\]

Both workflows discretize this projection using 20 nm target voxels. The
legacy notebook constructs a full three-dimensional `PCI.wire` volume and sums
it along the propagation direction. The clean notebook's `projected_wire`
class evaluates the equivalent two-dimensional voxel chord lengths directly,
avoiding the unused 2000 cubed volume.

For the scan positions used here, every 2.5 micrometre displacement is an
integer multiple of the 20 nm voxel size. Consequently, the clean projection
has the same intended voxel geometry as the legacy projection without a
fractional-pixel interpolation difference.

### 4. Apply absorption and phase shift

For a material with refractive index written in terms of \(\delta\) and
\(\beta\), `PCI.py` calculates the field-amplitude transmission and target
phase shift. In compact form, the field immediately after the wire is

\[
E_{\mathrm{exit}}(x,y)
=E_{\mathrm{incident}}(x,y)
\exp\left[-\frac{\mu t(x,y)}{2}\right]
\exp\left[-i k\delta t(x,y)\right].
\]

The factor of one half in the absorption exponent is present because this is
the transmission of the **field amplitude**. The corresponding intensity
attenuation is \(\exp[-\mu t]\). This operation is implemented by
`XFEL.propagate_through_target()` in `PCI.py`.

### 5. Propagate to the SAXS detector

The detector is placed 1.31 m after the wire, at an absolute position of

\[
z_d=z_t+1.31\ \mathrm{m}=1.56\ \mathrm{m}
\]

relative to the source waist. The propagation distance after the target is
therefore 1.31 m.

Setting the detector category to `"SAXS"` makes
`XFEL.propagate_to()` call `lorentz_propagate_to_position()`. Despite the
historical method name, this routine implements a single-FFT Fresnel
propagator:

\[
E_D(X,Y)=
\frac{e^{ikz}}{i\lambda z}
\exp\left[\frac{ik}{2z}(X^2+Y^2)\right]
\mathcal{F}\left\{
E_{\mathrm{exit}}(x,y)
\exp\left[\frac{ik}{2z}(x^2+y^2)\right]
\right\}.
\]

The output-plane pixel size is rescaled by the Fresnel transform:

\[
\Delta X=\frac{\lambda z}{N\Delta x},
\]

where \(N\) and \(\Delta x\) are the target-plane grid size and pixel size.

### 6. Calculate detector intensity and the q axis

The simulated SAXS intensity is

\[
I_{\mathrm{SAXS}}(X,Y)=|E_D(X,Y)|^2.
\]

The Fourier-grid momentum-transfer coordinates are

\[
q_x=2\pi f_x,
\qquad
\Delta q=\frac{2\pi}{N\Delta x},
\qquad
|q|_{\max}\simeq\frac{\pi}{\Delta x}.
\]

With an 8 nm input pixel, both grids cover approximately
\(-0.3927\) to \(+0.3927\ \mathrm{nm}^{-1}\). Their sampling differs:

| Grid | \(\Delta q\) | Fresnel output pixel at 1.31 m |
|---|---:|---:|
| 4096 by 4096 | \(1.91748\times10^{-4}\ \mathrm{nm}^{-1}\) | 6.0447 micrometres |
| 8192 by 8192 | \(9.58738\times10^{-5}\ \mathrm{nm}^{-1}\) | 3.0223 micrometres |

For an exact FFT-bin axis, use

```python
q_axis = 2 * np.pi * np.fft.fftshift(
    np.fft.fftfreq(N, d=pixel_size_nm)
)
```

Both notebooks currently use an inclusive `linspace` for some plotting and
interpolation. That is a close approximation, but its spacing is based on
\(N-1\) intervals and is not exactly the FFT-bin spacing above.

### 7. Calculate the Mark1300 left/right SAXS observable

The clean workflow stores each detector intensity as a float32 TIFF, reopens
the TIFF, and averages exactly the two central detector rows:

```python
center = N_GRID // 2
lineout = saxs_intensity[center - 1:center + 1, :].mean(axis=0)
```

It then removes the central region \(|q_x|<0.10\ \mathrm{nm}^{-1}\) and sums
the two sidebands:

\[
L=\sum_{q_x<-0.10}I(q_x),
\qquad
R=\sum_{q_x>+0.10}I(q_x).
\]

The reported normalized asymmetry is

\[
f_L=\frac{L}{L+R}.
\]

On the 4096 grid, the clean notebook excludes 522 pixels on each side of the
center, corresponding to an effective cutoff of
\(0.100092\ \mathrm{nm}^{-1}\). The legacy analysis excludes 1040 pixels on
the 8192 grid, corresponding to \(0.099709\ \mathrm{nm}^{-1}\). Thus the two
pixel masks represent essentially the same physical q cutoff.

The interpolation onto the experimental q coordinates and normalization used
in plots happen after the detector pattern is calculated. They do not create
the simulated SAXS pattern and do not change the raw Mark1300 sums.

## Comparison with `SAXS_PCI_Pointing_Div`

| Component | `clean_saxs_design.ipynb` | `SAXS_PCI_Pointing_Div.ipynb` |
|---|---|---|
| Physics implementation | Current `PCI.py` | Current `PCI.py` when rerun |
| Photon energy | 8.2 keV | 8.2 keV |
| Input pixel size | 8 nm | 8 nm |
| Beam grid | 4096 by 4096 | 8192 by 8192 |
| Wire position | 0.25 m from waist | Same |
| Detector distance after wire | 1.31 m | Same |
| Wire | Cu, 5 micrometre radius | Same |
| Target discretization | 20 nm, 2000 pixels, direct 2-D projection | 20 nm, 2000 cubed full-volume construction |
| Active target-plane FWHM | 7.5 micrometres | 6 micrometres in the committed active cell |
| Active offsets | -10 to +10 micrometres, inclusive | -10 to +7.5 micrometres |
| SAXS propagator | `PCI.py` Fresnel single FFT | Same |
| Saved SAXS image | Compressed float32 TIFF | TIFF from the in-memory array |
| Simulation lineout | Two central rows | Ten central rows for the generation notebook's experimental-profile plot |
| Mark1300 lineout | Two central rows | Two central rows in `PlotSAXS_Pointing_Div.ipynb` |
| Mark1300 cutoff | Physical 0.10 inverse nm converted to 522 pixels | Hard-coded 1040 pixels, approximately 0.10 inverse nm |
| Workflow organization | Simulation and Mark1300 analysis together | TIFF generation and asymmetry analysis split between two notebooks |
| PCI result | Separate analytic target-exit attenuation comparison | Additional LightPipes Fresnel propagation to form a PCI detector image |

### Common core workflow

The common sequence is:

```text
Gaussian source
    -> propagate to wire
    -> apply Cu absorption and phase
    -> SAXS Fresnel FFT to detector
    -> detector intensity |E|^2
    -> detector TIFF / lineout
    -> q-space sideband integration
    -> L, R, and L/(L+R)
```

The beamline call in both notebooks eventually follows this same `PCI.py`
path:

```python
beamline.propagate_XFEL_to(detector=detector)
```

because the detector has `category="SAXS"`.

### Important differences

1. **The committed beam configurations differ.** The clean notebook targets a
   7.5 micrometre FWHM, whereas the active legacy cell is configured for 6
   micrometres. The legacy notebook contains commented alternatives, but those
   are not its active configuration.

2. **The grids differ.** Reducing 8192 to 4096 halves the target-plane field of
   view and doubles both the q-bin spacing and Fresnel detector-plane pixel
   size. The q range remains approximately unchanged because the 8 nm input
   pixel is unchanged.

3. **The clean notebook consolidates two legacy stages.**
   `SAXS_PCI_Pointing_Div.ipynb` generates the SAXS TIFFs, while
   `PlotSAXS_Pointing_Div.ipynb` reopens them and calculates the two-row
   Mark1300 asymmetry. The clean notebook performs both operations explicitly
   in one function.

4. **The legacy generation lineout is not its final asymmetry lineout.** It
   averages ten central rows when overlaying simulation and experimental
   profiles. The later Mark1300 analysis averages two central rows. The clean
   notebook intentionally follows the latter convention.

5. **The PCI comparisons are different quantities.** The legacy notebook also
   reconstructs the target-exit field in LightPipes and propagates it to a PCI
   detector. The clean notebook's optional PCI comparison calculates only an
   unpropagated target-exit attenuation profile. That curve must not be
   interpreted as a PCI detector simulation.

6. **Archived TIFFs may reflect an older run.** Existing files under
   `SAXS_asymmetry/outputs/saxs/detector_tiffs/Data_8nm` are outputs, not a
   guarantee that the currently active cells have
   exactly the settings or `PCI.py` version that originally produced them.

## Are the results directly interchangeable?

No. The two implementations share the same physical model, but their current
results are not expected to agree point by point because \(N\), beam FWHM,
offset coverage, and some lineout rules differ.

To make a controlled one-to-one comparison, use the same:

- `PCI.py` revision;
- grid size and input pixel size;
- photon energy and bandwidth;
- source waist or target-plane beam FWHM;
- wire radius, voxel size, projection, and offsets;
- target and detector positions;
- TIFF data type;
- central-row averaging rule; and
- physical q mask.

Raw left/right sums should also be treated as arbitrary internal units. The
FFT implementation does not include an explicit continuous-transform
\((\Delta x)^2\) normalization, and a plain sum does not multiply by
\(\Delta q\). Consequently, raw sums from different grid sizes should not be
compared directly. Ratios such as \(L/(L+R)\) are more robust because common
normalization and bin-width factors cancel.
