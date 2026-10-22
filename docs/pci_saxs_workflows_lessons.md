---
icon: lucide/notebook-tabs
---

# PCI / SAXS

## Workflow lessons, physical interpretation, and PCI_torch assessment

*A repository-grounded guide for calculation, comparison, validation, and wiki documentation.*

> **CURRENT BASELINE**
> 8.2 keV | 4096 × 4096 | 8 nm target pixels | 10 µm Cu wire | σL = 4.67 nm, σR = 0 nm | ten-row SAXS lineouts | 6.0 and 7.11 µm Gaussian cases

Prepared from the active unified notebooks, generated artifacts, implementation source, and legacy notes.

**Scope:** SAXS/PCI implementation in `src/SAXS_asymmetry/` and workflows in
`notebooks/saxs_asymmetry/`. The separate bremsstrahlung-denoising package is
outside this physics pipeline.

**Structure and workflow review:** 22 October 2026

!!! note "Figure provenance"

    The `SAXS_asymmetry` sources cited by this guide live under
    `src/SAXS_asymmetry/` and `notebooks/saxs_asymmetry/`. Generated figures are
    written under `outputs/saxs_asymmetry/` and are referenced by path rather
    than embedded. They are generated, normally untracked artifacts and may
    be absent from a fresh checkout. Old symmetric-sigma results are historical
    examples, not quantitative predictions for the current 4.67/0 nm selection.

---

## 00 Executive summary

*What should survive into the wiki even if implementation details change*

### One physical model, several observables

The source creates a complex incident field. The copper wire multiplies it by an amplitude-and-phase transmission. Free-space propagation then redistributes phase into intensity. Target-exit transmission, near-axis PCI, and finite-q SAXS are related outputs of this same complex field, but they are **not** interchangeable measurements.

- Beam FWHM alone does not define illumination: the small and large Gaussian roots can give the same target size with different curvature and therefore different propagated patterns.
- The active workflow is notebook 01 for calculation and artifact creation, followed by notebook 02 for artifact-consuming plotting without repeated propagation. This separation is a major reproducibility improvement.
- The 6.0 µm and 7.11 µm shifted-q reductions use independent accumulators. Each current table has 43 rows and two columns: offset in µm and ten-row left fraction.
- Detector-center correction is analysis geometry, not a new physical beam. The Gaussian shifted-mask branch uses +0.005 nm⁻¹; the realistic smoothing-pair sweep uses an unshifted mask. These reductions are not interchangeable.
- `PCI.py` is the reference engine used by the notebooks. `PCI_torch.py` is an experimental port with additional dependencies and an external propagator import; it is not a validated drop-in replacement.
- Comparison quality is controlled as much by axis, mask, row averaging, orientation, and normalization as by the propagation model itself.
- The standalone quick tool compares Gaussian symmetric sigmas or independent sigma pairs. The separate notebook sweep compares realistic illumination at six ordered sigma pairs and writes its own consolidated bundle.

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

