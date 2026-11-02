# -*- coding: utf-8 -*-
"""静态介绍页：板块一 需求与创新（叙述为主）/ 板块二 产品与结构（图为主），两人各讲约 2.5 分钟
单文件，图片全部内嵌，双击离线可看；三维模型另见 3d.html。讲稿见 design/33_讲解稿_双人5分钟.md。
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


def autocrop(im, pad=12, tol=18):
    """按左上角背景色裁掉四周空白（正交视图背景大、产品占比小）。"""
    bg = Image.new('RGB', im.size, im.getpixel((2, 2)))
    box = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > tol else 0).getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def img(path, w=1600, q=84, crop=None):
    im = Image.open(path)
    if im.mode == 'RGBA':                       # 透明底渲染：铺与版面一致的浅灰底
        bg = Image.new('RGB', im.size, (238, 240, 243)); bg.paste(im, mask=im.split()[3]); im = bg
    im = im.convert('RGB')
    if crop == 'auto':
        im = autocrop(im)
    elif crop:
        im = im.crop(crop)
    im.thumbnail((w, w))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


I = {k: img(os.path.join(FULL, k + '_v3.png')) for k in ('hero', 'exploded', 'weigh', 'cup', 'allopen', 'loading')}
I['front'] = img(os.path.join(FULL, 'front_v3.png'), crop='auto')
I['top'] = img(os.path.join(FULL, 'top_v3.png'), crop='auto')
I['cell'] = img(os.path.join(R3, 'v3_cell_iso.png'))
I['pour'] = img(os.path.join(R3, 'v3_pour45.png'), w=1200)
I['section'] = img(os.path.join(DES, '32_整机v3_剖面A-A.png'), w=2000)
I['hinge'] = img(os.path.join(DES, '32_整机v3_剖面A-A.png'), w=1400, crop=(1300, 180, 2380, 820))   # 剖面里铰链脊一角：霍尔 / 磁铁 / 干燥片

# ---------------------------------------------------------------- 板块一 需求与创新（叙述为主）
SOURCE = ('我国老年人慢性病多病共存现象普遍，许多人每日需同时服用多种药物。现有分格药盒以存放为主，'
          '在取药、分装与服药确认三个环节仍依赖使用者的手部灵活性与记忆力：药片沉于格底难以捏取，'
          '每周分装需逐格开盖，是否已经服药无从确认，药品受潮也缺乏有效防护。')
STATS = [('31.8%–48.8%', '社区老年多重用药者的服药不依从率'), ('6 种', '平均同时服用的药物种数'),
         ('46.8%', '非网民中 60 岁及以上人群占比'), ('3–5 kg', '老年人指尖捏力，关节炎患者再降低 30%–40%')]
PEOPLE = [('居家多病共存的老年人', '65 岁以上，每日服用 3 种及以上药物，多为独居或与配偶同住。'),
          ('手部功能或视力减退者', '关节炎、帕金森病等导致捏取困难或手部震颤，或视力下降、辨识困难。'),
          ('家属与照护人员', '负责每周为老人分装药物，并希望远程了解老人的服药情况。')]
SCENES = [('每日定时取药', '到点提醒，当日药格亮灯；开盖后提杯倾倒或指腹推取，即可取出当次药品。'),
          ('每周集中分装', '家属一次开启全部日盖，将托盘整体取出，在桌面借助漏斗板完成一周分装。'),
          ('服药状态记录', '开盖检测与称重联合判断药品是否已被取出，并同步至家属端。'),
          ('日常存放', '每格独立密封并配有干燥片，药杯可单独取出清洗或随身携带。')]
INNOV = [('取药方式由“捏取”改为“倾倒与推取”',
          '药杯设后侧勾手、前部收拢倒药口与圆弧杯底：提杯倾斜约 40° 即开始出药，也可用指腹将药片推至杯口取出，不再依赖精细捏取。'),
         ('一次开启，整盘分装',
          '七个日盖共用一根联动轴，拨动侧面拨片即可同时开启；托盘两端设提耳并配漏斗板，一周药量可在桌面一次分装完成，且不会串格。'),
         ('只称药品的称重结构',
          '托盘经三点定位支承于独立的称重架上，电池与外壳不计入称量；每次放回自动对位、归零，结合开盖检测形成服药记录。'),
         ('药芯不含电子元件',
          '传感与开盖检测全部集成在底座内，托盘与药杯可整体取出水洗；每个日盖内置干燥片，保持密封腔干燥。'),
         ('跨领域成熟结构的移植与验证',
          '上述结构分别借鉴量杯、药房数药盘、收银硬币杯、厨房秤与精密仪器定位等成熟做法，并经三维装配校验与物理仿真验证。')]
VALUE = [('约 ¥210', '单台出厂成本（千台批量估算）'), ('约 ¥17', '全部结构创新带来的单台成本增量'),
         ('¥399', '建议零售价，一次买断'), ('约 ¥2 / 月', '用户持续支出（干燥片）')]



# ---------------------------------------------------------------- 成本明细：直接读 design/34_成本估算_v3.md 的表格，页面与文档保持一致
def md_table(path, heading):
    """取 markdown 里某个二级标题下的第一张表，返回数据行（去掉表头、分隔行与「小计 / 合计」行）。"""
    lines = open(path, encoding='utf-8').read().split('\n')
    i = next(k for k, l in enumerate(lines) if l.startswith('## ' + heading))
    rows = []
    for l in lines[i + 1:]:
        if l.startswith('## '):
            break
        if l.startswith('|'):
            rows.append([c.strip() for c in l.strip('|').split('|')])
        elif rows:
            break
    return [r for r in rows[2:] if not r[0].startswith('**')]


COST_MD = os.path.join(DES, '34_成本估算_v3.md')
SPEC_FIX = {'FPC，藏在铰链脊里': '柔性电路板，置于铰链脊内'}       # 文档里的口语说明换成正式说法
ELEC = md_table(COST_MD, '2.')                    # 物料 | 选型 | 数量 | 单价 | 小计
STRUCT = md_table(COST_MD, '3.')                  # 零件 | 材料 | 重量 | ¥ / 台 | 说明
MOLD = md_table(COST_MD, '5.')                    # 模具 | ¥ 万
OTHER = [('组装、称重标定与出厂测试', '12.0'), ('包装与说明书', '6.0'), ('装药漏斗板（随机附送）', '1.5')]


def cost_tables():
    el = ''.join(f'<tr><td>{E(r[0])}</td><td class="m">{E(SPEC_FIX.get(r[1], r[1]))}</td><td class="n">{E(r[2])}</td><td class="n">{E(r[4])}</td></tr>'
                 for r in ELEC)
    st = ''.join(f'<tr><td>{E(r[0])}</td><td class="m">{E(r[1])}</td><td class="n">{E(r[3])}</td></tr>' for r in STRUCT)
    ot = ''.join(f'<tr><td>{E(a)}</td><td class="n">{E(b)}</td></tr>' for a, b in OTHER)
    mo = ''.join(f'<tr><td>{E(r[0])}</td><td class="n">{E(r[1])}</td></tr>' for r in MOLD)
    e_sum = sum(float(r[4]) for r in ELEC); s_sum = sum(float(r[3]) for r in STRUCT)
    m_lo = sum(float(r[1].split('–')[0]) for r in MOLD); m_hi = sum(float(r[1].split('–')[1]) for r in MOLD)
    return f'''<details class="costd" open><summary>成本明细（千台批量估算，单位：元 / 台）</summary><div class="ctab">
<div><h4>电子元件 <span>≈ {e_sum:.0f}</span></h4><table><tr><th>物料</th><th>规格</th><th class="n">数量</th><th class="n">小计</th></tr>{el}</table></div>
<div><h4>结构件 <span>≈ {s_sum:.0f}</span></h4><table><tr><th>零件</th><th>材料</th><th class="n">小计</th></tr>{st}</table></div>
<div><h4>其他费用 <span>≈ {sum(float(b) for _, b in OTHER):.1f}</span></h4><table>{ot}</table>
<h4 style="margin-top:16px">一次性模具 <span>约 {m_lo:.0f}–{m_hi:.0f} 万元</span></h4><table>{mo}</table>
<p class="cnote">模具按产量摊销：5 千台约 22–37 元 / 台，1 万台约 11–18 元 / 台。认证检测费用未计入。</p></div>
</div></details>'''


# ---------------------------------------------------------------- 板块二 产品与结构（图为主，每处一句）
USE = [('cup', '开启当日日盖，当日药格亮灯'), ('pour', '勾起药杯，倾斜即可倒出'),
       ('allopen', '拨动拨片，七个日盖同时开启'), ('loading', '整盘取出，配合漏斗板分装')]
KEYS = [('取药结构', 'cell', '后侧勾手、前部收拢倒药口与 R12 圆弧杯底；杯体单角切角，防止反装。'),
        ('装药结构', 'allopen', '铰链驱动轴带动七个日盖同步开启；托盘两端设提耳，配合漏斗板整盘分装。'),
        ('称重结构', 'weigh', '托盘经锥窝、V 槽、平面三点支承于铝制浮动架，下设 500 g 单点称重传感器。'),
        ('感知与保存', 'hinge', '红外与导光元件位于托盘下方并设隔光墙；霍尔传感器位于铰链脊内；日盖内置干燥片。')]
CHECKS = [('%d 对' % qa['pairwise_checked'], '零部件两两干涉检查，均无干涉'), ('0°–100°', '联动开盖全行程无干涉'),
          ('%.0f° / %.0f°' % (v3['first_exit_deg'], v3['last_exit_deg']), '倒药仿真：开始出药 / 完全倒空'),
          ('%.1f mm' % wc['tray_to_base_gap'], '称重间隙，与外壳分模线重合')]


CSS = '''
:root{--bg:#F4F6F9;--panel:#FFFFFF;--ink:#1C2733;--ink2:#46535F;--mute:#7A8794;--line:#DEE4EB;--accent:#1F5FAF;--accent2:#E9F0F9}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#7AAEF0;--accent2:#1C2B3D}}
:root[data-theme="dark"]{--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#7AAEF0;--accent2:#1C2B3D}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;line-height:1.7}
img{max-width:100%;display:block}
.top{position:sticky;top:0;z-index:9;display:flex;gap:18px;align-items:center;padding:10px 24px;background:color-mix(in srgb,var(--panel) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top b{font-size:15px;white-space:nowrap;letter-spacing:.5px} .top nav{display:flex;gap:18px;font-size:13px} .top nav a{color:var(--ink2);text-decoration:none;white-space:nowrap} .top nav a:hover{color:var(--accent)}
.top .sp{flex:1} .btn{white-space:nowrap;font-size:12px;padding:6px 12px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;text-decoration:none} .btn.pri{background:var(--accent);border-color:var(--accent);color:#fff}
button{white-space:nowrap;font:inherit;font-size:12px;padding:6px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:8px;cursor:pointer}
main{max-width:1140px;margin:0 auto;padding:0 24px 60px}
.cover{display:grid;grid-template-columns:1.4fr 1fr;gap:36px;align-items:center;margin-top:32px}
.cover img{border-radius:14px;box-shadow:0 16px 44px rgba(25,45,70,.12)}
.cover h1{font-size:36px;line-height:1.3;margin:0 0 6px;letter-spacing:1px} .cover .sub{font-size:16px;color:var(--accent);margin:0 0 14px}
.lead{color:var(--ink2);margin:0 0 16px;font-size:15px}
.specs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px} .specs span{font-size:13px;color:var(--ink2);background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:3px 12px}
.cta .btn{font-size:14px;padding:8px 18px;display:inline-block}
.part{margin-top:72px;padding:18px 0 12px;border-bottom:2px solid var(--accent)}
.part small{display:block;color:var(--accent);font-size:13px;letter-spacing:2px;font-weight:600} .part h2{margin:2px 0 0;font-size:28px;letter-spacing:1px}
section{margin-top:32px} h3{font-size:19px;margin:0 0 12px;display:flex;gap:10px;align-items:baseline} h3 i{font-style:normal;color:var(--accent);font-size:15px;font-variant-numeric:tabular-nums}
.para{font-size:15px;color:var(--ink2);margin:0 0 16px;max-width:900px;text-align:justify}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.stat b{display:block;font-size:26px;font-variant-numeric:tabular-nums;line-height:1.25} .stat span{display:block;color:var(--ink2);font-size:13.5px;margin-top:4px}
.src{color:var(--mute);font-size:12px;margin:8px 0 0}
.cards{display:grid;gap:12px} .c3{grid-template-columns:repeat(3,1fr)} .c4{grid-template-columns:repeat(4,1fr)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.card b{display:block;font-size:16px;margin-bottom:4px} .card p{margin:0;font-size:14px;color:var(--ink2)}
.innov{display:grid;gap:12px}
.inv{display:grid;grid-template-columns:56px 1fr;gap:4px 14px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.inv i{grid-row:span 2;font-style:normal;font-size:26px;font-weight:700;color:var(--accent);font-variant-numeric:tabular-nums;line-height:1.2}
.inv b{font-size:16.5px} .inv p{margin:0;font-size:14.5px;color:var(--ink2)}
.figs{display:grid;gap:14px} .f2{grid-template-columns:1fr 1fr} .f4{grid-template-columns:repeat(4,1fr)} .fov{grid-template-columns:1fr 1.4fr}
figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
figure .im{background:#E8EBEF;overflow:hidden;flex:1} figure .im img{width:100%;height:100%;object-fit:cover}
figure.fit .im{background:#F7F8FA} figure.fit .im img{object-fit:contain} figure.nat .im{flex:1;display:flex;align-items:center;background:#EEF0F3} figure.nat .im img{height:auto}
.f4 .im{aspect-ratio:4/3} .keys .im{aspect-ratio:16/9}
figcaption{padding:10px 14px;font-size:14px;color:var(--ink2)} figcaption b{display:block;color:var(--ink);font-size:16px;margin-bottom:2px}
.note{color:var(--ink2);font-size:14.5px;margin:12px 0 0}
.costd{margin-top:16px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 18px}
.costd summary{cursor:pointer;font-size:14px;color:var(--ink2);font-weight:600;padding:2px 0}
.ctab{display:grid;grid-template-columns:1.25fr 1fr .9fr;gap:22px;margin-top:12px}
.ctab h4{margin:0 0 6px;font-size:14px;display:flex;justify-content:space-between} .ctab h4 span{color:var(--accent);font-variant-numeric:tabular-nums}
.ctab table{border-collapse:collapse;width:100%;font-size:12.5px} .ctab th{color:var(--mute);font-weight:500;text-align:left;padding:4px 4px;border-bottom:1px solid var(--line);white-space:nowrap}
.ctab td{padding:4px 4px;border-bottom:1px solid var(--line);color:var(--ink2);vertical-align:top} .ctab td.m{color:var(--mute)} .ctab .n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.cnote{font-size:12px;color:var(--mute);margin:8px 0 0}
footer{margin-top:56px;color:var(--mute);font-size:12px;text-align:center;line-height:1.9} footer a{color:inherit}
@media (max-width:900px){.cover,.f2,.fov,.c3,.ctab{grid-template-columns:1fr} .stats,.c4,.f4{grid-template-columns:1fr 1fr} .top nav{display:none} .cover h1{font-size:28px}}
@media (max-width:520px){main{padding:0 16px 40px} .top{padding:8px 12px;gap:8px} .top b{font-size:13px} .top button{display:none} .stats,.c4{grid-template-columns:1fr} .stat b{font-size:22px} .inv{grid-template-columns:40px 1fr} .inv i{font-size:20px}}
@media print{.top{display:none} body{background:#fff} .part{break-before:page}}
'''

stats = ''.join(f'<div class="stat"><b>{E(v)}</b><span>{E(t)}</span></div>' for v, t in STATS)
people = ''.join(f'<div class="card"><b>{E(a)}</b><p>{E(b)}</p></div>' for a, b in PEOPLE)
scenes = ''.join(f'<div class="card"><b>{E(a)}</b><p>{E(b)}</p></div>' for a, b in SCENES)
innov = ''.join(f'<div class="inv"><i>{k + 1:02d}</i><b>{E(a)}</b><p>{E(b)}</p></div>' for k, (a, b) in enumerate(INNOV))
value = ''.join(f'<div class="stat"><b>{E(v)}</b><span>{E(t)}</span></div>' for v, t in VALUE)
use = ''.join(f'<figure><div class="im"><img src="{I[k]}" alt="{E(t)}"></div><figcaption>{E(t)}</figcaption></figure>' for k, t in USE)
keys = ''.join(f'<figure class="{"fit" if k == "hinge" else ""}"><div class="im"><img src="{I[k]}" alt="{E(t)}"></div>'
               f'<figcaption><b>{E(t)}</b>{E(d)}</figcaption></figure>' for t, k, d in KEYS)
checks = ''.join(f'<div class="stat"><b>{E(v)}</b><span>{E(t)}</span></div>' for v, t in CHECKS)

page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>适老智能药盒</title><style>{CSS}</style></head><body>
<div class="top"><b>适老智能药盒</b>
<nav><a href="#p1">一 · 需求与创新</a><a href="#p2">二 · 产品与结构</a></nav>
<div class="sp"></div><a class="btn pri" href="{LINK3D}">三维模型</a><a class="btn" href="{REPO}" target="_blank" rel="noopener">开源仓库</a>
<button onclick="tg()">深色 / 浅色</button></div>
<main>

<div class="cover">
  <img src="{I['hero']}" alt="适老智能药盒整机">
  <div><h1>适老智能药盒</h1><p class="sub">让取药与分装更简单</p>
  <p class="lead">面向居家多重用药的老年人，将取药、每周分装与服药记录整合于一台桌面设备，降低对手部灵活性与记忆力的依赖。</p>
  <div class="specs"><span>320 × 70 × 52 mm</span><span>七日分格</span><span>段码屏 + 三键</span><span>称重 · 红外 · 开盖检测</span><span>离线语音提醒</span></div>
  <p class="cta"><a class="btn pri" href="{LINK3D}">查看三维模型</a></p></div>
</div>

<div class="part" id="p1"><small>板块一</small><h2>需求与创新</h2></div>
<section><h3><i>1.1</i>问题来源</h3><p class="para">{E(SOURCE)}</p><div class="stats">{stats}</div>
<p class="src">数据来源：BMC Geriatrics（2023）、中国互联网络信息中心第 55 次统计报告、国民体质监测标准及相关文献。</p></section>
<section><h3><i>1.2</i>目标人群</h3><div class="cards c3">{people}</div></section>
<section><h3><i>1.3</i>应用场景</h3><div class="cards c4">{scenes}</div></section>
<section><h3><i>1.4</i>核心创新</h3><div class="innov">{innov}</div></section>
<section><h3><i>1.5</i>价值与成本</h3><div class="stats">{value}</div>
<p class="note">产品定位于白牌分格药盒（¥23–45）与进口按月收费分药设备（¥213–888 / 月）之间；多数结构创新由模具几何实现，不增加零件数量。</p>
{cost_tables()}</section>

<div class="part" id="p2"><small>板块二</small><h2>产品与结构</h2></div>
<section><h3><i>2.1</i>产品外观</h3><div class="figs f2">
<figure class="nat"><div class="im"><img src="{I['top']}" alt="俯视"></div><figcaption>俯视：长条形桌面形态，上部为七个独立日盖，可单独开启。</figcaption></figure>
<figure class="nat"><div class="im"><img src="{I['front']}" alt="正视"></div><figcaption>正视：前部为段码屏与三个按键，无需使用手机即可完成操作。</figcaption></figure></div></section>
<section><h3><i>2.2</i>使用方式</h3><div class="figs f4">{use}</div></section>
<section><h3><i>2.3</i>结构组成</h3><div class="figs fov">
<figure><div class="im"><img src="{I['exploded']}" alt="爆炸图"></div><figcaption>自上而下：日盖、药杯、托盘、称重浮动架与传感板、底座。</figcaption></figure>
<figure class="fit"><div class="im"><img src="{I['section']}" alt="整机剖面"></div><figcaption>整机剖面：药芯与电子部分完全分离。</figcaption></figure></div></section>
<section><h3><i>2.4</i>关键结构</h3><div class="figs f2 keys">{keys}</div></section>
<section><h3><i>2.5</i>设计验证</h3><div class="stats">{checks}</div></section>

<footer>注：倒药结果为刚体仿真，称重精度与操作手感有待样机测试；称重仅反映药品是否被取出，不作为服药证明。本产品不属于医疗器械。<br>
© 2026 anweat · <a href="{REPO}" target="_blank" rel="noopener">开源仓库</a> · 采用 <a href="{REPO}/blob/main/LICENSE" target="_blank" rel="noopener">CC BY-NC 4.0</a> 许可，商业使用请联系作者</footer>
</main>
<script>
function tg(){{const r=document.documentElement;const d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark';try{{localStorage.setItem('t',r.dataset.theme)}}catch(e){{}}}}
try{{const t=localStorage.getItem('t');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}
</script></body></html>'''

open(OUT, 'w', encoding='utf-8').write(page)
print('INTRO', OUT, round(os.path.getsize(OUT) / 1e6, 2), 'MB')
