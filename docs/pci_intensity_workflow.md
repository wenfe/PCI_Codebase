---
icon: lucide/scan-line
---

# PCI intensity calculation: workflow and physical meaning

This summary follows the documented `PCI.py` implementation, connects it to
the wave-optics discussion in [`SAXS-PCI.md`](SAXS-PCI.md), and explains how
the calculation was used in `01_calculate_and_save_data.ipynb`.

For the corresponding SAXS calculation and its Fresnel/Fraunhofer distinction, see the [SAXS intensity workflow](saxs_intensity_workflow.md).

!!! note "Source location"

    The implementation lives at `src/SAXS_asymmetry/PCI.py` and the workflow at
    `notebooks/saxs_asymmetry/01_calculate_and_save_data.ipynb`.

## Starting point: Rayleigh–Sommerfeld propagation in real space

The general scalar free-space starting point is the Rayleigh–Sommerfeld I
integral. For the complex sample-exit field, wavelength $\lambda$, $k=2\pi/\lambda$,
time dependence $e^{-i\omega t}$, and downstream distance $Z>0$,

$$
E_D(X,Y)=\iint E_{\mathrm{exit}}(x,y)\,
\underbrace{\frac{Z e^{ikR}}{i\lambda R^2}
\left(1+\frac{i}{kR}\right)}_{h_{\mathrm{RS}}(X-x,Y-y;Z)}
\,\mathrm dx\,\mathrm dy,
\qquad R=\sqrt{(X-x)^2+(Y-y)^2+Z^2}.
$$

