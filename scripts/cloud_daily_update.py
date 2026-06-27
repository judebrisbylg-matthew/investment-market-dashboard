#!/usr/bin/env python3
"""Cloud updater for the investment research dashboard.

This script is intentionally dependency-free so GitHub Actions can run it
without installing project packages. It updates data/market-data.json, refreshes
fund NAVs from Eastmoney/Tiantian where available, and upserts existing Notion
database rows when Notion secrets are configured.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET
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
    "025856": ("华夏中证电网设备主题ETF发起式联接A", "电网设备", "指数/ETF联接"),
    "377240": ("摩根新兴动力混合A", "成长/动力", "主动权益"),
    "007818": ("国泰中证全指通信设备ETF联接C", "通信/设备", "指数/ETF联接"),
}

FUND_RISK = {
    "006751": "中高",
    "018125": "高",
    "023531": "中",
    "018734": "中",
    "025856": "中高",
    "377240": "中",
    "007818": "高",
    "018896": "中高",
    "013180": "中",
    "004432": "中高",
    "100055": "中高",
    "014344": "中",
    "012733": "高",
    "519704": "中",
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
    "025856",
]

NEWS_FEEDS = [
    ("Google News Macro", "https://news.google.com/rss/search?q=Federal%20Reserve%20OR%20inflation%20OR%20Treasury%20yields%20OR%20oil%20OR%20China%20economy%20OR%20AI%20chips%20when%3A1d&hl=en-US&gl=US&ceid=US:en"),
    ("Google News Markets", "https://news.google.com/rss/search?q=stock%20market%20OR%20dollar%20OR%20bond%20market%20OR%20Brent%20oil%20OR%20semiconductor%20when%3A1d&hl=en-US&gl=US&ceid=US:en"),
    ("CNBC Markets", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("CNBC Economy", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml"),
]

NEWS_KEYWORDS = {
    "央行": ["fed", "federal reserve", "rate", "powell", "inflation", "central bank", "ecb", "boj", "yield"],
    "能源": ["oil", "brent", "wti", "opec", "energy", "gas"],
    "科技": ["ai", "chip", "semiconductor", "nvidia", "micron", "tesla", "apple", "microsoft", "data center"],
    "中国资产": ["china", "hong kong", "yuan", "renminbi", "beijing", "tariff"],
    "地缘": ["iran", "israel", "war", "g7", "geopolitical", "shipping"],
    "贸易": ["trade", "tariff", "export", "import", "deal"],
    "风险事件": ["credit", "debt", "default", "liquidity", "bank", "selloff", "recession"],
}

NEWS_IMPACT_WORDS = [
    "fed",
    "federal reserve",
    "rate",
    "inflation",
    "oil",
    "brent",
    "war",
    "china",
    "tariff",
    "ai",
    "chip",
    "semiconductor",
    "yield",
    "dollar",
    "credit",
]

NEWS_CATEGORY_PRIORITY = {
    "地缘": 8,
    "央行": 7,
    "能源": 6,
    "风险事件": 5,
    "中国资产": 4,
    "科技": 3,
    "贸易": 2,
}

EXCLUDE_NEWS_TERMS = [
    "dies at age",
    "passing of",
    "trillionaire club",
    "reward for failure",
    "sports",
    "celebrity",
    "streaming guide",
    "slams into",
    "killing",
    "killed",
]

TRUSTED_NEWS_TERMS = [
    "Reuters",
    "Bloomberg",
    "CNBC",
    "Associated Press",
    "Wall Street Journal",
    "WSJ",
    "Barron's",
    "MarketWatch",
    "Financial Times",
    "Investing.com",
    "Yahoo Finance",
    "Federal Reserve",
    "NDTV Profit",
    "Nikkei",
    "South China Morning Post",
    "The Guardian",
    "天下",
]


def log(message: str) -> None:
    print(f"[investment-center] {message}", flush=True)


def today_hkt() -> date:
    return datetime.now(HKT).date()


def fmt_cn(d: date) -> str:
    return f"{d.year}年{d.month}月{d.day}日"


def fmt_slash(d: date) -> str:
    return f"{d.year}/{d.month}/{d.day}"


def normalize_key(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[，。；：、,.!?:;|/\\()（）【】\[\]\"'“”‘’\-—_]", "", text)
    return text


def status_date_text(source_date: date | None, as_of: date, *, prefix: str = "来源") -> str:
    if source_date is None:
        return f"{prefix}日期待核验"
    lag = (as_of - source_date).days
    if lag <= 0:
        return f"{prefix}日期 {source_date.isoformat()}，今日可用"
    return f"{prefix}日期 {source_date.isoformat()}，沿用最近可得数据（滞后{lag}天）"


def extract_source_date(text: str, as_of: date) -> date | None:
    if not text:
        return None
    patterns = [
        r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                return None
    cn = re.search(r"(\d{1,2})月(\d{1,2})日", text)
    if cn:
        try:
            return date(as_of.year, int(cn.group(1)), int(cn.group(2)))
        except ValueError:
            return None
    slash = re.search(r"\((\d{1,2})/(\d{1,2})", text)
    if slash:
        try:
            return date(as_of.year, int(slash.group(1)), int(slash.group(2)))
        except ValueError:
            return None
    loose_slash = re.search(r"(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)", text)
    if loose_slash:
        try:
            return date(as_of.year, int(loose_slash.group(1)), int(loose_slash.group(2)))
        except ValueError:
            return None
    return None


def request_json(url: str, *, timeout: int = 15, headers: dict[str, str] | None = None) -> Any:
    req = Request(url, headers=headers or {"User-Agent": "investment-center-bot/1.0"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str, *, timeout: int = 15) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 investment-center-bot/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml, text/html;q=0.8",
        },
    )
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


def annotate_risk_status(data: dict[str, Any], as_of: date) -> dict[str, Any]:
    items = data.get("riskDashboard", [])
    fresh = 0
    stale = 0
    unknown = 0
    for item in items:
        text = " ".join(str(item.get(key, "")) for key in ("value", "normal", "warning", "danger", "description"))
        source_date = extract_source_date(text, as_of)
        item["sourceDate"] = source_date.isoformat() if source_date else "待核验"
        item["refreshStatus"] = status_date_text(source_date, as_of, prefix="指标")
        if source_date is None:
            unknown += 1
        elif (as_of - source_date).days <= 1:
            fresh += 1
        else:
            stale += 1
    status = "真实刷新" if stale == 0 and unknown == 0 else "部分沿用/待核验"
    return {
        "status": status,
        "fresh": fresh,
        "stale": stale,
        "unknown": unknown,
        "note": f"{fresh}项接近当日，{stale}项沿用最近可得数据，{unknown}项来源日期待核验。",
    }


def parse_rss_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=HKT)
        return parsed.astimezone(HKT)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def clean_html_text(value: str) -> str:
    value = re.sub(r"<.*?>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def find_risk_item(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    for item in data.get("riskDashboard", []):
        if item.get("name") == name:
            return item
    return None


def risk_signal_from_threshold(value: float, normal: tuple[float, float] | None = None, *,
                               green_if_below: float | None = None,
                               green_if_above: float | None = None,
                               yellow_if_below: float | None = None) -> tuple[int, str]:
    if normal and normal[0] <= value <= normal[1]:
        return 35, "正常绿灯"
    if green_if_below is not None and value < green_if_below:
        return 35, "正常绿灯"
    if green_if_above is not None and value > green_if_above:
        return 35, "正常绿灯"
    if yellow_if_below is not None and value < yellow_if_below:
        return 72, "危险红灯"
    return 55, "预警黄灯"


def update_risk_market_data(data: dict[str, Any], as_of: date) -> None:
    """Refresh risk items that can be fetched reliably without paid data."""
    try:
        market = request_json(
            "https://push2.eastmoney.com/api/qt/ulist.np/get?"
            "fltt=2&fields=f2,f3,f6,f12,f14&secids=1.000001,0.399001,100.HSI,100.UDI",
            timeout=20,
        )
        rows = {str(row.get("f12")): row for row in market.get("data", {}).get("diff", [])}

        sh_amount = float(rows.get("000001", {}).get("f6") or 0)
        sz_amount = float(rows.get("399001", {}).get("f6") or 0)
        if sh_amount > 0 and sz_amount > 0:
            a_turnover = (sh_amount + sz_amount) / 1_000_000_000_000
            item = find_risk_item(data, "A股成交额")
            if item:
                score, signal = risk_signal_from_threshold(a_turnover, green_if_above=1.0, yellow_if_below=0.7)
                item.update(
                    {
                        "value": f"沪深两市成交约{a_turnover:.2f}万亿元（东方财富指数口径，{fmt_cn(as_of)}）",
                        "score": score,
                        "signal": signal,
                        "sourceDate": as_of.isoformat(),
                        "refreshStatus": f"东方财富指数成交额，{fmt_cn(as_of)}可用；沪深两市合计约{a_turnover:.2f}万亿元",
                    }
                )

        hsi_amount = float(rows.get("HSI", {}).get("f6") or 0)
        if hsi_amount > 0:
            hsi_turnover = hsi_amount / 100_000_000
            item = find_risk_item(data, "港股成交额")
            if item:
                # HSI turnover is not whole-market turnover, so keep it yellow unless a full-market source is added.
                item.update(
                    {
                        "value": f"恒生指数成分成交约{hsi_turnover:.0f}亿港元（非港股全市场口径，{fmt_cn(as_of)}）",
                        "score": 55,
                        "signal": "预警黄灯",
                        "sourceDate": as_of.isoformat(),
                        "refreshStatus": f"东方财富恒生指数成交口径，{fmt_cn(as_of)}可用；非港股全市场成交额，需继续核验",
                    }
                )

        dxy = float(rows.get("UDI", {}).get("f2") or 0)
        if dxy > 0:
            item = find_risk_item(data, "美元指数")
            if item:
                score, signal = risk_signal_from_threshold(dxy, green_if_below=103.0)
                item.update(
                    {
                        "value": f"DXY约{dxy:.2f}（东方财富美元指数口径，{fmt_cn(as_of)}）",
                        "score": score,
                        "signal": signal,
                        "sourceDate": as_of.isoformat(),
                        "refreshStatus": f"东方财富美元指数，{fmt_cn(as_of)}可用",
                    }
                )
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        log(f"risk market data refresh failed: {exc}")


def mostly_english_text(value: str) -> bool:
    text = value or ""
    latin = len(re.findall(r"[A-Za-z]", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return latin >= 18 and latin > cjk * 2


def chinese_source_label(source: str) -> str:
    source = source or ""
    if "Federal Reserve" in source:
        return "美联储官网"
    if "CNBC" in source:
        return "美国财经电视台"
    if "Google News" in source:
        return "公开新闻聚合源"
    return "公开财经新闻源"


def chinese_news_summary(title: str, content: str, category: str) -> dict[str, str]:
    text = f"{title} {content}".lower()
    if any(word in text for word in ["warsh", "fed", "federal reserve", "rate", "powell", "central bank", "yield"]):
        return {
            "title": "美联储政策与利率预期再受关注，市场等待官员表态和收益率确认",
            "content": "最新央行相关消息显示，利率路径、官员表态和美债收益率仍是影响全球风险偏好的核心变量。",
            "meaning": "若降息预期降温或实际利率上行，成长股和高估值资产会承压；若收益率回落，风险资产可能修复。",
            "watch": "美联储官员讲话、10年期美债收益率、实际利率、美元指数、黄金和纳指表现",
        }
    if any(word in text for word in ["iran", "israel", "war", "sanction", "g7", "shipping"]):
        return {
            "title": "中东与地缘风险仍在扰动市场，原油、黄金和风险偏好需要重点跟踪",
            "content": "地缘局势相关消息显示，停火、制裁、能源运输和政策表态仍可能影响原油供应预期与避险交易。",
            "meaning": "地缘风险若反复，油价和黄金波动会放大，并可能压制全球权益市场风险偏好。",
            "watch": "中东局势、原油运输、布伦特油价、黄金价格、美元指数和军工板块表现",
        }
    if any(word in text for word in ["oil", "brent", "wti", "opec", "energy", "gas"]):
        return {
            "title": "油价与能源供给变量继续影响通胀预期，资源品和风险偏好需同步观察",
            "content": "能源市场消息显示，原油价格、供给扰动和库存变化仍会影响通胀交易、资源品以及全球股市情绪。",
            "meaning": "油价快速上行会推升通胀压力并压制风险偏好；油价回落则有利于缓和成本压力。",
            "watch": "布伦特油价、美国原油库存、产油国政策、通胀预期、航空和化工板块",
        }
    if any(word in text for word in ["chip", "semiconductor", "nvidia", "micron", "cerebras", "ai", "data center"]):
        return {
            "title": "人工智能和半导体仍是市场主线，但高估值与拥挤交易需要财报验证",
            "content": "科技链条消息显示，人工智能硬件、芯片、数据中心和算力需求仍受关注，但市场开始更重视订单、毛利率和现金流。",
            "meaning": "主线仍在，但不适合只看概念追高；需要用财报、订单和成交额验证趋势强度。",
            "watch": "费半指数、英伟达链条、云厂资本开支、芯片订单、毛利率和成交额",
        }
    if any(word in text for word in ["smart glasses", "wearable", "meta", "apple", "consumer electronics"]):
        return {
            "title": "人工智能终端和消费电子催化升温，真实销量和供应链订单是关键",
            "content": "消费电子和可穿戴设备消息显示，科技公司继续争夺人工智能终端入口，相关供应链关注度上升。",
            "meaning": "终端创新利好消费电子情绪，但需要销量、备货、毛利率和应用场景兑现。",
            "watch": "智能眼镜销量、消费电子供应链订单、光学器件、芯片和终端厂商指引",
        }
    if any(word in text for word in ["tariff", "trade", "manufacturing", "export", "import"]):
        return {
            "title": "贸易和关税变量继续影响制造业利润，订单、成本和供应链风险需跟踪",
            "content": "贸易政策相关消息显示，关税和供应链安排仍可能影响制造业成本、订单节奏和企业利润预期。",
            "meaning": "若关税压力上升，制造业和工业链利润会承压；若政策缓和，风险偏好可能修复。",
            "watch": "关税政策、制造业订单、企业毛利率、出口数据、汽车和工业品板块",
        }
    if any(word in text for word in ["china", "hong kong", "yuan", "beijing", "property"]):
        return {
            "title": "中国资产仍受政策、盈利和资金流共同影响，科技制造方向更值得跟踪",
            "content": "中国资产相关消息显示，政策预期、盈利修复和资金流变化仍是影响A股和港股表现的核心变量。",
            "meaning": "若政策和盈利同时改善，中国资产有修复机会；若成交不足，反弹持续性仍需验证。",
            "watch": "A股成交额、港股成交额、南向资金、人民币汇率、政策表态和科技制造板块",
        }
    return {
        "title": f"{category}重要消息待复核，需观察是否改变市场风险偏好",
        "content": f"{category}方向出现重要消息，但具体影响仍需结合官方信息、价格反应和成交确认。",
        "meaning": "先观察价格和成交是否确认，避免只根据单条新闻做仓位动作。",
        "watch": "官方公告、相关指数、成交额、利率、美元、商品价格和行业龙头表现",
    }


def classify_news(title: str, content: str) -> tuple[str, str, str, int]:
    text = f"{title} {content}".lower()
    category = "全球市场"
    score = 0
    best_rank = -1
    for candidate, words in NEWS_KEYWORDS.items():
        hits = sum(1 for word in words if word in text)
        rank = NEWS_CATEGORY_PRIORITY.get(candidate, 0)
        if hits and (hits + 1 > score or (hits + 1 == score and rank > best_rank)):
            category = candidate
            score = hits + 1
            best_rank = rank
    score += sum(1 for word in NEWS_IMPACT_WORDS if word in text)
    if category in {"央行", "能源", "地缘", "科技", "中国资产"}:
        score += 2
    if any(word in text for word in ["rise", "fall", "surge", "slump", "record", "cut", "hike", "warning"]):
        score += 1
    if category == "央行":
        assets = "美股、美元、美债、黄金、AI/半导体、A股宽基"
        direction = "待观察"
    elif category == "能源":
        assets = "原油、通胀交易、航空、化工、有色金属、全球股市"
        direction = "利多"
    elif category == "科技":
        assets = "美股科技、AI算力、半导体、消费电子、A股AI链"
        direction = "利多"
    elif category == "中国资产":
        assets = "A股、港股、人民币、中国消费、先进制造"
        direction = "待观察"
    elif category == "地缘":
        assets = "原油、黄金、美元、军工、全球风险资产"
        direction = "待观察"
    elif category == "贸易":
        assets = "全球贸易链、汽车、工业品、美元、欧股"
        direction = "待观察"
    elif category == "风险事件":
        assets = "信用债、银行、科技股、美元、全球股市"
        direction = "待观察"
    else:
        assets = "全球股市、美元、美债、商品"
        direction = "待观察"
    return category, assets, direction, score


def fetch_rss_news(as_of: date) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    min_date = as_of - timedelta(days=1)
    seen: set[str] = set()
    for source, url in NEWS_FEEDS:
        try:
            xml_text = request_text(url, timeout=20)
            root = ET.fromstring(xml_text)
        except (HTTPError, URLError, TimeoutError, ET.ParseError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
            continue
        for item in root.findall(".//item")[:30]:
            title = clean_html_text(item.findtext("title", ""))
            if not title or title in seen:
                continue
            item_source = source
            if source.startswith("Google News") and " - " in title:
                title_body, source_tail = title.rsplit(" - ", 1)
                if not any(term.lower() in source_tail.lower() for term in TRUSTED_NEWS_TERMS):
                    continue
                title = title_body.strip()
                item_source = f"{source} / {source_tail.strip()}"
            joined_text = f"{title} {clean_html_text(item.findtext('description', ''))}".lower()
            if any(term in joined_text for term in EXCLUDE_NEWS_TERMS):
                continue
            pub_dt = parse_rss_date(item.findtext("pubDate", ""))
            if pub_dt and pub_dt.date() < min_date:
                continue
            content = clean_html_text(item.findtext("description", ""))
            category, assets, direction, score = classify_news(title, content)
            if score < 4:
                continue
            seen.add(title)
            impact = "高" if score >= 6 else ("中高" if score >= 4 else "中")
            horizon = "短期：1天-2周" if category in {"央行", "能源", "地缘", "风险事件"} else "中期：2周-3个月"
            source_label = chinese_source_label(item_source)
            zh = chinese_news_summary(title, content, category)
            display_title = zh["title"] if mostly_english_text(title) else title
            display_key = normalize_key(display_title)
            if display_key in seen:
                continue
            seen.add(display_key)
            display_content = zh["content"] if mostly_english_text(content) or not content else content
            rows.append(
                {
                    "date": fmt_slash(pub_dt.date() if pub_dt else as_of),
                    "category": category,
                    "title": display_title[:120],
                    "content": display_content[:220] or display_title,
                    "assets": assets,
                    "direction": direction,
                    "impact": impact,
                    "horizon": horizon,
                    "meaning": zh["meaning"],
                    "action": "等待" if category in {"央行", "地缘", "风险事件"} else "观察等待",
                    "watch": zh["watch"],
                    "source": source_label,
                    "confidence": "高" if item_source == "Federal Reserve" else "中高",
                    "included": "是" if impact in {"高", "中高"} else "否",
                    "score": score,
                    "refreshStatus": f"公开新闻源刷新：{source_label}，发布时间 {pub_dt.isoformat(timespec='minutes') if pub_dt else '待核验'}",
                }
            )
    rows.sort(key=lambda row: (-int(row.get("score", 0)), row.get("title", "")))
    return rows[:10], errors


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
            nav_date = datetime.strptime(fetched["navDate"], "%Y-%m-%d").date()
            refresh_status = status_date_text(nav_date, as_of, prefix="净值")
            decision, reason = classify_fund(theme, fetched.get("day"), fetched.get("week"))
            day_value = round(float(fetched["day"]), 2) if fetched.get("day") is not None else old.get("day", 0)
            week_value = round(float(fetched["week"]), 2) if fetched.get("week") is not None else old.get("week", 0)
            nav_value = fetched.get("nav")
            reason = f"{reason} {refresh_status}；数据源：天天基金/东方财富。"
            check_lines.append(f"{code}: nav={nav_value}, day={day_value}%, navDate={fetched['navDate']}")
        else:
            refresh_status = "抓取失败，沿用上一版并待核验"
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
                "risk": FUND_RISK.get(code, old.get("risk", "中")),
                "decision": decision,
                "reason": reason,
                "type": fund_type,
                "latestNav": nav_value if nav_value is not None else old.get("latestNav", ""),
                "navDate": fetched["navDate"] if fetched else old.get("navDate", "待核验"),
                "refreshStatus": refresh_status,
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
        item["refreshStatus"] = "云端复核排序；新闻/估值若无新增可靠源，则沿用最近可得判断"
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
        item["refreshStatus"] = "公开资料复核；若无新公开信/访谈/13F，则不强行编写新观点"
        item.setdefault("stance", "无新增可靠观点")
        item.setdefault("strength", "中")
        item.setdefault("assets", "待核验")


def update_finance_news(data: dict[str, Any], as_of: date) -> None:
    """Refresh high-impact finance news from available public RSS feeds.

    If public feeds are insufficient, the script keeps the previous curated
    rows but marks them as carried forward. It must never silently relabel stale
    news as today's new news.
    """
    fetched, errors = fetch_rss_news(as_of)
    fetched = dedupe_news_items(fetched, 10)
    if len(fetched) >= 5:
        existing = dedupe_news_items(list(data.get("financeNews", [])), 10)
        combined = dedupe_news_items(fetched + existing, 10)
        for item in combined[len(fetched) :]:
            item["refreshStatus"] = (
                f"当天RSS有效新闻不足10条，沿用最近可靠新闻；原始来源日期 {safe_text(item.get('date'), '待核验')}。"
            )
            item["included"] = safe_text(item.get("included"), "否：沿用最近可靠新闻")
        data["financeNews"] = combined
        data["financeNewsStatus"] = {
            "status": "RSS刷新",
            "count": len(combined),
            "freshCount": len(fetched),
            "note": "优先使用当天公开RSS高影响新闻；不足10条时用最近可靠新闻补齐并标注沿用。",
            "errors": errors[:3],
        }
        return
    existing = dedupe_news_items(list(data.get("financeNews", [])), 10)
    for item in existing:
        item["date"] = safe_text(item.get("date"), fmt_slash(as_of))
        item.setdefault("category", "财经")
        item.setdefault("title", "待核验财经新闻")
        item.setdefault("content", "今日新闻源待核验。")
        item.setdefault("assets", "全球市场")
        item.setdefault("direction", "待观察")
        item.setdefault("impact", "中")
        item.setdefault("horizon", "短期：1天-2周")
        item.setdefault("meaning", "等待可靠新闻源确认。")
        item.setdefault("action", "观察等待")
        item.setdefault("watch", "官方公告、主流财经媒体、成交额、利率、美元和油价")
        item.setdefault("source", "待核验")
        item.setdefault("confidence", "中")
        item.setdefault("included", "否：待核验")
        item["refreshStatus"] = f"今日RSS有效新闻不足（{len(fetched)}条），沿用最近可靠新闻；需人工补充。"
    data["financeNews"] = existing[:10]
    data["financeNewsStatus"] = {
        "status": "沿用最近可靠新闻",
        "count": len(existing),
        "note": f"公开RSS有效新闻不足，仅抓到{len(fetched)}条；未将旧新闻伪装成当天新新闻。",
        "errors": errors[:3],
    }


def build_source_status(
    data: dict[str, Any],
    as_of: date,
    risk_status: dict[str, Any],
    fund_checks: list[str],
) -> dict[str, Any]:
    funds = data.get("fundHoldings", [])
    real_fund_rows = sum(1 for item in funds if "数据源：天天基金/东方财富" in str(item.get("reason", "")))
    news_status = data.get("financeNewsStatus", {"status": "待核验", "note": "新闻刷新状态待核验。"})
    experts = data.get("expertViews", [])
    industries = data.get("industryWatch", [])
    status = {
        "daily": {"status": "汇总生成", "note": "基于6个模块最新可得资料生成，不直接构成交易建议。"},
        "risk": risk_status,
        "industry": {
            "status": "云端复核排序",
            "count": len(industries),
            "note": "行业主线每日重新排序；若无新增可靠新闻/估值源，保留最近判断并标注复核。",
        },
        "experts": {
            "status": "公开资料复核",
            "count": len(experts),
            "note": "未发现可靠新增观点时，明确写无新增可靠观点，不编造新动向。",
        },
        "funds": {
            "status": "真实抓取" if real_fund_rows else "待核验",
            "count": len(funds),
            "fresh": real_fund_rows,
            "note": f"{real_fund_rows}/{len(funds)}只基金从天天基金/东方财富返回净值；QDII按真实滞后日期展示。",
            "sample": fund_checks[:4],
        },
        "news": news_status,
        "asOf": f"{fmt_slash(as_of)} 05:00 HKT",
    }
    blocking = [
        name
        for name, item in status.items()
        if isinstance(item, dict) and item.get("status") in {"待核验", "部分沿用/待核验", "沿用最近可靠新闻"}
    ]
    status["overall"] = "部分模块需核验" if blocking else "全部模块已刷新"
    status["blockingModules"] = blocking
    data["sourceStatus"] = status
    return status


def to_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, str):
        match = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace("％", "%"))
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def short_text(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", "", str(value or ""))
    return text if len(text) <= limit else text[:limit] + "..."


def news_focus_text(item: dict[str, Any]) -> str:
    category = str(item.get("category") or "财经")
    category_focus = {
        "央行": "利率路径",
        "科技": "AI财报验证",
        "地缘": "油金波动",
        "能源": "油价供给",
        "商品": "资源品传导",
        "中国资产": "政策和盈利修复",
        "美股": "估值和拥挤度",
        "港股": "资金面和科技资产",
        "风险事件": "信用和流动性",
        "贸易": "关税和供应链",
    }
    text = category_focus.get(category)
    if not text:
        title = str(item.get("title") or item.get("content") or "重要财经变量")
        text = short_text(title, 12).replace("...", "")
    return f"{category}：{text}"


def dedupe_news_items(items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        key = normalize_key(item.get("title") or item.get("content") or item.get("category"))
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def best_news_items(items: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    def weight(item: dict[str, Any]) -> tuple[int, int, int, str]:
        included = 0 if str(item.get("included", "")).startswith("是") else 1
        impact = {"高": 0, "中高": 1, "中": 2}.get(str(item.get("impact", "")), 3)
        score = -int(to_number(item.get("score"), 0))
        return included, impact, score, str(item.get("title", ""))

    return sorted(dedupe_news_items(items, 20), key=weight)[:limit]


def compact_fund_focus(top_fund: dict[str, Any] | None, weak_fund: dict[str, Any] | None) -> str:
    if not top_fund or not weak_fund:
        return "基金净值待核验"
    top_code = safe_text(top_fund.get("code"))
    top_theme = safe_text(top_fund.get("theme"))
    weak_code = safe_text(weak_fund.get("code"))
    weak_theme = safe_text(weak_fund.get("theme"))
    weak_move = to_number(weak_fund.get("day"))
    weak_word = "跌" if weak_move < 0 else "涨"
    return (
        f"强项{top_code}({top_theme})日涨{to_number(top_fund.get('day')):.2f}%，"
        f"弱项{weak_code}({weak_theme})日{weak_word}{abs(weak_move):.2f}%"
    )


def short_join(names: str, limit: int = 2) -> str:
    parts = [part.strip() for part in re.split(r"[、,，]", names or "") if part.strip()]
    return "、".join(parts[:limit]) or "核心主线"


def compact_news_focus(items: list[dict[str, Any]], limit: int = 2) -> str:
    focus = [news_focus_text(item) for item in best_news_items(items, limit)]
    return "；".join(focus) or "财经新闻待核验"


def compact_daily_news(items: list[dict[str, Any]]) -> str:
    best = best_news_items(items, 1)
    if not best:
        return "财经新闻待核验"
    item = best[0]
    category = safe_text(item.get("category"), "财经")
    watch = safe_text(item.get("watch"), "")
    title = safe_text(item.get("title"), "")
    if watch:
        first_watch = re.split(r"[、,，；;]", watch)[0].strip()
        return f"{category}看{first_watch}"
    return short_text(title, 18)


def fund_stress_state(funds: list[dict[str, Any]]) -> dict[str, Any]:
    moves = [to_number(item.get("day")) for item in funds if item.get("day") not in (None, "", "待核验")]
    if not moves:
        return {"active": False, "avg": 0.0, "weak_count": 0, "total": 0, "worst": 0.0}
    weak_count = sum(1 for value in moves if value < 0)
    total = len(moves)
    avg = sum(moves) / total
    worst = min(moves)
    active = weak_count >= max(4, total // 3) or avg <= -0.8 or worst <= -2.5
    return {
        "active": active,
        "avg": avg,
        "weak_count": weak_count,
        "total": total,
        "worst": worst,
    }


def urgent_daily_fields(
    *,
    as_of: date,
    signal: str,
    action: str,
    core_names: str,
    reserve_names: str,
    risk_names: str,
    top_fund: dict[str, Any] | None,
    weak_fund: dict[str, Any] | None,
    stress: dict[str, Any],
) -> dict[str, str]:
    core_tight = short_join(core_names, 3)
    reserve_tight = short_join(reserve_names, 2)
    risk_tight = compact_risk_names(risk_names)
    top_text = compact_fund_focus(top_fund, weak_fund)
    weak_count = int(stress.get("weak_count") or 0)
    total = int(stress.get("total") or 0)
    if action == "防守" or signal == "红灯":
        judgement = f"今天结论：红灯防守，{weak_count}/{total}只基金走弱，先把目标从找机会切到控回撤。"
        position = "仓位建议：先降高波动仓位，暂停左侧加仓，保留现金等风险回落。"
        need = f"今日动作：先做三件事：1）不加仓；2）检查弱项是否破位；3）只看{core_tight}能否放量止跌。"
        reason = f"防守原因：{risk_tight}压制风险偏好，弱项扩散时先保护本金。"
        risk = f"主要风险：普跌后弱修复再下杀；若{core_tight}缩量反弹，继续防守。"
    else:
        judgement = f"今天结论：黄灯偏防守，{weak_count}/{total}只基金走弱，不是普通震荡；先控回撤，暂停加仓。"
        position = "仓位建议：高波动仓位先降速，AI/半导体、PCB、有色等只等放量修复，不补跌。"
        need = f"今日动作：1）停止追高和补跌；2）盯{core_tight}能否放量收复；3）核对强弱分化：{top_text}。"
        reason = f"不操作原因：基金端普跌，{risk_tight}仍偏敏感，主线需成交和订单重新确认。"
        risk = f"主要风险：科技链和高波动资产同步补跌；若成交不足，{reserve_tight}可能继续拖累组合。"
    review = f"下次复盘：看{core_tight}是否放量止跌，{reserve_tight}是否继续转弱。"
    return {
        "asOf": f"{fmt_slash(as_of)} 05:00 HKT",
        "signal": signal,
        "action": action,
        "marketJudgement": judgement,
        "positionAdvice": position,
        "needAction": need,
        "actionReason": reason,
        "riskPoint": risk,
        "nextReview": review,
    }


def compact_risk_names(risk_names: str) -> str:
    names = [part.strip() for part in re.split(r"[、,，]", risk_names or "") if part.strip()]
    return "、".join(names[:2]) or "关键风险"


def compact_daily_fields(
    *,
    as_of: date,
    signal: str,
    action: str,
    core_names: str,
    reserve_names: str,
    risk_names: str,
    risk_focus: str,
    top_fund: dict[str, Any] | None,
    weak_fund: dict[str, Any] | None,
    news_items: list[dict[str, Any]],
) -> dict[str, str]:
    core_short = core_names or "核心主线"
    reserve_short = reserve_names or "候补轮动"
    core_tight = short_join(core_names, 2)
    reserve_tight = short_join(reserve_names, 2)
    risk_tight = compact_risk_names(risk_names)
    fund_short = compact_fund_focus(top_fund, weak_fund)
    news_short = compact_daily_news(news_items)
    if action == "进攻":
        judgement = f"今天结论：绿灯偏进攻，风险可控，围绕{core_tight}小幅试探。"
        position = f"仓位建议：小幅进攻{core_tight}，只买回调，不追高。"
        need = f"今日动作：看{core_tight}放量；基金看{fund_short}。"
        reason = f"操作原因：风控转绿，{news_short}，主线有确认。"
        risk = f"主要风险：{risk_tight}升温，或{core_tight}放量不持续。"
    elif action == "防守":
        judgement = f"今天结论：红灯防守，{news_short}扰动偏大，先控高波动仓位。"
        position = "仓位建议：降低高波动仓位，保留现金，不做左侧加仓。"
        need = f"今日动作：检查{risk_focus}；基金看{fund_short}。"
        reason = f"防守原因：{risk_tight}有压力，{news_short}仍扰动风险偏好。"
        risk = "主要风险：利率、美元、油价或信用风险上行，压制权益估值。"
    else:
        judgement = f"今天结论：黄灯等待，{news_short}待确认，先看{core_tight}能否放量。"
        position = "仓位建议：维持中性偏谨慎，不追高，等主线确认。"
        need = f"今日动作：盯{core_tight}成交/订单；基金看{fund_short}。"
        reason = f"不操作原因：{risk_tight}未转绿，{news_short}仍待确认。"
        risk = f"主要风险：{risk_tight}；若成交不足或消息反复，成长资产易回撤。"
    review = f"下次复盘：看{core_tight}是否放量，{reserve_tight}是否升温，新闻是否新增冲击。"
    return {
        "asOf": f"{fmt_slash(as_of)} 05:00 HKT",
        "signal": signal,
        "action": action,
        "marketJudgement": judgement,
        "positionAdvice": position,
        "needAction": need,
        "actionReason": reason,
        "riskPoint": risk,
        "nextReview": review,
    }


def industry_score(item: dict[str, Any]) -> float:
    prosperity = to_number(item.get("prosperity"))
    heat = to_number(item.get("heat"))
    risk = to_number(item.get("risk"))
    return prosperity * 0.45 + heat * 0.35 + (100 - risk) * 0.20


def format_focus_names(items: list[dict[str, Any]], limit: int = 3) -> str:
    names = [str(item.get("name") or "").strip() for item in items if item.get("name")]
    return "、".join(names[:limit]) or "无明确主线"


def important_risk_items(risk_items: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
    def risk_weight(item: dict[str, Any]) -> tuple[int, float]:
        signal = str(item.get("signal", ""))
        status = str(item.get("refreshStatus", ""))
        level = 3 if "红" in signal else 2 if "黄" in signal else 1 if "待核验" in status else 0
        return level, to_number(item.get("score"))

    selected = [
        item
        for item in risk_items
        if "红" in str(item.get("signal", ""))
        or "黄" in str(item.get("signal", ""))
        or "待核验" in str(item.get("refreshStatus", ""))
    ]
    return sorted(selected, key=risk_weight, reverse=True)[:limit]


def format_risk_focus(items: list[dict[str, Any]], limit: int = 3) -> str:
    parts = []
    for item in items[:limit]:
        name = short_text(item.get("name"), 12)
        value = short_text(item.get("value"), 34)
        signal = str(item.get("signal") or "待核验").replace("正常", "").replace("预警", "")
        parts.append(f"{name}：{value}，{signal}")
    return "；".join(parts) or "风险指标待核验"


def numbered_focus(items: list[str]) -> str:
    return "；".join(f"{idx + 1}）{item}" for idx, item in enumerate(items) if item)


def cn_blocking_modules(modules: list[str]) -> str:
    names = {
        "risk": "风控数据",
        "industry": "行业观察",
        "experts": "专家观点",
        "funds": "基金净值",
        "news": "财经新闻",
        "daily": "每日简报",
    }
    return "、".join(names.get(item, item) for item in modules) or "无"


def top_fund_moves(funds: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not funds:
        return None, None
    sortable = [item for item in funds if item.get("day") not in (None, "", "待核验")]
    if not sortable:
        return None, None
    return max(sortable, key=lambda item: to_number(item.get("day"))), min(sortable, key=lambda item: to_number(item.get("day")))


def compact_daily_text(signal: str, action: str, core_names: str, risk_names: str) -> tuple[str, str, str]:
    core_short = core_names or "核心主线"
    if action == "进攻":
        judgement = f"今天结论：绿灯偏进攻，风险整体可控，围绕{core_short}小幅试探，不追高。"
        reason = "操作原因：多数风控指标转绿，主线有成交和催化支撑，但仓位仍要分批控制。"
        risk = f"主要风险：{core_short}若放量不持续或业绩不兑现，短线仍可能回撤。"
    elif action == "防守":
        judgement = "今天结论：红灯防守，市场风险升温，先降低高波动资产暴露。"
        reason = f"防守原因：{risk_names or '关键风险指标'}出现红灯或系统性扰动，先保留现金等待风险回落。"
        risk = "主要风险：利率、美元、油价或信用风险继续上行，可能压制权益估值和风险偏好。"
    else:
        judgement = f"今天结论：黄灯等待，市场风险未失控，但估值和利率仍压制成长资产，先看{core_short}能否放量确认。"
        reason = "不操作原因：风控灯未转绿，实际利率和估值仍偏敏感，主线虽强但不适合追高。"
        risk = "主要风险：AI链局部偏贵，实际利率处在预警区；若美元/美债上行或成交不足，成长资产容易回撤。"
    return judgement, reason, risk


def compact_action_text(action: str, core_names: str, reserve_names: str, risk_names: str) -> tuple[str, str, str]:
    core_short = core_names or "核心主线"
    reserve_short = reserve_names or "候补轮动"
    if action == "进攻":
        position = f"仓位建议：小幅进攻{core_short}，只分批买回调，不追高。"
        need = f"今日动作：重点看{core_short}能否继续放量，确认后再小幅加仓。"
        review = f"下次复盘：看{core_short}成交、订单和业绩是否继续兑现。"
    elif action == "防守":
        position = "仓位建议：先降高波动资产，保留现金，等待风险回落。"
        need = "今日动作：先防守，不加仓；优先检查红灯风险是否扩散。"
        review = f"下次复盘：看{risk_names or '关键风险'}是否回落，主线是否止跌。"
    else:
        position = "仓位建议：维持中性偏谨慎，不追高，等主线确认。"
        need = f"今日动作：先等待；只观察{core_short}，看成交和业绩是否确认。"
        review = f"下次复盘：看{core_short}是否放量，{reserve_short}是否升温。"
    return position, need, review


def update_daily(data: dict[str, Any], as_of: date) -> None:
    risk_items = data.get("riskDashboard", [])
    yellow = sum(1 for item in risk_items if "黄" in str(item.get("signal", "")))
    red = sum(1 for item in risk_items if "红" in str(item.get("signal", "")))
    signal = "红灯" if red else ("黄灯" if yellow else "绿灯")
    action = "防守" if red else ("等待" if yellow else "进攻")
    source_status = data.get("sourceStatus", {})
    quality = source_status.get("overall", "数据状态待核验")
    stale_modules = cn_blocking_modules(source_status.get("blockingModules", []))
    risks = important_risk_items(risk_items)
    risk_focus = format_risk_focus(risks)
    industries = sorted(data.get("industryWatch", []), key=industry_score, reverse=True)
    core = [item for item in industries if str(item.get("tier")) == "核心主线"][:3]
    reserve = [item for item in industries if str(item.get("tier")) == "候补轮动"][:2]
    core_names = format_focus_names(core, 3)
    reserve_names = format_focus_names(reserve, 2)
    top_fund, weak_fund = top_fund_moves(data.get("fundHoldings", []))
    news = dedupe_news_items(data.get("financeNews", []), 10)
    data["financeNews"] = news
    risk_names = "、".join(short_text(item.get("name"), 8) for item in risks[:3]) or "风险指标"
    stress = fund_stress_state(data.get("fundHoldings", []))
    if stress.get("active"):
        data["daily"] = urgent_daily_fields(
            as_of=as_of,
            signal=signal,
            action=action,
            core_names=core_names,
            reserve_names=reserve_names,
            risk_names=risk_names,
            top_fund=top_fund,
            weak_fund=weak_fund,
            stress=stress,
        )
    else:
        data["daily"] = compact_daily_fields(
            as_of=as_of,
            signal=signal,
            action=action,
            core_names=core_names,
            reserve_names=reserve_names,
            risk_names=risk_names,
            risk_focus=risk_focus,
            top_fund=top_fund,
            weak_fund=weak_fund,
            news_items=news,
        )


def build_dashboard() -> tuple[dict[str, Any], list[str]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"missing dashboard data: {DATA_PATH}")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    as_of = today_hkt()
    update_risk_market_data(data, as_of)
    risk_status = annotate_risk_status(data, as_of)
    update_industry(data, as_of)
    update_experts(data, as_of)
    update_finance_news(data, as_of)
    _, checks = update_funds(data, as_of)
    build_source_status(data, as_of, risk_status, checks)
    update_daily(data, as_of)
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


def display_percent(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "待核验"


def notion_percent(value: Any) -> float | str:
    """Notion percent-formatted number fields expect 0.0415 to display 4.15%."""
    try:
        return round(float(value) / 100, 6)
    except (TypeError, ValueError):
        return "待核验"


def fund_forward_view(theme: str, decision: str, item: dict[str, Any], horizon: str) -> str:
    day = display_percent(item.get("day"))
    week = display_percent(item.get("week"))
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
            "说明": f"GitHub Actions 云端自动复核；{item.get('refreshStatus', '来源日期待核验')}。",
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
            "新闻日期/来源": f"{cn_date} / {item.get('refreshStatus', '云端自动复核')}",
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
            "观点来源": item.get("refreshStatus", "公开资料云端复核"),
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
        refresh_status = safe_text(item.get("refreshStatus"), "刷新状态待核验")
        decision = safe_text(item.get("decision"), "待核验")
        row = {
            "报表更新日期": as_of,
            "基金名称": item.get("name"),
            "基金代码": item.get("code"),
            "关联主线": theme,
            "夏普比率": item.get("sharp", "待核验"),
            "操作原因": f"{reason}；{refresh_status}",
            "操作语言": decision,
            "日涨跌": notion_percent(item.get("day")),
            "最大回撤": item.get("maxDrawdown", "待核验"),
            "最新净值": item.get("latestNav", "待核验"),
            "净值日期": nav_date,
            "类型": item.get("type", "待核验"),
            "风险等级": item.get("risk"),
            "风险": item.get("risk"),
            "近1周": notion_percent(item.get("week")),
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
            "新闻来源": f"{item.get('source', '待核验')}；{item.get('refreshStatus', '刷新状态待核验')}",
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
