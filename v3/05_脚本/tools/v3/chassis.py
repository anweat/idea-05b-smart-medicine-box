# -*- coding: utf-8 -*-
"""IDEA-05B · 整机 v3 的底座内部件（mm 场景建模，坐标同 params.py）

称重链：托盘 3 个半球脚 → 浮动架（锥窝 / V 槽 / 平面 = Maxwell 三点运动学定位）
        → 后中 1 只单点平行梁称重传感器（厨房秤架构）→ 底座固定座。
托盘、浮动架与底座之间全部留缝；4 个过载限位只在超载时才碰。
"""
import math
import bmesh
import params as P
import parts
import lib as L


def carrier(m):
    """称重浮动架：前梁（平面支承）+ 后梁（锥窝 + V 槽）+ 两端横梁，一体。"""
    x0, x1 = P.RAIL_X
    fz0, fz1 = P.RAIL_F['z']
    rz0, rz1 = P.RAIL_R['z']
    fr = L.add_box('Carrier', x1 - x0, P.RAIL_F['y'][1] - P.RAIL_F['y'][0], fz1 - fz0,
                   ((x0 + x1) / 2, sum(P.RAIL_F['y']) / 2, (fz0 + fz1) / 2), m)
    parts_ = [L.add_box('rr', x1 - x0, P.RAIL_R['y'][1] - P.RAIL_R['y'][0], rz1 - rz0,
                        ((x0 + x1) / 2, sum(P.RAIL_R['y']) / 2, (rz0 + rz1) / 2))]
    for xe in (x0 + 3, x1 - 3):
        parts_.append(L.add_box('end', 6, P.RAIL_R['y'][1] - P.RAIL_F['y'][0], fz1 - rz0,
                                (xe, (P.RAIL_F['y'][0] + P.RAIL_R['y'][1]) / 2, (rz0 + fz1) / 2)))
    L.union_into(fr, parts_)
    # 锥窝 / V 槽：90° 夹角，球心落在 TRAY_Z0 时与两斜面相切
    apex = P.TRAY_Z0 - P.BALL_R / math.sin(math.radians(45))
    top = rz1 + 1.0
    r_top = top - apex
    cx, cy = P.KIN['cone']
    L.boolean(fr, L.add_cyl('cone', 0.001, r_top, (cx, cy, (apex + top) / 2), seg=48, r2=r_top))
    vx, vy = P.KIN['vee']
    L.boolean(fr, L.add_prism_x('vee', [(vy - r_top, top), (vy + r_top, top), (vy, apex)], vx - 7, vx + 7))
    L.bevel(fr, 0.4, 2, 32)
    L.assign(fr, m)
    return fr


def load_cell(m_al, m_dark, m_base):
    """500 g 微型平行梁（双孔应变区），固定端坐在底座凸台，自由端经垫块托住后梁。"""
    Lc, S, x0, y, z0 = P.LC['L'], P.LC['S'], P.LC['x0'], P.LC['y'], P.LC['z0']
    beam = L.add_box('LoadCell', Lc, S, S, (x0 + Lc / 2, y, z0 + S / 2), m_al)
    zc = z0 + S / 2
    for dx in (-5.0, 5.0):
        L.boolean(beam, L.add_cyl('h', 2.0, S + 2, (x0 + Lc / 2 + dx, y, zc), axis='Y', seg=32))
    L.boolean(beam, L.add_box('slot', 10.0, S + 2, 0.9, (x0 + Lc / 2, y, zc)))
    L.assign(beam, m_al)
    gauge = L.add_box('StrainGauge', 9.0, 3.0, 0.15, (x0 + Lc / 2, y, z0 + S + 0.07), m_dark)
    boss = L.add_box('LC_Boss', 10.0, 6.0, z0 - 2.0, (x0 + 5.0, y, (2.0 + z0) / 2), m_base)
    spacer = L.add_box('LC_Spacer', 10.0, 6.0, P.RAIL_R['z'][0] - (z0 + S),
                       (x0 + Lc - 5.0, y, (z0 + S + P.RAIL_R['z'][0]) / 2), m_dark)
    return [beam, gauge, boss, spacer]


