import sys, math
sys.path.insert(0, 'tools')
from draw_lib import Sheet

INK='#25303F'; DIM='#1D6FD6'; GREY='#7A8699'; ACC='#0F7B6C'; HOT='#F08A3C'
SKIN=(246,214,190,125); SKIN_D=(220,175,148,125); NAIL=(255,243,232,170)
CUP=(232,240,246,255); CUP_E='#5B7284'; CUTFILL='#F7FAFC'

def thick_path(s, pts, w, fill):
    for i in range(len(pts)-1):
        (x1,y1),(x2,y2)=pts[i],pts[i+1]
        L=math.hypot(x2-x1,y2-y1); n=max(1,int(L*3))
        for k in range(n+1):
            t=k/n; s.circle(x1+(x2-x1)*t, y1+(y2-y1)*t, w/2, fill=fill)

def finger(s, x0, y0, ang_deg, length=38, w=14):
    a=math.radians(ang_deg)
    pts=[(x0,y0)]
    pts.append((x0-length*0.45*math.cos(a), y0-length*0.45*math.sin(a)))
    pts.append((x0-length*1.0*math.cos(a), y0-length*1.0*math.sin(a)))
    thick_path(s, pts, w, SKIN)
    # pad (slightly darker) and nail at tip
    thick_path(s, [(x0,y0),(x0-w*0.22*math.cos(a),y0-w*0.22*math.sin(a))], w*0.68, SKIN_D)
    nx,ny=x0+2.0*math.cos(a-math.pi/2), y0+2.0*math.sin(a-math.pi/2)
    s.circle(nx,ny,1.8,fill=NAIL)

def capsule(s,x,y,r=3.0,l=9,rot=0):
    c=math.radians(rot); dx,dy=math.cos(c)*l/2, math.sin(c)*l/2
    s.line([(x-dx,y-dy),(x+dx,y+dy)],fill=(214,178,120),width=r*1.75)
    s.circle(x-dx,y-dy,r,fill=(240,208,154),outline=(180,140,86),width=0.25)
    s.circle(x+dx,y+dy,r,fill=(240,208,154),outline=(180,140,86),width=0.25)
    s.circle(x,y,r,fill=(240,208,154))

def tablet(s,x,y,r=3.0):
    s.circle(x,y,r,fill=(250,250,245),outline=(166,172,178),width=0.35)
    s.line([(x-r*0.65,y),(x+r*0.65,y)],fill=(198,204,210),width=0.25)

def tag(s,x,y,n):
    s.circle(x,y,2.4,fill='#FFFFFF',outline=DIM,width=0.5)
    s.text(x,y+0.1,str(n),size=2.6,fill=DIM,anchor='mm',bold=True)

