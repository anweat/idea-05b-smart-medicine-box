# IDEA-05B 国内部署评估与操作清单

> 目标：让产品页在国内稳定访问；保留 GitHub 作为国际版。
> 现状：GitHub Pages 可用但国内访问不稳定；Gitee 已登录，但 **Gitee Pages 已停止服务**。

---

## 0. 结论先说

| 平台 | 可行性 | 说明 | 推荐度 |
|---|---|---|---|
| **Gitee Pages** | ❌ 不可行 | 2025–2026 社区反馈：仓库「服务」里已没有 Gitee Pages 入口，Gitee Pages 已停服/下线；Gitee 仍可做代码仓库 + 发行版附件 | 不推荐 |
| **AtomGit Pages** | ✅ 可行 | 开放原子基金会，国内开源平台；支持个人 Pages 仓库；可导入 GitHub/Gitee 仓库；需 AtomGit 账号/实名 | ⭐⭐⭐⭐（最贴合“国内开源平台”） |
| **GitCode Pages** | ✅ 可行 | CSDN 旗下，国内；Pages 功能可用；需 GitCode 账号 | ⭐⭐⭐ |
| **EdgeOne Pages（腾讯）** | ✅ 可行 | 国内 CDN；有免费额度；支持 Pages Drop 拖拽上传 / Git 集成；需腾讯云/EdgeOne 账号 | ⭐⭐⭐⭐⭐（最快、最稳） |
| CloudBase 静态托管（腾讯） | ✅ 可行 | 默认域名国内可访问；需腾讯云账号；CLI/控制台部署 | ⭐⭐⭐ |
| Vercel / Netlify / Cloudflare Pages | ⚠️ 不推荐 | 国内访问不稳定/被墙风险，不能保证 | — |

**建议**
- 想留在“开源平台”叙事里：**AtomGit Pages**（把 GitHub 仓库导入 AtomGit，Pages 目录选 `docs`）。
- 想最快上线 + 国内速度稳：**EdgeOne Pages**（直接上传 `deploy/docs_site.zip`，或 Git 集成）。
- Gitee 继续放代码/发行版可以，但**不要指望 Gitee Pages**。

