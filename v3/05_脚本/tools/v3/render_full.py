# -*- coding: utf-8 -*-
"""IDEA-05B · 整机 v3 出图（灯光/背景/相机沿用 tools/render_final.py，保持与原设计图一致）
用法：blender -b --factory-startup --python tools/v3/render_full.py -- hero allopen loading front top exp weigh cup
整机剖面不在这里渲染：原底壳网格非严格水密，剖切补面会糊成一片；改由 dump_full_section.py + draw_full_section.py 出工程图。
"""
import bpy, math, os, sys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
BLEND = os.path.join(ROOT, 'model', 'v3', 'IDEA-05_box_v3.blend')
OUT = os.path.join(ROOT, 'renders', 'v3', 'full')
os.makedirs(OUT, exist_ok=True)
import params as P

SHOW = 2
CX = P.CELL_CX[SHOW] * 0.001


def setup():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    try:
        sc.cycles.device = 'GPU'
    except Exception:
        pass
    sc.cycles.samples = 72
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1600, 1200, 100
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    sc.view_settings.exposure = -0.75
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.74, 0.73, 0.71, 1); bg.inputs[1].default_value = 0.32

    def matte(name, col, rough=0.6):
        m = bpy.data.materials.new(name); m.use_nodes = True
        p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        p.inputs['Base Color'].default_value = (*col, 1); p.inputs['Roughness'].default_value = rough
        return m
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0.16, 0.14, -0.0021))
    fl = bpy.context.object; fl.name = 'Floor'; fl.data.materials.append(matte('FloorMat', (0.70, 0.685, 0.66)))
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0.16, 1.1, 0.45), rotation=(math.radians(90), 0, 0))
    bd = bpy.context.object; bd.name = 'Backdrop'; bd.data.materials.append(matte('BackMat', (0.74, 0.725, 0.70), 0.8))

    def area(name, loc, energy, size, color=(1, 1, 1), target=(0.16, 0.035, 0.035)):
        d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.size = size; d.color = color
        o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    area('Key', (0.52, -0.52, 0.62), 55, 0.55, (1.0, 0.97, 0.92))
    area('Fill', (-0.42, -0.42, 0.26), 14, 0.8, (0.88, 0.94, 1.0))
    area('Rim', (-0.08, 0.60, 0.42), 30, 0.35, (1.0, 0.95, 0.88))
    area('Top', (0.16, 0.10, 0.95), 10, 0.7)
    area('FrontFill', (0.16, -0.75, 0.045), 18, 0.8, (1.0, 0.98, 0.95), (0.16, 0.0, 0.035))
    pl = bpy.data.lights.new('CupGlow', 'POINT'); pl.energy = 0.30; pl.color = (1.0, 0.60, 0.26); pl.shadow_soft_size = 0.009
    g = bpy.data.objects.new('CupGlow', pl); sc.collection.objects.link(g); g.location = (CX, P.POCKET_CY * 0.001, 0.031)
    return sc, fl, bd


def camera(sc, loc, target, lens=58, ortho=None):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_start, cd.clip_end = 0.002, 200
    if ortho:
        cd.type = 'ORTHO'; cd.ortho_scale = ortho
    o = bpy.data.objects.new('cam', cd); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o
    return o


def render(sc, name):
    sc.render.filepath = os.path.join(OUT, name)
    bpy.ops.render.render(write_still=True)
    print('RENDERED', name)


def lid(i, deg):
    bpy.data.objects['Lid_%d' % i].rotation_euler = (math.radians(-deg), 0, 0)


def gang(deg):
    """联动全开：7 盖 + 驱动轴 + 拨片一起转。"""
    for o in bpy.data.objects:
        if o.name.startswith(('Lid_', 'DriveShaft', 'Paddle')) and o.parent is None:
            o.rotation_euler = (math.radians(-deg), 0, 0)


def show_template():
    bpy.context.view_layer.layer_collection.children['Accessory'].exclude = False


def objs(prefix):
    return [o for o in bpy.data.objects if o.name.startswith(prefix)]


def hide(names_or_prefixes):
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith(tuple(names_or_prefixes)):
            o.hide_render = True
            for c in o.children:
                c.hide_render = True


def lift(prefixes, dz):
    for o in bpy.data.objects:
        if o.parent is None and o.type == 'MESH' and o.name.startswith(tuple(prefixes)):
            o.location.z += dz


