# -*- coding: utf-8 -*-
"""IDEA-05B v3 · 取药动画（整机模型 + Bullet 刚体仿真 → PNG 帧，再由 ffmpeg 合成 MP4 / GIF）

    pour   开盖 → 勾手提杯 → 移到接药碟上方 → 绕前唇前倾，药片倒进接药碟
    sweep  不提杯：指腹从杯后往前一抹，药被推上弧底、停在唇台边
    load   批量装药：拨片联动全开 7 盖 → 捏提耳整盘提起 → 盖装药漏斗模板 → 按日撒药，药经漏斗落进各杯

用法：blender -b --factory-startup --python tools/v3/anim_take.py -- pour   （或 sweep / load）
场景整体换成 mm（1 BU = 1 mm，重力 9810 mm/s²）：Bullet 对 mm 级小件在米制下不稳。
"""
import os, sys, math
import bpy, bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parts
import params as P
import lib as L

ROOT = os.path.dirname(os.path.dirname(HERE))
MODE = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'pour'
OUT = os.path.join(ROOT, 'renders', 'v3', 'anim', MODE)
os.makedirs(OUT, exist_ok=True)
FPS = 30
SHOW = 2
CX = P.CELL_CX[SHOW]
LIP = Vector((CX, P.CUP_Y0, P.CUP_Z0 + P.LIP_Z))        # 杯的倒药支点：前唇
HINGE = Vector((CX, P.HINGE_Y, P.HINGE_Z))
MU = 0.4

# ---------------------------------------------------------------- 1) 整机 → mm 场景，变换全部烘焙
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, 'model', 'v3', 'IDEA-05_box_v3.blend'))
sc = bpy.context.scene
if MODE == 'load':
    bpy.context.view_layer.layer_collection.children['Accessory'].exclude = False   # 装药模板
    for o in [o for o in bpy.data.objects if o.name.startswith('Pill_')]:
        bpy.data.objects.remove(o, do_unlink=True)                                  # 空杯开始装
for o in bpy.data.objects:
    if o.name.startswith(('Lid_', 'DriveShaft', 'Paddle')):
        o.rotation_euler = (0, 0, 0)                     # 从闭盖开始
bpy.context.view_layer.update()
S = Matrix.Scale(1000.0, 4)
for o in list(bpy.data.objects):
    if o.type != 'MESH':
        continue
    mw = o.matrix_world.copy()
    if o.data.users > 1:
        o.data = o.data.copy()
    o.parent = None
    o.data.transform(S @ mw)
    o.matrix_world = Matrix.Identity(4)
sc.unit_settings.scale_length = 0.001
sc.render.fps = FPS


def pivot(ob, p):
    """把物体原点挪到 p（网格反向平移），之后可直接对 location / rotation 打关键帧。"""
    ob.data.transform(Matrix.Translation(-p))
    ob.location = p


def key(ob, f, loc=None, rot=None):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert('location', frame=f)
    if rot is not None:
        ob.rotation_euler = rot
        ob.keyframe_insert('rotation_euler', frame=f)


def rigid(ob, kind, shape, kinematic=False, mass=0.0004):
    bpy.context.view_layer.objects.active = ob
    bpy.ops.rigidbody.object_add(type=kind)
    rb = ob.rigid_body
    rb.collision_shape = shape
    rb.friction, rb.restitution = MU, 0.08
    rb.use_margin, rb.collision_margin = True, 0.04
    if kind == 'ACTIVE':
        rb.mass = mass
        rb.use_deactivation = False
        rb.linear_damping, rb.angular_damping = 0.1, 0.25
    else:
        rb.kinematic = kinematic
        if shape == 'MESH':
            rb.mesh_source = 'BASE'


# 7 个日盖都挂到各自的铰链轴上，磁铁 / 干燥片 / 铰链节跟着盖走
lids = []
for i, cx in enumerate(P.CELL_CX):
    h = Vector((cx, P.HINGE_Y, P.HINGE_Z))
    lid_i = bpy.data.objects['Lid_%d' % i]
    pivot(lid_i, h)
    for c in [o for o in bpy.data.objects if o.name in ('Magnet_%d' % i, 'Desiccant_%d' % i, 'DesGrille_%d' % i)
              or o.name.startswith('Hinge_%d_' % i)]:
        pivot(c, h)
        c.location = (0, 0, 0)
        c.parent = lid_i
    lids.append(lid_i)
lid = lids[SHOW]
for n in ('DriveShaft', 'Paddle'):
    pivot(bpy.data.objects[n], Vector((0, P.HINGE_Y, P.HINGE_Z)))
cup = bpy.data.objects['CupV3_%d' % SHOW]
pivot(cup, LIP)
pills = [o for o in bpy.data.objects if o.name.startswith('Pill_')]
# 展示位置的药离唇口太近、落下时会弹出倒嘴：静置前统一挪到杯后半部、逐粒错开高度轻放
for k, o in enumerate(pills):
    c = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    tgt = Vector((CX + (-9, 8, -2, 9, -8)[k], P.CUP_Y0 + (34, 36, 44, 46, 48)[k], c.z + 0.6 + 2.2 * k))
    o.location += tgt - c

