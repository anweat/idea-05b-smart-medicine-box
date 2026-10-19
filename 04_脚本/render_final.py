import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'model','IDEA-05_box.blend'))
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.device='GPU'; sc.cycles.samples=80; sc.cycles.use_denoising=True
sc.render.resolution_x=1600; sc.render.resolution_y=1200; sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
try: sc.view_settings.look='AgX - Medium High Contrast'
except: pass
sc.view_settings.exposure=0.0

# background
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs[0].default_value=(0.86,0.845,0.82,1); bg.inputs[1].default_value=0.32

def matte(name,col,rough=0.6):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*col,1); p.inputs['Roughness'].default_value=rough
    return m

# studio floor + backdrop (hide for ortho views)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0.16,0.14,-0.0021))
floor=bpy.context.object; floor.name='Floor'; floor.data.materials.append(matte('FloorMat',(0.85,0.83,0.79),0.6))
bpy.ops.mesh.primitive_plane_add(size=4, location=(0.16,1.1,0.45), rotation=(math.radians(90),0,0))
bd=bpy.context.object; bd.name='Backdrop'; bd.data.materials.append(matte('BackMat',(0.88,0.86,0.83),0.8))

def area(name,loc,energy,size,color=(1,1,1),target=(0.16,0.035,0.035)):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.size=size; d.color=color
    o=bpy.data.objects.new(name,d); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    return o
area('Key',(0.52,-0.52,0.62),55,0.55,(1.0,0.97,0.92))
area('Fill',(-0.42,-0.42,0.26),14,0.8,(0.88,0.94,1.0))
area('Rim',(-0.08,0.60,0.42),30,0.35,(1.0,0.95,0.88))
area('Top',(0.16,0.10,0.95),10,0.7,(1,1,1))
area('FrontFill',(0.16,-0.75,0.045),18,0.8,(1.0,0.98,0.95),(0.16,0.0,0.035))
# warm guide light
gl=bpy.data.lights.new('Guide','AREA'); gl.energy=1.2; gl.size=0.03; gl.color=(1.0,0.68,0.32)
glo=bpy.data.objects.new('Guide',gl); sc.collection.objects.link(glo); glo.location=(0.1156,0.030,0.058)
glo.rotation_euler=(math.radians(180),0,0)
pl=bpy.data.lights.new('CupGlow','POINT'); pl.energy=0.30; pl.color=(1.0,0.60,0.26); pl.shadow_soft_size=0.009
g2=bpy.data.objects.new('CupGlow',pl); sc.collection.objects.link(g2); g2.location=(0.1156,0.033,0.034)

def camera(name,loc,target,lens=80,ortho=None):
    cd=bpy.data.cameras.new(name); cd.lens=lens
    if ortho: cd.type='ORTHO'; cd.ortho_scale=ortho
    o=bpy.data.objects.new(name,cd); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    return o
cam_hero=camera('CamHero',(0.300,-0.560,0.400),(0.150,0.030,0.055),lens=58)
cam_front=camera('CamFront',(0.16,-1.0,0.030),(0.16,0.035,0.030),lens=80,ortho=0.365)
cam_top=camera('CamTop',(0.16,0.035,1.0),(0.16,0.035,0.0),lens=80,ortho=0.375)
cam_exp=camera('CamExp',(0.54,-0.50,0.45),(0.16,0.033,0.075),lens=56)
cam_cup=camera('CamCup',(0.174,-0.118,0.052),(0.116,0.036,0.036),lens=48)

def lid2(open_=True,ang=50):
    o=bpy.data.objects.get('Lid_2')
    if o: o.rotation_euler=(math.radians(-ang),0,0) if open_ else (0,0,0)

def render(name,cam,res=(1600,1200),show_env=True):
    floor.hide_render=not show_env; bd.hide_render=not show_env
    sc.camera=cam; sc.render.resolution_x,sc.render.resolution_y=res
    sc.render.filepath=os.path.join(ROOT,'renders',name)
    bpy.ops.render.render(write_still=True); print('RENDERED',name)

def explode():
    dz={'lids':0.085,'cups':0.065,'tray':0.045,'internals':0.025,'pills':0.065}
    for o in bpy.data.objects:
        n=o.name
        if n.startswith('Lid_'): o.location.z+=dz['lids']
        elif n.startswith('Cup_') or n.startswith('CupWin_') or n=='GuideDisk': o.location.z+=dz['cups']
        elif n.startswith('Pill'): o.location.z+=dz['pills']
        elif n in ('Tray','HingeRail') or n.startswith('Gasket') or n.startswith('Hinge_') or n.startswith('TrayDay'): o.location.z+=dz['tray']
        elif n in ('Battery','BattTxt','PCB','LoadCell','SensorPlate','Speaker','Desiccant'): o.location.z+=dz['internals']

def cup_detail():
    keep=('Cup_2','CupWin_2','GuideDisk')
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        if o.name.startswith('Pill'): continue
        if o.name in keep: continue
        o.hide_render=True
    # simple platform under cup
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.1156,0.02,0.0255))
    pl2=bpy.context.object; pl2.name='CupStand'; pl2.scale=(0.06,0.07,1)
    pl2.data.materials.append(matte('Stand',(0.9,0.88,0.84),0.55))

if __name__=='__main__':
    import sys
    mode=sys.argv[-1]
    if mode=='hero':
        lid2(True,50); render('hero',cam_hero,show_env=True)
    elif mode=='front':
        lid2(False); render('front',cam_front,show_env=False)
    elif mode=='top':
        lid2(False); render('top',cam_top,show_env=False)
    elif mode=='exp':
        lid2(True,50); explode(); sc.view_settings.exposure=-0.45; render('exploded',cam_exp,show_env=True)
    elif mode=='cup':
        lid2(False); cup_detail(); sc.view_settings.exposure=-0.85
        bg.inputs[0].default_value=(0.55,0.54,0.52,1)
        floor.data.materials.clear(); floor.data.materials.append(matte('DarkFloor',(0.42,0.41,0.39),0.6))
        render('cup_detail',cam_cup,show_env=True)
