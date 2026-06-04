# Youth AI Competitions Daily Web Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static website and GitHub Pages publishing flow for the youth AI competitions daily reports, replacing WeChat full-report delivery with web publishing.

**Architecture:** The project will keep Markdown reports in `reports/` as the source of truth. A Python generator will parse those reports, render a static homepage plus per-day detail pages, emit a JSON archive index and shared assets, and a GitHub Actions workflow will test and deploy the generated site to GitHub Pages from `main`.

**Tech Stack:** Python 3 standard library, `unittest`, static HTML/CSS/JS, GitHub Actions Pages.

---

### Task 1: Create the project scaffolding for site generation

**Files:**
- Create: `scripts/generate_daily_site.py`
- Create: `tests/test_generate_daily_site.py`
- Create: `.github/workflows/pages.yml`
- Create: `docs/github-pages.md`
- Modify: `README.md`

- [ ] **Step 1: Create the missing project directories**

Run:

```bash
mkdir -p scripts tests .github/workflows docs
```

Expected: the directories `scripts`, `tests`, `.github/workflows`, and `docs` exist under the project root.

- [ ] **Step 2: Write the failing tests for report parsing and site generation**

Write `tests/test_generate_daily_site.py` with:

```python
import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_daily_site import build_site, parse_report


class ParseReportTests(unittest.TestCase):
    def test_parse_report_extracts_summary_and_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "youth-ai-competitions-2026-06-04.md"
            path.write_text(
                textwrap.dedent(
                    """\
                    青少年AI赛事资料更新 2026-06-04

                    今日变化提醒
                    - 第一条变化。
                    - 第二条变化。
                    - 第三条变化。

                    主表
                    | 赛事 | 年级 |
                    | --- | --- |
                    | 样例赛 | 小学 |

                    渠道覆盖与失败说明
                    - 说明内容。
                    """
                ),
                encoding="utf-8",
            )

            report = parse_report(path)

            self.assertEqual(report.date, "2026-06-04")
            self.assertEqual(report.title, "青少年AI赛事资料更新 2026-06-04")
            self.assertEqual(report.summary_bullets[:2], ["第一条变化。", "第二条变化。"])
            self.assertIn("主表", report.sections)
            self.assertEqual(report.archive_headline, "第一条变化。")

    def test_parse_report_supports_markdown_headings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "youth-ai-competitions-2026-05-31.md"
            path.write_text(
                textwrap.dedent(
                    """\
                    # 青少年AI赛事资料更新 2026-05-31

                    ## 今日变化提醒
                    - 旧格式第一条。
                    - 旧格式第二条。

                    ## 渠道覆盖与失败说明
                    - 说明内容。
                    """
                ),
                encoding="utf-8",
            )

            report = parse_report(path)

            self.assertEqual(report.title, "青少年AI赛事资料更新 2026-05-31")
            self.assertEqual(report.summary_bullets[0], "旧格式第一条。")


class BuildSiteTests(unittest.TestCase):
    def test_build_site_writes_home_detail_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "reports"
            reports_dir.mkdir()
            (reports_dir / "youth-ai-competitions-2026-06-03.md").write_text(
                "青少年AI赛事资料更新 2026-06-03\\n\\n今日变化提醒\\n- 旧日报变化。\\n\\n渠道覆盖与失败说明\\n- 说明。\\n",
                encoding="utf-8",
            )
            (reports_dir / "youth-ai-competitions-2026-06-04.md").write_text(
                "青少年AI赛事资料更新 2026-06-04\\n\\n今日变化提醒\\n- 最新日报变化。\\n- 第二条。\\n\\n渠道覆盖与失败说明\\n- 说明。\\n",
                encoding="utf-8",
            )

            build_site(root)

            self.assertTrue((root / "index.html").exists())
            self.assertTrue((root / "daily" / "2026-06-04.html").exists())
            self.assertTrue((root / "site-data" / "reports.json").exists())
            self.assertIn("最新日报变化", (root / "index.html").read_text(encoding="utf-8"))
            self.assertIn("暖灰", (root / "assets" / "site.css").read_text(encoding="utf-8"))
            data = json.loads((root / "site-data" / "reports.json").read_text(encoding="utf-8"))
            self.assertEqual(data[0]["date"], "2026-06-04")


class CliTests(unittest.TestCase):
    def test_cli_builds_site_for_current_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "reports"
            reports_dir.mkdir()
            (reports_dir / "youth-ai-competitions-2026-06-04.md").write_text(
                "青少年AI赛事资料更新 2026-06-04\\n\\n今日变化提醒\\n- 今日变化。\\n\\n渠道覆盖与失败说明\\n- 说明。\\n",
                encoding="utf-8",
            )

            script_src = Path(__file__).resolve().parent.parent / "scripts" / "generate_daily_site.py"
            script_dir = root / "scripts"
            script_dir.mkdir()
            script_dst = script_dir / "generate_daily_site.py"
            script_dst.write_text(script_src.read_text(encoding="utf-8"), encoding="utf-8")

            result = subprocess.run(
                ["python3", str(script_dst)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "index.html").exists())
            self.assertTrue((root / "daily" / "2026-06-04.html").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail because the generator does not exist yet**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: FAIL with an import error or missing `scripts.generate_daily_site`.

- [ ] **Step 4: Write the initial generator implementation**

Write `scripts/generate_daily_site.py` based on the Shanghai project generator, but adapt it to the youth competitions report schema:

```python
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path


