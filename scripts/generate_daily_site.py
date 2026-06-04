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


def format_date_label(date: str) -> str:
    year, month, day = date.split("-")
    return f"{year} / {month} / {day}"


def normalize_heading(text: str) -> str:
    return re.sub(r"^#+\s*", "", text).strip()


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
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def extract_bullets(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^[-*]\s*(.+)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return items


def parse_report(path: Path) -> Report:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    title = normalize_heading(lines[0].strip())
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", title)
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


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text.lower()).strip("-")


def render_inline(text: str) -> str:
    placeholders: list[str] = []

    def store(fragment: str) -> str:
        placeholders.append(fragment)
        return f"__HTML_PLACEHOLDER_{len(placeholders) - 1}__"

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda match: store(
            f'<a href="{html.escape(match.group(2), quote=True)}">{html.escape(match.group(1))}</a>'
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda match: store(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )
    text = re.sub(
        r"(?<![\(\"=])(https?://[^\s<)]+)",
        lambda match: store(
            f'<a href="{html.escape(match.group(1), quote=True)}">{html.escape(match.group(1))}</a>'
        ),
        text,
    )

    escaped = html.escape(text)
    for index, fragment in enumerate(placeholders):
        escaped = escaped.replace(f"__HTML_PLACEHOLDER_{index}__", fragment)
    return escaped


def render_markdown_table(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
    if len(table_lines) < 2:
        return render_rich_text(text)

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:
        rows.append([cell.strip() for cell in line.strip("|").split("|")])

    thead = "".join(f"<th>{render_inline(cell)}</th>" for cell in headers)
    tbody_rows = []
    for row in rows:
        cells = "".join(f"<td>{render_inline(cell)}</td>" for cell in row)
        tbody_rows.append(f"<tr>{cells}</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{thead}</tr></thead><tbody>{"".join(tbody_rows)}</tbody></table></div>'


def render_rich_text(text: str) -> str:
    blocks: list[str] = []
    current_list: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        bullet = re.match(r"^[-*]\s*(.+)$", stripped)
        if bullet:
            current_list.append(f"<li>{render_inline(bullet.group(1).strip())}</li>")
            continue
        if current_list:
            blocks.append(f"<ul>{''.join(current_list)}</ul>")
            current_list = []
        if stripped:
            blocks.append(f"<p>{render_inline(stripped)}</p>")
    if current_list:
        blocks.append(f"<ul>{''.join(current_list)}</ul>")
    return "".join(blocks)


def render_detail_section(title: str, content: str) -> str:
    if title == "主表":
        body = render_markdown_table(content)
    else:
        body = render_rich_text(content)
    return f'<section id="{slugify(title)}"><h2>{html.escape(title)}</h2>{body}</section>'


def render_archive_item(report: Report) -> str:
    return f"""
    <article class="archive-item">
      <strong>{html.escape(report.date)}</strong>
      <div>
        <div class="headline">{render_inline(report.archive_headline)}</div>
        <p>{render_inline(report.archive_summary)}</p>
      </div>
      <a class="jump" href="{html.escape(report.detail_path)}">阅读全文</a>
    </article>
    """


def render_trend_card(report: Report, index: int) -> str:
    headline = report.trend_bullets[0] if report.trend_bullets else report.archive_headline
    description = report.trend_bullets[1] if len(report.trend_bullets) > 1 else report.archive_summary
    return f"""
    <article class="trend-card">
      <div class="tag">趋势 {index}</div>
      <h3>{render_inline(headline)}</h3>
      <p>{render_inline(description)}</p>
    </article>
    """


def write_assets(assets_dir: Path) -> None:
    css = """/* 暖灰苹果风赛事日报站样式 */
:root {
  --bg: linear-gradient(180deg, #ebe6de 0%, #f3f0eb 38%, #e0d8ce 100%);
  --paper: rgba(255, 255, 255, 0.68);
  --paper-strong: rgba(255, 255, 255, 0.84);
  --ink: #1f1f20;
  --muted: #686259;
  --line: rgba(33, 28, 22, 0.08);
  --accent: #a95a2a;
  --link: #0a66d1;
  --shadow: 0 20px 60px rgba(76, 56, 35, 0.08);
  --radius-xl: 34px;
  --radius-lg: 26px;
  --radius-md: 18px;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Helvetica Neue", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at 10% 0%, rgba(244, 209, 170, 0.42), transparent 22%),
    radial-gradient(circle at 90% 5%, rgba(255, 255, 255, 0.75), transparent 18%),
    radial-gradient(circle at 65% 100%, rgba(196, 183, 170, 0.24), transparent 28%),
    var(--bg);
}
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
.page { width: min(1120px, calc(100vw - 32px)); margin: 0 auto; padding: 40px 0 72px; }
.hero, .detail-hero { padding: 28px 0 24px; }
.hero { text-align: center; }
.eyebrow { color: var(--accent); font-size: 13px; font-weight: 700; margin-bottom: 10px; }
.hero h1, .detail-hero h1 { font-size: clamp(42px, 6vw, 64px); line-height: 1.02; letter-spacing: -0.045em; margin: 0; }
.hero p { color: var(--muted); font-size: clamp(18px, 2.3vw, 22px); line-height: 1.45; max-width: 760px; margin: 18px auto 0; }
.feature, .trend-card, .summary-card, .detail-card, .archive-wrap, .toc {
  background: var(--paper);
  border: 1px solid rgba(255,255,255,0.45);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}
.feature { border-radius: var(--radius-xl); padding: 28px; display: grid; grid-template-columns: 1.3fr .85fr; gap: 20px; }
.feature-copy h2 { font-size: clamp(30px, 4.4vw, 52px); line-height: 1.16; letter-spacing: -0.035em; margin: 8px 0 14px; max-width: 12ch; }
.bullet-list { margin: 20px 0 0; padding-left: 22px; line-height: 1.8; }
.summary-card { border-radius: var(--radius-lg); padding: 22px; display: flex; flex-direction: column; justify-content: space-between; gap: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(250,247,242,0.82)); }
.summary-card .card-label { color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.summary-card .date-chip { display: inline-flex; align-items: center; width: fit-content; border-radius: 999px; background: rgba(169, 90, 42, 0.1); color: #7a4d2f; border: 1px solid rgba(169, 90, 42, 0.16); padding: 10px 14px; font-size: 13px; font-weight: 700; letter-spacing: 0.08em; }
.summary-card .claim { font-size: clamp(22px, 2.3vw, 32px); line-height: 1.32; letter-spacing: -0.03em; margin-top: 0; }
.summary-card .cta { margin-top: 6px; color: var(--accent); font-weight: 700; }
.section { margin-top: 42px; }
.section-head { text-align: center; margin-bottom: 18px; }
.section-head h2 { font-size: 38px; line-height: 1.08; letter-spacing: -0.035em; margin: 0; }
.section-head p { color: var(--muted); font-size: 17px; margin: 8px 0 0; }
.trend-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.trend-card { border-radius: 28px; padding: 22px; }
.trend-card .tag { color: var(--accent); font-size: 12px; font-weight: 700; margin-bottom: 10px; }
.trend-card h3 { font-size: 25px; line-height: 1.18; letter-spacing: -0.025em; margin: 0 0 10px; }
.trend-card p { color: var(--muted); font-size: 15px; line-height: 1.68; margin: 0; }
.archive-wrap { border-radius: var(--radius-xl); overflow: hidden; }
.archive-item { display: grid; grid-template-columns: 120px 1fr 110px; gap: 18px; padding: 20px 24px; border-top: 1px solid var(--line); align-items: center; }
.archive-item:first-child { border-top: 0; }
.archive-item .headline { font-size: 18px; margin-bottom: 4px; }
.archive-item p { margin: 0; color: var(--muted); line-height: 1.6; font-size: 14px; }
.archive-item .jump { justify-self: end; color: var(--accent); font-weight: 700; }
.detail-layout { display: grid; grid-template-columns: 280px 1fr; gap: 24px; align-items: start; }
.toc { border-radius: 24px; padding: 18px; position: sticky; top: 18px; }
.toc h3 { margin: 0 0 12px; font-size: 18px; }
.toc ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.toc a { color: var(--muted); font-size: 14px; }
.detail-card { border-radius: var(--radius-xl); padding: 28px; }
.detail-card section + section { margin-top: 28px; }
.detail-card h2 { font-size: 28px; line-height: 1.15; letter-spacing: -0.025em; margin: 0 0 14px; }
.detail-card p { line-height: 1.8; margin: 10px 0; }
.detail-card ul { padding-left: 22px; line-height: 1.8; }
.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 20px; background: var(--paper-strong); }
table { width: 100%; border-collapse: collapse; min-width: 860px; }
th, td { text-align: left; vertical-align: top; padding: 14px 16px; border-top: 1px solid var(--line); line-height: 1.65; }
thead th { border-top: 0; font-size: 14px; color: var(--muted); font-weight: 700; background: rgba(255,255,255,.52); }
.footer-nav { margin-top: 28px; display: flex; justify-content: space-between; gap: 12px; }
code { background: rgba(255,255,255,.7); border-radius: 8px; padding: 1px 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .92em; }
@media (max-width: 900px) {
  .feature, .detail-layout, .trend-grid, .archive-item { grid-template-columns: 1fr; }
  .archive-item .jump { justify-self: start; }
  .toc { position: static; }
  .page { width: min(100vw - 20px, 1120px); padding-top: 24px; }
}
"""
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
    latest_date_label = format_date_label(latest.date)
    archive_items = "\n".join(render_archive_item(report) for report in reports)
    trend_cards = "\n".join(render_trend_card(report, idx) for idx, report in enumerate(reports[:5], start=1))
    latest_bullets = "".join(f"<li>{render_inline(item)}</li>" for item in latest.summary_bullets[:4])
    path.write_text(
        f"""<!doctype html>
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
        <h2>{render_inline(latest.archive_headline)}</h2>
        <ul class="bullet-list">{latest_bullets}</ul>
      </div>
      <article class="summary-card">
        <div>
          <div class="card-label">今日更新</div>
          <div class="date-chip">{html.escape(latest_date_label)}</div>
        </div>
        <div class="claim">{render_inline(latest.archive_summary)}</div>
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
</html>""",
        encoding="utf-8",
    )


def write_detail_pages(root: Path, reports: list[Report]) -> None:
    daily_dir = root / "daily"
    for index, report in enumerate(reports):
        prev_link = reports[index - 1].detail_path if index > 0 else ""
        next_link = reports[index + 1].detail_path if index + 1 < len(reports) else ""
        nav_links = "".join(
            f'<li><a href="#{slugify(name)}">{html.escape(name)}</a></li>'
            for name in SECTION_TITLES
            if report.sections.get(name)
        )
        body = "".join(
            render_detail_section(name, report.sections.get(name, ""))
            for name in SECTION_TITLES
            if report.sections.get(name)
        )
        prev_html = f'<a href="../{prev_link}">← 更新的日报</a>' if prev_link else ""
        next_html = f'<a href="../{next_link}">更早的日报 →</a>' if next_link else ""
        html_text = f"""<!doctype html>
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
        <ul>{nav_links}</ul>
      </aside>
      <article class="detail-card">
        {body}
        <div class="footer-nav">
          <span>{prev_html}</span>
          <span>{next_html}</span>
        </div>
      </article>
    </div>
  </main>
</body>
</html>"""
        (daily_dir / f"{report.date}.html").write_text(html_text, encoding="utf-8")


def build_site(root: Path) -> None:
    reports = collect_reports(root)
    if not reports:
        raise ValueError("No reports found in reports/")
    assets_dir = root / "assets"
    daily_dir = root / "daily"
    data_dir = root / "site-data"
    assets_dir.mkdir(parents=True, exist_ok=True)
    daily_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    write_assets(assets_dir)
    write_json_index(data_dir / "reports.json", reports)
    write_homepage(root / "index.html", reports)
    write_detail_pages(root, reports)


if __name__ == "__main__":
    build_site(Path.cwd())
