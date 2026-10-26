# -*- coding: utf-8 -*-
"""IDEA-05B · 取药结构 v3：建模 → 结构校验 → 出图 → 导出
流程沿用 v2：mm 场景建模+校验 → finalize_meters() → 米场景渲染 → 存 blend/GLB/STL
用法：blender -b --factory-startup --python tools/v3/build_v3.py
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import parts
import params as P
import lib as L

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'renders', 'v3')
MOD = os.path.join(ROOT, 'model', 'v3')
SHOW = 2                                    # 展示格：周三


def bvh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(ob, dg)


def min_gap(a, b):
    """a 的顶点到 b 表面的最近距离（mm），两件都已在世界坐标。"""
    tb = bvh(b)
    mw, mwb = a.matrix_world, b.matrix_world.inverted()
    best = 1e9
    for v in a.data.vertices:
        p = mwb @ (mw @ v.co)
        hit = tb.find_nearest(p)
        if hit[0] is not None:
            best = min(best, hit[3])
    return round(best, 3)


L.reset()
M = parts.materials()
tray = parts.tray(M)
cups = [parts.cup('CupV3_%d' % i, M, cx) for i, cx in enumerate(P.CELL_CX)]
lids = [parts.lid('Lid_%d' % i, M, cx) for i, cx in enumerate(P.CELL_CX)]

# ---------------- 结构校验
info = dict(cell_cx=[round(c, 3) for c in P.CELL_CX])
info['cup_x_tray_mm3'] = [L.interference_volume(c, tray) for c in cups]
info['cup_x_lid_closed_mm3'] = [L.interference_volume(c, l) for c, l in zip(cups, lids)]
info['lid_x_tray_closed_mm3'] = L.interference_volume(lids[0], tray)
info['handle_to_lid_gap_mm'] = min_gap(cups[0], lids[0])
sweep = {}
for a in (0, 15, 30, 45, 60, 75, 90, 105):
    parts.set_lid_angle(lids[0], a)
    sweep[str(a)] = [L.interference_volume(cups[0], lids[0]), L.interference_volume(tray, lids[0])]
info['lid_sweep_cup_tray_mm3'] = sweep
parts.set_lid_angle(lids[0], 0)

# 防呆：杯绕 Z 转 180° 放进同一杯位，必须与角填块干涉
probe = parts.cup('probe', M, 0.0, place=False)
probe.rotation_euler = (0, 0, math.pi)
probe.location = (P.CELL_CX[0], P.CUP_Y0 + P.CUP_D, P.CUP_Z0)
bpy.context.view_layer.update()
info['reversed_cup_x_tray_mm3'] = L.interference_volume(probe, tray)
bpy.data.objects.remove(probe, do_unlink=True)

# 剖面关键尺寸（杯局部）
prof, y_lip = parts.cup_floor_profile()
info['cup_section'] = dict(lip_z=P.LIP_Z, low_z=P.FLOOR_LOW_Z, back_floor_z=P.FLOOR_BACK_Z,
                           cove_r=P.COVE_R, lip_land_y=[0.0, round(y_lip, 2)],
                           depth_rim_to_low=round(P.CUP_H - P.FLOOR_LOW_Z, 2),
                           lip_above_low=round(P.LIP_Z - P.FLOOR_LOW_Z, 2),
                           funnel_half_angle_deg=round(math.degrees(math.atan(
                               (P.CUP_W / 2 - P.CUP_WALL - P.SPOUT_W / 2) / P.FUNNEL_LEN)), 1),
                           handle_top_world_z=P.CUP_Z0 + P.CUP_H + P.HANDLE_H,
                           lid_cavity_top_world_z=P.HINGE_Z + P.LID_H - P.LID_TOP_T)
rep = L.report([tray, cups[0], lids[0]], os.path.join(MOD, 'v3_report.json'), extra=info)
print('V3_INFO', json.dumps(info, ensure_ascii=False))

# ---------------- 展示件：周三格开盖 + 药片；另一只杯倒药姿态
pills = []
cx = P.CELL_CX[SHOW]
base = P.CUP_Z0
for k, (kind, x, y, z, rz) in enumerate([
        ('t', -6, 12, 3.2, 0), ('t', 4, 11, 3.2, 0), ('c', 7, 26, 3.9, 20), ('o', -8, 28, 4.2, -30),
        ('c', -1, 40, 4.4, 80)]):
    loc = (cx + x, P.CUP_Y0 + y, base + z + 1.9)
    if kind == 't':
        o = parts.tablet('Pill_%d' % k, M['pill_w'], 8.0, 3.6, loc)
    elif kind == 'o':
        o = parts.capsule('Pill_%d' % k, M['pill_w'], 13.0, 6.5, loc)
        o.scale = (1, 1, 0.65)
    else:
        o = parts.capsule('Pill_%d' % k, M['pill_o'] if k == 2 else M['pill_i'], 18.0, 6.4, loc)
    o.rotation_euler = (0, 0, math.radians(rz))
    pills.append(o)
parts.set_lid_angle(lids[SHOW], P.LID_OPEN_DEG)

model = [tray] + cups + lids + pills
bpy.context.view_layer.update()
for o in model:                         # finalize_meters 只缩网格不缩 location：先把变换烘焙进网格
    o.data.transform(o.matrix_world); o.matrix_world.identity()
L.finalize_meters(model)
bpy.context.view_layer.update()

# ---------------- 渲染（米场景）
L.studio(bg=0.90)
C = Vector((cx, 35.0, 34.0)) * 0.001
L.lights(tuple(C))
L.setup_render(res=(1600, 1150), samples=64, exposure=-0.15)


def shot(name):
    L.render_to(os.path.join(OUT, name))


def cam(loc_off, tgt=C, lens=60):
    L.clear_cameras()
    L.cam_persp(tuple(Vector(loc_off) + tgt), tuple(tgt), lens=lens)


# 1) 整排 3/4（周三开盖）
cam((0.13, -0.42, 0.26), Vector((0.16, 0.035, 0.034)), lens=55)
shot('v3_row_iso.png')
# 2) 周三格近景（看收拢槽 / 弧底 / 勾手）
cam((0.05, -0.11, 0.11), lens=55)
shot('v3_cell_iso.png')
# 3) 俯视（看收拢 22° 与防呆角）
L.clear_cameras(); L.cam_ortho('top', tuple(C), scale=0.085)
shot('v3_cell_top.png')

# 4) 剖面 A–A：过周三杯中轴（x = cx），保留 +X 半边，从 -X 看
secs = []
for o in [tray, cups[SHOW], lids[SHOW]] + pills:
    s = o.copy(); s.data = o.data.copy(); L.link(s)
    s.matrix_world = o.matrix_world.copy()
    secs.append(s)
for s in secs:
    s.data.transform(s.matrix_world); s.matrix_world.identity()
for s in secs[:3]:
    L.cut_half(s, 'X', cx * 0.001, keep='+', cap=True, section_mat=M['section'])
hide = [o for o in model]
for o in hide:
    o.hide_render = True
L.clear_cameras(); L.cam_ortho('left', tuple(C), scale=0.078)
shot('v3_section_AA.png')
cam((-0.09, -0.10, 0.07), lens=60)
shot('v3_section_AA_iso.png')
for s in secs:
    bpy.data.objects.remove(s, do_unlink=True)
for o in hide:
    o.hide_render = False

# 5) 倒药姿态：周三杯提起、绕前唇前倾 45°
from mathutils import Matrix
cup = cups[SHOW]
pv = Vector((cx, P.CUP_Y0, P.CUP_Z0 + P.LIP_Z)) * 0.001
POUR = (Matrix.Translation((0, -0.004, 0.030)) @ Matrix.Translation(pv) @
        Matrix.Rotation(math.radians(45), 4, 'X') @ Matrix.Translation(-pv))
saved = {o.name: o.matrix_world.copy() for o in [cup] + pills}
for o in [cup] + pills:
    o.matrix_world = POUR @ o.matrix_world
bpy.context.view_layer.update()
for o in pills:                         # 静态图里药片不会自己滑：倒药过程看 sim_pour_*.png
    o.hide_render = True
cam((0.11, -0.16, 0.09), Vector((cx * 0.001, 0.02, 0.06)), lens=55)
shot('v3_pour45.png')
for o in pills:
    o.hide_render = False
for o in [cup] + pills:
    o.matrix_world = saved[o.name]
bpy.context.view_layer.update()

# ---------------- 交付（复位后存）
L.strip_scene_helpers()
for o in list(bpy.data.objects):
    if o.name.startswith('QA_'):
        bpy.data.objects.remove(o, do_unlink=True)
L.save_blend(os.path.join(MOD, '取药结构_v3.blend'))
L.export_glb(os.path.join(MOD, '取药结构_v3.glb'))
L.export_stl(os.path.join(ROOT, 'stl', 'v3_药杯.stl'), [cups[0]])
L.export_stl(os.path.join(ROOT, 'stl', 'v3_托盘.stl'), [tray])
print('V3_DONE')
