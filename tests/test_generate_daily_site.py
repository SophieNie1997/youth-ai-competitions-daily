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
            self.assertIn("今日更新", homepage)
            self.assertIn("2026 / 06 / 04", homepage)
            css = (root / "assets" / "site.css").read_text(encoding="utf-8")
            self.assertIn("暖灰", css)
            self.assertIn("clamp(24px, 3vw, 40px)", css)
            data = json.loads((root / "site-data" / "reports.json").read_text(encoding="utf-8"))
            self.assertEqual(data[0]["date"], "2026-06-04")


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
