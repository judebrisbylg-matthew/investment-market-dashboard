from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cloud_daily_update as updater  # noqa: E402


class OpportunityRadarTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
