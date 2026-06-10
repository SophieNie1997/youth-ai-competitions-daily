import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.generate_daily_site import (
    build_site,
    extract_trend_card_data,
    parse_report,
    summarize_for_card,
)


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
                "青少年AI赛事资料更新 2026-06-03\n\n今日变化提醒\n- 旧日报变化。\n\n渠道覆盖与失败说明\n- 说明。\n",
                encoding="utf-8",
            )
            (reports_dir / "youth-ai-competitions-2026-06-04.md").write_text(
                "青少年AI赛事资料更新 2026-06-04\n\n今日变化提醒\n- 最新日报变化。\n- 第二条。\n\n渠道覆盖与失败说明\n- 说明。\n",
                encoding="utf-8",
            )

            build_site(root)

            self.assertTrue((root / "index.html").exists())
            self.assertTrue((root / "daily" / "2026-06-04.html").exists())
            self.assertTrue((root / "site-data" / "reports.json").exists())
            homepage = (root / "index.html").read_text(encoding="utf-8")
            self.assertIn("最新日报变化", homepage)
            self.assertIn("核心变化", homepage)
            self.assertIn("feature-lead", homepage)
            self.assertIn("今日更新", homepage)
            self.assertIn("2026 / 06 / 04", homepage)
            self.assertIn("trend-meta", homepage)
            self.assertIn("关键日期", homepage)
            css = (root / "assets" / "site.css").read_text(encoding="utf-8")
            self.assertIn("暖灰", css)
            self.assertIn("clamp(24px, 3vw, 40px)", css)
            self.assertIn("-webkit-line-clamp: 4", css)
            self.assertIn(".meta-label", css)
            self.assertIn(".archive-item .headline code", css)
            data = json.loads((root / "site-data" / "reports.json").read_text(encoding="utf-8"))
            self.assertEqual(data[0]["date"], "2026-06-04")

    def test_build_site_removes_internal_operations_from_public_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "reports"
            reports_dir.mkdir()
            (reports_dir / "youth-ai-competitions-2026-06-10.md").write_text(
                textwrap.dedent(
                    """\
                    青少年AI赛事资料更新 2026-06-10

                    今日变化提醒
                    - `OpenCLI当日缓存缺失`：opencli-cache/latest.json 过期，BROWSER_CONNECT，daemon 无法启动，curl 失败。
                    - `APOAI 2026进入赛前3天`：官网确认比赛日为 `2026-06-13 14:00-20:00 GMT+8`。
                    - `AIEC 2026线下总决赛进入赛前3天`：官网仍显示 `2026-06-13` 举行总决赛。

                    主表
                    | 赛事 | 年级 |
                    | --- | --- |
                    | APOAI 2026 | 高中生 |

                    小红书新增线索
                    - `今天无可确认的当日新增小红书线索`：opencli-cache/latest.json 不是当天，自动化沙箱无法连通本机 daemon。
                    - `WAICY 2026 参赛指南` / `娃是AI原住民` / `发布时间：2026-06-04` / `5赞`。

                    渠道覆盖与失败说明
                    - `OpenCLI 直接预检`：doctor 输出 daemon failed，curl 失败。
                    """
                ),
                encoding="utf-8",
            )

            build_site(root)

            public_text = "\n".join(
                [
                    (root / "index.html").read_text(encoding="utf-8"),
                    (root / "daily" / "2026-06-10.html").read_text(encoding="utf-8"),
                    (root / "site-data" / "reports.json").read_text(encoding="utf-8"),
                ]
            )

            self.assertIn("APOAI 2026进入赛前3天", public_text)
            self.assertIn("WAICY 2026 参赛指南", public_text)
            for internal_text in (
                "OpenCLI",
                "opencli-cache",
                "BROWSER_CONNECT",
                "daemon",
                "curl",
                "自动化沙箱",
                "渠道覆盖与失败说明",
            ):
                self.assertNotIn(internal_text, public_text)


class SummaryTests(unittest.TestCase):
    def test_summarize_for_card_shortens_long_text(self) -> None:
        text = (
            "新增可报名区域赛事：2026年跨区域面向东盟国家青少年人工智能及机器人邀请赛已发正式通知，"
            "面向16省中小学生和中职学生开放，报名时间到2026-06-26 18:00，比赛时间2026-07-25。"
        )

        summary = summarize_for_card(text, 48)

        self.assertLessEqual(len(summary), 49)
        self.assertTrue(summary.endswith("…"))

    def test_extract_trend_card_data_builds_structured_fields(self) -> None:
        title, change_type, key_dates = extract_trend_card_data(
            "IAI²O 官网已正式延期：官网首页今天新增 Official Deadline Extension Notice，把 Registration Deadline "
            "从 2026-06-07 延到 2026-06-14，Submission Deadline 从 2026-06-20 延到 2026-06-28。"
        )

        self.assertEqual(title, "IAI²O")
        self.assertEqual(change_type, "官网已正式延期")
        self.assertEqual(key_dates, "2026-06-07 / 2026-06-14 / 2026-06-20")


class CliTests(unittest.TestCase):
    def test_cli_builds_site_for_current_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "reports"
            reports_dir.mkdir()
            (reports_dir / "youth-ai-competitions-2026-06-04.md").write_text(
                "青少年AI赛事资料更新 2026-06-04\n\n今日变化提醒\n- 今日变化。\n\n渠道覆盖与失败说明\n- 说明。\n",
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
