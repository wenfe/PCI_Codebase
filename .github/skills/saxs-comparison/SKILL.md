---
name: saxs-comparison
description: 'Compare SAXS left ratios, notebook curves, edge sigmas, beam widths, q shifts, and realistic illumination.'
---

# SAXS Comparison

Use this skill for parameter sensitivities or apparently inconsistent SAXS curves.

## Match configurations before comparing

Read both calculation paths and record edge sigmas, target FWHM, Gaussian root,
phase curvature, photon energy, propagation distances, grid spacing, offset sign,
q coordinates, mask boundaries, row averaging, and normalization.

Trace notebook 01 calculations and notebook 02 artifact loading separately.
An unchanged filename does not establish that outputs came from current settings.

## Numerical comparison

1. Reproduce the reference with the exact original reduction.
2. Validate any reduced calculation against saved full-model values at matching
   offsets and settings. Report measured maximum error and the acceptance limit.
3. Change one parameter at a time; keep the denominator convention consistent.
4. Report ratios at identical offsets, differences in percentage points, and
   crossing positions at an explicitly chosen ratio level.
5. Save numerical comparisons with their settings, not just images.

## Gotchas

- **Mask shift is not a physical change to illumination.** It changes which q
  intensities contribute to the side sums.
- **Smaller edge sigma does not guarantee a rigid horizontal shift.** Check
  curve deformation and non-monotonic behavior over the requested range.
- **FWHM alone does not specify the wavefield.** Match the Gaussian branch and
  wavefront curvature.
- **Realistic amplitude does not establish realistic phase.** Disclose the
  assumed phase model.
- **Interpolation is not a new simulation.** Identify interpolated values and
  never compare nearby sampled offsets as if they were identical.
