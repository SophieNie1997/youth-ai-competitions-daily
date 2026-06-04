# 青少年AI赛事日报网页发布设计

## 背景

当前项目 `每日青少年AI赛事资料更新` 以 Markdown 日报为主产物，落盘到 `reports/youth-ai-competitions-YYYY-MM-DD.md` 与 `reports/latest.md`。原自动化还要求把整篇日报通过微信发送，但现在目标已经切换为：

1. 完全改成网页发布；
2. 停止微信整篇发送；
3. 参考 `上海青少年AI教育情报` 项目，接入 GitHub Pages 自动发布。

本项目的新远端仓库已确定为：

- `https://github.com/SophieNie1997/youth-ai-competitions-daily.git`

## 目标

把当前项目升级为一个独立的静态日报站点，使每天自动化运行后能够：

1. 继续产出 Markdown 日报；
2. 从 Markdown 日报生成网页站点；
3. 生成首页、每日报详情页、JSON 归档索引和共享样式资源；
4. 用 GitHub Actions 自动部署到 GitHub Pages；
5. 将“网页发布成功”替代“微信整篇发送成功”作为自动化完成条件。

## 非目标

这次改造不做以下内容：

1. 不把赛事站并入 `上海青少年AI教育情报` 站点；
2. 不新增数据库、服务端或 CMS；
3. 不在首版加入复杂筛选、全文搜索、截止日倒计时组件；
4. 不保留微信整篇发送作为主交付链路。

## 推荐方案

采用与 `上海青少年AI教育情报` 相同的静态站发布模式，但按赛事日报字段做内容适配。

整体链路：

`reports/*.md` -> `scripts/generate_daily_site.py` -> `index.html` + `daily/*.html` + `site-data/reports.json` + `assets/*` -> GitHub Actions -> GitHub Pages

这是最稳的方案，因为：

1. 当前日报已经结构化，字段稳定；
2. 静态站适合 GitHub Pages，部署成本最低；
3. 自动化只需要在现有“生成 Markdown”之后增加“生成网页并推送”步骤；
4. 后续如果要做赛事筛选或截止提醒，也能在这套静态站上渐进增强。

## 信息架构

### 首页 `index.html`

首页需要承担三个职责：

1. 展示最新一篇日报的核心变化；
2. 横向汇总最近几天最值得关注的趋势；
3. 提供历史归档入口。

首页结构：

1. Hero
   - 标题：`青少年AI赛事资料更新`
   - 副标题：说明这是面向家长/学校/教育从业者的持续赛事情报站
2. 最新日报卡片
   - 显示当天日期
   - 抽取 `今日变化提醒` 前几条作为首页摘要
   - 链接到 `daily/YYYY-MM-DD.html`
3. 趋势/判断区块
   - 汇总最近几篇日报中的高优先级变化
   - 重点展示：新增赛事、报名截止、赛程变化、奖项变化
4. 历史归档区
   - 列出所有日报日期
   - 每项显示一条 headline 和一条 summary
   - 可点击进入详情页

### 每日报详情页 `daily/YYYY-MM-DD.html`

详情页完整保留日报核心结构，按赛事项目阅读习惯组织内容：

1. 页面标题
   - `青少年AI赛事资料更新 YYYY-MM-DD`
2. 目录导航
   - 今日变化提醒
   - 主表
   - 小红书新增线索
   - 渠道覆盖与失败说明
3. 正文区
   - 原样保留主要章节
   - 保留原始来源链接
4. 页脚导航
   - 返回首页
   - 前一天/后一天日报跳转（如果存在）

## Markdown 解析设计

赛事项目与上海项目不同，当前日报的稳定章节是：

1. `今日变化提醒`
2. `主表`
3. `小红书新增线索`
4. `渠道覆盖与失败说明`

生成器需要优先支持这组章节标题，并兼容 Markdown 标题格式：

1. 纯文本标题
2. `#` / `##` 标题

解析规则：

1. 从首行抽取标题和日期；
2. 用已知章节标题切分正文；
3. 从 `今日变化提醒` 中提取 bullet，作为：
   - 首页摘要
   - 趋势卡片来源
   - 历史归档 headline/summary 来源
4. `主表` 区块保留原 Markdown 表格，并在详情页转为 HTML table；
5. 其他章节按段落、列表和链接转为可读 HTML。

如果某天缺少 `今日变化提醒`，生成器应报错而不是静默发布，因为首页摘要依赖这部分内容。

## 文件结构

本次改造后，项目会新增或修改以下关键文件。

### 新增

- `scripts/generate_daily_site.py`
- `tests/test_generate_daily_site.py`
- `.github/workflows/pages.yml`
- `docs/github-pages.md`
- `docs/superpowers/specs/2026-06-04-youth-ai-competitions-daily-web-design.md`

### 生成产物

