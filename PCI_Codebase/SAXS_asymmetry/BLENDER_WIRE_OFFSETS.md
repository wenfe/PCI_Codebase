# Gaussian wire offsets in Blender

Both `wire_offset_scene.py` and `plot_gaussian_wire_offsets.py` now use native
Blender objects, materials, cameras and Cycles rendering. There is no Matplotlib
dependency. The `.py` files are Blender automation scripts, executed by Blender's
bundled runtime; a separate Python installation is not used.

From the repository root, run in PowerShell:

```powershell
.\SAXS_asymmetry\run_gaussian_wire_offsets_blender.ps1
.\SAXS_asymmetry\run_gaussian_wire_offsets_blender.ps1 -Offsets -5,0,5 -Fwhm 6 -OutputStem gaussian_wire_offsets_6um
```

The launcher locates Blender on PATH or the workspace portable Blender 4.5.13.
For another installation, pass `-BlenderPath 'C:/path/to/blender.exe'`.
The portable runtime was downloaded from the official Blender release server
and verified against its published SHA256 checksum. It lives under `tmp/`.

On any platform with Blender 4.5 LTS, the equivalent command is:

```text
blender --background --factory-startup --python-exit-code 1 --python SAXS_asymmetry/plot_gaussian_wire_offsets.py -- --offsets -5 0 5 --samples 48 --resolution 3200
```

The default output folder is
`SAXS_asymmetry/outputs/sigmaL_4nm_sigmaR_4nm/schematics/blender/` (the sigma folder
follows the notebook settings). It contains the complete 3200 × 2400 PNG figure,
three separate interaction PNGs, an experimental geometry PNG, a `.blend` file,
numeric `.npz` data and a metadata JSON. Use `-OutputDir` to change the folder.
These Blender outputs use a separate basename and folder from older PDF/SVG
exports; no new PDF or SVG is generated.

Open the `.blend` in Blender. The scene selector at the top right contains:

- **00**: complete figure with editable labels and profile curves, plus the 3D renders.
- **01–03**: the actual copper cylinders, Gaussian volume shaders and golden contour surfaces, dimensions,
  lights and orthographic cameras for each wire offset.
- **04**: the two green SAXS HAPG plates and both Jungfrau/XPCI image panels
  from Huang et al., Fig. 2, with a gold 3D primary beam and exactly one red 3D
  reflected SAXS branch. The plates and beams are native, editable Blender objects.

Images and fonts are packed into the `.blend`. The complete figure uses snapshots
of scenes 01–04; re-run the script after changing configuration to refresh all
panels consistently. Press Numpad 0 for camera view; render an individual scene
with F12. All three interaction cameras use the same scale for direct comparison.

Numeric geometry is parsed from notebook 01 without executing any notebook cells.
Blender X represents beam z, Blender Y represents transverse x, and Blender Z
represents wire y; one scene unit is one micrometre in interaction scenes. The
offset is wire centre minus beam axis. The Gaussian density uses
`exp(-4 ln(2) r² / FWHM²)`, with a display extinction chosen for legibility.
It illustrates incident illumination, not calculated absorption or propagation.
The beam appearance follows the yellow/orange illustration in Huber et al.,
*Nature Communications* 13, 3220 (2022), Fig. 1,
doi:10.1038/s41467-022-30703-y. It combines a translucent gold envelope at the
1/e² intensity radius with a bright yellow half-maximum core and fine amber
cross-section rims. These are intensity contours within the Gaussian halo,
not hard beam edges. The notebook FWHM, wire geometry, offsets, and numeric
profile data are independent of these display materials.
The red reflected beam uses the same translucent envelope style. Following
Huang et al., Fig. 2, the two HAPG mirrors are represented by one outgoing SAXS
branch starting on the upper mirror surface and directed toward the Jungfrau panel. This is an illustration of the
collected signal, not two independent ray traces or a calculated angular
distribution. The horizontal gold XFEL passes through the gap toward XPCI.

The HAPGs use the paper's simple green plate design and parallel tilt. Both
`inputs/reference/fig2_schematics/saxs_fig2.png` and `pci_fig2.png` are packed into
the `.blend` and displayed as the Jungfrau and XPCI reference panels from Fig. 2.
They are published reference images, not new offset simulations or physical
detector hit planes. XPCI includes the Optique Peter label and identifies the
7.5× objective / Andor Zyla arrangement in the paper's caption. The detailed
commercial camera housing has been replaced by this paper-style image panel.
