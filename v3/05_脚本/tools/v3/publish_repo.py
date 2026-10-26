# -*- coding: utf-8 -*-
"""把 v3 同步进 GitHub 仓库的工作副本（不改动 v1 原有内容，只追加 / 覆盖 v3 部分）
    python3 tools/v3/publish_repo.py <仓库工作副本目录>
写入：
    v3/                 文档、模型、打印件、渲染图、脚本、校验数据 + README
    docs/v3/            GitHub Pages：index.html（介绍页）+ 3d.html（3D 实时预览）+ assets/
    docs/index.html     顶部加一条 v3 入口（只加一次）
    README.md           开头加 v3 一节（只加一次）
之后在仓库目录里 git add / commit / push。
"""
import os, sys, shutil, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.abspath(sys.argv[1])
PAGES = 'https://anweat.github.io/idea-05b-smart-medicine-box/v3/'
J = lambda *p: os.path.join(ROOT, *p)

FILES = {
    '01_设计文档': [J('design', f) for f in ('31_创新点详述_v3.md', '30_取药结构v3_成熟实践方案.md', '33_讲解稿_双人5分钟.md',
                                         '34_成本估算_v3.md', '32_整机v3_剖面A-A.png', '30_取药结构v3_剖面与尺寸.png')],
    '02_三维模型': [J('model', 'v3', f) for f in ('IDEA-05_box_v3.blend', 'IDEA-05_box_v3.glb', 'IDEA-05_box_v3_closed.glb',
                                              '取药结构_v3.blend', '取药结构_v3.glb')],
    '03_打印件': sorted(glob.glob(J('stl', 'v3_*.stl'))),
    '04_渲染图': sorted(glob.glob(J('renders', 'v3', 'full', '*.png'))) + sorted(glob.glob(J('renders', 'v3', 'v3_*.png'))),
    '05_脚本/tools/v3': sorted(glob.glob(J('tools', 'v3', '*.py'))) + [J('tools', 'v3', 'encode_anim.sh')],
    '05_脚本/tools/v2': [J('tools', 'v2', 'lib.py')],
    '05_脚本/tools': [J('tools', 'draw_lib.py')],
    '06_校验数据': sorted(glob.glob(J('model', 'v3', '*.json'))),
}

V3_README = f'''# IDEA-05B 智能药盒 · v3（2026-10-26）

- **介绍页（在线）**：{PAGES}
- **3D 实时预览**：{PAGES}3d.html （闭盖 / 周三开盖 / 一拨全开，可旋转缩放）

v3 保持 320 × 70 × 52 的外形和 7 天日格，把取药、装药、称重、感知、保存的结构全部重做，每一处都借自已验证的做法，并在 3D 模型里装配、校验、仿真：

| 组 | 结构 | 借鉴 |
|---|---|---|
| 取药 | 后勾前嘴 · 收拢倒嘴 · R12 圆弧杯底 · 切角防呆 | 量杯 · 药房数药盘 · 收银机硬币杯 · SIM 卡 |
| 装药 | 同轴空程联动全开 · 提耳整盘提出 + 装药漏斗板 | 单向拨爪 · 烤盘耳 |
| 称重 | 浮动架 + 500 g 单点称重 · 三点运动学定位 | 厨房秤 · 精密仪器 |
| 感知 / 保存 | 通光孔 + 隔光墙 · 霍尔在铰链脊 · 干燥片进日盖 | 笔记本电脑合盖检测 |

## 目录

```
v3/
├─ 01_设计文档/   创新点详述、取药结构方案、讲解稿（双人 5 分钟）、成本估算、整机 / 取药剖面图
├─ 02_三维模型/   整机 IDEA-05_box_v3.blend（米制 1:1）+ GLB；取药结构单件模型
├─ 03_打印件/     药杯、托盘、装药漏斗模板 STL（mm）
├─ 04_渲染图/     主视觉 / 联动全开 / 批量装药 / 杯特写 / 爆炸 / 称重链 / 正视 / 俯视；取药结构图
├─ 05_脚本/       全部重建脚本（tools/v3/params.py 一处改参数）
└─ 06_校验数据/   干涉 / 间隙 / 联动 / 仿真 / 3D Print Toolbox 复检结果（JSON）
```

## 校验摘要

- 全机 103 对零件两两干涉为 0；联动全开 0→100° 与单开日盖全程无干涉；
- 托盘只压在称重浮动架上，离底座 / 铰链脊 0.8 mm（与分模线重合）；
- 倒药刚体仿真：倾过 40° 开始出药，58° 倒空；批量装药仿真 21 粒药全部落入本格杯；
- 出厂成本约 ¥210 / 台（1 千台批量），全部结构创新合计约 +¥17。

## 重建

脚本按原工作区目录结构写（`tools/`、`model/`、`renders/`、`design/` 同级），Blender 5.2：

```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b --factory-startup --python tools/v3/build_v3.py      # 取药结构单件 + 校验
$B -b --factory-startup --python tools/v3/build_full.py    # 整机集成 + 校验（读第一版 model/IDEA-05_box.blend）
$B -b --factory-startup --python tools/v3/render_full.py -- hero allopen loading cup exp weigh front top
python3 tools/v3/make_intro.py && python3 tools/v3/make_3d_page.py
```

边界：仿真为刚体近似；称重精度、IP54、手感未实测；不是医疗器械，称重只证明药离开药盒。
'''

