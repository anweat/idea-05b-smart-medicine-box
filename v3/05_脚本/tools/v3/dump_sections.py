# -*- coding: utf-8 -*-
"""从 v3 模型直接剖切出截面轮廓（mm），给 draw_sheet.py 画工程图用
    blender -b --factory-startup model/v3/取药结构_v3.blend --python tools/v3/dump_sections.py
输出 model/v3/sections.json：
    AA  过周四杯中轴的 YZ 剖面（托盘 / 杯 / 闭合日盖），坐标 (y, z)
    BB  杯口下 5 mm 的 XY 剖面（杯 / 托盘），坐标 (x, y)
"""
import os, sys, json
import bpy, bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P

ROOT = os.path.dirname(os.path.dirname(HERE))
CELL = 3
CX = P.CELL_CX[CELL]


def tris_mm(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    out = [[tuple(c * 1000.0 for c in v.co) for v in f.verts] for f in bm.faces]
    bm.free()
    return out


def slice_loops(tris, axis, value, keep):
    """三角面与平面 axis=value 求交 → 线段 → 按端点串成闭环；keep 为保留的两个坐标轴下标。"""
    segs = []
    for t in tris:
        d = [p[axis] - value for p in t]
        pts = []
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]
            da, db = d[i], d[(i + 1) % 3]
            if (da < 0) != (db < 0):
                s = da / (da - db)
                pts.append(tuple(a[k] + (b[k] - a[k]) * s for k in keep))
        if len(pts) == 2:
            segs.append(pts)
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    nbr = {}
    for a, b in segs:
        nbr.setdefault(key(a), []).append(key(b))
        nbr.setdefault(key(b), []).append(key(a))
    loops, used = [], set()
    for start in list(nbr):
        if start in used:
            continue
        loop, prev, cur = [start], None, start
        used.add(start)
        while True:
            nxt = [n for n in nbr[cur] if n != prev and n not in used]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            used.add(cur); loop.append(cur)
        if len(loop) > 2:
            loops.append(loop)
    return loops


# 平面避开顶点/共面（偏 0.013 mm），否则零面积交线会断环
xa = CX + 0.013
zb = P.CUP_Z0 + P.CUP_H - 5.0 + 0.013
res = dict(cell=CELL, cx=CX, AA={}, BB={}, AA_x=xa, BB_z=zb)
for name in ('TrayV3', 'CupV3_%d' % CELL, 'Lid_%d' % CELL):
    tr = tris_mm(bpy.data.objects[name])
    res['AA'][name] = slice_loops(tr, 0, xa, (1, 2))
    if not name.startswith('Lid'):
        res['BB'][name] = slice_loops(tr, 2, zb, (0, 1))
    print('SLICE', name, [len(l) for l in res['AA'][name]], [len(l) for l in res['BB'].get(name, [])])
json.dump(res, open(os.path.join(ROOT, 'model', 'v3', 'sections.json'), 'w'))
