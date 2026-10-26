# -*- coding: utf-8 -*-
"""IDEA-05B v3 · 静态介绍页：01 想法与设计 / 02 结构与功能 / 03 成本（5 分钟内讲完的密度）
单文件，图片全部内嵌，双击离线可看；不含动画 / 3D（之后另接）。讲稿见 design/33_讲解稿_双人5分钟.md。
    python3 tools/v3/make_intro.py [输出路径] [3D 页链接]
"""
import os, sys, io, base64, html
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import qa, wc, v3, off3

ROOT = os.path.dirname(os.path.dirname(HERE))
R3 = os.path.join(ROOT, 'renders', 'v3')
FULL = os.path.join(R3, 'full')
DES = os.path.join(ROOT, 'design')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DES, 'IDEA-05B_v3_介绍.html')
LINK3D = sys.argv[2] if len(sys.argv) > 2 else 'web_v3/3d.html'
REPO = 'https://github.com/anweat/idea-05b-smart-medicine-box'
E = html.escape


def autocrop(im, pad=40, tol=18):
    """按左上角背景色裁掉四周空白（正交视图背景大、产品占比小）。"""
    bg = Image.new('RGB', im.size, im.getpixel((2, 2)))
    box = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > tol else 0).getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def img(path, w=1600, q=84, crop=None):
    im = Image.open(path).convert('RGB')
    if crop == 'auto':
        im = autocrop(im)
    elif crop:
        im = im.crop(crop)
    im.thumbnail((w, w))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


I = {k: img(os.path.join(FULL, k + '_v3.png')) for k in ('hero', 'exploded', 'weigh', 'cup', 'allopen', 'loading')}
I['cell'] = img(os.path.join(R3, 'v3_cell_iso.png'))
I['pour'] = img(os.path.join(R3, 'v3_pour45.png'), w=1200)
I['section'] = img(os.path.join(DES, '32_整机v3_剖面A-A.png'), w=2000)
I['hinge'] = img(os.path.join(DES, '32_整机v3_剖面A-A.png'), w=1400, crop=(1300, 180, 2380, 820))   # 剖面里铰链脊一角：霍尔 / 磁铁 / 干燥片

# ---------------------------------------------------------------- 01 想法与设计
STATS = [('31.8–48.8%', '社区老人多重用药不按时吃'), ('6 种', '平均每人同时在吃的药'),
         ('46.8%', '不上网的人里 60 岁以上占比'), ('3–5 kg', '老人指尖捏力，关节炎再降三到四成')]
GOALS = [('取药', '取药不用捏'), ('装药', '装药一次装完'), ('记录', '吃没吃自动知道'), ('保存', '药放着不受潮')]
REFS = [('量杯', '后勾前嘴'), ('药房数药盘', '收拢倒嘴'), ('硬币杯', '圆弧杯底'), ('SIM 卡', '切角防呆'),
        ('棘轮拨爪', '联动全开'), ('烤盘耳', '整盘提出'), ('厨房秤', '只称药'), ('精密仪器', '三点定位'),
        ('笔记本电脑', '开盖检测')]

# ---------------------------------------------------------------- 02 结构与功能（每条一句话）
GROUPS = [
    ('取药', '手指不用捏', 'cell', [
        ('后勾前嘴', '勾起杯子就能倒，手在药的反方向'),
        ('收拢倒嘴', '药从 24 mm 倒嘴中间排队出来'),
        ('R12 圆弧杯底', '指腹一抹，药停在杯口边'),
        ('切角防呆', '杯子放反放不进')],
     '%.0f° 开始出药 · %.0f° 倒空' % (v3['first_exit_deg'], v3['last_exit_deg'])),
    ('装药', '一周一次装完', 'loading', [
        ('联动全开', '拨一下拨片，7 个盖一起开；单开一格互不影响'),
        ('提耳 + 漏斗板', '整盘端到桌上装，药撒进哪格就进哪格')],
     '联动 0–100° 全程无干涉'),
    ('称重', '只称药，放回自动归零', 'weigh', [
        ('浮动架 + 单点称重', '托盘只压在秤上，电池、外壳都不进称重'),
        ('三点定位', '锥窝 / V 槽 / 平面，每次放回同一位置')],
     '托盘离壳 %.1f mm，与分模线重合' % wc['tray_to_base_gap']),
    ('感知与保存', '药芯不带一根线', 'hinge', [
        ('通光孔 + 隔光墙', '7 组红外互不串光，今日格杯底亮灯'),
        ('霍尔在铰链脊', '开盖检测在底座里，药芯可整盘水洗'),
        ('干燥片进日盖', '每格一片，干燥剂在密封腔里')],
     '全机 %d 对零件零干涉' % qa['pairwise_checked']),
]
CHECKS = [('%d 对' % qa['pairwise_checked'], '零件两两零干涉'), ('0–100°', '联动全开无干涉'),
          ('%.0f°–%.0f°' % (v3['first_exit_deg'], v3['last_exit_deg']), '倒药仿真出药 → 倒空'),
          ('≤ %.1f mm' % off3, '药片出口偏离倒嘴中线')]

