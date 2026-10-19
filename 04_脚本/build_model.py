import bpy, bmesh, math, os
from mathutils import Vector

MM=0.001
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'

# ---------------------------------------------------------------- utils
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)

def mat(name, color, rough=0.5, metal=0.0, trans=0.0, ior=1.45, emit=None, es=0.0, alpha=1.0, coat=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if 'IOR' in p.inputs: p.inputs['IOR'].default_value=ior
    if 'Transmission Weight' in p.inputs: p.inputs['Transmission Weight'].default_value=trans
    if 'Alpha' in p.inputs: p.inputs['Alpha'].default_value=alpha
    if 'Coat Weight' in p.inputs: p.inputs['Coat Weight'].default_value=coat
    if emit:
        p.inputs['Emission Color'].default_value=(*emit,1)
        p.inputs['Emission Strength'].default_value=es
    m.use_backface_culling=False
    return m

def assign(obj,m):
    obj.data.materials.clear(); obj.data.materials.append(m)

def smooth(obj, angle=38):
    for p in obj.data.polygons: p.use_smooth=True
    md=obj.modifiers.new('es','EDGE_SPLIT'); md.split_angle=math.radians(angle)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=md.name)

def apply_bevel(obj, w, seg=3, angle=32):
    md=obj.modifiers.new('bv','BEVEL'); md.width=w*MM; md.segments=seg
    md.limit_method='ANGLE'; md.angle_limit=math.radians(angle)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=md.name)

def rr_profile(w,d,r,seg=8):
    pts=[]; hw,hd=w/2,d/2
    cs=[(hw-r,hd-r,0),(-hw+r,hd-r,90),(-hw+r,-hd+r,180),(hw-r,-hd+r,270)]
    for cx,cy,a0 in cs:
        for i in range(seg):
            a=math.radians(a0+i*90/seg)
            pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts

