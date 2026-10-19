from PIL import Image, ImageDraw, ImageFont
import os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F='/System/Library/Fonts/Hiragino Sans GB.ttc'
def f(sz,w=0): return ImageFont.truetype(F,sz,index=(2 if w else 0))
INK=(31,41,55); GREY=(110,122,138); ACC=(15,123,108); HOT=(224,122,50); LINE=(218,225,233)
BG=(244,246,249); CARD=(255,255,255)

W,H=2000,1250
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)

def card(x,y,w,h,r=18):
    d.rounded_rectangle([x+2,y+4,x+w+2,y+h+4],radius=r,fill=(232,236,241))
    d.rounded_rectangle([x,y,x+w,y+h],radius=r,fill=CARD,outline=(228,233,240),width=2)

def fit(path,box_w,box_h,crop=None):
    img=Image.open(path).convert('RGB')
    if crop: img=img.crop(crop)
    iw,ih=img.size; sc=min(box_w/iw,box_h/ih)
    return img.resize((int(iw*sc),int(ih*sc)),Image.LANCZOS)

def paste_fit(path,x,y,w,h,crop=None):
    img=fit(path,w,h,crop); im.paste(img,(x+(w-img.width)//2,y+(h-img.height)//2))

def txt(x,y,s,sz=20,color=INK,bold=False,anchor='la'):
    d.text((x,y),s,font=f(sz,1 if bold else 0),fill=color,anchor=anchor)

# header
txt(40,30,'IDEA-05  智能药盒 · 7 格演进版',46,INK,True)
txt(42,92,'SMART MEDICINE BOX  ·  RETRIEVAL + SENSING UPGRADE  ·  320 × 70 × 52 mm',19,GREY)
txt(1960,36,'2026.10  ·  已确认方案',18,GREY,False,'ra')
d.line([(40,124),(1960,124)],fill=(210,218,228),width=2)

# hero
card(40,142,1140,668)
paste_fit(os.path.join(R,'renders/hero.png'),52,154,1116,600,crop=(120,250,1560,1120))
txt(60,760,'① 可取出药杯  ② 7 个独立日盖  ③ 段码屏 + 3 键  ④ 7 格导光 / 7 天进度',17,GREY)

# right: upgrades
card(1200,142,760,330)
txt(1224,158,'核心升级',26,INK,True)
ups=[('01','同尺寸 7 格 → 7 只可取出药杯；浅口 15 mm、前唇 5 mm、24 mm 倒药口'),
     ('02','取药两条路：斜插指取 3 步；提杯倾倒 2 步，手抖/关节炎也能完成'),
     ('03','称重只承托药芯：装药逐格标定，取药前后差重校验，输出三态'),
     ('04','SHT40 温湿度 + 光照 + IP54 密封 + 可换干燥剂，超限给动作'),
     ('05','段码屏 + 3 键 + 7 天进度 + 7 格导光；离线优先，断网可用'),
     ('06','离线语音唤醒 + 亲情语音；长者端零账号 / 家属端管理')]
y=198
for n,t in ups:
    d.rounded_rectangle([1224,y+2,1252,y+26],radius=7,fill=(238,246,244),outline=(190,216,210))
    txt(1238,y+13,n,13,ACC,True,'mm')
    txt(1262,y+2,t,16.5,INK)
    y+=42

# right: spec table
card(1200,492,760,318)
txt(1224,508,'产品参数',26,INK,True)
rows=[('外形尺寸','320 × 70 × 52 mm，圆角 R8'),('空机重量','≤ 380 g（含一周药约 430 g）'),
      ('格数 / 药杯','7 格（周一–周日）；单杯 41.9 × 54 × 15 mm'),
      ('称重','500 g 单点式 + HX711；0.2–0.5 g，装药基线'),
      ('环境','SHT40 + VEML7700 + 硅胶密封（目标 IP54）+ 干燥剂'),
      ('交互','58 × 18 段码屏 + 主键 22 mm + 2 副键 + 7 灯'),
      ('语音','SU-03T 离线唤醒 + MEMS 麦克风 + 8 Ω 2 W'),
      ('电源','3.7 V 3000 mAh；Type-C + 磁吸 pogo 底座'),]
y=548
for i,(k,v) in enumerate(rows):
    if i%2==0: d.rounded_rectangle([1220,y-4,1940,y+26],radius=6,fill=(247,249,252))
    txt(1228,y,k,16,GREY)
    txt(1400,y,v,16,INK)
    y+=32

# bottom cards
def bottom_card(x,title,path,crop=None,sub=''):
    card(x,830,430,300)
    txt(x+20,844,title,21,INK,True)
    paste_fit(path,x+20,876,390,210,crop=crop)
    if sub: txt(x+20,1098,sub,15,GREY)
bottom_card(40,'正视图 · 控制带 / 7 日标签',os.path.join(R,'renders/front.png'),crop=(60,430,1540,790),sub='段码屏 08:30 · 已服药主键 · 状态灯 · 语音播报')
bottom_card(490,'俯视图 · 7 个烟灰日盖',os.path.join(R,'renders/top.png'),crop=(80,390,1520,800),sub='周一–周日；按压弹开；日盖可整排取下')
bottom_card(940,'爆炸图 · 6 层',os.path.join(R,'renders/exploded.png'),crop=(300,140,1360,1060),sub='日盖 / 药杯 / 托盘 / 称重传感 / 主板电池 / 底壳')
card(1390,830,570,300)
txt(1410,844,'取药几何 · 前唇 + 倒药口',21,INK,True)
paste_fit(os.path.join(R,'design/05_retrieval_geometry.png'),1410,876,530,180,crop=(540,250,1500,780))
txt(1410,1064,'浅口 15 mm · 前唇 5 mm · 24 mm 倒药口 · 杯底 10×24 透光窗',15,GREY)
txt(1410,1088,'指腹落点距唇口 5 mm；提杯倾斜 40–50° 可整粒倒出',15,GREY)

# footer
d.line([(40,1150),(1960,1150)],fill=(210,218,228),width=2)
txt(40,1164,'IDEA-05B  ·  7 格演进版  ·  取药几何 B+C  ·  主机 + 药芯 + 爆炸 + 渲染  ·  Blender 5.2  /  GLB',16,GREY)
txt(1960,1164,'320 × 70 × 52 mm  ·  7 剂/周  ·  BOM ≈ ¥160–180',16,GREY,False,'ra')

im.save(os.path.join(R,'design/09_IDEA-05B_design_board.png'))
print('board saved', im.size)
