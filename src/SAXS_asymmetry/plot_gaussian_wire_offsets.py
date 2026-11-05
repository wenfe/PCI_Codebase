"""Build and render the Gaussian-wire figure with Blender Cycles.

Run with Blender, whose bundled scripting API builds the native 3D scenes:
  blender --background --factory-startup --python-exit-code 1 --python src/SAXS_asymmetry/plot_gaussian_wire_offsets.py -- --offsets -5 0 5

The notebook is parsed for numeric configuration only; no cells are executed.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import operator
import sys
from pathlib import Path

try:
    import bpy
except ImportError:
    raise SystemExit("Run this script inside Blender, not standalone Python. Use run_gaussian_wire_offsets_blender.ps1 or blender --background --python plot_gaussian_wire_offsets.py")

import numpy as np

SAXS_DIR = Path(__file__).resolve().parent
if __package__:
    from .paths import NOTEBOOKS_DIR, OUTPUTS_DIR
else:
    if str(SAXS_DIR) not in sys.path:
        sys.path.insert(0, str(SAXS_DIR))
    from paths import NOTEBOOKS_DIR, OUTPUTS_DIR  # noqa: E402

NOTEBOOK = NOTEBOOKS_DIR / "01_calculate_and_save_data.ipynb"
FIGURE_WIDTH, FIGURE_HEIGHT = 160, 95
EXPERIMENTAL_OFFSET_FILES = {
    -5: "p3129_r0484_22.855.tiff",
    0: "p3129_r0484_22.862.tiff",
    5: "p3129_r0484_22.869.tiff",
}
if __package__:
    from .wire_offset_scene import (
        INK, MUTED, BLUE, COPPER, RULE, BEAM, BEAM_STYLE, APPARATUS_STYLE, camera, draw_interaction_3d, draw_setup_3d,
        image_plane, line, material, new_scene, render, text,
    )
else:
    from wire_offset_scene import (
        INK, MUTED, BLUE, COPPER, RULE, BEAM, BEAM_STYLE, APPARATUS_STYLE, camera, draw_interaction_3d, draw_setup_3d,
        image_plane, line, material, new_scene, render, text,
    )

def read_notebook_geometry(path=NOTEBOOK):
    """Read restricted numeric expressions without executing notebook code."""
    notebook = json.loads(Path(path).read_text(encoding="utf-8"))
    cells = [ast.parse("".join(c["source"])) for c in notebook["cells"]
             if c["cell_type"] == "code"]
    units = {"nm": 1.0, "um": 1e3, "m": 1e9, "keV": 1.0}
    binary = {ast.Mult: operator.mul, ast.Div: operator.truediv,
              ast.Add: operator.add, ast.Sub: operator.sub}

    def number(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return float(node.value)
        if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "PCI" and node.attr in units):
            return units[node.attr]
        if isinstance(node, ast.BinOp) and type(node.op) in binary:
            return binary[type(node.op)](number(node.left), number(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -number(node.operand)
        raise ValueError(f"Unsupported numeric notebook setting: {ast.dump(node)}")

    required = {"WIRE_RADIUS", "PHOTON_ENERGY", "Z_TARGET", "Z_SAXS_DETECTOR",
                "Z_PCI_DETECTOR", "WIRE_SIGMA_LEFT_NM", "WIRE_SIGMA_RIGHT_NM"}
    values = {}
    for tree in cells:
        for statement in tree.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name) and target.id in required:
                        values[target.id] = number(statement.value)
    if required - values.keys():
        raise ValueError(f"Missing notebook settings: {required - values.keys()}")
    # Select the first divergent clean Gaussian case, as configured in notebook 01.
    for tree in cells:
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "make_clean_saxs_case" and node.args
                    and any(k.arg == "divergent" and isinstance(k.value, ast.Constant)
                            and k.value.value is True for k in node.keywords)):
                values["FWHM_UM"] = number(node.args[0])
                return values
    raise ValueError("No divergent make_clean_saxs_case(...) found in notebook 01")


def make_plot_data(config, offsets, fwhm):
    radius = config["WIRE_RADIUS"] / 1e3
    half_width = max(14.0, max(abs(x) for x in offsets) + radius + 3, 2 * fwhm)
    transverse = np.linspace(-half_width, half_width, 2401)
    intensity = np.exp(-4 * np.log(2) * (transverse / fwhm) ** 2)
    offsets = np.asarray(offsets, dtype=float)
    local = transverse[None, :] - offsets[:, None]
    chord = 2 * np.sqrt(np.clip(radius**2 - local**2, 0, None))
    # For a circular Gaussian and a wire long compared with the illuminated spot,
    # the 2-D geometrical intercepted fraction reduces to this 1-D integral.
    scale = 2 * np.sqrt(np.log(2)) / fwhm
    fraction = np.array([
        0.5 * (math.erf(scale * (d + radius)) - math.erf(scale * (d - radius)))
        for d in offsets
    ])
    return dict(transverse_um=transverse, incident_intensity_over_peak=intensity,
                offsets_um=offsets, wire_chord_um=chord,
                geometric_intercepted_fraction=fraction,
                wire_radius_um=np.asarray(radius), fwhm_um=np.asarray(fwhm))


def filled_polygon(name, points, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], [list(range(len(points)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def draw_profile(data, index, left, bottom, width, height, palette):
    """Editable curves, fills and type in the Blender presentation scene."""
    half = float(data["transverse_um"][-1])
    fwhm, radius = float(data["fwhm_um"]), float(data["wire_radius_um"])
    offset = float(data["offsets_um"][index])
    px = lambda x: left + width*(x+half)/(2*half)
    py = lambda y: bottom + height*y
    intensity = lambda x: math.exp(-4*math.log(2)*(x/fwhm)**2)
    filled_polygon("Cu wire silhouette", [(px(x), py(y), 0.1)
                   for x, y in [(offset-radius, 0), (offset+radius, 0),
                                (offset+radius, 1.07), (offset-radius, 1.07)]], palette["pale_copper"])
    xs = np.linspace(-half, half, 801)
    # Two fills distinguish the Gaussian overlap with the geometric silhouette.
    for start, stop, key in [(-half, offset-radius, "pale_blue"),
                             (offset-radius, offset+radius, "overlap"),
                             (offset+radius, half, "pale_blue")]:
        segment = np.linspace(start, stop, 241)
        points = [(px(start), bottom, 0.2)] + [(px(x), py(intensity(x)), 0.2) for x in segment]
        points.append((px(stop), bottom, 0.2))
        filled_polygon("Incident Gaussian fill", points, palette[key])
    line("Incident Gaussian intensity", [(px(x), py(intensity(x)), 0.4) for x in xs], palette["blue"], 0.085)
    for boundary in [offset-radius, offset+radius]:
        for y in np.arange(0, 1.04, 0.065):
            line("Wire edge guide", [(px(boundary), py(y), 0.5), (px(boundary), py(y+0.03), 0.5)],
                 palette["copper"], 0.028)
    line("x axis", [(left, bottom, 0.6), (left+width, bottom, 0.6)], palette["rule"], 0.035)
    line("Intensity axis", [(left, bottom, 0.6), (left, py(1.08), 0.6)], palette["rule"], 0.035)
    step = 5 if half <= 20 else 10**math.floor(math.log10(half))
    ticks = np.arange(math.ceil(-half/step)*step, half, step)
    for x in ticks:
        line("x tick", [(px(x), bottom, 0.7), (px(x), bottom-0.3, 0.7)], palette["muted"], 0.025)
        text(f"{x:g}", (px(x), bottom-1.35, 0.8), 0.95, palette["muted"], align="CENTER")
    if index == 0:
        for y in [0, 0.5, 1]:
            text(f"{y:.1f}", (left-0.8, py(y)-0.32, 0.8), 0.95, palette["muted"], align="RIGHT")
        label = text("Normalized intensity [a.u.]", (left-4, py(0.54), 0.8),
                     1.05, palette["ink"], align="CENTER")
        label.rotation_euler.z = math.pi/2
    line("FWHM dimension", [(px(-fwhm/2), py(0.5), 0.7), (px(fwhm/2), py(0.5), 0.7)], palette["blue"], 0.04)
    for x in [-fwhm/2, fwhm/2]:
        line("FWHM tick", [(px(x), py(0.47), 0.7), (px(x), py(0.53), 0.7)], palette["blue"], 0.04)
    text(f"FWHM {fwhm:g} µm", (px(0), py(0.62), 0.8), 0.95, palette["blue"], align="CENTER")
    text("Transverse position, x [(µm)]", (left+width/2, bottom-3, 0.8), 1.05, palette["muted"], align="CENTER")


def rosa_figure_paths(directory):
    """Resolve the titleless, equal-q-scale experimental ROSA panel exports."""
    paths = [Path(directory).resolve() / Path(EXPERIMENTAL_OFFSET_FILES[offset]).with_suffix(".png")
             for offset in [-5, 0, 5]]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"ROSA figure not found: {path}")
    return paths


def draw_figure(config, data, interaction_paths, setup_path, resolution, rosa_paths=None):
    """Manuscript layout: setup (a), followed by offset examples (b)--(d)."""
    scene = new_scene("00 | Gaussian wire offsets - complete figure", resolution,
                      round(resolution*FIGURE_HEIGHT/FIGURE_WIDTH), 16)
    scene.cycles.use_denoising = False
    camera(scene, (80, FIGURE_HEIGHT/2, 200), (80, FIGURE_HEIGHT/2, 0), FIGURE_WIDTH)
    palette = {name: material("Figure " + name, color, flat=True) for name, color in {
        "ink": INK, "muted": MUTED, "blue": BLUE, "beam": BEAM, "copper": COPPER, "rule": RULE,
        "pale_blue": "#e8f0f8", "pale_copper": "#f5e9df", "overlap": "#dedddc",
    }.items()}
    image_plane("Blender-rendered experimental geometry", setup_path, (80, 75, 0), 144, 144*0.27)
    text("(a)", (9, 91, 1), 1.8, palette["ink"], bold=True)
    line("Section rule", [(9, 55, 1), (151, 55, 1)], palette["rule"], 0.035)
    for index, (offset, path, left) in enumerate(zip(data["offsets_um"], interaction_paths, [9, 58, 107])):
        sign = f"{offset:+g}" if offset else "0"
        # Position a smaller zero explicitly: some Arial versions lack the ₀ glyph.
        heading = text(f"({chr(98+index)})  x", (left, 51.5, 1), 1.8, palette["ink"], bold=True)
        heading["offset_notation"], heading["offset_um"] = "x_0", float(offset)
        bpy.context.view_layer.update()
        subscript = text("0", (left+heading.dimensions.x+0.1, 51.0, 1),
                         1.17, palette["ink"], bold=True)
        bpy.context.view_layer.update()
        text(f" = {sign} µm", (subscript.location.x+subscript.dimensions.x, 51.5, 1),
             1.8, palette["ink"], bold=True)
        image_plane(f"Blender-rendered offset {offset:g} um", path, (left+21.75, 32.5, 0), 43.5, 43.5*0.68)
        if index == 0:
            text(f"{2*float(data['wire_radius_um']):g} µm Cu wire", (left+27, 46.6, 1), 1.08,
                 palette["copper"], align="CENTER")
            text("Gaussian XFEL", (left+1, 43, 1), 1.1, palette["beam"])
        if index == 1:
            text("Incident Gaussian", (left, 16.8, 1), 1.02, palette["blue"], bold=True)
            text("Cu wire edge", (left+24, 16.8, 1), 1.02, palette["copper"])
        draw_profile(data, index, left, 4, 43.5, 10, palette)
    figure_height = FIGURE_HEIGHT
    scene["panel_layout"] = "(a) experimental setup; (b)-(d) transverse offsets with normalized incident Gaussian profiles"
    if rosa_paths is not None:
        if len(rosa_paths) != 3:
            raise ValueError("Provide three ROSA figures in negative, zero, positive offset order")
        # Extend the canvas below the existing figure, preserving its scale.
        panel_width = 46
        rosa_images = [bpy.data.images.load(str(path), check_existing=True) for path in rosa_paths]
        for image in rosa_images:
            image.reload()
        panel_heights = [panel_width * image.size[1] / image.size[0] for image in rosa_images]
        row_height = math.ceil(max(panel_heights) + 4)
        for obj in scene.objects:
            if obj != scene.camera:
                obj.location.y += row_height
        figure_height += row_height
        scene.render.resolution_y = round(resolution * figure_height / FIGURE_WIDTH)
        scene.camera.location.y = figure_height / 2
        line("ROSA section rule", [(9, row_height - 0.5, 1), (151, row_height - 0.5, 1)],
             palette["rule"], 0.035)
        for offset, path, left, height in zip([-4.95, 0, 4.95], rosa_paths, [9, 58, 107], panel_heights):
            panel = image_plane(f"ROSA experimental SAXS offset {offset:+g} um", path,
                                (left + 21.75, 2 + height / 2, 0), panel_width, height)
            panel["rosa_offset_um"] = offset
            panel["source_figure"] = str(Path(path).resolve())
            panel["q_axis_aspect"] = 1.0
        scene["panel_layout"] += "; untitled experimental ROSA SAXS at -4.95, 0, +4.95 µm, equal q-axis scaling, one shared colorbar"
    scene["figure_canvas"] = [FIGURE_WIDTH, figure_height]
    scene["editing"] = "Scenes 01–03 contain editable interactions; scene 04 contains the beamline. Re-run the script to refresh this presentation."
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__) 
    parser.add_argument("--offsets", type=float, nargs=3, default=[-5, 0, 5], metavar="UM")
    parser.add_argument("--fwhm", type=float, help="Target-plane intensity FWHM in µm")
    parser.add_argument("--notebook", type=Path, default=NOTEBOOK)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--output-stem", default="gaussian_wire_offsets_blender")
    parser.add_argument("--resolution", type=int, default=3200, help="Combined figure width in pixels")
    parser.add_argument("--samples", type=int, default=48, help="Cycles samples for each 3D scene")
    parser.add_argument("--rosa-figure-dir", type=Path,
                        help="Add titleless PNGs made by export_rosa_experimental_panels.py with equal q-axis scaling")
    # Blender consumes its own arguments; application arguments follow --.
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    if (not args.output_stem or args.output_stem in {".", ".."}
            or any(c in args.output_stem for c in '<>:"/\\|?*')):
        parser.error("Output stem must be a filename without directory components")
    config = read_notebook_geometry(args.notebook)
    fwhm = config["FWHM_UM"] if args.fwhm is None else args.fwhm
    if not math.isfinite(fwhm) or fwhm <= 0 or not all(map(math.isfinite, args.offsets)):
        parser.error("FWHM must be positive and offsets must be finite")
    if len(set(args.offsets)) != 3:
        parser.error("Choose three different wire offsets")
    if args.resolution < 800 or args.samples < 1:
        parser.error("Resolution must be at least 800 and samples at least 1")
    if not math.isfinite(config["WIRE_RADIUS"]) or config["WIRE_RADIUS"] <= 0:
        parser.error("Notebook wire radius must be finite and positive")
    rosa_paths = None
    if args.rosa_figure_dir is not None:
        if not np.allclose(args.offsets, [-5, 0, 5], rtol=0, atol=0.051):
            parser.error("ROSA columns require offsets corresponding to -4.95, 0, +4.95 µm")
        rosa_paths = rosa_figure_paths(args.rosa_figure_dir)
    data = make_plot_data(config, args.offsets, fwhm)
    tag = lambda value: f"{value:g}".replace(".", "p")
    sigma = f"sigmaL_{tag(config['WIRE_SIGMA_LEFT_NM'])}nm_sigmaR_{tag(config['WIRE_SIGMA_RIGHT_NM'])}nm"
    output = (args.output_dir or OUTPUTS_DIR/sigma/"schematics"/"blender").resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Reset only after all configuration has been validated. Run in a fresh process.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    startup_scene = bpy.context.scene
    paths, interactions = [], []
    panel_width = max(800, round(args.resolution*0.42))
    for index, offset in enumerate(args.offsets):
        scene = draw_interaction_3d(data, index, panel_width, args.samples)
        offset_tag = f"{offset:+g}".replace("+", "p").replace("-", "m").replace(".", "p")
        path = output/f"{args.output_stem}_offset_{offset_tag}um.png"
        render(scene, path)
        paths.append(path)
        interactions.append(path)
    setup = draw_setup_3d(config, round(args.resolution*0.9), args.samples)
    setup_path = output/f"{args.output_stem}_experimental_geometry.png"
    render(setup, setup_path)
    paths.append(setup_path)
    figure = draw_figure(config, data, interactions, setup_path, args.resolution, rosa_paths)
    figure_path = output/f"{args.output_stem}.png"
    render(figure, figure_path)
    paths.append(figure_path)
    bpy.data.scenes.remove(startup_scene)
    # All images and fonts travel with the .blend file.
    bpy.ops.file.pack_all()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.shading.type = "MATERIAL"
    blend_path = output/f"{args.output_stem}.blend"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=True)
    paths.append(blend_path)
    np.savez_compressed(output/f"{args.output_stem}_plot_data.npz", **data)
    metadata = dict(
        renderer=f"Blender {bpy.app.version_string} / Cycles", source_notebook=str(args.notebook.resolve()),
        notebook_numeric_settings=config, offsets_um=args.offsets, target_intensity_fwhm_um=fwhm,
        coordinate_mapping="Blender X = beam z; Blender Y = transverse x; Blender Z = wire y; one unit = one µm in interaction scenes",
        offset_definition="wire centre minus beam axis along the transverse coordinate",
        panel_layout=figure["panel_layout"],
        incident_beam_direction="Editable solid blue arrow along physical +z (Blender +X), before the Cu wire in panel (a)",
        transmitted_beam_direction="Editable blue arrow with Gaussian light after the Cu wire toward XPCI in panel (a)",
        reflected_beam_direction="Editable blue arrow along the reflected SAXS branch toward Jungfrau in panel (a)",
        experimental_offset_files={f"{offset:+g}": EXPERIMENTAL_OFFSET_FILES[offset]
                                   for offset in args.offsets if offset in EXPERIMENTAL_OFFSET_FILES},
        coordinate_axes="Panels (b)-(d): x transverse to beam and wire, y along wire, z along beam; shared origin at beam exit",
        incident_intensity="I(r)/I0 = exp(-4 ln(2) r^2/FWHM^2)",
        beam_style=BEAM_STYLE,
        apparatus_style=APPARATUS_STYLE,
        beam_style_reference="Huber et al., Nature Communications 13, 3220 (2022), Fig. 1. doi:10.1038/s41467-022-30703-y",
        beam_contours="Panels (b)-(d): golden outer envelope at 1/e² intensity radius and bright inner core at half-maximum radius. Panel (a): soft blue Gaussian light without contour shells.",
        geometric_intercepted_fraction=data["geometric_intercepted_fraction"].tolist(),
        interpretation="Incident envelope and geometry only; display volume density is illustrative, not absorption or propagated detector intensity.",
        wire_surface="Sharp cylinder; notebook nanometre edge blur is not resolved at this schematic scale.",
        reference="Huang et al., Fig. 2, Matter Radiat. Extremes 11, 017201 (2026). doi:10.1063/5.0279974",
        detectors="Jungfrau SAXS and XPCI/Optique Peter image panels from Huang et al., Fig. 2. Both published images are packed into the Blender file; they are reference panels, not newly simulated detector results. The XPCI label identifies the paper's 7.5x objective and Andor Zyla camera.",
        reflected_beams="Exactly one blue 3D Gaussian-style reflected SAXS branch beginning on the upper HAPG surface and reaching the Jungfrau panel. Its width and path are illustrative, not separate physical ray traces from each mirror.",
        mirrors="Two original green Highly Annealed Pyrolytic Graphite plates restored, including their locations, dimensions and parallel 15-degree tilts. Apparatus dimensions, distances and angles are schematic.",
        scene_names=[scene.name for scene in bpy.data.scenes], samples=args.samples,
        combined_resolution=[figure.render.resolution_x, figure.render.resolution_y], outputs=[str(path) for path in paths],
    )
    if rosa_paths is not None:
        metadata["rosa_wire_scan"] = dict(offsets_um=[-4.95, 0, 4.95],
                                          figures=[str(path) for path in rosa_paths],
                                          kind="experimental SAXS", q_axis_aspect=1, titles=False,
                                          shared_colorbar=True)
    (output/f"{args.output_stem}_metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print("Created native Blender scenes and renders:", flush=True)
    for path in paths:
        print(path, flush=True)


if __name__ == "__main__":
    main()
