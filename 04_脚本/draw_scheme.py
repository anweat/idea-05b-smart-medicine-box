import sys, math
sys.path.insert(0, 'tools')
from draw_lib import Sheet
from PIL import Image

INK='#25303F'; DIM='#1D6FD6'; GREY='#7A8699'; ACC='#0F7B6C'; HOT='#F08A3C'
GLASS=(204,225,240,185); GLASS2=(222,237,246,140); BODY='#E8EDF3'

W,D,H=320.0,70.0,52.0
BASE_H,TRAY_H,CAN_H=24.0,18.0,10.0
SIDE,FB,BB=5.0,4.0,4.0
LIDW,LIDD=310.0,62.0
LW=(LIDW-6*1.0)/7
CELLW,CELLD,GAP=41.93,16.83,1.5
PY=(LIDD-4-3*CELLD-2*GAP)/2
DAY=['周一','周二','周三','周四','周五','周六','周日']
DOSE=['早','中','晚']

def lx(i): return SIDE+i*(LW+1.0)
def cx(i): return lx(i)+(LW-CELLW)/2
def cy(r): return BB+2+PY+(2-r)*(CELLD+GAP)

def tag(s,x,y,n):
    s.circle(x,y,2.5,fill='#FFFFFF',outline=DIM,width=0.55)
    s.text(x,y+0.15,str(n),size=2.7,fill=DIM,anchor='mm',bold=True)

def legend(s,x,y,items,size=2.55,row=10.5,title=None):
    if title:
        s.text(x,y-7,title,size=3.0,fill=INK,bold=True); y+=2
    for n,txt in items:
        tag(s,x,y,n)
        s.text(x+5.5,y,txt,size=size,fill=INK,anchor='lm')
        ny=y+row
        # advance by number of lines
        y=ny + (txt.count('\n'))*row*0.72
    return y

