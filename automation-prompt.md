# 自动化 Prompt

每天搜索小红书等网络渠道上的青少年 AI 赛事相关资料，重点关注赛事名称、适合年级/年龄、奖项设置、比赛内容或可展示成果。整理为 `赛事 / 年级 / 奖项 / 比赛内容或成果` 的表格，并注明主要信息来源；如发现新增赛事、赛程变化、报名截止或奖项变化，优先提示变化。

这是一个独立 cron 自动化任务，不要把结果写回旧的“查找 OpenCLI”对话。每次运行都应视为一个新的独立对话/任务，并在本项目目录中归档日报。

## 先读普通本地进程生成的 OpenCLI 缓存

每天正式检索前，先读取本项目的 OpenCLI 预抓取缓存：

- Markdown 摘要：`/Users/sophienie/Documents/Codex/2026-05-27/youth-ai-competitions-daily/opencli-cache/latest.md`
- JSON 清单：`/Users/sophienie/Documents/Codex/2026-05-27/youth-ai-competitions-daily/opencli-cache/latest.json`

这组文件由普通本地 launchd 进程在自动化运行前生成，不依赖 Codex 自动化沙箱访问本机 daemon。如果缓存日期是当天，且其中有成功且非空记录，应先读取这些记录指向的原始 JSON 文件，把这些结果作为当天小红书/公众号等登录态或站点适配器资料来源。然后再用公开网页检索补充官网、新闻稿、报名页和新变化。

如果缓存日期是当天，且至少有一条成功且非空记录，本轮不要再在自动化沙箱内运行 `opencli doctor`、`daemon restart`、`curl http://127.0.0.1:19825/status` 或任何 `opencli search` 探测命令；直接使用缓存结果，再补公开网页检索。这样可以避免把已知的自动化沙箱 localhost 限制重复写成当日问题。

只有缓存缺失、过期或全部失败时，才按下方 OpenCLI 预检逻辑尝试直接调用；若直接调用仍失败，才降级到公开网页检索。即使自动化沙箱内直接调用失败，也不要丢弃当天已生成的 `opencli-cache` 成功结果。

必须参考小越越项目 `/Users/sophienie/Documents/Codex/2026-05-16/codex-openclaw-weixin` 和自动化任务 `上海青少年AI教育情报` 的实现方法：
- 在自动化里不要给微信发送 `/opencli ...` 前缀；`/opencli` 是微信直通命令。
- 自动化运行时应通过 shell 直接调用 OpenCLI 二进制。
- 优先 OpenCLI 路径：`/Users/sophienie/Library/Application Support/CodexWeixinBridge/node_modules/.bin/opencli`
- 回退 OpenCLI 路径：`/Users/sophienie/Documents/Codex/2026-05-16/https-mp-weixin-qq-com-s/tools/node/bin/node /Users/sophienie/Documents/Codex/2026-05-16/https-mp-weixin-qq-com-s/tools/opencli-global/lib/node_modules/@jackwener/opencli/dist/src/main.js`

先串行做 OpenCLI 预检和恢复，不要把第一批 OpenCLI 命令并行启动：

```bash
OPENCLI="/Users/sophienie/Library/Application Support/CodexWeixinBridge/node_modules/.bin/opencli"
"$OPENCLI" daemon status || true
"$OPENCLI" doctor || {
  "$OPENCLI" daemon restart || true
  sleep 3
  "$OPENCLI" doctor
}
```

如果 doctor 仍显示 daemon、Chrome extension 或 profile 未连接，再检查 `lsof -nP -iTCP:19825 -sTCP:LISTEN` 和 `curl -sS -H 'X-OpenCLI: 1' http://127.0.0.1:19825/status`，区分是 daemon 真没启动、扩展没连上，还是自动化运行环境临时无法访问本机 daemon。只有确认仍不可用时，日报中才按 OpenCLI 渠道失败处理，并只把普通网页搜索作为补充；不要假装小红书/登录态数据已获取。`Could not create symlink ...` 这类 OpenCLI 用户目录 shim 警告通常不是失败根因，除非后续 doctor/search 同时失败。

如果 `lsof` 能看到 `127.0.0.1:19825` 有 `node` 监听，但自动化环境里的 `curl`、`doctor` 或 `search` 仍失败，应优先表述为“当前自动化沙箱无法访问本机 OpenCLI daemon”，不要写成“OpenCLI 安装损坏”“小红书登录态失效”或“Chrome 扩展未安装”。这种情况下不要反复重启 daemon；直接降级检索，并在渠道说明中标注这是自动化运行环境限制，后续可由普通本地线程补抓登录态结果。

