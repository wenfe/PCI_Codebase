---
icon: lucide/notebook-tabs
---

# PCI / SAXS

## Workflow lessons, physical interpretation, and PCI_torch assessment

*A repository-grounded guide for calculation, comparison, validation, and wiki documentation.*

> **CURRENT BASELINE**
> 8.2 keV | 4096 × 4096 | 8 nm target pixels | 10 µm Cu wire | σL = σR = 4 nm | q-mask shift = +0.005 nm⁻¹ | 6.0 and 7.11 µm Gaussian cases

Prepared from the active unified notebooks, generated artifacts, implementation source, and legacy notes.

**Scope:** SAXS/PCI workflows in `SAXS_asymmetry`. The separate bremsstrahlung-denoising package is outside this physics pipeline.

**Repository snapshot:** 3 September 2026

!!! warning "Snapshot sources and figures"

    The `SAXS_asymmetry` sources and generated figures cited by this guide are
    not present in the current checkout. Their paths are retained as provenance,
    but unavailable images are not embedded as broken site assets.

---

## 00 Executive summary

*What should survive into the wiki even if implementation details change*

### One physical model, several observables

The source creates a complex incident field. The copper wire multiplies it by an amplitude-and-phase transmission. Free-space propagation then redistributes phase into intensity. Target-exit transmission, near-axis PCI, and finite-q SAXS are related outputs of this same complex field, but they are **not** interchangeable measurements.

- Beam FWHM alone does not define illumination: the small and large Gaussian roots can give the same target size with different curvature and therefore different propagated patterns.
- The active workflow is notebook 01 for calculation and artifact creation, followed by notebook 02 for read-only plotting. This separation is a major reproducibility improvement.
- The 6.0 µm and 7.11 µm shifted-q reductions must be accumulated independently. The corrected production tables contain 43 finite rows and no longer duplicate one another.
- Detector-center correction is analysis geometry, not a new physical beam. A +0.005 nm⁻¹ q shift moves the excluded window and changes the centered left fraction from about 0.5 to about 0.542.
- `PCI.py` is the usable reference engine. `PCI_torch.py` is a promising experimental port for batched/GPU work, but it is not presently importable or parity-validated in this workspace.
- Comparison quality is controlled as much by axis, mask, row averaging, orientation, and normalization as by the propagation model itself.
- The standalone symmetric-sigma sweep compares 0, 3, 3.8, 4, 6, 8, and 14 nm for the 7.11 µm beam on a 0.48 µm offset grid without changing the production notebooks. It reports the propagated Mark1300 fraction, overlays Erik's measured motor scan, and shows both wire-edge thickness zooms.

### Recommended reading order

| Sections | Purpose |
|---|---|
| 01–04 | System, physical model, numerical baseline, and propagators |
| 05–09 | All active and legacy workflow families |
| 10–11 | `PCI.py` architecture and PCI_torch comparison |
| 12–14 | Comparison discipline, lessons, wiki plan, and source map |

---

## 01 System and workflow map

*The stable conceptual architecture behind the notebooks*

```
Incident field                Copper wire                  Complex exit field
Gaussian or measured  ─────►  complex transmission  ─────►  amplitude + phase
                                                                    │
                                                                    ▼
                                                              Propagation
                                                            AS or Fresnel FFT
                                                                    │
                                                                    ▼
                                                          Detector intensity
                                                            and reductions

Branches of the same complex field:
  • Target exit ................ absorption / overlap
  • Near axis after propagation  PCI fringes
  • Finite q after propagation   SAXS structure
  • Reduced metrics ............ L, R, L/(L+R)
```

The calculation pipeline preserves the complete complex field through the target and propagation. Only at the selected observation plane is intensity formed as |E|². This keeps absorption, refraction, transmitted-beam interference, and diffraction in one model.

### Repository execution contract

| Stage | Primary artifact | Responsibility |
|---|---|---|
| 1. Calculate | `01_calculate_and_save_data.ipynb` | Build fields, propagate, reduce, and save tables/TIFF/NPZ artifacts. |
| 2. Plot | `02_plot_and_save_figures.ipynb` | Load saved artifacts and create figures without repeating propagation. |
| 3. Explain | `docs/*.md` and this guide | Record equations, conventions, limitations, and interpretation. |
| 4. Reproduce | legacy `SAXS_PCI_Pointing_Div.ipynb`; `PlotSAXS_Pointing_Div.ipynb`; `idealc.ipynb` | Preserve historical conventions without mixing them into the active pipeline. |


