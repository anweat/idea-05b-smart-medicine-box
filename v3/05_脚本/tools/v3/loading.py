# -*- coding: utf-8 -*-
"""IDEA-05B 整机 v3 · 批量装药零件（mm 场景建模，坐标同 params.py）

同轴空程联动全开：7 个日盖共用的铰链销做成驱动轴，每个铰链节里一只拨爪 + 一段空程槽。
  - 拨右端拨片 → 轴转 100° → 拨爪推着 7 盖同时翻开；拨回去，盖靠自重 + 阻尼跟着合上；
  - 单独开一格：盖带着铰链节在空程槽里自由转，轴不动（单向拨爪 / 空程联轴）。
  - 全部机构与日盖同轴，不扫过任何别的零件。
装药漏斗模板：7 个漏斗对准 7 只杯，漏斗口避开杯后勾手；放在托盘口上，药从漏斗滑进杯。
"""
import math
import params as P
import parts
import lib as L

AX = (P.HINGE_Y, P.HINGE_Z)


def _arc(r, a0, a1, n=24):
    """绕铰链轴的圆弧点（(y,z) 平面）；角度从 +y 量起，逆时针为正（度）。"""
    return [(AX[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             AX[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def knuckle_xs():
    return [cx + d for cx in P.CELL_CX for d in (-16, 16)]


def drive_shaft(m):
    """驱动轴 + 14 只拨爪（静止时朝下）。原点放在铰链轴上，绕 X 转即可。"""
    x0, x1 = P.SPINE['x'][0] - 1.0, P.PADDLE['x'][1]
    sh = L.add_cyl('DriveShaft', P.PIN_R, x1 - x0, ((x0 + x1) / 2, AX[0], AX[1]), axis='X', seg=24, m=m)
    r0, r1 = P.DOG['r']
    for x in knuckle_xs():
        L.boolean(sh, L.add_box('dog', 1.6, P.DOG['t'], r1 - r0 + 0.1, (x, AX[0], AX[1] - (r0 + r1) / 2 + 0.05)), 'UNION')
    L.assign(sh, m)
    L.offset_mesh(sh, 0, -AX[0], -AX[1])
    sh.location = (0, AX[0], AX[1])
    return sh


def knuckle_cutters():
    """每个铰链节：通孔（轴） + 中段空程槽。槽的下边是与拨爪侧面平行的平面（拨爪推它），上边留足 100° 空程。"""
    out = []
    a1 = P.NOTCH['deg'][1]
    half = P.DOG['t'] / 2 + 0.05
    for x in knuckle_xs():
        bore = L.add_cyl('bore', P.PIN_R + 0.05, 6.0, (x, AX[0], AX[1]), axis='X', seg=24)
        r = P.NOTCH['r']
        a_low = math.degrees(math.atan2(-math.sqrt(r * r - half * half), -half))   # 下边平面与圆弧的交点
        prof = [(AX[0] - half, AX[1])] + _arc(r, a_low, a1) + [AX]
        notch = L.add_prism_x('notch', prof, x - 1.0, x + 1.0)
        L.boolean(bore, notch, 'UNION')
        out.append((x, bore))
    return out


def paddle(m):
    """右端「全开」拨片：轴毂 + 摆臂 + 指垫，静止时朝前下方；原点在铰链轴上。"""
    p = P.PADDLE
    x0, x1 = p['x']
    xc, w = (x0 + x1) / 2, x1 - x0
    hub = L.add_cyl('Paddle', p['hub_r'], w, (xc, 0, 0), axis='X', seg=32, m=m)
    arm = L.add_box('arm', w, p['arm_w'], p['arm'], (xc, 0, -p['arm'] / 2))
    pad = L.add_cyl('pad', p['pad_r'], w, (xc, 0, -p['arm']), axis='X', seg=32)
    L.union_into(hub, [arm, pad])
    L.bevel(hub, 0.4, 2, 32)
    L.assign(hub, m)
    hub.rotation_euler = (math.radians(p['rest_deg'] + 90.0), 0, 0)   # 朝下(-90°) → 静止角
    hub.data.transform(hub.matrix_basis)
    hub.rotation_euler = (0, 0, 0)
    hub.location = (0, AX[0], AX[1])
    return hub


def template(m):
    """装药漏斗模板：顶板 + 7 个漏斗 + 支脚（落在托盘前后壁顶面，避开杯勾手和日盖）。"""
    T = P.TPL
    z0, z1 = T['z0'], T['z0'] + T['t']
    cx_mid = P.TRAY_X0 + P.TRAY_W / 2
    plate = parts.prism_z('LoadingTemplate', parts.rr(P.TRAY_W, P.TRAY_D, 4.0, cx_mid, P.TRAY_CY), z0, z1, m)
    (tw, td, tr), (bw, bd, br), w = T['top'], T['bot'], T['wall']
    for cx in P.CELL_CX:
        outer = parts.loft('fo', [(parts.rr(bw, bd, br, cx, T['cy']), T['zb']), (parts.rr(tw, td, tr, cx, T['cy']), z1)])
        L.boolean(plate, outer, 'UNION')
    for cx in P.CELL_CX:
        inner = parts.loft('fi', [(parts.rr(bw - 2 * w, bd - 2 * w, br - w * 0.5, cx, T['cy']), T['zb'] - 0.5),
                                  (parts.rr(tw - 2 * w, td - 2 * w, tr - w * 0.5, cx, T['cy']), z1 + 0.5)])
        L.boolean(plate, inner)
    # 支脚：落在托盘前壁（y4–7.4）和后壁（y61.8–63.4）顶面，x 取在格板 / 端壁处
    xs = [P.TRAY_X0 + 0.8] + [cx + P.PITCH / 2 for cx in P.CELL_CX[:-1]] + [P.TRAY_X0 + P.TRAY_W - 0.8]
    for x in xs:
        for y in (5.6, 62.6):
            L.boolean(plate, L.add_box('leg', 1.6, 1.6, z0 - P.TRAY_Z1 + 0.4, (x, y, (P.TRAY_Z1 + z0 + 0.4) / 2)), 'UNION')
    parts.clean(plate)
    L.assign(plate, m)
    return plate
