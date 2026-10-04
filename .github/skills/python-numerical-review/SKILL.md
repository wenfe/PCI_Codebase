---
name: python-numerical-review
description: 'Review scientific Python arrays, numerical reductions, parameter sweeps, and notebook reproducibility.'
---

# Python Numerical Review

Review the requested numerical path without expanding into unrelated frameworks.

- Verify array shapes, broadcasting, units, axis ordering, dtype, and coordinate
  spacing before accepting a computation.
- Check finite values, denominators, boundary handling, interpolation, and FFT
  centering/normalization against repository conventions.
- Check that every sweep case owns independent accumulators and output paths.
- Distinguish current source configuration, kernel state, and saved output
  provenance. Test important notebook paths from a reproducible state.
- Check whether ratios preserve a shared left/right normalization.
- Validate reduced or optimized implementations against the reference observable
  at matching settings; report actual error and tolerances.
- Use the smallest existing check covering the change. Escalate only when
  targeted evidence indicates a wider problem.
- Do not install packages globally, invent successful fallback results, or change
  scientific assumptions solely to make a check pass.

Report confirmed issues with source locations, numerical consequences, and
reproduction steps. State uncertainty when execution or reference data is missing.