def bisect_copy(name, y, keep_pos=True):
    """原底壳网格不水密，精确布尔会切空；用平面二分切掉 y<y 的部分（不补切面）。"""
    import bmesh
    o = bpy.data.objects[name]
    c = o.copy(); c.data = o.data.copy(); bpy.context.scene.collection.objects.link(c)
    c.data.transform(o.matrix_world); c.matrix_world = Matrix.Identity(4)
    bm = bmesh.new(); bm.from_mesh(c.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, y, 0), plane_no=(0, 1, 0),
                           clear_inner=keep_pos, clear_outer=not keep_pos)
    bm.to_mesh(c.data); bm.free(); c.data.update()
    o.hide_render = True
    return c


modes = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['hero']
for mode in modes:
    sc, fl, bd = setup()
    if mode == 'hero':
        lid(SHOW, 100)
        camera(sc, (0.300, -0.560, 0.400), (0.158, 0.032, 0.040), lens=74)
        render(sc, 'hero_v3')
    elif mode == 'allopen':
        gang(100)
        camera(sc, (0.30, -0.50, 0.46), (0.160, 0.040, 0.040), lens=70)
        render(sc, 'allopen_v3')
    elif mode == 'loading':
        # 批量装药：联动全开 → 捏两端提耳整盘提出 → 盖上装药漏斗模板
        gang(100)
        show_template()
        lift(['TrayV3', 'TrayDay', 'CupV3_', 'Pill_', 'Gasket_v3', 'LoadingTemplate'], 0.060)
        camera(sc, (0.34, -0.50, 0.50), (0.160, 0.035, 0.070), lens=60)
        render(sc, 'loading_v3')
    elif mode == 'front':
        lid(SHOW, 0); fl.hide_render = bd.hide_render = True
        camera(sc, (0.16, -1.0, 0.030), (0.16, 0.035, 0.030), ortho=0.365)
        render(sc, 'front_v3')
    elif mode == 'top':
        lid(SHOW, 100); fl.hide_render = bd.hide_render = True
        camera(sc, (0.16, 0.035, 1.0), (0.16, 0.035, 0.0), ortho=0.375)
        render(sc, 'top_v3')
    elif mode == 'cup':
        lid(SHOW, 100)
        camera(sc, (CX + 0.050, -0.050, 0.150), (CX, 0.036, 0.032), lens=50)
        render(sc, 'cup_v3')
    elif mode == 'exp':
        lid(SHOW, 0)
        lift(['PCB', 'Battery', 'BattTxt', 'Speaker'], 0.014)
        lift(['LoadCell', 'StrainGauge'], 0.030)
        lift(['SensorPlate', 'LED_', 'IR_', 'Carrier', 'LC_Spacer'], 0.046)
        lift(['TrayV3', 'TrayDay'], 0.078)
        lift(['Gasket_v3'], 0.100)
        lift(['CupV3_', 'Pill_'], 0.125)
        lift(['Lid_', 'Hinge_'], 0.165)
        sc.view_settings.exposure = -0.95
        camera(sc, (0.55, -0.64, 0.36), (0.16, 0.035, 0.100), lens=46)
        render(sc, 'exploded_v3')
    elif mode == 'weigh':
        # 称重链：拿掉日盖/杯/密封垫/前脸小件/传感板与主板，托盘抬起 40 mm 露出 3 个球脚与锥窝/V 槽/平面；底座只切掉前壁
        hide(['Lid_', 'Hinge_', 'CupV3_', 'Pill_', 'Gasket_v3', 'HingeRail',
              'Display', 'Btn', 'ControlBand', 'Brand', 'Mic', 'Spk_', 'Pl_', 'UI',
              'SensorPlate', 'LED_', 'IR_', 'PCB', 'Battery', 'BattTxt', 'Speaker'])   # 只留称重链上的件
        lift(['TrayV3', 'TrayDay'], 0.040)
        bisect_copy('BaseShell', 0.010)           # 只切掉前壁，底板留着
        bisect_copy('Seam', 0.010)
        sc.view_settings.exposure = -1.35
        camera(sc, (0.43, -0.29, 0.17), (0.16, 0.040, 0.034), lens=42)
        render(sc, 'weigh_v3')
