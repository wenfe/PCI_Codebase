"""Native Blender geometry, materials, cameras and annotations.

Run through plot_gaussian_wire_offsets.py inside Blender. In interaction scenes,
Blender (X,Y,Z) means (beam z, transverse x, wire y); one unit is one micrometre.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

if __package__:
    from .paths import REFERENCE_DIR
else:
    if str(Path(__file__).resolve().parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
    from paths import REFERENCE_DIR  # noqa: E402

ASSET_DIR = REFERENCE_DIR / "fig2_schematics"

INK, MUTED, BLUE, COPPER, GREEN, RULE = (
    "#182c40", "#596b7b", "#266ac2", "#b56835", "#729d40", "#dce4eb")
BEAM = "#c28a00"
BEAM_STYLE = "Golden translucent envelope and bright Gaussian core, inspired by Huber et al., Fig. 1 (2022)."
APPARATUS_STYLE = "Huang et al., Fig. 2: two green HAPG plates and Jungfrau/XPCI reference panels, with blue primary arrows, downstream Gaussian light, and one blue reflected SAXS branch."
BEAM_COLORS = {
    "gold": ("#ffd229", "#ffcd13", "#ffd022", "#ffe21a", "#e5a300"),
    "red": ("#ff4436", "#ff291c", "#ff392f", "#ff5536", "#d42a21"),
    "blue": ("#438ce4", "#8ac1ff", "#83bbf6", "#9dcbff", "#347bd0"),
}


def rgba(color):
    """sRGB design colour to Blender linear shader inputs."""
    values = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    return tuple(v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
                 for v in values) + (1,)


def material(name, color, *, metal=0, roughness=0.4, flat=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba(color)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeEmission" if flat else "ShaderNodeBsdfPrincipled")
    shader.inputs["Color" if flat else "Base Color"].default_value = rgba(color)
    if not flat:
        shader.inputs["Metallic"].default_value = metal
        shader.inputs["Roughness"].default_value = roughness
    links.new(shader.outputs[0], output.inputs["Surface"])
    return mat


def new_scene(name, width, height, samples=32):
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.seed = 17
    scene.cycles.max_bounces = 8
    scene.cycles.volume_bounces = 2
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new(name + " studio")
    scene.world.use_nodes = True
    nodes, links = scene.world.node_tree.nodes, scene.world.node_tree.links
    nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    nodes["Background"].inputs["Strength"].default_value = 0.65
    light_path = nodes.new("ShaderNodeLightPath")
    white = nodes.new("ShaderNodeBackground")
    white.inputs["Color"].default_value = (1, 1, 1, 1)
    mix = nodes.new("ShaderNodeMixShader")
    links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    links.new(nodes["Background"].outputs[0], mix.inputs[1])
    links.new(white.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes["World Output"].inputs["Surface"])
    return scene


def camera(scene, eye, target, scale):
    data = bpy.data.cameras.new(scene.name + " orthographic camera")
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = eye
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()
    data.type, data.ortho_scale, data.clip_end = "ORTHO", scale, 1000
    scene.camera = obj
    return obj


def studio(scene, scale=1):
    for name, position, power, size in [
        ("Large soft key", (-25, -35, 40), 18000, 42),
        ("Copper rim", (22, 20, 28), 11000, 32),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = power*scale**2, "DISK", size*scale
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = Vector(position)*scale
        obj.rotation_euler = (-obj.location).to_track_quat("-Z", "Y").to_euler()


def cylinder(name, radius, depth, location, mat, axis="Z"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    if axis == "X":
        obj.rotation_euler.y = math.pi/2
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    elif axis == "Y":
        obj.rotation_euler.x = math.pi/2
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def box(name, location, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name, obj.dimensions = name, size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft machined edges", "BEVEL")
        modifier.width, modifier.segments = bevel, 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def line(name, points, mat, radius=0.04, closed=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions, curve.resolution_u = "3D", 1
    curve.bevel_depth, curve.bevel_resolution = radius, 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point, coord in zip(spline.points, points):
        point.co = (*coord, 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def arrow(name, start, end, mat, radius=0.075, head=0.8):
    start, end = Vector(start), Vector(end)
    direction = (end-start).normalized()
    line(name, [start, end-direction*head*0.8], mat, radius)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius*3.5, radius2=0,
                                   depth=head, location=end-direction*head/2)
    obj = bpy.context.object
    obj.name = name + " arrowhead"
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)


def text(body, location, size, mat, *, align="LEFT", facing=None, bold=False):
    font = bpy.data.curves.new(body, "FONT")
    font.body, font.size, font.align_x, font.space_line = body, size*1.6, align, 1.2
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    if path.exists():
        font.font = bpy.data.fonts.load(str(path), check_existing=True)
    obj = bpy.data.objects.new(body, font)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    if facing:
        obj.rotation_euler = facing.rotation_euler
    font.materials.append(mat)
    return obj


def image_plane(name, path, center, width, height, facing=None):
    bpy.ops.mesh.primitive_plane_add(size=2, location=center)
    obj = bpy.context.object
    obj.name, obj.scale = name, (width/2, height/2, 1)
    if facing:
        obj.rotation_euler = facing.rotation_euler
    mat = bpy.data.materials.new(name + " image")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path), check_existing=True)
    tex.interpolation = "Linear"
    shader = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(tex.outputs["Color"], shader.inputs["Color"])
    links.new(shader.outputs[0], output.inputs["Surface"])
    obj.data.materials.append(mat)
    return obj


def beam_surface(name, color, opacity):
    """A clean, translucent illustration surface for the incident envelope."""
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgba(color)[:3], opacity)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    gold = nodes.new("ShaderNodeEmission")
    gold.inputs["Color"].default_value = rgba(color)
    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = opacity
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(gold.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return mat


def gaussian_volume(name, fwhm, length=36, center=(0, 0, 0), density=0.12,
                    color="gold", opacity_scale=1, contours=True):
    """Paper-inspired translucent beam with a Gaussian core and explicit envelope.

    The 1/e² shell and half-maximum core are intensity contours, not hard beam
    edges. The halo retains the original radial Gaussian and target-plane FWHM.
    Contours can be hidden for a soft schematic glow.
    """
    volume_color, emission_color, envelope_color, core_color, rim_color = BEAM_COLORS[color]
    mat = bpy.data.materials.new(name + " radial Gaussian volume")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    volume = nodes.new("ShaderNodeVolumePrincipled")
    volume.inputs["Color"].default_value = rgba(volume_color)
    volume.inputs["Anisotropy"].default_value = 0.15
    coords, split = nodes.new("ShaderNodeTexCoord"), nodes.new("ShaderNodeSeparateXYZ")
    links.new(coords.outputs["Object"], split.inputs[0])

    def math_node(operation, a, b=None):
        node = nodes.new("ShaderNodeMath")
        node.operation = operation
        for index, value in enumerate([a] if b is None else [a, b]):
            if isinstance(value, (int, float)):
                node.inputs[index].default_value = value
            else:
                links.new(value, node.inputs[index])
        return node.outputs[0]

    y2 = math_node("MULTIPLY", split.outputs["Y"], split.outputs["Y"])
    z2 = math_node("MULTIPLY", split.outputs["Z"], split.outputs["Z"])
    exponent = math_node("MULTIPLY", math_node("ADD", y2, z2), -4*math.log(2)/fwhm**2)
    gaussian = math_node("EXPONENT", exponent)
    links.new(math_node("MULTIPLY", gaussian, density*opacity_scale), volume.inputs["Density"])
    volume.inputs["Emission Color"].default_value = rgba(emission_color)
    links.new(math_node("MULTIPLY", gaussian, 0.015*opacity_scale), volume.inputs["Emission Strength"])
    links.new(volume.outputs["Volume"], output.inputs["Volume"])
    obj = cylinder(name, 1.6*fwhm/math.sqrt(2*math.log(2)), length, center, mat, axis="X")
    obj["intensity_fwhm_um"] = fwhm
    obj["description"] = ("Incident Gaussian envelope; schematic display density, no propagation calculation."
                          if color == "gold" else "Illustrative SAXS envelope; Gaussian radial display profile, not a propagated detector intensity.")
    obj["beam_style"] = BEAM_STYLE if color == "gold" else APPARATUS_STYLE
    obj["display_color"] = color
    if contours:
        w = fwhm/math.sqrt(2*math.log(2))
        envelope = cylinder(name + " | translucent 1/e² envelope", w, length, center,
                            beam_surface(name + " translucent envelope", envelope_color, 0.16*opacity_scale), axis="X")
        envelope["relative_intensity_contour"] = math.exp(-2)
        core = cylinder(name + " | luminous half-maximum core", fwhm/2, length, center,
                        beam_surface(name + " luminous core", core_color, 0.3*opacity_scale), axis="X")
        core["relative_intensity_contour"] = 0.5
        theta = [i*math.tau/160 for i in range(160)]
        rim = beam_surface(name + " contour", rim_color, 0.7*opacity_scale)
        for side in [-1, 1]:
            line(name + " | envelope rim", [(center[0]+side*length/2,
                 center[1]+w*math.cos(t), center[2]+w*math.sin(t)) for t in theta],
                 rim, min(0.045, fwhm*0.006), closed=True)
    return obj


def draw_interaction_3d(data, index, width=1200, samples=32):
    radius, fwhm, offset = (
        float(data["wire_radius_um"]), float(data["fwhm_um"]), float(data["offsets_um"][index]))
    scene = new_scene(f"{index+1:02d} | Wire offset {offset:+g} um", width, round(width*0.68), samples)
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1e-6
    scene["wire_offset_um"] = offset
    scene["coordinate_mapping"] = "Blender X = beam z; Blender Y = transverse x; Blender Z = wire y"
    extent = max(1, (max(abs(float(d)) for d in data["offsets_um"])+radius)/12, fwhm/10)
    cam = camera(scene, (45, -72, 35), (0, 0, -1), 53*extent)
    studio(scene)
    copper = material("Satin copper", "#cf8d55", metal=0.4, roughness=0.42)
    beam_ink = material("Beam annotations", BEAM, flat=True)
    wire = cylinder(f"Cu wire | diameter {2*radius:g} um", radius, 26, (0, offset, 0), copper)
    wire["radius_um"], wire["offset_um"] = radius, offset
    gaussian_volume("Incident XFEL | golden Gaussian beam", fwhm)
    # Physical coordinates: x is transverse (Blender Y), y follows the wire
    # (Blender Z), and z follows the beam (Blender X). Use a shared origin
    # just beyond the beam exit to keep the triad clear of the wire.
    axis_origin = (18.4, 0, 0)
    arrow("Transverse axis x", axis_origin, (18.4, 6.5, 0), beam_ink)
    text("x", (18.4, 7.1, 0), 1.4, beam_ink, facing=cam)
    arrow("Wire axis y", axis_origin, (18.4, 0, 6.5), beam_ink)
    text("y", (18.4, 0, 7.1), 1.4, beam_ink, facing=cam)
    arrow("Beam propagation z", (18.4, 0, 0), (23.5, 0, 0), beam_ink)
    text("z", (24, 0, 0), 1.4, beam_ink, facing=cam)
    scene["coordinate_axes"] = "Shared-origin xyz triad at beam exit: x transverse, y along wire, z along beam"
    # Offset values are shown once in the panel headings. Keep the region
    # below the cylinders free of duplicate labels and dimension guides.
    return scene


def assembly(name, location, rotation=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    if rotation is not None:
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = rotation
    return obj


def beam_segment(name, start, end, fwhm, *, opacity_scale=1, color="red", contours=True):
    """Orient the same radial beam shader along an arbitrary 3D ray."""
    start, end = Vector(start), Vector(end)
    vector = end-start
    before = set(bpy.context.scene.objects)
    gaussian_volume(name + " volume", fwhm, length=vector.length, color=color,
                    density=0.15, opacity_scale=opacity_scale, contours=contours)
    parts = set(bpy.context.scene.objects)-before
    parent = assembly(name, (start+end)/2, Vector((1, 0, 0)).rotation_difference(vector.normalized()))
    for obj in parts:
        obj.parent = parent
    parent["beam_start"] = list(start)
    parent["beam_end"] = list(end)
    parent["description"] = f"Illustrative {color} SAXS beam envelope; not a simulated angular intensity distribution."
    return parent


def hapg_crystal(index, center, palette):
    """Restore the original simple green plate at its original location/tilt."""
    plate = box(f"HAPG mirror {index}", center, (13, 5.5, 0.65), palette["hapg"], 0.12)
    plate.rotation_euler.y = -math.radians(15)
    plate["component"] = "Highly Annealed Pyrolytic Graphite; original green plate design"
    plate["reflection_normal"] = [-math.sin(math.radians(15)), 0, math.cos(math.radians(15))]
    return plate


def saxs_detector(cam):
    """Restore the original Fig. 2 reference panel, not a simulated pattern."""
    panel = image_plane("SAXS Jungfrau | Fig. 2 reference", ASSET_DIR/"saxs_fig2.png",
                        (26, -1, 15.8), 20, 18, facing=cam)
    panel["component"] = "Original Jungfrau SAXS reference image from Huang et al., Fig. 2"
    return panel


def pci_detector(cam):
    """XPCI image panel and Optique Peter label as shown in Huang et al., Fig. 2."""
    panel = image_plane("PCI Andor Zyla | Fig. 2 reference", ASSET_DIR/"pci_fig2.png",
                        (64, -1, 0), 12, 12, facing=cam)
    panel["component"] = "Fig. 2 XPCI reference panel; Optique Peter imaging system and Andor Zyla camera"
    white = material("Fig. 2 detector panel lettering", "#ffffff", flat=True)
    rotation = cam.rotation_euler.to_quaternion()
    bpy.ops.mesh.primitive_plane_add(size=2, location=panel.location + rotation @ Vector((0, -5.1, 0.05)))
    caption_band = bpy.context.object
    caption_band.name = "XPCI reference panel caption band"
    caption_band.scale = (6, 0.9, 1)
    caption_band.rotation_euler = cam.rotation_euler
    caption_band.data.materials.append(beam_surface("XPCI caption contrast", "#17212a", 0.70))
    text("Optique Peter", panel.location + rotation @ Vector((0, -5.15, 0.10)),
         0.95, white, align="CENTER", facing=cam)
    return panel


def fit_apparatus_camera(scene):
    """Frame every modeled part and label with a small publication margin."""
    bpy.context.view_layer.update()
    inverse = scene.camera.matrix_world.inverted()
    points = [inverse @ obj.matrix_world @ Vector(corner)
              for obj in scene.objects if obj.type in {"MESH", "CURVE", "FONT"}
              for corner in obj.bound_box]
    xmin, xmax = min(p.x for p in points), max(p.x for p in points)
    ymin, ymax = min(p.y for p in points), max(p.y for p in points)
    rotation = scene.camera.rotation_euler.to_quaternion()
    scene.camera.location += rotation @ Vector(((xmin+xmax)/2, (ymin+ymax)/2, 0))
    aspect = scene.render.resolution_x/scene.render.resolution_y
    scene.camera.data.ortho_scale = max((xmax-xmin)*1.045, (ymax-ymin)*aspect*1.075)


def draw_setup_3d(config, width=2800, samples=32):
    scene = new_scene("04 | SAXS and PCI experimental geometry", width, round(width*0.27), samples)
    cam = camera(scene, (0, -170, 45), (0, 0, 5), 147)
    studio(scene, 2)
    palette = {
        "hapg": material("HAPG original green plates", GREEN, metal=0.2),
        "ink": material("Apparatus labels", INK, flat=True),
        "muted": material("Apparatus secondary labels", MUTED, flat=True),
    }
    beam_ink = material("Blue primary XFEL annotations", "#052d70", flat=True)
    reflected_ink = material("Blue reflected SAXS annotations", "#287fbe", flat=True)
    copper = material("Beamline copper", "#cf8d55", metal=0.4, roughness=0.42)
    wire_x, wire_radius = -37, 0.9
    cylinder("Cu target wire", wire_radius, 16, (wire_x, 0, 0), copper)
    wire_entry, wire_exit = wire_x-wire_radius, wire_x+wire_radius
    primary_end = 57.6
    primary = gaussian_volume("Schematic primary XFEL", 1.4, length=primary_end-wire_exit,
                              center=((wire_exit+primary_end)/2, 0, 0), density=0.3,
                              color="blue", contours=False)
    primary["description"] = "Transmitted Gaussian light after the Cu wire; illustrative display, not a propagated detector intensity."
    arrow("Incident beam direction (+z)", (-64, -2, 0), (wire_entry, -2, 0),
          beam_ink, radius=0.22, head=1.5)
    arrow("Transmitted beam direction (+z)", (wire_exit, -2, 0), (primary_end, -2, 0),
          beam_ink, radius=0.22, head=1.5)
    text("Beam direction (+z)", (-52.5, -2, -3.4), 1.25, beam_ink,
         align="CENTER", facing=cam)
    detector = saxs_detector(cam)
    mirrors = [hapg_crystal(index, center, palette) for index, center in
               enumerate([(-6, 0, -2.8), (13.6, 0, 4.05)], start=1)]
    # Fig. 2 represents the mirror pair with ONE outgoing SAXS branch.
    # This is a diagram of the collected signal, not two independent ray traces.
    panel_anchor = Vector((-7.5, -6.0, 0.05))
    end = detector.location + cam.rotation_euler.to_quaternion() @ panel_anchor
    upper_mirror = mirrors[1]
    start = upper_mirror.location + upper_mirror.rotation_euler.to_quaternion() @ Vector((-5, -1, 0.325))
    reflected = beam_segment("Reflected SAXS | single branch", start, end, 1.2,
                             color="blue", contours=False)
    reflected["description"] = "One combined SAXS branch touching the upper HAPG surface and reaching the Jungfrau panel; illustrative beam width and path."
    reflected["reference_panel_anchor"] = list(panel_anchor)
    # A camera-facing arrow follows the reflected branch toward Jungfrau.
    # Its small depth offset keeps the annotation clear of the beam volume.
    arrow_front = cam.rotation_euler.to_quaternion() @ Vector((0, 0, 2.2))
    arrow("Reflected SAXS direction", start.lerp(end, 0.12) + arrow_front,
          start.lerp(end, 0.88) + arrow_front, reflected_ink, radius=0.10, head=1.1)
    pci_detector(cam)
    for label, location, size, mat, align in [
        (f"Gaussian XFEL  /  {config['PHOTON_ENERGY']:g} keV", (-68, 0, 3.2), 1.65, beam_ink, "LEFT"),
        (f"{2*config['WIRE_RADIUS']/1000:g} µm Cu wire", (-37, 0, 11), 1.7, palette["ink"], "CENTER"),
        ("SAXS HAPG mirrors", (2, -3, -7.5), 1.6, palette["ink"], "CENTER"),
        ("Reflected SAXS", (3, -2, 15), 1.6, reflected_ink, "CENTER"),
        ("Primary XFEL through gap", (29, -2, -4.5), 1.2, beam_ink, "CENTER"),
        (f"SAXS / Jungfrau  ·  {config['Z_SAXS_DETECTOR']/1e9:g} m", (26, 0, 28.5), 1.55, palette["ink"], "CENTER"),
        ("XPCI", (64, 0, 10), 1.9, palette["ink"], "CENTER"),
        ("7.5× objective / Andor Zyla", (59, -2, -9.2), 1.3, palette["muted"], "CENTER"),
    ]:
        text(label, location, size, mat, align=align, facing=cam)
    line("PCI distance", [(-36, -3, -15), (64, -3, -15)], palette["muted"], 0.035)
    for x in [-36, 64]:
        line("Distance endpoint", [(x, -3, -14.5), (x, -3, -15.5)], palette["muted"], 0.045)
    text(f"{config['Z_PCI_DETECTOR']/1e9:g} m from wire", (48, -3, -14.4), 1.3, palette["muted"],
         align="CENTER", facing=cam)
    scene["interpretation"] = "Fig. 2 HAPG plates, Jungfrau and XPCI image panels with 3D beams. One blue branch represents collected SAXS; both detector images are published references, not new simulations."
    scene["apparatus_style"] = APPARATUS_STYLE
    scene["incident_beam_direction"] = "Solid blue arrow along physical +z (Blender +X), before the Cu wire"
    scene["transmitted_beam_direction"] = "Blue arrow and Gaussian light after the Cu wire toward XPCI"
    scene["reflected_beam_direction"] = "Blue arrow along the reflected SAXS branch from the HAPG mirror toward Jungfrau"
    fit_apparatus_camera(scene)
    return scene


def render(scene, path):
    bpy.context.window.scene = scene
    scene.render.filepath = str(Path(path).resolve())
    print(f"RENDERING {scene.name} -> {path}", flush=True)
    bpy.ops.render.render(write_still=True)