- `index.html`
- `daily/YYYY-MM-DD.html`
- `site-data/reports.json`
- `assets/site.css`
- `assets/site.js`

### 修改

- `automation-prompt.md`
- `README.md`

## 页面视觉方向

视觉方向继续沿用上海项目的“克制、偏苹果官网、暖灰玻璃感”的基调，不做后台仪表盘风格。

但文案语义要改成赛事场景：

1. 首页标题改为赛事情报站；
2. 趋势区块更强调“赛程变化 / 截止临近 / 新增赛事”；
3. 不使用“机构转型”“课程观察”这类上海项目专用词；
4. 主表和赛事线索需要明显可扫读。

首版可以沿用同一套 CSS 结构，再做轻量文案和局部样式调整，不需要重做视觉系统。

## JSON 数据设计

`site-data/reports.json` 作为轻量归档索引，首页和后续扩展都依赖它。

每条记录至少包含：

1. `date`
2. `title`
3. `archiveHeadline`
4. `archiveSummary`
5. `summaryBullets`
6. `detailPath`

首版不加入更多结构化赛事字段，因为这些字段目前还只在 Markdown 表格里，直接从表格做稳定抽取会增加风险。后续如果要做赛事筛选，再单独设计结构化 schema。

## 自动化流程改造

`automation-prompt.md` 需要做三类修改。

### 1. 归档要求升级为网页发布

在日报生成后，自动化必须继续执行：

1. 更新 `reports/latest.md`
2. 运行 `python3 scripts/generate_daily_site.py`
3. 校验生成产物
4. 把 Markdown、网页产物和相关配置提交并推送到 GitHub `main`

### 2. 停止微信整篇发送

删除或显式废弃：

1. “通过小越越发送一次”的要求
2. 所有重试发送逻辑
3. 把微信送达当成完成条件的表述

保留历史说明即可，但新流程中不再执行微信整篇发送。

### 3. 明确 GitHub 发布要求

自动化完成前至少校验：

1. `index.html` 已更新
2. 当天 `daily/YYYY-MM-DD.html` 已生成
3. `site-data/reports.json` 已更新
4. `git status --short` 显示正确的待发布文件
5. `git push origin main` 成功

如果 push 失败，只能汇报“本地日报和网页已生成，GitHub Pages 发布被推送失败阻塞”，不能声称网站已更新。

## Git 与仓库接入

当前目录还不是 Git 仓库。为了完成 GitHub Pages 发布，本项目需要补齐：

1. `git init`
2. `git branch -M main`
3. `git remote add origin https://github.com/SophieNie1997/youth-ai-competitions-daily.git`

之后每日自动化按常规 `add/commit/push` 执行。

## 测试与校验

首版至少需要以下测试：

1. `parse_report` 能从赛事日报抽取日期、标题、`今日变化提醒` 和章节；
2. 支持无 Markdown 标题和有 Markdown 标题两种格式；
3. `build_site` 能生成：
   - `index.html`
   - `daily/YYYY-MM-DD.html`
   - `site-data/reports.json`
   - `assets/site.css`
4. CLI 运行 `python3 scripts/generate_daily_site.py` 能在当前项目根目录成功构建站点；
5. 生成后的首页包含当天摘要与归档入口。

本地验收命令：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_daily_site.py
```

## 风险与处理

### 风险 1：赛事日报章节较少

上海项目的站点生成器默认章节更多，赛事项目只有 4 个核心章节。处理方式是：

1. 改成以赛事章节集为准；
2. 不强行兼容上海项目的全部展示区块。

### 风险 2：当前项目不是 Git 仓库

没有 Git 就无法完成 push 和 Pages 发布。处理方式是：

1. 在实施阶段补 `git init`
2. 接入远端仓库
3. 再落 GitHub Actions

### 风险 3：日报表格格式未来变化

如果 `主表` 的 Markdown 表格列数变化，详情页的表格渲染可能受影响。处理方式是：

1. 首版支持标准 Markdown 表格；
2. 保留原始文本回退渲染；
3. 后续再考虑更强的表格解析。

## 实施边界

这次实施完成的标准是：

1. 当前项目本地可生成独立静态站；
2. 自动化 prompt 改成网页发布流程；
3. 仓库可推到 `SophieNie1997/youth-ai-competitions-daily`；
4. GitHub Actions 可自动部署 Pages；
5. 不再依赖微信整篇发送。

不要求本次就完成：

1. 高级筛选器
2. 赛事搜索
3. 截止日期自动解析器
4. 自定义域名

## 结论

本项目最合适的实现方式，是复用 `上海青少年AI教育情报` 的静态站发布链，改造成赛事场景专用版本。这样可以在最短路径内实现：

1. 日报继续以 Markdown 为事实源；
2. 网页站作为唯一正式发布渠道；
3. GitHub Pages 作为稳定公网交付面；
4. 后续再逐步演进为更强的赛事归档与筛选站点。
