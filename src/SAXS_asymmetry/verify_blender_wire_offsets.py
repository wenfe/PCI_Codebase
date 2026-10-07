"""Read-only verification, run by Blender after reopening the generated .blend."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root = Path.cwd()
sys.path.insert(0, str(root / "SAXS_asymmetry"))
import plot_gaussian_wire_offsets as plot

config = plot.read_notebook_geometry()
data = plot.make_plot_data(config, [-5, 0, 5], config["FWHM_UM"])
radius, fwhm = float(data["wire_radius_um"]), float(data["fwhm_um"])
assert len(bpy.data.scenes) == 5
scales = []
for scene in bpy.data.scenes:
    if "wire_offset_um" not in scene:
        continue
    wire = next(obj for obj in scene.objects if "radius_um" in obj)
    assert math.isclose(wire.location.y, scene["wire_offset_um"])
    assert np.allclose(tuple(wire.dimensions), (2*radius, 2*radius, 26))
    assert math.isclose(scene.unit_settings.scale_length, 1e-6, rel_tol=1e-6)
    beam = next(obj for obj in scene.objects if "intensity_fwhm_um" in obj)
    assert math.isclose(beam["intensity_fwhm_um"], fwhm)
    nodes = beam.data.materials[0].node_tree.nodes
    coefficient = -4*math.log(2)/fwhm**2
    assert any(node.type == "MATH" and node.operation == "MULTIPLY"
               and math.isclose(node.inputs[1].default_value, coefficient, rel_tol=1e-6)
               for node in nodes)
    scales.append(scene.camera.data.ortho_scale)
assert len(scales) == 3 and len(set(scales)) == 1

# Independent quadrature verifies the exported intercepted fractions.
for offset, fraction in zip(data["offsets_um"], data["geometric_intercepted_fraction"]):
    xs = np.linspace(offset-radius, offset+radius, 100001)
    ys = np.exp(-4*np.log(2)*(xs/fwhm)**2)
    integral = np.sum((ys[1:]+ys[:-1])*0.5*np.diff(xs))/(fwhm*math.sqrt(math.pi)/(2*math.sqrt(math.log(2))))
    assert math.isclose(float(fraction), integral, abs_tol=1e-8)
assert math.isclose(float(data["geometric_intercepted_fraction"][0]),
                    float(data["geometric_intercepted_fraction"][2]))

images = [image for image in bpy.data.images if image.source == "FILE"]
overview = next(scene for scene in bpy.data.scenes if scene.name.startswith("00"))
rosa_panels = [obj for obj in overview.objects if "rosa_offset_um" in obj]
assert len(rosa_panels) in (0, 3)
if rosa_panels:
    assert sorted(obj["rosa_offset_um"] for obj in rosa_panels) == [-4.95, 0, 4.95]
    assert {Path(obj["source_figure"]).name for obj in rosa_panels} == {
        "p3129_r0484_22.855.png", "p3129_r0484_22.862.png", "p3129_r0484_22.869.png"}
    assert all(obj["q_axis_aspect"] == 1 for obj in rosa_panels)
    assert not any(obj.type == "FONT" and "ROSA" in obj.data.body for obj in overview.objects)
assert len(images) == 6 + len(rosa_panels)
assert any(image.name == "saxs_fig2.png" for image in images)
assert any(image.name == "pci_fig2.png" for image in images)
assert all(image.packed_file and min(image.size) > 0 for image in images)
assert all(font.packed_file for font in bpy.data.fonts if font.filepath and font.filepath != "<builtin>")

bpy.context.window.scene = overview
bpy.context.view_layer.update()
canvas_width, canvas_height = overview.get("figure_canvas", [160, 120])
for obj in overview.objects:
    if obj.type == "FONT":
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        assert min(p.x for p in corners) >= 0 and max(p.x for p in corners) <= canvas_width, obj.name
        assert min(p.y for p in corners) >= 0 and max(p.y for p in corners) <= canvas_height, obj.name

beamline = next(scene for scene in bpy.data.scenes if scene.name.startswith("04"))
normal = Vector((-math.sin(math.radians(15)), 0, math.cos(math.radians(15))))
bpy.context.window.scene = beamline
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
detector = beamline.objects["SAXS Jungfrau | Fig. 2 reference"]
assert np.allclose(tuple(detector.location), (26, -1, 15.8))
assert np.allclose(tuple(detector.scale), (10, 9, 1))
assert not any(obj.name.startswith("Jungfrau sensor tile") for obj in beamline.objects)
for index in [1, 2]:
    plate = beamline.objects[f"HAPG mirror {index}"]
    assert (Vector(plate["reflection_normal"])-normal).length < 1e-5
    expected_center = [(-6, 0, -2.8), (13.6, 0, 4.05)][index-1]
    assert np.allclose(tuple(plate.location), expected_center)
    assert math.isclose(plate.rotation_euler.y, -math.radians(15), abs_tol=1e-7)
    local_points = [Vector(point) for point in plate.bound_box]
    size = [max(p[i] for p in local_points)-min(p[i] for p in local_points) for i in range(3)]
    assert np.allclose(size, (13, 5.5, 0.65))
    assert not plate.children

branches = [obj for obj in beamline.objects if "beam_start" in obj]
assert len(branches) == 1
reflected = branches[0]
assert reflected.name == "Reflected SAXS | single branch"
assert sum(obj.get("display_color") == "red" for obj in beamline.objects) == 1
assert not any(obj.name.startswith("Incident SAXS") for obj in beamline.objects)
start, end = Vector(reflected["beam_start"]), Vector(reflected["beam_end"])
mirror_frame = beamline.objects["HAPG mirror 2"].evaluated_get(depsgraph).matrix_world
mirror_start = mirror_frame.inverted() @ start
assert abs(mirror_start.x) < 6.5 and abs(mirror_start.y) < 2.75
assert math.isclose(mirror_start.z, 0.325, abs_tol=1e-5)
panel_frame = detector.evaluated_get(depsgraph).matrix_world
local_endpoint = panel_frame.inverted() @ end
assert abs(local_endpoint.x) < 1 and abs(local_endpoint.y) < 1
assert math.isclose(local_endpoint.z, 0.05, abs_tol=1e-4)
assert end.x > start.x and end.z > start.z

pci = beamline.objects["PCI Andor Zyla | Fig. 2 reference"]
assert np.allclose(tuple(pci.location), (64, -1, 0))
assert "Optique Peter" in beamline.objects
assert not any(obj.name.startswith("Zyla ") for obj in beamline.objects)
primary = beamline.objects["Schematic primary XFEL"]
primary_end = primary.location.x+primary.dimensions.x/2
assert math.isclose(primary_end, 57.6, abs_tol=1e-4)
pci_evaluated = pci.evaluated_get(depsgraph)
pci_left_edge = min((pci_evaluated.matrix_world @ Vector(c)).x for c in pci_evaluated.bound_box)
assert 0 < pci_left_edge-primary_end < 1, (pci_left_edge, primary_end)
for obj in beamline.objects:
    if obj.type == "FONT":
        evaluated = obj.evaluated_get(depsgraph)
        projected = [world_to_camera_view(beamline, beamline.camera.evaluated_get(depsgraph),
                                         evaluated.matrix_world @ Vector(c)) for c in evaluated.bound_box]
        assert all(0 <= p.x <= 1 and 0 <= p.y <= 1 for p in projected), obj.name
bpy.context.window.scene = overview

print(json.dumps({"status": "PASS", "scenes": len(bpy.data.scenes),
                  "packed_images": len(images), "wire_diameter_um": 2*radius,
                  "fwhm_um": fwhm, "offsets_um": [-5, 0, 5],
                  "checks": "reopened scene geometry, Gaussian profile, packed assets, text framing, Fig. 2 HAPG plates and both detector panels, exactly one red 3D SAXS branch, horizontal gold beam to XPCI"}))

# Render the saved presentation at screen size for visual review, without
# changing the saved .blend or the full-resolution deliverable.
overview.render.resolution_percentage = 50
overview.render.image_settings.file_format = "JPEG"
overview.render.image_settings.color_mode = "RGB"
overview.render.image_settings.quality = 94
overview.render.filepath = str(root / "tmp/blender-apparatus-final-review.jpg")
bpy.ops.render.render(write_still=True)