检索命令配方：
1. 小红书：对关键词运行 `$OPENCLI xiaohongshu search "关键词" --limit 20 --window background -f json`。查小红书必须用 `xiaohongshu`，不要用 `rednote`。对高相关、高互动或新赛程线索，再运行 `$OPENCLI xiaohongshu note "笔记URL" --window background -f json` 抽取正文。
2. 微信公众号/公开微信文章：运行 `$OPENCLI weixin search "关键词" --limit 10 --window background -f json`；对高相关文章再运行 `$OPENCLI weixin download --url "文章URL" --window background -f json`。
3. 官网/报名页/新闻稿：优先使用 OpenCLI 站点适配器；没有专用适配器时用 `$OPENCLI web read --url "页面URL" --stdout true --window background -f md` 或普通网页搜索补充，并注明来源。

每日关键词建议：
- `青少年 AI 竞赛 2026`
- `青少年 人工智能 比赛 报名`
- `全国青少年人工智能创新挑战赛 2026`
- `WAICY 2026 青少年 人工智能`
- `AIGCNYACC 青少年 人工智能 数字艺术`
- `WAIC YOUNG 青少年 AI 奥林匹克`
- `天枢杯 青少年 人工智能 安全`
- `智创杯 人工智能 创新大赛`
- `中小学生 AI 比赛`
- `AI 黑客松 青少年`
- `青少年 AI 小程序 比赛`
- `IOAI 人工智能 奥林匹克 高中`

重点跟踪赛事：
- 全国青少年人工智能创新挑战赛
- WAICY 世界青少年人工智能竞赛
- AIGCNYACC 全国青少年人工智能辅助生成数字艺术创作者大赛
- WAIC YOUNG 长三角青少年人工智能奥林匹克挑战赛
- 天枢杯青少年人工智能安全创新大赛
- 智创杯全国人工智能+创新大赛
- 数字中国创新大赛青少年 AI 机器人赛道
- IOAI/APOAI 人工智能奥林匹克
- AIEC AI Entrepreneurship Contest
- Microsoft Imagine Cup Junior
- 其他当天出现的新赛事或区域性中小学 AI 活动

日报格式：
- 标题包含日期：`青少年AI赛事资料更新 YYYY-MM-DD`
- 先给 `今日变化提醒`，列出 3-5 条最重要变化，尤其是报名截止、赛程变化、新增赛事、奖项变化。
- 然后给主表：`赛事 / 年级 / 奖项 / 比赛内容或成果 / 主要来源`
- 再给 `小红书新增线索`，保留笔记标题、作者、发布时间、互动量和可搜索关键词。
- 最后给 `渠道覆盖与失败说明`，说明 OpenCLI、小红书、公众号、官网检索是否成功。

归档要求：
- 将最终日报正文保存到本项目 `reports/youth-ai-competitions-YYYY-MM-DD.md`。
- 可同步更新 `reports/latest.md` 为当天最新版本。

网页发布要求：
- 完成日报正文后，不再通过微信发送整篇日报。
- 必须运行 `python3 scripts/generate_daily_site.py` 生成并刷新本项目网页日报站。
- 站点校验通过后，必须把当天 Markdown 与网页产物提交并推送到 GitHub `main`，让 GitHub Pages 自动更新公网网站。
- 站点至少要更新以下产物：
  - `index.html`
  - `daily/YYYY-MM-DD.html`
  - `site-data/reports.json`
  - `assets/site.css`
  - `assets/site.js`

发布校验要求：
1. `index.html` 已更新；
2. 当天 `daily/YYYY-MM-DD.html` 已生成；
3. `site-data/reports.json` 已更新；
4. 首页能看到当天摘要、趋势区块和历史归档入口；
5. `git status --short` 能看到当天应发布的变更，或确认当天无新增内容；
6. 如有变更，执行 `git add reports/youth-ai-competitions-YYYY-MM-DD.md reports/latest.md index.html daily/YYYY-MM-DD.html site-data/reports.json assets/site.css assets/site.js automation-prompt.md README.md .github/workflows/pages.yml docs/github-pages.md scripts/generate_daily_site.py tests/test_generate_daily_site.py`；
7. 提交：`git commit -m "chore: publish daily report YYYY-MM-DD"`；
8. 推送：`git push origin main`。
9. 如果 push 失败且错误明确属于暂时性网络/DNS/连接问题，例如 `Could not resolve host`、`Failed to connect`、`Connection timed out`、`Operation timed out`、`EAI_AGAIN`、`ENOTFOUND`、`ECONNRESET`、`ETIMEDOUT`、`TLS handshake`、`HTTP 5xx`，等待 `90` 秒后重试 `git push origin main`，最多重试 `2` 次。重试必须使用同一个已生成、已提交的版本，不要重新生成日报、不要创建重复提交、不要改动提交内容。
10. 如果重试后仍失败，或首次失败属于 GitHub 凭证、workflow scope、远端权限、non-fast-forward 等非暂时网络类问题，不要继续重试，不要说网站已更新；只能说“本地日报和网页已生成并提交，GitHub Pages 发布被推送失败阻塞”，并给出失败命令与错误摘要。
