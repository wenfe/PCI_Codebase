---
icon: lucide/waves
---

# PCI Codebase documentation

This site documents the wave-propagation models, numerical methods, and
analysis workflows used to study small-angle X-ray scattering (SAXS) and
propagation-based phase-contrast imaging (PCI).

## Repository and execution layout

The active study separates implementation, measured inputs, notebooks, and
generated results:

| Location | Responsibility |
|---|---|
| `src/SAXS_asymmetry/` | Propagation engine, shared path resolver, and standalone tools. |
| `data/experimental/`, `data/profiles/`, `data/reference/` | Measurement inputs, illumination profiles, and reference curves. |
| `notebooks/saxs_asymmetry/01_calculate_and_save_data.ipynb` | Calculate fields and reductions; save tables, TIFFs, and plot-data bundles. |
| `notebooks/saxs_asymmetry/02_plot_and_save_figures.ipynb` | Load saved results and create figures without repeating propagation. |
| `outputs/saxs_asymmetry/` | Generated study artifacts, normally excluded from version control. |
| `docs/` | Equations, workflow contracts, interpretation, and site sources. |
| `tests/` | Repository-layout and path-override checks. |

`SAXS_asymmetry.paths` defines these locations. `PCI_DATA_DIR` overrides the
input root; `PCI_OUTPUT_DIR` replaces the complete study-output root, not the
repository-level `outputs/` directory.

### Run the study

1. Install the locked project environment from the repository root with
   `uv sync --locked`.
2. Open notebook 01 from inside the repository and run its shared setup.
   Select the left/right wire sigmas before calculating dependent sections.
3. Run the required calculation sections in dependency order, then the
   completion cell to write the calculation manifest.
4. Run notebook 02's setup with the same sigma pair, followed by the matching
   plotting sections.

The current notebook selection is left sigma 4.67 nm and right sigma 0 nm.
Its main results live under
`outputs/saxs_asymmetry/sigmaL_4p67nm_sigmaR_0nm/`.
Other pairs use their own sigma-tagged directories. The standalone quick-sigma
tool and realistic smoothing-pair sweep instead use the shared
`quick_symmetric_sigma/` and `realistic_sigma_pair_scan/` directories.

!!! note "Generated artifacts and historical results"

    A fresh checkout need not contain simulation outputs. Generate them before
    running the associated plotting cells. Historical symmetric-sigma results
    are not the current asymmetric selection. The
    [workflow lessons](pci_saxs_workflows_lessons.md) also identify plotting
    inputs whose calculation producer is absent from the current notebook.

## Start here

- [SAXS and PCI](SAXS-PCI.md) presents the shared wave-optics model.
- [Propagation methods](propagators.md) derives the Rayleigh-Sommerfeld,
  angular-spectrum, and Fresnel formulations.
- [PCI intensity workflow](pci_intensity_workflow.md) traces the PCI
  calculation and its physical interpretation.
- [SAXS intensity workflow](saxs_intensity_workflow.md) explains the SAXS
  calculation and the Fresnel-to-Fraunhofer relationship.
- [Workflow lessons](pci_saxs_workflows_lessons.md) collects validation,
  comparison, and reproducibility guidance.

## Project guides

- [GitLab synchronization](gitlab_sync.md) explains the one-way mirror from
  GitHub `main` to GitLab `main`.
- [Documentation guide](markdown.md) describes how to preview, build, and
  extend this Zensical site.

## Build the site locally

Install the locked development dependencies, then start the preview server:

```powershell
uv sync --locked --only-group dev
uv run zensical serve
```

Create the same clean static build that GitHub Pages deploys:

```powershell
uv run zensical build --clean
```

The generated site is written to `site/`.
