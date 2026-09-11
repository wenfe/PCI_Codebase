# SAXS intensity calculation: workflow, Fresnel propagation, and the Fraunhofer limit

This summary follows [`PCI.py`](../SAXS_asymmetry/PCI.py), [`SAXS-PCI.md`](SAXS-PCI.md), and [`01_calculate_and_save_data.ipynb`](../SAXS_asymmetry/01_calculate_and_save_data.ipynb). It complements the [PCI intensity workflow](pci_intensity_workflow.md).

## Starting point: Rayleigh–Sommerfeld propagation in real space

For a known sample-exit field, the scalar free-space propagation problem starts
with the real-space Rayleigh–Sommerfeld I convolution:

$$
E_D=E_{\mathrm{exit}}*h_{\mathrm{RS}},
\qquad
h_{\mathrm{RS}}(\Delta x,\Delta y;L)
=\frac{L e^{ikR}}{i\lambda R^2}\left(1+\frac{i}{kR}\right),
\qquad R=\sqrt{\Delta x^2+\Delta y^2+L^2}.
$$

Here $L>0$, $k=2\pi/\lambda$, and the time convention is $e^{-i\omega t}$.
Angular spectrum expresses the same propagation in Fourier space through
$\mathcal F[h_{\mathrm{RS}}]=e^{ik_zL}$. The SAXS calculation uses its **paraxial
Fresnel approximation**, which can also be evaluated with a Fourier transform.
See the [real-space foundation and approximation hierarchy](propagators.md#rayleighsommerfeld-real-space-foundation).

## Implemented SAXS workflow

**The current SAXS calculation uses single-FFT Fresnel diffraction. Fraunhofer diffraction is its far-field approximation, obtained by neglecting the input quadratic propagation phase.** The code retains that phase, so calling its implemented algorithm “Fraunhofer diffraction” would be inaccurate.

The physical sequence is

```text
Gaussian or measured illumination, including phase
    -> complex field at the wire
Projected Cu thickness + material optical constants
    -> sample amplitude transmission and phase shift
Incident field × sample transmission
    -> complex exit field
Multiply by input Fresnel phase -> FFT -> output Fresnel factor
    -> complex detector field
Squared magnitude |E|²
    -> 2-D SAXS intensity
Average selected detector rows -> exclude central q region -> sum left/right
    -> 1-D SAXS profile and asymmetry observables
```

## 1. The diffraction equation behind the code

Let $(x,y)$ denote sample-plane coordinates, $(X,Y)$ detector-plane coordinates, and $L$ the **sample-to-detector distance**. For wavelength $\lambda$ and $k=2\pi/\lambda$, the Fresnel diffraction integral is

$$
E_D(X,Y)=\frac{e^{ikL}}{i\lambda L}
\iint E_{\mathrm{exit}}(x,y)
\exp\!\left[\frac{ik}{2L}\big((X-x)^2+(Y-y)^2\big)\right]
\,\mathrm dx\,\mathrm dy.
$$

Expanding the squares separates the expression into an output phase and a Fourier transform:

$$
E_D(X,Y)=\frac{e^{ikL}}{i\lambda L}
e^{ik(X^2+Y^2)/(2L)}
\mathcal F\!\left[
E_{\mathrm{exit}}(x,y)e^{ik(x^2+y^2)/(2L)}
\right](q_x,q_y),
$$

$$
q_x=\frac{kX}{L},\qquad q_y=\frac{kY}{L},
\qquad
\mathcal F[g](q_x,q_y)=\iint g(x,y)e^{-i(q_xx+q_yy)}\,\mathrm dx\,\mathrm dy.
$$

This is the equation developed in `SAXS-PCI.md` and implemented, with the discrete normalization caveat below, by `XFEL.lorentz_propagate_to_position()`. The function name is historical; the calculation is Fresnel wave propagation.

The detector intensity is

$$
I_D(X,Y)=\frac{1}{(\lambda L)^2}
\left|\mathcal F\!\left[
E_{\mathrm{exit}}e^{ik(x^2+y^2)/(2L)}
\right]\right|^2.
$$

The output phase and global phase have unit magnitude and disappear when calculating this intensity. **The input quadratic phase remains inside the Fourier transform and can change the intensity pattern.** That placement is the decisive distinction from Fraunhofer propagation.

## 2. Construct the incident and sample-exit fields

### Illumination at the wire

Notebook 01 creates an XFEL with `make_xfel()` and chooses the Gaussian source waist using `source_waist_for_target_fwhm()`. `gaussian_XFEL.initialize_to_position()` evaluates a paraxial Gaussian field at `Z_TARGET`.

For a target intensity FWHM $d$, the target Gaussian radius is $w_t=d/\sqrt{2\ln2}$. The code solves

$$
w_t^2=w_0^2+\left(\frac{\lambda z_t}{\pi w_0}\right)^2
$$

for the source waist $w_0$. The smaller-waist root is labeled “divergent,” and the larger-waist root “collimated” or “large-root.” They can have the same intensity width at the sample while having different wavefront curvature. The large-root beam still has finite curvature.

The implemented Gaussian field has the form

$$
E_{\mathrm{in}}(x,y)=\frac{C}{q_G}
e^{-(x^2+y^2)/w_t^2}
e^{-ik(x^2+y^2)/(2R_t)},
\quad
\frac{1}{q_G}=\frac{1}{R_t}-i\frac{\lambda}{\pi w_t^2},
\quad C=2.3\times10^{10}.
$$

The amplitude determines which part of the wire is illuminated; the phase determines local propagation directions. The source phase is part of the diffraction input, including when considering a Fraunhofer approximation.

**Source-sign caveat:** the negative curvature phase above, combined with the positive-sign downstream Fresnel propagator, describes converging curvature for positive $R_t$. The notebook's “divergent” label records the selected waist root and intended geometry, but this phase convention needs reconciliation before quantitatively interpreting divergence or magnification. The same issue is described in the PCI workflow.

### Projected wire and transmission

`make_projected_wire(offset_um)` builds a Cu wire through the notebook's `ProjectedWire` subclass. It samples the cylindrical chord

$$
t(x)=2\sqrt{a^2-(x-x_0)^2}
\quad\text{inside the wire},
$$

sets thickness to zero outside it, applies the selected boundary blur, broadcasts the profile along the wire, and shifts the resulting projection. Although the helper is named `voxelized_chord_profile`, its current expression samples the analytic square-root chord; it does not count a three-dimensional voxel volume.

The sample changes both amplitude and phase:

$$
E_{\mathrm{exit}}(x,y)
=E_{\mathrm{in}}(x,y)
e^{-\mu t(x,y)/2}e^{-ik\delta t(x,y)}.
$$

`Target.get_absorption()` supplies field transmission, `Target.get_phase_shift()` supplies $k\delta t$, and `propagate_through_target()` interpolates those two maps separately onto the XFEL grid before constructing the complex exit field.

Physically, attenuation removes intensity from the transmitted coherent beam, while thickness-dependent phase changes its subsequent interference. The code retains the full transmission exponential. At 8.2 keV, its Cu model gives approximately −9.79 radians of phase change through the 10 µm central chord, so a weak-phase expansion is not quantitatively justified throughout the wire.

The implemented attenuation coefficient is $\mu_{\mathrm{code}}=10E_\gamma\beta$ in nm⁻¹, approximately 1.34% below $2k\beta$. The [PCI workflow](pci_intensity_workflow.md) details the material constants, units, and interpolation behavior.

## 3. Trace the SAXS propagation in `PCI.py`

For each Gaussian case and offset, notebook 01 calls

```text
simulate_gaussian_saxs_intensity(source_waist_nm, offset_um)
    -> make_xfel(source_waist_nm)
    -> make_projected_wire(offset_um)
    -> jungfrau(category="SAXS", position=Z_TARGET + Z_SAXS_DETECTOR)
    -> Beamline.propagate_XFEL_to(detector=detector)
    -> XFEL.propagate_to(...)
    -> initialize_to_position(target.position)
    -> propagate_through_target(...)
    -> lorentz_propagate_to_position(position=sample_to_detector_distance)
    -> xfel.intensity_detector
```

The `"SAXS"` detector category selects `lorentz_propagate_to_position()`. The `"PCI"` category instead selects angular spectrum propagation. The source and sample-transmission physics are shared.

The SAXS propagator's essential operations are:

```python
# Reduced form of the existing implementation; all lengths are in nm.
new_pixel_size = wavelength * L / (N * old_pixel_size)

U = fft2(field_in * np.exp(1j * k * (x**2 + y**2) / (2 * L)))
X, Y = output_grid(new_pixel_size, N)
R = np.exp(1j * k * L) / (1j * wavelength * L)
R = R * np.exp(1j * k * (X**2 + Y**2) / (2 * L))

field_out = R * fftshift(U)
intensity = np.abs(field_out)**2
```

`output_grid` here represents the method's `_define_image_scale()` call. The output coordinates are newly sampled detector coordinates, not the original sample coordinates. When the field is stored on the XFEL object, `intensity_detector` recomputes its squared magnitude; no plotting call is needed.

There is one forward FFT and no inverse FFT in this numerical form, because the transformed coordinates map directly to the detector plane. That fact alone does not imply Fraunhofer diffraction: the input Fresnel phase is still present.

Two discrete conventions matter when comparing this code with the continuous equation:

- The code omits the input pixel-area factor $\Delta x\Delta y$ multiplying the FFT. Its returned intensity is therefore the unnormalized FFT magnitude squared divided by $(\lambda L)^2$, rather than a fully normalized continuous diffraction intensity.
- The stored input is centered in the array, but the code does not apply `ifftshift` before `fft2`. Relative to a consistently centered-coordinate transform, this adds an output phase ramp, which cancels in the detector intensity. It matters if comparing complex fields or using them for further coherent propagation.

## 4. Detector coordinates and the SAXS q axis

A single-FFT Fresnel calculation links the input and output sampling:

$$
\Delta X=\frac{\lambda L}{N\Delta x},\qquad
\Delta q_x=\frac{k\Delta X}{L}=\frac{2\pi}{N\Delta x}.
$$

For a plane wave incident along the optical axis, $q_x\simeq kX/L$ is the small-angle transverse momentum transfer. The total scattering-vector magnitude for scattering angle $\alpha$ is $q=2k\sin(\alpha/2)\simeq k\alpha$. With curved illumination, the notebook's signed q axis remains a detector coordinate relative to the nominal optical axis; the incident field contains a range of local directions.

| Current notebook parameter | Value |
|---|---|
| Photon energy and wavelength | 8.2 keV; approximately 0.15120 nm |
| Input grid | $4096\times4096$, $\Delta x=8$ nm |
| Sample position | 0.25 m from the source reference |
| SAXS propagation distance | 1.31 m after the sample |
| Detector absolute position used by `Beamline` | 1.56 m |
| Calculated detector pixel spacing | Approximately 6.04469 µm |
| Calculated detector window width | Approximately 24.7590 mm |
| FFT q-bin spacing | Approximately $1.917476\times10^{-4}$ nm⁻¹ |
| Negative Nyquist coordinate | $-\pi/\Delta x\simeq-0.392699$ nm⁻¹ |

These are the numerical detector sampling values. The `jungfrau` class name does not cause the propagated intensity to be rebinned onto a physical detector's pixels.

The exact centered FFT axis is

```python
q_fft = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(N, d=dx))
# Equivalent for the current even N:
q_fft = (np.arange(N) - N // 2) * (2 * np.pi / (N * dx))
```

Notebook 01 also defines `Q_AXIS = np.linspace(-Q_MAX, Q_MAX, N)`. This is slightly different: it includes both endpoints, uses $N-1$ intervals, and has no zero-valued bin for even $N$. Its center-index value is approximately $+9.59\times10^{-5}$ nm⁻¹. The notebook uses this axis for some profile interpolation and realistic-profile masks, while its shifted-mask calculation uses the exact FFT spacing. These conventions should be distinguished in precise q comparisons.

## 5. When would the SAXS calculation become Fraunhofer diffraction?

Fraunhofer propagation makes the additional approximation

$$
\exp\!\left[\frac{ik(x^2+y^2)}{2L}\right]\simeq1
$$

over the significant input field. Then

$$
I_{\mathrm{Fraunhofer}}(X,Y)
\simeq\frac{1}{(\lambda L)^2}
\left|\mathcal F[E_{\mathrm{exit}}](kX/L,kY/L)\right|^2.
$$

This extra step distinguishes Fraunhofer from Fresnel diffraction; both are Fourier-transform calculations. See the derivation in [MIT Optics, Recitation 3, sections 3–4](https://ocw.mit.edu/courses/2-71-optics-spring-2014/821609ddc97b5e4a46e1e5e5c8ba29cc_MIT2_71S14_Rec3.pdf).

For a characteristic illuminated radius $a$, the phase being neglected is approximately

$$
\Delta\phi_F=\frac{\pi a^2}{\lambda L}=\pi N_F,
\qquad N_F=\frac{a^2}{\lambda L}.
$$

Fraunhofer requires this phase variation to be small enough for the desired accuracy. At the notebook's 1.31 m distance:

| Representative transverse radius | $N_F$ | Input Fresnel phase at that radius |
|---|---:|---:|
| Wire radius: 5 µm | 0.1262 | 0.3965 rad |
| Gaussian radius for 6 µm intensity FWHM: 5.096 µm | 0.1311 | 0.4119 rad |
| Gaussian radius for 7.11 µm intensity FWHM: 6.039 µm | 0.1841 | 0.5784 rad |

These are illustrative phase scales, not an error estimate for the final SAXS ratio. The significant illuminated support, Gaussian tails, and observable being compared determine the actual approximation error. They do not establish a deeply asymptotic Fraunhofer regime for the full field; the current implementation retains the Fresnel term.

Even if that propagation phase were neglected, the **incident Gaussian phase would remain in $E_{\mathrm{exit}}$**. With the implemented source sign, the source and input propagation phases combine as

$$
E_{\mathrm{in}}e^{ikr^2/(2L)}
\propto e^{-r^2/w_t^2}
\exp\!\left[\frac{ikr^2}{2}\left(\frac{1}{L}-\frac{1}{R_t}\right)\right].
$$

Approximating propagation as Fraunhofer does not turn a curved incident field into a plane wave.

## 6. Relation to the usual electron-density SAXS formula

The conventional weak-scattering description in `SAXS-PCI.md` gives scattering intensity proportional to the squared Fourier transform of electron density. The transmission calculation connects to that result through

$$
T\simeq1-\frac{\mu t}{2}-ik\delta t,
\qquad
E_{\mathrm{exit}}\simeq E_{\mathrm{in}}
+E_{\mathrm{in}}\left(-\frac{\mu t}{2}-ik\delta t\right).
$$

The first term is the transmitted reference beam. The second is the sample-induced field. For uniform illumination, weak scattering, negligible absorption, and sufficiently small longitudinal momentum transfer, $\delta t$ is proportional to projected electron density and its Fourier transform gives the familiar SAXS amplitude.

The general calculation in `PCI.py` preserves both contributions coherently:

$$
I_D=|E_{\mathrm{reference}}+E_{\mathrm{sample}}|^2.
$$

It therefore includes their interference where they overlap. No mean-density or direct-beam subtraction is performed before propagation. The notebook excludes a central detector region only when reducing the already calculated intensity.

Higher $|q|$ probes finer transverse structure; a sinusoidal spatial period $d$ corresponds to $q=2\pi/d$. Smoothing the projected wire boundaries generally suppresses high-q structure. Here smoothing is applied to thickness before the nonlinear complex transmission is formed, so it should not automatically be equated to multiplying the final intensity by one Gaussian form factor.

Moving the wire changes which thickness and phase gradients lie under the finite Gaussian beam. Together with wavefront curvature and the Fresnel phase, this can change left/right SAXS intensity. A pure translation of an isolated object under uniform plane-wave illumination in the Fraunhofer limit would instead multiply its scattering amplitude by a phase factor and leave its intensity unchanged. The simulated offset dependence thus reflects illumination and propagation as well as sample geometry.

## 7. Notebook 01: images, lineouts, and asymmetry

### Clean Gaussian scans

The clean scan calculates four cases: 6.0 and 7.11 µm target FWHM, each with the small-waist and large-waist roots. Each case uses 43 wire offsets from −10.0 to +10.16 µm in 0.48 µm steps. This grid has no exactly zero offset.

For each case and offset, the notebook saves a float32 detector TIFF and forms a two-row mean:

$$
P(q_x)=\frac{1}{2}\sum_{j\in\{2047,2048\}}I_D(j,q_x).
$$

`mark1300_sides()` excludes the central region using

```python
h = round(0.10 / Q_STEP)  # 522 for the current grid
left  = lineout[:2048-h].sum()
right = lineout[2048+h:].sum()
```

This approximately selects $|q_x|\ge0.10$ nm⁻¹. The mask uses signed horizontal q, not radial $\sqrt{q_x^2+q_y^2}$. Its integer slices are not perfectly mirror-symmetric on the even FFT grid: the nearest included negative bin is −523 times `Q_STEP`, while the nearest positive bin is +522 times `Q_STEP`.

The raw table contains offset in **nm**, left sum $S_L$, and right sum $S_R$. The common fraction

$$
f_L=\frac{S_L}{S_L+S_R}
$$

is the share of the selected side signal on the left. It is not transmission through the wire, nor the fraction of all incident photons. Equal selected side signals give $f_L=0.5$; the alternative signed asymmetry would be $(S_L-S_R)/(S_L+S_R)=2f_L-1$.

### Shifted detector-center masks

For the two small-waist cases, the notebook also calculates two-row and ten-row fractions with the mask center shifted to $q_c=+0.005$ nm⁻¹. It approximately retains

$$
q_x<-0.095\;\mathrm{nm}^{-1}
\quad\text{and}\quad
q_x>+0.105\;\mathrm{nm}^{-1},
$$

using fractional weights where a bin crosses a mask boundary. This changes the integration windows; it does not shift the incident beam or recompute propagation. A shifted mask can yield a non-half fraction even for a pattern symmetric about zero.

### Profiles for plotting and other branches

| Notebook branch | Calculation or reduction |
|---|---|
| Clean profile bundle | Two-row means interpolated onto the experimental q axis, divided by each profile's own maximum, then multiplied by 2. These are display-normalized profiles. |
| Methods profiles and gallery | Reuse clean 7.11 µm SAXS results; use ten-row means for the Methods profile comparison. Gallery “PCI” images are sample-exit intensity. |
| Divergence scan | Recalculate small-root target FWHM 6, 9, and 12 µm and large-root 12 µm cases on 50 offsets; reuse the 7.11 µm clean case on its 43 offsets. |
| Realistic illumination | Resample a measured intensity image to the beam grid, normalize its sum to 1, use its square root as amplitude, and supply modeled Gaussian curvature from the 7.11 µm case. Propagate the complex exit field with the same Fresnel function. |
| Realistic SAXS reduction | Ten-row means, `Q_AXIS < -0.10` and `Q_AXIS > +0.10` masks, and $S_L/(S_L+S_R)$. The saved profile bundle retains raw ten-row curves. |
| Experimental comparison images | Reuse the clean small-waist 7.11 µm SAXS TIFFs; this is not another diffraction algorithm. |

The realistic field contains measured amplitude and assumed phase, not a fully measured complex wavefront. The current `FORCE_RECALCULATE=True` causes the main clean and realistic computations to run again; existing TIFFs can be reused by the corresponding paths when that flag is false.

## 8. Output files and quantitative interpretation

The current output base is `SAXS_asymmetry/outputs/sigmaL_4nm_sigmaR_4nm/`, reflecting 4 nm blur at both wire boundaries.

| Artifact relative to that base | Contents |
|---|---|
| `saxs/detector_tiffs/Data_8nm/<case>/SAXS_Offset<offset>um.tif` | Two-dimensional detector intensity in simulation units. |
| `saxs/tables/*SAXS_asymmetry_Mark1300_*.dat` | Offset in nm and raw two-row left/right sums. |
| `combined_plot_data/clean_saxs_profiles.npz` | Experimental q reference, offsets in µm, and display-normalized profiles. |
| `clean_pci/mark1300_*_shifted_q_mask_left_fraction.dat` | SAXS fractions with the shifted mask, for two-row and ten-row reductions; these remain SAXS observables despite the directory name. |
| `realistic_profile/tables/realistic_profile_saxs_left_right.dat` | Realistic-profile offset in nm, raw side sums, and left fraction. |
| `combined_plot_data/realistic_saxs_lineouts.npz` | q axis, offsets in µm, and raw ten-row profiles. |

The source prefactor, missing FFT pixel-area factor, and absence of detector efficiency and pixel-response modeling mean these arrays are not calibrated photon counts or an absolute differential scattering cross section. Side sums also omit a q-bin integration factor. Common multiplicative factors cancel in a fraction formed from one image, but this does not justify absolute comparisons across different source normalizations, grids, or extraction regions.

The model assumes coherent monochromatic scalar illumination, a projected sample transmission, and paraxial free-space propagation for SAXS. Its retained Fresnel phase is physically relevant; the Gaussian source-sign issue, sample approximation, q-axis conventions, and numerical sampling still need consideration when interpreting quantitative agreement with experiment.
