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
        return "".join(part.get("plain_text") or part.get("text", {}).get("content", "") for part in rich_text)

    def sample_data_with_radar(self) -> dict:
        return {
            "v2": {
                "businessDate": "2026-08-24",
                "batchId": "HKT-20260824T061500-dashboard-v2",
                "marketGate": "风险允许",
                "dataHealth": "绿灯",
            },
            "opportunityRadar": {
                "businessDate": "2026-08-24",
                "marketGate": "风险允许",
                "dataHealth": "绿灯",
                "coverage": 1.0,
                "executionStatus": "灰灯",
                "executionBoundary": "未接入验证完备的执行模型，不形成买卖指令。",
                "industries": [{"name": "AI芯片/半导体", "score": 82, "tier": "核心主线", "operation": "继续观察", "marketDate": "2026-08-21", "nextSignal": "成交确认"}],
                "funds": [{"code": "004432", "name": "南方有色金属ETF联接A", "theme": "有色金属", "latestNav": 1.9, "day": 2.9, "navDate": "2026-08-21", "decision": "继续观察"}],
            },
        }

    def test_radar_uses_run_date_but_retains_market_dates(self) -> None:
        data = {
            "industryWatch": [
                {"name": "AI芯片/半导体", "score": 82, "marketDate": "2026-08-21"},
            ],
            "fundHoldings": [
                {"code": "004432", "name": "南方有色金属ETF联接A", "navDate": "2026-08-21"},
            ],
            "v2": {"marketGate": "风险允许", "dataHealth": "绿灯"},
        }

        radar = updater.build_opportunity_radar(data, date(2026, 8, 24))

        self.assertEqual(radar["businessDate"], "2026-08-24")
        self.assertEqual(radar["industries"][0]["marketDate"], "2026-08-21")
        self.assertEqual(radar["executionStatus"], "灰灯")

    def test_module7_blocks_show_business_date_and_gray_execution_boundary(self) -> None:
        blocks = visible.page_blocks("7", self.sample_data_with_radar(), [], [])
        text = " ".join(self.block_text(block) for block in blocks)

        self.assertIn("页面7｜业务日期 2026-08-24", text)
        self.assertIn("执行灰灯", text)

    def test_dashboard_radar_keeps_gray_execution_status(self) -> None:
        radar = generator.dashboard_opportunity_radar(self.sample_data_with_radar())

        self.assertEqual(radar["businessDate"], "2026-08-24")
        self.assertEqual(radar["executionStatus"], "灰灯")
        self.assertEqual(radar["industries"][0]["marketDate"], "2026-08-21")


if __name__ == "__main__":
    unittest.main()