---

## 02 Physical model and manifestation

*How the equations become visible in the data*

### Complex refractive index and target transmission

The material is represented by `n = 1 - δ + iβ`. For projected thickness `t(x,y)`, the field transmission is:

```
T_field(x,y) = exp[-µ t(x,y)/2] · exp[-i k δ t(x,y)]

E_exit(x,y)  = E_in(x,y) · T_field(x,y),     with  µ = 2 k β
```

The factor one-half belongs to **field-amplitude** attenuation. Squaring the field produces Beer–Lambert **intensity** attenuation `exp[-µ t]`. Phase is not visible at the exit plane by itself; it becomes visible after propagation through interference.

### What appears at each plane

| Observation | Dominant manifestation | Interpretation |
|---|---|---|
| Before target | Beam envelope and curvature | Illumination profile, focus history, and wavefront radius. |
| Immediately after target | Attenuation shadow plus stored phase delay | Useful for overlap/transmission; not yet detector PCI. |
| Near axis after propagation | Bright/dark fringes around boundaries | Propagation-based PCI: phase gradients converted into intensity. |
| Finite q after propagation | Diffraction/scattering structure | SAXS: spatial frequencies of the exit field and their interference. |
| Left/right reduction | S-shaped response versus wire offset | A calibration observable whose slope and baseline depend on mask and beam geometry. |

> **Core interpretation**
> SAXS and PCI are separated mainly by propagation distance, detector coordinates, and spatial-frequency region. They should not be modeled as unrelated effects, and complex fields must be combined **before** taking the absolute square whenever coherence is intended.

---

## 03 Current numerical baseline

*Values in the active unified notebooks, not historical defaults*

| Quantity | Active value | Consequence |
|---|---|---|
| Photon energy | 8.2 keV | λ = 0.15120024 nm; k ≈ 41.5554 nm⁻¹. |
| Simulation grid | 4096 × 4096 | 16.8 million samples per real array. |
| Target pixel | 8 nm | 32.768 µm real-space field of view. |
| Source to target | 0.25 m | Sets Gaussian spreading and phase curvature. |
| SAXS distance | 1.31 m after target | Single-FFT Fresnel output spacing about 6.045 µm. |
| PCI distance | 6.31 m after target | Angular-spectrum output remains at 8 nm sampling. |
| Wire | Cu, radius 5 µm | 10 µm ideal central chord. |
| Wire projection | 2000 samples at 8 nm | 16 µm target-map field of view; analytic chord sampled at beam resolution. |
| Bandwidth | 0 eV | All active unified cases are monochromatic. |
| Central SAXS exclusion | \|q\| < 0.10 nm⁻¹ | Removes the strongest forward region from Mark1300 side sums. |

### Gaussian roots used by current cases

| Target FWHM | Divergent / small root | Quasi-collimated / large root |
|---|---|---|
| 6.00 µm | 2.846721 µm | 4.226664 µm |
| 7.11 µm | 2.129269 µm | 5.650827 µm |
| 9.00 µm | 1.610216 µm | 7.472373 µm |
| 12.00 µm | 1.188675 µm | 10.122307 µm |

> **Documentation drift found**
> Older workflow pages still describe 7.5/7.1 µm cases and 20 nm wire voxels. The active unified pipeline now uses 7.11 µm and an 8 nm projected-wire discretization. Preserve old values only inside a clearly labelled legacy section.

### User-controlled parameter summary

The calculation notebook is the source of truth for physical and numerical
controls. The plotting notebook must use the same sigma selection and validates
it against the saved calculation manifest. The active production result set is
`outputs/sigmaL_4nm_sigmaR_4nm/`.

#### Primary model and reduction controls

| Parameter | Active value | Meaning and scope |
|---|---:|---|
| Left wire-edge blur, `WIRE_SIGMA_LEFT_NM` | 4 nm | Gaussian smoothing applied to the negative-coordinate wire boundary. |
| Right wire-edge blur, `WIRE_SIGMA_RIGHT_NM` | 4 nm | Gaussian smoothing applied to the positive-coordinate wire boundary. The active model is therefore symmetric. |
| Shifted Mark1300 mask, `Q_MASK_SHIFT_NM_INV` | +0.005 nm⁻¹ | Moves the excluded q interval from approximately [−0.100, +0.100] to [−0.095, +0.105] nm⁻¹. This shifts the mask, not the simulated q data. |
| Mark1300 cutoff, `MARK1300_Q_MIN` | 0.10 nm⁻¹ | Excludes the intense central region from left/right SAXS sums. |
| Profile comparison limit, `Q_COMPARE_MAX` | 0.30 nm⁻¹ | Upper bound used for profile normalization and comparison plots; it does not change propagation. |
| Central rows | 2 and 10 | Two rows are the main Mark1300 reduction; 10 rows provide the pointing and shifted-mask comparison. |
| Gaussian geometry | Divergent and quasi-collimated | Selects the small or large source-waist root for a requested target FWHM. |

