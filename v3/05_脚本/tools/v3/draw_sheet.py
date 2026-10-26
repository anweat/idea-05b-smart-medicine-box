# -*- coding: utf-8 -*-
"""取药结构 v3 · 工程图板（剖面 A–A + 俯剖 B–B + 仿真结果）
数据全部来自模型：model/v3/sections.json（dump_sections.py 剖切）、sim_pour_report.json、v3_report.json
    python3 tools/v3/draw_sheet.py
"""
import os, sys, json, math
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import params as P
from draw_lib import font

ROOT = os.path.dirname(os.path.dirname(HERE))
MOD = os.path.join(ROOT, 'model', 'v3')
sec = json.load(open(os.path.join(MOD, 'sections.json')))
sim = json.load(open(os.path.join(MOD, 'sim_pour_report.json')))
rep = json.load(open(os.path.join(MOD, 'v3_report.json')))['extra']

W, H = 2400, 1560
BG, INK, MUTE, ACC = (247, 248, 250), (40, 48, 60), (120, 130, 145), (18, 118, 100)
C_TRAY, C_CUP, C_LID, C_DIM = (214, 210, 200), (190, 222, 236), (176, 184, 192), (200, 90, 30)
im = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(im)
F = {k: font(v) for k, v in dict(t=46, h=30, b=24, s=21, xs=18).items()}
FB = font(30, bold=True)

d.text((70, 48), '取药结构 v3 · 剖面与关键尺寸', fill=INK, font=F['t'])
d.text((70, 112), '320×70×52 / 7 日格；药杯与托盘的 5 处关键结构都借自成熟做法。单位 mm，图中轮廓由 3D 模型直接剖切。',
       fill=MUTE, font=F['b'])


# ---------------------------------------------------------------- 工具
def mapper(ox, oy, s, u0, v0):
    return lambda u, v: (ox + (u - u0) * s, oy - (v - v0) * s)


def poly(loops, T, fill, outline=INK, width=2):
    for lp in loops:
        pts = [T(*p) for p in lp]
        d.polygon(pts, fill=fill, outline=outline, width=width)


def arrow(p, q, col=C_DIM, w=2, head=9):
    d.line([p, q], fill=col, width=w)
    for a, b in ((p, q), (q, p)):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for s in (-1, 1):
            d.line([b, (b[0] - head * math.cos(ang + s * 0.4), b[1] - head * math.sin(ang + s * 0.4))], fill=col, width=w)


def vdim(T, u, v0, v1, text, side=1, off=0):
    p, q = T(u, v0), T(u, v1)
    x = p[0] + off
    d.line([(p[0], p[1]), (x + 6 * side, p[1])], fill=C_DIM, width=1)
    d.line([(q[0], q[1]), (x + 6 * side, q[1])], fill=C_DIM, width=1)
    arrow((x, p[1]), (x, q[1]))
    tw = d.textlength(text, font=F['s'])
    d.text((x + 10 if side > 0 else x - 10 - tw, (p[1] + q[1]) / 2 - 12), text, fill=C_DIM, font=F['s'])


def hdim(T, v, u0, u1, text, off=0, up=True):
    p, q = T(u0, v), T(u1, v)
    y = p[1] + off
    d.line([(p[0], p[1]), (p[0], y)], fill=C_DIM, width=1)
    d.line([(q[0], q[1]), (q[0], y)], fill=C_DIM, width=1)
    arrow((p[0], y), (q[0], y))
    tw = d.textlength(text, font=F['s'])
    d.text(((p[0] + q[0]) / 2 - tw / 2, y - 30 if up else y + 6), text, fill=C_DIM, font=F['s'])


def leader(p, q, text, col=ACC):
    d.line([p, q], fill=col, width=2)
    d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=col)
    d.multiline_text((q[0] + 8, q[1] - 14), text, fill=col, font=F['s'], spacing=6)


# ---------------------------------------------------------------- A–A 剖面（YZ）
ax, ay, S = 330, 900, 13.0
T = mapper(ax, ay, S, 0.0, 22.0)               # 画面 u=y（前→后），v=z
d.text((70, 180), 'A–A  过「周四」杯中轴的纵剖面（左＝前脸，右＝铰链）', fill=INK, font=F['h'])
cup = 'CupV3_%d' % sec['cell']
poly(sec['AA']['Lid_%d' % sec['cell']], T, C_LID)
poly(sec['AA']['TrayV3'], T, C_TRAY)
poly(sec['AA'][cup], T, C_CUP)
z0, zr = P.CUP_Z0, P.CUP_Z0 + P.CUP_H
y0 = P.CUP_Y0
vdim(T, -1.5, z0 + P.FLOOR_LOW_Z, zr, '杯口→最低点 %.0f' % (P.CUP_H - P.FLOOR_LOW_Z), side=-1, off=-40)
vdim(T, -1.5, z0 + P.FLOOR_LOW_Z, z0 + P.LIP_Z, '唇高 %.0f' % (P.LIP_Z - P.FLOOR_LOW_Z), side=-1, off=-200)
vdim(T, 70.5, P.TRAY_Z0, P.TRAY_Z0 + P.TRAY_FLOOR, '托盘底 %.0f' % P.TRAY_FLOOR, side=1, off=30)
vdim(T, 70.5, zr, zr + P.HANDLE_H, '勾手 %.1f' % P.HANDLE_H, side=1, off=30)
vdim(T, 70.5, zr + P.HANDLE_H, rep['cup_section']['lid_cavity_top_world_z'], '离盖 %.1f' %
     (rep['cup_section']['lid_cavity_top_world_z'] - zr - P.HANDLE_H), side=1, off=30)