# ---------------------------------------------------------------- 03 成本（与 design/34_成本估算_v3.md 一致）
COST = [('电子料', 152.0), ('结构件', 38.0), ('组装测试', 12.0), ('包装', 6.0), ('装药板', 1.5)]
COST_TOTAL = sum(v for _, v in COST)


def bars():
    mx = max(v for _, v in COST)
    return ''.join(f'''<div class="bar" title="{E(n)}：¥{v:g}（{v / COST_TOTAL * 100:.0f}%）"><span class="bl">{E(n)}</span>
<span class="bt"><i style="width:{v / mx * 100:.1f}%"></i></span><span class="bv">¥{v:g}<em>{v / COST_TOTAL * 100:.0f}%</em></span></div>'''
                   for n, v in COST)


def group(name, sub, pic, items, key):
    li = ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in items)
    fit = ' fit' if pic == 'hinge' else ''
    return f'''<article class="grp"><div class="gimg{fit}"><img src="{I[pic]}" alt="{E(name)}"></div>
<div class="gbody"><h4>{E(name)}<small>{E(sub)}</small></h4><ul>{li}</ul><p class="key">{E(key)}</p></div></article>'''


CSS = '''
:root{--bg:#F3F5F8;--panel:#FFFFFF;--ink:#1F2A37;--ink2:#4A5868;--mute:#7A8899;--line:#DFE6EE;--accent:#1D6FD6;--accent2:#E8F1FC;--good:#0F7A62;--bar:#1D6FD6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#6AA8F5;--accent2:#1C2B3D;--good:#4CC3A2;--bar:#5B9BEA}}
:root[data-theme="dark"]{--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#6AA8F5;--accent2:#1C2B3D;--good:#4CC3A2;--bar:#5B9BEA}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;line-height:1.6}
img{max-width:100%;display:block}
.top{position:sticky;top:0;z-index:9;display:flex;gap:16px;align-items:center;padding:10px 20px;background:color-mix(in srgb,var(--panel) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top b{font-size:15px;white-space:nowrap} .top nav{display:flex;gap:16px;font-size:13px} .top nav a{color:var(--ink2);text-decoration:none;white-space:nowrap} .top nav a:hover{color:var(--accent)}
.top .sp{flex:1} .btn{white-space:nowrap;font-size:12px;padding:6px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;text-decoration:none} .btn.pri{background:var(--accent);border-color:var(--accent);color:#fff} button{white-space:nowrap;font:inherit;font-size:12px;padding:6px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;cursor:pointer}
main{max-width:1160px;margin:0 auto;padding:0 20px 60px}
.cover{display:grid;grid-template-columns:1.45fr 1fr;gap:32px;align-items:center;margin-top:28px}
.cover img{border-radius:16px;box-shadow:0 18px 50px rgba(25,45,70,.14)}
.k{color:var(--accent);font-size:13px;letter-spacing:2px;font-weight:600}
.cover h1{font-size:40px;line-height:1.25;margin:8px 0 12px} .lead{color:var(--ink2);margin:0 0 16px}
.cta{margin:0 0 14px} .cta .btn{font-size:14px;padding:8px 16px;display:inline-block}
.specs{display:flex;flex-wrap:wrap;gap:8px} .specs span{font-size:13px;color:var(--ink2);background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:3px 12px}
.part{margin-top:64px;display:flex;gap:14px;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:10px}
.part i{font-style:normal;color:var(--accent);font-weight:700;font-size:20px;font-variant-numeric:tabular-nums} .part h2{margin:0;font-size:26px}
section{margin-top:28px} h3{font-size:18px;margin:0 0 12px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.stat b{display:block;font-size:28px;font-variant-numeric:tabular-nums;line-height:1.2} .stat span{display:block;color:var(--ink2);font-size:14px;margin-top:4px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.goals{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.goal{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px} .goal i{font-style:normal;font-size:12px;color:var(--mute)} .goal b{display:block;font-size:17px;color:var(--accent)}
.refs{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.ref{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:14px;display:flex;gap:6px;flex-wrap:wrap} .ref b{font-weight:600} .ref span{color:var(--ink2)} .ref span::before{content:"→ ";color:var(--accent)}
.flows{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.flow{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}
.flow h4{margin:0 0 8px;font-size:16px} .flow ol{margin:0 0 12px;padding-left:20px;font-size:14px;color:var(--ink2)} .flow ol li{margin:3px 0}
.flow .imgs{display:grid;grid-template-columns:1fr 1fr;gap:8px} .flow .imgs img{border-radius:8px;aspect-ratio:4/3;object-fit:cover;width:100%}
.ov{display:grid;grid-template-columns:1fr 1.4fr;gap:16px}
figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden} figure img{width:100%;height:100%;object-fit:contain} .ov figure:first-child img{object-fit:cover}
.grps{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grp{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}
.gimg{background:#E6E9EE;aspect-ratio:16/8;overflow:hidden} .gimg img{width:100%;height:100%;object-fit:cover} .gimg.fit{background:#F7F8FA} .gimg.fit img{object-fit:contain}
.gbody{padding:14px 18px 16px;display:flex;flex-direction:column;flex:1}
.grp h4{margin:0 0 8px;font-size:19px;display:flex;gap:10px;align-items:baseline} .grp h4 small{font-size:14px;color:var(--accent);font-weight:500}
.grp ul{list-style:none;margin:0;padding:0;display:grid;gap:6px;font-size:14px} .grp li{display:flex;gap:10px} .grp li b{flex:none;width:118px;font-weight:600} .grp li span{color:var(--ink2)}
.key{margin:12px 0 0;padding-top:10px;border-top:1px solid var(--line);font-size:14px;color:var(--good);font-weight:600;margin-top:auto}
.checks{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.check{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px} .check b{display:block;font-size:20px;font-variant-numeric:tabular-nums} .check span{font-size:13px;color:var(--ink2)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}
.bars{display:grid;gap:12px} .bar{display:grid;grid-template-columns:72px 1fr 100px;gap:12px;align-items:center;font-size:14px}
.bl{color:var(--ink2)} .bt{height:14px;position:relative} .bt i{display:block;height:100%;background:var(--bar);border-radius:0 4px 4px 0}
.bv{font-variant-numeric:tabular-nums;text-align:right} .bv em{font-style:normal;color:var(--mute);margin-left:8px;font-size:12px}
table{border-collapse:collapse;width:100%;font-size:14px} td{padding:10px 4px;border-bottom:1px solid var(--line)} tr:last-child td{border:0} td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.note{color:var(--mute);font-size:12px;margin:12px 0 0}
footer{margin-top:48px;color:var(--mute);font-size:12px;text-align:center}
@media (max-width:900px){.cover,.row2,.flows,.ov,.grps{grid-template-columns:1fr} .stats,.checks{grid-template-columns:1fr 1fr} .top nav{display:none} .cover h1{font-size:30px}}
@media (max-width:520px){main{padding:0 16px 40px} .top{padding:8px 12px;gap:8px} .top b{font-size:13px} .top button{display:none} .refs{grid-template-columns:1fr 1fr} .stat b{font-size:22px} .grp li{flex-direction:column;gap:0} .grp li b{width:auto} .bar{grid-template-columns:60px 1fr 84px;gap:8px;font-size:13px}}
@media print{.top{display:none} body{background:#fff} .part{break-before:page}}
'''

