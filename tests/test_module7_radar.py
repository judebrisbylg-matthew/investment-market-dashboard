from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch


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

    def test_effective_business_date_rolls_sunday_back_to_friday(self) -> None:
        self.assertEqual(
            updater.effective_business_date(date(2026, 8, 23)),
            date(2026, 8, 21),
        )

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

    def test_contract_separates_field_completeness_from_blocked_decision_data(self) -> None:
        data = {
            "riskDashboard": [{"signal": "正常绿灯"} for _ in range(10)],
            "industryWatch": [{"marketDate": "2026-08-21"} for _ in range(10)],
            "financeNews": [{"title": "已核验新闻", "source": "公开来源"} for _ in range(10)],
            "fundHoldings": [{"code": code, "navDate": "2026-08-21"} for code in updater.FUND_ORDER],
            "sourceStatus": {
                "blockingModules": ["industry"],
                "degradedModules": [],
                "risk": {"fresh": 10, "stale": 0},
            },
        }

        contract = updater.notion_v2_contract(data, date(2026, 8, 25))

        self.assertEqual(contract.get("fieldCompleteness"), 1.0)
        data_quality = contract.get("dataQuality", {})
        self.assertEqual(data_quality.get("decisionStatus"), "不可用")
        self.assertIn("行业", data_quality.get("decisionReason", ""))

    def test_industry_fallback_marks_weekend_market_date_unresolved(self) -> None:
        data = {
            "industryWatch": [{
                "name": "AI芯片/半导体",
                "rankingMarket": "A股",
                "marketDate": "2026-08-23",
                "reason": "上次扫描结果。",
            }],
        }

        with patch.object(updater, "build_dynamic_industry_pool", side_effect=RuntimeError("source unavailable")):
            updater.update_industry(data, date(2026, 8, 24))

        item = data["industryWatch"][0]
        self.assertEqual(item["marketDate"], "待核验")
        self.assertIn("原行情日期2026-08-23", item["refreshStatus"])

    def test_daily_summary_is_research_only_when_industry_is_blocked(self) -> None:
        data = {
            "riskDashboard": [{"signal": "正常绿灯"}],
            "sourceStatus": {"blockingModules": ["industry"], "overall": "行业数据回退"},
            "industryWatch": [{"name": "AI芯片/半导体", "tier": "核心主线", "score": 90}],
            "fundHoldings": [],
            "financeNews": [],
        }

        updater.update_daily(data, date(2026, 8, 25))

        daily_text = " ".join(str(value) for value in data["daily"].values())
        self.assertEqual(data["daily"]["action"], "数据核验")
        self.assertIn("数据核验", daily_text)
        self.assertNotIn("仓位建议", daily_text)
        self.assertNotIn("加仓", daily_text)

    def test_radar_replaces_legacy_action_when_decision_data_is_unavailable(self) -> None:
        data = {
            "v2": {
                "marketGate": "数据不足",
                "dataHealth": "灰灯",
                "dataQuality": {"decisionStatus": "不可用", "decisionReason": "行业观察数据回退"},
            },
            "industryWatch": [{
                "name": "AI芯片/半导体",
                "score": 84,
                "tier": "核心主线",
                "operation": "建议加仓",
                "marketDate": "2026-08-21",
                "refreshStatus": "接口异常，沿用最近交易日",
            }],
            "fundHoldings": [],
        }

        radar = updater.build_opportunity_radar(data, date(2026, 8, 25))

        self.assertEqual(radar["industries"][0]["operation"], "仅研究快照，待核验")
        self.assertEqual(radar["industries"][0]["score"], 84)
        self.assertEqual(radar["industries"][0]["marketDate"], "2026-08-21")
        self.assertIn("接口异常", radar["industries"][0]["sourceStatus"])

    def test_dashboard_radar_exports_completeness_and_decision_state_separately(self) -> None:
        data = self.sample_data_with_radar()
        data["opportunityRadar"].update({
            "fieldCompleteness": 0.9643,
            "dataQuality": {
                "decisionStatus": "不可用",
                "decisionReason": "行业观察数据待核验",
            },
        })

        radar = generator.dashboard_opportunity_radar(data)

        self.assertEqual(radar.get("fieldCompleteness"), 0.9643)
        self.assertEqual(radar.get("decisionStatus"), "不可用")
        self.assertEqual(radar.get("decisionReason"), "行业观察数据待核验")

    def test_coded_dashboard_export_labels_unrefreshed_candidates_as_a_catalog(self) -> None:
        data = {
            "v2": {"businessDate": "2026-08-25"},
            "codedOpportunityRadar": updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 25)),
        }

        radar = generator.dashboard_coded_opportunity_radar(data)

        self.assertEqual(radar.get("catalogLabel"), "候选名册｜20/20 未接入日更数据")
        self.assertNotIn("actionRationale", radar["stocks"][0])
        self.assertNotIn("nextTrigger", radar["etfs"][0])


if __name__ == "__main__":
    unittest.main()
