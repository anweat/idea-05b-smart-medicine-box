# -*- coding: utf-8 -*-
"""IDEA-05B · 整机 v3：在原设计模型（外观基线）里换装 v3 取药结构 + 称重浮动架 + 传感器
读 model/IDEA-05_box.blend（米制）→ 删旧托盘/杯/7 圈密封/旧称重片/底座干燥剂
→ 新零件在 mm 下建好再缩到米 → 整机校验 → 存 model/v3/IDEA-05_box_v3.blend + GLB（开盖/闭盖）
用法：blender -b --factory-startup --python tools/v3/build_full.py
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
ROOT = os.path.dirname(os.path.dirname(HERE))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, 'model', 'IDEA-05_box.blend'))
import parts
import chassis
import loading
import params as P
import lib as L

MOD = os.path.join(ROOT, 'model', 'v3')
MM = 0.001
SHOW = 2                                    # 周三：开盖展示格
LID_SHOW_DEG = 100.0

# ---------------------------------------------------------------- 材质（沿用原模型材质，外观一致）
def M(name, color=None, rough=0.5, **kw):
    m = bpy.data.materials.get(name)
    return m if m is not None else L.mat(name, color, rough, **kw)


MAT = dict(cup=M('PP translucent'), tray=M('PP tray'), al=M('Aluminium'), inner=M('ABS inner'),
           white=M('ABS warm white'), dark=M('Dark plastic'), tpe=M('TPE foot'), sil=M('Silicone'),
           led=M('LED dim'), led_on=M('LED warm'), gold=M('Gold'),
           gel=M('Silica gel', (0.86, 0.91, 0.95), 0.6),
           pill_w=M('Tablet', (0.97, 0.97, 0.95), 0.35), pill_o=M('Capsule orange'), pill_i=M('Capsule ivory'))
# parts.materials() 的键名映射到原材质
PM = dict(cup=MAT['cup'], tray=MAT['tray'], pill_w=MAT['pill_w'], pill_o=MAT['pill_o'], pill_i=MAT['pill_i'],
          lid=M('PC smoked'), shell=MAT['white'], section=M('Section', (0.95, 0.45, 0.12), 0.6), win=MAT['led'])


def to_m(ob, mat=None):
    """mm 网格 → 米：烘焙变换再整体缩放。"""
    bpy.context.view_layer.update()
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)
    ob.data.transform(Matrix.Scale(MM, 4))
    ob.data.update()
    if mat is not None:
        L.assign(ob, mat)
    return ob


def clamp_y(ob, y0, y1):
    """把盒状件在 Y 向裁短（世界坐标 mm）。"""
    mw, inv = ob.matrix_world, ob.matrix_world.inverted()
    for v in ob.data.vertices:
        w = mw @ v.co
        w.y = min(max(w.y, y0 * MM), y1 * MM)
        v.co = inv @ w
    ob.data.update()


# ---------------------------------------------------------------- 1) 删旧件
old = [o for o in bpy.data.objects if o.name == 'Tray' or o.name.startswith(('Cup_', 'CupWin_', 'Pill', 'Gasket'))
       or o.name in ('GuideDisk', 'LoadCell', 'Desiccant', 'HingeRail')]   # 铰链装饰条换成驱动轴（联动全开）
removed = sorted(o.name for o in old)
for o in old:
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- 2) 让位：传感板 / 主板 / 电池
sp = bpy.data.objects['SensorPlate']
sp.data.transform(sp.matrix_world); sp.matrix_world = Matrix.Identity(4)
for v in sp.data.vertices:
    v.co.x = min(max(v.co.x, 20 * MM), 300 * MM)
clamp_y(sp, 16.0, 54.0)
clamp_y(bpy.data.objects['PCB'], 10.0, 53.0)
clamp_y(bpy.data.objects['Battery'], 9.0, 53.0)

# ---------------------------------------------------------------- 3) 日盖：下开口内腔（给勾手让位）+ 磁铁 + 干燥片
lids = [bpy.data.objects['Lid_%d' % i] for i in range(P.CELL_N)]
pads, grills = chassis.desiccant(MAT['gel'], MAT['tray'])
halls, mags = chassis.hall_and_magnets(MAT['dark'], MAT['al'])
for i, lid in enumerate(lids):
    lid.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    cut = parts.prism_z('lc', parts.rr(P.LID_CAV_W, P.LID_CAV_D, P.LID_CAV_R, 0, -P.LID_D / 2),
                        -1.0, P.LID_H - P.LID_TOP_T)
    cut.data.transform(Matrix.Scale(MM, 4))
    cut.matrix_world = lid.matrix_world.copy()
    L.boolean(lid, cut)
    for ob in (pads[i], grills[i]):          # 干燥片在日盖局部坐标里建的
        ob.data.transform(Matrix.Scale(MM, 4))
        ob.parent = lid
        ob.matrix_parent_inverse = Matrix.Identity(4)
    mg = to_m(mags[i])                        # 磁铁按闭盖世界坐标建 → 转成日盖局部再挂上
    mg.data.transform(lid.matrix_world.inverted())
    mg.parent = lid
    mg.matrix_parent_inverse = Matrix.Identity(4)

# ---------------------------------------------------------------- 4) 新件
tray = to_m(parts.tray(PM), MAT['tray'])
cups = [to_m(parts.cup('CupV3_%d' % i, PM, cx), MAT['cup']) for i, cx in enumerate(P.CELL_CX)]
carrier = to_m(chassis.carrier(MAT['al']))
lc = [to_m(o) for o in chassis.load_cell(MAT['al'], MAT['gold'], MAT['inner'])]
stops = [to_m(o) for o in chassis.stops(MAT['tpe'])]
for k, s in enumerate(stops):
    s.name = 'Stop_%d' % k
spine = to_m(chassis.spine(MAT['white']))
halls = [to_m(o) for o in halls]
irs = [to_m(o) for o in chassis.ir_parts(MAT['led'], MAT['dark'], MAT['led_on'], today=SHOW)]
gasket = to_m(chassis.gasket(MAT['sil']))
# 联动全开：驱动轴 + 拨爪、铰链节开通孔 + 空程槽并挂到各自日盖上、右端拨片
shaft = to_m(loading.drive_shaft(MAT['al']))
shaft.location = (0, P.HINGE_Y * MM, P.HINGE_Z * MM)        # to_m 会烘焙变换，原点重新放回铰链轴
shaft.data.transform(Matrix.Translation((0, -P.HINGE_Y * MM, -P.HINGE_Z * MM)))
for x, cut in loading.knuckle_cutters():
    k = min((o for o in bpy.data.objects if o.name.startswith('Hinge_')),
            key=lambda o: abs(o.matrix_world.translation.x * 1000 - x))
    to_m(cut)
    L.boolean(k, cut)
    i = int(k.name.split('_')[1])
    mw = k.matrix_world.copy(); k.parent = lids[i]; k.matrix_world = mw
paddle = to_m(loading.paddle(MAT['white']))
paddle.data.transform(Matrix.Translation((0, -P.HINGE_Y * MM, -P.HINGE_Z * MM)))
paddle.location = (0, P.HINGE_Y * MM, P.HINGE_Z * MM)
knuckles = [o for o in bpy.data.objects if o.name.startswith('Hinge_')]


def gang(deg, lids_too=True):
    """联动：轴、拨片（和日盖）一起转 deg（开盖方向为负）。"""
    for o in [shaft, paddle] + (lids if lids_too else []):
        o.rotation_euler = (math.radians(-deg), 0, 0)
    bpy.context.view_layer.update()


tpl = to_m(loading.template(M('PP template', (0.52, 0.80, 0.76), 0.35, transmission=0.3)))
# 周三杯里的药（展示用）
cx = P.CELL_CX[SHOW]
pills = []
for k, (kind, x, y, z, rz) in enumerate([('t', -6, 12, 3.2, 0), ('t', 4, 11, 3.2, 0), ('c', 7, 26, 3.9, 20),
                                         ('o', -8, 28, 4.2, -30), ('c', -1, 40, 4.4, 80)]):
    loc = (cx + x, P.CUP_Y0 + y, P.CUP_Z0 + z + 1.9)
    if kind == 't':
        o = parts.tablet('Pill_%d' % k, MAT['pill_w'], 8.0, 3.6, loc)
    elif kind == 'o':
        o = parts.capsule('Pill_%d' % k, MAT['pill_w'], 13.0, 6.5, loc); o.scale = (1, 1, 0.65)
    else:
        o = parts.capsule('Pill_%d' % k, MAT['pill_o'] if k == 2 else MAT['pill_i'], 18.0, 6.4, loc)
    o.rotation_euler = (0, 0, math.radians(rz))
    pills.append(to_m(o))

# ---------------------------------------------------------------- 5) 整机校验（mm）
def bvh(ob):
    return BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())


def gap(a, b):
    """双向顶点→表面最近距离（mm）。"""
    best = 1e9
    for x, y in ((a, b), (b, a)):
        t = bvh(y); mw = x.matrix_world; inv = y.matrix_world.inverted()
        for v in x.data.vertices:
            h = t.find_nearest(inv @ (mw @ v.co))
            if h[0] is not None:
                best = min(best, h[3])
    return round(best * 1000, 3)


def inter(a, b):
    return round(L.interference_volume(a, b) * 1e9, 3)


def tri_hits(a, b):
    """两件三角面相交对数（世界坐标 BVH overlap）。不要求网格水密——原日盖网格不水密，
    精确布尔求交会漏报，涉及日盖的检查都用这个。"""
    def tree(o):
        o.data.calc_loop_triangles()
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        return BVHTree.FromPolygons(vs, [t.vertices[:] for t in o.data.loop_triangles])
    return len(tree(a).overlap(tree(b)))


def bb(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [min(c[i] for c in cs) for i in range(3)], [max(c[i] for c in cs) for i in range(3)]


def bb_overlap(a, b, pad=0.0005):
    (a0, a1), (b0, b1) = bb(a), bb(b)
    return all(a0[i] - pad < b1[i] and b0[i] - pad < a1[i] for i in range(3))


base = bpy.data.objects['BaseShell']
qa = dict(removed=removed)
# 称重隔离：托盘只碰浮动架；浮动架只碰传感器垫块
qa['weigh_chain'] = dict(
    tray_to_carrier_gap=gap(tray, carrier), tray_x_carrier_mm3=inter(tray, carrier),
    tray_to_base_gap=gap(tray, base), tray_to_spine_gap=gap(tray, spine), tray_to_shaft_gap=gap(tray, shaft), tray_to_paddle_gap=gap(tray, paddle),
    tray_to_sensorplate_gap=gap(tray, sp),
    carrier_to_base_gap=gap(carrier, base), carrier_to_sensorplate_gap=gap(carrier, sp),
    carrier_to_stops_gap=min(gap(carrier, s) for s in stops),
    carrier_to_loadcell_fixed_end_gap=gap(carrier, lc[0]),
    spacer_to_carrier_gap=gap(lc[3], carrier), spacer_to_loadcell_gap=gap(lc[3], lc[0]),
    boss_to_loadcell_gap=gap(lc[2], lc[0]))
# 日盖开合扫掠（原日盖网格，已开腔）
sweep = {}
for ang in (0, 30, 60, 90, 105):
    lids[0].rotation_euler = (math.radians(-ang), 0, 0)
    bpy.context.view_layer.update()
    sweep[str(ang)] = dict(cup=tri_hits(lids[0], cups[0]), tray=tri_hits(lids[0], tray), spine=tri_hits(lids[0], spine))
lids[0].rotation_euler = (0, 0, 0)
qa['lid_sweep_tri_hits'] = sweep
qa['handle_to_lid_gap'] = gap(cups[0], lids[0])
# 联动全开：轴 + 拨片 + 7 盖一起转 0→100°；拨片不碰托盘(含提耳) / 底座 / 铰链脊 / 末格日盖，拨爪不碰铰链节
link = []
for ang in range(0, 101, 10):
    gang(ang)
    link.append(dict(deg=ang, paddle_x_tray=tri_hits(paddle, tray), paddle_x_base=tri_hits(paddle, base),
                     paddle_x_spine=tri_hits(paddle, spine), paddle_x_lid6=tri_hits(paddle, lids[6]),
                     shaft_x_knuckles=sum(tri_hits(shaft, k) for k in knuckles),
                     lids_x_cups=sum(tri_hits(l, c) for l, c in zip(lids, cups)),
                     lids_x_spine=sum(tri_hits(l, spine) for l in lids)))
gang(0)
qa['gang_open'] = dict(table=link, all_zero=all(v == 0 for r in link for k, v in r.items() if k != 'deg'))
# 单独开一格（轴不动）：铰链节在空程槽里转，拨爪不挡
qa['single_lid_shaft_tri'] = {}
for ang in (30, 60, 100):
    lids[0].rotation_euler = (math.radians(-ang), 0, 0); bpy.context.view_layer.update()
    qa['single_lid_shaft_tri'][str(ang)] = sum(tri_hits(shaft, k) for k in knuckles if k.parent is lids[0])
lids[0].rotation_euler = (0, 0, 0)
# 装药模板落在托盘口上（7 盖全开）：不碰杯 / 勾手 / 日盖 / 铰链脊
for l in lids:
    l.rotation_euler = (math.radians(-100), 0, 0)
bpy.context.view_layer.update()
qa['template'] = dict(x_cups_mm3=max(inter(tpl, c) for c in cups), x_lids_tri=max(tri_hits(tpl, l) for l in lids),
                      x_spine_mm3=inter(tpl, spine), x_tray_mm3=inter(tpl, tray), to_tray_gap=gap(tpl, tray),
                      to_handle_gap=min(gap(tpl, c) for c in cups[:2]))
for l in lids:
    l.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
# 全量两两干涉（新/改件之间 + 新件对原件），白名单 = 设计上就接触的件
new = [tray, carrier, spine, gasket, shaft, paddle] + cups + lc + stops + halls + irs
others = [o for o in bpy.data.objects if o.type == 'MESH' and o not in new and o not in pills
          and o.parent is None and not o.name.startswith(('Floor', 'Backdrop'))]
allowed = {('TrayV3', 'Carrier'), ('LC_Spacer', 'Carrier'), ('LC_Spacer', 'LoadCell'), ('LC_Boss', 'LoadCell'),
           ('LC_Boss', 'BaseShell'), ('StrainGauge', 'LoadCell'), ('Gasket_v3', 'TrayV3'), ('HingeSpine', 'BaseShell'),
           ('DriveShaft', 'Paddle')}
allowed |= {(b, a) for a, b in allowed}
hits = []
pool = new + others
checked = 0
for i, a in enumerate(new):
    for b in pool:
        if b is a or (b in new and new.index(b) <= i):
            continue
        na, nb = a.name.split('.')[0], b.name.split('.')[0]
        if (na, nb) in allowed or (na.startswith('Stop') and nb == 'BaseShell') or (nb.startswith('Stop') and na == 'BaseShell'):
            continue
        if na.startswith(('Hall_', 'LED_', 'IR_')) and nb in ('HingeSpine', 'SensorPlate'):
            continue
        if nb.startswith(('Hall_', 'LED_', 'IR_')) and na in ('HingeSpine', 'SensorPlate'):
            continue
        if na.startswith('Gasket') or nb.startswith('Gasket') or nb.startswith(('Lid_', 'Hinge_', 'LoadingTemplate')):
            continue
        if not bb_overlap(a, b):
            continue
        checked += 1
        v = inter(a, b)
        if v > 0.01:
            hits.append([na, nb, v])
qa['pairwise_checked'] = checked
qa['pairwise_hits_mm3'] = hits
qa['cup_x_tray_mm3'] = [inter(c, tray) for c in cups]
qa['cup_x_lid_closed_tri'] = [tri_hits(c, l) for c, l in zip(cups, lids)]
qa['parts'] = {o.name: {k: v for k, v in L.stats(o).items() if k in ('watertight', 'shells', 'bbox_mm', 'volume_mm3')}
               for o in [tray, cups[0], carrier, spine, gasket, lc[0], shaft, paddle, tpl]}
print('FULL_QA', json.dumps(qa, ensure_ascii=False))
json.dump(qa, open(os.path.join(MOD, 'full_qa.json'), 'w'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- 6) 保存 + GLB
for o in list(bpy.data.objects):
    if o.type in ('CAMERA', 'LIGHT') or o.name.startswith('QA_'):
        bpy.data.objects.remove(o, do_unlink=True)
# 装药模板是配件：单独导出，并放进不参与视图层的集合（整机 GLB / 默认渲染里不出现）
L.export_stl(os.path.join(ROOT, 'stl', 'v3_装药漏斗模板.stl'), [tpl])
acc = bpy.data.collections.new('Accessory'); bpy.context.scene.collection.children.link(acc)
for c in list(tpl.users_collection):
    c.objects.unlink(tpl)
acc.objects.link(tpl)
bpy.context.view_layer.layer_collection.children['Accessory'].exclude = True
L.export_glb(os.path.join(MOD, 'IDEA-05_box_v3_closed.glb'))
lids[SHOW].rotation_euler = (math.radians(-LID_SHOW_DEG), 0, 0)
bpy.context.view_layer.update()
L.export_glb(os.path.join(MOD, 'IDEA-05_box_v3.glb'))
L.save_blend(os.path.join(MOD, 'IDEA-05_box_v3.blend'))
print('FULL_DONE')