BANNER = ('<div id="v3-banner" style="background:#1D6FD6;color:#fff;text-align:center;font-size:14px;padding:9px 16px">'
          '新版 v3：取药 / 装药 / 称重结构全面升级 · '
          '<a href="v3/" style="color:#fff;font-weight:700">看介绍页</a> · '
          '<a href="v3/3d.html" style="color:#fff;font-weight:700">3D 实时预览</a></div>')
README_V3 = f'''## 新版 v3（2026-10-26）

- **介绍页**：{PAGES}　·　**3D 实时预览**：{PAGES}3d.html
- 文件：[`v3/`](v3/)（文档、模型、打印件、渲染图、脚本、校验数据），说明见 [`v3/README.md`](v3/README.md)
- 取药 / 装药 / 称重 / 感知 / 保存结构全部重做；下文为第一版（2026-10-18）内容，保留不动。

---

'''

# ---------------------------------------------------------------- v3/ 文件
dst_root = os.path.join(REPO, 'v3')
if os.path.exists(dst_root):
    shutil.rmtree(dst_root)
n = 0
for sub, paths in FILES.items():
    d = os.path.join(dst_root, sub)
    os.makedirs(d, exist_ok=True)
    for p in paths:
        shutil.copy2(p, d); n += 1
open(os.path.join(dst_root, 'README.md'), 'w', encoding='utf-8').write(V3_README)

# ---------------------------------------------------------------- docs/v3 页面
web = os.path.join(REPO, 'docs', 'v3')
if os.path.exists(web):
    shutil.rmtree(web)
subprocess.run([sys.executable, os.path.join(HERE, 'make_3d_page.py'), web, '../assets/model-viewer.min.js'], check=True)
subprocess.run([sys.executable, os.path.join(HERE, 'make_intro.py'), os.path.join(web, 'index.html'), '3d.html'], check=True)

# ---------------------------------------------------------------- v1 入口（只加一次）
idx = os.path.join(REPO, 'docs', 'index.html')
s = open(idx, encoding='utf-8').read()
if 'id="v3-banner"' not in s:
    s = s.replace('<body>', '<body>\n' + BANNER, 1)
    open(idx, 'w', encoding='utf-8').write(s)
rd = os.path.join(REPO, 'README.md')
s = open(rd, encoding='utf-8').read()
if '## 新版 v3' not in s:
    head, rest = s.split('\n', 1)
    s = head + '\n\n' + README_V3 + rest.lstrip('\n')
    open(rd, 'w', encoding='utf-8').write(s)
print('PUBLISH', REPO, n, 'files')