bpy.ops.rigidbody.world_add()
rw = sc.rigidbody_world
rw.substeps_per_frame, rw.solver_iterations = 40, 60
sc.gravity = (0, 0, -9810.0)

ground = L.add_box('Ground_rb', 2000, 2000, 10, (CX, 0, -2.1 - 5), L.mat('Table', (0.80, 0.78, 0.75), 0.7))
rigid(ground, 'PASSIVE', 'BOX')
for o in pills:
    rigid(o, 'ACTIVE', 'CONVEX_HULL')

if MODE == 'pour':
    F_END = 170
    # 接药碟（白瓷），放在盒子正前方
    dish = L.add_cyl('Dish', 46, 10, (CX, -66, -2.1 + 5), seg=64, m=L.mat('Porcelain', (0.95, 0.95, 0.93), 0.15))
    L.boolean(dish, L.add_cyl('dc', 43, 10, (CX, -66, -2.1 + 5 + 2), seg=64))
    L.bevel(dish, 0.8, 2, 30)
    rigid(dish, 'PASSIVE', 'MESH')
    rigid(cup, 'PASSIVE', 'MESH', kinematic=True)
    key(lid, 1, rot=(0, 0, 0)); key(lid, 18, rot=(0, 0, 0)); key(lid, 40, rot=(math.radians(-100), 0, 0))
    up = LIP + Vector((0, 0, 38))
    fwd = up + Vector((0, -60, 0))
    key(cup, 1, loc=LIP, rot=(0, 0, 0)); key(cup, 45, loc=LIP)
    key(cup, 70, loc=up); key(cup, 95, loc=fwd, rot=(0, 0, 0))
    key(cup, 135, loc=fwd + Vector((0, 0, -4)), rot=(math.radians(68), 0, 0))
    key(cup, F_END, loc=fwd + Vector((0, 0, -4)), rot=(math.radians(68), 0, 0))
    cam_loc, cam_tgt, lens = Vector((CX + 190, -260, 170)), Vector((CX, -22, 30)), 50
elif MODE == 'load':
    F_END = 230
    # 1) 拨片 → 驱动轴 → 7 盖同时翻开
    for o in lids + [bpy.data.objects['DriveShaft'], bpy.data.objects['Paddle']]:
        key(o, 1, rot=(0, 0, 0)); key(o, 12, rot=(0, 0, 0)); key(o, 42, rot=(math.radians(-100), 0, 0))
    # 2) 捏两端提耳，托盘 + 7 杯 + 密封垫整盘提起；装药模板从上方落到托盘口
    lift = [o for o in bpy.data.objects if o.name.startswith(('TrayV3', 'TrayDay', 'CupV3_', 'Gasket_v3'))]
    tpl = bpy.data.objects['LoadingTemplate']
    up = Vector((0, 0, 55))
    for o in lift:                              # 关键帧相对各自原位（周三杯的原点已挪到前唇）
        b = o.location.copy()
        key(o, 1, loc=b); key(o, 50, loc=b); key(o, 80, loc=b + up)
    key(tpl, 1, loc=Vector((0, 0, 120))); key(tpl, 80, loc=Vector((0, 0, 120))); key(tpl, 100, loc=up)
    tpl.hide_render = True; tpl.keyframe_insert('hide_render', frame=1); tpl.keyframe_insert('hide_render', frame=79)
    tpl.hide_render = False; tpl.keyframe_insert('hide_render', frame=80)
    for c in [o for o in lift if o.name.startswith('CupV3_')] + [tpl]:
        rigid(c, 'PASSIVE', 'MESH', kinematic=True)
    # 3) 按日撒药：每格 3 粒，从漏斗上方落下（落下前是 kinematic，到点切成动态）
    mats = dict(w=L.mat('Tablet', (0.97, 0.97, 0.95), 0.35), o=L.mat('Capsule orange', (0.88, 0.52, 0.24), 0.3),
                i=L.mat('Capsule ivory', (0.94, 0.90, 0.78), 0.28), b=L.mat('Tablet blue', (0.55, 0.70, 0.90), 0.35))
    for i, cx in enumerate(P.CELL_CX):
        f_drop = 110 + i * 12
        for k, (kind, dx, dy) in enumerate((('t', -5, 0), ('c', 6, 4), ('s', 0, -6))):
            loc = (cx + dx, P.TPL['cy'] + dy, P.TPL['z0'] + 55 + 18 + k * 9)
            if kind == 't':
                o = parts.tablet('Drop_%d_%d' % (i, k), mats['w'], 8.0, 3.6, loc)
            elif kind == 'c':
                o = parts.capsule('Drop_%d_%d' % (i, k), mats['o'] if i % 2 else mats['i'], 16.0, 6.0, loc)
                o.rotation_euler = (0.3, 0.2, 0.6)
            else:
                o = parts.tablet('Drop_%d_%d' % (i, k), mats['b'], 6.5, 3.2, loc)
            rigid(o, 'ACTIVE', 'CONVEX_HULL')
            o.rigid_body.kinematic = True
            o.keyframe_insert('rigid_body.kinematic', frame=1)
            o.keyframe_insert('rigid_body.kinematic', frame=f_drop - 1)
            o.rigid_body.kinematic = False
            o.keyframe_insert('rigid_body.kinematic', frame=f_drop)
            o.hide_render = True
            o.keyframe_insert('hide_render', frame=1)
            o.keyframe_insert('hide_render', frame=f_drop - 6)
            o.hide_render = False
            o.keyframe_insert('hide_render', frame=f_drop - 5)
    cam_loc, cam_tgt, lens = Vector((290, -235, 245)), Vector((165, 30, 78)), 46