The 4 nm edge sigma is a wire-boundary blur, not the Gaussian beam sigma and
not the beam FWHM. At the active 8 nm target sampling it equals 0.5 target
pixel. It is applied consistently to the projected-wire calculation, clean PCI
scan, realistic-profile target interaction, and analytic-chord comparison.
Experimental measurements and imported reference curves are not modified by
this sigma.

The shifted-q reduction is calculated only for the divergent Mark1300 7.11 µm
and 6.0 µm cases. The shift is about 26 q-grid samples, while the 0.10 nm⁻¹
central half-width is about 522 samples.

#### Beam-size controls

| Workflow | Target FWHM values | Notes |
|---|---|---|
| Clean SAXS | 6.0 and 7.11 µm | Both divergent and quasi-collimated roots are calculated. |
| Clean PCI | 6.0 and 7.11 µm | Uses exact angular-spectrum propagation for the saved detector fields. |
| Methods baseline | 7.11 µm | Reuses the corresponding clean SAXS calculation. |
| Divergence study | 6.0, 7.11, 9.0, and 12.0 µm | The 7.11 µm baseline is supplemented by divergent 6/9/12 µm and a quasi-collimated 12 µm case. |
| Realistic-profile workflow | Measured profile | No Gaussian FWHM is imposed on its intensity. Its modeled phase curvature is borrowed from the 7.11 µm Gaussian case. |
| Realistic/Gaussian comparison plot | 7.11 µm nominal Gaussian | Plot-only reference profile. |

All active 7.1-labelled Gaussian cases have been conformed to 7.11 µm. For
Gaussian cases, source waist is derived from the requested target FWHM and
the selected divergent/collimated root; it is not an independent input.

#### Scan and sampling controls

| Workflow | Active sampling |
|---|---|
| Clean SAXS, Methods data, and realistic profile | 43 offsets on a 0.48 µm grid from −10.0 through +10.16 µm. |
| Clean PCI | 50 evenly spaced offsets from −10 to +10 µm. |
| Divergence study | 50 evenly spaced offsets from −10 to +10 µm. |
| Analytic transmission | 49 evenly spaced offsets from −10 to +10 µm. |
| Experimental PCI/SAXS image comparison | 43 matched offsets from −10.0 through +10.16 µm at 0.48 µm spacing, using the exact Clean SAXS grid. |
| Methods GIF | 43 frames from −10.0 through +10.16 µm at 0.48 µm spacing, using every generated Methods offset. |

#### Changes relative to the repository baseline

The active workflow introduces or changes the following controls:

- independent left/right wire-edge sigmas, currently set to the symmetric 4/4 nm model;
- sigma-tagged output trees so different sigma pairs remain isolated;
- all active 7.1 µm cases conformed to 7.11 µm, plus the 6.0 µm SAXS/PCI case;
- the divergence comparison to include 6, 9, and 12 µm, with its offset count increased from 11 to 50;
- projected-wire voxel size from 20 to 8 nm;
- clean SAXS offset spacing from 0.5 to 0.48 µm; and
- `FORCE_RECALCULATE` from false to true for the current production run.

The +0.005 nm⁻¹ q-mask shift remains an explicit control but was already
present in the earlier workflow. The experimental-comparison gallery and GIF
now consume the exact 0.48 µm Clean SAXS grid so every requested plot has a
corresponding stored TIFF.

### Quick symmetric-sigma reference sweep

`SAXS_asymmetry/quick_symmetric_sigma_check.py` is a deliberately separate
sensitivity runner for

```text
sigma_left = sigma_right = 0, 3, 3.8, 4, 6, 8, or 14 nm.
```

It produces the Mark1300 observable for the 7.11 µm divergent beam.
The sweep uses 43 offsets from −10.0 through +10.16 µm at 0.48 µm spacing:

