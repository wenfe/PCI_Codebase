# SAXS and PCI as a unified wave-propagation problem

> This page is a revised Markdown version of the 2021 notes in
> `SAXS-PCI.docx`. It explains the physical connection between small-angle
> X-ray scattering (SAXS) and propagation-based phase-contrast imaging (PCI).
> For details of the current numerical implementation, see
> [SAXS calculation and comparison](saxs_calculation_comparison.md) and
> [PCI calculation and comparison](pci_calculation_comparison.md).

## Overview

SAXS and PCI can be described with the same wave-optics calculation:

```text
incident X-ray field
    -> transmission through the sample
    -> free-space propagation
    -> detector intensity
```

The sample changes both the amplitude and phase of the incident field. After
free-space propagation, these changes interfere with the transmitted beam:

- close to the optical axis, the interference produces the image-like
  contrast usually called PCI;
- at larger momentum transfer, the same propagated field produces the SAXS
  pattern.

The distinction between PCI and SAXS is therefore mainly the detector region
and spatial-frequency range being examined, not a difference in the
underlying propagation physics.

## 1. Conventional SAXS description

For a weakly scattering object illuminated by a plane wave, the elastic
scattering amplitude is proportional to the Fourier transform of its electron
density. In the first Born approximation,

$$
\frac{\mathrm d\sigma}{\mathrm d\Omega}
= r_e^2
  \left|
    \int n_e(\mathbf r)
    \exp(-i\mathbf q\cdot\mathbf r)\,\mathrm d^3\mathbf r
  \right|^2,
$$

where:

- $r_e$ is the classical electron radius;
- $n_e(\mathbf r)$ is the electron density;
- $\mathbf q=\mathbf k_{\mathrm out}-\mathbf k_{\mathrm in}$ is the
  momentum-transfer vector; and
- $|\mathbf k_{\mathrm in}|=|\mathbf k_{\mathrm out}|=k=2\pi/\lambda$ for
  elastic scattering.

For a uniform object, the forward intensity scales approximately as the
square of the total number of electrons, $N_e^2$. Near an absorption edge, the
real electron density can be replaced by the appropriate complex scattering
factor.

This scattering-amplitude picture is useful for thin, weak objects. It becomes
less intuitive when the sample is thick or strongly absorbing, or when the
small-angle scattering overlaps the directly transmitted beam. In that
regime, the interference between the scattered and transmitted fields must be
retained explicitly.

## 2. Refractive-index description of the sample

The complex X-ray refractive index is written as

$$
n = 1-\delta+i\beta.
$$

The refractive-index decrement is related to the electron density by

$$
\delta
= \frac{2\pi r_e\rho_e}{k^2}
= \frac{r_e\lambda^2\rho_e}{2\pi},
$$

where $\rho_e$ is the electron density. This relation is the direct connection
between the scattering-length-density and refraction descriptions.

For a projected sample thickness $t(x,y)$, the thin-object transmission
function is

$$
T(x,y)
= \exp\!\left[-\frac{\mu t(x,y)}{2}\right]
  \exp[-ik\delta t(x,y)],
$$

with

$$
\mu=2k\beta.
$$

The field immediately after the sample is therefore

$$
E_{\mathrm exit}(x,y)=E_{\mathrm in}(x,y)T(x,y).
$$

The factor $1/2$ in the absorption term is important: $T$ acts on the field
amplitude, whereas the intensity attenuation is
$\exp[-\mu t(x,y)]$.

For a weak, non-absorbing phase object,

$$
T(x,y)\approx 1-ik\delta t(x,y).
$$

The first term is the transmitted beam. The second contains the spatial
variation of the sample and gives the usual scattering amplitude after
propagation. This expansion shows why the scattering and refraction pictures
agree in the thin-target, weak-scattering limit.

## 3. Rayleigh–Sommerfeld propagation and the Fresnel approximation

For time dependence $e^{-i\omega t}$, a known exit field $E(x',y',0)$ over
the whole sample plane gives the outgoing field in a homogeneous scalar
half-space $Z>0$ through the exact Rayleigh–Sommerfeld I integral:

$$
E(X,Y,Z)
= \frac{1}{i\lambda}
  \iint_{\mathbb R^2} E(x',y',0)\,
  \frac{e^{ikR}}{R}\frac{Z}{R}
  \left(1+\frac{i}{kR}\right)\,
  \mathrm dx'\,\mathrm dy',
$$

where

$$
R=\sqrt{(X-x')^2+(Y-y')^2+Z^2}.
$$

