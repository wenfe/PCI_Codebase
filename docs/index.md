---
icon: lucide/waves
---

# PCI Codebase documentation

This site documents the wave-propagation models, numerical methods, and
analysis workflows used to study small-angle X-ray scattering (SAXS) and
propagation-based phase-contrast imaging (PCI).

!!! note "Repository snapshot"

    Some pages describe simulation sources and generated figures that are not
    present in the current checkout. Those pages retain the scientific context
    and mark unavailable artifacts explicitly.

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
