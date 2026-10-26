# -*- coding: utf-8 -*-
"""整机 v3 剖面 A–A：过周四杯中轴（x≈160）切开所有零件，导出各件截面轮廓（mm，(y, z)）
    blender -b --factory-startup model/v3/IDEA-05_box_v3.blend --python tools/v3/dump_full_section.py
输出 model/v3/full_section.json：[{name, color, loops:[[...]], closed:[bool]}]
"""
import os, sys, json
import bpy, bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P

ROOT = os.path.dirname(os.path.dirname(HERE))
X = P.CELL_CX[3] + 0.013                     # 避开顶点 / 共面
for o in bpy.data.objects:                   # 闭盖状态出图
    if o.name.startswith('Lid_'):
        o.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()


def chains(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.transform(ob.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    segs = []
    for f in bm.faces:
        pts = [tuple(c * 1000.0 for c in v.co) for v in f.verts]
        d = [p[0] - X for p in pts]
        hit = []
        for i in range(3):
            a, b, da, db = pts[i], pts[(i + 1) % 3], d[i], d[(i + 1) % 3]
            if (da < 0) != (db < 0):
                s = da / (da - db)
                hit.append((a[1] + (b[1] - a[1]) * s, a[2] + (b[2] - a[2]) * s))
        if len(hit) == 2:
            segs.append(hit)
    bm.free()
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    nbr = {}
    for a, b in segs:
        nbr.setdefault(key(a), []).append(key(b))
        nbr.setdefault(key(b), []).append(key(a))
    loops, closed, used = [], [], set()
    for start in list(nbr):
        if start in used:
            continue
        lp, prev, cur = [start], None, start
        used.add(start)
        while True:
            nxt = [n for n in nbr[cur] if n != prev and n not in used]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            used.add(cur); lp.append(cur)
        if len(lp) > 2:
            loops.append(lp)
            closed.append(start in nbr[cur])
    return loops, closed


out = []
for o in bpy.context.view_layer.objects:          # 配件（装药模板）在排除的集合里，不进剖面
    if o.type != 'MESH' or o.hide_get():
        continue
    lo = min((o.matrix_world @ v.co).x for v in o.data.vertices) * 1000 if o.data.vertices else 0
    hi = max((o.matrix_world @ v.co).x for v in o.data.vertices) * 1000 if o.data.vertices else 0
    if not (lo < X < hi):
        continue
    loops, closed = chains(o)
    if not loops:
        continue
    m = o.active_material
    col = list(m.diffuse_color)[:3] if m else [0.8, 0.8, 0.8]
    out.append(dict(name=o.name, mat=m.name if m else '', color=col, loops=loops, closed=closed))
    print('CUT', o.name, len(loops), sum(closed))
json.dump(dict(x=X, parts=out), open(os.path.join(ROOT, 'model', 'v3', 'full_section.json'), 'w'))
