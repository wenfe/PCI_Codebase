---
name: saxs-plotting
description: 'Create reproducible SAXS/PCI plots and multi-panel sensitivity figures from saved simulation data.'
---

# SAXS Plotting

Keep plotting separate from simulation unless a requested observable is missing.
Reuse notebook 02 loading and figure-saving patterns where applicable.

## Comparison figures

- Use one documented reference across panels and vary one factor per panel.
- Use matching axes, explicit units, readable legends, and a distinctive
  reference style. Include actual edge sigmas and q-mask convention.
- Distinguish raw simulated samples, interpolation, fitted curves, and measured
  points. Disclose smoothing and sparse sampling.
- Label Gaussian root/curvature and assumed phase for realistic illumination.
- Preserve left/right ratios with shared normalization; do not independently
  normalize the detector halves when comparing their balance.

## Output verification

Save a raster preview, vector output when requested, and the plotted numerical
data with parameter metadata. Use the user's output directory and do not
overwrite unrelated figures without approval.

Inspect the rendered figure for clipped labels, hidden curves, misleading axis
limits, and unreadable legends. Verify finite data and nonempty output files.
Explain unresolved numerical ripples rather than silently removing them.
