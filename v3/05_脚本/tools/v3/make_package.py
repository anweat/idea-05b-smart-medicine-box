# -*- coding: utf-8 -*-
"""打 v3 交付包：展示页 + 文档 + 模型 + 打印件 + 渲染 + 脚本 + 校验数据 → 目录 + zip
    python3 tools/v3/make_package.py
"""
import os, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATE = '20261026'
NAME = 'IDEA-05_智能药盒_v3交付包_%s' % DATE
PKG = os.path.join(ROOT, NAME)

J = lambda *p: os.path.join(ROOT, *p)
FILES = {
    '00_展示页': [J('design', 'IDEA-05B_v3_展示.html')],
    '01_设计文档': [J('design', '31_创新点详述_v3.md'), J('design', '30_取药结构v3_成熟实践方案.md'),
                J('design', '32_整机v3_剖面A-A.png'), J('design', '30_取药结构v3_剖面与尺寸.png'),
                J('00_状态与下一步.md')],
    '02_三维模型': [J('model', 'v3', f) for f in ('IDEA-05_box_v3.blend', 'IDEA-05_box_v3.glb',
                                              'IDEA-05_box_v3_closed.glb', '取药结构_v3.blend', '取药结构_v3.glb')],
    '03_打印件': [J('stl', 'v3_药杯.stl'), J('stl', 'v3_托盘.stl'), J('stl', 'v3_装药漏斗模板.stl')],
    '04_渲染/整机': [J('renders', 'v3', 'full', f) for f in sorted(os.listdir(J('renders', 'v3', 'full')))
                  if f.endswith('.png')],
    '04_渲染/取药结构': [J('renders', 'v3', f) for f in sorted(os.listdir(J('renders', 'v3')))
                     if f.startswith('v3_') and f.endswith('.png')],
    '04_渲染/动画': [J('renders', 'v3', 'anim', m + ext) for m in ('pour', 'sweep', 'load') for ext in ('.mp4', '.gif')],
    '05_脚本/v3': [J('tools', 'v3', f) for f in sorted(os.listdir(J('tools', 'v3'))) if f.endswith('.py')],
    '05_脚本/v2': [J('tools', 'v2', 'lib.py')],
    '05_脚本': [J('tools', 'draw_lib.py')],
    '06_校验数据': [J('model', 'v3', f) for f in ('full_qa.json', 'v3_report.json', 'print3d_check.json',
                                              'sim_pour_report.json', 'sections.json', 'full_section.json')],
}

README = '''# IDEA-05B 智能药盒 · v3 交付包（{date}）

**先打开 `00_展示页/IDEA-05B_v3_展示.html`**（单文件，双击离线可看；3D 交互查看需联网加载查看器）。

## v3 做了什么
320×70×52 / 7 个烟灰日盖 / 前脸屏 + 3 键。取药、装药、称重、感知、保存都用别的行业验证过的结构：
量杯式后勾手、数药盘式收拢倒嘴、硬币杯式 R12 弧底、SIM 卡式防呆、同轴空程联动全开 + 提耳整盘提出 + 装药漏斗模板、
厨房秤式浮动架 + 单点称重、三点运动学定位（锥窝 / V 槽 / 平面）、笔记本式开盖检测（霍尔在铰链脊、磁铁在盖）、干燥片进密封腔。
11 条创新点的详细说明见 `01_设计文档/31_创新点详述_v3.md`。

## 目录
- `00_展示页/` 展示 HTML
- `01_设计文档/` 创新点详述、取药结构方案、整机剖面 A–A、取药结构剖面与尺寸、项目状态
- `02_三维模型/` 整机 `IDEA-05_box_v3.blend`（米制 1:1）+ GLB（开盖 / 闭盖）；取药结构单件模型
- `03_打印件/` 药杯、托盘、装药漏斗模板 STL（mm）
- `04_渲染/` 整机（主视觉 / 联动全开 / 批量装药 / 杯特写 / 爆炸 / 称重链 / 正视 / 俯视）、取药结构、动画（提杯倒药 / 一抹即得 / 批量装药，MP4 + GIF）
- `05_脚本/` 全部重建脚本（`v3/params.py` 一处改参数）
- `06_校验数据/` 整机干涉与间隙、3D Print Toolbox 复检、倒药仿真、截面数据

## 重建（Blender 5.2，在原工作区目录结构下运行）
```bash
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b --factory-startup --python tools/v3/build_v3.py        # 取药结构单件 + 校验
$B -b --factory-startup --python tools/v3/build_full.py      # 整机集成 + 校验（读 model/IDEA-05_box.blend）
$B -b --factory-startup --python tools/v3/render_full.py -- hero allopen loading cup exp weigh front top
for m in pour sweep load; do $B -b --factory-startup --python tools/v3/anim_take.py -- $m; done
tools/v3/encode_anim.sh pour sweep load                      # 帧 → MP4 / GIF（需 ffmpeg）
$B -b model/v3/取药结构_v3.blend --python tools/v3/check_print3d.py   # 需 3D Print Toolbox 扩展
python3 tools/v3/make_site.py && python3 tools/v3/make_package.py
```

## 边界
仿真为刚体近似；称重分辨率、IP54、勾手 / 弧底手感未实测；日盖弹开机构仍只有外形；联动轴拨爪 / 铰链节为概念尺寸；托盘 312 宽需设计确认。
'''.format(date=DATE)

if os.path.exists(PKG):
    shutil.rmtree(PKG)
rows = []
for sub, paths in FILES.items():
    d = os.path.join(PKG, sub)
    os.makedirs(d, exist_ok=True)
    for p in paths:
        if not os.path.exists(p):
            print('MISSING', p)
            continue
        shutil.copy2(p, d)
        rows.append((os.path.getsize(p), os.path.join(sub, os.path.basename(p))))
open(os.path.join(PKG, 'README.md'), 'w', encoding='utf-8').write(README)
total = sum(r[0] for r in rows)
lines = ['IDEA-05B 智能药盒 · v3 交付包 · 文件清单', '=' * 60,
         '文件数：%d    合计：%.2f MB' % (len(rows) + 1, total / 1e6), '']
lines += ['%10.1f KB  %s' % (s / 1024, p) for s, p in sorted(rows, key=lambda r: r[1])]
open(os.path.join(PKG, '文件清单.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
zp = PKG + '.zip'
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for base, _, fs in os.walk(PKG):
        for f in fs:
            full = os.path.join(base, f)
            z.write(full, os.path.relpath(full, ROOT))
print('PKG', PKG, len(rows), 'files', round(total / 1e6, 1), 'MB  zip', round(os.path.getsize(zp) / 1e6, 1), 'MB')