| Observable | Fast-path method | Main finding |
|---|---|---|
| Divergent Mark1300 fraction | Separable 1-D complex field and 4096-point Fresnel FFT with the +0.005 nm⁻¹ shifted q mask; overlay Erik's measured motor offsets and left fractions | Sigma strongly changes the offset response; the maximum change from sigma 8 nm is about 0.213 for sigma 0 nm, 0.196 for sigma 3 nm, 0.155 for sigma 3.8 nm, and 0.120 for sigma 14 nm. The motor points provide an experimental reference on the 7.11 µm panel. |

The fraction plot is saved separately from two standalone 8 × 6 inch wire-edge
thickness figures: the left edge (−5.04 to −4.99 µm) uses the `_wire_left_edge`
filename suffix, and the right edge (4.99 to 5.04 µm) uses `_wire_right_edge`.
Both figures use matching rainbow colors and legend labels for every sigma.
Current tables and summaries cover the 7.11 µm case;
earlier 6.0 and 7.0 µm table files may remain in the output directory.

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/quick_symmetric_sigma/mark1300_symmetric_sigma.png`
    is not included in this checkout.


---

## 04 Propagation choices

*Choose by physical plane and sampling requirements*

**Angular spectrum — near field / PCI**
FFT of exit field → multiply by `exp(i k_z z)` → inverse FFT → same pixel spacing → exact Helmholtz transfer.

**Single-FFT Fresnel — far field / SAXS**
Multiply input chirp → one forward FFT → multiply output chirp → pixel spacing = `λz/(N dx)` → paraxial scaled detector plane.

| Feature | Angular spectrum | Single-FFT Fresnel |
|---|---|---|
| Primary use | Detector PCI; target-to-target hops | Far-field SAXS detector |
| Transforms | Forward FFT + inverse FFT | One forward FFT with input/output chirps |
| Approximation | Exact scalar Helmholtz transfer on sampled grid | Paraxial Fresnel approximation |
| Output sampling | Same `dx` as input | `dX = λz/(N dx)` |
| Principal risk | Periodic wrap-around if field reaches window edges | Comparing indices without converting to detector coordinates |
| At active settings | 8 nm at 6.31 m | about 6.045 µm at 1.31 m |

For the current 4096 × 4096 grid, a `complex64` field is about 128 MiB and a `complex128` field is about 256 MiB. FFTs need several live arrays, so practical memory use is a multiple of these numbers. Batch size multiplies the requirement.

> **Do not compare arrays by pixel index alone**
> The angular-spectrum and scaled-Fresnel arrays may have the same shape but represent different physical pixel sizes. Every saved result should carry its plane, pixel spacing, axis convention, and normalization.

---

## 05 Workflow A — clean Gaussian SAXS

*Controlled comparison of beam size and curvature*

Notebook 01 creates four cases: divergent and large-root beams at 6.0 and 7.11 µm target FWHM. Each case scans the same shifted 10 µm Cu wire, propagates 1.31 m, saves float32 detector TIFFs, and reduces two central rows outside the Mark1300 central q mask.

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/saxs/figures/SAXS_Mark1300_collimated_6um_7p11um.png`
    is not included in this checkout.

**Figure 1. Clean SAXS comparison.** At fixed material and propagation, changing the Gaussian root changes wavefront curvature. The left fraction remains an S-shaped offset calibration, while detailed left/right amplitudes and saturation shift slightly.

| Case | Centered fraction | Fraction range |
|---|---|---|
| Divergent 7.11 µm | 0.500048 | 0.373308 to 0.625469 |
| Large-root 7.11 µm | 0.500043 | 0.377016 to 0.621674 |
| Divergent 6.0 µm | 0.500047 | 0.374449 to 0.624308 |
| Large-root 6.0 µm | 0.500044 | 0.376636 to 0.622059 |

> **Lesson:** matching target FWHM is necessary but not sufficient. Compare the root, wavefront radius, intensity profile, and propagated detector sampling together.

---

## 06 Workflow B — asymmetry methods and gallery

*Offset, divergence, and visual cross-checks*