hdim(T, z0 + P.LIP_Z, y0, y0 + rep['cup_section']['lip_land_y'][1], '唇台 %.1f' % rep['cup_section']['lip_land_y'][1],
     off=-150)
# 弧底 R12：从圆心引线
cyy, czz = y0 + P.GULLY_Y, z0 + P.FLOOR_LOW_Z + P.COVE_R
a = math.radians(-125)
pc = T(cyy + P.COVE_R * math.cos(a), czz + P.COVE_R * math.sin(a))
leader(pc, (pc[0] + 60, pc[1] + 150), '③ 硬币杯式弧底 R%.0f：指腹把药推上弧面，停在唇台边再捏' % P.COVE_R)
ph = T(y0 + P.CUP_D - 4, zr + P.HANDLE_H - 0.8)
leader(ph, (ph[0] - 330, ph[1] - 120), '① 后侧 T 形勾手（与前倒嘴相对，量杯式）')
pg = T(y0 + 30, z0 + P.FLOOR_BACK_Z - 0.6)
leader(pg, (pg[0] - 60, pg[1] + 175), '杯直接坐托盘底；底下 10×24 通光孔 + 隔光墙')
d.text(T(-3, 54.5), '日盖', fill=MUTE, font=F['s'])
d.text((ax - 30, ay + 150), '前', fill=MUTE, font=FB)
d.text((T(70, 22)[0] - 10, ay + 150), '后', fill=MUTE, font=FB)

# ---------------------------------------------------------------- B–B 俯剖（XY）
bx, by, S2 = 1490, 980, 12.0
cx = sec['cx']
T2 = mapper(bx, by, S2, cx - 24.0, 2.0)
d.text((1420, 180), 'B–B  杯口下 5 mm 的俯剖（下＝前脸）', fill=INK, font=F['h'])
tray_loops = sec['BB']['TrayV3']
outer = max(tray_loops, key=lambda lp: max(abs(p[0] - cx) for p in lp))
d.rectangle([T2(cx - 24, 66)[0], T2(cx - 24, 66)[1], T2(cx + 24, 4)[0], T2(cx + 24, 4)[1]], fill=C_TRAY)
for lp in tray_loops:
    if lp is outer:
        continue
    if all(abs(p[0] - cx) < 24 for p in lp):
        d.polygon([T2(*p) for p in lp], fill=BG, outline=INK, width=2)
poly(sec['BB'][cup], T2, C_CUP)
hw = P.SPOUT_W / 2
hdim(T2, y0, cx - hw, cx + hw, '① 倒嘴 %.0f' % P.SPOUT_W, off=70, up=False)
pf = T2(cx + hw + 3.0, y0 + P.CUP_WALL + 7.0)
leader(pf, (pf[0] + 120, pf[1] + 40), '② 数药盘式收拢 %.0f°' % rep['cup_section']['funnel_half_angle_deg'])
pk = T2(cx - P.CUP_W / 2 + 1.6, y0 + P.CUP_D - 1.6)
leader(pk, (T2(cx + 24, 0)[0] + 50, pk[1] - 10), '④ SIM 卡式切角 %.0f\n+ 托盘角填块\n反装放不进' % P.CUP_KEY)
pl = T2(cx + P.POCKET_W / 2 - 0.2, y0 + 40)
leader(pl, (pl[0] + 90, pl[1] - 10), '⑤ 杯位口导入 0.4×1.5')

# ---------------------------------------------------------------- 仿真结果
tx, ty = 1420, 1130
d.text((tx, ty), '倒药刚体仿真（6 粒：圆片×3、椭圆片、1#/2# 胶囊；μ=0.4，绕前唇 35°/s 前倾）', fill=INK, font=F['b'])
v3 = sim['v3']
rows = [('第一粒倒出', '%.0f°' % v3['first_exit_deg']),
        ('全部倒出', '%.0f°' % v3['last_exit_deg']),
        ('倾到 70° 时杯内残留', '%d / 6' % v3['remaining_at_70']),
        ('出口偏离倒嘴中线', '最大 %.1f mm' % max(abs(p['exit_x_mm']) for p in v3['pills']))]
for i, r in enumerate(rows):
    y = ty + 50 + i * 46
    if i:
        d.line([(tx, y - 6), (tx + 880, y - 6)], fill=(222, 226, 232), width=1)
    d.text((tx, y), r[0], fill=MUTE, font=F['s'])
    d.text((tx + 400, y), r[1], fill=ACC, font=F['s'])
d.text((tx, ty + 245), '弧底把唇口内侧变成斜面：杯子倾过 ~40° 药就开始出，58° 倒空，且都从 24 mm 倒嘴中间出来。',
       fill=MUTE, font=F['xs'])
d.text((70, H - 60), '校验：7 杯×托盘 / 杯×闭盖 / 开盖 0–105° 扫掠干涉均为 0；反装杯与防呆块干涉 %.0f 立方毫米（放不进）；'
       '3D Print Toolbox：0 非流形 / 0 自相交 / 0 薄面(<1 mm)。' % rep['reversed_cup_x_tray_mm3'], fill=MUTE, font=F['xs'])

out = os.path.join(ROOT, 'design', '30_取药结构v3_剖面与尺寸.png')
im.save(out)
print('SHEET', out)