# =========================================================== 05 section
def sheet_section():
    s=Sheet(240,74,ppm=16,ss=2); s.origin(20,14)
    s.text(0,-14,'IDEA-05  取药几何：浅口药杯 + 前唇倒药口 + 斜底',size=4.2,fill=INK,bold=True)
    s.text(0,-8.6,'单杯 41.9 × 54 × 15 mm  ·  内深 10–11 mm  ·  “斜向指取 + 提杯倾倒”双方式  ·  单位 mm',size=2.3,fill=GREY)
    X0=20.0; Z0=36.0
    def X(x): return X0+x
    def Z(z): return Z0-z
    s.rrect(X(0),Z(15),54,15,2.2,fill=CUP,outline=CUP_E,width=0.55)
    s.line([(X(1.6),Z(15)),(X(1.6),Z(9))],fill='#8FA6B8',width=2.0)
    s.line([(X(1.6),Z(9)),(X(1.6),Z(4))],fill='#8FA6B8',width=2.0)
    s.line([(X(1.6),Z(4)),(X(13.6),Z(5))],fill='#8FA6B8',width=2.0)
    s.line([(X(13.6),Z(5)),(X(52.4),Z(6))],fill='#8FA6B8',width=2.2)
    s.line([(X(52.4),Z(6)),(X(52.4),Z(15))],fill='#8FA6B8',width=2.2)
    s.rrect(X(-0.3),Z(9),1.4,9,0.6,fill='#CAD7E2',outline=CUP_E,width=0.4)
    s.circle(X(0.4),Z(9),1.4,fill='#CAD7E2',outline=CUP_E,width=0.35)
    s.rect(X(19),Z(1.4),16,1.4,fill=(174,214,232,255),outline='#7FA8C2',width=0.3)
    capsule(s,X(10),Z(7.2),r=2.8,l=8,rot=-7)
    tablet(s,X(20),Z(8.0),r=2.9)
    capsule(s,X(36),Z(9.4),r=2.6,l=7,rot=7)
    finger(s,X(8.0),Z(7.4),258,length=29,w=12.0)
    s.dim_h(X(0),X(54),Z(0)+10,'54',size=2.8)
    s.dim_v(Z(15),Z(0),X(0)-6,'15',size=2.8)
    s.text(X(33),Z(7.6),'3.4° + 前槽 4.8°',size=2.05,fill=HOT,anchor='ma')
    # brief inline labels
    s.text(X(2.5),Z(15)-2.6,'R2 唇口 5 mm',size=1.85,fill=CUP_E,anchor='lm')
    s.text(X(54)+1.5,Z(11.5),'R3 内角',size=1.85,fill=CUP_E,anchor='lm')
    s.text(X(27),Z(0)+4.0,'杯底透光窗 10×24',size=1.8,fill='#4F86A6',anchor='ma')

    lx=92; ly=2
    items=['前唇高 5 mm：静置挡药，倾倒时越过',
           '指腹落点距唇口仅 5 mm，35–45° 斜插即可触药',
           '微斜底 3.4° + 前部浅槽 4.8°：药向前聚集',
           '内壁 R3 / 底壁 R2，无锐边、不夹药',
           '杯底透光窗 10 × 24 mm：与 LED / 红外对位',
           '食品级 PP，壁厚 1.6 mm，可水洗']
    s.text(lx,ly,'设计要点',size=2.9,fill=INK,bold=True)
    for i,t in enumerate(items):
        y=ly+8+i*7.4
        s.circle(lx+1.6,y,1.6,fill='#E8F1F6',outline=DIM,width=0.35)
        s.text(lx+1.6,y+0.1,str(i+1),size=1.9,fill=DIM,anchor='mm',bold=True)
        s.text(lx+5.2,y,t,size=2.35,fill=INK,anchor='lm')
    s.text(lx,ly+56,'指取 3 步：开盖 → 斜插取药 → 合盖（3–5 s）',size=2.4,fill=ACC,bold=True)
    s.text(lx,ly+62,'倒取 2 步：提杯 → 倾斜 40° 倒出（手抖/关节炎）',size=2.4,fill=HOT,bold=True)
    s.save('design/05_retrieval_geometry.png',out_w=s.W//2)

# =========================================================== 06 options
def sheet_options():
    s=Sheet(300,200,ppm=9,ss=2); s.origin(22,34)
    s.text(0,-19,'取药几何方案对比：从“抠药”到“斜插入口 / 提杯倾倒”',size=4.6,fill=INK,bold=True)
    s.text(0,-12,'评价：步骤数 / 耗时 / 指力 / 可清洁性 / 成本 / 密封风险  ·  单位 mm',size=2.5,fill=GREY)

    def card(x,y,title,sub,col):
        s.rrect(x,y,130,50,3,fill='#FFFFFF',outline='#D6DEE7',width=0.5)
        s.text(x+4,y+6,title,size=2.9,fill=col,bold=True)
        s.text(x+4,y+10.4,sub,size=1.8,fill=GREY)
        return (x+6,y+15)

    # A deep well
    cx,cy=card(0,0,'A  现状：深格 + 垂直壁','深 25 mm ｜ 需下探、药贴底，指甲/关节吃力',GREY)
    s.rrect(cx,cy,110,28,2.2,fill=(238,243,247,255),outline=CUP_E,width=0.5)
    s.rrect(cx+1.6,cy+2,106.8,28,1.4,fill=CUTFILL,outline='#B7C6D2',width=0.3)
    tablet(s,cx+55,cy+24,r=2.8)
    s.arrow(cx+26,cy-2,cx+26,cy+7,fill=GREY,width=0.6,head=2.2)
    s.text(cx+28,cy+3,'下探',size=1.8,fill=GREY)
    s.text(cx+2,cy+31,'3 步 ｜ 5–10 s ｜ 失败率高',size=1.9,fill=GREY)

    # B sloped + lip
    cx,cy=card(150,0,'B  浅口 + 前唇（一体模）','深 15 mm ｜ 前部浅槽，可斜插；不可拆洗',ACC)
    s.rrect(cx,cy,110,15,2.2,fill=(238,243,247,255),outline=CUP_E,width=0.5)
    s.line([(cx+1.6,cy+5),(cx+108.4,cy+1)],fill='#8FA6B8',width=1.8)
    s.rrect(cx-0.2,cy+1,1.3,9,0.6,fill='#CAD7E2',outline=CUP_E,width=0.3)
    tablet(s,cx+12,cy+2.4,r=2.6)
    s.arrow(cx-2,cy+1.5,cx+12,cy+3.5,fill=ACC,width=0.6,head=2.2)
    s.text(cx+2,cy+31,'3 步 ｜ 3–5 s ｜ 成本最低',size=1.9,fill=ACC)

    # C removable cup
    cx,cy=card(0,64,'C  可取出药杯 + 倒药口（推荐）','斜插指取 + 提杯倾倒 ｜ 可水洗、可带走',HOT)
    s.rrect(cx,cy,110,15,2.2,fill=(232,240,246,255),outline=CUP_E,width=0.55)
    s.line([(cx+1.6,cy+5),(cx+108.4,cy+1)],fill='#8FA6B8',width=1.8)
    s.rrect(cx-0.2,cy+1,1.3,9,0.6,fill='#CAD7E2',outline=CUP_E,width=0.3)
    s.rrect(cx+110/2-9,cy-4,18,3.6,1.4,fill='#F7FAFC',outline=CUP_E,width=0.3)
    s.text(cx+110/2,cy-2.2,'提手',size=1.5,fill=GREY,anchor='mm')
    capsule(s,cx+18,cy+2.6,r=2.4,l=7,rot=-5)
    s.arrow(cx-2,cy+1.5,cx+12,cy+3.5,fill=HOT,width=0.6,head=2.2)
    s.arrow(cx+110/2,cy-6,cx+110/2,cy-1,fill=HOT,width=0.6,head=2.2)
    s.text(cx+2,cy+31,'3–5 步 ｜ 3–6 s ｜ +7 杯，+¥2–3',size=1.9,fill=HOT)

    # D silicone
    cx,cy=card(150,64,'D  可翻出硅胶软胆（配件）','按压翻出、药落手心 ｜ 重度关节炎友好',GREY)
    s.rrect(cx,cy,110,15,2.2,fill=(240,236,232,255),outline='#B79E8C',width=0.5)
    s.rrect(cx+4,cy+2,102,11,1.2,fill=(226,214,204,255),outline='#A98C78',width=0.3)
    s.arrow(cx+55,cy, cx+55,cy-8,fill='#A98C78',width=0.7,head=2.4)
    s.text(cx+55,cy-11,'翻出',size=1.8,fill='#8B6F5E',anchor='ma')
    s.text(cx+2,cy+31,'2 步 ｜ 2–4 s ｜ 需测吸味/清洁',size=1.9,fill=GREY)

    # recommendation
    s.rrect(0,124,280,58,3,fill='#F2F7F6',outline='#B9D4CE',width=0.55)
    s.text(5,131,'推荐：B + C 组合（同一只杯，两种取法）',size=3.1,fill=ACC,bold=True)
    s.text(5,137.5,'每格一只可取出药杯：内深 10–11 mm、微斜底 + 前槽、前唇 5 mm、24 mm 倒药口，指腹落点距唇口 5 mm。',size=2.05,fill=INK)
    s.text(5,142.6,'日常“开盖 → 斜插指取 → 合盖”3 步；手抖/关节炎时“提杯 → 倾倒”2 步，不必把手指伸进格底。',size=2.05,fill=INK)
    s.text(5,148.4,'模具：杯体 PP 注塑（7 腔一模）+ 托盘 PP + 日盖 PC 烟灰；杯底 10×24 透光窗与底座 LED / 红外对位。',size=2.0,fill=GREY)
    s.text(5,153.6,'待验证：5 mm 唇口“静置不漏 / 倾倒不洒”；透光窗 ≥70 % @850 nm；杯口与托盘 0.4 mm 间隙不夹手。',size=2.0,fill=GREY)
    s.text(5,160.0,'对 21 格方案同样适用：杯体缩小到 41.9 × 16.8 × 15，前唇与倒药口做法不变。',size=2.0,fill=GREY)
    s.save('design/06_retrieval_options.png',out_w=s.W//2)

if __name__=='__main__':
    sheet_section(); sheet_options(); print('ok')