| Branch | Calculation | Purpose |
|---|---|---|
| Offset scan | Reuse clean divergent 7.11 µm TIFFs; two-row Mark1300 sums; 10-row display profiles | Dense calibration curve and experimental lineout comparison. |
| Divergence scan | 7.11 µm baseline plus 6, 9, 12 µm divergent and 12 µm large-root cases | Separate spot-size/curvature effects on calibration slope. |
| Gallery/movie | Target-exit PCI beside far-field SAXS for each wire offset | Verify that spatial motion and left/right response are physically consistent. |

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/methods/figures/05_divergence_scan.png` is not
    included in this checkout.

**Figure 2. Existing divergence-scan figure.** Wider/less-divergent cases have a broader transition than the dense 7.11 µm baseline. The stored table now also contains a 6.0 µm case, so this figure is older than the current table.

> **Open plotting issue found during audit**
> The current divergence table has five cases and the column name `mark1300_frac`. Notebook 02 defines only four colors and reads `left_fraction`. Rerunning that cell will fail or omit a case until the field name and color mapping are corrected. Treat the existing PNG as historical until regenerated.

---

## 07 Workflow C — clean PCI and shifted-q correction

*Separate target-exit attenuation from detector-plane phase contrast*

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/clean_pci/clean_pci_field_overview_6um.png` is not
    included in this checkout.

**Figure 3.** The 6.0 µm clean PCI chain: incident beam, wire thickness, target-exit attenuation, and propagated detector fringes. The last panel is the physical manifestation of phase-to-intensity conversion.

The clean branch calculates 6.0 and 7.11 µm detector PCI using exact angular-spectrum propagation over 6.31 m. It separately scans target-exit left/right transmission without propagation. These are deliberately different observables.

### Shifted-q detector-center correction

The unshifted Mark1300 reduction rejects \|q\| < 0.10 nm⁻¹. With `q_shift = +0.005 nm⁻¹`, the accepted sides become approximately `q < -0.095` and `q > +0.105` nm⁻¹. This is equivalent to evaluating `|q - 0.005| ≥ 0.10` nm⁻¹.

| Shifted-q case | Rows averaged | Centered left fraction | Full range |
|---|---|---|---|
| 7.11 µm | 2 / 10 | 0.541755 / 0.541755 | 0.412167 to 0.663430 |
| 6.0 µm | 2 / 10 | 0.541798 / 0.541798 | 0.413327 to 0.662288 |

> **Lesson from the 6.0 µm correction**
> Per-case accumulators are essential. Reusing one mutable list silently produced a second file with the first case's numbers. Notebook 01 now stores each case independently; notebook 02 validates three finite columns and rejects an exact duplicate.

---

## 08 Physical comparison in one figure

*What the active 6.0/7.11 µm results say*

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/clean_pci/clean_pci_saxs_mark1300_left_right_vs_offset.png`
    is not included in this checkout.

**Figure 4. Updated three-panel summary.** Top: target-exit PCI transmission and experimental transmission. Middle: far-field SAXS side signals. Bottom: shifted-q asymmetry, including independent 6.0 µm two-row and 10-row curves.

| Observation | Physical reading |
|---|---|
| Exit transmission minimum | The centered wire blocks the highest-fluence part of the beam; the 6.0 µm spot gives a deeper minimum than 7.11 µm. |
| SAXS left/right exchange | Moving the wire reverses which finite-q side receives more power, giving the calibration sigmoid. |
| Shifted baseline | A centered symmetric object no longer gives 0.5 because the analysis mask is intentionally displaced. |
| 2 rows vs 10 rows | The near-identical curves here indicate vertical averaging stabilizes noise without materially changing this symmetric simulated reduction. |

---

## 09 Workflow D — realistic measured illumination

*Retain measured amplitude, supply a modeled phase*

The measured profile branch reads `RealisticProfile_10nm.tif`, clips invalid/negative values, resamples from 10 nm to the 8 nm simulation grid, normalizes total intensity, and uses `sqrt(intensity)` as amplitude. The missing phase is supplied by the divergent 7.11 µm Gaussian curvature.

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/realistic_profile/figures/01_realistic_vs_gaussian_profile.png`
    is not included in this checkout.

**Figure 5.** The measured profile is structured and slightly asymmetric relative to the nominal Gaussian. This changes beam–wire overlap and therefore both exit transmission and SAXS asymmetry.

| Metric | Current artifact |
|---|---|
| Realistic target-exit left fraction | 0.431897 to 0.586446; centered 0.506338 |
| Realistic total transmission | 0.727045 to 0.994101 |
| Realistic SAXS left fraction | 0.372335 to 0.625611; centered 0.487651 |
| Detector lineout | 10 central rows; side sums outside \|q\| < 0.10 nm⁻¹ |

