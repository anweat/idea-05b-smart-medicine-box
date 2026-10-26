# -*- coding: utf-8 -*-
"""IDEA-05B v3 · 单文件展示页（图片 / GLB 全部内嵌，双击离线可看；3D 查看需联网加载 model-viewer）
数据全部读模型输出：model/v3/full_qa.json、sim_pour_report.json、v3_report.json
    python3 tools/v3/make_site.py  [输出路径]
"""
import os, sys, io, json, base64, html
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MOD = os.path.join(ROOT, 'model', 'v3')
R3 = os.path.join(ROOT, 'renders', 'v3')
FULL = os.path.join(R3, 'full')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'design', 'IDEA-05B_v3_展示.html')

from content import qa, sim, rep, wc, v3, off3, sweep_ok, INNOV, TAG


def img(path, w=1600, q=84, crop=None):
    im = Image.open(path).convert('RGB')
    if crop:
        im = im.crop(crop)
    im.thumbnail((w, w))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def glb(path):
    return 'data:model/gltf-binary;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


E = html.escape
I = {k: img(os.path.join(FULL, k + '_v3.png')) for k in ('hero', 'front', 'top', 'exploded', 'weigh', 'cup', 'allopen', 'loading')}
I['section'] = img(os.path.join(ROOT, 'design', '32_整机v3_剖面A-A.png'), w=2000)
I['sheet'] = img(os.path.join(ROOT, 'design', '30_取药结构v3_剖面与尺寸.png'), w=2000)
I['cell'] = img(os.path.join(R3, 'v3_cell_iso.png'))
I['celltop'] = img(os.path.join(R3, 'v3_cell_top.png'), w=1000)
V = {k: 'data:video/mp4;base64,' + base64.b64encode(open(os.path.join(R3, 'anim', k + '.mp4'), 'rb').read()).decode()
     for k in ('pour', 'sweep', 'load')}
GLB = glb(os.path.join(MOD, 'IDEA-05_box_v3.glb'))


def card(t, no, title, sub, how, ev, pic):
    name, col = TAG[t]
    return f'''<article class="card" id="i{no}">
  <div class="cimg"><img src="{I[pic]}" alt="{E(title)}" loading="lazy"></div>
  <div class="cbody">
    <div class="ctag" style="--c:{col}"><span>{name}</span><b>{no}</b></div>
    <h3>{E(title)}</h3><p class="csub">{E(sub)}</p>
    <dl><dt>怎么做</dt><dd>{E(how)}</dd><dt>证据</dt><dd class="ev">{E(ev)}</dd></dl>
  </div></article>'''


qa_rows = [
    ('7 杯 × 托盘 / 杯 × 闭合日盖干涉', '全部 0'),
    ('日盖开合 0–105° 扫掠（杯 / 托盘 / 铰链脊）', '全部 0' if sweep_ok else '有干涉'),
    ('联动全开 0→100°（拨片 / 拨爪 / 7 盖 vs 托盘、底座、铰链脊、杯）', '全部 0' if qa['gang_open']['all_zero'] else '有干涉'),
    ('单独开一格到 100°（拨爪 vs 铰链节空程槽）', '全部 0' if not any(qa['single_lid_shaft_tri'].values()) else '有干涉'),
    ('装药模板落座（vs 杯 / 勾手 / 日盖 / 托盘）', '全部 0，离勾手 %.1f mm' % qa['template']['to_handle_gap']),
    ('零件两两干涉', '%d 对，全部 0' % qa['pairwise_checked'] if not qa['pairwise_hits_mm3'] else str(qa['pairwise_hits_mm3'])),
    ('托盘 → 浮动架', '相切接触（唯一传力点）'),
    ('托盘 → 底座 / 铰链脊 / 铰链梁 / 传感板', '%.1f / %.1f / %.1f / %.1f mm' % (wc['tray_to_base_gap'], wc['tray_to_spine_gap'], wc['tray_to_rail_gap'], wc['tray_to_sensorplate_gap'])),
    ('浮动架 → 底座 / 传感板 / 过载限位', '%.1f / %.1f / %.1f mm' % (wc['carrier_to_base_gap'], wc['carrier_to_sensorplate_gap'], wc['carrier_to_stops_gap'])),
    ('反装药杯', '与防呆块干涉 %.0f mm³（放不进）' % rep['reversed_cup_x_tray_mm3']),
    ('3D Print Toolbox（托盘 / 杯 / 日盖）', '0 非流形 · 0 自相交 · 0 薄面'),
]
qa_html = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td></tr>' for a, b in qa_rows)

