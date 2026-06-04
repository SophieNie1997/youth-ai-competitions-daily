# 每日青少年AI赛事资料更新

这个目录是 `每日青少年AI赛事资料更新` 自动化任务的独立项目工作区。

目标：
- 每天搜索小红书等渠道上的青少年 AI 赛事资料。
- 整理为 `赛事 / 年级 / 奖项 / 比赛内容或成果 / 主要来源` 表格。
- 优先提示新增赛事、赛程变化、报名截止和奖项变化。
- 将最终日报发布到静态网页，并通过 GitHub Pages 对外更新。

运行方式：
- 自动化类型为 Codex cron，不再绑定旧对话。
- 每次运行作为独立任务处理。
- 每日结果保存到 `reports/`，并由 `scripts/generate_daily_site.py` 生成站点。

关键外部依赖：
- OpenCLI: `/Users/sophienie/Library/Application Support/CodexWeixinBridge/node_modules/.bin/opencli`
- GitHub 仓库：`https://github.com/SophieNie1997/youth-ai-competitions-daily.git`
