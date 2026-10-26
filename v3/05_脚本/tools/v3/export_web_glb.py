# -*- coding: utf-8 -*-
"""给 3D 实时预览页导出 3 种状态的 GLB（Draco 压缩）：闭盖 / 周三开盖 / 一拨全开
    blender -b --factory-startup --python tools/v3/export_web_glb.py
输出 model/v3/web/{closed,open,allopen}.glb
"""
import os, math
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'model', 'v3', 'web')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, 'model', 'v3', 'IDEA-05_box_v3.blend'))


def pose(lids, gang):
    """lids：单独打开的格；gang：拨片联动全开（7 盖 + 驱动轴 + 拨片一起转 100°）。"""
    for o in bpy.data.objects:
        if o.parent is not None:
            continue
        if o.name.startswith('Lid_'):
            deg = 100 if gang or int(o.name.split('_')[1]) in lids else 0
        elif o.name.startswith(('DriveShaft', 'Paddle')):
            deg = 100 if gang else 0
        else:
            continue
        o.rotation_euler = (math.radians(-deg), 0, 0)
    bpy.context.view_layer.update()


for name, lids, gang in (('closed', (), False), ('open', (2,), False), ('allopen', (), True)):
    pose(lids, gang)
    path = os.path.join(OUT, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_yup=True,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6)
    print('WEBGLB', name, os.path.getsize(path))
