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


def dashboard_opportunity_radar(data: dict) -> dict:
    """Return the safe, display-ready subset of the Module 7 daily snapshot."""
    radar = data.get("opportunityRadar", {})
    return {
        "businessDate": radar.get("businessDate", "待核验"),
        "marketGate": radar.get("marketGate", "数据不足"),
        "dataHealth": radar.get("dataHealth", "灰灯"),
        "coverage": radar.get("coverage", 0),
        "executionStatus": radar.get("executionStatus", "灰灯"),
        "executionBoundary": radar.get("executionBoundary", "不形成买卖指令。"),
        "industries": radar.get("industries", [])[:10],
        "funds": radar.get("funds", []),
    }


def dashboard_coded_opportunity_radar(data: dict) -> dict:
    """Return only the display-safe coded Module 7 research contract."""
    radar = data.get("codedOpportunityRadar", {})
    fields = (
        "code", "name", "assetType", "theme", "researchStatus", "executionEligible",
        "executionAction", "actionRationale", "nextTrigger", "invalidCondition",
        "dataDate", "dataStatus",
    )
    relationship_fields = (
        "stockCodes", "etfCode", "relationship", "expressionStrategy", "relationshipStatus",
    )
    return {
        "businessDate": radar.get("businessDate", data.get("v2", {}).get("businessDate", "待核验")),
        "marketGate": radar.get("marketGate", data.get("v2", {}).get("marketGate", "数据不足")),
        "dataHealth": radar.get("dataHealth", data.get("v2", {}).get("dataHealth", "灰灯")),
        "executionEngineStatus": radar.get("executionEngineStatus", "未启用"),
        "executionBoundary": radar.get("executionBoundary", "执行引擎未启用；不形成交易动作。"),
        "stocks": [{key: item.get(key) for key in fields} for item in radar.get("stocks", [])],
        "etfs": [{key: item.get(key) for key in fields} for item in radar.get("etfs", [])],
        "relationships": [
            {key: item.get(key) for key in relationship_fields}
            for item in radar.get("relationships", [])
        ],
    }


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract = data["v2"]
    daily = data["daily"]
    opportunity_radar = dashboard_opportunity_radar(data)
    coded_opportunity_radar = dashboard_coded_opportunity_radar(data)

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
    market_meaning = {
        "巴菲特 / Berkshire Hathaway": "偏防守；高估值阶段不要追涨。",
        "霍华德·马克斯 / Oaktree": "偏谨慎；检查AI与成长资产是否过热。",
        "比尔·阿克曼 / Pershing Square": "选择性偏多，但估值必须合理。",
        "克里斯·霍恩 / TCI": "长期偏多高壁垒企业，不支持无差别追涨。",
        "雷·达里奥 / Bridgewater": "偏防守与分散，关注债务和货币周期。",
        "大卫·泰珀 / Appaloosa": "偏进攻，但只适合观察高弹性资产的交易节奏。",
        "斯坦利·德鲁肯米勒 / Duquesne": "长期认可AI，短期反对拥挤追高。",
        "高瓴 / 张磊": "作为中国成长价值和产业研究坐标，重点看盈利兑现。",
        "肯·格里芬 / Citadel": "用于观察流动性、波动率和市场结构，不作方向性跟单。",
        "凯瑟琳·伍德 / ARK": "作为高波动成长和创新资产情绪指标，不作组合模板。",
    }
    expert_details = [
        {
            "name": x.get("name", "待核验机构"),
            "strength": x.get("strength", "待核验"),
            "stance": x.get("stance", "待核验"),
            "style": x.get("style", "待核验"),
            "focus": x.get("assets", "待核验"),
            "meaning": market_meaning.get(x.get("name", ""), x.get("view", "待核验")),
            "detail": x.get("view", "待核验"),
            "sourceStatus": x.get("refreshStatus", "待核验"),
        }
        for x in experts
    ]
    tracking_experts = [x for x in expert_details if "跟踪" in str(x.get("stance", "")) or "待验证" in str(x.get("stance", ""))]
    verified_new_experts = [
        x for x in expert_details
        if "无新增" not in str(x.get("stance", "")) and x not in tracking_experts
    ]
    strong_experts = [x for x in expert_details if x.get("strength") in {"高", "中高"}]
    evidence = {
        "count": len(experts),
        "newCount": len(verified_new_experts),
        "trackingCount": len(tracking_experts),
        "strongCount": len(strong_experts),
        "independentBuyCount": 0,
        "leading": [x["name"] for x in experts if x.get("strength") == "高"][:3],
        "note": "机构观点只作佐证，不能独立触发买入。",
        "details": expert_details,
        "strongDetails": strong_experts,
        "trackingDetails": tracking_experts,
        "verifiedNewDetails": verified_new_experts,
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
        {"code": "03", "name": "跨市验证", "state": "仅佐证", "tone": "gray", "desc": f"{evidence['trackingCount']}项待验证"},
        {"code": "04", "name": "重大事件", "state": "已刷新", "tone": "green", "desc": "影响前10"},
        {"code": "05", "name": "持仓研究", "state": "已刷新", "tone": "green", "desc": "2股 / 12基"},
        {"code": "06", "name": "新机会雷达", "state": opportunity_radar["executionStatus"], "tone": "gray", "desc": "仅研究 / 不执行"},
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
    output += "export const opportunityRadar: { businessDate: string; marketGate: string; dataHealth: string; coverage: number; executionStatus: string; executionBoundary: string; industries: Array<{ name: string; score: number | string; tier: string; operation: string; marketDate: string; nextSignal: string }>; funds: Array<{ code: string; name: string; theme: string; latestNav: number | string; day: number | string; navDate: string; decision: string }> } = "
    output += f"{dump(opportunity_radar)};\n\n"
    output += "export const codedOpportunityRadar: { businessDate: string; marketGate: string; dataHealth: string; executionEngineStatus: string; executionBoundary: string; stocks: Array<{ code: string; name: string; assetType: string; theme: string; researchStatus: string; executionEligible: boolean; executionAction: string | null; actionRationale: string; nextTrigger: string; invalidCondition: string; dataDate: string | null; dataStatus: string }>; etfs: Array<{ code: string; name: string; assetType: string; theme: string; researchStatus: string; executionEligible: boolean; executionAction: string | null; actionRationale: string; nextTrigger: string; invalidCondition: string; dataDate: string | null; dataStatus: string }>; relationships: Array<{ stockCodes: string[]; etfCode: string; relationship: string; expressionStrategy: string | null; relationshipStatus: string }> } = "
    output += f"{dump(coded_opportunity_radar)};\n\n"
    TARGET.write_text(output, encoding="utf-8")
    print(f"Generated {TARGET.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
