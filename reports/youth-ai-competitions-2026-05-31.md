# 青少年AI赛事资料更新 2026-05-31

## 今日变化提醒

- `OpenCLI 渠道仍未恢复`：`2026-05-31` 串行复测主路径与回退路径 `doctor`，两者都返回 `Daemon: not running`、`Extension: not connected`、`Connectivity: failed (Failed to start opencli daemon)`；但 `lsof -nP -iTCP:19825 -sTCP:LISTEN` 同时看到本机已有 `node` 在监听 `127.0.0.1:19825`，而同一环境下 `curl http://127.0.0.1:19825/status` 仍报无法连接，说明今天更像是自动化运行环境到本机 daemon 的访问异常，而不只是“没启动”。
- `IOAI 2026`：截至 `2026-05-31`，官网已明确挂出 [Registration](https://ioai-official.org/registration-2026/) 页面并写明 `Registration for IOAI 2026 is open!`，相较前几天只看到赛程与规则入口，现阶段已进入代表队实际报名窗口。
- `AIGCNYACC`：官网时间轴仍显示 `2026-05-22` 至 `2026-06-20` 为省赛作品提交期，距离当前日期只剩 `20` 天，且仍要求提交手绘草稿与不少于 `3` 张 AIGC 过程截图，临近省赛截止。
- `WAICY 2026`：截至 `2026-05-31`，首页仍写 “Be the first to know when WAICY 2026 registration opens”，但独立 [注册页](https://www.waicy.org/waicy-2026-registration/) 仍可填写 `Grade / Country / Track` 等字段，首页与注册页状态继续冲突，报名前需人工确认。
- `新增赛事线索`：公开网页检索到 [IAI²O International AI Innovation Olympiad](https://iai2o-official.org/) 官方站已写明 `2026 National Preliminary Round Applications Are Open`，亚洲区报名截止 `2026-06-07`、提交截止 `2026-06-20`，可作为今年新出现的国际青少年 AI 竞赛补充跟踪。

## 主表

| 赛事 | 年级 | 奖项 | 比赛内容或成果 | 主要来源 |
| --- | --- | --- | --- | --- |
| 全国青少年人工智能创新挑战赛（第九届） | 小学、初中、高中/中职 | 页面正文写决赛后 `10` 个工作日内公布成绩并发放国家级获奖证书；正文仍提到金、银、铜奖及优秀指导教师奖 | 个人或 `3` 人内团队参赛；方向含智能机器人应用、AI 场景设计、开源硬件/芯片、数字化仿真；含作品提交、现场竞技、成果展示、答辩评审；但报名时间仍存在正文 `2月20日-4月15日` 与页面顶部 `至 2026-07-15 16:52` 的冲突 | [赛事页](https://ssbook.cn/event.php?cid=-1&shid=176786236081409) |
| WAICY 2026 世界青少年人工智能竞赛 | `6-18` 岁 | `2026` 页未公开奖项名额；可参考 `2025` 全球赛已有 `Gold / Silver / Bronze / AI Excellence / Impact Excellence / Design Excellence` 等结构 | 赛道包括 `AI Showcase`、`AI Generated Art`、`AI Large Language Model`；支持个人或团队、全球远程参与；首页仍写“报名未开”，但独立注册页仍开放表单字段 | [WAICY 2026](https://www.waicy.org/waicy-2026/), [注册页](https://www.waicy.org/waicy-2026-registration/), [WAICY 2025 奖项结构](https://www.waicy.org/waicy-2025/) |
| AIGCNYACC 全国青少年人工智能辅助生成数字艺术创作者大赛 | 小学、初中、高中、中职 | 省赛一等奖 `5%` / 二等奖 `10%` / 三等奖 `15%` / 优胜奖 `20%`；国赛一等奖 `5%`，另设最佳创意、最佳技术应用、最佳文化传承等专项奖 | 覆盖 `15` 个赛项，方向含 AI+图像、影像、音频、文本、非遗；需提交作品、创作草稿、`>=3` 张 AIGC 过程截图；当前仍处于 `2026-05-22` 至 `2026-06-20` 省赛作品提交期，`2026-07-01` 至 `2026-08-15` 为国赛提交期 | [官网时间轴](https://www.aigcnyacc.com/), [关于大赛](https://www.aigcnyacc.com/www/about.html?id=about), [参赛技术规范](https://www.aigcnyacc.com/www/signUpDetails.html?id=signUp) |
| WAIC YOUNG 长三角青少年人工智能奥林匹克挑战赛（第六届） | 长三角小学、初中、高中/中职 | 当前公开稿可核验到 `AI 自画像` 评一、二、三等奖；既有 `网安守护者` 赛题公开过一等奖 `10%`、二等奖 `20%`、三等奖 `40%` | 公开稿确认本届已启动，并重点提到 `AIGC音乐创作`、`机器狗越障` 等项目；成果形式覆盖音乐/图像创作、机器人闯关、现场展示 | [启动稿](https://info.datadowell.com/rgzn/0-1778040263462.html), [WAIC 官网入口](https://www.worldaic.com.cn/en) |
| 天枢杯青少年人工智能安全创新大赛 2026 | `18` 岁及以下小学、初中、高中、中职 | 各组别设特等奖、一等奖、二等奖、三等奖、单项奖；特等奖另含奖金 `2000` 元（税前）与线下展示 | 分 `AI 创作赛道` 与 `AI 安全赛道`；创作赛道含 AIGC 海报、AI 安全创想家等方向，安全赛道含线下比赛+答辩；官网赛程显示已完成 `5月中旬` 决赛，颁奖典礼在 `6月初` | [官网](https://www.tianshucup.com/), [参赛指南 PDF](https://oss-static.tianshucup.com/topic/86c6cbb626c6485889c20a4622909e38.pdf) |
| 智创杯全国人工智能+创新大赛（第二届） | 小学、初中、高中、职业院校、本科、研究生 | 一等奖 `90-100` 分、二等奖 `80-89` 分、三等奖 `60-79` 分；一二等奖可申领 AI 礼品 | 三赛道：创意设计、算法应用、实践操作；官网仍写比赛时间 `2026-03-01` 至 `2027-01-15`，报名截止 `2027-01-30 23:59:59`；实践操作赛道要求指定 AI 项目开发并现场演示答辩 | [官网](https://rgzn.aisaihk.com/) |
| 数字中国创新大赛青少年 AI 机器人赛道 2026 | 小学至中职 | 首页仍强调设实体与虚拟仿真机器人赛项；奖项细则本次未在首页直接展开，过往公开稿包含一、二、三等奖及优秀指导教师/学校奖 | 主题为“新质产·数智芯·少年志”，聚焦实体与虚拟仿真机器人赛项，覆盖小学至中职全学段，强调创新思维、跨学科应用、团队协作与科学家精神 | [大赛官网](https://www.dcic-china.com/), [福州市数据管理局参赛指南](https://sjglj.fuzhou.gov.cn/zwgk/gzdt/202603/t20260331_5303011.htm) |
| APOAI 2026 亚太人工智能奥林匹克 | 中学生/高中生 | 奖牌分配按个人赛成绩确定，官网摘要未公开奖牌比例 | `2026-06-13` 由中国主办，采用分布式混合形式；比赛为 `6` 小时同步个人赛，`4` 道 AI 任务，最多每个国家/地区 `8` 名正式选手 | [APOAI 2026](https://www.apoai.org/apoai2026), [Competition Regulations](https://www.apoai.org/apoai2026competitionregulations) |
| IOAI 2026 国际人工智能奥林匹克 | 高中生为主 | 官网已开放注册，但首页未直接列奖牌比例；已有 `Contest Rules` 与 `Financial Aid 2026` 入口 | 第三届 IOAI 将于 `2026-08-02` 至 `2026-08-08` 在哈萨克斯坦阿斯塔纳举办；官网已明确 `Registration for IOAI 2026 is open!`，并持续更新 `2026 Kazakhstan` 专区 | [IOAI 官网](https://ioai-official.org/), [Registration 2026](https://ioai-official.org/registration-2026/) |
| AIEC AI Entrepreneurship Contest 2026 | `Grade 6-12`，团队为主 | 总奖为 `1st / 2nd / 3rd Place`；另设 `AI Innovation`、`Business Potential`、`Social Impact in AI`、`UX & Design Excellence`、`Rising AI Entrepreneurs`、`Team Excellence` 等专项奖 | 围绕 AI 创业项目，需提交摘要/提案、原型证据、市场验证数据、AI 技术说明；半决赛 `2026-05-09` 已结束，线下总决赛与 `AI Showcase` 定于 `2026-06-13` 在多伦多地区举行 | [赛事主页](https://aiec-youth.org/contest/), [资源页](https://aiec-youth.org/resources/) |
| Microsoft Imagine Cup Junior | 最近可核验公开页为 `5-18` 岁；其中 `AI for Good` 为 `13-18` 岁、`Tech for Good` 为 `5-12` 岁 | 最近明确可核验的官方页仍显示全球优胜团队可获奖杯与奖品 | 典型交付为 `PowerPoint + 视频`，偏 AI/Tech for Good 创意表达，不要求正式编码；截至 `2026-05-31`，微软官方公开检索结果里仍以 `2024` Imagine Cup Junior 页面为最新明确赛页，未见独立 `2026` Junior 规则页 | [微软教育博客 2024 启动页](https://www.microsoft.com/en-us/education/blog/?p=2227), [2024 获奖页](https://www.microsoft.com/en-us/education/blog/2024/06/congratulations-to-the-imagine-cup-junior-2024-winners/) |
| IAI²O International AI Innovation Olympiad（新增跟踪） | 官方站表述为 `teenagers` | 官网当前重点公开报名与赛程，未见详细奖项比例；结果公告节点已公布 | `2026 National Preliminary Round Applications Are Open`；亚洲区报名截止 `2026-06-07`、提交截止 `2026-06-20`、结果公布 `2026-06-30`；赛道含 `AIIC`、`AI4SCI`、`AI4BIZ`，全球总决赛拟于 `2026-09-14` 至 `2026-09-17` 在 MIT 举办 | [官方主页](https://iai2o-official.org/) |
| 首届中学生人形机器人足球赛（北京海淀，区域活动） | 中学生 | 公开报道未列全量奖项细则；优胜队伍可参与 `2026` 世界人形机器人运动会相关项目 | `2026-05-23` 至 `2026-05-24` 在北京海淀举行总决赛；强调机器人 `AI 自主决策`、无人工遥控，适合作为具身智能方向校队/区域选拔活动跟踪 | [央视报道](https://news.cctv.com/2026/05/24/ARTIwh2AzTZDmFQtGxd7OYl7260524.shtml), [北京市政府信息](https://www.beijing.gov.cn/fuwu/bmfw/sy/jrts/202605/t20260507_4639801.html) |

## 小红书新增线索

- 今日无通过 OpenCLI 站内检索成功获取、且可完整核验的新增小红书笔记。
- 实测命令 `opencli xiaohongshu search "全国青少年人工智能创新挑战赛 2026" --limit 5 --window background -f json` 返回 `BROWSER_CONNECT`，错误信息为 `Failed to start opencli daemon`。
- 在 OpenCLI 未恢复前，今天不把搜索引擎抓到的零散小红书落地页伪装成“小红书站内新增线索”。
- 明日恢复后优先复测关键词：`全国青少年人工智能创新挑战赛 2026`、`WAICY 2026 青少年 人工智能`、`AIGCNYACC 青少年 人工智能 数字艺术`、`IAI2O AI Olympiad`。

## 渠道覆盖与失败说明

- `OpenCLI doctor`：主路径与回退路径在 `2026-05-31` 实测均返回 `Daemon: not running`、`Extension: not connected`、`Connectivity: failed (Failed to start opencli daemon)`；回退路径同时继续出现 `Could not create symlink ... EPERM` 警告。
- `本机 daemon 探针`：`lsof -nP -iTCP:19825 -sTCP:LISTEN` 可见 `node` 监听 `127.0.0.1:19825`，但同一环境下 `curl -sS -H 'X-OpenCLI: 1' http://127.0.0.1:19825/status` 失败，说明自动化运行环境到本机 daemon 的访问本身也存在问题。
- `OpenCLI xiaohongshu search`：实测关键词 `全国青少年人工智能创新挑战赛 2026` 失败，错误码 `BROWSER_CONNECT`。
- `OpenCLI weixin search`：同一关键词在带超时复测时表现为长时间挂起，未能在限定时间内返回正文结果；因此今天仍没有登录态公众号检索结果。
- `降级检索`：今天主表主要依赖赛事官网、官方 PDF、官方报名页、政府/主办方公开稿与可直接访问的公开新闻；涉及 `WAIC YOUNG`、`Imagine Cup Junior` 等缺少统一当年规则页的项目，已明确标注为媒体转载或历史官方页。
- `风险提示`：`全国青少年人工智能创新挑战赛` 报名时间口径冲突、`WAICY 2026` 首页与注册页状态冲突、`Microsoft Imagine Cup Junior` 暂未检索到独立 `2026` Junior 官方赛页，这三项都不建议只凭单一传播稿做报名判断。
