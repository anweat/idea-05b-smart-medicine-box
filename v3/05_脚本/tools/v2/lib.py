# -*- coding: utf-8 -*-
"""IDEA-05B · Blender 5.2 几何/渲染/校验通用库（单位 mm，建好后再缩到 m）

约定：所有 build_*.py 都在 mm 场景里建模、校验、渲染；最后调用
finalize_meters() 把网格缩到 1:1 米制再存 .blend / 导 GLB / STL。
"""
import bpy, bmesh, math, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

MM = 0.001


# ---------------------------------------------------------------- 场景
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.001      # 1 BU = 1 mm
    sc.unit_settings.length_unit = 'MILLIMETERS'
    return sc


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- 材质
def mat(name, color, rough=0.45, metal=0.0, transmission=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if transmission > 0:
        p.inputs['Transmission Weight'].default_value = transmission
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
    m.diffuse_color = (*color, 1.0)
    return m


def assign(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob


# ---------------------------------------------------------------- 基元
def _finish(name, bm, m):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    if m is not None:
        assign(ob, m)
    return ob


def add_box(name, sx, sy, sz, loc=(0, 0, 0), m=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x * sx + loc[0]
        v.co.y = v.co.y * sy + loc[1]
        v.co.z = v.co.z * sz + loc[2]
    return _finish(name, bm, m)


def add_cyl(name, r, h, loc=(0, 0, 0), axis='Z', seg=64, m=None, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h)
    if axis == 'X':
        for v in bm.verts:
            v.co.x, v.co.y, v.co.z = v.co.z, v.co.y, -v.co.x
    elif axis == 'Y':
        for v in bm.verts:
            v.co.x, v.co.y, v.co.z = v.co.x, v.co.z, -v.co.y
    for v in bm.verts:
        v.co.x += loc[0]; v.co.y += loc[1]; v.co.z += loc[2]
    return _finish(name, bm, m)


def add_prism_x(name, profile_yz, x0, x1, m=None):
    """把 (y,z) 闭合多边形沿 X 挤出成实体。"""
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for (y, z) in profile_yz]
    b = [bm.verts.new((x1, y, z)) for (y, z) in profile_yz]
    n = len(profile_yz)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    return _finish(name, bm, m)


# ---------------------------------------------------------------- 布尔
def prune_materials(ob):
    """删掉空材质槽并重映射面材质索引（布尔并集常引入 None 槽）。"""
    me = ob.data
    if not any(m is None for m in me.materials):
        return ob
    keep = [m for m in me.materials if m is not None]
    remap, k = {}, 0
    for i, m in enumerate(me.materials):
        if m is not None:
            remap[i] = k
            k += 1
    for p in me.polygons:
        p.material_index = remap.get(p.material_index, 0)
    me.materials.clear()
    for m in keep:
        me.materials.append(m)
    return ob


def boolean(obj, tool, op='DIFFERENCE', delete_tool=True):
    md = obj.modifiers.new('bool', 'BOOLEAN')
    md.operation = op
    md.object = tool
    md.solver = 'EXACT'
    md.use_hole_tolerant = False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=md.name)
    if delete_tool:
        bpy.data.objects.remove(tool, do_unlink=True)
    prune_materials(obj)
    return obj


def union_into(obj, tools):
    for t in tools:
        boolean(obj, t, 'UNION')
    return obj


def subtract(obj, tools):
    for t in tools:
        boolean(obj, t, 'DIFFERENCE')
    return obj


def bevel(obj, width, segments=2, angle=32.0, clamp=True):
    md = obj.modifiers.new('bev', 'BEVEL')
    md.width = width
    md.segments = segments
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(angle)
    md.use_clamp_overlap = clamp
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=md.name)
    return obj


def join_bm(objs, name, m=None):
    """不用 ops.join（后台不稳），直接 bmesh 合并（shell 各自闭合）。"""
    bm = bmesh.new()
    for o in objs:
        tmp = bmesh.new()
        tmp.from_mesh(o.data)
        tmp.transform(o.matrix_world)
        me = bpy.data.meshes.new('tmp')
        tmp.to_mesh(me)
        tmp.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    ob = _finish(name, bm, m or (objs[0].data.materials[0] if objs[0].data.materials else None))
    for o in objs:
        if o is not ob:
            bpy.data.objects.remove(o, do_unlink=True)
    return ob


def offset_mesh(ob, dx=0.0, dy=0.0, dz=0.0):
    """把网格数据整体平移（保持 object 变换为 0，便于后续绕轴旋转）。"""
    from mathutils import Matrix
    ob.data.transform(Matrix.Translation((dx, dy, dz)))
    ob.data.update()
    return ob


def apply_all(objs):
    for o in objs:
        bpy.context.view_layer.objects.active = o
        for md in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=md.name)


# ---------------------------------------------------------------- 统计 / 校验
def _u():
    """当前 1 BU 等于多少 mm。"""
    sl = bpy.context.scene.unit_settings.scale_length
    return 1000.0 if sl >= 0.5 else 1.0


