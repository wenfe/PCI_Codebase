HRXP - calculates PCI and SAXS images for an XFEL beamline.
This file is part of HRXP, the Hibef ReLaX XFEL Propagator.

HRXP is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

GitHub `main` syncs to GitLab through the [Sync main to GitLab workflow](.github/workflows/sync-gitlab.yml). See [setup and troubleshooting](docs/gitlab_sync.md).

The related [bremsstrahlung denoising code](https://github.com/Helmholtz-AI-Matter/bremsstrahlung_denoising) is included as a Git submodule. After cloning this repository, initialize it with:

```sh
git submodule update --init --recursive
```

## Quick SAXS left/right sigma comparison

Use [the quick sigma script](SAXS_asymmetry/quick_symmetric_sigma_check.py)
to manually compare Gaussian 7.11 um SAXS with measured left/right intensities.
From the repository root, provide one or more ordered sigma pairs in nm:

```sh
python SAXS_asymmetry/quick_symmetric_sigma_check.py --sigma-pair 4 8 --sigma-pair 8 4
```

The inexpensive 1-D reduction preserves the full simulation's normalized
left/right signals for a straight wire and a separable Gaussian beam. This
command creates a two-panel comparison:

- **Shifted SAXS intensities:** left is solid and right is dashed, with a color
  per sigma pair. Each simulated pair shares the denominator `max(left + right)`
  over the offset scan. Experimental halves likewise share
  `max(left_exp + right_exp)`; they are not independently peak-normalized.
- **Shifted left fraction:** the default q-mask shift is `+0.005 nm^-1`, adjustable
  with `--q-mask-shift-nm-inv`. Both panels use this same shifted, fractional-bin
  mask, so the simulated fraction equals `left / (left + right)` from panel a).
  The measured fraction uses the separately saved motor fraction, not a fraction
  recalculated from the measured halves; these experimental references can differ.

Experimental inputs must exist under
[the Erik input directory](SAXS_asymmetry/inputs/experimental/Erik):
`left_exp.npy`, `right_exp.npy`, `motor_positions_um.npy`, and (for plots)
`left_div_left_right_exp.npy`. The motor positions are already converted to
target offsets in um and are used directly in saved order. This is a visual
comparison tool, not an automatic fit; it applies no fitted scale or position
shift.

Outputs default to `SAXS_asymmetry/outputs/quick_symmetric_sigma`:

- `sigmaL4_sigmaR8_pairs_7p11um.png`: intensity and fraction comparisons for
  `--sigma-pair 4 8`. Multiple pairs are included in order, for example
  `sigmaL4_sigmaR8_sigmaL8_sigmaR4_pairs_7p11um.png`. Decimal values use `p`
  instead of a decimal point, consistent with the table filenames.
- `mark1300_saxs_7p11um_sigmaL_*nm_sigmaR_*nm.dat`: per-pair offset, shifted
  normalized left, right, total, and shifted left fraction columns.
- `experimental_saxs_left_right_normalized.dat`: measured offsets and normalized
  halves.

Use `--output-dir PATH` to retain separate trials, or `--no-plot` to write only
tables. The original symmetric sweep and its fraction/wire-edge figures remain
available using `--sigmas 0 3 4 6 8 14` (also the no-argument default).
`--sigmas` and `--sigma-pair` are mutually exclusive. Use `--sigma-pair 4 4`
for a symmetric case in the new intensity comparison.

Run the [focused regression tests](SAXS_asymmetry/test_quick_symmetric_sigma_check.py):

```sh
python -m unittest SAXS_asymmetry.test_quick_symmetric_sigma_check
```

The tests check shifted-mask integrals and consistency between both panels and
exported tables. The full 2-D comparison test additionally checks the retained
unshifted signals against local saved `(4, 4)` and `(4, 8)` simulation tables when
available; it reports a skip if they have not been generated.

## Position-matched detector images

The [calculation notebook](SAXS_asymmetry/01_calculate_and_save_data.ipynb)
includes a "Position-matched experimental and realistic-beam detector images"
section. Run its shared setup cell and then this section; the full offset scans
are not required. Configure the experimental input directory, motor-zero
reference, and requested offsets in that cell. Filename suffixes are motor
positions in mm; target offsets in um are calculated as
`(motor_position - motor_zero) / sqrt(2) * 1000`.

The calculation selects nearby experimental frames and simulates their actual
offsets using the measured beam intensity and the existing divergent-beam phase
model. It uses a separate finer grid to cover the experimental q range without
changing the existing scans. Wire construction uses the same shared factory,
including voxel dimensions, edge smoothing, and offset handling, without
overrides. The exit field is propagated to the SAXS detector with the same
target and Fresnel propagation methods as the earlier realistic scan; no
separate PCI image or analytic transmission is calculated. Each run
recalculates only the selected positions and saves a
compressed bundle of raw images, source filenames, positions, q coordinates,
and simulation settings under the selected sigma output directory.

In the [plotting notebook](SAXS_asymmetry/02_plot_and_save_figures.ipynb), run the
global setup and the matching section to save a comparison figure and individual
simulated detector PNGs. Experimental and simulated panels have identical q-axis
limits using [explicit image extents](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.imshow.html),
but separate logarithmic intensity scales shared across positions.
There is no absolute intensity calibration or simulated experimental beamstop.
Nonpositive or invalid measured pixels are masked for logarithmic display; the
saved experimental arrays remain unchanged.

The Gaussian detector comparison gallery likewise reuses the Clean SAXS TIFFs
and produces SAXS-only figures. Missing TIFFs are generated with the existing
Gaussian SAXS helper. The former analytic-chord PCI and transmission outputs
are no longer generated or required; previously saved files are left untouched.
The dedicated PCI sections elsewhere in the notebooks are unchanged.