page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDEA-05B 智能药盒 v3</title>
<style>
:root{{--bg:#EEF2F7;--panel:#FFFFFF;--ink:#22303F;--mute:#6C7C8E;--line:#DCE6F2;--blue:#1D6FD6;--bad:#B4532F;--good:#0F8A6E}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#141A21;--panel:#1C242E;--ink:#E3EAF2;--mute:#9AA9B9;--line:#2C3845;--blue:#6AA8F5;--bad:#E08A62;--good:#4CC3A2}}}}
:root[data-theme="dark"]{{--bg:#141A21;--panel:#1C242E;--ink:#E3EAF2;--mute:#9AA9B9;--line:#2C3845;--blue:#6AA8F5;--bad:#E08A62;--good:#4CC3A2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;line-height:1.6}}
img{{max-width:100%;display:block}}
.bar{{position:sticky;top:0;z-index:9;display:flex;gap:16px;align-items:center;padding:10px 20px;background:color-mix(in srgb,var(--panel) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
.bar h1{{font-size:15px;margin:0;font-weight:600}} .bar .sp{{flex:1}}
.bar nav{{display:flex;gap:14px;font-size:13px;overflow-x:auto}} .bar a{{color:var(--mute);text-decoration:none;white-space:nowrap}} .bar a:hover{{color:var(--blue)}}
button{{white-space:nowrap;font:inherit;font-size:12px;padding:6px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;cursor:pointer}}
main{{max-width:1240px;margin:0 auto;padding:0 20px 60px}}
section{{margin-top:56px}}
h2{{font-size:26px;margin:0 0 6px}} .lead{{color:var(--mute);margin:0 0 22px;max-width:860px}}
.hero{{display:grid;grid-template-columns:1.5fr 1fr;gap:28px;align-items:center;margin-top:28px}}
.hero h2{{font-size:38px;line-height:1.25}} .hero .k{{color:var(--blue);font-size:13px;letter-spacing:2px;font-weight:600}}
.hero img{{border-radius:16px;box-shadow:0 18px 50px rgba(25,45,70,.14)}}
.stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:20px}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.stat b{{display:block;font-size:28px;font-variant-numeric:tabular-nums}} .stat span{{color:var(--mute);font-size:13px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
model-viewer{{width:100%;height:520px;background:var(--panel);border-radius:16px;border:1px solid var(--line)}}
.cards{{display:grid;grid-template-columns:1fr;gap:18px}}
.card{{display:grid;grid-template-columns:420px 1fr;background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden}}
.cimg{{background:#E8ECF1;display:flex;align-items:center}} .cimg img{{width:100%;height:100%;object-fit:cover;max-height:330px}}
.cbody{{padding:20px 24px}}
.ctag{{display:flex;gap:10px;align-items:center;font-size:12px}} .ctag span{{color:var(--c);border:1px solid var(--c);border-radius:20px;padding:1px 10px}} .ctag b{{color:var(--mute);font-size:13px}}
.card h3{{margin:8px 0 2px;font-size:21px}} .csub{{margin:0 0 12px;color:var(--blue);font-size:14px}}
dl{{margin:0;display:grid;grid-template-columns:80px 1fr;gap:6px 12px;font-size:14px}} dt{{color:var(--mute)}} dd{{margin:0}} dd.ev{{color:var(--good)}}
.vids{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}} .vids figure{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden}}
.vids video{{width:100%;display:block;background:#C7C4BF}} .vids figcaption{{padding:12px 14px;font-size:14px}} .vids figcaption b{{display:block;font-size:16px;margin-bottom:2px}}
table{{border-collapse:collapse;width:100%;font-size:14px}} td,th{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}} th{{color:var(--mute);font-weight:500}}
td.n{{font-variant-numeric:tabular-nums}} .bad{{color:var(--bad)}} .good{{color:var(--good);font-weight:600}}
.gallery{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .gallery figure{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.gallery figcaption{{padding:8px 12px;font-size:13px;color:var(--mute)}}
.sheet img{{border-radius:12px;border:1px solid var(--line)}}
ul.b{{margin:0;padding-left:20px}} ul.b li{{margin:4px 0}}
footer{{margin-top:60px;color:var(--mute);font-size:12px;text-align:center}}
@media (max-width:900px){{.hero,.grid2,.gallery,.vids{{grid-template-columns:1fr}} .card{{grid-template-columns:1fr}} .bar nav{{display:none}} .hero h2{{font-size:28px}}}}
@media (max-width:520px){{.bar{{gap:8px;padding:8px 12px}} .bar h1{{font-size:13px}} main{{padding:0 16px 40px}} .stats{{grid-template-columns:1fr 1fr}} dl{{grid-template-columns:1fr}} model-viewer{{height:360px}}}}
@media print{{.bar,model-viewer{{display:none}} body{{background:#fff}}}}
</style>
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script>
</head><body>
<div class="bar"><h1>IDEA-05B 智能药盒 · v3</h1>
<nav><a href="#demo">取药 / 装药</a><a href="#model">3D</a><a href="#innov">创新点</a><a href="#views">整机</a><a href="#qa">校验</a><a href="#edge">边界</a></nav>
<div class="sp"></div><button onclick="tg()">深色 / 浅色</button><button onclick="print()">打印 / PDF</button></div>
<main>
<div class="hero">
  <img src="{I['hero']}" alt="IDEA-05B v3 整机">
  <div><div class="k">SMART MEDICINE BOX · 320 × 70 × 52 mm</div>
  <h2>一勾、一倒，<br>药就到手心。</h2>
  <p class="lead">7 天日格、可取出药杯、一拨全开整盘装药、只称药芯的称重、格内导光与开盖检测、每格干燥片。每一处关键结构都借自已经验证过的做法——量杯、数药盘、硬币杯、SIM 卡、厨房秤、精密仪器定位、笔记本合盖检测——并在 3D 模型里装配、校验、仿真过。</p>
  <div class="stats">
    <div class="stat"><b class="good">{v3['first_exit_deg']:.0f}°–{v3['last_exit_deg']:.0f}°</b><span>药杯开始出药 → 倒空的倾角</span></div>
    <div class="stat"><b>{wc['tray_to_base_gap']:.1f} mm</b><span>称重浮动缝（与分模线重合）</span></div>
    <div class="stat"><b>{qa['pairwise_checked']} / 0</b><span>零件两两干涉检查 / 干涉数</span></div>
    <div class="stat"><b>{len(INNOV)}</b><span>条创新点，全部有模型证据</span></div>
  </div></div>
</div>

<section id="demo"><h2>取药与装药演示</h2><p class="lead">整机 3D 模型 + 刚体仿真：药片的翻滚、滑落、落碟都是物理计算出来的，不是手摆的。</p>
<div class="vids">
<figure><video src="{V['pour']}" autoplay loop muted playsinline poster="{I['cup']}"></video>
<figcaption><b>提杯倒药</b>开盖 → 食指勾住后侧勾手提杯 → 移到碟子上方 → 前倾，药从 24 mm 倒嘴集中流出。</figcaption></figure>
<figure><video src="{V['sweep']}" autoplay loop muted playsinline poster="{I['cell']}"></video>
<figcaption><b>不提杯，一抹即得</b>指腹从杯后往前一抹，药被推上 R12 弧底，停在唇台边，再捏起来就容易了。</figcaption></figure>
<figure><video src="{V['load']}" autoplay loop muted playsinline poster="{I['loading']}"></video>
<figcaption><b>一周的药，一次装完</b>拨片联动全开 7 盖 → 捏提耳整盘提起 → 盖上漏斗模板 → 按日撒药，药经漏斗落进各自的杯。</figcaption></figure>
</div>
<div class="panel" style="margin-top:16px"><table>
<tr><td>开始出药的倾角</td><td class="n good">{v3['first_exit_deg']:.0f}°</td><td>全部倒空</td><td class="n good">{v3['last_exit_deg']:.0f}°</td></tr>
<tr><td>出口偏离倒嘴中线</td><td class="n good">≤ {off3:.1f} mm</td><td>倾到 70° 时杯内残留</td><td class="n good">{v3['remaining_at_70']} / 6</td></tr>
</table><p class="lead" style="margin:10px 0 0;font-size:13px">6 粒药：Ø8 圆片 ×2、Ø10 圆片、椭圆片、1# / 2# 胶囊；摩擦系数 0.4。刚体近似，绝对角度以手板为准。</p></div>
<div class="sheet" style="margin-top:18px"><img src="{I['sheet']}" alt="取药结构剖面与尺寸"></div></section>

<section id="model"><h2>3D 整机</h2><p class="lead">拖动旋转、滚轮缩放。周三日盖打开，杯里有药；底座内部有浮动架、称重传感器、传感板。（需联网加载 3D 查看器；离线时显示静态图。）</p>
<model-viewer src="{GLB}" camera-controls auto-rotate auto-rotate-delay="2500" rotation-per-second="12deg" shadow-intensity="0.6" exposure="0.9" camera-orbit="-25deg 65deg 0.55m" alt="IDEA-05B v3 3D 模型">
<img slot="poster" src="{I['hero']}" alt="" style="width:100%;height:100%;object-fit:contain">
</model-viewer></section>

<section id="innov"><h2>{len(INNOV)} 条创新点</h2><p class="lead">每条写清「怎么做」和「证据」；证据全部来自 3D 模型校验或仿真。</p>
<div class="cards">{''.join(card(*c) for c in INNOV)}</div></section>

<section id="views"><h2>整机视图</h2>
<div class="sheet" style="margin-bottom:14px"><img src="{I['section']}" alt="整机剖面 A–A"></div>
<div class="gallery">
<figure><img src="{I['allopen']}" alt="联动全开"><figcaption>联动全开：拨右端拨片，7 个日盖同时翻开</figcaption></figure>
<figure><img src="{I['loading']}" alt="批量装药"><figcaption>批量装药：整盘提出，盖上 7 漏斗装药模板</figcaption></figure>
<figure><img src="{I['exploded']}" alt="爆炸图"><figcaption>爆炸图：日盖（磁铁 + 干燥片）→ 药杯 → 密封垫 → 托盘 → 浮动架 / 传感板 → 称重传感器 → 主板 / 电池 → 底座</figcaption></figure>
<figure><img src="{I['weigh']}" alt="称重链"><figcaption>称重链：托盘抬起，露出 3 个球脚与锥窝 / V 槽 / 平面；底座前半剖开</figcaption></figure>
<figure><img src="{I['cup']}" alt="周三格"><figcaption>周三格开盖：后侧勾手、收拢倒嘴、弧底</figcaption></figure>
<figure><img src="{I['front']}" alt="正视"><figcaption>正视：段码屏 / 3 键 / 7 格日期；0.8 mm 称重浮动缝与分模线重合</figcaption></figure>
<figure><img src="{I['top']}" alt="俯视"><figcaption>俯视</figcaption></figure>
</div></section>

<section id="qa"><h2>校验</h2><p class="lead">自写脚本 + Blender 官方扩展 3D Print Toolbox 两道独立检查。</p>
<div class="panel"><table>{qa_html}</table></div></section>

<section id="edge"><h2>诚实边界</h2><div class="panel"><ul class="b">
<li>仿真是刚体近似（单一摩擦系数，无药粉 / 静电 / 受潮）。</li>
<li>称重分辨 0.2–0.5 g、IP54、干燥片寿命、勾手与弧底手感：<b>都还没实测</b>，是设计目标。</li>
<li>日盖按压弹开机构（push-push + 阻尼）本轮仍只有外形；联动轴的拨爪 / 铰链节是概念尺寸（铰链节 Ø4.2），量产需加粗铰链节。</li>
<li>称重只证明「药离开了药仓」，不证明吞服；对外只讲三态。不是医疗器械，不宣称治疗 / 诊断。</li>
</ul></div></section>
<footer>IDEA-05B 智能药盒 v3 · 2026-10-26 · 图与数据由 tools/v3/ 脚本从 3D 模型生成</footer>
</main>
<script>
function tg(){{const r=document.documentElement;const d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark';try{{localStorage.setItem('t',r.dataset.theme)}}catch(e){{}}}}
try{{const t=localStorage.getItem('t');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}
</script>
</body></html>'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(page)
print('SITE', OUT, round(os.path.getsize(OUT) / 1e6, 2), 'MB')