In the combined “SAXS left ratio versus motor experiment” panel, the realistic
and 7.11 µm Gaussian ratios use the fractional mask centered at
`Q_MASK_SHIFT_NM_INV = +0.005 nm⁻¹`. The effect of ±1 µm motor-position
uncertainty is shown as a shaded envelope around the measured response.

> **Interpretation boundary**
> A measured intensity TIFF does not contain phase. The realistic branch is therefore a **hybrid model**: measured amplitude plus Gaussian phase curvature. Document that assumption explicitly whenever calling the result "realistic."

---

## 10 Workflow E — experiment comparison and legacy paths

*Keep reproducibility without mixing incompatible conventions*

### Gaussian experimental comparison

The active comparison reuses divergent 7.11 µm SAXS TIFFs and calculates distinct analytic-chord target-exit PCI images. It compares simulated transmission with the r0484 motor scan after independent max normalization. The current analytic transmission minimum is 0.741599 at zero offset and reaches 1 away from the wire.

!!! note "Figure unavailable"

    `SAXS_asymmetry/outputs/experimental_comparison/figures/04_exit_transmission.png`
    is not included in this checkout.

**Figure 6.** Simulated target-exit transmission versus the experimental scan. Shape agreement is meaningful; absolute-flux agreement is not tested because each curve is normalized independently.

### Legacy calculation families

| Artifact | Use | Do not assume |
|---|---|---|
| `SAXS_PCI_Pointing_Div.ipynb` | Reproduce historical Gaussian/wire propagation and TIFFs | Current q mask, axis direction, or filenames. |
| `PlotSAXS_Pointing_Div.ipynb` | Reproduce earlier Mark1300 plots | Current row averaging, central exclusion, or orientation. |
| `idealc.ipynb` | Idealized 2048-grid LightPipes-style study | Current copper constants, sampling, or active pipeline equivalence. |
| `PCI.py` LightPipes compatibility method | Fixed-grid Fresnel legacy reproduction | Same behavior as exact angular spectrum or scaled single-FFT Fresnel. |

> **Legacy rule**
> A legacy result is valid when its conventions are reproduced intentionally. It becomes misleading only when its row count, q axis, mask, orientation, material constants, or propagator are compared as if they were current defaults.

---

## 11 PCI.py reference implementation

*Usable NumPy/SciPy engine and its responsibilities*

| Class | Role | Key responsibility |
|---|---|---|
| `Material` / `Cu` | Optical constants | δ, β, phase coefficient, and attenuation coefficient. |
| `Target` / `wire` | Sample geometry | Projected thickness, absorption, phase shift, shift/rotation. |
| `XFEL` | Wavefield engine | Grid, target interaction, angular-spectrum and Fresnel propagation. |
| `gaussian_XFEL` | Source model | Gaussian width, curvature, Gouy phase, and target FWHM. |
| `Detector` / `jungfrau` | Observation plane | Category selects PCI or SAXS path; stores field and axes. |
| `Beamline` | Orchestration | Sort targets, propagate source to requested detector. |

### Strengths in the current workflow

- Imports successfully in the project environment and is the engine used by notebook 01.
- Provides NumPy arrays compatible with SciPy interpolation, Pillow TIFF output, and the existing analysis stack.
- The active workflow wraps the wire with a memory-efficient projected-chord implementation, avoiding a full 3-D target volume.
- The angular-spectrum path handles evanescent modes with a decaying complex `k_z` branch.
- A dedicated `intensity_detector` property makes detector intensity available without plotting.

### Limits to document

- Raw FFT intensities are simulation units; absolute photons per detector area require explicit transform, pixel-area, source, and detector calibration.
- The active notebooks are monochromatic. The library's broader bandwidth path should be validated before being presented as an incoherent-spectrum model.
- Large grids are memory- and I/O-intensive; float32 TIFF reuse is part of the design, not just an optimization.
- Print statements and notebook-oriented display imports remain inside the library, which complicates clean batch use.

---

## 12 PCI_torch assessment

*Experimental tensor port — useful direction, not a drop-in replacement*

