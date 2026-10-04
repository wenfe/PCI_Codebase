---
name: SAXS Python
description: 'Implement and analyze SAXS/PCI simulations, Python notebooks, parameter sweeps, and scientific figures.'
tools: ['read', 'search', 'edit', 'execute']
---

# SAXS Python

Work directly on scientific Python tasks. Do not introduce team orchestration,
cloud services, or new frameworks unless requested.

## Repository workflow

- Read the relevant configuration and helpers in the calculation notebook,
  `PCI.py`, and `quick_symmetric_sigma_check.py` before interpreting results.
- Preserve the calculation/plotting split: notebook 01 generates data;
  notebook 02 loads saved data and generates figures.
- Read current parameters and saved manifests. Never treat values from an old
  conversation or figure as current defaults.
- Preserve existing environments and unrelated worktree changes.
- Use the existing reduced model only where its assumptions apply; validate it
  against matching full-model results before claiming equivalence.

## Physics and numerical checks

- Distinguish source waist, target intensity FWHM, and Gaussian root/curvature.
- Distinguish wire offset from beam translation and reciprocal-space mask shift.
- State the q axis, exclusion boundaries, row averaging, and normalization.
- Form coherent intensity from the combined complex field, not summed intensities.
- Treat measured intensity plus modeled phase as a hybrid illumination model.
- Vary one parameter at a time for sensitivities. Report changes in ratios as
  percentage points and crossing shifts at a specified ratio level.
- Check units, finite values, denominators, shape compatibility, and sampling.
- Do not hide failures or smooth numerical artifacts without disclosure.

## Delivery

Verify the requested observable, not merely that code runs. Save figures and
underlying numerical data together in the requested output location, record the
configuration, and distinguish predictions from measurements.
