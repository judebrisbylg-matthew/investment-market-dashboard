from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cloud_daily_update as updater  # noqa: E402
import source_validation as validation  # noqa: E402


class SourceConfigTests(unittest.TestCase):
    def test_business_date_uses_prior_completed_open_day(self) -> None:
        open_days = {date(2026, 8, 21), date(2026, 8, 24)}

        self.assertEqual(
            validation.business_date_for(
                datetime(2026, 8, 25, 6, 15, tzinfo=validation.HKT), open_days
            ),
            date(2026, 8, 24),
        )

    def test_updater_does_not_label_national_day_closure_as_a_business_day(self) -> None:
        self.assertEqual(updater.effective_business_date(date(2026, 10, 7)), date(2026, 9, 30))

    def test_fund_source_config_has_each_approved_fund_once(self) -> None:
        rows = validation.load_source_config(ROOT / "data" / "fund-official-sources.json")

        self.assertEqual({row["code"] for row in rows}, set(updater.FUND_ORDER))
        self.assertEqual(len(rows), len(updater.FUND_ORDER))
        self.assertTrue(all(row["source"] == "基金管理人官网" for row in rows))
        self.assertTrue(all(row["url"].startswith("https://") for row in rows))


if __name__ == "__main__":
    unittest.main()