stats = ''.join(f'<div class="stat"><b>{E(v)}</b><span>{E(t)}</span></div>' for v, t in STATS)
goals = ''.join(f'<div class="goal"><i>{E(a)}</i><b>{E(b)}</b></div>' for a, b in GOALS)
refs = ''.join(f'<div class="ref"><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in REFS)
groups = ''.join(group(*g) for g in GROUPS)
checks = ''.join(f'<div class="check"><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in CHECKS)

page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDEA-05B 智能药盒</title><style>{CSS}</style></head><body>
<div class="top"><b>IDEA-05B 智能药盒</b>
<nav><a href="#p1">01 想法与设计</a><a href="#p2">02 结构与功能</a><a href="#p3">03 成本</a></nav>
<div class="sp"></div><a class="btn pri" href="{LINK3D}">3D 模型</a><a class="btn" href="{REPO}" target="_blank" rel="noopener">GitHub</a>
<button onclick="tg()">深色 / 浅色</button></div>
<main>

<div class="cover">
  <img src="{I['hero']}" alt="IDEA-05B 智能药盒整机">
  <div><div class="k">SMART MEDICINE BOX</div>
  <h1>一勾、一倒，<br>药就到手心。</h1>
  <p class="lead">给每天吃好几种药的老人：取药不用捏，装药一次装完，吃没吃自动知道，药放着不受潮。</p>
  <p class="cta"><a class="btn pri" href="{LINK3D}">打开 3D 模型 →</a></p>
  <div class="specs"><span>320 × 70 × 52 mm</span><span>7 天 7 格</span><span>段码屏 + 3 键</span><span>称重 · 红外 · 开盖检测</span><span>离线语音</span></div></div>
</div>

<div class="part" id="p1"><i>01</i><h2>想法与设计</h2></div>
<section id="s11"><h3>1.1 用户与痛点</h3><div class="stats">{stats}</div></section>
<section id="s12"><div class="row2">
<div><h3>1.2 设计目标</h3><div class="goals">{goals}</div></div>
<div><h3>1.3 设计方法：借成熟结构</h3><div class="refs">{refs}</div></div></div></section>
<section id="s14"><h3>1.4 怎么用</h3><div class="flows">
<div class="flow"><h4>每天取药</h4><ol><li>开当天的盖</li><li>勾住杯后的小勾提起，一倾就倒出</li><li>不提杯也行：指腹一抹，药停在杯口边</li></ol>
<div class="imgs"><img src="{I['cup']}" alt="开盖"><img src="{I['pour']}" alt="提杯倾倒"></div></div>
<div class="flow"><h4>每周装药</h4><ol><li>拨一下拨片，7 个盖一起开</li><li>捏两端提耳，整盘端到桌上，盖上漏斗板装药</li><li>放回去，自动对正、自动归零</li></ol>
<div class="imgs"><img src="{I['allopen']}" alt="联动全开"><img src="{I['loading']}" alt="批量装药"></div></div>
</div></section>

<div class="part" id="p2"><i>02</i><h2>结构与功能</h2></div>
<section id="s21"><h3>2.1 结构总览</h3><div class="ov">
<figure><img src="{I['exploded']}" alt="爆炸图"></figure><figure><img src="{I['section']}" alt="整机剖面"></figure></div></section>
<section id="s22"><h3>2.2 – 2.5 取药 · 装药 · 称重 · 感知与保存</h3><div class="grps">{groups}</div></section>
<section id="s26"><h3>2.6 验证</h3><div class="checks">{checks}</div></section>

<div class="part" id="p3"><i>03</i><h2>成本</h2></div>
<section id="s31"><div class="stats">
<div class="stat"><b>≈ ¥{COST_TOTAL:.0f}</b><span>出厂成本 / 台（1 千台批量）</span></div>
<div class="stat"><b>+¥17</b><span>全部结构创新合计，约 8%</span></div>
<div class="stat"><b>¥11–18 万</b><span>一次性模具</span></div>
<div class="stat"><b>¥399</b><span>建议零售，买断</span></div></div></section>
<section id="s32"><div class="row2">
<div class="panel"><h3>成本构成（¥ / 台）</h3><div class="bars">{bars()}</div>
<p class="note">取药结构、提耳、隔光墙都是模具里的形状，不增加零件。电子料按华秋 / 立创报价，结构件按 3D 模型体积算重量，均为估算。</p></div>
<div class="panel"><h3>价格带</h3><table>
<tr><td>白牌 7 格药盒（只分格 + 闹铃）</td><td class="n">¥23–45</td></tr>
<tr><td>进口自动分药机（按月收费）</td><td class="n">¥213–888 / 月</td></tr>
<tr><td><b>IDEA-05B（买断）</b></td><td class="n"><b>¥399</b></td></tr>
<tr><td>用户持续花费（干燥片）</td><td class="n">≈ ¥2 / 月</td></tr></table></div></div></section>

<footer>仿真为刚体近似，称重精度与手感待手板实测；称重只证明药离开药盒，不证明服下，不是医疗器械。<br>IDEA-05B 智能药盒 · 2026-10 · <a href="{REPO}" target="_blank" rel="noopener" style="color:inherit">github.com/anweat/idea-05b-smart-medicine-box</a></footer>
</main>
<script>
function tg(){{const r=document.documentElement;const d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark';try{{localStorage.setItem('t',r.dataset.theme)}}catch(e){{}}}}
try{{const t=localStorage.getItem('t');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}
</script></body></html>'''

open(OUT, 'w', encoding='utf-8').write(page)
print('INTRO', OUT, round(os.path.getsize(OUT) / 1e6, 2), 'MB')
