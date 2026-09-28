# Revised SAXS manuscript section

Use `saxs_section_updated.tex` to replace the two supplied subsections. The `.txt` file contains identical LaTeX for convenient copying. The manuscript preamble needs `amsmath` and `graphicx`.

Keep these accompanying graphics on the manuscript graphics path:

- `01_experimental_setup.png`: the supplied updated schematic, including its bottom row of experimental SAXS patterns.
- `02_asymmetric_sigma_wire_edges.png`: the supplied edge-profile comparison, copied under a name that reflects its asymmetric cases.
- `03_saxs_workflow.pdf`: the workflow with the right-edge width corrected from 2 nm to 0 nm and the translated thickness written with separate left/right widths.

The section now uses sigma_L = 4.67 nm and sigma_R = 0 nm, defines the independently smoothed wire halves, lists the six actual width pairs in the edge figure, and uses fixed side-integration regions q_x < -0.10 nm^-1 and q_x > +0.10 nm^-1. All q-window-shift parameters and discussion have been removed from the manuscript section.

The bottom-row images in the setup figure are described as experimental measurements at approximately -4.95, 0, and +4.95 micrometres, following the figure metadata. The illustrated geometric offsets are -5, 0, and +5 micrometres. These differ from the discrete simulated scan positions.

The workflow caption now distinguishes the retained Fresnel propagation phase from the additional Fraunhofer approximation shown for comparison. Existing citation keys and equation labels are preserved. The old `fig:symmetric_sigma` figure label remains as an alias for compatibility with references elsewhere in the manuscript; the revised text uses `fig:wire_edge_smoothing`.

Validation: the section compiled with pdfLaTeX without warnings after resolving cross-references; its rendered equations, captions, and corrected workflow were visually checked. The original bibliography was not supplied, so citation keys should be resolved by the full manuscript bibliography. No simulation data were recalculated.
