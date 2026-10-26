# -*- coding: utf-8 -*-
"""整机 v3 · 剖面 A–A 工程图（轮廓来自 model/v3/full_section.json，颜色取各零件材质）
    python3 tools/v3/draw_full_section.py
"""
import os, sys, json
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import params as P
from draw_lib import font

ROOT = os.path.dirname(os.path.dirname(HERE))
data = json.load(open(os.path.join(ROOT, 'model', 'v3', 'full_section.json')))
qa = json.load(open(os.path.join(ROOT, 'model', 'v3', 'full_qa.json')))['weigh_chain']

W, H = 2400, 1480
BG, INK, MUTE, ACC, DIM = (247, 248, 250), (40, 48, 60), (120, 130, 145), (18, 118, 100), (200, 90, 30)
im = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(im)
F = dict(t=font(46), b=font(24), s=font(21), xs=font(18))
d.text((70, 48), '整机剖面 A–A · 过「周四」杯中轴', fill=INK, font=F['t'])
d.text((70, 112), '左＝前脸，右＝铰链。轮廓由整机 3D 模型直接剖切；颜色＝零件材质。单位 mm。', fill=MUTE, font=F['b'])

S = 17.0
OX, OY = 640, 1180                         # y=0 → OX；z=0 → OY
T = lambda y, z: (OX + y * S, OY - z * S)


def srgb(c):
    return tuple(int(255 * min(1.0, max(0.0, v)) ** (1 / 2.2)) for v in c)


ORDER = ['BaseShell', 'BackPlate', 'ControlBand', 'Seam', 'HingeSpine', 'DriveShaft', 'Battery', 'PCB', 'LoadCell',
         'StrainGauge', 'SensorPlate', 'LED_', 'IR_', 'Carrier', 'TrayV3', 'Gasket_v3', 'CupV3', 'Lid_', 'DesGrille',
         'Desiccant', 'Magnet', 'Hall']
rank = lambda p: next((i for i, k in enumerate(ORDER) if p['name'].startswith(k)), 99)
for p in sorted(data['parts'], key=rank):
    if p['name'].startswith('BackTxt'):
        continue
    col = srgb(p['color'])
    if p['name'].startswith('Lid_'):
        col = (196, 204, 212)
    if p['name'].startswith('CupV3'):
        col = (178, 214, 230)
    for lp, cl in zip(p['loops'], p['closed']):
        pts = [T(y, z) for y, z in lp]
        if cl and len(pts) > 2:
            d.polygon(pts, fill=col, outline=INK, width=2)
        else:
            d.line(pts, fill=INK, width=2)


def leader(anchor, label, side, slot):
    ax, ay = T(*anchor)
    x = OX - 60 if side < 0 else OX + 70 * S + 60
    y = 210 + slot * 56
    tw = d.textlength(label, font=F['s'])
    tx = x - tw - 14 if side < 0 else x + 14
    d.line([(ax, ay), (x, y)], fill=ACC, width=2)
    d.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], fill=ACC)
    d.text((tx, y - 13), label, fill=ACC, font=F['s'])


y0, z0 = P.CUP_Y0, P.CUP_Z0
LEFT = [((20.0, 51.2), '日盖（烟灰 PC）'),
        ((22.0, 48.6), '每盖 1 片干燥片 + 冲孔格栅'),
        ((5.6, 41.85), '一件多腔硅胶密封垫'),
        ((y0 + 5.0, z0 + P.LIP_Z - 0.4), '唇台 + R12 弧底（硬币杯）'),
        ((y0 + 26.0, z0 + 2.6), '药杯直接坐托盘底'),
        ((5.5, 33.0), '托盘 = 药芯（不带电子件）'),
        ((P.POCKET_CY - 6.0, 25.8), '通光孔 10×24'),
        ((P.POCKET_CY - 7.0, 22.4), '红外对管 + 导光 LED'),
        ((11.0, 23.2), '球脚 → 前梁平面（三点定位之一）'),
        ((11.0, 20.6), '称重浮动架（铝）'),
        ((3.2, 24.4), '称重浮动缝 %.1f（与分模线重合）' % qa['tray_to_base_gap']),
        ((25.0, 12.0), '主板'),
        ((25.0, 6.0), '电池'),
        ((2.0, 3.0), '底座（暖白 ABS）')]
RIGHT = [((P.HINGE_Y, P.HINGE_Z), '驱动轴（联动全开，拨爪在铰链节内）'),
         ((65.0, 44.6), '磁铁 φ3（随盖转）'),
         ((y0 + P.CUP_D - 4.0, z0 + P.CUP_H + P.HANDLE_H - 0.8), '后侧 T 形勾手（量杯式）'),
         ((66.6, 39.8), '霍尔（开盖检测）'),
         ((67.5, 31.0), '铰链脊（属底座，托盘可整盘取出）'),
         ((50.0, 29.0), '药杯 CupV3'),
         ((50.0, 21.0), '传感板（LED / 红外）'),
         ((59.0, 22.2), '浮动架后梁（锥窝 / V 槽在两端）'),
         ((59.0, 16.0), '500 g 单点平行梁称重传感器'),
         ((60.0, 19.4), '应变片')]
# 标签按锚点高度从上到下排，引线少交叉
for i, (a, t) in enumerate(sorted(LEFT, key=lambda r: -r[0][1])):
    leader(a, t, -1, i * 1.05 + 0.4)
for i, (a, t) in enumerate(sorted(RIGHT, key=lambda r: -r[0][1])):
    leader(a, t, 1, i * 1.45 + 0.4)

# 尺寸：总高 52 / 浮动缝
x = OX + 70 * S + 26
for zz in (0, 52):
    d.line([T(70, zz), (x + 8, T(70, zz)[1])], fill=DIM, width=1)
d.line([(x, T(70, 0)[1]), (x, T(70, 52)[1])], fill=DIM, width=2)
d.text((x + 10, (T(70, 0)[1] + T(70, 52)[1]) / 2 - 12), '52', fill=DIM, font=F['s'])
d.text((OX - 10, OY + 30), '前', fill=MUTE, font=F['b'])
d.text((OX + 70 * S - 20, OY + 30), '后', fill=MUTE, font=F['b'])
d.text((70, H - 70), '称重链只有一条：托盘 3 个球脚 → 浮动架 → 垫块 → 称重传感器 → 固定座 → 底座。托盘离底座 %.1f、离铰链脊 %.1f、离传感板 %.1f；'
       '浮动架离底座 %.1f、离过载限位 %.1f（mm，整机模型实测）。' % (qa['tray_to_base_gap'], qa['tray_to_spine_gap'],
                                                  qa['tray_to_sensorplate_gap'], qa['carrier_to_base_gap'],
                                                  qa['carrier_to_stops_gap']), fill=MUTE, font=F['xs'])
out = os.path.join(ROOT, 'design', '32_整机v3_剖面A-A.png')
im.save(out)
print('SHEET', out)
