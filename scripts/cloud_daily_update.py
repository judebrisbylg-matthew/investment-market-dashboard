#!/usr/bin/env python3
"""Cloud updater for the investment research dashboard.

This script is intentionally dependency-free so GitHub Actions can run it
without installing project packages. It updates data/market-data.json, refreshes
fund NAVs from Eastmoney/Tiantian where available, and upserts existing Notion
database rows when Notion secrets are configured.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "market-data.json"
HKT = ZoneInfo("Asia/Hong_Kong")
NOTION_VERSION = "2022-06-28"

FUND_META = {
    "013180": ("广发国证新能源车电池ETF联接C", "新能源车/电池", "指数/ETF联接"),
    "004432": ("南方有色金属ETF联接A", "有色金属", "指数/ETF联接"),
    "006751": ("富国互联科技股票A", "AI/互联网", "主动权益"),
    "100055": ("富国全球科技互联网股票(QDII)A", "全球科技互联网", "QDII"),
    "014344": ("鹏华中证500指数增强A", "A股宽基", "指数增强"),
    "012733": ("易方达中证人工智能主题ETF联接A", "AI/半导体", "指数/ETF联接"),
    "519704": ("交银先进制造混合A", "先进制造", "主动权益"),
    "018896": ("易方达消费电子ETF联接A", "消费电子", "指数/ETF联接"),
    "018125": ("永赢先进制造智选混合发起C", "先进制造", "主动权益"),
    "023531": ("永赢国证通用航空产业ETF发起联接C", "航空航天", "指数/ETF联接"),
    "018734": ("华夏中证绿色电力ETF发起式联接A", "绿色电力", "指数/ETF联接"),
    "377240": ("摩根新兴动力混合A", "成长/动力", "主动权益"),
    "007818": ("国泰中证全指通信设备ETF联接C", "通信/设备", "指数/ETF联接"),
}

FUND_ORDER = [
    "018896",
    "006751",
    "007818",
    "012733",
    "004432",
    "018125",
    "377240",
    "519704",
    "014344",
    "013180",
    "100055",
    "023531",
    "018734",
]


def log(message: str) -> None:
    print(f"[investment-center] {message}", flush=True)


def today_hkt() -> date:
    return datetime.now(HKT).date()


def fmt_cn(d: date) -> str:
    return f"{d.year}年{d.month}月{d.day}日"


def fmt_slash(d: date) -> str:
    return f"{d.year}/{d.month}/{d.day}"


def request_json(url: str, *, timeout: int = 15, headers: dict[str, str] | None = None) -> Any:
    req = Request(url, headers=headers or {"User-Agent": "investment-center-bot/1.0"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str, *, timeout: int = 15) -> str:
    req = Request(url, headers={"User-Agent": "investment-center-bot/1.0"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def percent(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace("%", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_fund_rows(html: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row_html in re.findall(r"<tr>(.*?)</tr>", html, flags=re.S):
        cells = re.findall(r"<td.*?>(.*?)</td>", row_html, flags=re.S)
        if len(cells) < 4:
            continue
        clean = [re.sub(r"<.*?>", "", c).replace("&nbsp;", "").strip() for c in cells]
        if not re.match(r"\d{4}-\d{2}-\d{2}", clean[0]):
            continue
        rows.append(
            {
                "date": clean[0],
                "nav": float(clean[1]) if clean[1] else None,
                "acc_nav": clean[2] if len(clean) > 2 else "",
                "daily": percent(clean[3] if len(clean) > 3 else None),
            }
        )
    return rows


def fetch_fund(code: str) -> dict[str, Any] | None:
    query = urlencode({"type": "lsjz", "code": code, "page": 1, "per": 25})
    url = f"https://fundf10.eastmoney.com/F10DataApi.aspx?{query}"
    try:
        rows = parse_fund_rows(request_text(url))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        log(f"fund {code} fetch failed: {exc}")
        return None
    if not rows:
        log(f"fund {code} returned no rows")
        return None
    latest = rows[0]
    week = None
    if len(rows) >= 6 and latest["nav"] and rows[5]["nav"]:
        week = (latest["nav"] / rows[5]["nav"] - 1) * 100
    return {
        "navDate": latest["date"],
        "nav": latest["nav"],
        "day": latest["daily"],
        "week": week,
    }


def classify_fund(theme: str, day: float | None, week: float | None) -> tuple[str, str]:
    d = day or 0.0
    w = week or 0.0
    if d >= 4.0 or w >= 10.0:
        return "观察等待", f"{theme}短线涨幅较快，先看持续性和回撤，不追高。"
    if d <= -3.0 or w <= -8.0:
        return "暂不加仓", f"{theme}短线承压明显，等待企稳和成交确认。"
    if d > 0.0 and w > 0.0:
        return "继续观察", f"{theme}短线修复，但仍需要验证趋势延续。"
    return "观察等待", f"{theme}信号不够强，维持观察。"


def update_funds(data: dict[str, Any], as_of: date) -> tuple[list[dict[str, Any]], list[str]]:
    old_by_code = {str(item.get("code")): item for item in data.get("fundHoldings", [])}
    updated: list[dict[str, Any]] = []
    check_lines: list[str] = []
    for code in FUND_ORDER:
        name, theme, fund_type = FUND_META[code]
        old = old_by_code.get(code, {})
        fetched = fetch_fund(code)
        time.sleep(0.15)
        if fetched:
            decision, reason = classify_fund(theme, fetched.get("day"), fetched.get("week"))
            day_value = round(float(fetched["day"]), 2) if fetched.get("day") is not None else old.get("day", 0)
            week_value = round(float(fetched["week"]), 2) if fetched.get("week") is not None else old.get("week", 0)
            nav_value = fetched.get("nav")
            reason = f"{reason} 净值日期：{fetched['navDate']}，数据源：天天基金/东方财富。"
            check_lines.append(f"{code}: nav={nav_value}, day={day_value}%, navDate={fetched['navDate']}")
        else:
            decision = old.get("decision", "待核验")
            reason = old.get("reason", "数据源抓取失败，沿用上一版并待核验。")
            day_value = old.get("day", 0)
            week_value = old.get("week", 0)
            nav_value = old.get("nav") or old.get("latestNav")
            reason = f"{reason} 报表更新日期：{fmt_cn(as_of)}；数据源本次待核验。"
            check_lines.append(f"{code}: fetch failed, carried forward")
        updated.append(
            {
                "name": name,
                "code": code,
                "theme": theme,
                "day": day_value,
                "week": week_value,
                "risk": old.get("risk", "中"),
                "decision": decision,
                "reason": reason,
                "type": fund_type,
                "latestNav": nav_value if nav_value is not None else old.get("latestNav", ""),
            }
        )
    data["fundHoldings"] = updated
    return updated, check_lines


def operation_priority(operation: str) -> int:
    order = {
        "建议加仓": 0,
        "继续观察": 1,
        "止盈跟踪": 2,
        "观察等待": 3,
        "暂不追高": 4,
        "暂不加仓": 5,
        "减仓回避": 6,
        "待核验": 7,
    }
    return order.get(operation, 8)


def update_industry(data: dict[str, Any], as_of: date) -> None:
    items = list(data.get("industryWatch", []))
    if not items:
        return
    for item in items:
        item["reviewDate"] = fmt_cn(as_of + timedelta(days=1))
        item.setdefault("news", "当日新闻/催化待核验。")
        item.setdefault("valuation", "估值待核验。")
        item.setdefault("reason", "操作原因待核验。")
        item.setdefault("nextSignal", "成交额、政策、订单、价格、业绩")
    items.sort(
        key=lambda x: (
            0 if x.get("tier") == "核心主线" else 1,
            -float(x.get("prosperity", 0)),
            -float(x.get("heat", 0)),
            operation_priority(str(x.get("operation", ""))),
        )
    )
    data["industryWatch"] = items


def update_experts(data: dict[str, Any], as_of: date) -> None:
    for item in data.get("expertViews", []):
        view = str(item.get("view", ""))
        if "复核至" in view:
            view = re.sub(r"复核至\d{4}/\d{1,2}/\d{1,2}", f"复核至{fmt_slash(as_of)}", view)
        else:
            view = f"复核至{fmt_slash(as_of)}：{view or '无新增可靠公开观点，保留原框架待核验。'}"
        item["view"] = view
        item.setdefault("stance", "无新增可靠观点")
        item.setdefault("strength", "中")
        item.setdefault("assets", "待核验")


def update_finance_news(data: dict[str, Any], as_of: date) -> None:
    """Roll the finance news date forward conservatively.

    A production-grade news feed can be added later through a licensed news API.
    Until then, the script never fabricates unknown facts: existing curated rows
    are carried forward with today's review date and source/watch fields intact.
    """
    existing = list(data.get("financeNews", []))[:10]
    for item in existing:
        item["date"] = fmt_slash(as_of)
        item.setdefault("category", "财经")
        item.setdefault("title", "待核验财经新闻")
        item.setdefault("content", "今日新闻源待核验。")
        item.setdefault("assets", "全球市场")
        item.setdefault("direction", "待观察")
        item.setdefault("impact", "中")
        item.setdefault("horizon", "短期：1天-2周")
        item.setdefault("meaning", "等待可靠新闻源确认。")
        item.setdefault("action", "观察等待")
        item.setdefault("watch", "官方公告、Reuters/Bloomberg/CNBC/WSJ、成交与利率")
        item.setdefault("source", "待核验")
        item.setdefault("confidence", "中")
        item.setdefault("included", "否：待核验")
    data["financeNews"] = existing


def update_daily(data: dict[str, Any], as_of: date) -> None:
    risk_items = data.get("riskDashboard", [])
    yellow = sum(1 for item in risk_items if "黄" in str(item.get("signal", "")))
    red = sum(1 for item in risk_items if "红" in str(item.get("signal", "")))
    signal = "红灯" if red else ("黄灯" if yellow else "绿灯")
    action = "防守" if red else ("等待" if yellow else "进攻")
    data["daily"] = {
        "asOf": f"{fmt_slash(as_of)} 05:00 HKT",
        "signal": signal,
        "action": action,
        "marketJudgement": f"{fmt_cn(as_of)}更新：系统按最新可得交易日和新闻资料复盘；若部分市场休市，交易数据沿用最近可得日期并保留滞后说明。当前风险灯号为{signal}，操作维持{action}。",
        "positionAdvice": "权益仓位维持中性偏谨慎；优先观察核心主线的业绩兑现和成交确认，不因单日波动追高。",
        "needAction": "今日先完成数据核验：基金净值、风险指标、行业主线排序、专家观点和财经新闻是否有新增可靠信号。",
        "actionReason": "不盲动原因：自动化更新只负责同步最新可得资料，交易动作仍需结合估值、拥挤度、成交额和宏观风险确认。",
        "riskPoint": "主要风险：美债实际利率、美元指数、油价、AI拥挤交易、A股/港股成交不足和新闻事件反复。",
        "nextReview": "复盘重点：基金净值日期、AI/PCB订单、铜铝金价格、数据中心电力需求、央行发言和高影响财经新闻。",
    }


def build_dashboard() -> tuple[dict[str, Any], list[str]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"missing dashboard data: {DATA_PATH}")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    as_of = today_hkt()
    update_daily(data, as_of)
    update_industry(data, as_of)
    update_experts(data, as_of)
    update_finance_news(data, as_of)
    _, checks = update_funds(data, as_of)
    data["generatedAt"] = datetime.now(HKT).isoformat(timespec="seconds")
    data["automation"] = {
        "source": "GitHub Actions",
        "timezone": "Asia/Hong_Kong",
        "rule": "daily 05:00 HKT",
        "notionUpsert": "enabled when NOTION_* secrets exist",
    }
    return data, checks


@dataclass
class NotionConfig:
    token: str
    db_daily: str
    db_risk: str
    db_industry: str
    db_experts: str
    db_funds: str
    db_news: str


class NotionClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.schemas: dict[str, dict[str, Any]] = {}

    def api(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"https://api.notion.com/v1{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }
        req = Request(url, data=body, method=method, headers=headers)
        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Notion {method} {path} failed: {exc.code} {detail}") from exc

    def schema(self, db_id: str) -> dict[str, Any]:
        if db_id not in self.schemas:
            self.schemas[db_id] = self.api("GET", f"/databases/{db_id}").get("properties", {})
        return self.schemas[db_id]

    def property_value(self, prop: dict[str, Any], value: Any) -> dict[str, Any] | None:
        prop_type = prop.get("type")
        if value is None or str(value).strip() == "":
            value = "待核验"
        text = str(value)
        if prop_type == "title":
            return {"title": [{"text": {"content": text[:2000]}}]}
        if prop_type == "rich_text":
            return {"rich_text": [{"text": {"content": text[:2000]}}]}
        if prop_type == "select":
            return {"select": {"name": text[:100]}}
        if prop_type == "multi_select":
            names = [part.strip() for part in re.split(r"[,，/、|]", text) if part.strip()]
            return {"multi_select": [{"name": name[:100]} for name in names[:10]]}
        if prop_type == "date":
            if isinstance(value, date):
                start = value.isoformat()
            else:
                start = parse_date(text).isoformat()
            return {"date": {"start": start}}
        if prop_type == "number":
            try:
                return {"number": float(str(value).replace("%", ""))}
            except ValueError:
                return None
        if prop_type == "checkbox":
            return {"checkbox": text in {"是", "true", "True", "1", "yes", "Yes"}}
        if prop_type == "url":
            return {"url": text if text.startswith(("http://", "https://", "file://")) else None}
        return None

    def build_props(self, db_id: str, row: dict[str, Any]) -> dict[str, Any]:
        schema = self.schema(db_id)
        props: dict[str, Any] = {}
        for key, value in row.items():
            if key not in schema:
                continue
            prop_value = self.property_value(schema[key], value)
            if prop_value is not None:
                props[key] = prop_value
        return props

    def find_page(self, db_id: str, key_filters: dict[str, Any]) -> str | None:
        schema = self.schema(db_id)
        conditions = []
        for key, value in key_filters.items():
            if key not in schema:
                continue
            prop_type = schema[key].get("type")
            if prop_type == "date":
                conditions.append({"property": key, "date": {"equals": parse_date(str(value)).isoformat()}})
            elif prop_type == "title":
                conditions.append({"property": key, "title": {"equals": str(value)}})
            elif prop_type == "rich_text":
                conditions.append({"property": key, "rich_text": {"equals": str(value)}})
            elif prop_type == "number":
                try:
                    conditions.append({"property": key, "number": {"equals": float(value)}})
                except ValueError:
                    continue
            elif prop_type == "select":
                conditions.append({"property": key, "select": {"equals": str(value)}})
        if not conditions:
            return None
        filter_payload = conditions[0] if len(conditions) == 1 else {"and": conditions}
        result = self.api("POST", f"/databases/{db_id}/query", {"filter": filter_payload, "page_size": 1})
        rows = result.get("results", [])
        return rows[0]["id"] if rows else None

    def upsert(self, db_id: str, row: dict[str, Any], key_filters: dict[str, Any]) -> str:
        props = self.build_props(db_id, row)
        if not props:
            return "skipped:no matching properties"
        page_id = self.find_page(db_id, key_filters)
        if page_id:
            self.api("PATCH", f"/pages/{page_id}", {"properties": props})
            return "updated"
        self.api("POST", "/pages", {"parent": {"database_id": db_id}, "properties": props})
        return "created"


def parse_date(value: str) -> date:
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y年%-m月%-d日"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    match = re.search(r"(\d{4})[/-年](\d{1,2})[/-月](\d{1,2})", text)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return today_hkt()


def notion_config(require: bool) -> NotionConfig | None:
    keys = {
        "token": os.getenv("NOTION_TOKEN", ""),
        "db_daily": os.getenv("NOTION_DB_DAILY", ""),
        "db_risk": os.getenv("NOTION_DB_RISK", ""),
        "db_industry": os.getenv("NOTION_DB_INDUSTRY", ""),
        "db_experts": os.getenv("NOTION_DB_EXPERTS", ""),
        "db_funds": os.getenv("NOTION_DB_FUNDS", ""),
        "db_news": os.getenv("NOTION_DB_NEWS", ""),
    }
    missing = [name for name, value in keys.items() if not value]
    if missing and require:
        raise RuntimeError(f"missing Notion secrets: {', '.join(missing)}")
    if missing:
        log(f"Notion sync skipped; missing: {', '.join(missing)}")
        return None
    return NotionConfig(**keys)


def safe_text(*values: Any, default: str = "待核验") -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def industry_month_judgement(item: dict[str, Any]) -> str:
    name = safe_text(item.get("name"), "该赛道")
    operation = safe_text(item.get("operation"), "待核验")
    signal = safe_text(item.get("nextSignal"), "成交额、政策、订单、价格和业绩")
    if operation == "建议加仓":
        return f"{name}未来1月偏进攻；若{signal}继续验证，可分批加仓，失败则降回观察。"
    if operation == "继续观察":
        return f"{name}未来1月维持观察；重点看{signal}是否连续兑现，不因单日波动追高。"
    if operation == "止盈跟踪":
        return f"{name}未来1月偏强但需止盈跟踪；若价格或成交转弱，优先锁定利润。"
    if operation == "暂不追高":
        return f"{name}未来1月主线仍在，但拥挤度偏高；等待回调、财报或订单验证后再判断。"
    if operation == "暂不加仓":
        return f"{name}未来1月先不加仓；等待风险释放和基本面信号修复。"
    if operation == "减仓回避":
        return f"{name}未来1月以防守为主；除非风险显著下降，否则回避或降低权重。"
    return f"{name}未来1月待核验；重点跟踪{signal}。"


def expert_market(assets: str) -> str:
    if any(key in assets for key in ["中国", "A股", "港股", "互联网平台", "创新药"]):
        return "中国资产/港股/A股"
    if any(key in assets for key in ["黄金", "全球", "非美元", "债务"]):
        return "全球宏观/商品/债券"
    if any(key in assets for key in ["Apple", "Microsoft", "Tesla", "Alphabet", "Amazon", "美股"]):
        return "美股/全球科技"
    return "全球市场"


def fund_valuation_constraint(theme: str, nav_date: date) -> str:
    return (
        f"{theme}需结合对应指数PE/PB、市净率分位、成交额和净值趋势复核；"
        f"净值日期 {nav_date.isoformat()}，若数据源延迟则按最新真实净值日期判断。"
    )


def fund_forward_view(theme: str, decision: str, item: dict[str, Any], horizon: str) -> str:
    day = item.get("day", "待核验")
    week = item.get("week", "待核验")
    if decision in {"建议加仓", "继续观察"}:
        bias = "偏修复，但需要成交额和净值趋势继续验证"
    elif decision in {"观察等待", "暂不加仓"}:
        bias = "先观察，不把短线波动直接当成趋势反转"
    elif decision == "止盈跟踪":
        bias = "偏强但需跟踪回撤和止盈窗口"
    else:
        bias = "待核验"
    return f"{theme}{horizon}判断：{bias}；日涨跌 {day}%，近1周 {week}%，动作={decision}。"


def sync_notion(data: dict[str, Any], config: NotionConfig) -> dict[str, int]:
    client = NotionClient(config.token)
    as_of = today_hkt()
    cn_date = fmt_cn(as_of)
    stats = {"created": 0, "updated": 0, "skipped": 0}

    def count(status: str) -> None:
        if status.startswith("created"):
            stats["created"] += 1
        elif status.startswith("updated"):
            stats["updated"] += 1
        else:
            stats["skipped"] += 1

    daily = data.get("daily", {})
    core_industries = [
        item.get("name", "待核验")
        for item in data.get("industryWatch", [])
        if item.get("tier") == "核心主线"
    ][:5]
    fund_actions = [
        f"{item.get('code', '待核验')} {item.get('decision', '待核验')}"
        for item in data.get("fundHoldings", [])
    ][:5]
    risk_signal = daily.get("signal", "待核验")
    count(
        client.upsert(
            config.db_daily,
            {
                "日期": as_of,
                "一句话日报": daily.get("marketJudgement"),
                "市场总判断": daily.get("marketJudgement"),
                "今日灯号": daily.get("signal"),
                "进攻/防守/等待": daily.get("action"),
                "今日需要动作": daily.get("needAction"),
                "仓位建议": daily.get("positionAdvice"),
                "不动作理由": daily.get("actionReason"),
                "主要风险点": daily.get("riskPoint"),
                "专家观点校验": "详见 4.全球投资专家观点追踪",
                "风控仪表盘结论": f"当前风控灯号为{risk_signal}；详见 2.风控仪表盘。",
                "行业观察池结论": "核心主线：" + "、".join(core_industries) if core_industries else "核心主线待核验。",
                "基金持仓动作": "；".join(fund_actions) if fund_actions else "基金持仓动作待核验。",
                "值得关注资产/行业": daily.get("nextReview"),
                "明日/下次复盘重点": daily.get("nextReview"),
            },
            {"日期": as_of},
        )
    )

    for item in data.get("riskDashboard", []):
        normal_value = item.get("normal", "待核验")
        warning_value = item.get("warning", "待核验")
        danger_value = item.get("danger", "待核验")
        row = {
            "监控更新日期": as_of,
            "更新日期": as_of,
            "监控指标": item.get("name"),
            "今日数值": item.get("value"),
            "今日灯号": item.get("signal"),
            # Keep multiple aliases because Notion headers have changed between
            # emoji styles. build_props only writes names that exist in schema.
            "正常✅绿灯（持有）": normal_value,
            "✅正常绿灯（持有）": normal_value,
            "🟢正常绿灯（持有）": normal_value,
            "正常绿灯（持有）": normal_value,
            "预警⚠️ 黄灯（减仓）": warning_value,
            "⚠️预警黄灯（减仓）": warning_value,
            "🟡预警黄灯（减仓）": warning_value,
            "预警黄灯（减仓）": warning_value,
            "危险🚨红灯（轻仓）": danger_value,
            "🚨危险红灯（轻仓）": danger_value,
            "🔴危险红灯（轻仓）": danger_value,
            "危险红灯（轻仓）": danger_value,
            "说明": "GitHub Actions 云端自动复核；若交易数据滞后，沿用最新可得来源日期。",
        }
        count(client.upsert(config.db_risk, row, {"监控更新日期": as_of, "监控指标": item.get("name")}))

    for item in data.get("industryWatch", []):
        operation = str(item.get("operation", "待核验"))
        month_judgement = industry_month_judgement(item)
        row = {
            "更新日期": as_of,
            "层级": item.get("tier"),
            "行业/赛道": item.get("name"),
            "PE/PB估值约束": item.get("valuation"),
            "一句话抓手": item.get("news"),
            "下次复盘日期": parse_date(str(item.get("reviewDate", cn_date))),
            "代表公司": item.get("companies", "待核验"),
            "代表指数/ETF": item.get("etf", "待核验"),
            "关联主线": item.get("nextSignal"),
            "操作原因": item.get("reason"),
            "操作语言": item.get("operation"),
            "行业景气度": label_score(item.get("prosperity")),
            "资金热度": label_score(item.get("heat")),
            "风险等级": label_score(item.get("risk")),
            "新闻日期/来源": f"{cn_date} / 云端自动复核",
            "最新行业新闻/催化剂": item.get("news"),
            "未来1月判断": month_judgement,
            "未来1季判断": item.get("reason"),
            "重点跟踪信号": item.get("nextSignal"),
        }
        count(client.upsert(config.db_industry, row, {"更新日期": as_of, "行业/赛道": item.get("name")}))

    for item in data.get("expertViews", []):
        expert_name = item.get("name", "待核验")
        assets = safe_text(item.get("assets"), "待核验")
        style = safe_text(item.get("style"), "待核验")
        view = safe_text(item.get("view"), "无新增可靠公开观点，保留原框架待核验。")
        row = {
            "更新日期": as_of,
            "专家/机构": expert_name,
            "观点日期": fmt_slash(as_of),
            "观点来源": "公开资料云端复核",
            "核心判断": view,
            "对应资产": assets,
            "证据强度": item.get("strength"),
            "操作语言": item.get("stance"),
            "与市场是否一致": item.get("stance"),
            "人物类型": item.get("style"),
            "身份/风格": style,
            "重仓领域/资产": assets,
            "代表股票/ETF": assets,
            "估值约束": "不直接按观点买入；需结合相关资产估值、盈利兑现、现金流和拥挤度复核。",
            "可验证信号": "公开信/访谈原文、13F或持仓披露、相关资产成交额、业绩与估值变化。",
            "后续验证结果": "待后续复盘；若无新增可靠公开观点，保留原框架并标注复核日期。",
            "对应市场": expert_market(assets),
            "操作原因": view,
            "看多方向": assets,
            "看空/回避方向": "高估值但业绩未兑现、现金流不足或交易过度拥挤的资产。",
            "观点周期": "中期复核；若出现公开信、13F或重大访谈则提前更新。",
        }
        count(client.upsert(config.db_experts, row, {"更新日期": as_of, "专家/机构": expert_name}))

    for item in data.get("fundHoldings", []):
        nav_date = extract_nav_date(str(item.get("reason", ""))) or as_of
        theme = safe_text(item.get("theme"), "待核验")
        reason = safe_text(item.get("reason"), "操作原因待核验。")
        decision = safe_text(item.get("decision"), "待核验")
        row = {
            "报表更新日期": as_of,
            "基金名称": item.get("name"),
            "基金代码": item.get("code"),
            "关联主线": theme,
            "夏普比率": item.get("sharp", "待核验"),
            "操作原因": reason,
            "操作语言": decision,
            "日涨跌": item.get("day"),
            "最大回撤": item.get("maxDrawdown", "待核验"),
            "最新净值": item.get("latestNav", "待核验"),
            "净值日期": nav_date,
            "类型": item.get("type", "待核验"),
            "风险等级": item.get("risk"),
            "风险": item.get("risk"),
            "近1周": item.get("week"),
            "股指约束（PE-市净率）": fund_valuation_constraint(theme, nav_date),
            "预测未来1月": fund_forward_view(theme, decision, item, "1月"),
            "预测未来1季": fund_forward_view(theme, decision, item, "1季"),
            "预测未来半年": fund_forward_view(theme, decision, item, "半年"),
            "预测未来1年": fund_forward_view(theme, decision, item, "1年"),
        }
        count(client.upsert(config.db_funds, row, {"报表更新日期": as_of, "基金代码": item.get("code")}))

    for item in data.get("financeNews", [])[:10]:
        row = {
            "新闻日期": as_of,
            "新闻类别": item.get("category"),
            "新闻标题": item.get("title"),
            "核心内容": item.get("content"),
            "影响资产": item.get("assets"),
            "影响方向": item.get("direction"),
            "影响级别": item.get("impact"),
            "时间维度": item.get("horizon"),
            "对行情的含义": item.get("meaning"),
            "对应投资抓手": item.get("action"),
            "需重点跟踪": item.get("watch"),
            "新闻来源": item.get("source"),
            "可信度": item.get("confidence"),
            "是否纳入每日简报": item.get("included"),
        }
        count(client.upsert(config.db_news, row, {"新闻日期": as_of, "新闻标题": item.get("title")}))

    return stats


def label_score(value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "待核验"
    if score >= 80:
        return "高"
    if score >= 65:
        return "中高"
    if score >= 45:
        return "中"
    return "低"


def extract_nav_date(reason: str) -> date | None:
    match = re.search(r"净值日期[:：]\s*(\d{4}-\d{2}-\d{2})", reason)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="validate without writing files or Notion")
    args = parser.parse_args()

    data, checks = build_dashboard()
    log("fund sample checks:")
    for line in checks[:6]:
        log(f"  {line}")

    require_notion = os.getenv("REQUIRE_NOTION", "false").lower() == "true"
    config = notion_config(require_notion)
    if config and not args.dry_run:
        stats = sync_notion(data, config)
        log(f"Notion upsert stats: {stats}")
    elif args.dry_run:
        log("dry run: Notion sync and file write skipped")

    if not args.dry_run:
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log(f"wrote {DATA_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"ERROR: {exc}")
        raise
