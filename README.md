# AI 晨报仪表盘 · AI HOT Daily Dashboard

一个**零依赖、单文件**的 AI 资讯晨报仪表盘。每天基于 [AI HOT](https://aihot.news) 的公开日报 API 拉取数据，渲染成一份可在浏览器直接打开的响应式 HTML 看板。

> 数据来源：[AI HOT](https://aihot.news)（公开、匿名、只读 API）。第三方原文版权归原作者所有，本仓库仅做聚合展示与格式化呈现。

## 特性

- **五个固定版块**：模型发布/更新、产品发布/更新、行业动态、论文研究、技巧与观点。
- **全局连续编号**：跨版块统一计数，不在版块内重新计数。
- **Hero 概览 + 锚点导航**：顶部展示日报日期、总条数与五版块统计；中部提供一键跳转锚点。
- **响应式卡片网格**：`auto-fill` 自适应列数，手机 / 平板 / 桌面均友好。
- **每张卡片包含**：连续序号、标题（链 AI HOT 中文阅读页）、来源 chip、≤60 字中文摘要、原文外链（`target="_blank" rel="noopener noreferrer"`）。
- **北京时间人话格式**：所有时间由脚本预转为 `Asia/Shanghai` 人话格式，文件内不保留任何 ISO 时间戳。
- **纯单文件**：HTML / CSS / JS 全部内联，无任何外部资源（CDN、字体、图片均不依赖）。

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | **最终产物 / 部署入口**：可直接双击打开，也是 GitHub Pages 的服务入口。 |
| `build_dashboard.py` | 生成脚本：拉取 AI HOT 日报、映射到五版块、截断摘要、输出单文件 HTML。 |
| `dailies_latest.json` | 当日原始日报数据快照（用于离线复现，非必需）。 |

## 本地重新生成

```bash
# 1. 拉取当日日报（若当日尚未生成，按 AI HOT 契约回退到最近一期）
curl -sS "https://aihot.virxact.com/api/v1/dailies/latest" -o dailies_latest.json

# 2. 生成单文件 HTML 仪表盘
python3 build_dashboard.py

# 3. 打开产物
open index.html   # Windows 可用 start index.html
```

> 说明：AI HOT 日报接口对「当日日报不存在」的约定处理为——返回 404 时查询有界的
> `/api/v1/dailies?limit=7` 索引，取其中实际返回的最近日期再请求完整日报，绝不自行拼接日期。

## 版块映射

日报接口已按 `模型发布/更新 / 产品发布/更新 / 行业动态 / 论文研究 / 技巧与观点` 组织
`sections`。本仪表盘以这五个标签为**固定版块**，按固定顺序展示；若某版块当日无内容，
则显示优雅的空态提示，版块结构不被破坏。日报的 `lead`（头条）会与「论文研究」首条去重，
仅在对应版块内以「今日头条」徽标强调一次。

## 部署

`index.html` 是纯静态单文件，可直接：

- 双击用浏览器打开；
- 拖入任意静态托管（GitHub Pages、Vercel、Netlify、Cloudflare Pages 等）；
- 用 WorkBuddy 的 CloudStudio 部署。

### GitHub Pages（本仓库已启用）

本仓库已开启 GitHub Pages，从 `main` 分支根目录直接提供 `index.html`：

- 线上地址：`https://gatsby666-jay.github.io/ai-hot-daily-dashboard/`
- 如需重新生成并发布：本地跑 `python3 build_dashboard.py` 后，`git add index.html && git commit && git push` 即可，Pages 会自动重新构建。

> 修改入口文件或分支后，可在仓库 **Settings → Pages** 中调整来源（Source）。


## 免责声明

- 本仓库为个人/学习用途的资讯聚合展示，不构成投资建议。
- 数据版权与原始表述归 AI HOT 及各原始发布方所有；引用具体数字、政策或原话请以第三方原文为准。
- AI HOT 的使用边界与再分发条款见 <https://aihot.virxact.com/terms>。

## License

代码以 MIT 许可证开源；数据归属见上方「数据来源」与「免责声明」。