def top_view():
    s=Sheet(470,180,ppm=6,ss=2); s.origin(34,48)
    s.rrect(0,0,W,D,8,fill=BODY,outline=INK,width=0.55)
    s.rrect(1.8,1.8,W-3.6,D-3.6,6.6,fill='#EEF2F7',outline='#C0CAD6',width=0.3)
    s.rrect(SIDE,BB,LIDW,LIDD,4,fill='#E9EFF6',outline='#A9B6C6',width=0.35)
    s.dashdot([(SIDE,BB+0.3),(SIDE+LIDW,BB+0.3)],fill='#8A94A6',width=0.35)
    for i in range(7):
        x=lx(i)
        s.rrect(x,BB,LW,LIDD,4,fill=GLASS,outline='#5E7C95',width=0.45)
        s.line([(x+2.5,BB+2.2),(x+LW-2.5,BB+2.2)],fill=(255,255,255,150),width=0.5)
        for r in range(3):
            due=(i==2 and r==0)
            s.rrect(cx(i),cy(r),CELLW,CELLD,2.4,
                    fill=(255,214,168,215) if due else (252,253,255,160),
                    outline=HOT if due else '#9FB0C2',width=0.5 if due else 0.25)
            if due: s.rrect(cx(i)-1,cy(r)-1,CELLW+2,CELLD+2,3.2,outline=(240,138,60,110),width=0.5)
        s.line([(x+LW/2,BB-0.5),(x+LW/2,BB-6)],fill='#90A0B2',width=0.35)
        s.text(x+LW/2,BB-13,DAY[i],size=3.4,fill='#2C4A63',anchor='mm',bold=True)
        s.rrect(x+LW/2-12,66.4,24,4.6,1.8,fill='#F7FAFC',outline='#52708A',width=0.4)
        for k in (-2.0,0,2.0): s.line([(x+LW/2+k,68.0),(x+LW/2+k,69.6)],fill='#8B9AAB',width=0.3)
    for r in range(3): s.text(-7,cy(r)+CELLD/2,DOSE[r],size=4.2,fill=ACC,anchor='rm',bold=True)
    # dims
    s.dim_h(0,W,84,'320',size=3.8)
    s.dim_v(0,D,334,'70',size=3.8,left=False)
    # tags
    tag(s,cx(2)+CELLW/2,63.5,1)
    tag(s,lx(4)+LW/2,68.7,2)
    tag(s,lx(6)+LW-4.5,BB+4.5,3)
    tag(s,cx(5)+CELLW-5,cy(2)+CELLD/2,4)
    tag(s,lx(0)+5,cy(1)+CELLD/2,5)
    legend(s,344,8,[
        (1,'21 格 = 7 天 × 3 剂（早/中/晚）\n单格 41.9 × 16.8 × 15 mm ≈ 10.6 ml'),
        (2,'7 个独立日盖：按压弹开（<3 N）\n阻尼下放，单手可开'),
        (3,'透明 PC 日盖（可选琥珀避光版）\n阻隔 400 nm 以下紫外'),
        (4,'每格独立：引导灯 + 红外余量检测\n磁吸辅助合盖 + 霍尔开盖记录'),
        (5,'可换药芯：7×1 / 7×2 / 7×3\n共用同一底座，抽出即可水洗'),
    ])
    s.text(0,-40,'IDEA-05  21 格换芯药盒 · 顶视图（1:1 设计稿，单位 mm）',size=5.6,fill=INK,bold=True)
    s.text(0,-31,'TOP VIEW  ·  320 × 70 × 52 mm  ·  共用底座 + 可换药芯',size=3.1,fill=GREY)
    s.save('design/01_top_layout.png',out_w=s.W//2)

def front_view():
    s=Sheet(470,150,ppm=8,ss=2); s.origin(34,38)
    y0,y1,y2=0.0,CAN_H,CAN_H+TRAY_H
    s.rrect(0,0,W,H,8,fill=BODY,outline=INK,width=0.55)
    s.rect(6,y0,W-12,CAN_H,fill=GLASS)
    s.rect(6,y1,W-12,TRAY_H,fill='#EEF2F6')
    s.rect(6,y2,W-12,BASE_H,fill='#F3F5F8')
    for yy in (y1,y2): s.line([(2,yy),(W-2,yy)],fill='#9AA8B8',width=0.4)
    for i in range(7):
        x=lx(i)
        s.rrect(x,y0+1.2,LW,CAN_H-2.4,2.0,fill=GLASS2,outline='#7E94A8',width=0.4)
        s.text(x+LW/2,y0+CAN_H/2+0.4,DAY[i],size=3.4,fill='#274A66',anchor='mm',bold=True)
        s.rrect(x+0.9,y1+1.4,LW-1.8,TRAY_H-2.8,2.2,fill=(226,238,246,185),outline='#B3C1D0',width=0.3)
        s.rrect(x+LW/2-12,y0-1.5,24,3.4,1.4,fill='#F8FBFD',outline='#52708A',width=0.35)
    bx,by,br=100,y2+BASE_H/2,10.4
    # display
    s.rrect(14,y2+3.2,58,17.6,1.8,fill='#0F151C',outline='#4A5666',width=0.45)
    s.text(17,y2+4.8,'08:30',size=4.6,fill='#F4F7FA',bold=True)
    s.text(17,y2+14.9,'周三 · 早 3 粒',size=1.7,fill='#9FB4C6')
    s.rrect(60,y2+5.2,5.4,2.7,0.6,outline='#9FB4C6',width=0.25)
    s.rect(65.4,y2+5.9,1.0,1.4,fill='#9FB4C6'); s.rect(60.8,y2+6.0,3.2,1.2,fill='#7FD3B4')
    # secondary keys
    s.circle(128,by,6.0,fill='#F7F9FC',outline='#9EADBE',width=0.4)
    s.text(128,by+0.1,'稍后',size=1.9,fill='#5B6C80',anchor='mm')
    s.circle(146,by,6.0,fill='#FDF3F0',outline='#C98A78',width=0.4)
    s.text(146,by+0.1,'呼叫',size=1.9,fill='#A2563F',anchor='mm')
    # weekday dots
    for k in range(7):
        s.circle(172+k*5.6,by-2.0,1.2,fill=DIM if k<5 else '#B7C3D0')
        s.text(172+k*5.6,by+2.6,'一二三四五六日'[k],size=1.55,fill=GREY,anchor='ma')
    # button
    s.circle(bx,by,br+1.6,fill='#E9EEF4',outline='#C2CCD8',width=0.4)
    s.circle(bx,by,br,fill='#FDFDFD',outline='#93A2B3',width=0.5)
    s.circle(bx,by,4.4,fill=None,outline=(15,123,108,160),width=1.0)
    # status LED
    s.circle(226,by-1.0,2.0,fill='#7FD3B4',outline='#5FA98F',width=0.3)
    # mic + speaker
    s.circle(240,by,0.9,fill='#4B5A6B')
    gx,gy=258,y2+6.0
    for r in range(3):
        for c in range(5): s.circle(gx+c*4.2,gy+r*4.2,0.85,fill='#4B5A6B')
    s.text(268,y2+21.0,'语音播报 / 拾音',size=1.7,fill=GREY,anchor='ma')
    # logo mark
    s.text(200,y2+8.6,'S M A R T   C A R E',size=1.5,fill='#96A2B1')
    # dims
    s.dim_h(0,W,64,'320',size=3.8)
    s.dim_v(0,H,-9,'52',size=3.8)
    s.dim_v(y0,CAN_H,332,'10',size=2.6,left=False)
    s.dim_v(CAN_H,CAN_H+TRAY_H,332,'18',size=2.6,left=False)
    s.dim_v(CAN_H+TRAY_H,H,332,'24',size=2.6,left=False)
    for n,(x,y) in {1:(42,33.6),2:(112,33.4),3:(137,33.2),4:(200,33.4),5:(226,by+4.6),6:(244,33.4),7:(268,gy+10.0)}.items():
        tag(s,x,y,n)
    legend(s,344,2,[
        (1,'段码屏：时间 / 下一剂 / 温湿度\n强光可读，暗处自动调光'),
        (2,'⌀22 主键（0.8–2 N）：短按“已服药”\n长按“重播语音”'),
        (3,'⌀12 副键：“稍后提醒 / 呼叫家属”'),
        (4,'7 天进度灯：本周完成情况一眼可见'),
        (5,'状态灯：绿=已确认，橙=待服，红=漏服'),
        (6,'MEMS 麦克风：离线唤醒“小药盒”'),
        (7,'8Ω 2W 扬声器：75 dB、1–2 kHz 增强\n支持家属录音“亲情语音”'),
    ],size=2.45,row=10.2)
    s.text(0,-14,'IDEA-05  正视图 · 控制带 / 药格前窗 / 透明日盖',size=5.2,fill=INK,bold=True)
    s.save('design/02_front_view.png',out_w=s.W//2)

def section():
    s=Sheet(250,170,ppm=10,ss=2); s.origin(30,34)
    yc,yt,yb=0.0,CAN_H,CAN_H+TRAY_H
    s.rrect(0,0,D,H,6,fill=BODY,outline=INK,width=0.6)
    # canopy
    s.rrect(4,1.0,D-8,CAN_H-1.8,3.0,fill=GLASS,outline='#7E94A8',width=0.45)
    s.rrect(4.4,CAN_H-1.4,D-8.8,1.2,0.6,fill=(112,122,134,200))
    # tray
    s.rrect(2,yt,D-4,TRAY_H,2.6,fill='#F2F4F7',outline='#8794A4',width=0.45)
    # cells
    for r in range(3):
        rx=4+PY+r*(CELLD+GAP)
        due=(r==0)
        s.rrect(rx,yt+1.4,CELLD,15.0,2.0,
                fill=(255,219,178,215) if due else '#FBFCFE',
                outline=HOT if due else '#A9B7C6',width=0.5 if due else 0.3)
        if due:
            s.circle(rx+CELLD/2,yt+15.9,2.6,fill=(255,190,120,130))
            s.circle(rx+5.3,yt+8.6,1.5,fill='#F6E7C8',outline='#C9A96A',width=0.25)
            s.circle(rx+9.2,yt+7.8,1.5,fill='#F6E7C8',outline='#C9A96A',width=0.25)
            s.circle(rx+12.0,yt+10.0,1.4,fill='#F6E7C8',outline='#C9A96A',width=0.25)
        s.text(rx+CELLD/2,yt+13.3,DOSE[r],size=2.0,fill='#7B8A9B',anchor='mm')
    # base
    s.rect(3,yb-0.4,D-6,0.8,fill=(112,122,134,200))       # gasket
    s.rect(8,yb+0.4,30,1.8,fill='#C9D3DE',outline='#7E8B9B',width=0.3)  # platform
    s.rrect(24,yb+2.6,8,3.0,0.8,fill='#B9C6D4',outline='#6E7C8D',width=0.3)  # load cell
    s.rect(3,yb+6.4,D-6,1.5,fill='#A9CBB9',outline='#5E8B75',width=0.25)   # sensor pcb
    s.rrect(6,yb+10.8,28,6.0,1.3,fill='#F1D98A',outline='#B79A3E',width=0.3) # battery
    s.rect(38,yb+11.0,24,1.4,fill='#3E7C5E',outline='#24503B',width=0.25)   # pcb
    s.rrect(44,yb+17.2,18,3.8,1.0,fill='#D8E8F6',outline='#6E93B4',width=0.3) # desiccant
    for fx in (10,D-15): s.rrect(fx,yb+20.6,5.0,2.2,1.0,fill='#5B6878')
    for px in (54,60): s.circle(px,yb+20.9,1.3,fill='#C9A227',outline='#8B6F14',width=0.25)
    for px in (54,60): s.circle(px,yb+20.9,0.35,fill='#FFF3C4')
    # dims
    s.dim_v(0,H,-18,'52',size=3.4)
    s.dim_v(0,CAN_H,-8,'10',size=2.3)
    s.dim_v(CAN_H,CAN_H+TRAY_H,-8,'18',size=2.3)
    s.dim_h(0,D,59,'70',size=3.4)
    # tags
    tag(s,D/2,4.5,1); tag(s,10,yt+6,2); tag(s,D-6,23,3); tag(s,12,yb+1.3,4)
    tag(s,44,yb+7.1,5); tag(s,18,yb+13.8,6); tag(s,48,yb+11.7,7); tag(s,49,yb+19.1,8); tag(s,63,yb+19.1,9)
    legend(s,82,2,[
        (1,'透明 PC 日盖 + TPU 密封唇（IPX4）'),
        (2,'药格浅口 15 mm，前低后高斜面\n好倒、好抠、不撒'),
        (3,'可水洗药芯（食品级 PP）'),
        (4,'悬浮称重：取药前后称差 = 实际取药量'),
        (5,'SHT40 置于药仓侧壁，避开发热源'),
        (6,'电池与药仓间做隔热隔层'),
        (7,'离线语音 + BLE/WiFi 主控板'),
        (8,'可换干燥剂：按湿度趋势提醒更换'),
        (9,'磁吸 pogo 充电触点 + 防滑硅胶脚'),
    ],size=2.5,row=10.6)
    s.text(0,-20,'IDEA-05  横剖 A–A（过一日三格，单位 mm）',size=4.8,fill=INK,bold=True)
    s.save('design/03_section.png',out_w=s.W//2)

def compare():
    s=Sheet(470,300,ppm=6,ss=2); s.origin(34,54)
    # ---- current 7 slots ----
    s.rrect(0,0,W,D,8,fill=BODY,outline=INK,width=0.5)
    s.rrect(6,6,W-12,D-12,5,fill='#EEF2F7',outline='#C0CAD6',width=0.3)
    inner=(W-2*10-6*4)/7
    for i in range(7):
        s.rrect(10+i*(inner+4),9,inner,D-24,2.6,fill=(236,244,250,255),outline='#8FA2B6',width=0.3)
    s.rect(10,55,W-20,8,fill='#E3E8EE')
    s.text(W/2,-9,'现状：7 格 · 每日 1 剂',size=3.8,fill=GREY,anchor='ma',bold=True)
    s.text(0,-34,'槽位方案对比：不改外形尺寸，把单周容量提升到 3 倍',size=4.6,fill=INK,bold=True)
    s.text(W/2,80,'320 × 70 × 52 mm · 7 剂 / 周',size=2.8,fill=GREY,anchor='ma')
    # ---- gap: arrow ----
    s.origin(34,146)
    s.text(W/2,0,'同尺寸内 7 → 21 格',size=5.4,fill=HOT,anchor='ma',bold=True)
    s.line([(W/2-40,8),(W/2-8,8)],fill=HOT,width=0.8); s.arrow(W/2-40,8,W/2-10,8,fill=HOT,width=0.8,head=3.0)
    s.line([(W/2+8,8),(W/2+40,8)],fill=HOT,width=0.8); s.arrow(W/2+40,8,W/2+10,8,fill=HOT,width=0.8,head=3.0)
    # ---- optimized 21 cells ----
    s.origin(34,170)
    s.rrect(0,0,W,D,8,fill=BODY,outline=INK,width=0.5)
    s.rrect(SIDE,BB,LIDW,LIDD,4,fill='#E9EFF6',outline='#A9B6C6',width=0.3)
    for i in range(7):
        s.rrect(lx(i),BB,LW,LIDD,4,fill=GLASS,outline='#5E7C95',width=0.35)
        for r in range(3):
            due=(i==2 and r==0)
            s.rrect(cx(i),cy(r),CELLW,CELLD,2.0,
                    fill=(255,214,168,215) if due else (252,253,255,150),
                    outline=HOT if due else '#9FB0C2',width=0.4 if due else 0.2)
        s.text(lx(i)+LW/2,BB-6.5,DAY[i],size=2.9,fill='#2C4A63',anchor='mm',bold=True)
    for r in range(3): s.text(-6,cy(r)+CELLD/2,DOSE[r],size=3.0,fill=ACC,anchor='rm',bold=True)
    s.text(W/2,-11,'优化：21 格 · 每日 3 剂（早 / 中 / 晚）',size=3.8,fill=ACC,anchor='ma',bold=True)
    s.text(W/2,80,'同尺寸 320 × 70 × 52 mm · 21 剂 / 周 · 容量 ×3',size=2.8,fill=ACC,anchor='ma')
    s.save('design/04_compare.png',out_w=s.W//2)

if __name__=='__main__':
    top_view(); front_view(); section(); compare(); print('ok')
