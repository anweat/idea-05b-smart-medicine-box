import base64, io, os
from PIL import Image

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1600,1060
BG='#F5F8FC'; CARD='#FFFFFF'; LINE='#DFE9F4'; BLUE='#1D6FD6'; DARK='#22303F'
GREY='#6C7C8E'; TEAL='#0F7B6C'; HOT='#DF7A32'; SOFT='#EEF5FC'
FONT='Hiragino Sans GB, PingFang SC, Microsoft YaHei, Noto Sans SC, sans-serif'

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def rect(x,y,w,h,r=14,fill=CARD,stroke=LINE,sw=1,op=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'

def txt(x,y,s,size=13,fill=DARK,weight=400,anchor='start',ls=0,op=1):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}">{esc(s)}</text>'

def en(x,y,s,size=10,fill=BLUE,weight=600,anchor='start',ls=0.8):
    return f'<text x="{x}" y="{y}" font-family="Helvetica Neue, Arial, sans-serif" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}">{esc(s)}</text>'

def line(x1,y1,x2,y2,stroke=GREY,width=1,dash=None,op=1):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" opacity="{op}"{d}/>'

def circle(cx,cy,r,fill,stroke='none',sw=1,op=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'

def data_uri(path,crop=None,trim=True,maxw=None):
    im=Image.open(path).convert('RGBA')
    if crop: im=im.crop(crop)
    if trim:
        bb=im.getbbox(); im=im.crop(bb)
    if maxw and im.width>maxw:
        im=im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS)
    buf=io.BytesIO(); im.save(buf,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode(), im.size

def image(uri,x,y,w,h):
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="{uri}" xlink:href="{uri}"/>'

def fit_place(iw,ih,x,y,w,h,align='center'):
    sc=min(w/iw,h/ih); nw,nh=iw*sc,ih*sc
    ox=x+(w-nw)/2; oy=y+(h-nh)/2
    if align=='left': ox=x
    if align=='top': oy=y
    return ox,oy,nw,nh

def callout(fx,fy,nx,ny,n,label,tx,ty,anchor='start',lx=None,ly=None):
    # leader from feature to number, then text next to number
    pts=f'{fx},{fy} {lx if lx is not None else nx},{ly if ly is not None else ny} {nx},{ny}'
    out=f'<polyline points="{pts}" fill="none" stroke="#8FA3B8" stroke-width="0.9"/>'
    out+=circle(fx,fy,2.1,BLUE)
    out+=circle(nx,ny,9.5,BLUE)
    out+=txt(nx,ny+3.8,str(n),9.5,'#FFFFFF',600,'middle')
    out+=txt(tx,ty,label,10.5,DARK,400,anchor)
    return out

S=[]
S.append(f'<svg id="board" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
S.append('<title>IDEA-05B 智能药盒 · 7 格取药升级 · 概念图板</title><desc>整体效果、三视图、爆炸图、取药几何、细节、参数与功能说明</desc>')
S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
# soft top gradient
S.append('<defs><linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F5F8FC"/></linearGradient>'
         '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#1B2B40" flood-opacity="0.07"/></filter></defs>')
S.append(f'<rect x="0" y="0" width="{W}" height="84" fill="url(#top)"/>')

# ---------------- header
S.append(txt(28,48,'智能药盒',34,DARK,700))
S.append(txt(206,46,'IDEA-05B',26,BLUE,600,ls=1))
S.append(txt(28,72,'SMART MEDICINE BOX  ·  7 格取药升级  ·  可取出药杯  ·  集成称重 / 环境感应 / 离线语音',11.5,GREY,ls=0.4))
S.append(txt(800,42,'为长辈而设计  ·  更好取药  ·  更懂保存  ·  双端可管',15,DARK,400,'middle'))
S.append(txt(800,64,'SMART LIFE  ·  BETTER HEALTH',10,GREY,400,'middle',2.2))
S.append(txt(1576,34,'2026.10  ·  设计定稿  ·  7 格演进版',10.5,GREY,400,'end'))
S.append(txt(1576,54,'320 × 70 × 52 mm  ·  BOM ≈ ¥160–180',10.5,GREY,400,'end'))
S.append(line(24,84,1576,84,'#D8E4F2',1.2))

# ---------------- row1 hero
S.append(rect(24,96,986,374,16,CARD,LINE,1))
S.append(txt(44,124,'整体效果图',17,DARK,600))
S.append(en(150,124,'OVERALL VIEW'))
S.append(txt(990,124,'按压弹开 · 格内导光 · 可取出药杯',10,GREY,400,'end'))
hero_uri,(hw,hh)=data_uri(f'{ROOT}/renders/trans/hero.png',trim=True,maxw=1100)
hx,hy,hwid,hhei=fit_place(hw,hh,40,132,954,320)
S.append(image(hero_uri,hx,hy,hwid,hhei))
# callouts on hero
# feature fractions
Fx=lambda fx,fy: (hx+fx*hwid, hy+fy*hhei)
f_cup=Fx(0.43,0.40); f_lid=Fx(0.67,0.34); f_disp=Fx(0.115,0.71); f_btn=Fx(0.215,0.80); f_led=Fx(0.305,0.835); f_spk=Fx(0.795,0.745)
S.append(callout(*f_cup, 470,170,1,'可取出药杯：浅口 15 mm / 前唇 5 mm / 24 mm 倒药口',486,174,'start',470,196))
S.append(callout(*f_lid, 860,170,2,'独立日盖：按压弹开、阻尼下放',876,174,'start',860,196))
S.append(callout(*f_disp, 120,420,3,'段码屏：时间 / 下一剂 / 温湿度',136,424,'start',120,440))
S.append(callout(*f_btn, 330,430,4,'⌀22 主键 + 2 副键',346,434,'start',330,450))
S.append(callout(*f_led, 560,430,5,'7 天进度 + 7 格导光',576,434,'start',560,450))
S.append(callout(*f_spk, 860,420,6,'语音播报 / 拾音',876,424,'start',860,440))

# ---------------- row1 right: spec
S.append(rect(1026,96,550,206,16,CARD,LINE,1))
S.append(txt(1046,124,'产品参数',17,DARK,600))
S.append(en(1556,124,'PRODUCT SPEC',anchor='end'))
rows=[('外形','320 × 70 × 52 mm'),('格数','7 格 · 周一–周日'),('药杯','41.9 × 54 × 15 mm · PP'),
      ('取药','浅口 15 · 前唇 5 · 口 24 mm'),('称重','500 g + 7 红外 + 7 霍尔'),('环境','SHT40 + 光照 + IP54'),
      ('交互','段码屏 + 3 键 + 7 灯'),('语音','SU-03T + 2 W · 亲情语音'),('电源','3000 mAh · Type-C + pogo')]
ty=146
for i,(k,v) in enumerate(rows):
    if i%2==0: S.append(rect(1040,ty-12,522,19,5,'#F4F8FD','none',0))
    S.append(txt(1048,ty,k,10.5,GREY))
    S.append(txt(1136,ty,v,10.5,DARK,500))
    ty+=18.2

# ---------------- row1 right: features
S.append(rect(1026,314,550,156,16,CARD,LINE,1))
S.append(txt(1046,342,'核心能力',17,DARK,600))
S.append(en(1556,342,'KEY FEATURES',anchor='end'))
feats=[('称重三态','已确认 / 已取出未确认 / 未动'),('环境动作','超温/超湿 → 具体建议'),('离线优先','断网可提醒、可记录'),('双端 App','长者零账号 / 家属管理')]
for i,(t,d) in enumerate(feats):
    cx=1046+(i%2)*258; cy=358+(i//2)*54
    S.append(rect(cx,cy,244,46,10,'#F6FAFF','#E6EFF8',0.8))
    S.append(circle(cx+22,cy+23,12,SOFT))
    S.append(txt(cx+22,cy+27,'●',11,BLUE,600,'middle'))
    S.append(txt(cx+40,cy+19,t,11.5,DARK,600))
    S.append(txt(cx+40,cy+35,d,9.5,GREY))

# ---------------- row2 front
S.append(rect(24,486,576,274,16,CARD,LINE,1))
S.append(txt(44,514,'正视图',17,DARK,600))
S.append(en(120,514,'FRONT VIEW'))
S.append(txt(580,514,'1:2',9.5,GREY,400,'end'))
f_uri,(fw,fh)=data_uri(f'{ROOT}/renders/trans/front.png',trim=True,maxw=1200)
fx,fy,fwid,fhei=fit_place(fw,fh,44,540,536,110)
S.append(image(f_uri,fx,fy,fwid,fhei))
# dim 320
S.append(line(fx,fy+fhei+30,fx+fwid,fy+fhei+30,BLUE,1))
S.append(line(fx,fy+fhei+25,fx,fy+fhei+35,BLUE,1)); S.append(line(fx+fwid,fy+fhei+25,fx+fwid,fy+fhei+35,BLUE,1))
S.append(txt(fx+fwid/2,fy+fhei+23,'320 mm',9.5,BLUE,500,'middle'))
# vertical 52 approximate
S.append(line(fx-14,fy+fhei*0.10,fx-14,fy+fhei*0.88,BLUE,1))
S.append(line(fx-19,fy+fhei*0.10,fx-9,fy+fhei*0.10,BLUE,1)); S.append(line(fx-19,fy+fhei*0.88,fx-9,fy+fhei*0.88,BLUE,1))
S.append(txt(fx-18,fy+fhei*0.50,'52',9,BLUE,500,'end'))
S.append(txt(44,700,'段码屏 08:30 · 已服药主键 · 状态灯 · 语音播报 / 拾音',10.5,DARK,500))
S.append(txt(44,722,'周一–周日标签 · 7 个独立烟灰日盖 · 日盖可整排取下',10,GREY))
S.append(rect(44,736,120,22,11,SOFT,'none',0)); S.append(txt(104,751,'按压弹开 <3 N',9,BLUE,500,'middle'))
S.append(rect(172,736,120,22,11,SOFT,'none',0)); S.append(txt(232,751,'格内导光 / 7 天进度',9,BLUE,500,'middle'))

# ---------------- row2 top
S.append(rect(612,486,288,274,16,CARD,LINE,1))
S.append(txt(632,514,'俯视图',17,DARK,600))
S.append(en(702,514,'TOP VIEW'))
t_uri,(tw,th)=data_uri(f'{ROOT}/renders/trans/top.png',trim=True,maxw=900)
tx,ty,twid,thei=fit_place(tw,th,620,548,230,100)
S.append(image(t_uri,tx,ty,twid,thei))
S.append(line(tx,ty+thei+26,tx+twid,ty+thei+26,BLUE,1))
S.append(line(tx,ty+thei+21,tx,ty+thei+31,BLUE,1)); S.append(line(tx+twid,ty+thei+21,tx+twid,ty+thei+31,BLUE,1))
S.append(txt(tx+twid/2,ty+thei+19,'320 mm',9,BLUE,500,'middle'))
S.append(line(tx+twid+14,ty,tx+twid+14,ty+thei,BLUE,1))
S.append(line(tx+twid+9,ty,tx+twid+19,ty,BLUE,1)); S.append(line(tx+twid+9,ty+thei,tx+twid+19,ty+thei,BLUE,1))
S.append(txt(tx+twid+18,ty+thei/2,'70',9,BLUE,500,'start'))
S.append(txt(632,690,'7 个独立烟灰日盖',10.5,DARK,500))
S.append(txt(632,710,'周一–周日 · 按压弹开',10,GREY))
S.append(txt(632,732,'日盖可整排取下清洗',10,GREY))

# ---------------- row2 exploded
S.append(rect(912,486,664,274,16,CARD,LINE,1))
S.append(txt(932,514,'爆炸图',17,DARK,600))
S.append(en(1556,514,'EXPLODED VIEW',anchor='end'))
e_uri,(ew,eh)=data_uri(f'{ROOT}/renders/trans/exploded.png',trim=True,maxw=900)
ex,ey,ewid,ehei=fit_place(ew,eh,928,530,300,220,align='left')
S.append(image(e_uri,ex,ey,ewid,ehei))
layers=[(0.55,0.10,'①','烟灰 PC 日盖：按压弹开 + 阻尼'),(0.50,0.28,'②','可取出药杯：PP · 可水洗'),
        (0.50,0.44,'③','药芯托盘：7 腔 · 密封口'),(0.50,0.60,'④','称重 / 传感板：红外 + 霍尔 + SHT40'),
        (0.56,0.84,'⑤','主板 / 电池：ESP32-C3 + 3000 mAh'),(0.80,0.93,'⑥','底壳 + pogo + 防滑脚')]
for fx0,fy0,n,label in layers:
    px=ex+fx0*ewid; py=ey+fy0*ehei
    nx=1250; ny=py
    S.append(f'<polyline points="{px},{py} {nx-10},{ny} {nx},{ny}" fill="none" stroke="#8FA3B8" stroke-width="0.9"/>')
    S.append(circle(px,py,2.0,BLUE)); S.append(circle(nx,ny,9,BLUE))
    S.append(txt(nx,ny+3.4,n,8.8,'#FFFFFF',600,'middle'))
    S.append(txt(nx+16,ny+3.5,label,10,DARK,400,'start'))

# ---------------- row3 geometry
S.append(rect(24,776,496,204,16,CARD,LINE,1))
S.append(txt(44,804,'取药几何',17,DARK,600))
S.append(en(124,804,'RETRIEVAL GEOMETRY',size=9.5))
S.append(txt(500,804,'前唇 5 mm · 倒药口 24 mm',9.5,GREY,400,'end'))
g_uri,(gw,gh)=data_uri(f'{ROOT}/design/05_retrieval_geometry.png',crop=(540,330,1450,810),trim=False,maxw=900)
gx,gy,gwid,ghei=fit_place(gw,gh,44,812,456,145)
S.append(image(g_uri,gx,gy,gwid,ghei))
S.append(txt(44,974,'浅口 15 · 前唇 5 · 倒药口 24 mm；指取 3 步 / 提杯倾倒 2 步',9.6,DARK,500))

# ---------------- row3 details
S.append(rect(532,776,468,204,16,CARD,LINE,1))
S.append(txt(552,804,'细节展示',17,DARK,600))
S.append(en(980,804,'DETAILS',anchor='end'))
ui_uri,(uw,uh)=data_uri(f'{ROOT}/renders/trans/ui.png',trim=True,maxw=800)
ux,uy,uwid,uhei=fit_place(uw,uh,544,814,210,100)
S.append(image(ui_uri,ux,uy,uwid,uhei))
S.append(txt(544,930,'段码屏 + 3 键 + 状态灯',10,DARK,500))
cup_uri,(cw,ch)=data_uri(f'{ROOT}/renders/trans/hero.png',crop=(450,450,940,750),trim=True,maxw=700)
cx2,cy2,cwid,chei=fit_place(cw,ch,770,818,210,96)
S.append(rect(766,812,218,104,10,'#E8EFF6','#D3E0EC',0.8))
S.append(image(cup_uri,cx2,cy2,cwid,chei))
S.append(txt(770,930,'周三药杯：开盖 + 药片导光',10,DARK,500))
S.append(txt(544,950,'屏幕强光可读 · 按键 0.8–2 N · 杯内 LED 导光',9.6,GREY))

# ---------------- row3 flow
S.append(rect(1012,776,564,204,16,CARD,LINE,1))
S.append(txt(1032,804,'使用流程 / 双端',17,DARK,600))
S.append(en(1556,804,'FLOW & APP',anchor='end'))
steps=[('1','开盖'),('2','取药'),('3','合盖'),('4','确认同步')]
for i,(n,t) in enumerate(steps):
    cx=1060+i*128; cy=838
    S.append(circle(cx,cy,15,BLUE)); S.append(txt(cx,cy+4.5,n,11.5,'#FFFFFF',600,'middle'))
    S.append(txt(cx,cy+30,t,9.8,DARK,500,'middle'))
    if i<3: S.append(f'<line x1="{cx+17}" y1="{cy}" x2="{cx+111}" y2="{cy}" stroke="#C9D9EA" stroke-width="1" stroke-dasharray="4 3"/>')
S.append(rect(1032,884,526,36,9,'#F2F8F6','#D7EAE4',0.8))
S.append(txt(1044,906,'长者端：零账号 · 3 键 + 语音 · 断网可用',10.2,TEAL,500))
S.append(rect(1032,928,526,36,9,'#F4F8FD','#DFE9F4',0.8))
S.append(txt(1044,950,'家属端：排药 / 依从性 / 环境 / 库存 / 远程提醒',10.2,DARK,500))

# ---------------- footer
S.append(rect(24,996,1552,52,12,'#1D6FD6','none',0))
S.append(txt(44,1028,'IDEA-05B  ·  7 格  ·  320 × 70 × 52 mm  ·  可取出药杯  ·  集成称重  ·  环境感应  ·  离线语音  ·  双端 App',11.5,'#FFFFFF',500))
S.append(txt(1556,1028,'以人为本  ·  安全可靠  ·  智能科技  ·  守护健康',9.5,'#DCEBFF',400,'end'))
S.append('</svg>')
svg='\n'.join(S)

os.makedirs(f'{ROOT}/design',exist_ok=True)
open(f'{ROOT}/design/10_IDEA-05B_concept_board.svg','w').write('<?xml version="1.0" encoding="UTF-8"?>\n'+svg)
print('svg bytes', len(svg))

# standalone html
html=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDEA-05B 智能药盒 · 概念图板</title>
<style>
:root{{--bg:#E9EFF6;--bar:#FFFFFF;--ink:#22303F;--blue:#1D6FD6;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);font-family:"Hiragino Sans GB","PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink)}}
.bar{{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:14px;padding:10px 18px;background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-bottom:1px solid #DCE6F2}}
.bar h1{{font-size:15px;margin:0;font-weight:600;letter-spacing:.5px}}
.bar .sub{{font-size:11px;color:#6C7C8E}}
.bar .sp{{flex:1}}
button{{font:inherit;font-size:12px;padding:7px 12px;border:1px solid #CBDCEE;background:#fff;color:#22303F;border-radius:8px;cursor:pointer}}
button:hover{{border-color:var(--blue);color:var(--blue)}}
#stage{{max-width:1600px;margin:16px auto 40px;padding:0 16px}}
#board{{width:100%;height:auto;display:block;border-radius:14px;box-shadow:0 18px 50px rgba(25,45,70,.14);background:#F5F8FC}}
.zoomed #board{{width:1600px;max-width:none}}
.zoomed #stage{{overflow:auto;max-width:none}}
.hint{{text-align:center;color:#7D8DA0;font-size:11px;margin:0 0 12px}}
@media print{{.bar,.hint{{display:none}} body{{background:#fff}} #stage{{margin:0;padding:0}} #board{{box-shadow:none;border-radius:0}}}}
</style></head>
<body>
<div class="bar">
  <h1>IDEA-05B 智能药盒 · 概念图板</h1>
  <div class="sub">7 格取药升级 · 320 × 70 × 52 mm</div>
  <div class="sp"></div>
  <button onclick="document.body.classList.toggle('zoomed')">放大 / 适应</button>
  <button onclick="dl()">下载 SVG</button>
  <button onclick="window.print()">打印 / PDF</button>
</div>
<div id="stage">
  <p class="hint">单文件自包含：所有渲染图已内嵌，双击即可离线查看</p>
  {svg}
</div>
<script>
function dl(){{
  const s=document.getElementById('board');
  const xml=new XMLSerializer().serializeToString(s);
  const blob=new Blob(['<?xml version="1.0" encoding="UTF-8"?>\\n'+xml],{{type:'image/svg+xml;charset=utf-8'}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob); a.download='IDEA-05B_concept_board.svg'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),3000);
}}
</script>
</body></html>'''
open(f'{ROOT}/design/10_IDEA-05B_concept_board.html','w').write(html)
print('html bytes', len(html))
