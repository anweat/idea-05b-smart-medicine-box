# -*- coding: utf-8 -*-
"""IDEA-05B v3 · 3D 实时预览页（model-viewer，闭盖 / 周三开盖 / 一拨全开 三种状态 + 关键结构标注）
GLB 作为同目录 assets/ 下的独立文件加载（GitHub Pages / 本地服务器打开；需联网加载查看器脚本）。
    python3 tools/v3/make_3d_page.py <输出目录> [model-viewer 脚本地址]   # 写 <输出目录>/3d.html + assets/*.glb + assets/poster.jpg
仓库 Pages 版传 ../assets/model-viewer.min.js（原产品页自托管的 v4.1.0），本地预览默认用 CDN。
"""
import os, sys, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WEB = os.path.join(ROOT, 'model', 'v3', 'web')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'design', 'web_v3')
MV = sys.argv[2] if len(sys.argv) > 2 else 'https://cdn.jsdelivr.net/npm/@google/model-viewer@4.1.0/dist/model-viewer.min.js'
REPO = 'https://github.com/anweat/idea-05b-smart-medicine-box'
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
for n in ('closed', 'open', 'allopen'):
    shutil.copy2(os.path.join(WEB, n + '.glb'), os.path.join(OUT, 'assets', n + '.glb'))
im = Image.open(os.path.join(ROOT, 'renders', 'v3', 'full', 'hero_v3.png')).convert('RGB')
im.thumbnail((1400, 1400))
im.save(os.path.join(OUT, 'assets', 'poster.jpg'), quality=82, optimize=True, progressive=True)


def gl(x, y, z):
    """Blender 坐标（mm，Z 向上）→ glTF 坐标（m，Y 向上）。"""
    return '%.4fm %.4fm %.4fm' % (x / 1000, z / 1000, -y / 1000)


# 标注点：都在不随状态移动的零件上
HOTSPOTS = [(gl(115.6, 58.0, 48.6), '后侧勾手', '勾起杯子就能倒'),
            (gl(115.6, 9.5, 35.0), '24 mm 倒嘴', '药从中间排队出来'),
            (gl(317.6, 60.0, 31.0), '全开拨片', '拨一下 7 盖齐开'),
            (gl(2.0, 34.0, 35.5), '托盘提耳', '整盘端走装药'),
            (gl(60.0, -0.5, 12.0), '段码屏 + 3 键', '老人不用学手机')]
hs = ''.join(f'''<button class="hs" slot="hotspot-{i}" data-position="{p}" data-normal="0m 1m 0m"><span><b>{t}</b>{d}</span></button>'''
             for i, (p, t, d) in enumerate(HOTSPOTS))

page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDEA-05B 3D 模型</title>
<style>
:root{{--bg:#EEF1F5;--panel:#FFFFFF;--ink:#1F2A37;--ink2:#4A5868;--mute:#7A8899;--line:#DFE6EE;--accent:#1D6FD6}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#6AA8F5}}}}
:root[data-theme="dark"]{{--bg:#11161C;--panel:#1A222B;--ink:#E4EAF1;--ink2:#B5C1CE;--mute:#8B99A8;--line:#2B3642;--accent:#6AA8F5}}
*{{box-sizing:border-box}} html,body{{height:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;display:flex;flex-direction:column}}
.top{{display:flex;gap:14px;align-items:center;padding:10px 20px;background:var(--panel);border-bottom:1px solid var(--line)}}
.top b{{font-size:15px;white-space:nowrap}} .top a{{color:var(--ink2);text-decoration:none;font-size:13px;white-space:nowrap}} .top a:hover{{color:var(--accent)}} .sp{{flex:1}}
.bar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px 20px}}
.seg{{display:inline-flex;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:3px}}
.seg button{{font:inherit;font-size:13px;border:0;background:transparent;color:var(--ink2);padding:6px 14px;border-radius:7px;cursor:pointer;white-space:nowrap}}
.seg button[aria-pressed="true"]{{background:var(--accent);color:#fff}}
.tog{{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:6px 12px;border-radius:8px;cursor:pointer;white-space:nowrap}}
.hint{{color:var(--mute);font-size:12px;margin-left:auto}}
model-viewer{{flex:1;width:100%;min-height:420px;background:radial-gradient(ellipse at 50% 40%,var(--panel),var(--bg));--poster-color:transparent}}
.hs{{border:0;background:transparent;padding:0;cursor:default}}
.hs::before{{content:"";display:block;width:12px;height:12px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px rgba(255,255,255,.85)}}
.hs span{{position:absolute;left:18px;top:-6px;white-space:nowrap;background:var(--panel);color:var(--ink2);border:1px solid var(--line);border-radius:8px;padding:4px 9px;font-size:12px;line-height:1.35;box-shadow:0 4px 14px rgba(0,0,0,.08)}}
.hs span b{{display:block;color:var(--ink);font-size:13px}}
.nolabels .hs span{{display:none}}
@media (max-width:640px){{.top{{padding:8px 12px;gap:10px}} .bar{{padding:10px 12px}} .hint{{display:none}} .hs span{{font-size:11px}} .top .opt{{display:none}}}}
</style>
<script type="module" src="{MV}"></script>
</head><body>
<div class="top"><b>IDEA-05B 智能药盒 · 3D</b><div class="sp"></div>
<a href="index.html">← 介绍页</a><a class="opt" href="{REPO}" target="_blank" rel="noopener">GitHub</a>
<a class="opt" href="{REPO}/blob/main/LICENSE" target="_blank" rel="noopener">CC BY-NC 4.0 · 商用请联系</a></div>
<div class="bar">
  <div class="seg" role="group" aria-label="状态">
    <button data-src="assets/closed.glb">闭盖</button>
    <button data-src="assets/open.glb" aria-pressed="true">周三开盖</button>
    <button data-src="assets/allopen.glb">一拨全开</button>
  </div>
  <button class="tog" id="rot">自动旋转：开</button>
  <button class="tog" id="lab">标注：开</button>
  <span class="hint">拖动旋转 · 滚轮 / 双指缩放 · 右键 / 双指平移</span>
</div>
<model-viewer id="mv" src="assets/open.glb" poster="assets/poster.jpg" alt="IDEA-05B 智能药盒 3D 模型"
  camera-controls auto-rotate auto-rotate-delay="3000" rotation-per-second="10deg" interaction-prompt="none"
  camera-orbit="25deg 64deg 0.5m" min-camera-orbit="auto auto 0.18m" max-camera-orbit="auto auto 1.2m"
  shadow-intensity="0.7" shadow-softness="0.9" exposure="0.95" environment-image="neutral">{hs}</model-viewer>
<script>
const mv=document.getElementById('mv');
document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{{
  document.querySelectorAll('.seg button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  const orbit=mv.getCameraOrbit(); mv.src=b.dataset.src;
  mv.addEventListener('load',()=>{{mv.cameraOrbit=`${{orbit.theta}}rad ${{orbit.phi}}rad ${{orbit.radius}}m`;}},{{once:true}});
}});
const rot=document.getElementById('rot');
rot.onclick=()=>{{mv.autoRotate=!mv.autoRotate;rot.textContent='自动旋转：'+(mv.autoRotate?'开':'关');}};
const lab=document.getElementById('lab');
lab.onclick=()=>{{const off=mv.classList.toggle('nolabels');lab.textContent='标注：'+(off?'关':'开');}};
</script></body></html>'''
open(os.path.join(OUT, '3d.html'), 'w', encoding='utf-8').write(page)
print('PAGE3D', OUT)
