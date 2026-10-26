# -*- coding: utf-8 -*-
"""IDEA-05B · 倒药刚体仿真：原设计药杯（v1）vs 取药结构 v3 药杯

两只杯同场：静置 0.67 s → 绕前唇以约 35°/s 匀速前倾到 100° → 保持 1.5 s。
统计：药片开始滑动的倾角、越过唇口的倾角、70° 时 / 结束时杯内残留数、出口横向偏移。
场景 1 BU = 1 mm，重力 9810 mm/s²（Bullet 对 mm 级小件不稳，故不用米制）。
用法：blender -b --factory-startup --python tools/v3/sim_pour.py
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Matrix
import parts
import params as P
import lib as L

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'renders', 'v3')
MOD = os.path.join(ROOT, 'model', 'v3')
FPS, F_SETTLE = 60, 40
TILT_MAX = 100.0                # 超过 90° 才能看出原设计杯到底多少度才倒得出
F_TILT = F_SETTLE + int(round(120 * TILT_MAX / 70.0))   # 恒定约 35°/s
F_END = F_TILT + 90
MU = 0.40                       # 药片-PP 静摩擦约 0.3–0.45，取中值
GAP_X = 90.0


def old_cup(mats):
    """原设计 IDEA-05_box.blend 的药杯：直壁满宽、前 12 mm 底 4.0 / 其余 5.0（≈3.4°/4.8° 台阶），24 宽倒药口唇高 5。"""
    W, D, H = P.CUP_W, P.CUP_D, P.CUP_H
    body = parts.prism_z('CupV1', parts.rr(W, D, 3.5, 0, D / 2), 0, H, mats['cup'])
    L.bevel(body, 0.6, 2, 32)
    prof = [(-3, 9.0), (1.6, 9.0), (1.6, 4.0), (12.0, 4.0), (14.0, 5.0), (D + 2, 5.0), (D + 2, H + 3), (-3, H + 3)]
    cav = L.add_prism_x('cav', prof, -W, W)
    plan = parts.prism_z('plan', parts.rr(38.7, 50.8, 2.6, 0, D / 2), 2.0, H + 4)
    L.boolean(cav, plan, 'INTERSECT')
    L.boolean(body, cav)
    L.boolean(body, L.add_box('sp', 24, 8, 12, (0, 0, 9.0 + 6)))
    parts.clean(body)
    return body


def make_pills(mats, tag, x0):
    """6 粒：2 圆片 Ø8、1 大圆片 Ø10、1 椭圆片、2 粒胶囊（1#、2#）。杯局部坐标给位置。"""
    spec = [('t', 8.0, 3.6, (-9, 40)), ('t', 8.0, 3.6, (8, 44)), ('t', 10.0, 4.2, (0, 34)),
            ('o', 14.0, 7.0, (-8, 26)), ('c', 19.4, 6.9, (9, 28)), ('c', 15.9, 5.8, (-1, 46))]
    out = []
    for k, (kind, a, b, (x, y)) in enumerate(spec):
        loc = (x0 + x, y, 6.0 + 7.0 * k * 0.6)
        if kind == 't':
            o = parts.tablet('%s_pill%d' % (tag, k), mats['pill_w'], a, b, loc)
        elif kind == 'o':
            o = parts.capsule('%s_pill%d' % (tag, k), mats['pill_w'], a, b, loc)
            o.scale = (1, 1, 0.62)
        else:
            o = parts.capsule('%s_pill%d' % (tag, k), mats['pill_o'] if k == 4 else mats['pill_i'], a, b, loc)
            o.rotation_euler = (0, 0, math.radians(70 if k == 4 else 15))
        out.append(o)
    return out


L.reset()
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, F_END
M = parts.materials()
bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame = 30
rw.solver_iterations = 60
rw.point_cache.frame_start, rw.point_cache.frame_end = 1, F_END
sc.gravity = (0, 0, -9810.0)

rigs = {}
for tag, x0, builder in (('v1', 0.0, old_cup), ('v3', GAP_X, None)):
    c = builder(M) if builder else parts.cup('CupV3', M, 0.0, place=False)
    # 原点放在前唇外沿（倒药时的支点）：杯局部 (0, 0, LIP_Z)
    lip = 9.0 if tag == 'v1' else P.LIP_Z
    L.offset_mesh(c, 0, 0, -lip)
    c.location = (x0, 0, lip)
    bpy.context.view_layer.objects.active = c
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    rb = c.rigid_body
    rb.kinematic = True
    rb.collision_shape = 'MESH'
    rb.mesh_source = 'BASE'
    rb.friction, rb.restitution = MU, 0.05
    rb.use_margin, rb.collision_margin = True, 0.05
    for f, ang in ((1, 0), (F_SETTLE, 0), (F_TILT, TILT_MAX), (F_END, TILT_MAX)):
        c.rotation_euler = (math.radians(ang), 0, 0)
        c.keyframe_insert('rotation_euler', frame=f)
    for fc in c.animation_data.action.fcurves if hasattr(c.animation_data.action, 'fcurves') else []:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    ps = make_pills(M, tag, x0)
    for o in ps:
        bpy.context.view_layer.objects.active = o
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        r = o.rigid_body
        r.collision_shape = 'CONVEX_HULL'
        r.mass = 0.0004
        r.friction, r.restitution = MU, 0.1
        r.use_margin, r.collision_margin = True, 0.04
        r.use_deactivation = False
        r.linear_damping, r.angular_damping = 0.1, 0.2
    rigs[tag] = (c, ps, lip)