| Dimension | `PCI.py` | `PCI_torch.py` |
|---|---|---|
| Backend | NumPy/SciPy FFT and interpolation | PyTorch tensors and `torch.fft`, plus SciPy/PIL utilities |
| Current import | Passes | Fails: `multiprocess` missing; `torchvision` and `torchaudio` also absent |
| Portability | Repository-contained except optional LightPipes | Hard-coded `/home/thiess94/...` path and external `propagatorsv1` module |
| Device/batch | Single array, CPU | `device` and `batch_size` parameters; spot shifts and noise batches |
| Precision | Mostly NumPy `complex128` unless cast | Gaussian source explicitly `complex64` |
| Propagators | Angular spectrum, scaled Fresnel, optional LightPipes | Angular spectrum, scaled Fresnel, and external selectable propagators |
| Autograd | Not applicable | Core FFT operations can be differentiable, but SciPy, NumPy, `detach`/`cpu` calls, and global diagnostics break end-to-end guarantees |
| Validation status | Used by generated artifacts | No parity tests or benchmark found |

### Important numerical differences found

- `PCI_torch.get_k(Lambda=...)` evaluates `2*pi/Lambda` but does not return it.
- Its default angular-spectrum non-propagating branch assigns a negative real `k_z` unless `has_evanescent=True`; the reference engine uses an imaginary decaying branch.
- The Torch single-FFT Fresnel code lacks an explicit `dx²` Riemann-sum normalization, as does the current NumPy legacy-style method; amplitude parity therefore needs a declared convention.
- The Torch source uses a fixed `2.3e10/q` scaling and `complex64`; compare normalized shapes separately from absolute amplitude.
- Both broad-band implementations should be audited for incoherent intensity summation. This does not affect the active notebooks because bandwidth is zero.

> **Recommended Torch roadmap**
> First make the module self-contained and importable. Then build small-grid parity tests for source field, wire transmission, angular spectrum, Fresnel sampling, and gradients. Only after numerical parity should GPU speed and memory be benchmarked on the 4096 grid.

---

## 13 Comparison and validation playbook

*A result is comparable only when its conventions are comparable*

### Minimum metadata for every curve or image

| Category | Record explicitly |
|---|---|
| Source | Energy, bandwidth, amplitude profile, target FWHM, Gaussian root, wavefront radius, normalization. |
| Target | Material constants, radius/thickness model, voxel/pixel size, interpolation, offset sign. |
| Propagation | Method, distance, approximation, input/output pixel size, field of view, FFT normalization. |
| Reduction | Rows averaged, q grid, q shift, excluded band, side definitions, interpolation/binning. |
| Presentation | Linear/log scale, independent/shared normalization, cropping, transpose/mirror operations. |
| Provenance | Notebook cell or script, source commit, artifact path, date, and whether reused or recalculated. |

### Recommended parity ladder

1. Import and construct identical small grids without optional plotting or external paths.
2. Compare Gaussian complex fields: amplitude error, phase error after removing global phase, and FWHM.
3. Compare projected thickness, absorption, phase delay, and exit field before any propagation.
4. Compare angular-spectrum output and verify power conservation when only propagating modes are present.
5. Compare Fresnel physical axes and normalized shapes; separately state any amplitude normalization convention.
6. Compare final reductions using the same q array, mask, row average, and orientation.
7. Benchmark wall time and peak memory only after numerical tolerances pass.

### Current audit warnings

| Finding | Impact | Action |
|---|---|---|
| Clean/realistic offset grid | 43 samples from −10.0 through +10.16 µm at exactly 0.48 µm spacing | The Methods scan, paired comparison, and GIF reuse this grid; the PCI, divergence, and transmission grids remain unchanged. |
| Two q-axis conventions | `linspace` endpoints differ slightly from exact FFT-bin spacing | Use one exported q axis for masks, interpolation, tables, and plots. |
| Divergence plot schema mismatch | Notebook 02 may fail or omit the fifth case | Read `mark1300_frac` and map colors by case name. |
| Manifest artifact is stale | Existing JSON does not yet list the new 6.0 µm shifted-q file | Rerun notebook 01 completion cell after calculation changes. |
| Historical docs use old values | Wiki can silently mix 7.5/20 nm with 7.11/8 nm | Add versioned current/legacy tables. |

---

## 14 Lessons learned and proposed wiki structure

*Turn implementation history into durable project knowledge*

### Ten durable lessons