The factor $Z/R$ is the propagation direction cosine. This real-space
integral is equivalent to angular spectrum propagation; see the
[derivation and references](propagators.md#rayleighsommerfeld-real-space-foundation).
For $kR\gg1$, the correction $i/(kR)$ can be neglected, leaving the familiar
$Ze^{ikR}/(i\lambda R^2)$ kernel. The Fresnel approximation follows below.

### Paraxial approximation

When transverse distances are small compared with $Z$,

$$
R\approx Z+\frac{(X-x')^2+(Y-y')^2}{2Z}.
$$

Using $Z/R\approx1$ and $R\approx Z$ in the slowly varying amplitude gives

$$
\begin{aligned}
E(X,Y,Z)
&=\frac{e^{ikZ}}{i\lambda Z}
  \exp\!\left[\frac{ik}{2Z}(X^2+Y^2)\right] \\
&\quad\times
  \iint E(x',y',0)
  \exp\!\left[\frac{ik}{2Z}(x'^2+y'^2)\right]
  \exp[-i(q_xx'+q_yy')]
  \,\mathrm dx'\,\mathrm dy',
\end{aligned}
$$

where

$$
q_x=\frac{kX}{Z},
\qquad
q_y=\frac{kY}{Z}.
$$

The integral is a two-dimensional Fourier transform of the exit field
multiplied by a quadratic phase factor. This is why the propagation can be
calculated efficiently with an FFT.

The detector records intensity rather than complex field:

$$
I(X,Y,Z)=|E(X,Y,Z)|^2.
$$

## 4. How SAXS and PCI appear in the same field

It is often helpful to split the projected density into a constant background
and a spatially varying part:

$$
\rho_e(x,y)=\bar\rho_e+\Delta\rho_e(x,y).
$$

The constant part mainly modifies the transmitted beam through a nearly
uniform phase shift and attenuation. The varying part generates finite-$q$
structure. These contributions must be added as **complex fields before the
absolute square is taken**:

$$
I=|E_{\mathrm transmitted}+E_{\mathrm variation}|^2.
$$

This expression contains the cross term responsible for interference. It
explains the two familiar limits:

- **PCI:** near the direct beam, interference converts phase variations into
  real-space intensity contrast;
- **SAXS:** farther from the direct beam, the intensity is dominated by the
  Fourier components of the sample's density variations.

Subtracting the mean density before a Fourier transform can be useful for
isolating finite-$q$ SAXS, but it removes the transmitted field. The mean
contribution must be restored coherently if the calculation is also expected
to reproduce PCI or the forward-scattering region.

## 5. Incident illumination

### Plane and spherical waves

A plane wave has a constant phase across the sample plane. A point source a
distance $z_s$ upstream produces, in the paraxial approximation, a spherical
phase front:

$$
E(x',y',0)\propto
\exp\!\left[\frac{ik}{2z_s}(x'^2+y'^2)\right].
$$

An arbitrary measured illumination profile may be included as an amplitude
envelope multiplying this phase factor.

### Gaussian beam

A focused X-ray beam is more accurately represented as a Gaussian beam. With
$r^2=x^2+y^2$,

$$
I(r,z)=I_0\left(\frac{w_0}{w(z)}\right)^2
\exp\!\left[-\frac{2r^2}{w^2(z)}\right],
$$

and one consistent field convention is

$$
E(r,z)=E_0\frac{w_0}{w(z)}
\exp\!\left[-\frac{r^2}{w^2(z)}\right]
\exp\!\left[-ikz-\frac{ikr^2}{2R(z)}+i\zeta(z)\right].
$$

The beam parameters are

$$
z_R=\frac{\pi w_0^2}{\lambda},
\qquad
w(z)=w_0\sqrt{1+\left(\frac{z}{z_R}\right)^2},
$$

$$
R(z)=z\left[1+\left(\frac{z_R}{z}\right)^2\right],
\qquad
\zeta(z)=\tan^{-1}\!\left(\frac{z}{z_R}\right).
$$

Here $w_0$ is the waist radius at which the intensity has fallen to
$e^{-2}$ of its on-axis value. If the transverse intensity is written with an
RMS width $\sigma$ as $\exp[-r^2/(2\sigma^2)]$, then $w=2\sigma$.

In the far field, the half-angle divergence is approximately

$$
\theta\approx\frac{\lambda}{\pi w_0}.
$$

For a total of $N_\gamma$ photons in a circular Gaussian profile, the peak
fluence is

$$
I_0=\frac{2N_\gamma}{\pi w_0^2},
$$

provided $I$ is interpreted as photons per unit area.

## 6. Validity and limitations

The unified treatment is reliable when the following assumptions are
appropriate:

1. **Scalar field:** polarization effects can be neglected.
2. **Paraxial propagation:** propagation angles and transverse dimensions are
   small relative to the sample-to-detector distance.
3. **Thin-object or projection approximation:** the sample is represented by
   one projected complex transmission function.
4. **Single scattering:** multiple scattering inside density fluctuations is
   negligible.
5. **Coherent propagation:** the required spatial and temporal coherence is
   present, or partial coherence is modelled separately.

Absorption by a thick, nearly uniform layer can be represented by the complex
transmission function. Strong multiple scattering, dynamical diffraction, or
significant evolution of the field inside a thick sample requires a more
complete model, such as multislice propagation.

For typical X-ray beam sizes and metre-scale propagation distances, the
geometrical correction to $Z/R\approx1$ is extremely small. The exact size of
the error should nevertheless be evaluated from the actual beam footprint,
detector extent, and propagation distance rather than assumed universally.

## 7. Relation to this repository

The current Python workflow follows the same conceptual sequence:

```text
Gaussian source
    -> field at the target
    -> sample absorption and phase shift
    -> numerical propagation
    -> detector intensity |E|^2
```

The main implementation is [`PCI.py`](../SAXS_asymmetry/PCI.py). The two
propagation paths and their active numerical settings are documented in:

- [SAXS calculation and comparison](saxs_calculation_comparison.md)
- [PCI calculation and comparison](pci_calculation_comparison.md)
- [Propagation methods](propagators.md)

The historical notes state that the ImageJ plugin applied an absolute
normalization in photons per unit detector area. Do not assume that the raw
arrays produced by the current Python FFT implementation have this absolute
normalization: its raw sums are simulation units unless an explicit transform
normalization, pixel-area factor, source normalization, and detector response
are applied.

## Key takeaway

The most robust way to connect SAXS and PCI is to propagate the complete
complex exit field and calculate the detector intensity only after all field
components have been added. This preserves the interference with the
transmitted beam automatically and avoids treating forward scattering, SAXS,
and PCI as unrelated phenomena.
