# IDEA-05B 智能药盒 · v3（2026-10-26）

- **介绍页（在线）**：https://anweat.github.io/idea-05b-smart-medicine-box/v3/
- **3D 实时预览**：https://anweat.github.io/idea-05b-smart-medicine-box/v3/3d.html （闭盖 / 周三开盖 / 一拨全开，可旋转缩放）

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

## 许可

CC BY-NC 4.0（署名 · 非商业）。**商业使用需事先联系作者授权**：GitHub [@anweat](https://github.com/anweat)。详见仓库根目录 [`LICENSE`](../LICENSE)。