1. Start from the complete complex field; do not bolt SAXS and PCI together after intensity has been formed.
2. Name the observation plane. "PCI" at target exit and propagated detector PCI are different observables.
3. FWHM does not encode curvature. Record the Gaussian root and source waist.
4. Sampling is physics metadata. A 4096-array can mean 8 nm pixels or roughly 6.045 µm detector pixels.
5. Reduction conventions can dominate small differences: q mask, q shift, rows, axis, and orientation must match.
6. Independent normalization is valid for shape comparison but cannot support absolute-flux claims.
7. Measured intensity plus modeled phase is a hybrid assumption, not a complete measured wavefield.
8. Calculation and plotting should remain separated; artifacts create reproducible interfaces between them.
9. Every multi-case accumulator and filename should be keyed by case and validated against duplication.
10. Acceleration follows parity. A GPU port is valuable only after physics, axes, precision, and reductions agree.

### Suggested wiki pages

| Page | Core content |
|---|---|
| 1. Overview | One-field concept, workflow map, glossary, source-of-truth policy. |
| 2. Physics | Gaussian beam, Cu transmission, PCI/SAXS manifestation, validity limits. |
| 3. Numerical methods | Angular spectrum, Fresnel FFT, sampling, normalization, memory. |
| 4. Active workflows | Notebook 01 sections, artifacts, notebook 02 figures, run order. |
| 5. Reduction conventions | Mark1300 mask, shifted q, two/10 rows, left/right orientation. |
| 6. Experiment comparison | Runs, interpolation, motor scan, normalization, uncertainty. |
| 7. PCI.py vs PCI_torch | Capability matrix, blockers, parity tests, benchmark protocol. |
| 8. Legacy archive | Historical notebooks, LightPipes, old values, reproduction notes. |
| 9. Known issues | Schema mismatches, offset endpoint, stale manifests/docs, ownership. |

> **Definition of done for a wiki result**
> A reader can identify the source field, target, propagation plane, sampling, reduction, normalization, generated artifact, and known limitations without opening the notebook.

---

## Appendix A — Source and artifact map

*Files inspected for this guide*

| Source | Role |
|---|---|
| `SAXS_asymmetry/01_calculate_and_save_data.ipynb` | Active calculation and artifact pipeline. |
| `SAXS_asymmetry/02_plot_and_save_figures.ipynb` | Active read-only plotting pipeline. |
| `SAXS_asymmetry/quick_symmetric_sigma_check.py` | Standalone 0/3/3.8/4/6/8/14 nm symmetric-sigma Mark1300 sensitivity runner for 7.11 µm with 0.48 µm offset spacing, Erik motor-scan overlay, and both wire-edge thickness zooms. |
| `SAXS_asymmetry/PCI.py` | Reference NumPy/SciPy wave-propagation implementation. |
| `SAXS_asymmetry/PCI_torch.py` | Experimental PyTorch port. |
| `docs/SAXS-PCI.md` | Unified physical interpretation. |
| `docs/propagators.md` | Propagation equations and intended implementation behavior. |
| `docs/saxs_intensity_workflow.md` | Detailed SAXS workflow and propagation notes. |
| `docs/pci_intensity_workflow.md` | Detailed PCI workflow and physical interpretation. |
| `SAXS_asymmetry/01_variables_and_functions.md` | Notebook variable/function inventory. |
| `outputs/combined_plot_data/calculation_manifest.json` | Generated artifact inventory; currently needs refresh for the new 6.0 shifted-q file. |

### Primary generated artifacts cited in the analysis

| Artifact family | Location |
|---|---|
| Clean SAXS tables/TIFFs | `SAXS_asymmetry/outputs/saxs/` |
| Methods tables/figures/movie | `SAXS_asymmetry/outputs/methods/` |
| Clean PCI fields/tables/figures | `SAXS_asymmetry/outputs/clean_pci/` and `outputs/combined_plot_data/` |
| Symmetric-sigma sensitivity tables/figures | `SAXS_asymmetry/outputs/quick_symmetric_sigma/` |
| Realistic-profile results | `SAXS_asymmetry/outputs/realistic_profile/` |
| Experimental comparison | `SAXS_asymmetry/outputs/experimental_comparison/` |

---

### Status of this guide

This is a technical synthesis of the repository snapshot on 3 September 2026. It is intended for internal documentation and code review. It is not a substitute for experimental calibration, uncertainty analysis, or peer-reviewed validation of the physical model.

*Prepared locally from repository sources. No external scientific claims were introduced beyond the equations and assumptions implemented or documented in the codebase.*

---

*Converted from `output/pdf/pci_saxs_workflows_lessons.pdf` (17 pages).
Original figure paths are retained as provenance, but unavailable PNG files
are not embedded in this site.*
