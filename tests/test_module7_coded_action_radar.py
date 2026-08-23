from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cloud_daily_update as updater  # noqa: E402
import generate_dashboard_data as generator  # noqa: E402
import notion_visible_pages as visible  # noqa: E402


class OpportunityRadarTests(unittest.TestCase):
    @staticmethod
    def block_text(block: dict) -> str:
        kind = block.get("type", "")
        payload = block.get(kind, {})
        rich_text = payload.get("rich_text", [])
        text = "".join(part.get("plain_text") or part.get("text", {}).get("content", "") for part in rich_text)
        if kind == "table":
            for row in payload.get("children", []):
                for cell in row.get("table_row", {}).get("cells", []):
                    text += "".join(part.get("plain_text") or part.get("text", {}).get("content", "") for part in cell)
        return text

    def test_coded_radar_has_spec_codes_and_no_actions_without_model(self) -> None:
        radar = updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 21))

        self.assertEqual([item["code"] for item in radar["stocks"]], [
            "002230", "601138", "300308", "300502", "600584",
            "000977", "002463", "002475", "603986", "688041",
        ])
        self.assertEqual([item["code"] for item in radar["etfs"]], [
            "512720", "516010", "512880", "515220", "515880",
            "562500", "588000", "516960", "512760", "159819",
        ])
        candidates = radar["stocks"] + radar["etfs"]
        self.assertTrue(all(item["researchStatus"] == "数据不足" for item in candidates))
        self.assertTrue(all(item["executionEligible"] is False for item in candidates))
        self.assertTrue(all(item["executionAction"] is None for item in candidates))

    def test_every_relationship_links_catalog_codes(self) -> None:
        radar = updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 21))
        stock_codes = {item["code"] for item in radar["stocks"]}
        etf_codes = {item["code"] for item in radar["etfs"]}

        for relation in radar["relationships"]:
            self.assertTrue(set(relation["stockCodes"]).issubset(stock_codes))
            self.assertIn(relation["etfCode"], etf_codes)
            self.assertIsNone(relation["expressionStrategy"])
            self.assertEqual(relation["relationshipStatus"], "关系待验证")

    def test_dashboard_export_preserves_codes_and_null_actions(self) -> None:
        raw = {
            "codedOpportunityRadar": updater.build_coded_opportunity_radar(
                {"v2": {}}, date(2026, 8, 21)
            )
        }
        radar = generator.dashboard_coded_opportunity_radar(raw)

        self.assertEqual(radar["stocks"][0]["code"], "002230")
        self.assertEqual(radar["etfs"][-1]["code"], "159819")
        self.assertIsNone(radar["stocks"][0]["executionAction"])
        self.assertEqual(radar["executionEngineStatus"], "未启用")

    def test_opportunity_page_has_three_coded_columns_and_engine_boundary(self) -> None:
        page = (Path(__file__).resolve().parents[1] / "dashboard/app/page.tsx").read_text(encoding="utf-8")
        self.assertIn("codedOpportunityRadar", page)
        self.assertIn("7C｜半年潜力股TOP10", page)
        self.assertIn("7E｜股票基金替代关系", page)
        self.assertIn("7D｜潜力基金ETF TOP10", page)
        self.assertIn("执行引擎未启用", page)

    def test_module7_notion_blocks_show_code_pools_without_fake_actions(self) -> None:
        data = {
            "v2": {"businessDate": "2026-08-21", "batchId": "test"},
            "opportunityRadar": {"businessDate": "2026-08-21"},
        }
        data["codedOpportunityRadar"] = updater.build_coded_opportunity_radar(data, date(2026, 8, 21))
        text = " ".join(self.block_text(block) for block in visible.page_blocks("7", data, [], []))

        self.assertIn("7C｜半年潜力股TOP10", text)
        self.assertIn("002230", text)
        self.assertIn("7E｜股票基金替代关系", text)
        self.assertIn("512760", text)
        self.assertIn("7D｜潜力基金ETF TOP10", text)
        self.assertIn("执行引擎未启用", text)
        self.assertNotIn("重仓", text)


if __name__ == "__main__":
    unittest.main()