SECTION_TITLES = [
    "今日变化提醒",
    "主表",
    "小红书新增线索",
    "渠道覆盖与失败说明",
]


@dataclass
class Report:
    date: str
    title: str
    summary_bullets: list[str]
    archive_headline: str
    archive_summary: str
    trend_bullets: list[str]
    detail_path: str
    sections: dict[str, str]
    source_path: str


def normalize_heading(text: str) -> str:
    return re.sub(r"^#+\\s*", "", text).strip()


def split_sections(lines: list[str]) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw in lines:
        normalized = normalize_heading(raw.strip())
        if normalized in SECTION_TITLES:
            current = normalized
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(raw.rstrip())
    return {key: "\\n".join(value).strip() for key, value in sections.items()}


def extract_bullets(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^[-*]\\s*(.+)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return items


def parse_report(path: Path) -> Report:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    title = normalize_heading(lines[0].strip())
    date_match = re.search(r"(\\d{4}-\\d{2}-\\d{2})", title)
    if not date_match:
        raise ValueError(f"Could not find date in title: {title}")
    date = date_match.group(1)
    sections = split_sections(lines[1:])
    summary_bullets = extract_bullets(sections.get("今日变化提醒", ""))
    if not summary_bullets:
        raise ValueError(f"Report has no 今日变化提醒 bullets: {path}")
    return Report(
        date=date,
        title=title,
        summary_bullets=summary_bullets,
        archive_headline=summary_bullets[0],
        archive_summary=summary_bullets[1] if len(summary_bullets) > 1 else summary_bullets[0],
        trend_bullets=summary_bullets[:3],
        detail_path=f"daily/{date}.html",
        sections=sections,
        source_path=str(path),
    )


def collect_reports(root: Path) -> list[Report]:
    reports = [parse_report(path) for path in sorted((root / "reports").glob("youth-ai-competitions-*.md"))]
    return sorted(reports, key=lambda item: item.date, reverse=True)


def build_site(root: Path) -> None:
    reports = collect_reports(root)
    if not reports:
        raise ValueError("No reports found in reports/")
    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "daily").mkdir(parents=True, exist_ok=True)
    (root / "site-data").mkdir(parents=True, exist_ok=True)
    write_assets(root / "assets")
    write_json_index(root / "site-data" / "reports.json", reports)
    write_homepage(root / "index.html", reports)
    write_detail_pages(root, reports)


if __name__ == "__main__":
    build_site(Path.cwd())