def stops(m):
    """4 个过载限位柱（TPE 头），与浮动架底面留 STOP_GAP。"""
    out = []
    for (x, y, rail) in ((22.0, 11.0, P.RAIL_F), (298.0, 11.0, P.RAIL_F),
                         (32.0, 59.0, P.RAIL_R), (288.0, 59.0, P.RAIL_R)):
        top = rail['z'][0] - P.STOP_GAP
        out.append(L.add_cyl('Stop', 2.5, top - 2.0, (x, y, (top + 2.0) / 2), seg=32, m=m))
    return out


def spine(m):
    """底座铰链脊：日盖铰链挂在底座上（不在托盘上），托盘才能整盘取出；顶面让开驱动轴，内藏霍尔。"""
    (x0, x1), (y0, y1), (z0, z1) = P.SPINE['x'], P.SPINE['y'], P.SPINE['z']
    sp = parts.prism_z('HingeSpine', parts.rr(x1 - x0, y1 - y0, 2.0, (x0 + x1) / 2, (y0 + y1) / 2), z0 - 0.5,
                       P.SPINE_STRIP_TOP, m)
    L.bevel(sp, 0.8, 2, 32)
    for cx in P.CELL_CX:                     # 日盖铰链节让位
        for dx in (-16, 16):
            L.boolean(sp, L.add_cyl('kn', 2.6, 5.0, (cx + dx, P.HINGE_Y, P.HINGE_Z), axis='X', seg=32))
    L.assign(sp, m)
    return sp


def hall_and_magnets(m_chip, m_mag):
    """每格 1 颗霍尔（藏在铰链脊里）+ 日盖后壁 1 颗 Ø3×1.5 磁铁（随盖转）。"""
    halls, mags = [], []
    for i, cx in enumerate(P.CELL_CX):
        halls.append(L.add_box('Hall_%d' % i, 3.0, 1.4, 1.0, (cx, 65.2, P.SPINE_STRIP_TOP - 0.9), m_chip))
        mags.append(L.add_cyl('Magnet_%d' % i, 1.5, 1.5, (cx, 65.0, 44.6), axis='Y', seg=24, m=m_mag))
    return halls, mags


def ir_parts(m_led, m_ir, m_on, today=2):
    """传感板上每格：1 颗导光 LED + 1 对红外对管，正对托盘通光孔，两侧是托盘隔光墙。"""
    out = []
    for i, cx in enumerate(P.CELL_CX):
        out.append(L.add_box('LED_%d' % i, 3.0, 3.0, 0.8, (cx, P.POCKET_CY, 22.2), m_on if i == today else m_led))
        for dy in (-7.0, 7.0):
            out.append(L.add_box('IR_%d' % i, 2.4, 2.0, 1.0, (cx, P.POCKET_CY + dy, 22.3), m_ir))
    return out


def desiccant(m_pad, m_grille):
    """每个日盖内顶 1 片 30×34×2 硅胶干燥片 + 冲孔格栅（日盖局部坐标，铰链为原点）。"""
    pads, grills = [], []
    for i, cx in enumerate(P.CELL_CX):
        yc = 30.0 - P.HINGE_Y
        pads.append(L.add_box('Desiccant_%d' % i, 30.0, 34.0, 1.6, (0, yc, 7.1), m_pad))
        g = L.add_box('DesGrille_%d' % i, 33.0, 37.0, 0.6, (0, yc, 6.0), m_grille)
        for gx in range(-12, 13, 4):
            L.boolean(g, L.add_box('slot', 1.6, 28.0, 2.0, (gx, yc, 6.0)))
        grills.append(g)
    return pads, grills


def gasket(m):
    """1 件多腔硅胶密封垫：7 个框 + 连接筋，压在托盘口（替代原 7 圈独立圈）。"""
    g = parts.prism_z('Gasket_v3', parts.rr(P.TRAY_W - 2.0, P.TRAY_D - 2.0, 3.5, P.TRAY_X0 + P.TRAY_W / 2, P.TRAY_CY),
                      P.TRAY_Z1 - 0.35, P.TRAY_Z1, m)
    for cx in P.CELL_CX:
        L.boolean(g, parts.prism_z('o', parts.rr(P.POCKET_W + 1.0, P.POCKET_D + 1.8, 4.0, cx, P.POCKET_CY),
                                   P.TRAY_Z1 - 1.0, P.TRAY_Z1 + 1.0))
    return g
