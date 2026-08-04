#!/usr/bin/env python3
"""Generate the static B-dashboard contract from the audited daily JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "market-data.json"
TARGET = ROOT / "dashboard" / "app" / "dashboard-data.ts"


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def tone(signal: str) -> str:
    if "红" in signal:
        return "red"
    if "黄" in signal:
        return "yellow"
    if "灰" in signal:
        return "gray"
    return "green"


def date_short(value: str) -> str:
    if not value or value == "待核验":
        return "待核验"
    match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", value)
    return f"{int(match.group(2)):02d}.{int(match.group(3)):02d}" if match else value


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract = data["v2"]
    daily = data["daily"]

    excluded = {"国际油价（美元/桶）", "AI巨头营收增速"}
    selected_risks = [r for r in data["riskDashboard"] if r["name"] not in excluded]
    risks = [
        [r["name"], r["value"], tone(r["signal"]), r["normal"], r["refreshStatus"], r["sourceDate"]]
        for r in selected_risks
    ]
    light_counts = {"green": 0, "yellow": 0, "red": 0, "gray": 0}
    for row in risks:
        light_counts[row[2]] += 1

    industries = []
    for item in data["industryWatch"][:10]:
        score = int(item.get("score") or 0)
        heat = float(item.get("heat") or 0)
        prosperity = float(item.get("prosperity") or 0)
        risk = float(item.get("risk") or 50)
        hit = re.search(r"新闻命中(\d+)项", item.get("reason", ""))
        high_frequency = min(int(hit.group(1)) if hit else 0, 10)
        factors = {
            "trend": round(score * 0.25),
            "flow": round(heat * 0.25),
            "fundamental": round(prosperity * 0.25),
            "hf": high_frequency,
            "value": round((100 - risk) * 0.15),
        }
        research = min(sum(factors.values()), 100)
        research_tone = "green" if research >= 70 else "yellow" if research >= 55 else "red"
        execution_tone = "gray" if contract["dataHealth"] == "灰灯" else ("red" if contract["marketGate"] == "停止新增" else research_tone)
        industries.append({
            "name": item["name"], "score": research, **factors,
            "research": research_tone, "execute": execution_tone,
            "risk": item.get("nextSignal") or item.get("reason"),
            "operation": item.get("operation", "继续观察"),
            "proxy": "五因子为公开字段透明代理，并非真实资金流或PE。",
        })

    events = []
    for item in data["financeNews"][:10]:
        direction = 1 if item.get("direction") == "利多" else -1 if item.get("direction") == "利空" else 0
        events.append({
            "title": item["title"], "priority": int(item.get("score") or 0),
            "direction": direction, "confidence": item.get("confidence", "待核验"),
            "source": item.get("source", "公开来源"), "date": item.get("date", ""),
            "watch": item.get("watch", ""),
        })

    funds = [
        {
            "code": item["code"], "name": item["name"], "sector": item.get("theme", "待分类"),
            "day": item.get("day"), "week": item.get("week"), "risk": item.get("risk", "待核验"),
            "decision": item.get("decision", "等待"), "direction": item.get("reason", ""),
            "date": item.get("navDate", "待核验"),
        }
        for item in data["fundHoldings"]
    ]

    experts = data.get("expertViews", [])
    evidence = {
        "count": len(experts),
        "newCount": sum("无新增" not in x.get("stance", "") for x in experts),
        "strongCount": sum(x.get("strength") in {"高", "中高"} for x in experts),
        "leading": [x["name"] for x in experts if x.get("strength") == "高"][:3],
        "note": "机构观点只作佐证，不能独立触发买入。",
    }

    freshest = {
        "风控": max((r.get("sourceDate", "") for r in data["riskDashboard"] if r.get("sourceDate") != "待核验"), default="待核验"),
        "赛道": data.get("sourceStatus", {}).get("industry", {}).get("sourceDate", "待核验"),
        "跨市场": contract["businessDate"],
        "事件": max((x.get("date", "") for x in data["financeNews"]), default="待核验"),
        "持仓": max((x.get("navDate", "") for x in data["fundHoldings"]), default="待核验"),
    }
    module_status = [
        {"code": "01", "name": "市场风控", "state": contract["marketGate"], "tone": "yellow" if contract["marketGate"] == "风险偏高" else "red" if contract["marketGate"] == "停止新增" else "green", "desc": f"{light_counts['yellow']}项预警"},
        {"code": "02", "name": "行业赛道", "state": "已刷新", "tone": "green", "desc": "20池 / 前10"},
        {"code": "03", "name": "跨市验证", "state": "仅佐证", "tone": "gray", "desc": f"{evidence['newCount']}项新增"},
        {"code": "04", "name": "重大事件", "state": "已刷新", "tone": "green", "desc": "影响前10"},
        {"code": "05", "name": "持仓研究", "state": "已刷新", "tone": "green", "desc": "2股 / 12基"},
    ]
    risk_score = max(int(r.get("score") or 0) for r in data["riskDashboard"])
    snapshot = {
        "businessDate": contract["businessDate"], "generatedAt": contract["generatedAt"],
        "asOf": data.get("sourceStatus", {}).get("asOf", daily.get("asOf", "")),
        "marketGate": contract["marketGate"], "dataHealth": contract["dataHealth"],
        "coverage": round(float(contract["coverage"]) * 100), "riskScore": risk_score,
        "lightCounts": light_counts, "daily": daily,
        "freshness": [{"name": k, "date": date_short(v), "width": round(float(contract["moduleCoverage"].get(str(i), 0)) * 100)} for i, (k, v) in enumerate(freshest.items(), 1)],
        "moduleStatus": module_status,
    }

    stock_source = data.get("stockHoldings", []) or [
        {"code": "002837", "name": "英维克", "theme": "电力 / 数据中心能源", "watch": "能否放量站回20日线并连续2日强于沪深300"},
        {"code": "002555", "name": "三七互娱", "theme": "游戏传媒 / AI应用", "watch": "游戏ETF与个股是否同步放量、连续强于沪深300"},
    ]
    stocks = [
        {
            "code": item.get("code"), "name": item.get("name"), "sector": item.get("theme"),
            "signal": {"绿灯": "green", "黄灯": "yellow", "红灯": "red"}.get(item.get("signal"), "gray"),
            "direction": item.get("direction", "数据不足"), "watch": item.get("watch"),
            "latestPrice": item.get("latestPrice", "待核验"), "day": item.get("day", "待核验"),
            "fiveDay": item.get("fiveDay", "待核验"), "marketDate": item.get("marketDate", "待核验"),
            "risk": item.get("risk", "待核验"),
        }
        for item in stock_source
    ]

    output = "// Generated from data/market-data.json. Do not edit by hand.\n"
    for name, value in (("snapshot", snapshot), ("risks", risks), ("sectors", industries), ("events", events), ("evidence", evidence), ("stocks", stocks), ("funds", funds)):
        output += f"export const {name} = {dump(value)} as const;\n\n"
    TARGET.write_text(output, encoding="utf-8")
    print(f"Generated {TARGET.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
