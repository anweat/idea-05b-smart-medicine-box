import bpy, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'model','IDEA-05_box.blend')
OUT=os.path.join(ROOT,'model')
bpy.ops.wm.open_mainfile(filepath=SRC)
for o in list(bpy.data.objects):
    if o.type in ('CAMERA','LIGHT'): bpy.data.objects.remove(o, do_unlink=True)
# open-lid
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'IDEA-05_box.glb'), export_format='GLB',
    use_selection=False, export_apply=True, export_yup=True)
# closed-lid
lid=bpy.data.objects.get('Lid_2')
if lid: lid.rotation_euler=(0,0,0)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'IDEA-05_box_closed.glb'), export_format='GLB',
    use_selection=False, export_apply=True, export_yup=True)
print('EXPORTED')
