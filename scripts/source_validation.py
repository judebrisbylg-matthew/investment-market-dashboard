#!/usr/bin/env python3
"""Validation primitives for the free-source daily release boundary."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
HKT = ZoneInfo("Asia/Hong_Kong")


def load_source_config(path: Path) -> list[dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"{path.name} must contain a JSON list")
    for row in rows:
        if not isinstance(row, dict) or not all(row.get(key) for key in ("code", "source", "url", "assetType")):
            raise ValueError(f"invalid source configuration row in {path.name}")
        if not str(row["url"]).startswith("https://"):
            raise ValueError(f"source URL must be HTTPS: {row['code']}")
    return rows


def load_trading_calendar(path: Path) -> set[date]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    year = int(payload["year"])
    closed = {date.fromisoformat(value) for value in payload.get("closedDays", [])}
    current = date(year, 1, 1)
    end = date(year, 12, 31)
    open_days: set[date] = set()
    while current <= end:
        if current.weekday() < 5 and current not in closed:
            open_days.add(current)
        current += timedelta(days=1)
    return open_days


def business_date_for(run_at: datetime, open_days: set[date]) -> date:
    if run_at.tzinfo is None:
        raise ValueError("run_at must include a timezone")
    local = run_at.astimezone(HKT)
    candidate = local.date() - timedelta(days=1) if local.hour < 16 else local.date()
    for _ in range(10):
        if candidate in open_days:
            return candidate
        candidate -= timedelta(days=1)
    raise ValueError("no completed A-share open day within 10 calendar days")


def check_config(*, live: bool) -> int:
    errors: list[str] = []
    calendar = load_trading_calendar(ROOT / "data" / "a-share-trading-calendar-2026.json")
    if not calendar:
        errors.append("ERROR trading calendar has no open days")
    else:
        print(f"OK trading calendar: {len(calendar)} open days")
    rows = load_source_config(ROOT / "data" / "fund-official-sources.json")
    for row in rows:
        if not live:
            print(f"OK {row['code']} {row['source']}")
            continue
        try:
            request = Request(row["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=15) as response:
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status}")
            print(f"OK {row['code']} {row['source']}")
        except Exception as exc:  # A preflight failure must be visible, not inferred away.
            errors.append(f"ERROR {row['code']} {exc}")
    print("\n".join(errors))
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.check_config or not args.no_write:
        parser.error("only --check-config --no-write is supported")
    return check_config(live=args.live)


if __name__ == "__main__":
    raise SystemExit(main())