def prism(name,w,d,h,r,loc,m=None,bevel=0.0,seg=8):
    pts=rr_profile(w,d,r,seg)
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bot=[bm.verts.new((x*MM,y*MM,-h/2*MM)) for x,y in pts]
    top=[bm.verts.new((x*MM,y*MM, h/2*MM)) for x,y in pts]
    n=len(pts)
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        j=(i+1)%n
        bm.faces.new((bot[i],bot[j],top[j],top[i]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    ob.location=(loc[0]*MM,loc[1]*MM,loc[2]*MM)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active=ob
    if m: assign(ob,m)
    if bevel>0: apply_bevel(ob,bevel)
    smooth(ob)
    return ob

def boolean(obj,cutter,op='DIFFERENCE'):
    md=obj.modifiers.new('bool','BOOLEAN'); md.object=cutter; md.operation=op; md.solver='EXACT'
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def cyl(name,r,h,loc,axis='Z',m=None,verts=48,bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r*MM,depth=h*MM,location=(loc[0]*MM,loc[1]*MM,loc[2]*MM))
    ob=bpy.context.object; ob.name=name
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    if axis=='Y': ob.rotation_euler=(math.radians(90),0,0)
    if axis=='X': ob.rotation_euler=(0,math.radians(90),0)
    if m: assign(ob,m)
    if bevel>0: apply_bevel(ob,bevel,2)
    smooth(ob)
    return ob

def text_mesh(name, body, size_mm, loc, rot=(0,0,0), m=None, extrude=0.15, align='CENTER'):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body
    try: cu.font=bpy.data.fonts.load(FONT)
    except: pass
    cu.size=size_mm*MM; cu.extrude=extrude*MM; cu.align_x=align; cu.align_y='CENTER'
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob)
    ob.location=(loc[0]*MM,loc[1]*MM,loc[2]*MM); ob.rotation_euler=rot
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    ob=bpy.context.object
    if m: assign(ob,m)
    return ob

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join()
    ob=bpy.context.object; ob.name=name
    return ob

# ---------------------------------------------------------------- scene
clear()
sc=bpy.context.scene
sc.unit_settings.system='METRIC'
sc.unit_settings.scale_length=1.0
sc.render.engine='CYCLES'
sc.cycles.device='GPU'
sc.cycles.samples=96
sc.cycles.use_denoising=True

# materials
M_WHITE  = mat('ABS warm white',(0.905,0.885,0.845),rough=0.40,coat=0.15)
M_WHITE2 = mat('ABS inner',(0.82,0.80,0.76),rough=0.55)
M_GLASS  = mat('PC smoked',(0.50,0.53,0.56),rough=0.04,trans=0.90,ior=1.49)
M_LABEL  = mat('Print light',(0.93,0.92,0.88),rough=0.5)
M_CUP    = mat('PP translucent',(0.90,0.93,0.94),rough=0.30,trans=0.42,ior=1.48)
M_TRAY   = mat('PP tray',(0.93,0.94,0.94),rough=0.45)
M_SIL    = mat('Silicone',(0.20,0.21,0.22),rough=0.62)
M_TPE    = mat('TPE foot',(0.22,0.22,0.23),rough=0.75)
M_GLASSBLK=mat('Display glass',(0.01,0.012,0.014),rough=0.06,coat=0.6)
M_BTN    = mat('Button PC',(0.955,0.955,0.95),rough=0.28,coat=0.25)
M_TEAL   = mat('Teal accent',(0.045,0.42,0.37),rough=0.35)
M_DARK   = mat('Dark plastic',(0.055,0.06,0.07),rough=0.5)
M_AL     = mat('Aluminium',(0.72,0.73,0.75),rough=0.32,metal=1.0)
M_GOLD   = mat('Gold',(0.85,0.66,0.28),rough=0.25,metal=1.0)
M_PCB    = mat('PCB',(0.04,0.24,0.15),rough=0.5)
M_BATT   = mat('Battery',(0.55,0.60,0.66),rough=0.45,metal=0.25)
M_IVORY  = mat('Capsule ivory',(0.94,0.90,0.78),rough=0.28)
M_ORANGE = mat('Capsule orange',(0.88,0.52,0.24),rough=0.30)
M_WHITEP = mat('Tablet',(0.97,0.97,0.95),rough=0.35)
M_TEXT   = mat('Print dark',(0.02,0.024,0.03),rough=0.5)
M_LED_W  = mat('LED warm',(1.0,0.78,0.45),rough=0.3,emit=(1.0,0.70,0.35),es=9.0)
M_LED_T  = mat('LED teal',(0.1,0.85,0.72),rough=0.3,emit=(0.06,0.75,0.62),es=4.0)
M_LED_DIM= mat('LED dim',(0.25,0.32,0.34),rough=0.4)
M_WIN    = mat('Window',(0.55,0.78,0.90),rough=0.2,emit=(0.35,0.65,0.85),es=0.25)

# ---------------------------------------------------------------- body shell
body=prism('BaseShell',320,70,24,8,(160,35,12),M_WHITE,bevel=2.2)
cav=prism('cav',306,56,28,6,(160,35,16),None,bevel=1.0)
boolean(body,cav)
# top rim chamfer already from bevel
# front display recess plate + USB slot + speaker etc. are added as separate objects

# ---------------------------------------------------------------- tray
tray=prism('Tray',310,62,18,4,(160,35,33),M_TRAY,bevel=0.9)
cup_cx=[26.715+i*44.43 for i in range(7)]
for cx in cup_cx:
    cut=prism('cut',42.3,54.4,20,3.5,(cx,35,35),None,bevel=0.5)
    boolean(tray,cut)
# soften cut edges lightly
apply_bevel(tray,0.25,2,angle=40)
for i,cx in enumerate(cup_cx):
    text_mesh(f'TrayDay_{i}',['周一','周二','周三','周四','周五','周六','周日'][i],4.6,(cx,3.75,31.5),rot=(math.radians(90),0,0),m=M_TEXT,extrude=0.12)

# ---------------------------------------------------------------- cups
cups=[]
for i,cx in enumerate(cup_cx):
    cup=prism(f'Cup_{i}',41.9,54,15,3.5,(cx,35,34),M_CUP,bevel=0.7)
    # inner cavity, sloped floor: front basin 30.5 (y<=20), main 31.5 (y>=20)
    # build cutter mesh
    w,d,r=38.7,50.8,2.6; seg=8
    pts=rr_profile(w,d,r,seg)
    me=bpy.data.meshes.new('cut'); bm=bmesh.new()
    bot=[]; top=[]
    for x,y in pts:
        wy=35+y
        fz = 30.5 if wy<20 else 31.5
        bot.append(bm.verts.new(((cx+x)*MM,wy*MM,fz*MM)))
        top.append(bm.verts.new(((cx+x)*MM,wy*MM,46*MM)))
    n=len(pts)
    bm.faces.new(list(reversed(top)))
    for k in range(n):
        j=(k+1)%n
        bm.faces.new((bot[k],bot[j],top[j],top[k]))
    c=bm.verts.new((cx*MM,35*MM,31.5*MM))
    for k in range(n):
        j=(k+1)%n
        bm.faces.new((bot[j],bot[k],c))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    cut=bpy.data.objects.new('cut',me); bpy.context.collection.objects.link(cut)
    boolean(cup,cut)
    # front spout: 24 wide, z 35.5..46, y 6..14
    sp=prism('sp',24,8,11,1.6,(cx,10,40.5),None,bevel=0.3)
    boolean(cup,sp)
    apply_bevel(cup,0.35,2,angle=40)
    smooth(cup,40)
    assign(cup,M_CUP)
    cups.append(cup)
    # cup bottom window (emissive for open cup)
    win=prism(f'CupWin_{i}',10,24,0.5,2.0,(cx,35,26.35),M_LED_W if i==2 else M_WIN,bevel=0.15)
    win.name=f'CupWin_{i}'

# ---------------------------------------------------------------- gasket rings
def frame_ring(name,w,d,r,thick,h,loc,m):
    po=rr_profile(w,d,r,8); pi=rr_profile(w-2*thick,d-2*thick,r-thick,8)
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    ob_=[]; ib_=[]; ot=[]; it=[]
    for x,y in po:
        ob_.append(bm.verts.new((x*MM,y*MM,-h/2*MM)))
        ot.append(bm.verts.new((x*MM,y*MM, h/2*MM)))
    for x,y in pi:
        ib_.append(bm.verts.new((x*MM,y*MM,-h/2*MM)))
        it.append(bm.verts.new((x*MM,y*MM, h/2*MM)))
    n=len(po)
    for k in range(n):
        j=(k+1)%n
        bm.faces.new((ob_[k],ob_[j],ot[j],ot[k]))
        bm.faces.new((ib_[j],ib_[k],it[k],it[j]))
        bm.faces.new((ot[k],ot[j],it[j],it[k]))
        bm.faces.new((ob_[j],ob_[k],ib_[k],ib_[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    ob.location=(loc[0]*MM,loc[1]*MM,loc[2]*MM); assign(ob,m); smooth(ob,50)
    return ob

for cx in cup_cx:
    frame_ring('Gasket',43.3,55.4,3.6,0.5,0.7,(cx,35,42.05),M_SIL)

# ---------------------------------------------------------------- hinge rail
prism('HingeRail',310,4,4.5,1.2,(160,65.8,43.4),M_DARK,bevel=0.6)

# ---------------------------------------------------------------- lids
lids=[]
for i,cx in enumerate(cup_cx):
    bpy.ops.object.select_all(action='DESELECT')
    lid=prism(f'Lid_{i}',43.4,62,9.5,6.0,(0,0,0),M_GLASS,bevel=2.2)
    # hollow it: inner cavity open at bottom
    cav_l=prism('lc',39.4,58,8.0,4.2,(0,0,0.2),None,bevel=0.6)
    boolean(lid,cav_l)
    apply_bevel(lid,0.4,2,angle=40)
    smooth(lid,40)
    assign(lid,M_GLASS)
    # shift mesh into hinge-local frame: y -62..0, z 0..9.5
    for v in lid.data.vertices:
        v.co.y -= 31*MM; v.co.z += 4.75*MM
    # handle
    hd=prism('Handle',26,8,4,1.6,(0,0,0),M_WHITE,bevel=0.8)
    for v in hd.data.vertices:
        v.co.y -= 56*MM; v.co.z += 11.6*MM
    bpy.ops.object.select_all(action='DESELECT')
    lid.select_set(True); hd.select_set(True); bpy.context.view_layer.objects.active=lid
    bpy.ops.object.join(); lid=bpy.context.object; lid.name=f'Lid_{i}'
    # day label
    t=text_mesh(f'Day_{i}',['周一','周二','周三','周四','周五','周六','周日'][i],7.0,(0,0,0),m=M_LABEL,extrude=0.2)
    for v in t.data.vertices:
        v.co.y -= 48*MM; v.co.z += 9.72*MM
    bpy.ops.object.select_all(action='DESELECT')
    lid.select_set(True); t.select_set(True); bpy.context.view_layer.objects.active=lid
    bpy.ops.object.join(); lid=bpy.context.object; lid.name=f'Lid_{i}'
    # hinge placement
    lid.location=(cx*MM,66*MM,42*MM)
    if i==2:
        lid.rotation_euler=(math.radians(-38),0,0)
    lids.append(lid)

# ---------------------------------------------------------------- control band + seam
ch=prism('ControlBand',306,21,0.8,4.0,(160,-0.15,12),M_WHITE2,bevel=0.4)
ch.rotation_euler=(math.radians(90),0,0)
frame_ring('Seam',319.4,69.4,7.9,0.5,0.32,(160,35,24.0),M_DARK)

# hinge knuckles
for i,cx in enumerate(cup_cx):
    for dx in (-16,16):
        cyl(f'Hinge_{i}_{dx}',2.1,4.2,(cx+dx,66,42),'X',M_DARK,verts=24)

# ---------------------------------------------------------------- front UI
# display plate + texture
disp=prism('Display',58,18,1.6,3.0,(43,-0.5,12),M_GLASSBLK,bevel=0.6)
disp.rotation_euler=(math.radians(90),0,0)
img=bpy.data.images.load(os.path.join(ROOT,'model','display_ui.png'))
img.pack()
ui_mat=bpy.data.materials.new('UI'); ui_mat.use_nodes=True
nt=ui_mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); em=nt.nodes.new('ShaderNodeEmission')
tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=img
nt.links.new(tex.outputs['Color'],em.inputs['Color']); em.inputs['Strength'].default_value=2.2
nt.links.new(em.outputs['Emission'],out.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=1,location=(43*MM,-1.35*MM,12*MM),rotation=(math.radians(90),0,0))
uip=bpy.context.object; uip.name='UI_Plane'; uip.scale=(54*MM,16.9*MM,1); assign(uip,ui_mat)

# buttons
cyl('BtnBezel',11.3,1.2,(96,-0.35,12),'Y',M_DARK,bevel=0.4)
b1=cyl('BtnMain',10,3.2,(96,-0.7,12),'Y',M_BTN,bevel=0.8)
ring=bpy.ops.mesh.primitive_torus_add(major_radius=5*MM,minor_radius=0.7*MM,location=(96*MM,-2.4*MM,12*MM),rotation=(math.radians(90),0,0))
r=bpy.context.object; r.name='BtnRing'; assign(r,M_TEAL); smooth(r,60)
cyl('BtnBezel2',6.9,1.0,(122,-0.4,12),'Y',M_DARK,bevel=0.3)
b2=cyl('BtnSnooze',6,2.6,(122,-0.6,12),'Y',M_BTN,bevel=0.6)
cyl('BtnBezel3',6.9,1.0,(140,-0.4,12),'Y',M_DARK,bevel=0.3)
b3=cyl('BtnCall',6,2.6,(140,-0.6,12),'Y',M_BTN,bevel=0.6)
# button labels
text_mesh('T1','已服药',2.8,(96,-2.42,12),rot=(math.radians(90),0,0),m=mat('LabelTeal',(0.02,0.26,0.23),rough=0.5),extrude=0.15)
text_mesh('T2','稍后',2.0,(122,-2.02,12),rot=(math.radians(90),0,0),m=M_TEXT,extrude=0.12)
text_mesh('T3','呼叫',2.0,(140,-2.02,12),rot=(math.radians(90),0,0),m=M_TEXT,extrude=0.12)
# progress leds
for k in range(7):
    mm = M_LED_T if k<5 else M_LED_DIM
    cyl(f'Pl_{k}',1.45,0.7,(166+k*6,-0.90,12),'Y',mm,verts=24)
cyl('StatusLed',2.0,0.8,(220,-0.90,12),'Y',M_LED_T,verts=24)
cyl('Mic',0.95,0.6,(234,-0.80,12),'Y',M_DARK,verts=24)
for rr_ in range(3):
    for cc in range(5):
        cyl(f'Spk_{rr_}{cc}',0.8,0.5,(258+cc*4.2,-0.85,8+rr_*4.2),'Y',M_DARK,verts=16)
# small brand
text_mesh('Brand','IDEA-05',3.0,(296,-0.68,5.0),rot=(math.radians(90),0,0),m=M_TEXT,extrude=0.12)

# USB-C slot
usb_cut=prism('usbc',10,3.6,10,1.6,(321,35,12),None,bevel=0.3)
boolean(body,usb_cut)
usb_in=prism('UsbInsert',8,3.2,3.0,1.2,(318,35,12),M_DARK,bevel=0.3)

# pogo pads
for yy in (31,39):
    for xx in (148,158):
        cyl('Pogo',1.35,0.5,(xx,yy,0.05),'Z',M_GOLD,verts=24)
# feet
for xx,yy in ((20,10),(300,10),(20,60),(300,60)):
    prism('Foot',12,7,2.2,2.0,(xx,yy,-1.0),M_TPE,bevel=0.6)

# back label plate
plate=prism('BackPlate',58,26,0.8,3.0,(160,69.4,11),M_WHITE2,bevel=0.4)
plate.rotation_euler=(math.radians(90),0,0)
text_mesh('BackTxt','IDEA-05  3.7V 3000mAh',2.4,(160,70.0,14),rot=(math.radians(-90),0,0),m=M_TEXT,extrude=0.1)

# ---------------------------------------------------------------- internals
batt=prism('Battery',95,52,8,3.0,(150,35,6),M_BATT,bevel=0.8)
text_mesh('BattTxt','3.7V 3000mAh',2.2,(150,10,6),rot=(math.radians(90),0,0),m=M_TEXT,extrude=0.08)
pcb=prism('PCB',260,50,1.6,2.0,(160,35,12),M_PCB,bevel=0.2)
lcell=prism('LoadCell',40,14,4,1.5,(160,35,18),M_AL,bevel=0.4)
splate=prism('SensorPlate',296,52,1.6,2.0,(160,35,21),M_PCB,bevel=0.2)
spk=cyl('Speaker',15,7,(272,35,8),'Z',M_DARK,bevel=0.4)
des=prism('Desiccant',40,20,8,2.0,(212,52,6),M_WHITE2,bevel=0.6)

# warm guide light disk
cyl('GuideDisk',9.0,0.4,(cup_cx[2],35,31.25),'Z',M_LED_W,verts=48)

# ---------------------------------------------------------------- pills in open cup
import random
random.seed(7)
cx=cup_cx[2]
pill_specs=[(-11,-12,33.6,M_IVORY,0),(-3,-7,33.4,M_ORANGE,25),(7,-11,33.6,M_IVORY,60),(-6,4,33.5,M_ORANGE,-20),(5,5,33.5,M_WHITE,40),(12,8,33.4,M_IVORY,-35),(-12,10,33.6,M_WHITE,15)]
for k,(dx,dy,z,mm,rot) in enumerate(pill_specs):
    if mm==M_WHITE:
        ob=cyl(f'PillT{k}',3.4,2.4,(cx+dx,35+dy,z),'Z',mm,verts=32,bevel=0.5)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=3.0*MM,location=(0,0,0))
        ob=bpy.context.object; ob.name=f'PillC{k}'
        ob.scale=(1.0,1.0,1.9); assign(ob,mm); smooth(ob,60)
        ob.rotation_euler=(math.radians(rot),math.radians(90),0)
        ob.location=((cx+dx)*MM,(35+dy)*MM,z*MM)

# ---------------------------------------------------------------- collections
cols={'Body':[], 'Tray':[], 'Cups':[], 'Lids':[], 'Internals':[], 'Pills':[]}
for o in bpy.data.objects:
    if o.name.startswith('Lid_'): cols['Lids'].append(o)
    elif o.name.startswith('Cup_') or o.name.startswith('CupWin_'): cols['Cups'].append(o)
    elif o.name.startswith('Pill'): cols['Pills'].append(o)
for nm,objs in [('Lids',cols['Lids']),('Cups',cols['Cups']),('Pills',cols['Pills'])]:
    c=bpy.data.collections.new(nm); sc.collection.children.link(c)
    for o in objs:
        for cc in list(o.users_collection): cc.objects.unlink(o)
        c.objects.link(o)

# ---------------------------------------------------------------- save
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','IDEA-05_box.blend'))
print('SAVED', len(bpy.data.objects), 'objects')