def _bmesh(ob):
    bm = bmesh.new()
    dg = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(dg)
    me = oe.to_mesh()
    bm.from_mesh(me)
    oe.to_mesh_clear()
    return bm


def volume(ob):
    bm = _bmesh(ob)
    v = bm.calc_volume(signed=False)
    bm.free()
    return v


def stats(ob):
    bm = _bmesh(ob)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    nonman = [e for e in bm.edges if len(e.link_faces) != 2]
    loose = [v for v in bm.verts if not v.link_edges]
    # 壳数
    seen, shells = set(), 0
    for f in bm.faces:
        if f.index in seen:
            continue
        shells += 1
        stack = [f]
        while stack:
            cur = stack.pop()
            if cur.index in seen:
                continue
            seen.add(cur.index)
            for e in cur.edges:
                for nf in e.link_faces:
                    if nf.index not in seen:
                        stack.append(nf)
    vol = bm.calc_volume(signed=False)
    u = _u()
    mw = ob.matrix_world
    world = [mw @ v.co for v in bm.verts]
    bt = BVHTree.FromBMesh(bm)
    tw = []
    faces = bm.faces[:]
    step = max(1, len(faces) // 400)
    for f in faces[::step]:
        c = f.calc_center_median()
        n = f.normal
        hit = bt.ray_cast(c - n * 0.02, -n, 300.0)
        if hit[0] is not None:
            tw.append(hit[3] + 0.02)
    tw.sort()
    bm.free()
    xs = [p.x for p in world]; ys = [p.y for p in world]; zs = [p.z for p in world]
    o = ob
    return dict(name=o.name, verts=len(o.data.vertices), polys=len(o.data.polygons),
                volume_mm3=round(vol * u ** 3, 2), shells=shells,
                nonmanifold_edges=len(nonman), loose_verts=len(loose),
                watertight=(len(nonman) == 0 and len(loose) == 0),
                bbox_mm=[round((max(xs) - min(xs)) * u, 2), round((max(ys) - min(ys)) * u, 2),
                         round((max(zs) - min(zs)) * u, 2)],
                bbox_min=[round(min(xs) * u, 2), round(min(ys) * u, 2), round(min(zs) * u, 2)],
                wall_min_mm=round(tw[0] * u, 3) if tw else None,
                wall_p05_mm=round(tw[len(tw) // 20] * u, 3) if tw else None,
                wall_median_mm=round(tw[len(tw) // 2] * u, 3) if tw else None)


def report(objs, path=None, extra=None):
    rep = [stats(o) for o in objs]
    out = dict(objects=rep, extra=extra or {})
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    print('DSH_REPORT ' + json.dumps(out, ensure_ascii=False))
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').write(txt)
    return out


def interference_volume(a, b):
    a2 = a.copy(); a2.data = a.data.copy(); link(a2)
    b2 = b.copy(); b2.data = b.data.copy(); link(b2)
    a2.matrix_world = a.matrix_world.copy(); b2.matrix_world = b.matrix_world.copy()
    boolean(a2, b2, 'INTERSECT')
    v = volume(a2)
    bpy.data.objects.remove(a2, do_unlink=True)
    return round(v, 3)


def cap_holes(ob, section_mat=None):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    if boundary:
        res = bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        newf = res.get('faces', [])
        if newf and section_mat is not None:
            me = ob.data
            idx = None
            for i, m in enumerate(me.materials):
                if m is not None and m.name == section_mat.name:
                    idx = i
                    break
            if idx is None:
                me.materials.append(section_mat)
                idx = len(me.materials) - 1
            for f in newf:
                f.material_index = idx
        if newf:
            bmesh.ops.triangulate(bm, faces=newf)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return ob


def assign_plane_faces(ob, axis, value, mat):
    """把正好落在切平面上的面改成剖面色（EXACT 布尔不保证继承工具材质）。"""
    me = ob.data
    ai = {'X': 0, 'Y': 1, 'Z': 2}[axis]
    tol = 0.01 / _u()
    idx = None
    for i, m in enumerate(me.materials):
        if m is not None and m.name == mat.name:
            idx = i
            break
    if idx is None:
        me.materials.append(mat)
        idx = len(me.materials) - 1
    n = 0
    for p in me.polygons:
        if all(abs(me.vertices[i].co[ai] - value) < tol for i in p.vertices):
            p.material_index = idx
            n += 1
    return n


def cut_half(ob, axis='Y', value=0.0, keep='+', cap=True, section_mat=None):
    d = ob.dimensions
    big = 4.0 * (max(d.x, d.y, d.z) + 1.0)
    if axis == 'Y':
        c = (0, value + (big / 2 if keep != '+' else -big / 2), 0)
        size = (big * 2, big, big * 2)
    elif axis == 'X':
        c = (value + (big / 2 if keep != '+' else -big / 2), 0, 0)
        size = (big, big * 2, big * 2)
    else:
        c = (0, 0, value + (big / 2 if keep != '+' else -big / 2))
        size = (big * 2, big * 2, big)
    tool = add_box('cut', *size, loc=c, m=section_mat)
    boolean(ob, tool, 'DIFFERENCE')
    if section_mat is not None:
        assign_plane_faces(ob, axis, value, section_mat)
    if cap:
        cap_holes(ob, section_mat)
    return ob


# ---------------------------------------------------------------- 单位 / 导出
def finalize_meters(objs):
    """把网格从 mm 缩到 m（1:1），并把场景单位改回 1 BU = 1 m。"""
    sc = bpy.context.scene
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = 'MILLIMETERS'
    for o in objs:
        if o.type != 'MESH':
            continue
        o.scale = (MM, MM, MM)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.select_set(False)


def strip_scene_helpers():
    for o in list(bpy.data.objects):
        if o.type in ('LIGHT', 'CAMERA') or o.name.startswith('QA_'):
            bpy.data.objects.remove(o, do_unlink=True)


def save_blend(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print('SAVED', path)


def export_glb(path, objs=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for o in bpy.context.view_layer.objects:      # 被排除的集合（配件）不在视图层里，不能选
        o.select_set(objs is None or o in objs)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=False,
                              export_apply=True, export_yup=True)
    print('GLB', path, os.path.getsize(path))


def export_stl(path, objs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    select(objs)
    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                              global_scale=1000.0, apply_modifiers=True)
    except Exception:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True, global_scale=1.0)
    print('STL', path, os.path.getsize(path))


def select(objs):
    for o in bpy.data.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


# ---------------------------------------------------------------- 渲染
def studio(bg=0.93, strength=0.25, ground_z=-0.0022, ground=True):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    n = w.node_tree.nodes.get('Background')
    n.inputs[0].default_value = (bg, bg * 1.005, bg * 1.02, 1)
    n.inputs[1].default_value = strength
    if ground:
        g = add_box('QA_Ground', 2.4, 2.4, 0.004, loc=(0, 0, ground_z - 0.002),
                    m=mat('M_ground', (0.86, 0.87, 0.89), 0.75))
        g.name = 'QA_Ground'
    return sc


def _area(name, loc, energy, size, color=(1, 1, 1), target=(0, 0, 0.015)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.size = size
    d.color = color
    o = bpy.data.objects.new('QA_' + name, d)
    link(o)
    o.location = loc
    look_at(o, target)
    return o


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def lights(target=(0, 0, 0.015)):
    """影棚三灯（米制坐标 / 瓦）。"""
    _area('key', (-0.26, -0.28, 0.33), 8.0, 0.30, (1, .97, .92), target)
    _area('fill', (0.30, -0.14, 0.24), 3.5, 0.26, (.82, .90, 1), target)
    _area('rim', (0.0, 0.30, 0.30), 4.5, 0.22, (1, .95, .90), target)


def setup_render(res=(1500, 1120), samples=48, transparent=False, exposure=-0.4):
    sc = bpy.context.scene
    for e in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = e
            break
        except TypeError:
            continue
    try:
        sc.eevee.taa_render_samples = samples
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.exposure = exposure
    sc.view_settings.look = 'AgX - Medium High Contrast' if sc.view_settings.view_transform == 'AgX' else 'None'
    return sc


def cam_persp(loc, target, lens=85.0):
    d = bpy.data.cameras.new('c')
    d.lens = lens
    d.clip_start, d.clip_end = 0.002, 200.0
    o = bpy.data.objects.new('QA_cam', d)
    link(o)
    o.location = loc
    look_at(o, target)
    bpy.context.scene.camera = o
    return o


def cam_ortho(view, target=(0, 0, 0.015), scale=0.34):
    d = bpy.data.cameras.new('c')
    d.type = 'ORTHO'
    d.ortho_scale = scale
    d.clip_start, d.clip_end = 0.002, 200.0
    o = bpy.data.objects.new('QA_cam', d)
    link(o)
    R = 1.2
    pos = {'front': (0, -R, target[2]), 'back': (0, R, target[2]),
           'left': (-R, 0, target[2]), 'right': (R, 0, target[2]),
           'top': (target[0], target[1], R)}[view]
    o.location = (pos[0] + target[0] if view in ('left', 'right') else pos[0],
                  pos[1] + target[1] if view in ('front', 'back', 'top') else pos[1],
                  pos[2])
    if view == 'top':
        o.rotation_euler = (0, 0, 0)
    else:
        look_at(o, target)
    bpy.context.scene.camera = o
    return o


def render_to(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('RENDER', path)
    return path


def clear_cameras():
    """只删相机，保留灯光。"""
    for o in list(bpy.data.objects):
        if o.type == 'CAMERA':
            bpy.data.objects.remove(o, do_unlink=True)


def clear_cams():
    """删相机 + 灯光（收尾用）。"""
    for o in list(bpy.data.objects):
        if o.type in ('CAMERA', 'LIGHT'):
            bpy.data.objects.remove(o, do_unlink=True)