```

- [ ] **Step 5: Run the tests again and capture the remaining failures**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: some tests still fail because homepage/detail rendering helpers and assets are incomplete.

- [ ] **Step 6: Commit the scaffolding and first generator pass**

```bash
git add docs/superpowers/plans/2026-06-04-youth-ai-competitions-daily-web-implementation.md scripts/generate_daily_site.py tests/test_generate_daily_site.py
git commit -m "feat: scaffold youth competitions site generator"
```

### Task 2: Finish the static site renderer and verify output

**Files:**
- Modify: `scripts/generate_daily_site.py`
- Modify: `tests/test_generate_daily_site.py`
- Modify: `reports/latest.md` by running the generator later
- Generate: `index.html`
- Generate: `daily/*.html`
- Generate: `site-data/reports.json`
- Generate: `assets/site.css`
- Generate: `assets/site.js`

- [ ] **Step 1: Add the HTML rendering helpers and assets writer**

Expand `scripts/generate_daily_site.py` with:

```python
def write_assets(assets_dir: Path) -> None:
    css = """/* 暖灰苹果风赛事日报站样式 */ ... """
    js = """document.documentElement.dataset.site = 'youth-ai-competitions-daily';"""
    (assets_dir / "site.css").write_text(css, encoding="utf-8")
    (assets_dir / "site.js").write_text(js, encoding="utf-8")


def write_json_index(path: Path, reports: list[Report]) -> None:
    path.write_text(
        json.dumps(
            [
                {
                    "date": report.date,
                    "title": report.title,
                    "archiveHeadline": report.archive_headline,
                    "archiveSummary": report.archive_summary,
                    "summaryBullets": report.summary_bullets[:3],
                    "detailPath": report.detail_path,
                }
                for report in reports
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_homepage(path: Path, reports: list[Report]) -> None:
    latest = reports[0]
    archive_items = "\\n".join(render_archive_item(report) for report in reports)
    trend_cards = "\\n".join(render_trend_card(report, idx) for idx, report in enumerate(reports[:5], start=1))
    path.write_text(
        f\"\"\"<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(latest.title)}</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">Youth AI Competitions Daily</div>
      <h1>青少年AI赛事资料更新</h1>
      <p>聚焦新增赛事、报名截止、赛程变化与奖项调整的持续日报站点。</p>
    </section>
    <section class="feature">
      <div class="feature-copy">
        <div class="eyebrow">最新日报</div>
        <h2>{html.escape(latest.archive_headline)}</h2>
        <ul class="bullet-list">
          {''.join(f'<li>{html.escape(item)}</li>' for item in latest.summary_bullets[:4])}
        </ul>
      </div>
      <article class="summary-card">
        <div class="date">{html.escape(latest.date)}</div>
        <div class="claim">{html.escape(latest.archive_summary)}</div>
        <a class="cta" href="{html.escape(latest.detail_path)}">查看当日详情页 →</a>
      </article>
    </section>
    <section class="section">
      <div class="section-head">
        <h2>最新日报判断</h2>
        <p>最近几天最值得优先关注的赛事变化。</p>
      </div>
      <div class="trend-grid">{trend_cards}</div>
    </section>
    <section class="section">
      <div class="section-head">
        <h2>历史归档</h2>
        <p>按日期查看每一篇青少年AI赛事日报。</p>
      </div>
      <div class="archive-wrap">{archive_items}</div>
    </section>
  </main>
</body>
</html>\"\"\",
        encoding="utf-8",
    )
```

- [ ] **Step 2: Add detail-page rendering for the four report sections**

In `scripts/generate_daily_site.py`, add:

```python
def write_detail_pages(root: Path, reports: list[Report]) -> None:
    daily_dir = root / "daily"
    for index, report in enumerate(reports):
        prev_link = reports[index - 1].detail_path if index > 0 else ""
        next_link = reports[index + 1].detail_path if index + 1 < len(reports) else ""
        body = "".join(render_detail_section(name, report.sections.get(name, "")) for name in SECTION_TITLES if report.sections.get(name))
        html_text = f\"\"\"<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(report.title)}</title>
  <link rel="stylesheet" href="../assets/site.css">
</head>
<body>
  <main class="page">
    <section class="detail-hero">
      <div class="eyebrow"><a href="../index.html">返回首页</a></div>
      <h1>{html.escape(report.title)}</h1>
    </section>
    <div class="detail-layout">
      <aside class="toc">
        <h3>目录</h3>
        <ul>
          {''.join(f'<li><a href="#{slugify(name)}">{html.escape(name)}</a></li>' for name in SECTION_TITLES if report.sections.get(name))}
        </ul>
      </aside>
      <article class="detail-card">{body}
        <div class="footer-nav">
          <span>{f'<a href="{prev_link}">← 更新的日报</a>' if prev_link else ''}</span>
          <span>{f'<a href="{next_link}">更早的日报 →</a>' if next_link else ''}</span>
        </div>
      </article>
    </div>
  </main>
</body>
</html>\"\"\"
        (daily_dir / f"{report.date}.html").write_text(html_text, encoding="utf-8")
```

- [ ] **Step 3: Implement Markdown-to-HTML helpers for bullets, paragraphs, and tables**

Add the helper layer in `scripts/generate_daily_site.py`:

```python
def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9\\u4e00-\\u9fff]+", "-", text.lower()).strip("-")


def render_detail_section(title: str, content: str) -> str:
    if title == "主表":
        return f'<section id="{slugify(title)}"><h2>{html.escape(title)}</h2>{render_markdown_table(content)}</section>'
    return f'<section id="{slugify(title)}"><h2>{html.escape(title)}</h2>{render_rich_text(content)}</section>'


def render_rich_text(text: str) -> str:
    blocks: list[str] = []
    current_list: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        bullet = re.match(r"^[-*]\\s*(.+)$", stripped)
        if bullet:
            current_list.append(f"<li>{html.escape(bullet.group(1).strip())}</li>")
            continue
        if current_list:
            blocks.append(f"<ul>{''.join(current_list)}</ul>")
            current_list = []
        if stripped:
            blocks.append(f"<p>{html.escape(stripped)}</p>")
    if current_list:
        blocks.append(f"<ul>{''.join(current_list)}</ul>")
    return "".join(blocks)
```

- [ ] **Step 4: Run the full test suite and verify it passes**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS for every test in `tests/test_generate_daily_site.py`.

- [ ] **Step 5: Generate the site for the real project reports**

Run:

```bash
python3 scripts/generate_daily_site.py
```

Expected: `index.html`, `daily/`, `site-data/reports.json`, and `assets/` are created or updated in the project root.

- [ ] **Step 6: Verify the generated files exist and contain the latest report**

Run:

```bash
test -f index.html && test -f daily/2026-06-04.html && test -f site-data/reports.json && test -f assets/site.css && echo OK
```

Expected: output `OK`.

- [ ] **Step 7: Spot-check the homepage and latest detail page**

Run:

```bash
sed -n '1,140p' index.html
sed -n '1,180p' daily/2026-06-04.html
```

Expected: the homepage headline reads `青少年AI赛事资料更新`, the latest summary is visible, and the detail page contains the four expected sections.

- [ ] **Step 8: Commit the finished site generator and generated assets**

```bash
git add scripts/generate_daily_site.py tests/test_generate_daily_site.py index.html daily site-data assets
git commit -m "feat: build youth competitions static report site"
```

### Task 3: Replace WeChat delivery rules with GitHub Pages publishing

**Files:**
- Modify: `automation-prompt.md`
- Modify: `README.md`
- Create: `docs/github-pages.md`
- Create: `.github/workflows/pages.yml`

- [ ] **Step 1: Update the README to describe web publishing instead of WeChat delivery**

Replace the README delivery and dependency sections so it reads:

```markdown
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
```

- [ ] **Step 2: Rewrite the automation prompt’s delivery section for site publishing**

In `automation-prompt.md`, replace the current “微信发送要求” block with:

```markdown
网页发布要求：
- 完成日报正文后，不再通过微信发送整篇日报。
- 必须运行 `python3 scripts/generate_daily_site.py` 生成并刷新本项目网页日报站。
- 站点校验通过后，必须把当天 Markdown 与网页产物提交并推送到 GitHub `main`，让 GitHub Pages 自动更新公网网站。
- 站点至少要更新以下产物：
  - `index.html`
  - `daily/YYYY-MM-DD.html`
  - `site-data/reports.json`
  - `assets/site.css`

发布校验要求：
1. `index.html` 已更新；
2. 当天 `daily/YYYY-MM-DD.html` 已生成；
3. `site-data/reports.json` 已更新；
4. 首页能看到当天摘要、趋势区块和历史归档入口；
5. `git status --short` 能看到当天应发布的变更，或确认当天无新增内容；
6. 如有变更，执行 `git add reports/youth-ai-competitions-YYYY-MM-DD.md reports/latest.md index.html daily/YYYY-MM-DD.html site-data/reports.json assets/site.css assets/site.js automation-prompt.md README.md .github/workflows/pages.yml docs/github-pages.md scripts/generate_daily_site.py tests/test_generate_daily_site.py`；
7. 提交：`git commit -m "chore: publish daily report YYYY-MM-DD"`；
8. 推送：`git push origin main`。如果 push 因凭证、网络或远端权限失败，不要说网站已更新，只能说“本地日报和网页已生成，GitHub Pages 发布被推送失败阻塞”，并给出失败命令与错误摘要。
```

- [ ] **Step 3: Add the GitHub Pages workflow**

Create `.github/workflows/pages.yml` with:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: github-pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure Pages
        uses: actions/configure-pages@v5

      - name: Run tests
        run: python3 -m unittest discover -s tests -v

      - name: Generate site
        run: python3 scripts/generate_daily_site.py

      - name: Stage static site
        run: |
          rm -rf _site
          mkdir -p _site
          cp index.html _site/
          cp -R assets daily site-data _site/
          touch _site/.nojekyll

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 4: Add the GitHub Pages operator guide**

Create `docs/github-pages.md` with:

```markdown
# GitHub Pages 发布说明

这个项目已经准备为 GitHub Pages 静态站发布。

## 本地构建

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_daily_site.py
```

## 首次发布

1. 初始化本地 Git 仓库并切到 `main`。
2. 添加远端：

```bash
git remote add origin https://github.com/SophieNie1997/youth-ai-competitions-daily.git
git push -u origin main
```

3. 在 GitHub 仓库页面进入 `Settings` -> `Pages`。
4. 将 `Build and deployment` 的 `Source` 设置为 `GitHub Actions`。
5. 打开 `Actions` 页面，等待 `Deploy GitHub Pages` workflow 成功。

成功后，站点 URL 通常是：

```text
https://sophienie1997.github.io/youth-ai-competitions-daily/
```
```

- [ ] **Step 5: Run tests after the prompt/docs/workflow changes**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS; documentation and workflow changes should not break the tested generator.

- [ ] **Step 6: Commit the publishing flow changes**

```bash
git add README.md automation-prompt.md docs/github-pages.md .github/workflows/pages.yml
git commit -m "chore: add github pages publishing flow"
```

### Task 4: Initialize Git, connect the remote, and publish the first version

**Files:**
- Create: `.git/` metadata via Git
- Modify: generated site files by running the generator
- Publish: remote `origin` on GitHub

- [ ] **Step 1: Initialize the repository and switch to the main branch**

Run:

```bash
git init
git branch -M main
```

Expected: `.git` exists and `git branch --show-current` returns `main`.

- [ ] **Step 2: Add the GitHub remote if it is not already configured**

Run:

```bash
git remote add origin https://github.com/SophieNie1997/youth-ai-competitions-daily.git
git remote -v
```

Expected: `origin` appears for both fetch and push with the GitHub URL.

- [ ] **Step 3: Run the tests and generator one more time before first publish**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_daily_site.py
```

Expected: tests pass and the site artifacts are current.

- [ ] **Step 4: Inspect the Git diff for the first publish set**

Run:

```bash
git status --short
```

Expected: the output shows the Markdown reports, generator, tests, workflow, docs, and generated site files that should be published.

- [ ] **Step 5: Create the first publish commit**

```bash
git add .
git commit -m "chore: publish youth competitions daily site"
```

- [ ] **Step 6: Push the repository to GitHub**

Run:

```bash
git push -u origin main
```

Expected: push succeeds and GitHub receives the full project contents.

- [ ] **Step 7: Verify the Pages workflow file is present on the remote branch**

Run:

```bash
git ls-files .github/workflows/pages.yml scripts/generate_daily_site.py tests/test_generate_daily_site.py index.html site-data/reports.json
```

Expected: each listed file path appears in the output.

- [ ] **Step 8: Record the first-release operational note**

Add this note to the project’s runbook or release comment:

```text
After the first push, open GitHub Settings -> Pages and confirm the source is GitHub Actions. The website is not considered live until the Deploy GitHub Pages workflow has succeeded.
```

- [ ] **Step 9: Commit any final operator-note updates**

```bash
git add docs/github-pages.md README.md
git commit -m "docs: note first pages activation step"
```

## Spec Coverage Check

- Static site generator from Markdown reports: covered by Task 1 and Task 2.
- Event-specific homepage and detail pages: covered by Task 2.
- Replace WeChat delivery with web publishing: covered by Task 3.
- GitHub Pages workflow and docs: covered by Task 3.
- Git initialization and remote publishing to `SophieNie1997/youth-ai-competitions-daily`: covered by Task 4.

## Placeholder Scan

- No `TODO`, `TBD`, or “implement later” placeholders remain.
- All file paths are explicit.
- All commands are concrete and runnable in this repository.

## Type Consistency Check

- The plan consistently uses `today 变化提醒` as the summary source and `reports/youth-ai-competitions-YYYY-MM-DD.md` as the report pattern.
- The generator output paths are consistent across tests, workflow, and automation prompt updates.