This sums complex contributions from the input plane in **real space**.
Fourier transformation of the exact kernel gives $\mathcal F[h_{\mathrm{RS}}]=e^{ik_zZ}$,
so angular spectrum is the equivalent **Fourier-space** formulation, including
evanescent decay. See the [real-space foundation and derivation](propagators.md#rayleighsommerfeld-real-space-foundation)
for assumptions, conventions, and the Fresnel limit. The code evaluates this
propagation through angular spectrum.

## Implemented PCI workflow

**The PCI branch propagates the complex sample-exit field by the angular spectrum method, then calculates intensity as its squared magnitude.** Its central equation, for a single material, is

$$
I_{\mathrm{PCI}}(x,y;Z)=
\left|
\mathcal F^{-1}\!\left[
\mathcal F\!\left\{
E_{\mathrm{in}}(x,y)
e^{-\mu t(x,y)/2}
e^{-ik\delta t(x,y)}
\right\}
e^{ik_zZ}
\right]
\right|^2,
\qquad k_z=\sqrt{k^2-k_x^2-k_y^2}.
$$

Here $t$ is the material path length, $\delta$ determines the phase change, $\mu$ determines intensity attenuation, and $Z$ is the distance **from the sample to the observation plane**. The implementation details of $\mu$ and grid interpolation are explained below.

```text
Photon energy + source waist + sample position
    -> complex incident field at the sample
Wire geometry + material optical constants
    -> projected thickness -> amplitude transmission and phase change
Incident field × complex sample transmission
    -> complex exit field
FFT -> multiply each angular component by exp(i kz Z) -> inverse FFT
    -> complex field at the PCI plane
Squared magnitude |E|²
    -> PCI intensity image
```

## 1. Define the grid and incident field

`XFEL` defines an $N\times N$ transverse grid with pixel spacing $\Delta x=\Delta y$. Lengths inside `PCI.py` are in **nanometres**: `nm = 1`, `um = 1e3`, and `m = 1e9`. Photon energy is in keV.

The wavelength and vacuum wavenumber are

$$
\lambda\simeq\frac{1.239842}{E_\gamma}\;\mathrm{nm},
\qquad k=\frac{2\pi}{\lambda}.
$$

`get_k()` uses the equivalent rounded conversion `5.06773076 * photon_energy`; `get_lambda()` returns $2\pi/k$.

`gaussian_XFEL.initialize_to_position(z)` evaluates a paraxial Gaussian source model directly at the sample position. It does not numerically march the field from the focus to that first sample. The beam parameters are

$$
z_R=\frac{\pi w_0^2}{\lambda},\qquad
w(z)=w_0\sqrt{1+(z/z_R)^2},\qquad
R(z)=\frac{z^2+z_R^2}{z}.
$$

At the focus, the code sets $R=\infty$. With $r^2=x^2+y^2$, its actual field expression is

$$
\frac{1}{q_G}=\frac{1}{R}-i\frac{\lambda}{\pi w^2},
\qquad
E_{\mathrm{in}}=\frac{C}{q_G}
\exp\!\left[-\frac{ikr^2}{2q_G}\right]
=\frac{C}{q_G}e^{-r^2/w^2}e^{-ikr^2/(2R)},
\quad C=2.3\times10^{10}.
$$

The Gaussian envelope controls which parts of the wire are illuminated. The transverse phase controls the wavefront curvature and therefore its subsequent focusing or spreading. $w$ is the radius where intensity falls to $e^{-2}$ of its peak; the intensity FWHM diameter is $\sqrt{2\ln2}\,w\simeq1.17741w$. $q_G$ is the Gaussian beam parameter, distinct from SAXS momentum transfer.

**Phase-convention caveat:** the negative curvature phase written above is what the code implements. Combined with the positive-sign angular spectrum propagator below, positive $R$ represents a converging wavefront. This needs to be reconciled with the notebook's intended “divergent” source interpretation; the width formula alone does not establish propagation direction. This document describes the existing code without changing that sign.

## 2. Convert the sample into a complex transmission

### Project the geometry

The sample is represented by material path length along the beam:

$$
t_i(x,y)=\int f_i(x,y,z)\,\mathrm dz
\simeq\sum_j f_i(x,y,z_j)\,\Delta z,
$$

where $f_i$ is material occupancy or relative density. This is the **projection approximation**: one transverse transmission screen represents the sample; diffraction inside its thickness is not calculated.

The base `wire._get_projection()` builds a voxel volume, sums along axis 2, multiplies by `voxel_size`, and rotates/shifts the projection. For an ideal straight cylinder, the corresponding continuum thickness is

$$
t(x)=
\begin{cases}
2\sqrt{a^2-(x-x_0)^2},& |x-x_0|\le a,\\
0,& |x-x_0|>a,
\end{cases}
$$

with radius $a$ and transverse offset $x_0$. The notebook's `ProjectedWire` overrides the volume calculation: it samples this chord directly, blurs the profile at the boundaries, broadcasts it into two dimensions, and shifts it. The blur models a smooth projected boundary; it is not a detector blur or a simulation of random three-dimensional roughness.

### Calculate attenuation and phase

For the convention $n=1-\delta+i\beta$ with time dependence $e^{-i\omega t}$,

$$
T(x,y)=e^{-\tau(x,y)/2}e^{-i\Delta\phi(x,y)},
\quad
\tau=\sum_i\mu_i t_i,
\quad
\Delta\phi=\sum_i k\delta_i t_i.
$$

The physical relationship is $\mu=2k\beta=4\pi\beta/\lambda$: $\beta$ attenuates the field, while the intensity attenuation coefficient is twice the field coefficient. The electron-density relation is $\delta=r_e\lambda^2\rho_e/(2\pi)$ away from corrections to the atomic scattering factors. These relations connect refraction, absorption, and scattering. See the [LBNL X-Ray Data Booklet, sections 1.7 and 3.1](https://xdb.lbl.gov/xdb.pdf).

The current material implementation uses

$$
\delta_{\mathrm{code}}
=0.933386\,(602.2\,\rho\,Z/A)\,
\frac{r_e\lambda^2}{2\pi},
\qquad
\beta_{\mathrm{code}}=\frac{a_\mu\rho}{E_\gamma^{p_\mu}},
\qquad
\mu_{\mathrm{code}}=10E_\gamma\beta_{\mathrm{code}}.
$$

Here $\rho$ is in g/cm³; the factor 602.2 converts $\rho Z/A$ to electron density in nm⁻³. The factor 0.933386 is a fixed correction in the code. `Cu` supplies the empirical absorption parameters $a_\mu$ and $p_\mu$.

`Material._get_phase_shift()` supplies $k\delta$, `Target.get_phase_shift()` multiplies it by the projected thickness, and `Target.get_absorption()` returns **field transmission** $e^{-\tau/2}$.

Despite its comments and printed `[1/um]` label, `_get_mu()` acts as an **intensity attenuation coefficient in nm⁻¹**, because it is multiplied by thickness in nm inside $e^{-\mu t/2}$. Its conversion `10 * E * beta` is about 1.34% below the physical $2k\beta$ with the code's wavenumber. Thus the physical formula and the implemented approximation should not be treated as numerically identical.

### Apply transmission to the incident field

`XFEL.propagate_through_target()` performs these operations:

1. Interpolate the target's amplitude transmission onto the beam grid using `_interpolate_target2beam()` and `RectBivariateSpline`.
2. Extract the incident amplitude and phase from the complex field.
3. Multiply the amplitude by the interpolated transmission.
4. Interpolate $\Delta\phi$ onto the beam grid and subtract it from the incident phase.
5. Reconstruct the complex exit field:

$$
E_{\mathrm{exit}}=A_{\mathrm{in}}T_A
\exp[i(\phi_{\mathrm{in}}-\Delta\phi)].
$$

The library interpolates **amplitude transmission and phase separately**, after their calculation on the target grid. Consequently, interpolating a thickness map and then exponentiating it is not exactly the same discrete operation near an edge.

Immediately after the sample,

$$
I_{\mathrm{exit}}=|E_{\mathrm{exit}}|^2
=I_{\mathrm{in}}T_A^2
\simeq I_{\mathrm{in}}e^{-\mu t}.
$$

The phase factor disappears from this local squared magnitude. A phase-only sample therefore has unchanged exit intensity even though its complex field has changed.

## 3. Propagate by the angular spectrum method to distance Z

`XFEL.spectral_propagate_to_position()` decomposes the exit field into transverse plane-wave components. Here “spectrum” means **spatial/angular spectrum**, not a distribution of photon energies.

For a component with transverse wavenumbers $(k_x,k_y)$, the scalar Helmholtz equation requires

$$
k_x^2+k_y^2+k_z^2=k^2.
$$

Each component evolves independently through homogeneous free space:

$$
\widetilde{E}_Z(k_x,k_y)
=\widetilde{E}_{\mathrm{exit}}(k_x,k_y)H(k_x,k_y;Z),
\qquad H=e^{ik_zZ}.
$$

The function implements the following sequence, with `position` interpreted as propagation distance $Z$:

```python
c = fftshift(fft2(field_in))
kx = 2 * np.pi * fftshift(fftfreq(N, d=pixel_size))
ky = 2 * np.pi * fftshift(fftfreq(N, d=pixel_size))
kx, ky = np.meshgrid(kx, ky)

argument = k**2 - kx**2 - ky**2
root = np.sqrt(np.abs(argument))
kz = np.where(argument >= 0, root, 1j * root)

field_out = ifft2(ifftshift(c * np.exp(1j * kz * Z)))
intensity = np.abs(field_out)**2
```

This is an explanatory extraction; `intensity` is evaluated by the caller or intensity property in the library. `fftshift` and `ifftshift` align array ordering; they do not add a physical optical element.

| Operation | Physical meaning |
|---|---|
| `fft2(field_in)` | Decompose the complete complex wave into components traveling at different angles. |
| `fftfreq` multiplied by $2\pi$ | Convert grid frequencies into transverse wavenumbers, in nm⁻¹. |
| $k_z=\sqrt{k^2-k_x^2-k_y^2}$ | Determine the longitudinal wavenumber for each component. |
| Multiply by $e^{ik_zZ}$ | Advance each component by its propagation phase. |
| `ifft2` | Recombine those components coherently at the observation plane. |
| Squared magnitude | Convert the resulting field into the intensity observable. |

For $k_x^2+k_y^2\le k^2$, $k_z$ is real: these components propagate, with $k_x/k$ and $k_y/k$ giving transverse direction cosines. For $k_x^2+k_y^2>k^2$, the code chooses $k_z=i\kappa$ with $\kappa>0$, so $e^{ik_zZ}=e^{-\kappa Z}$ decays downstream. These are evanescent components.

The square-root kernel is **exact for homogeneous scalar Helmholtz propagation**. It does not make the paraxial expansion used by Fresnel propagation. Numerical sampling and the scalar/sample approximations remain separate limitations. For a research treatment of FFT angular spectrum diffraction, see [Carbajal-Dominguez et al.](https://arxiv.org/abs/1002.1999).

The FFT/inverse-FFT pair preserves the input pixel spacing and array size. It does not automatically enlarge the field of view as the beam spreads.

## 4. Why phase becomes intensity contrast

The sample changes the relative phases across the wavefront. After propagation, contributions originating at different transverse positions overlap. Depending on their phase difference, they interfere constructively or destructively, producing bright and dark structure, often strongest near sample boundaries.

Writing the propagated field as a reference field plus the sample-induced change gives

$$
I=|E_{\mathrm{ref}}+E_{\mathrm{obj}}|^2
=|E_{\mathrm{ref}}|^2+|E_{\mathrm{obj}}|^2
+2\operatorname{Re}(E_{\mathrm{ref}}^*E_{\mathrm{obj}}).
$$

The cross term is the interference contribution. Propagating the full complex field retains it automatically. Propagating the exit **intensity** would discard the required phase information.

The short-distance, paraxial limit makes this connection explicit through the transport-of-intensity equation:

$$
\frac{\partial I}{\partial z}
=-\frac{1}{k}\nabla_\perp\!\cdot
\left(I\nabla_\perp\phi\right).
$$

For uniform incident intensity $I_0$, negligible absorption, and $\phi=-k\delta t$, it gives

$$
I(Z)-I_0\simeq Z I_0\delta\,\nabla_\perp^2t.
$$

This limiting expression explains sensitivity to thickness variations and boundaries. `PCI.py` calculates the propagated field directly; it does not use this approximation to compute its detector image. In particular, the short-distance expression should not be assumed valid for the notebook's 6.31 m propagation.

## 5. Where intensity is calculated and stored

| Code entry or array | Meaning |
|---|---|
| `Beamline.propagate_XFEL_to()` | Calls `XFEL.propagate_to()` using the registered targets and requested observation plane. |
| `XFEL.propagate_to()` | Initializes the source at the first target, applies transmission, and selects the final propagation method. A detector category of `"PCI"`, or no detector, selects angular spectrum. |
| `intensity_beforetarget` | Incident intensity at the target: $|E_{\mathrm{in}}|^2$. |
| `phase_beforetarget` | Incident phase at the target. |
| `intensity_aftertarget` | Sample-exit intensity: $|E_{\mathrm{exit}}|^2$. |
| `phase_aftertarget` | Exit phase: $\phi_{\mathrm{in}}-\Delta\phi$. |
| `XFEL.intensity_detector` | Squared magnitude of the XFEL object's **current stored field**, whatever its plane. |
| `Detector.intensity_detector` | Squared magnitude of the complex field saved on that detector by `set_raw_data()`. |

The intensity property computes `realPart**2 + imagPart**2` when read; plotting is not required. With `reset=False`, propagation returns a field without replacing the object's stored field, so calculate `np.abs(returned_field)**2` to obtain intensity at the returned plane.

At the `Beamline` level, detector position is an absolute longitudinal coordinate; the dispatcher subtracts the last target position. A direct call to `spectral_propagate_to_position(position=L, ...)` instead expects the separation itself.

## 6. The current clean-PCI notebook workflow

`simulate_clean_pci()` follows the same physics but calls the notebook-local `angular_spectrum_propagate()` for the last step. That helper uses metres internally and unshifted FFT frequencies; its transfer function is equivalent to the shifted implementation in `PCI.py`.

| Parameter | Current notebook value |
|---|---|
| Photon energy | 8.2 keV, monochromatic; $\lambda\simeq0.15120$ nm |
| Beam grid | $4096\times4096$ at 8 nm; 32.768 µm window width |
| Source-to-sample distance | 0.25 m |
| Sample-to-PCI distance | 6.31 m, passed directly as a propagation distance $Z$|
| Cu wire | Radius 5 µm; central thickness 10 µm |
| Target grid | 2000 samples per transverse dimension at 8 nm |
| Boundary blur widths | Left and right both 4 nm |
| Incident intensity FWHM at the sample | Separate 6.0 and 7.11 µm cases |

The centered calculation is `incident -> exit_field -> detector_field`. It saves incident intensity, thickness, and exit intensity in `clean_pci_fields*.npz`, and saves $|E_{\mathrm{detector}}|^2$ separately in `clean_pci_detector_intensity*.tif`. Despite the NPZ filename, that bundle does **not** store the complex fields or their phases.

The separate `scan_clean_pci_exit()` evaluates absorption-weighted transmission for 50 offsets from −10 to +10 µm. It calculates left/right exit-plane sums and normalizes them by total incident intensity. It does not propagate to the PCI detector. Likewise, several Methods, realistic-profile, and experimental-comparison outputs named “PCI” are sample-exit intensity or transmission. Their physical interpretation follows the observation plane, not the filename.

For scale, the current Cu formulas at 8.2 keV give

$$
\delta\simeq2.3566\times10^{-5},\quad
\beta\simeq4.9886\times10^{-7},\quad
\mu_{\mathrm{code}}\simeq4.0906\times10^{-5}\;\mathrm{nm}^{-1}.
$$

An ideal 10 µm central chord therefore has local transmission $e^{-\mu t}\simeq0.6643$ and phase change $-k\delta t\simeq-9.79$ radians. The beam-integrated transmission depends on illumination and wire offset. This phase change also shows why a weak-phase expansion is useful for intuition but is not quantitatively justified everywhere in this wire; the code retains the full exponential.

## 7. Connection to the SAXS-PCI notes

`SAXS-PCI.md` describes the common wave-optics foundation: sample transmission followed by free-space propagation and intensity detection. Its Fresnel integral and the PCI angular spectrum propagator are connected by

$$
k_z\simeq k-\frac{k_x^2+k_y^2}{2k},
\qquad
H_{\mathrm{Fresnel}}
=e^{ikL}\exp\!\left[-i\frac{L}{2k}(k_x^2+k_y^2)\right].
$$

This is the paraxial limit of the angular spectrum kernel. The repository uses different numerical forms for different observation grids:

| Path | Implementation | Output sampling |
|---|---|---|
| PCI detector | `spectral_propagate_to_position()`; clean notebook uses its equivalent local helper | Fixed $\Delta x$ and $N$; exact square-root kernel. |
| SAXS detector | `lorentz_propagate_to_position()` | Single-FFT Fresnel integral with quadratic phase factors; $\Delta X=\lambda L/(N\Delta x)$. |
| Legacy PCI compatibility | `fresnel_convolution_propagate_to_position()` | Calls `LightPipes.Fresnel`; fixed-grid Fresnel convolution. |

The name `lorentz` is historical: its implementation is Fresnel diffraction, not a Lorentz transformation. LightPipes documents `Fresnel` as a convolution propagator in its [command reference](https://opticspy.github.io/lightpipes/command-reference.html#LightPipes.Fresnel).

PCI emphasizes image-plane intensity variations involving the transmitted beam; SAXS emphasizes angular or finite-momentum-transfer structure. Both arise from the same complex exit field. Neither the name PCI nor the name SAXS uniquely determines a propagation algorithm. A far-field formula proportional to the squared Fourier transform of projected electron density requires additional illumination and weak-scattering assumptions; it is not the general PCI intensity calculation.

## 8. Limits when interpreting the calculated image

- **Finite FFT window.** The angular spectrum implementation uses an unpadded FFT and therefore periodic boundaries. Light leaving one side can reappear at the opposite side. At 6.31 m, the 32.768 µm window and transfer-function sampling need convergence checks before the result is interpreted as an isolated detector image. An exact propagation kernel does not guarantee an accurate finite-grid result. Transfer-function undersampling is a documented angular spectrum limitation; see [Wang et al.](https://arxiv.org/abs/2203.10966).
- **Power conservation is a limited check.** For represented propagating modes, $|H|=1$, so the FFT/inverse-FFT pair preserves the discrete sum of intensity, apart from numerical error. This remains true on a periodic grid and cannot by itself rule out wrap-around. At 8.2 keV and 8 nm pixels, every represented mode is propagating; the evanescent branch is unused.
- **Intensity units and detector response.** The Gaussian prefactor is a fixed numerical scale. The code does not establish absolute photon counts, integrate over physical detector pixels, or apply a detector efficiency/point-spread model. The single-FFT SAXS function also omits the input-area factor $\Delta x\Delta y$ needed to approximate a continuously normalized diffraction integral. Raw PCI and SAXS sums therefore need explicit normalization before absolute comparison.
- **Coherence.** The monochromatic workflow retains coherent interference correctly. The optional broadband dispatcher in the current `PCI.py` sums energy-weighted complex fields, and passes only the final energy sample to `Detector.set_raw_data()`. It is not a validated energy-integrating detector model, for which distinct photon energies ordinarily contribute as $\sum_j w_j|E_j|^2$. The clean notebook disables bandwidth sampling.
- **Sample and source model.** The sample is a scalar projected transmission screen. Multiple scattering, internal diffraction, polarization effects, and unmeasured source-phase structure are outside this model. The Gaussian curvature-sign issue and approximate attenuation conversion described above remain relevant to quantitative interpretation.

This summary is grounded in the current source files. Some statements in the existing `propagators.md`, including exact attenuation conversion, unit-power Gaussian normalization, and incoherent broadband handling, describe behavior absent from the current `PCI.py` and should not be used to override the implementation traced here.