else:
    F_END = 130
    rigid(cup, 'PASSIVE', 'MESH')
    key(lid, 1, rot=(math.radians(-100), 0, 0))
    # 手指：R7 胶囊，前倾向下 35°；关键帧给的是指尖球心（杯局部 y / 离杯底 z）
    r, Lf = 7.0, 60.0
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=r)
    for v in bm.verts:
        v.co.z += (Lf / 2 - r) * (1 if v.co.z > 0 else -1 if v.co.z < 0 else 0)
    finger = L._finish('Finger', bm, L.mat('Skin', (0.86, 0.66, 0.55), 0.55))
    th = math.radians(125)                                # 局部 +Z 指向前下方 35°
    d = Vector((0, -math.cos(math.radians(35)), -math.sin(math.radians(35))))
    finger.rotation_euler = (th, 0, 0)
    rigid(finger, 'PASSIVE', 'CAPSULE', kinematic=True)

    def tip(y, z):
        c = Vector((CX, P.CUP_Y0 + y, P.CUP_Z0 + z)) - d * (Lf / 2 - r)
        return c
    for f, (y, z) in ((1, (46, 34)), (20, (46, 34)), (40, (46, 11.4)), (95, (17, 10.6)), (108, (13, 11.6)),
                      (F_END, (22, 40))):
        key(finger, f, loc=tip(y, z))
    cam_loc, cam_tgt, lens = Vector((CX + 75, -95, 140)), Vector((CX, 30, 30)), 46

rw.point_cache.frame_start, rw.point_cache.frame_end = 1, F_END
sc.frame_start, sc.frame_end = 1, F_END
bpy.ops.ptcache.bake_all(bake=True)
print('BAKED', MODE)
if MODE == 'load':                              # 核对：每粒药最后落在哪一格的杯里
    sc.frame_set(F_END)
    ok, bad = 0, []
    for o in [o for o in bpy.data.objects if o.name.startswith('Drop_')]:
        i = int(o.name.split('_')[1]); p = o.matrix_world.translation
        cell = min(range(P.CELL_N), key=lambda j: abs(P.CELL_CX[j] - p.x))
        inside = abs(p.x - P.CELL_CX[i]) < P.CUP_W / 2 - 1.6 and P.CUP_Y0 < p.y < P.CUP_Y0 + P.CUP_D \
            and P.CUP_Z0 + 55 < p.z < P.CUP_Z0 + 55 + P.CUP_H
        ok += inside and cell == i
        if not (inside and cell == i):
            bad.append((o.name, round(p.x, 1), round(p.y, 1), round(p.z, 1)))
    print('LOAD_CHECK in_own_cup=%d/21 bad=%s' % (ok, bad))
if MODE == 'pour':
    sc.frame_set(F_END)
    dish_c = Vector((CX, -66))
    n_in = sum((Vector((o.matrix_world.translation.x, o.matrix_world.translation.y)) - dish_c).length < 43
               for o in pills)
    print('POUR_CHECK in_dish=%d/%d' % (n_in, len(pills)))

# ---------------------------------------------------------------- 2) 灯光 / 相机（mm 场景：能量 ×1e6、尺寸 ×1000）
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes.get('Background')
bgn.inputs[0].default_value = (0.78, 0.77, 0.75, 1); bgn.inputs[1].default_value = 0.35
tgt = cam_tgt


def area(name, off, e, size):
    dl = bpy.data.lights.new(name, 'AREA'); dl.energy = e * 1e6; dl.size = size * 1000
    o = bpy.data.objects.new(name, dl); sc.collection.objects.link(o)
    o.location = tgt + Vector(off) * 1000
    L.look_at(o, tgt)


area('key', (0.35, -0.35, 0.45), 40, 0.5)
area('fill', (-0.40, -0.30, 0.25), 12, 0.7)
area('rim', (-0.05, 0.55, 0.40), 22, 0.35)
area('top', (0.0, 0.05, 0.80), 8, 0.6)
cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_start, cd.clip_end = 1, 1e5
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam)
cam.location = cam_loc; L.look_at(cam, cam_tgt); sc.camera = cam
L.setup_render(res=(960, 720), samples=32, exposure=-0.9)
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = os.path.join(OUT, 'f_')
bpy.ops.render.render(animation=True)
print('ANIM_DONE', MODE, F_END)