```text
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
| 2. Plot | `02_plot_and_save_figures.ipynb` | Load saved artifacts and create figures without repeating propagation; plotting is not read-only on disk. |
| 3. Explain | `docs/*.md` and this guide | Record equations, conventions, limitations, and interpretation. |
| 4. Reproduce | legacy `SAXS_PCI_Pointing_Div.ipynb` and `PlotSAXS_Pointing_Div.ipynb` | Preserve historical conventions without mixing them into the active pipeline. |

### Directory ownership and run order

| Repository location | Contents |
|---|---|
| `src/SAXS_asymmetry/` | NumPy engine, experimental Torch port, path resolver, and standalone utilities. |
| `data/experimental/` | SAXS profiles, motor-scan arrays, and transmission measurements. |
| `data/profiles/` | Measured incident-intensity TIFFs. |
| `data/reference/` | External reference curves. |
| `notebooks/saxs_asymmetry/` | Active calculation/plotting pair and historical notebooks. |
| `outputs/saxs_asymmetry/<sigma_tag>/` | Selected-sigma results and calculation manifest. |
| `outputs/saxs_asymmetry/quick_symmetric_sigma/` | Standalone Gaussian sigma comparisons. |
| `outputs/saxs_asymmetry/realistic_sigma_pair_scan/` | Checkpointed realistic pair tables, consolidated data, and figures. |
| `docs/` and `tests/` | Site sources and repository-layout checks. |

`src/SAXS_asymmetry/paths.py` is the path authority. `PCI_DATA_DIR`
replaces the input root; `PCI_OUTPUT_DIR` replaces the study-output root.
Set overrides before notebook setup. Notebook setup searches for
`pyproject.toml`, so start the notebooks from within the repository.

Install the locked environment with `uv sync --locked`. Run notebook 01's
setup, select the sigma pair, and execute the required dependent sections.
Run the completion cell to write
`<sigma_tag>/combined_plot_data/calculation_manifest.json`.
Then run notebook 02's setup with the same pair and its corresponding plots.
The current tag is `sigmaL_4p67nm_sigmaR_0nm`.

The smoothing-pair sweep depends on the clean-case configuration and
realistic-field setup. Its checkpoint tables sit outside the selected sigma
tree and are reused when shape, offsets, and finite fractions match.
`FORCE_RECALCULATE` does not invalidate those checkpoints. After changing
their physical assumptions, invalidate the affected pair tables explicitly.

---

## 02 Physical model and manifestation

*How the equations become visible in the data*

### Complex refractive index and target transmission

The material is represented by `n = 1 - δ + iβ`. For projected thickness `t(x,y)`, the field transmission is:

```text
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
| Wire-edge smoothing | Left 4.67 nm, right 0 nm | Selected independently; old symmetric 4/4 nm results are not the current baseline. |
| SAXS lineout | Ten central rows, indices 2043–2052 | Used by clean scans, Methods, realistic reductions, and shifted-mask fractions. |

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
controls. The plotting notebook must use the same sigma selection and loads
the selected tree's calculation manifest. Loading the manifest is not a
complete cache-compatibility check. The current result tree is
`outputs/saxs_asymmetry/sigmaL_4p67nm_sigmaR_0nm/`.

#### Primary model and reduction controls

| Parameter | Active value | Meaning and scope |
|---|---:|---|
| Left wire-edge blur, `WIRE_SIGMA_LEFT_NM` | 4.67 nm | Gaussian smoothing applied to the negative-coordinate wire boundary. |
| Right wire-edge blur, `WIRE_SIGMA_RIGHT_NM` | 0 nm | Positive-coordinate wire boundary is unblurred. The selected model is asymmetric. |
| Shifted Mark1300 mask, `Q_MASK_SHIFT_NM_INV` | +0.005 nm⁻¹ | Moves the excluded q interval from approximately [−0.100, +0.100] to [−0.095, +0.105] nm⁻¹. This shifts the mask, not the simulated q data. |
| Mark1300 cutoff, `MARK1300_Q_MIN` | 0.10 nm⁻¹ | Excludes the intense central region from left/right SAXS sums. |
| Profile comparison limit, `Q_COMPARE_MAX` | 0.30 nm⁻¹ | Upper bound used for profile normalization and comparison plots; it does not change propagation. |
| Central rows | 10 | Shared clean, Methods, realistic, pointing, and shifted-mask SAXS extraction. |
| Gaussian geometry | Divergent and quasi-collimated | Selects the small or large source-waist root for a requested target FWHM. |

The left 4.67 nm edge sigma is a wire-boundary blur, not the Gaussian beam
sigma and not the beam FWHM. At 8 nm target sampling it is approximately
0.584 target pixel; the right sigma is zero. The selected pair is applied
to the projected-wire calculation, clean PCI
scan, realistic-profile target interaction, and analytic-chord comparison.
Experimental measurements and imported reference curves are not modified by
this sigma.

During the clean pass, shifted-q tables are calculated for the small-root
7.11 µm and 6.0 µm cases. Notebook 02 also applies the shifted mask to saved
realistic lineouts for selected comparison panels. The dedicated realistic
smoothing-pair sweep remains unshifted. The +0.005 nm⁻¹ shift is about
26 q-grid samples; the 0.10 nm⁻¹ central half-width is about 522 samples.

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
| Divergence study | Same 43-offset 0.48 µm grid as Clean SAXS. |
| Analytic transmission | 49 evenly spaced offsets from −10 to +10 µm. |
| Experimental PCI/SAXS image comparison | 43 matched offsets from −10.0 through +10.16 µm at 0.48 µm spacing, using the exact Clean SAXS grid. |
| Methods GIF | 43 frames from −10.0 through +10.16 µm at 0.48 µm spacing, using every generated Methods offset. |

#### Changes relative to the repository baseline

The active workflow introduces or changes the following controls:

- independent left/right wire-edge sigmas, currently set to the asymmetric 4.67/0 nm model;
- sigma-tagged output trees so different sigma pairs remain isolated;
- all active 7.1 µm cases conformed to 7.11 µm, plus the 6.0 µm SAXS/PCI case;
- the divergence comparison to include 6, 9, and 12 µm on the common 43-offset grid;
- projected-wire voxel size from 20 to 8 nm;
- clean SAXS offset spacing from 0.5 to 0.48 µm; and
- `FORCE_RECALCULATE` from false to true for the current production run.

The +0.005 nm⁻¹ q-mask shift remains an explicit control but was already
present in the earlier workflow. The experimental-comparison gallery and GIF
consume the exact 0.48 µm Clean SAXS grid so every requested plot has a
corresponding stored TIFF.

### Standalone Gaussian sigma comparisons

`src/SAXS_asymmetry/quick_symmetric_sigma_check.py` is a separate sensitivity
runner. Its default symmetric sweep is

```text
sigma_left = sigma_right = 0, 3, 4, 6, 8, or 14 nm.
```

It produces the Mark1300 observable for the 7.11 µm divergent beam.
The sweep uses 43 offsets from −10.0 through +10.16 µm at 0.48 µm spacing:

| Observable | Fast-path method | Main finding |
|---|---|---|
| Small-root Gaussian Mark1300 fraction | Separable 1-D complex field and 4096-point Fresnel FFT with a shifted, fractional-bin q mask; overlay the measured motor fraction | Compare response shapes only with matching sigma, q shift, and normalization. Older numerical sweep summaries are not current-baseline predictions. |

The fraction plot is saved separately from two standalone 8 × 6 inch wire-edge
thickness figures: the left edge (−5.04 to −4.99 µm) uses the `_wire_left_edge`
filename suffix, and the right edge (4.99 to 5.04 µm) uses `_wire_right_edge`.
Both figures use matching rainbow colors and legend labels for every sigma.
Repeatable `--sigma-pair LEFT RIGHT` arguments instead select independent
edges. Pair mode writes normalized left/right intensities and their fraction,
using the same mask shift in both panels. Each scan shares one
`max(left + right)` denominator, rather than normalizing halves independently.
The measured fraction is loaded separately from the measured halves.
`--sigmas` and `--sigma-pair` are mutually exclusive.

The default output directory is
`outputs/saxs_asymmetry/quick_symmetric_sigma/`; `--output-dir` isolates trials,
and `--no-plot` writes tables only. Old files in that directory do not establish
the parameters of a new run.

### Realistic smoothing-pair sweep

Notebook 01 also compares `(0, 0)`, `(3, 3)`, `(4, 4)`, `(4.67, 0)`,
`(6, 8)`, and `(8, 14)` nm using measured incident amplitude and the 7.11 µm
small-root Gaussian phase model. This is a full realistic-field calculation,
not the separable Gaussian CLI reduction.

It saves two-column offset/fraction checkpoints and
`realistic_7p11um_unshifted_fL_smoothing_pairs.npz` under
`outputs/saxs_asymmetry/realistic_sigma_pair_scan/`. Bundle metadata records
sigma pairs, grid, pixel size, offset step, q cutoff and shift, phase FWHM,
and lineout row count. Its mask is unshifted and uses signed horizontal q.

Notebook 02 overlays measured motor fractions and a ±1 µm horizontal-position
uncertainty envelope. It saves
`02_realistic_7p11um_fL_smoothing_pairs.png` and a vector PDF. The current
3.4 × 3.4 inch layout fits one manuscript column with a single-column legend
above the axes. Keep the 8.5/7.5/7.6 pt label/tick/legend typography readable
at `\columnwidth`; do not treat a renamed manuscript copy as a separate
simulation result.


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

Notebook 01 creates four cases: small-root and large-root beams at 6.0 and
7.11 µm target FWHM. Each scans the selected 10 µm Cu wire, propagates
1.31 m, saves float32 detector TIFFs, and reduces ten central rows outside
the Mark1300 central q mask.

!!! note "Generated figure"

    `saxs/figures/SAXS_Mark1300_collimated_6um_7p11um.png` is relative to the
    selected sigma tree. Run notebook 02 after generating compatible inputs.

**Figure 1. Clean SAXS comparison.** At fixed material and propagation, changing the Gaussian root changes wavefront curvature. The left fraction remains an S-shaped offset calibration, while detailed left/right amplitudes and saturation shift slightly.

The earlier symmetric 4/4 nm audit found approximately half left fraction
near the center. Do not reuse those numerical ranges for the current
asymmetric wire. The 43-point grid contains no exactly zero offset; any
reported centered value must state whether it was separately calculated or
interpolated.

> **Lesson:** matching target FWHM is necessary but not sufficient. Compare the root, wavefront radius, intensity profile, and propagated detector sampling together.

---

## 06 Workflow B — asymmetry methods and gallery

*Offset, divergence, and visual cross-checks*

| Branch | Calculation | Purpose |
|---|---|---|
| Offset scan | Reuse clean small-root 7.11 µm TIFFs; ten-row Mark1300 sums and display profiles | Dense calibration curve and experimental lineout comparison. |
| Divergence scan | 7.11 µm baseline plus 6, 9, 12 µm divergent and 12 µm large-root cases | Separate spot-size/curvature effects on calibration slope. |
| Gallery/movie | Target-exit PCI beside far-field SAXS for each wire offset | Verify that spatial motion and left/right response are physically consistent. |

!!! note "Generated figure"

    `methods/figures/05_divergence_scan.png` is relative to the selected sigma
    tree. Its five cases share the 43-offset grid.

**Figure 2. Divergence-scan comparison.** Compare the five cases with their
specified Gaussian root and target FWHM; width alone does not identify phase
curvature.

The table schema is `case`, `offset_um`, `mark1300_frac`.
Notebook 02 now reads that schema and has a color mapping for all five cases.
The older schema/color mismatch is no longer an open issue in that cell.

---

## 07 Workflow C — clean PCI and shifted-q correction

*Separate target-exit attenuation from detector-plane phase contrast*

!!! note "Generated figure"

    `clean_pci/clean_pci_field_overview_6um.png` is relative to the selected
    sigma tree.

**Figure 3.** The 6.0 µm clean PCI chain: incident beam, wire thickness, target-exit attenuation, and propagated detector fringes. The last panel is the physical manifestation of phase-to-intensity conversion.

The clean branch calculates 6.0 and 7.11 µm detector PCI using exact angular-spectrum propagation over 6.31 m. It separately scans target-exit left/right transmission without propagation. These are deliberately different observables.

### Shifted-q detector-center correction

The unshifted Mark1300 reduction rejects \|q\| < 0.10 nm⁻¹. With `q_shift = +0.005 nm⁻¹`, the accepted sides become approximately `q < -0.095` and `q > +0.105` nm⁻¹. This is equivalent to evaluating `|q - 0.005| ≥ 0.10` nm⁻¹.

| Shifted-q case | Current saved table | Columns |
|---|---|---|
| 7.11 µm | `clean_pci/mark1300_7p11um_shifted_q_mask_left_fraction.dat` | Offset in µm, ten-row fraction. |
| 6.0 µm | `clean_pci/mark1300_6p0um_shifted_q_mask_left_fraction.dat` | Offset in µm, ten-row fraction. |

> **Lesson from the 6.0 µm correction**
> Per-case accumulators are essential. Notebook 01 now stores each case
> independently. The current schema is two columns, not the older
> offset/two-row/ten-row format. Regenerate legacy files; do not assume the
> plotting loader validates every stale-cache condition.

---

## 08 Physical comparison in one figure

*What the active 6.0/7.11 µm results say*

!!! note "Generated figure"

    `clean_pci/clean_pci_saxs_mark1300_left_right_vs_offset.png` is relative
    to the selected sigma tree.

**Figure 4. Three-panel summary.** Top: target-exit PCI transmission and
experimental transmission. Middle: SAXS side signals. Bottom: shifted-q
asymmetry, including independent 6.0 and 7.11 µm ten-row curves.

| Observation | Physical reading |
|---|---|
| Exit transmission minimum | The centered wire blocks the highest-fluence part of the beam; the 6.0 µm spot gives a deeper minimum than 7.11 µm. |
| SAXS left/right exchange | Moving the wire reverses which finite-q side receives more power, giving the calibration sigmoid. |
| Shifted baseline | A centered symmetric object no longer gives 0.5 because the analysis mask is intentionally displaced. |
| Ten-row averaging | A fixed extraction convention, not an independent source of noise or a detector-noise simulation. |

---

## 09 Workflow D — realistic measured illumination

*Retain measured amplitude, supply a modeled phase*

The measured profile branch reads `RealisticProfile_10nm.tif`, clips invalid/negative values, resamples from 10 nm to the 8 nm simulation grid, normalizes total intensity, and uses `sqrt(intensity)` as amplitude. The missing phase is supplied by the divergent 7.11 µm Gaussian curvature.

!!! note "Generated figure"

    `realistic_profile/figures/01_realistic_vs_gaussian_profile.png` is
    relative to the selected sigma tree.

**Figure 5.** The measured profile is structured and slightly asymmetric relative to the nominal Gaussian. This changes beam–wire overlap and therefore both exit transmission and SAXS asymmetry.

| Saved observable | Convention |
|---|---|
| Target-exit left fraction | Exit-plane left sum divided by total exit sum; not propagated detector PCI. |
| Total transmission | Exit-plane total divided by incident total. |
| Realistic SAXS left fraction | Ten-row signed-horizontal-q side sums using the unshifted `Q_AXIS` cutoff. |
| Detector lineout bundle | Raw ten-row lineouts, q axis, offsets in µm, and lineout-row metadata. |

Numerical ranges from the previous symmetric-sigma snapshot are not current
values. Derive them from the selected sigma tree and state any interpolation
used to quote a value at zero offset.

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

The current calculation notebook reuses small-root 7.11 µm SAXS TIFFs and
calculates distinct analytic-chord target-exit PCI images. It also writes
`experimental_comparison/tables/analytic_exit_transmission.dat` on a
49-offset grid. The simulated transmission is normalized by its maximum;
the experimental transmission is normalized separately for shape comparison.

!!! note "Calculation and plotting revisions differ"

    Notebook 02's Gaussian comparison section currently saves SAXS-only
    detector images. Its plotting code does not consume the analytic PCI and
    transmission outputs still produced by notebook 01. Those files are not
    evidence that the SAXS-only figure contains propagated PCI.

### Position-matched realistic detector figures

Notebook 02 has a plotting section that loads
`combined_plot_data/rosa_realistic_detector_comparison.npz` from the selected
sigma tree. It expects experimental/simulated images, actual and requested
offsets, motor positions, filenames, and explicit experimental/simulation
extents. It saves figures under `realistic_profile/figures/rosa_wire_scan/`.
The panels use separate logarithmic intensity scales, not an absolute-flux
calibration.

The current notebook 01 contains no cell that produces this bundle, and its
completion manifest does not list it. Do not promise that running notebook 01
from top to bottom regenerates these figures. Supply a bundle from the
matching calculation revision before using that plotting section. The README
describes a producer that is not present in this notebook snapshot.

### Legacy calculation families

| Artifact | Use | Do not assume |
|---|---|---|
| `SAXS_PCI_Pointing_Div.ipynb` | Reproduce historical Gaussian/wire propagation and TIFFs | Current q mask, axis direction, or filenames. |
| `PlotSAXS_Pointing_Div.ipynb` | Reproduce earlier Mark1300 plots | Current row averaging, central exclusion, or orientation. |
| Historical `idealc.ipynb` reference | Older idealized LightPipes-style study; notebook absent from the current checkout | A runnable entry point in the current repository. |
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
| Dependency contract | Declared NumPy/SciPy notebook stack | Additional `multiprocess`, `torch`, `torchvision`, and `torchaudio` imports are outside the declared project dependencies. |
| Portability | Repository-contained except optional LightPipes | Machine-specific external search path and `propagatorsv1` import. |
| Device/batch | Single array, CPU | `device` and `batch_size` parameters; spot shifts and noise batches |
| Precision | Mostly NumPy `complex128` unless cast | Gaussian source explicitly `complex64` |
| Propagators | Angular spectrum, scaled Fresnel, optional LightPipes | Angular spectrum, scaled Fresnel, and external selectable propagators |
| Autograd | Not applicable | Core FFT operations can be differentiable, but SciPy, NumPy, `detach`/`cpu` calls, and global diagnostics break end-to-end guarantees |
| Validation status | Used by the calculation notebook | No parity tests or benchmark in the current test suite. |

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
| Clean/realistic offset grid | 43 samples from −10.0 through +10.16 µm at exactly 0.48 µm spacing | Methods, divergence, paired comparison, and GIF reuse it; clean PCI and analytic transmission retain separate grids. |
| Two q-axis conventions | `linspace` endpoints differ slightly from exact FFT-bin spacing | Use one exported q axis for masks, interpolation, tables, and plots. |
| Old shifted-mask tables | Three-column two-row/ten-row artifacts do not match the current two-column format | Regenerate both cases with ten-row extraction and rerun the completion cell. |
| Manifest coverage | The completion cell lists both shifted cases, but not the realistic smoothing sweep or position-matched detector bundle | Track these additional inputs separately; the manifest is not an exhaustive inventory. |
| Pair-checkpoint reuse | Valid shape/offset/finiteness does not establish full physical compatibility | Invalidate affected pair tables when source, target, grid, or reduction assumptions change. |
| Detector comparison producer missing | Position-matched plotting consumes a bundle absent from the current calculation pipeline | Obtain the matching producer revision or an existing compatible bundle before plotting. |
| Historical baseline | Old 4/4 nm results can be mistaken for the current 4.67/0 nm selection | State sigma pair, extraction schema, and q shift with every reported value. |

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
| 5. Reduction conventions | Mark1300 mask, shifted q, ten-row extraction, legacy two-row distinction, left/right orientation. |
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
| `notebooks/saxs_asymmetry/01_calculate_and_save_data.ipynb` | Active calculation and artifact pipeline. |
| `notebooks/saxs_asymmetry/02_plot_and_save_figures.ipynb` | Artifact-consuming plotting pipeline; does not repeat propagation. |
| `src/SAXS_asymmetry/quick_symmetric_sigma_check.py` | Standalone Gaussian symmetric-sigma or independent-pair sensitivity tool. |
| `src/SAXS_asymmetry/paths.py` | Canonical repository paths and environment overrides. |
| `src/SAXS_asymmetry/PCI.py` | Reference NumPy/SciPy wave-propagation implementation. |
| `src/SAXS_asymmetry/PCI_torch.py` | Experimental PyTorch port. |
| `docs/SAXS-PCI.md` | Unified physical interpretation. |
| `docs/propagators.md` | Propagation equations and intended implementation behavior. |
| `docs/saxs_intensity_workflow.md` | Detailed SAXS workflow and propagation notes. |
| `docs/pci_intensity_workflow.md` | Detailed PCI workflow and physical interpretation. |
| `outputs/saxs_asymmetry/<sigma_tag>/combined_plot_data/calculation_manifest.json` | Selected-run manifest written by notebook 01's completion cell. |

### Primary generated artifacts cited in the analysis

| Artifact family | Location |
|---|---|
| Clean SAXS tables/TIFFs | `outputs/saxs_asymmetry/<sigma_tag>/saxs/` |
| Methods tables/figures/movie | `outputs/saxs_asymmetry/<sigma_tag>/methods/` |
| Clean PCI fields/tables/figures | `outputs/saxs_asymmetry/<sigma_tag>/clean_pci/` and `outputs/saxs_asymmetry/<sigma_tag>/combined_plot_data/` |
| Symmetric-sigma sensitivity tables/figures | `outputs/saxs_asymmetry/quick_symmetric_sigma/` |
| Realistic smoothing-pair results | `outputs/saxs_asymmetry/realistic_sigma_pair_scan/` |
| Realistic-profile results | `outputs/saxs_asymmetry/<sigma_tag>/realistic_profile/` |
| Experimental comparison | `outputs/saxs_asymmetry/<sigma_tag>/experimental_comparison/` |

Here `<sigma_tag>` is generated from the selected pair; the current value is
`sigmaL_4p67nm_sigmaR_0nm`. The directory structures above are relative to the
default output root and follow `PCI_OUTPUT_DIR` when overridden.

---

### Status of this guide

This guide was updated against the repository structure and notebook sources
on 22 October 2026. It is not a new numerical validation of every saved
artifact, nor a substitute for experimental calibration, uncertainty
analysis, or peer-reviewed validation of the physical model.

*Prepared locally from repository sources. No external scientific claims were introduced beyond the equations and assumptions implemented or documented in the codebase.*

---

*Originally converted from a historical PDF report. Generated figures are
described by their current artifact locations rather than embedded in the
documentation site.*