> 参考（社区现状，非官方公告，最终以你账号 UI 为准）：
> - [LINUX DO：gitee 的 GiteePages 在哪里](https://linux.do/t/topic/1201281/13)
> - [Cocos 论坛：gitee pages 下架了](https://forum.cocos.org/t/topic/157839/7)
> - [CSDN：2025 年已没有 Gitee Pages 选项](https://wenku.csdn.net/answer/ywttssaw5n)
> - [AtomGit Pages 介绍](http://docs.openatom.tech/app/pages/)
> - [GitCode Pages 帮助](https://gitcode.net/gitcode/help-docs/-/wikis/docs/user/pages)
> - [EdgeOne Pages / Pages Drop](https://pages.edgeone.ai/zh/resources/announcing-pages-drop-free-static-website-hosting)

---

## 1. 已准备好的东西

| 文件 | 用途 |
|---|---|
| `deploy/docs_site.zip` | 纯静态站（index.html + assets + GLB + 概念图板），压缩后约 8.5 MB（解压约 15.9 MB），可直接拖到 EdgeOne Pages Drop / 上传到 AtomGit/GitCode 仓库 |
| `deploy/patch_links.py` | 一键把页面里的 GitHub 链接替换成国内仓库/Release/站点地址 |
| 仓库 `docs/` | 已包含完整站点；导入 AtomGit/GitCode 后 Pages 目录选 `docs` 即可 |

站点本身特点：
- 所有图片、3D GLB、`model-viewer` 都在本地，**不依赖外部 CDN**；
- 三个 GLB（整体 / 开盖 / 拆解）各约 2.2 MB；
- 页面用相对路径，放在 `https://host/<repo>/` 子路径也能正常工作；
- 唯一需要替换的是 GitHub 仓库/Release 链接（国内访问慢）。

---

## 2. 方案 A：AtomGit Pages（推荐给“国内开源平台”）

1. 打开 [AtomGit](https://atomgit.com/)，注册/登录并完成实名（如需）。
2. 「新建仓库」→「导入仓库」，填 GitHub 地址：
   `https://github.com/anweat/idea-05b-smart-medicine-box`
   （也可以在 AtomGit 里新建空仓库，然后把本地仓库 push 上去。）
3. 进入仓库「设置 / Pages」：
   - 分支选 `main`；
   - 目录选 `/docs`；
   - 保存并等待构建。
4. 得到类似 `https://<用户名>.atomgit.io/<仓库名>/` 的地址。
5. 在本地运行：
   ```bash
   python3 deploy/patch_links.py \
     --repo "https://atomgit.com/<用户名>/<仓库名>" \
     --release "https://atomgit.com/<用户名>/<仓库名>/releases/download/v1.0.0/IDEA-05B_delivery_20261018.zip" \
     --site "https://<用户名>.atomgit.io/<仓库名>"
   ```
   然后 commit/push；页面里的 GitHub 链接就会换成 AtomGit。
6. 把 30 MB 完整 zip 传到 AtomGit 的「发行版 / Release」，拿到国内下载直链；没有 Release 附件功能时，可放在 Gitee 发行版，页面链接指向 Gitee。

> 注意：AtomGit 的 Pages 入口/目录规则可能随版本变化；如果设置里只有“分支”没有“目录”，把站点内容放到仓库根目录（或把 `docs/` 内容复制到根）即可。

---

## 3. 方案 B：EdgeOne Pages（最快、国内速度最稳）

### 命令行部署（推荐，已验证匿名部署可用）

```bash
# 静态站 zip 已生成：deploy/docs_site.zip
npx edgeone makers deploy ./deploy/docs_site.zip \
  -n idea-05b-smart-pill-box \
  --anonymous --site china
```

- 成功后会输出 `Access URL`（带临时 token）、Project ID、Deploy ID、Claim 链接；
- 匿名项目约 1 小时内需认领，否则删除；
- 认领：`npx edgeone makers claim --sid <Sid>`（需先 `npx edgeone login --site china`）；
- 长期/CI：创建 EdgeOne API Token，`edgeone makers deploy ... -t <TOKEN>`。

### 控制台/拖拽部署

1. 登录 [EdgeOne Pages](https://pages.edgeone.ai/)（腾讯云账号 / EdgeOne 账号）。
2. 选择 **Pages Drop**（拖放部署）或 **Git 集成**：
   - Pages Drop：直接把 `deploy/docs_site.zip` 拖进去；
   - Git 集成：绑定 GitHub/GitLab/Gitee 仓库，构建目录填 `docs`，无构建命令。
3. 得到默认域名（如 `*.edgeone.app`），国内可直接访问。
4. 如需绑定自己的域名：需要 **ICP 备案**；默认域名一般不需要。
5. 同样运行 `patch_links.py`，把页面里的 GitHub 链接换成国内仓库/下载地址。

> EdgeOne 免费额度/单文件限制以控制台为准；本站最大单文件是 `board.html`（约 4.1 MB），GLB 约 2.2 MB，通常没问题。

---

## 4. 方案 C：GitCode Pages

1. 登录 [GitCode](https://gitcode.com/)，新建/导入仓库。
2. 仓库「服务 / Pages」开启，分支 `main`，目录 `docs`。
3. 默认域名形如 `https://<用户名>.gitcode.net/<仓库名>/`（以平台实际为准）。
4. 同样替换页面链接。

---

## 5. Gitee 还能怎么用

- **代码镜像**：Gitee「新建仓库 → 导入仓库」填 GitHub 地址；或本地 `git push` 到 Gitee。
- **发行版附件**：Gitee 仓库「发行版」可上传 30 MB 完整 zip，作为国内下载直链。
- **不要开 Gitee Pages**：入口已不存在；不要在这上面耗时间。

---

## 6. 链接替换

`deploy/patch_links.py` 会把以下内容替换：

- `https://github.com/anweat/idea-05b-smart-medicine-box`
- `https://github.com/anweat/idea-05b-smart-medicine-box/releases/download/v1.0.0/IDEA-05B_delivery_20261018.zip`
- `https://anweat.github.io/idea-05b-smart-medicine-box`
- 导航里的“GitHub”字样 → “代码仓库”

用法：

```bash
python3 deploy/patch_links.py \
  --repo "https://gitee.com/<user>/<repo>" \
  --release "https://gitee.com/<user>/<repo>/releases/download/v1.0.0/IDEA-05B_delivery_20261018.zip" \
  --site "https://<user>.atomgit.io/<repo>"
```

替换后重新打包 `deploy/docs_site.zip`（或直接 push 仓库）即可。

---

## 7. 需要我继续做什么

- 你只要在 **AtomGit / GitCode / EdgeOne** 任意一个平台登录，并给我：
  - 平台名 + 仓库地址（或空仓库地址），以及一个可推送的 **Personal Access Token**；或
  - EdgeOne Pages 的 **API Token**；
- 我就可以直接把 `docs/` 推上去、开 Pages、替换链接、验证国内访问。
- 如果不想给 token：用 `deploy/docs_site.zip` 拖到 EdgeOne Pages Drop，2 分钟也能上线；我可以远程指导。
