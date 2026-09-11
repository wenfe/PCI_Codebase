# Variables & Functions Reference

Covers both notebooks:

- [Part 1 — `01_calculate_and_save_data.ipynb`](#part-1--01_calculate_and_save_dataipynb) (the numerical pipeline)
- [Part 2 — `02_plot_and_save_figures.ipynb`](#part-2--02_plot_and_save_figuresipynb) (the plotting pipeline)

---

# Part 1 — `01_calculate_and_save_data.ipynb`

Units follow `PCI.py` base units: **length = nm** (`nm=1.0`, `um=1e3`, `mm=1e6`, `m=1e9`), **energy = keV** (`keV=1`, `eV=1e-3`). So `PIXEL_SIZE = 8*PCI.nm` is the float `8.0`, and `Z_TARGET = 0.25*PCI.m` is `2.5e8`. Grid is always `(4096, 4096)`.

---

## Cell 2 — Shared setup

**Paths & config** — all `pathlib.Path`: `START_DIR`, `SAXS_DIR`, `INPUT_DIR`, `OUTPUT_ROOT`, `OUTPUT_DIR`, `PLOT_DATA_DIR`. `OUTPUT_DIR` is the sigma-specific root `outputs/sigmaL_4nm_sigmaR_4nm`; `SIGMA_TAG` is the string `"sigmaL_4nm_sigmaR_4nm"`. `FORCE_RECALCULATE` is `bool` (`True`).

**Scalar constants**

| Name | Type | Value |
|---|---|---|
| `N_GRID` | `int` | 4096 |
| `PIXEL_SIZE` | `float` | 8.0 nm |
| `PHOTON_ENERGY` | `float` | 8.2 keV |
| `LAMBDA_NM` | `float` | ≈0.15120 nm |
| `Z_TARGET` / `Z_SAXS_DETECTOR` / `Z_PCI_DETECTOR` | `float` | 2.5e8 / 1.31e9 / 6.31e9 nm |
| `WIRE_RADIUS` | `float` | 5000.0 nm |
| `WIRE_VOXEL_SIZE` | `float` | 8.0 nm |
| `WIRE_VOXEL_NUMBER` | `int` | 2000 |
| `WIRE_SIGMA_LEFT_NM` | `float` | 4.0 nm (0.5 target pixel) |
| `WIRE_SIGMA_RIGHT_NM` | `float` | 4.0 nm (0.5 target pixel) |
| `GRID_CENTER` | `int` | 2048 |
| `Q_MAX` | `np.float64` | ≈0.3927 nm⁻¹ |
| `Q_STEP` | `float` | ≈1.9175e-4 nm⁻¹ |
| `MARK1300_Q_MIN` | `float` | 0.10 nm⁻¹ |
| `MARK1300_CENTER_HALF_WIDTH_PIXELS` | `int` | 522 |

**Axis arrays** — `SPACE_AXIS_NM` and `Q_AXIS`, both `np.ndarray (4096,) float64`.

**Functions / class**

| Name | Signature | Returns |
|---|---|---|
| `voxelized_chord_profile` | `(radius, voxel_size, voxel_number)` | `ndarray (2000,) float64` — thickness in nm |
| `asymmetric_blur_profile` | `(profile, *, sigma_left_nm, sigma_right_nm, sample_size_nm, center_index=None, truncate=3.0)` | `ndarray` — projected thickness convolved separately on the left and right |
| `source_waist_for_target_fwhm` | `(fwhm, *, divergent=True, wavelength, distance)` | `np.float64` — waist in nm |
| `ProjectedWire` | `class(PCI.wire)` | stores `sigma_left_nm`/`sigma_right_nm`; overrides `_get_projection()` → blurred `ndarray (2000,2000) float64`, cached in `self._density1` |
| `make_projected_wire` | `(offset_um, *, z_target, sigma_left_nm=4.0, sigma_right_nm=4.0)` | `ProjectedWire` |
| `make_xfel` | `(source_waist_nm=None)` | `PCI.XFEL` if `None`, else `PCI.gaussian_XFEL` |
| `save_float32_tiff` | `(path, array)` | `None` |
| `load_float32_tiff` | `(path)` | `ndarray float32` (copy) |
| `central_row_lineout` | `(intensity, row_count, *, dtype=None)` | `ndarray (4096,)` |
| `mark1300_sides` | `(lineout)` | **`tuple[float, float]`** |
| `signed_half_weights` | `(axis, *, tolerance, dtype=float)` | **`tuple[ndarray, ndarray]`** |
| `offset_tag` | `(offset_um, decimals=1)` | `str` (`-2.5 → "m2p5"`) |
| `simulate_gaussian_saxs_intensity` | `(source_waist_nm, offset_um)` | `ndarray (4096,4096) float32` |
| `get_gaussian_saxs_tiff` | `(source_waist_nm, offset_um, path)` | `ndarray float32` |
| `load_pointing_profiles` | `()` | `dict[int, tuple[ndarray, ndarray]]` |
| `pointing_lineout` | `(lineout)` | `ndarray` resampled onto `POINTING_Q_AXIS`, max = 2 |

Inside `load_pointing_profiles`: `scales` is `dict[int, float]` (`{528: 50e3, 534: 80e3, 546: 80e3}`), `profiles` is `dict[int, tuple]`, and `q_positive`/`left`/`right` are `ndarray float64`.

- `POINTING_EXPERIMENTAL` — `dict[int, tuple[ndarray, ndarray]]`, keys `528, 534, 546`
- `POINTING_Q_AXIS` — `ndarray float64`

---

## Cell 4 — Clean Gaussian SAXS scan

`SAXS_OUTPUT_DIR`, `SAXS_TABLE_DIR`, `SAXS_TIFF_ROOT` — `pathlib.Path`.

**`make_clean_saxs_case(fwhm_um, *, divergent) -> dict`** with keys:

| Key | Type |
|---|---|
| `"name"` | `str` (e.g. `"mark1300_7p11um"`) |
| `"label"` | `str` |
| `"fwhm_um"` | `float` |
| `"source_waist"` | `np.float64` (nm) |
| `"data_dir"` | `Path` |
| `"table_path"` | `Path` |

Locals: `tag`, `geometry`, `table_name`, `name` — `str`; `source_waist` — `np.float64`.

| Name | Type | Detail |
|---|---|---|
| `CLEAN_SAXS_CASES` | **`dict[str, dict]`** | 4 entries: `mark1300_7p11um`, `collimated_7p11um`, `collimated_6um`, `mark1300_6um` |
| `CLEAN_SAXS_OFFSET_STEP_UM` | `float` | 0.48 µm |
| `CLEAN_SAXS_OFFSET_MIN_UM` / `CLEAN_SAXS_OFFSET_MAX_UM` | `float` | −10.0 / +10.16 µm |
| `CLEAN_SAXS_OFFSETS_UM` | `ndarray (43,) float64` | 0.48 µm grid from −10.0 through +10.16 µm |
| `Q_MASK_SHIFT_NM_INV` | `float` | 0.005 nm⁻¹ |
| `shifted_q_axis` | `ndarray (4096,) float64` | |
| `shifted_left_edge` / `shifted_right_edge` | `float` | −0.095 / 0.105 nm⁻¹ |
| `shifted_left_weights` / `shifted_right_weights` | `ndarray (4096,) float64` | soft 0→1 masks |
| `SHIFTED_MASK_CASES` | **`tuple[str, str]`** | `("mark1300_7p11um", "mark1300_6um")` |

**Accumulators**

| Name | Type |
|---|---|
| `clean_saxs_records` | `dict[str, ndarray (43,3)]` |
| `clean_7p11um_ten_row_pointing` | `list[ndarray float32]` |
| `shifted_saxs_rows` | `dict[str, list[tuple[float,float,float]]]` |
| `clean_profile_bundle` | `dict[str, ndarray]` — `"q_reference"`, `"offsets_um"`, then `"<case>_lineouts"` |

**Loop vars** — `for case_name, case in CLEAN_SAXS_CASES.items()` yields 2-tuples, but unpacked: `case_name` is `str` (the key), `case` is `dict` (the config). Also `records` (`list` → `ndarray (43,3)`), `pointing_lineouts` (`list`), `index` (`int`), `offset_um` (`np.float64`), `detector_path` (`Path`), `intensity` (`ndarray (4096,4096) float32`), `two_row_lineout`/`ten_row_lineout` (`ndarray (4096,) float32`), `left`/`right` (`float`), `plot_lineout` (`ndarray`), `shifted_fractions` (`list[np.float64]`), `lineout` (`ndarray`), `shifted_left`/`shifted_right` (`np.float64`), `directory` (`Path`).

---

## Cell 6 — Methods, Method 1

| Name | Type |
|---|---|
| `METHODS_OUTPUT_DIR`, `METHODS_TABLE_DIR`, `METHODS_MOVIE_DIR`, `methods_table_path` | `Path` |
| `METHODS_SOURCE_WAIST` | `np.float64` |
| `METHODS_OFFSETS_UM` | `ndarray (43,)` — same object as `CLEAN_SAXS_OFFSETS_UM` |
| `clean_7p11um_case` | `dict` |
| `clean_7p11um_records` | `ndarray (43,3) float64` |
| `methods_records` | `list[dict]`, 43 entries |

`make_methods_record(offset_um, left, right, pointing) -> dict` with keys `"offset_um"` (`float`), `"mark1300_left"` (`float`), `"mark1300_right"` (`float`), `"mark1300_frac"` (`float`), `"pointing_lineout"` (`ndarray float32`).

`methods_record_from_intensity(intensity, offset_um) -> dict` — same shape, from a full detector image.

---

## Cell 8 — Method 2, divergence scan

| Name | Type | Detail |
|---|---|---|
| `divergence_table_path` | `Path` | |
| `DIV_OFFSETS_UM` | `ndarray (11,) float64` | `linspace(-10, 10, 11)` |
| `DIV_CASES` | **`dict[str, np.float64]`** | `"6.0 um FWHM"`, `"9.0 um FWHM"`, `"12.0 um FWHM"`, `"collimated"` → waist in nm |
| `divergence_rows` | `list[tuple[str, float, float]]` | 43 seeded rows plus the unchanged divergence cases |
| `case_name` / `waist_nm` | `str` / `np.float64` | loop over `DIV_CASES` |
| `fraction` | `float` | `mark1300_frac` |
| `stream` | `io.TextIOWrapper` | |

---

## Cell 10 — Method 3, movie data

| Name | Type |
|---|---|
| `methods_saxs_paths`, `methods_pci_paths` | `list[Path]` (43 each) |
| `methods_xfel` | `PCI.gaussian_XFEL` or `None` |
| `methods_incident` | `ndarray complex` or `None` |
| `methods_pci_exit_intensity(offset_um)` | → `ndarray (4096,4096) float64` |
| `methods_saxs_tiff`, `methods_pci_tiff`, `clean_tiff`, `path` | `Path` |

Both `methods_incident` and `methods_xfel` are `del`-ed at the end.

---

## Cell 12 — Clean detector-propagated PCI

| Name | Type | Detail |
|---|---|---|
| `CLEAN_PCI_DIR`, `clean_pci_fields_path`, `clean_pci_detector_path` | `Path` | |
| `COPPER_ATTENUATION_LENGTH_NM` | `float` | 1/µ for Cu, nm |
| `CLEAN_PCI_CASES` | **`dict[str, dict]`** | keys `"7p11um"`, `"6um"` |
| `pci_extent_um` | `ndarray (4,) float64` | imshow extent, µm |

Inner case dict: `"fwhm_um"` (`float`), `"fields_path"`/`"detector_path"`/`"table_path"`/`"raw_table_path"` (`Path`), plus `"incident_intensity"` (`ndarray (4096,4096) float64`) **added at runtime** and popped in cell 13.

- `angular_spectrum_propagate(field, distance_m) -> ndarray complex128`. Locals: `pixel_size_m`, `wavenumber_m` (`float`), `spatial_frequency` (`ndarray (4096,)`), `kx`/`ky`/`dispersion`/`root` (`ndarray (4096,4096)`), `kz` (`complex128`, imaginary where evanescent).
- `simulate_clean_pci(fwhm_um)` → **4-tuple** `(incident, thickness_nm, exit_field, detector_field)` = complex, float, complex, complex arrays. Locals include `xfel` (`gaussian_XFEL`), `target` (`ProjectedWire`), `wire_projection_nm` (`ndarray (2000,2000)`).

Loop: `pci_incident`, `pci_thickness_nm`, `pci_exit`, `pci_detector` — `ndarray`; `fields` — `NpzFile`.

---

## Cell 13 — Clean PCI exit scan

`scan_clean_pci_exit(wire_offsets_nm, incident_intensity)` → **3-tuple** `(left, right, total_before)` = `(ndarray (50,), ndarray (50,), float)`.

Locals: `center_index` (`int`), `incident_lineout` (`ndarray (4096,)`), `y_factor` (`np.float64`), `target_axis_nm`/`centered_chord_nm`/`shifted_chord_nm` (`ndarray (2000,)`), `left_weights`/`right_weights`/`thickness_nm`/`exit_lineout` (`ndarray (4096,)`).

| Name | Type |
|---|---|
| `clean_pci_offsets_um` | `ndarray (50,) float64` |
| `clean_pci_left`, `clean_pci_right`, `clean_pci_total` | `ndarray (50,) float64` |
| `clean_pci_before` | `float` |
| `clean_pci_normalized` | `ndarray (50,3) float64` |

Raises `FloatingPointError` (non-finite) or `ValueError` (transmission outside [0,1]).

---

## Cell 15 — Shifted-q tables

`saxs_7_shifted`, `saxs_6_shifted` — `ndarray (43,3) float64`.

---

## Cell 17 — Realistic-profile setup

| Name | Type | Detail |
|---|---|---|
| `REALISTIC_DIR`, `REALISTIC_TABLE_DIR`, `REALISTIC_TIFF_DIR`, `PROFILE_PATH` | `Path` | |
| `PROFILE_PIXEL_SIZE` | `float` | 10.0 nm |
| `REALISTIC_OFFSETS_UM` | `ndarray (43,)` | alias of `CLEAN_SAXS_OFFSETS_UM` |
| `REALISTIC_Q_MIN` | `float` | 0.10 nm⁻¹ |
| `image` | `PIL.TiffImageFile` | |
| `profile_native` | `ndarray float32` | cleaned in place |
| `index_scale` | `float` | 0.8 |
| `profile_raw` | `ndarray (4096,4096) float32` | |
| `realistic_incident` | `ndarray (4096,4096) float32` | sum-normalised to 1 |
| `realistic_xfel` | `PCI.XFEL` | plane source |
| `phase_source_waist`, `phase_rayleigh_range`, `phase_wavefront_radius` | `np.float64` | nm |
| `phase_1d` | `ndarray (4096,) complex64` | |
| `realistic_field_at_target` | `ndarray (4096,4096) complex64` | |

---

## Cell 18 — Realistic-profile scan

| Name | Type | Detail |
|---|---|---|
| `realistic_pci_table_path`, `realistic_saxs_table_path`, `realistic_lineout_path` | `Path` | |
| `realistic_tiff_path(offset_um)` | → `Path` | |
| `can_reuse_realistic` | `bool` | |
| `pci_table`, `saxs_table` | `ndarray` | reload branch only |
| `realistic_pci_left/right`, `realistic_saxs_left/right` | `list[float]` → `ndarray (43,)` | |
| `realistic_lineouts` | `list[ndarray]` → `ndarray (43,4096) float64` | |
| `realistic_pci_total`, `realistic_saxs_total` | `ndarray (43,)` | compute branch only |
| `left_q_mask`, `right_q_mask` | `ndarray (4096,) bool` | |
| `left_x_weights`, `right_x_weights` | `ndarray (4096,) float32` | |
| `incident_total` | `float` | |
| `target` | `ProjectedWire` | |
| `exit_field` | `ndarray complex64` | |
| `exit_intensity`, `saxs_intensity` | `ndarray float32` | |
| `saxs_field` | `ndarray complex` | |
| `lineout` | `ndarray (4096,) float64` | |

Note: `realistic_pci_left` and friends are `list` in the compute branch until rebound to `ndarray`; in the reuse branch they arrive as `ndarray` table columns. Same name, branch-dependent type.

---

## Cell 20 — Experimental-comparison setup

`EXPERIMENTAL_DIR`, `EXPERIMENTAL_TABLE_DIR`, `EXPERIMENTAL_PCI_TIFF_DIR` — `Path`; `comparison_case` — `dict`; `comparison_xfel` — `PCI.gaussian_XFEL`; `comparison_field_at_target` — `ndarray (4096,4096) complex`.

---

## Cell 21 — Analytic-chord PCI and transmission

| Name | Type | Detail |
|---|---|---|
| `copper` | `PCI.Cu` | |
| `absorption_coefficient_nm`, `phase_coefficient_nm` | `float` | per nm |
| `analytic_wire_chord_nm(offset_um)` | → `ndarray (4096,) float64` | |
| `analytic_pci_exit_intensity(offset_um)` | → `ndarray (4096,4096) float64` | |
| `thickness`, `factor` | `ndarray` (broadcast; `factor` `complex128`) | |
| `comparison_offsets_um` | `ndarray (43,) float64` | Copy of the 0.48 µm Clean SAXS grid; analytic PCI is generated at matching offsets |
| `comparison_pci_paths`, `comparison_saxs_paths` | `list[Path]` (43 each) | |
| `transmission_offsets_um` | `ndarray (49,) float64` | `linspace(-10, 10, 49)` |
| `incident_intensity` | `ndarray (4096,4096) float64` | `del`-ed at cell end |
| `incident_column_power` | `ndarray (4096,) float64` | |
| `incident_sum` | `float` | |
| `sim_transmission` | `list[float]` → `ndarray (49,) float64` | max-normalised |
| `exit_column_power` | `ndarray (4096,)` | |
| `pci_path` | `Path` | |

---

## Cell 23 — Completion summary

| Name | Type | Detail |
|---|---|---|
| `required_outputs` | **`dict[str, list[Path]]`** | 5 keys: `clean_saxs_tables`, `methods_tables`, `clean_pci`, `realistic_profile`, `experimental_comparison` |
| `missing` | `list[str]` | raises `RuntimeError` if non-empty |
| `summary` | `dict` | `"grid"` `int`, `"pixel_size_nm"` `float`, `"photon_energy_keV"` `float`, `"force_recalculate"` `bool`, `"sections"` `dict[str, list[str]]` |

---

## Cross-cell name reuse

`case_name`/`case` (cells 4, 12, 13 → `str` + `dict`; cell 8 → `str` + `np.float64` as `waist_nm`), `offset_um` (`np.float64`, cells 4/8/10/13/18/21), `intensity` (`ndarray float32`, cells 4/8/18), `index` (`int`), `directory` (`Path`), `lineout` (`ndarray`), `path` (`Path`).

---

## Types at a glance

- **`dict`** — `CLEAN_SAXS_CASES`, `CLEAN_PCI_CASES`, `DIV_CASES`, `POINTING_EXPERIMENTAL`, `clean_saxs_records`, `shifted_saxs_rows`, `clean_profile_bundle`, `required_outputs`, `summary`, every per-case config, every methods record
- **`tuple`** — `SHIFTED_MASK_CASES`; returns of `mark1300_sides`, `signed_half_weights`, `simulate_clean_pci`, `scan_clean_pci_exit`; each `(q_values, lineout)` in `POINTING_EXPERIMENTAL`; each `(case_name, case)` from `.items()`
- **`list`** — `methods_records`, `divergence_rows`, `clean_7p11um_ten_row_pointing`, `methods_saxs_paths`, `methods_pci_paths`, `comparison_*_paths`, `missing`
- **`pathlib.Path`** — every `*_DIR`, `*_ROOT`, `*_PATH`, `*_path`
- **`np.ndarray`** — every `*_AXIS`, `*_OFFSETS_UM`, `*_weights`, `*_mask`, `*lineout*`, `*intensity*`, `*field*`, `*_records`, `*_table`
- **`float`/`np.float64`** — physical constants, `*_coefficient*`, `*_waist*`, left/right sums
- **`int`** — `N_GRID`, `GRID_CENTER`, `WIRE_VOXEL_NUMBER`, `MARK1300_CENTER_HALF_WIDTH_PIXELS`, `index`
- **`bool`** — `FORCE_RECALCULATE`, `can_reuse_realistic`
- **classes** — `ProjectedWire` (subclass of `PCI.wire`); instances of `PCI.XFEL`, `PCI.gaussian_XFEL`, `PCI.jungfrau`, `PCI.Beamline`, `PCI.Cu`

---

**Note on the `.items()` pattern:** in `for case_name, case in CLEAN_SAXS_CASES.items()`, the *pair* is a tuple, but `case_name` is a `str` and `case` is a `dict`. The only actual tuple constant in the notebook is `SHIFTED_MASK_CASES`.

---
---

# Part 2 — `02_plot_and_save_figures.ipynb`

Read-only plotting pipeline: it loads the tables, TIFFs, and `.npz`/`.npy` bundles written by notebook 01 and never repeats a propagation. Same unit conventions as Part 1. Extra import: `rossendorfer_farbenliste as rofl` (a colour helper — `rofl.b()`, `rofl.o()`, `rofl.g()` return colour values; `rofl.cmap()` returns a matplotlib colormap).

Both notebooks use the fixed `SIGMA_TAG = "sigmaL_4nm_sigmaR_4nm"`. Calculations and figures are isolated below `SAXS_asymmetry/outputs/sigmaL_4nm_sigmaR_4nm/`, and notebook 02 validates that the selected calculation manifest has the same tag.

---

## Cell 2 — Load plotting setup

**Paths** — all `pathlib.Path`: `START_DIR`, `SAXS_DIR`, `INPUT_DIR`, `OUTPUT_ROOT`, `OUTPUT_DIR`, `PLOT_DATA_DIR`, `SAXS_PICKLE_DIR`, `ERIK_DIR`, `LINGEN_REFERENCE_PATH`, `TRANSMISSION_SCAN_PATH`, `manifest_path`.

**Constants**

| Name | Type | Value |
|---|---|---|
| `N_GRID` | `int` | 4096 |
| `PIXEL_SIZE` | `float` | 8.0 nm |
| `WIRE_SIGMA_LEFT_NM` / `WIRE_SIGMA_RIGHT_NM` | `float` | 4.0 / 4.0 nm |
| `SIGMA_TAG` | `str` | `"sigmaL_4nm_sigmaR_4nm"` |
| `Z_SAXS_DETECTOR` | `float` | 1.31e9 nm |
| `Q_MAX` | `np.float64` | ≈0.3927 nm⁻¹ |
| `Q_STEP` | `float` | ≈1.9175e-4 nm⁻¹ |
| `Q_MIN` | `float` | 0.10 nm⁻¹ — inner exclusion radius |
| `Q_MASK_SHIFT_NM_INV` | `float` | +0.005 nm⁻¹ — shifted-mask centre |
| `Q_COMPARE_MAX` | `float` | 0.30 nm⁻¹ — outer band edge for normalisation |
| `MOTOR_POSITION_UNCERTAINTY_UM` | `float` | 1.0 µm horizontal uncertainty |
| `EXPERIMENTAL_RUNS` | **`tuple[int, int, int]`** | `(528, 534, 546)` |
| `Q_AXIS` | `ndarray (4096,) float64` | `linspace(-Q_MAX, Q_MAX, 4096)` |
| `SAMPLE_AXIS_UM` | `ndarray (4096,) float64` | real-space axis in µm |
| `SAMPLE_EXTENT_UM` | `list[float]` — 4 elements | `[x0, x1, x0, x1]` for `imshow` |
| `Q_EXTENT` | `list[float]` — 4 elements | `[-qmax, qmax, -qmax, qmax]` |

> `SAMPLE_EXTENT_UM` and `Q_EXTENT` are plain Python **lists** built by `[a, b] * 2`, not arrays (unlike `pci_extent_um` in notebook 01, which is an `ndarray`).

**Helper functions**

| Name | Signature | Returns |
|---|---|---|
| `require` | `(path)` | `pathlib.Path` — raises `RuntimeError` if missing |
| `load_tiff` | `(path)` | `ndarray float32` (copy) |
| `save_figure` | `(fig, path, *, dpi=200)` | `pathlib.Path` — creates parent dirs, saves with `bbox_inches="tight"` |
| `offset_tag` | `(offset_um, decimals=1)` | `str` — identical to notebook 01's version |
| `load_run_halves` | `(run: int)` | **`tuple[ndarray, ndarray, ndarray]`** — `(q_positive, left, right)`, `float64`, NaN→0 |
| `load_pointing_profiles` | `()` | `dict[int, tuple[ndarray, ndarray]]` — mirrored, scale-normalised |
| `load_realistic_experimental_profile` | `(run: int)` | `dict` with `"q"` (`ndarray`), `"normalized"` (`ndarray`), `"left_fraction"` (`np.float64`) |
| `load_erik_reference` | `()` | `dict[str, ndarray]` — 7 keys, see below |
| `load_transmission_scan` | `()` | **`tuple[ndarray, ndarray]`** — `(position_um, normalized_transmission)` |

Locals worth noting:

- `load_pointing_profiles`: `scales` — `dict[int, float]` `{528: 50e3, 534: 80e3, 546: 80e3}`; `profiles` — `dict[int, tuple]`; `q`, `lineout` — `ndarray float64`
- `load_realistic_experimental_profile`: `keep` (`ndarray bool`), `order` (`ndarray int64` from `argsort`), `q_signed` / `intensity` (`ndarray float64`), `scale_mask` / `outer` (`ndarray bool`)
- `load_erik_reference`: `ratio`, `total`, `right` — `ndarray float64`
- `load_transmission_scan`: `data` (`ndarray (3, N)` after the optional transpose), `minimum` (`int`)

**`load_erik_reference()` dict keys** — every value an `ndarray float64`:
`"offsets_um"`, `"left"`, `"right"`, `"total"`, `"left_fraction"`, `"motor_offsets_um"`, `"motor_left_fraction"`.

**Module-level loaded references**

| Name | Type | Detail |
|---|---|---|
| `pointing_experimental` | `dict[int, tuple[ndarray, ndarray]]` | keys `528, 534, 546` |
| `erik` | `dict[str, ndarray]` | the 7 keys above |
| `transmission_position_um`, `transmission` | `ndarray float64` | unpacked 2-tuple from `load_transmission_scan()` |

---

## Cell 5 — Quick sigma and Mark1300 check

This lightweight cell validates the manifest's `wire_sigma_left_nm` and
`wire_sigma_right_nm` against the configured 4 nm/4 nm values. It plots the
two normalized Gaussian kernels and reads only the divergent Mark1300 7.11 µm
and 6 µm tables for their normalized left/right signals and `L/(L+R)` curves.
It does not load detector TIFFs or repeat propagation.

| Name | Type | Detail |
|---|---|---|
| `manifest_sigmas`, `configured_sigmas` | `tuple[float, float]` | saved and selected left/right sigma pairs |
| `quick_table_dir`, `quick_figure_dir`, `quick_check_path` | `Path` | sigma-tagged input/output paths |
| `quick_mark1300_cases` | `dict[str, Path]` | divergent 7.11 µm and 6 µm tables |
| `sigma_axis_nm`, `kernel` | `ndarray` | normalized Gaussian-kernel plot data |
| `fig`, `axes` | `Figure`, `ndarray (3,)` of `Axes` | sigma, left/right, and asymmetry panels |

Output: `quick_sigma_Mark1300_7p11um_vs_6um.png`.

---

## Cell 6 — Clean SAXS per-offset figures

| Name | Type | Detail |
|---|---|---|
| `SAXS_OUTPUT_DIR`, `SAXS_TABLE_DIR`, `SAXS_FIGURE_DIR`, `SAXS_TIFF_ROOT` | `Path` | |
| `clean_cases` | **`dict[str, dict]`** | 4 keys, matching notebook 01's `CLEAN_SAXS_CASES`; each value has `"label"` (`str`) and `"table"` (`Path`) — **only 2 keys**, unlike the 6-key config dicts in 01 |
| `clean_profiles` | `np.lib.npyio.NpzFile` | `clean_saxs_profiles.npz` |
| `pointing_q` | `ndarray` | `clean_profiles["q_reference"]` |

**Loop vars**: `case_name` (`str`), `case` (`dict`), `table` (`ndarray (43,3)`), `offsets_um` / `fractions` (`ndarray (43,)`), `lineouts` (`ndarray (43, Nq)`), `results_dir` / `data_dir` (`Path`), `index` (`int`), `offset_um` / `fraction` (`np.float64`), `lineout` (`ndarray`), `intensity` (`ndarray (4096,4096) float32`), `fig` (`matplotlib.figure.Figure`), `axes` (`ndarray` of `Axes`, shape `(2,)`), `image` (`AxesImage`), `output_path` (`Path`), `run` (`int`), `q_values` / `experimental` (`ndarray`).

---

## Cell 7 — Combined 4-case asymmetry figure

| Name | Type | Detail |
|---|---|---|
| `fig` | `Figure` | |
| `axes` | `ndarray (2,)` of `Axes` | |
| `styles` | **`dict[str, dict]`** | case name → `{"color": str, "marker": str}` kwargs |
| `table` | `ndarray (43,3)` | |
| `offsets_um`, `left`, `right` | `ndarray (43,) float64` | |
| `scale` | `np.float64` | `nanmax(left + right)` |

Output: `SAXS_Mark1300_collimated_6um_7p11um.png`.

---

## Cell 9 — Methods offset-scan figure

| Name | Type | Detail |
|---|---|---|
| `METHODS_DIR`, `METHODS_TABLE_DIR`, `METHODS_FIGURE_DIR`, `METHODS_MOVIE_DIR`, `METHODS_FRAME_DIR` | `Path` | |
| `methods_profiles` | `NpzFile` | keys `"q"`, `"offsets_um"`, `"lineouts"` |
| `methods_table` | `ndarray (43,3) float64` | |
| `methods_offsets_um`, `methods_fraction` | `ndarray (43,) float64` | |
| `lingen_table` | `ndarray` | external 6 µm reference |
| `lingen_offsets_um`, `lingen_fraction` | `ndarray float64` | |
| `cmap` | `matplotlib.colors.LinearSegmentedColormap` | `plt.cm.coolwarm` |
| `offset_um`, `lineout`, `run`, `q_values`, `experimental` | loop vars — `np.float64`, `ndarray`, `int`, `ndarray`, `ndarray` | |

Output: `01_offset_scan.png`.

---

## Cell 10 — Divergence-scan figure

| Name | Type | Detail |
|---|---|---|
| `divergence` | **`np.ndarray` structured (recarray-style)** | from `genfromtxt(..., names=True)`; actual fields are `"case"` (`str`), `"offset_um"` (`float64`), `"mark1300_frac"` (`float64`) |
| `case_order` | `list[str]` | de-duplicated case names, order preserved via `dict.fromkeys` |
| `colors` | `list` | 4 colour values (`rofl.b()`, `rofl.o()`, `rofl.g()`, `"tab:red"`) |
| `rows` | `ndarray` structured | boolean-masked subset per case |
| `ax` | `matplotlib.axes.Axes` | single axis, not an array |

> ⚠️ **This cell currently fails.** `genfromtxt(names=True)` takes its field names from the file's header line, which notebook 01 writes as `# case  offset_um  mark1300_frac`. The plot call asks for `rows["left_fraction"]`, so the cell raises `ValueError` (saved in the notebook as execution 17). Fix by using `rows["mark1300_frac"]`, or by renaming the header written in notebook 01 cell 8.

Output: `05_divergence_scan.png`.

---

## Cell 11 — Movie frames and GIF

| Name | Type | Detail |
|---|---|---|
| `gallery_offsets_um` | `ndarray (43,) float64` | Every generated Methods offset (`-10.0` through `10.16` in `0.48` µm steps) |
| `gif_frames` | `list[PIL.Image.Image]` | 43 RGB frames |
| `pci_half_width_um` | `float` | 16.384 µm |
| `q_half_width` | `float` | `abs(Q_AXIS).max()` |
| `frame_index` | `int` | |
| `offset_um` | `np.float64` | |
| `pci`, `saxs` | `ndarray (4096,4096) float32` | |
| `pci_max`, `saxs_max` | `float` | |
| `step` | `int` | `4` — downsample stride |
| `pci_display`, `saxs_display` | `ndarray (1024,1024) float32` | strided views |
| `frame_path`, `gif_path` | `Path` | |
| `frame` | `PIL.PngImageFile` | context-manager var |

Output: `PCI_after_sample_SAXS_detector_offset_scan.gif`.

---

## Cell 13 — Clean PCI field-overview figures

| Name | Type | Detail |
|---|---|---|
| `CLEAN_PCI_DIR` | `Path` | |
| `clean_pci_field_cases` | **`dict[str, dict]`** | keys `"7p11um"`, `"6um"`; each value has `"fwhm_um"` (`float`), `"fields"` (`Path`), `"detector"` (`Path`), `"figure"` (`Path`) |
| `case` | `dict` | loop var — note this loop uses `.values()`, so there is **no** `case_name` here |
| `fields` | `NpzFile` | keys `"incident_intensity"`, `"thickness_um"`, `"exit_intensity"`, `"extent_um"`, `"fwhm_um"` |
| `detector_intensity` | `ndarray (4096,4096) float32` | |
| `extent_um` | `ndarray (4,) float64` | |
| `thickness_um` | `ndarray (4096,4096)` | interpolated zero-offset projected thickness map loaded from the field bundle |
| `thickness_profile_um` | `ndarray (4096,)` | center-row wire thickness plotted against `SAMPLE_AXIS_UM` |
| `axes` | `ndarray (5,)` of `Axes` | incident map, thickness map, thickness line plot, exit map, detector map |
| `axis` | `Axes` | inner loop var |

The thickness curve uses the horizontal centre row of the saved target map:
`thickness_um[thickness_um.shape[0] // 2]`. Its x coordinate is
`SAMPLE_AXIS_UM`, so the plot directly shows distance across the wire in
micrometres versus projected wire thickness in micrometres. The title records
the symmetric 4 nm left and right boundary sigmas.

---

## Cell 15 — Three-panel clean PCI / SAXS summary figure

**Loaded tables** — all `ndarray float64`:

| Name | Shape | Source |
|---|---|---|
| `clean_pci`, `clean_pci_6` | `(50, 4)` | `pci_exit_left_right_vs_offset[_6um].dat` |
| `saxs_7`, `saxs_6` | `(43, 3)` | `DivSAXS_asymmetry_Mark1300_*.dat` |
| `q_shifted_7`, `q_shifted_6` | `(43, 3)` | shifted-q mask tables |

**Validation loop**: `label` (`str`), `shifted_data` (`ndarray`) — raises `ValueError` on a malformed table or if the 6 µm table duplicates the 7.11 µm one.

**Derived**

| Name | Type |
|---|---|
| `saxs_7_offsets_um`, `saxs_7_left`, `saxs_7_right` | `ndarray (43,) float64` |
| `saxs_7_scale`, `saxs_6_scale`, `erik_scale` | `np.float64` |
| `saxs_6_offsets_um`, `saxs_6_left`, `saxs_6_right` | `ndarray (43,) float64` |
| `motor_order` | `ndarray int64` (`argsort`) |
| `motor_x`, `motor_y` | `ndarray float64` |
| `motor_band_x` | `ndarray (500,) float64` |
| `motor_shift_plus`, `motor_shift_minus` | `ndarray (500,) float64` |
| `axes` | `ndarray (3,)` of `Axes` |
| `axis` | `Axes` (grid loop) |

Output: `clean_pci_saxs_mark1300_left_right_vs_offset.png`.

---

## Cell 17 — Realistic incident-profile figure

| Name | Type | Detail |
|---|---|---|
| `REALISTIC_DIR`, `REALISTIC_TABLE_DIR`, `REALISTIC_FIGURE_DIR` | `Path` | |
| `incident` | `ndarray (4096,4096) float32` | `del`-ed at cell end, then **reloaded in cell 15** |
| `image` | `AxesImage` | |
| `ax` | `Axes` | |

Output: `00_realistic_incident_profile.png`.

---

## Cell 18 — Realistic vs Gaussian profile comparison

| Name | Type | Detail |
|---|---|---|
| `GAUSSIAN_FWHM_UM` | `float` | 7.11 |
| `PROFILE_VIEW_HALF_WIDTH_UM` | `float` | 10.0 |
| `FWHM_PER_SIGMA` | `np.float64` | ≈2.3548 |
| `view_indices` | `ndarray int64` | `flatnonzero` result |
| `view` | **`slice`** | reused for both array axes |
| `view_axis_um` | `ndarray float64` | |
| `view_extent_um` | `list[float]` — 4 elements | |
| `incident` | `ndarray float32` | reloaded, then `del`-ed |
| `realistic_map`, `gaussian_map` | `ndarray (Nv, Nv) float32` | peak-normalised |
| `gaussian_1d` | `ndarray (Nv,) float32` | |
| `realistic_lineout`, `gaussian_lineout` | `ndarray (Nv,) float64` | y-projections |
| `fig` | `Figure` | built with `figure()` + `add_gridspec`, not `subplots` |
| `grid` | `matplotlib.gridspec.GridSpec` | 2×2, height ratios `[1.0, 0.85]` |
| `column` | `int` | |
| `profile_map` | `ndarray` | |
| `title` | `str` | |
| `axis`, `lineout_axis` | `Axes` | |

Output: `01_realistic_vs_gaussian_profile.png`.

---

## Cell 19 — Four-panel realistic-profile figure

| Name | Type | Detail |
|---|---|---|
| `realistic_pci` | `ndarray (43, 6) float64` | 6 columns incl. the two ratio columns |
| `realistic_saxs` | `ndarray (43, 4) float64` | |
| `realistic_bundle` | `NpzFile` | keys `"offsets_um"`, `"q_axis"`, `"lineouts"` |
| `realistic_offsets_um` | `ndarray (43,) float64` | |
| `realistic_lineouts` | `ndarray (43, 4096) float64` | |
| `realistic_q_axis` | `ndarray (4096,) float64` | |
| `realistic_experimental` | **`dict[int, dict]`** | run → the `load_realistic_experimental_profile` dict |
| `gaussian` | `ndarray (43,3) float64` | 7.11 µm reference table |
| `q_shifted_gaussian` | `ndarray (43,3) float64` | 7.11 µm two-/ten-row shifted-q fractions |
| `gaussian_offsets_um`, `gaussian_left`, `gaussian_right`, `gaussian_total` | `ndarray (43,) float64` | |
| `lingen` | `ndarray float64` | |
| `methods_zero_index` | `int` | index of the offset nearest 0 |
| `methods_profile_q` | `ndarray` | |
| `methods_profile` | `ndarray float64` | rescaled in place later |
| `real_pci_left`, `real_pci_right`, `real_pci_total` | `ndarray (43,) float64` | |
| `incident_total` | `np.float64` | recovered via `nanmedian(total / column 5)` |
| `real_saxs_left`, `real_saxs_right`, `real_saxs_total` | `ndarray (43,) float64` | |
| `shifted_q_axis`, `shifted_left_weights`, `shifted_right_weights` | `ndarray (4096,) float64` | fractional q masks centered at +0.005 nm⁻¹ |
| `realistic_shifted_left`, `realistic_shifted_right`, `realistic_shifted_fraction` | `ndarray (43,) float64` | realistic-profile reduction using the shifted q mask |
| `real_scale`, `gaussian_scale` | `np.float64` | |
| `profile_index` | `int` | |
| `realistic_interp` | `ndarray float64` | resampled onto `methods_profile_q` |
| `profile_mask` | `ndarray bool` | `Q_MIN ≤ |q| ≤ Q_COMPARE_MAX` |
| `run`, `profile` | `int`, `dict` | loop over `realistic_experimental` |
| `axes` | `ndarray (4,)` of `Axes` | |

The SAXS-ratio panel uses the +0.005 nm⁻¹ shifted mask for the realistic and
7.11 µm Gaussian curves and shows the effect of ±1 µm motor-position
uncertainty as a shaded envelope. Output: `02_realistic_pci_saxs_left_right.png`.

---

## Cell 21 — Experimental-comparison directories

`EXPERIMENTAL_DIR`, `EXPERIMENTAL_TABLE_DIR`, `EXPERIMENTAL_PCI_TIFF_DIR`, `EXPERIMENTAL_FIGURE_DIR` — all `Path`. No other bindings; the cell only creates the figure directory.

---

## Cell 22 — PCI-exit / SAXS side-by-side gallery

| Name | Type | Detail |
|---|---|---|
| `comparison_offsets_um` | `ndarray (21,) float64` | `arange(-10.0, 10.5, 1.0)` |
| `reference_pci` | `ndarray float32` | first frame, used only for `pci_vmax`, then `del`-ed |
| `pci_vmax` | `float` | shared colour scale across all 41 figures |
| `offset_um` | `np.float64` | |
| `tag` | `str` | from `offset_tag` |
| `pci_image`, `saxs_image` | `ndarray (4096,4096) float32` | |
| `im0`, `im1` | `AxesImage` | |
| `axes` | `ndarray (2,)` of `Axes` | |

Output: 41 × `01_exit_pci_and_saxs_offset_<tag>um.png`.

---

## Cell 23 — Transmission comparison figure

| Name | Type | Detail |
|---|---|---|
| `sim_transmission` | `ndarray (49, 2) float64` | `analytic_exit_transmission.dat` |
| `fig`, `ax` | `Figure`, `Axes` | |

Output: `04_exit_transmission.png`.

---

## Notebook 02 — cross-cell name reuse

| Name | Cells | Types |
|---|---|---|
| `fig` | 5, 6, 7, 9, 10, 11, 13, 15, 17, 18, 19, 22, 23 | `matplotlib.figure.Figure` |
| `axes` | 5, 6, 7, 9, 11, 13, 15, 19, 22 | `ndarray` of `Axes` (shape varies: 2, 3, 4, or 5) |
| `ax` | 10, 17, 23 | a single `Axes` — **not** an array |
| `axis` | 13, 15, 18 | `Axes` (inner loop) |
| `case_name`, `case` | 4, 5, 8 (`case_name` only), 11 (`case` only) | `str`, `dict` |
| `table` | 4, 5 | `ndarray (43,3)` |
| `offsets_um`, `left`, `right` | 5 | `ndarray float64` |
| `incident` | 14, 15 | `ndarray float32` — loaded, `del`-ed, reloaded |
| `image` | 4, 14 | `AxesImage` |
| `offset_um` | 4, 7, 9, 19 | `np.float64` |
| `run`, `q_values`, `experimental` | 4, 7 | `int`, `ndarray`, `ndarray` |
| `lineout` | 7 | `ndarray` |
| `intensity` | 4 | `ndarray float32` |
| `scale` | 5 | `np.float64` |
| `profile` | 16 | `dict` |
| `label` | 12 | `str` |

---

## Notebook 02 — types at a glance

- **`dict`** — `clean_cases`, `styles`, `clean_pci_field_cases`, `pointing_experimental`, `erik`, `realistic_experimental`, and the dicts returned by `load_realistic_experimental_profile` / `load_erik_reference` / `load_pointing_profiles`
- **`tuple`** — `EXPERIMENTAL_RUNS`; returns of `load_run_halves` (3-tuple) and `load_transmission_scan` (2-tuple); each `(q, lineout)` in `pointing_experimental`
- **`list`** — `SAMPLE_EXTENT_UM`, `Q_EXTENT`, `view_extent_um`, `case_order`, `colors`, `gif_frames`
- **`slice`** — `view` (cell 15) — the only slice object in either notebook
- **structured `ndarray`** — `divergence` (cell 8), fields `case` / `offset_um` / `left_fraction`
- **`NpzFile`** — `clean_profiles`, `methods_profiles`, `realistic_bundle`, `fields`
- **matplotlib objects** — `fig` (`Figure`), `axes` (`ndarray` of `Axes`), `ax` / `axis` / `lineout_axis` (`Axes`), `image` / `im0` / `im1` (`AxesImage`), `cmap` (`Colormap`), `grid` (`GridSpec`)
- **`pathlib.Path`** — every `*_DIR`, `*_PATH`, `*_path`, `*_ROOT`
- **`float` / `np.float64`** — `Q_MIN`, `Q_COMPARE_MAX`, `pci_vmax`, `pci_max`, `saxs_max`, every `*_scale`, `incident_total`
- **`int`** — `N_GRID`, `step`, `frame_index`, `index`, `column`, `minimum`, `methods_zero_index`, `profile_index`, `run`

---

## Where notebook 01 and 02 differ on the same names

| Name | In 01 | In 02 |
|---|---|---|
| case registry | `CLEAN_SAXS_CASES` — 6-key config dicts | `clean_cases` — 2-key (`"label"`, `"table"`) plotting dicts |
| clean-PCI registry | `CLEAN_PCI_CASES` — `"fields_path"`, `"detector_path"`, `"table_path"`, `"raw_table_path"` | `clean_pci_field_cases` — `"fields"`, `"detector"`, `"figure"` |
| imshow extent | `pci_extent_um` — `ndarray (4,)` | `SAMPLE_EXTENT_UM`, `Q_EXTENT`, `view_extent_um` — plain `list` |
| experimental pointing | `POINTING_EXPERIMENTAL` (uppercase constant) | `pointing_experimental` (lowercase) |
| divergence column | written with header `mark1300_frac` | read as field `left_fraction` → **mismatch, cell 8 raises `ValueError`** |
| `offset_tag` | defined in cell 2 | redefined identically in cell 2 |
| `load_pointing_profiles` | inlines the pickle read | delegates to `load_run_halves` |

---

# Part 3 — `quick_symmetric_sigma_check.py`

`SAXS_asymmetry/quick_symmetric_sigma_check.py` is a standalone sensitivity
runner. It compares symmetric boundary models

```text
sigma_left_nm = sigma_right_nm = 0, 3, 3.8, 4, 6, 8, or 14 nm
```

for the 7.11 µm divergent Gaussian case. The sweep uses
43 offsets from −10.0 through +10.16 µm at 0.48 µm spacing. It does not edit the
notebooks or write into a sigma-tagged production tree. All artifacts go to
`SAXS_asymmetry/outputs/quick_symmetric_sigma/`.

Run it from the repository root with:

```powershell
.\.venv\Scripts\python.exe SAXS_asymmetry\quick_symmetric_sigma_check.py
```

Optional CLI arguments are `--sigmas <values...>`,
`--q-mask-shift-nm-inv <value>`, `--output-dir <path>`, and `--no-plot`.

## Module constants and case registries

| Name | Type | Value or role |
|---|---|---|
| `SAXS_DIR` | `Path` | Directory containing the script and `PCI.py` |
| `GRID_SIZE` | `int` | 4096 |
| `PIXEL_SIZE_NM` | `float` | 8.0 nm |
| `WIRE_RADIUS_NM` | `float` | 5000 nm |
| `WIRE_VOXEL_SIZE_NM` | `float` | 8.0 nm |
| `WIRE_VOXEL_NUMBER` | `int` | 2000 |
| `PHOTON_ENERGY_KEV` | `float` | 8.2 keV |
| `WAVELENGTH_NM` | `float` | `PCI.HC_KEV_NM / PHOTON_ENERGY_KEV` |
| `Z_TARGET_NM` | `float` | 0.25 m in the internal nm unit |
| `Z_SAXS_DETECTOR_NM` | `float` | 1.31 m in the internal nm unit |
| `Q_STEP_NM_INV` | `float` | Exact FFT q-bin spacing, about 1.91748e-4 nm^-1 |
| `MARK1300_Q_MIN_NM_INV` | `float` | 0.10 nm^-1 |
| `Q_MASK_SHIFT_NM_INV` | `float` | Default shifted-mask centre, +0.005 nm^-1 |
| `OFFSET_MIN_UM` / `OFFSET_MAX_UM` | `float` | −10.0 / +10.16 µm |
| `OFFSET_STEP_UM` | `float` | 0.48 µm for the quick-check sweep |
| `DEFAULT_OUTPUT_DIR` | `Path` | `outputs/quick_symmetric_sigma` |
| `ERIK_DIR` | `Path` | Directory containing the motor positions and measured left fractions |
| `MARK1300_BEAM_CASES` | `dict[str, float]` | Divergent SAXS case: 7.11 µm |

## Functions

| Function | Return | Purpose |
|---|---|---|
| `voxelized_chord_profile()` | `ndarray (2000,)` | Construct the 8 nm sampled 10 µm Cu-wire chord |
| `symmetric_blur(profile, sigma_nm)` | `ndarray` | Apply one Gaussian sigma to both boundaries; sigma 0 returns an unblurred copy |
| `asymmetric_blur(profile, sigma_left_nm, sigma_right_nm)` | `ndarray` | Join independently blurred negative- and positive-x halves; also supports the 4/8 validation case |
| `load_erik_motor_reference()` | `dict[str, ndarray]` | Load and validate `motor_offsets_um` and `motor_left_fraction` |
| `source_waist_for_target_fwhm(fwhm_um)` | `float` | Solve for the divergent/small Gaussian root |
| `gaussian_target_line_field(fwhm_um)` | `ndarray (4096,) complex128` | Generate the exact central target-plane Gaussian field in one dimension |
| `mark1300_left_fraction_scan(fwhm_um, offsets_um, sigma_left_nm, sigma_right_nm, q_mask_shift_nm_inv)` | `ndarray` | Calculate the divergent Mark1300 fraction using the separable 1-D Fresnel FFT |
| `validate_mark1300_reduction()` | `None` | Compare the 1-D result with saved full 2-D 4/8 nm tables; fail above `3e-7` absolute error |
| `save_scan_table(...)` | `None` | Save every offset and sigma curve as a whitespace table |
| `save_selected_offset_summary(...)` | `None` | Save fractions nearest requested −2, 0, and +2 µm, including both requested and sampled offsets |
| `save_sigma_effect_summary(...)` | `None` | Save the maximum absolute change from the 8 nm reference curve |
| `save_comparison_plot(...)` | `list[Path]` | Save the separate 7.11 µm absolute-fraction plot with the Erik motor overlay and two standalone 8 × 6 inch wire-edge thickness figures, using `_wire_left_edge` and `_wire_right_edge` filename suffixes and consistent rainbow sigma colors |
| `parse_args()` | `argparse.Namespace` | Parse CLI overrides |
| `main()` | `int` | Run the Mark1300 sweep, validation, tables, and figure |

## Calculation paths

The Mark1300 path constructs the complex divergent Gaussian line field,
applies Cu amplitude attenuation and phase delay, adds the Fresnel quadratic
phase, and performs a 4096-point FFT for each offset. The straight wire and
Gaussian source are separable in x and y, so the omitted y factor is common to
both side sums and cancels in `L/(L+R)`.

## Generated artifacts

| Artifact | Contents |
|---|---|
| `mark1300_left_fraction_7p11um.dat` | Full divergent 7.11 µm Mark1300 sweep |
| `mark1300_selected_offsets.csv` | 7.11 µm Mark1300 fractions nearest requested −2, 0, and +2 µm; sampled positions are −1.84, +0.08, and +2.00 µm |
| `mark1300_sigma_effect_summary.csv` | Maximum 7.11 µm Mark1300 change relative to sigma 8 nm |
| `mark1300_symmetric_sigma.png` | One 7.11 µm Mark1300 absolute-fraction panel with Erik motor points; lower left-edge (−5.04 to −4.99 µm) and right-edge (4.99 to 5.04 µm) thickness zooms with matching rainbow colors and legend labels for all seven sigmas |

Earlier `mark1300_left_fraction_6p0um.dat` and
`mark1300_left_fraction_7p0um.dat` files may remain in the output directory;
the current sweep regenerates the 7.11 µm table, summaries, and figure.

The current validation errors against the saved full 2-D asymmetric 4/8 nm
shifted-mask results are `2.02e-7` for 6.0 µm and `1.98e-7` for 7.11 µm.
