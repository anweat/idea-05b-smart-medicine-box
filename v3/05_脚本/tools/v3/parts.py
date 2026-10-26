# -*- coding: utf-8 -*-
"""IDEA-05B · 取药结构 v3 零件（mm 场景建模；几何工具复用 tools/v2/lib.py）"""
import os, sys, math
import bmesh, bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'v2'))
sys.path.insert(0, HERE)
import lib as L
import params as P


# ---------------------------------------------------------------- 2D / 挤出 / 放样
def round_poly(pts, radii, seg=6):
    """凸多边形逐角倒圆；radii 为单值或与 pts 等长的列表。"""
    n = len(pts)
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * n
    out = []
    for i in range(n):
        p = Vector(pts[i]); a = Vector(pts[i - 1]); b = Vector(pts[(i + 1) % n])
        r = radii[i]
        if r <= 0:
            out.append((p.x, p.y)); continue
        u = (a - p).normalized(); v = (b - p).normalized()
        th = u.angle(v) / 2.0
        d = min(r / math.tan(th), (a - p).length * 0.49, (b - p).length * 0.49)
        r = d * math.tan(th)
        t1 = p + u * d; t2 = p + v * d
        c = p + (u + v).normalized() * (r / math.sin(th))
        a1 = math.atan2(t1.y - c.y, t1.x - c.x); a2 = math.atan2(t2.y - c.y, t2.x - c.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(seg + 1):
            t = a1 + da * k / seg
            out.append((c.x + r * math.cos(t), c.y + r * math.sin(t)))
    return out


def rr(w, d, r, cx=0.0, cy=0.0, seg=6):
    h, k = w / 2, d / 2
    return [(x + cx, y + cy) for x, y in round_poly([(-h, -k), (h, -k), (h, k), (-h, k)], r, seg)]


def loft(name, rings, m=None):
    """rings = [(pts_xy, z), ...]，点数一致，自下而上；两端封口。"""
    bm = bmesh.new()
    layers = [[bm.verts.new((x, y, z)) for x, y in pts] for pts, z in rings]
    n = len(layers[0])
    bm.faces.new(list(reversed(layers[0])))
    bm.faces.new(layers[-1])
    for A, B in zip(layers, layers[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((A[i], A[j], B[j], B[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return L._finish(name, bm, m)


def prism_z(name, pts, z0, z1, m=None):
    return loft(name, [(pts, z0), (pts, z1)], m)


def corner_tri(name, corner, sx, sy, leg, z0, z1, over=1.0, m=None):
    """直角三角棱柱：直角在 corner，沿 (sx,0)/(0,sy) 方向各 leg；向外多伸 over 保证布尔穿透。"""
    cx, cy = corner
    # 斜边过 (cx+sx*leg, cy) 与 (cx, cy+sy*leg)；三个顶点都向外推 over，保证穿透
    a = (cx - sx * over, cy - sy * over)
    b = (cx + sx * (leg + over), cy - sy * over)
    c = (cx - sx * over, cy + sy * (leg + over))
    pts = [a, b, c]
    # 保证逆时针
    area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if area < 0:
        pts = [a, c, b]
    return prism_z(name, pts, z0, z1, m)


def clean(ob, dist=5e-3):
    """布尔后清理：合并重点 + 消除零面积三角（EXACT 布尔偶尔在共线处留下退化面）。"""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bnd = [e for e in bm.edges if len(e.link_faces) == 1]
    if bnd:
        bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return ob


# ---------------------------------------------------------------- 材质
def materials():
    return dict(
        cup=L.mat('PP translucent', (0.74, 0.86, 0.92), 0.32, transmission=0.25),
        tray=L.mat('PP tray', (0.86, 0.85, 0.82), 0.5),
        lid=L.mat('PC smoked', (0.36, 0.39, 0.42), 0.08, alpha=0.42),
        shell=L.mat('ABS warm white', (0.905, 0.885, 0.845), 0.40),
        section=L.mat('Section', (0.95, 0.45, 0.12), 0.6),
        pill_w=L.mat('Tablet', (0.97, 0.97, 0.95), 0.35),
        pill_o=L.mat('Capsule orange', (0.88, 0.52, 0.24), 0.30),
        pill_i=L.mat('Capsule ivory', (0.94, 0.90, 0.78), 0.28),
        win=L.mat('Window', (0.55, 0.78, 0.90), 0.2),
    )


# ---------------------------------------------------------------- 药杯 CupV3
def cup_floor_profile():
    """YZ 剖面（杯局部）：唇口平台 → ③ 硬币杯弧底 → 聚药沟 → 缓坡到后端；上沿高出杯口。"""
    R, lo = P.COVE_R, P.FLOOR_LOW_Z
    rise = P.LIP_Z - lo
    y_lip = P.GULLY_Y - math.sqrt(R * R - (R - rise) ** 2)
    pts = [(-3.0, P.LIP_Z), (y_lip, P.LIP_Z)]
    cy, cz = P.GULLY_Y, lo + R
    a0 = math.atan2(P.LIP_Z - cz, y_lip - cy)
    a1 = -math.pi / 2
    for k in range(1, 13):
        t = a0 + (a1 - a0) * k / 12
        pts.append((cy + R * math.cos(t), cz + R * math.sin(t)))
    pts.append((P.CUP_D + 2.0, P.FLOOR_BACK_Z + (P.CUP_D + 2.0 - P.GULLY_Y) *
                (P.FLOOR_BACK_Z - lo) / (P.CUP_D - P.CUP_WALL - P.GULLY_Y)))
    pts.append((P.CUP_D + 2.0, P.CUP_H + 3.0))
    pts.append((-3.0, P.CUP_H + 3.0))
    return pts, y_lip


def cup_plan():
    """俯视内腔：后段直壁 + ② 前段收拢到倒嘴宽（向前穿出前壁 = 倒嘴）。"""
    hw = P.CUP_W / 2 - P.CUP_WALL
    sw = P.SPOUT_W / 2
    yf = P.CUP_WALL + P.FUNNEL_LEN
    yb = P.CUP_D - P.CUP_WALL
    # 倒嘴先以 24 宽直通前壁，再张开：避免斜壁与前壁夹出楔形薄边
    pts = [(-sw, -3.0), (sw, -3.0), (sw, P.CUP_WALL), (hw, yf), (hw, yb), (-hw, yb), (-hw, yf), (-sw, P.CUP_WALL)]
    radii = [0.0, 0.0, 1.5, P.INNER_R_FRONT, P.INNER_R_BACK, P.INNER_R_BACK, P.INNER_R_FRONT, 1.5]
    return round_poly(pts, radii, seg=8)


def cup(name, mats, cx=0.0, place=True):
    W, D, H = P.CUP_W, P.CUP_D, P.CUP_H
    body = prism_z(name, rr(W, D, P.CUP_R, 0, D / 2), 0.0, H, mats['cup'])
    L.bevel(body, 0.6, 2, 32)
    # ④ 后左角切角
    L.boolean(body, corner_tri('key', (-W / 2, D), 1, -1, P.CUP_KEY, -1, H + 1))
    # 内腔 = YZ 底面剖面 ∩ 俯视收拢轮廓
    prof, _ = cup_floor_profile()
    cav = L.add_prism_x('cav', prof, -W, W)
    plan = prism_z('plan', cup_plan(), -1.0, H + 4.0)
    L.boolean(cav, plan, 'INTERSECT')
    L.boolean(body, cav)
    # 杯底取芯（均匀壁厚）
    L.boolean(body, prism_z('core', rr(W - 2 * P.CORE_INSET, D - 2 * P.CORE_INSET, 1.5, 0, D / 2),
                            -1.0, P.CORE_TOP))
    # ① 后侧 T 形勾手（和后壁一体）
    # 勾手 = 一个 L 形截面沿 X 挤出（腹板+翼板一次成形，不做两次布尔）
    # 背面比杯后壁内缩 0.3、腹板内面比内壁凸出 0.8：与杯体两侧都不共面
    yb, yi = D - 0.3, D - P.CUP_WALL - 0.8
    zt, zb = H + P.HANDLE_H, H - 1.2
    prof_h = [(yb, zb), (yb, zt), (yi - P.HANDLE_FLANGE, zt), (yi - P.HANDLE_FLANGE, zt - P.HANDLE_T),
              (yi, zt - P.HANDLE_T), (yi, zb)]
    # 圆角直接做在 2D 截面上（凸角 R0.6、内角 R0.8）；对带凹角的实体用倒角修改器会自交
    prof_h = round_poly(prof_h, [0.0, 0.6, 0.6, 0.6, 0.8, 0.0], seg=4)
    web = L.add_prism_x('handle', prof_h, -P.HANDLE_W / 2, P.HANDLE_W / 2)
    L.boolean(body, web, 'UNION')
    clean(body)
    L.assign(body, mats['cup'])
    bpy.ops.object.select_all(action='DESELECT')
    for p in body.data.polygons:
        p.use_smooth = False
    if place:
        L.offset_mesh(body, cx, P.CUP_Y0, P.CUP_Z0)
    return body


# ---------------------------------------------------------------- 托盘 TrayV3
def tray(mats, n=P.CELL_N):
    x0 = P.TRAY_X0 if n == P.CELL_N else P.CELL_CX[0] - P.PITCH / 2
    w = P.TRAY_W if n == P.CELL_N else P.PITCH
    cxs = P.CELL_CX[:n]
    t = prism_z('TrayV3', rr(w, P.TRAY_D, P.TRAY_R if n == P.CELL_N else 0.01, x0 + w / 2, P.TRAY_CY),
                P.TRAY_Z0, P.TRAY_Z1, mats['tray'])
    L.bevel(t, 0.9, 2, 32)
    zf = P.TRAY_Z0 + P.TRAY_FLOOR
    zl = P.TRAY_Z1 - P.LEADIN_DZ
    over = 0.6
    k = (P.LEADIN_DZ + over) / P.LEADIN_DZ
    for cx in cxs:
        base = rr(P.POCKET_W, P.POCKET_D, P.POCKET_R, cx, P.POCKET_CY, seg=6)
        top = rr(P.POCKET_W + 2 * P.LEADIN_X * k, P.POCKET_D + 2 * P.LEADIN_Y * k,
                 P.POCKET_R + P.LEADIN_X * k, cx, P.POCKET_CY, seg=6)
        L.boolean(t, loft('pk', [(base, zf), (base, zl), (top, P.TRAY_Z1 + over)]))
        # 通光孔
        L.boolean(t, L.add_box('lh', P.LIGHT_W, P.LIGHT_D, 6, (cx, P.POCKET_CY, P.TRAY_Z0)))
    for cx in cxs:
        # ④ 防呆角填块（杯位后左角）
        corner = (cx - P.POCKET_W / 2, P.POCKET_CY + P.POCKET_D / 2)
        L.boolean(t, corner_tri('kf', corner, 1, -1, P.KEY_LEG_TRAY, zf - 0.5, zl), 'UNION')
        # 隔光墙（托盘底下两侧）
        for s in (-1, 1):
            xb = cx + s * (P.LIGHT_W / 2 + 1.0 + P.BAFFLE_T / 2)
            L.boolean(t, L.add_box('bf', P.BAFFLE_T, P.BAFFLE_L, P.BAFFLE_H + 0.4,
                                   (xb, P.POCKET_CY, P.TRAY_Z0 - P.BAFFLE_H / 2 + 0.2)), 'UNION')
    if n == P.CELL_N:
        # 三点运动学定位脚：托盘底 3 个 R3 半球（只留地板以下部分，不顶进杯位）
        for (bx, by) in P.KIN.values():
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=P.BALL_R)
            for v in bm.verts:
                v.co.x += bx; v.co.y += by; v.co.z += P.TRAY_Z0
            ball = L._finish('ball', bm, None)
            L.boolean(ball, L.add_box('bc', 10, 10, 6, (bx, by, P.TRAY_Z0 + 1.0 - 3.0)), 'INTERSECT')
            L.boolean(t, ball, 'UNION')
        # 端部提耳（烤盘耳）：全开后双手捏两耳整盘提出
        for s, xe in ((-1, P.TRAY_X0), (1, P.TRAY_X0 + P.TRAY_W)):
            ear = L.add_box('ear', P.EAR['x_out'] + 0.6, P.EAR['y'][1] - P.EAR['y'][0], P.EAR['z'][1] - P.EAR['z'][0],
                            (xe + s * (P.EAR['x_out'] - 0.6) / 2, sum(P.EAR['y']) / 2, sum(P.EAR['z']) / 2))
            L.bevel(ear, 0.8, 2, 32)
            L.boolean(t, ear, 'UNION')
    L.assign(t, mats['tray'])
    return t


# ---------------------------------------------------------------- 日盖（外形=原设计，下开口腔体）
def lid(name, mats, cx):
    # 先多做 3 mm 再切掉：外倒角只留在顶边，下沿不成刀口
    o = prism_z(name, rr(P.LID_W, P.LID_D, P.LID_R, 0, -P.LID_D / 2), -3.0, P.LID_H, mats['lid'])
    L.bevel(o, 2.0, 3, 32)
    L.boolean(o, L.add_box('lb', P.LID_W + 4, P.LID_D + 4, 4.0, (0, -P.LID_D / 2, -2.0)))
    L.boolean(o, prism_z('lc', rr(P.LID_CAV_W, P.LID_CAV_D, P.LID_CAV_R, 0, -P.LID_D / 2),
                         -1.0, P.LID_H - P.LID_TOP_T))
    o.location = (cx, P.HINGE_Y, P.HINGE_Z)
    return o


def set_lid_angle(o, deg):
    o.rotation_euler = (math.radians(-deg), 0, 0)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- 药片（展示 / 仿真）
def tablet(name, m, d=8.0, h=3.6, loc=(0, 0, 0)):
    o = L.add_cyl(name, d / 2, h, (0, 0, 0), seg=32, m=m)
    L.bevel(o, h * 0.32, 3, 30)
    o.location = loc
    return o


def capsule(name, m, L_=18.0, d=6.4, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=d / 2)
    half = (L_ - d) / 2
    for v in bm.verts:
        v.co.y += half if v.co.y > 0 else -half if v.co.y < 0 else 0
    o = L._finish(name, bm, m)
    o.location = loc
    return o