# 线性插值（Blender 5 的分层动作没有 fcurves 属性时，用通道包遍历）
try:
    for tag, (c, ps, lip) in rigs.items():
        act = c.animation_data.action
        for layer in getattr(act, 'layers', []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for kp in fc.keyframe_points:
                            kp.interpolation = 'LINEAR'
except Exception as e:
    print('INTERP_WARN', e)

bpy.ops.ptcache.bake_all(bake=True)


def tilt_at(f):
    if f <= F_SETTLE:
        return 0.0
    if f >= F_TILT:
        return TILT_MAX
    return TILT_MAX * (f - F_SETTLE) / (F_TILT - F_SETTLE)


track = {t: {o.name: [] for o in rigs[t][1]} for t in rigs}
for f in range(1, F_END + 1):
    sc.frame_set(f)
    for tag, (c, ps, lip) in rigs.items():
        inv = c.matrix_world.inverted()
        for o in ps:
            p = inv @ o.matrix_world.translation          # 杯局部（原点=前唇外沿，z 相对唇口）
            track[tag][o.name].append((f, p.x, p.y, p.z))

res = {}
for tag, (c, ps, lip) in rigs.items():
    per = []
    for o in ps:
        tr = track[tag][o.name]
        ref = tr[F_SETTLE - 1]
        f_move = next((f for f, x, y, z in tr[F_SETTLE:] if math.hypot(y - ref[2], x - ref[1]) > 1.5), None)
        f_out = next((f for f, x, y, z in tr if y < -1.0), None)
        x_out = next((x - 0 for f, x, y, z in tr if y < 0.5), None)
        settled_in = ref[2] > 0                       # 静置阶段仍在杯内
        per.append(dict(pill=o.name.split('_')[1], settled_inside=settled_in,
                        slide_start_deg=None if f_move is None else round(tilt_at(f_move), 1),
                        exit_deg=None if f_out is None else round(tilt_at(f_out), 1),
                        exit_x_mm=None if x_out is None else round(x_out, 1)))
    outs = [p['exit_deg'] for p in per if p['exit_deg'] is not None]
    slides = [p['slide_start_deg'] for p in per if p['slide_start_deg'] is not None]
    res[tag] = dict(pills=per, n=len(per), n_out=len(outs),
                    remaining_at_70=len(per) - len([a for a in outs if a <= 70.0]),
                    remaining_at_end=len(per) - len(outs),
                    first_slide_deg=min(slides) if slides else None,
                    median_slide_deg=sorted(slides)[len(slides) // 2] if slides else None,
                    first_exit_deg=min(outs) if outs else None,
                    last_exit_deg=max(outs) if outs else None)
res['setup'] = dict(mu=MU, fps=FPS, settle_s=round(F_SETTLE / FPS, 2), tilt_s=round((F_TILT - F_SETTLE) / FPS, 2),
                    tilt_max_deg=TILT_MAX, pivot='front lip outer edge', substeps=rw.substeps_per_frame)
os.makedirs(MOD, exist_ok=True)
open(os.path.join(MOD, 'sim_pour_report.json'), 'w').write(json.dumps(res, ensure_ascii=False, indent=1))
print('SIM_RESULT', json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'pills'} for k, v in res.items()},
                               ensure_ascii=False))

# ---------------- 出图：mm 场景直接打光（能量按 1e6 放大，距离 ×1000）
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.9, 0.905, 0.92, 1); bg.inputs[1].default_value = 0.35
tgt = Vector((GAP_X / 2, 20, 10))


def area(name, off, e, size):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = e * 1e6; d.size = size * 1000
    o = bpy.data.objects.new(name, d); L.link(o); o.location = tgt + Vector(off) * 1000
    L.look_at(o, tgt)


area('key', (-0.20, -0.30, 0.30), 9.0, 0.30)
area('fill', (0.30, -0.15, 0.20), 3.5, 0.26)
area('rim', (0.0, 0.30, 0.30), 4.0, 0.22)
g = L.add_box('Ground', 3000, 3000, 2, (GAP_X / 2, 0, -60), L.mat('g', (0.86, 0.87, 0.89), 0.8))
L.setup_render(res=(1500, 760), samples=48, exposure=-0.2)
d = bpy.data.cameras.new('cam'); d.lens = 55; d.clip_start, d.clip_end = 1, 1e5
cam = bpy.data.objects.new('cam', d); L.link(cam); cam.location = tgt + Vector((150, -330, 170))
L.look_at(cam, tgt); sc.camera = cam
for f in [F_SETTLE] + [F_SETTLE + int(round(120 * a / 70.0)) for a in (32, 47, 70, 95)]:
    sc.frame_set(f)
    L.render_to(os.path.join(OUT, 'sim_pour_f%03d_%02ddeg.png' % (f, int(round(tilt_at(f))))))
print('SIM_DONE')
