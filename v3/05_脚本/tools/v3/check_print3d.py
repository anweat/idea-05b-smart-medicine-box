# -*- coding: utf-8 -*-
"""用官方扩展 3D Print Toolbox 对 v3 零件做第二道独立检查（与 tools/v2/lib.stats 互为校核）
需要已安装扩展 print3d_toolbox，所以**不要**加 --factory-startup：
    blender -b model/v3/取药结构_v3.blend --python tools/v3/check_print3d.py
"""
import os, sys, json
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
report = sys.modules['bl_ext.blender_org.print3d_toolbox.report']
PARTS = ['TrayV3', 'CupV3_0', 'Lid_0']
THICK_MIN_MM = 1.0              # 注塑件最薄处下限（格板顶 1.33、杯壁 1.6）

sc = bpy.context.scene
u = 1000.0 if sc.unit_settings.scale_length >= 0.5 else 1.0     # 1 BU 等于多少 mm
sc.print3d_toolbox.thickness_min = THICK_MIN_MM / u
out = {}
for name in PARTS:
    ob = bpy.data.objects[name]
    for o in bpy.data.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.mesh.print3d_check_all()
    out[name] = {it.name: it.value for it in report.get()}
    bpy.ops.mesh.print3d_info_volume()
    out[name].update({it.name: it.value for it in report.get()})
print('P3D', json.dumps(out, ensure_ascii=False))
open(os.path.join(ROOT, 'model', 'v3', 'print3d_check.json'), 'w').write(json.dumps(out, ensure_ascii=False, indent=1))
