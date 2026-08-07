"""Publish the latest 0-5 dashboard snapshots into visible Notion pages.

The six user-facing pages are latest-snapshot views.  Historical rows continue
to live in the hidden 6A-6F databases.  This module owns only the delimited
SYSTEM_MANAGED region and deliberately preserves page titles, child pages and
uploaded files.
"""

from __future__ import annotations

from datetime import date
from typing import Any


START_PREFIX = "【系统每日数据区开始】"
END_MARKER = "【系统每日数据区结束】"
LEGACY_DASHBOARD_PREFIXES = (
    "01｜市场环境与风控",
    "01 | 市场环境与风控",
)
ATTACHMENT_HEADING = "原始终稿 Excel 附件"


def _text(value: Any, limit: int = 1900) -> str:
    value = "待核验" if value is None or str(value).strip() == "" else str(value).strip()
    return value[:limit]


def _rt(value: Any, *, bold: bool = False) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": _text(value)}, "annotations": {"bold": bold}}]


def paragraph(value: Any, *, color: str = "default") -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rt(value), "color": color}}


def heading(value: Any, level: int = 2) -> dict[str, Any]:
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": _rt(value, bold=True)}}


def callout(value: Any, emoji: str = "📊", color: str = "blue_background") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {"rich_text": _rt(value), "icon": {"type": "emoji", "emoji": emoji}, "color": color},
    }


def table(headers: list[str], rows: list[list[Any]]) -> dict[str, Any]:
    def row(values: list[Any], header: bool = False) -> dict[str, Any]:
        return {
            "object": "block",
            "type": "table_row",
            "table_row": {"cells": [_rt(value, bold=header) for value in values]},
        }

    width = len(headers)
    normalized = [(values + [""] * width)[:width] for values in rows]
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": True,
            "has_row_header": False,
            "children": [row(headers, True)] + [row(values) for values in normalized],
        },
    }


def _signal(value: Any) -> str:
    value = str(value or "")
    for light in ("红灯", "黄灯", "绿灯", "灰灯"):
        if light in value:
            return light
    return "灰灯"


def _source_date(item: dict[str, Any], fallback: str) -> str:
    return _text(item.get("sourceDate") or item.get("marketDate") or item.get("navDate") or fallback)


def _start_block(page_no: str, business_date: str, batch_id: str) -> dict[str, Any]:
    return callout(
        f"{START_PREFIX}｜页面{page_no}｜业务日期 {business_date}｜批次 {batch_id}",
        emoji="🔄",
        color="gray_background",
    )


def _end_block() -> dict[str, Any]:
    return paragraph(END_MARKER, color="gray")


def _summary(data: dict[str, Any]) -> list[dict[str, Any]]:
    contract = data.get("v2", {})
    daily = data.get("daily", {})
    counts = contract.get("riskLightCounts", {})
    return [
        callout(
            "量化纪律：数据健康优先；市场闸门决定风险上限；行业只展示前10；机构与事件只做验证；持仓只给研究方向。",
            "📊",
        ),
        table(
            ["生成日期", "数据健康", "系统市场闸门", "风控绿/黄/红/灰", "机会执行状态", "今日总动作"],
            [[
                contract.get("businessDate"), contract.get("dataHealth"), contract.get("marketGate"),
                f"{counts.get('绿灯', 0)}/{counts.get('黄灯', 0)}/{counts.get('红灯', 0)}/{counts.get('灰灯', 0)}",
                daily.get("action"), daily.get("needAction"),
            ]],
        ),
        paragraph(
            f"市场判断：{_text(daily.get('marketJudgement'))}｜仓位方向：{_text(daily.get('positionAdvice'))}｜"
            f"主要风险：{_text(daily.get('riskPoint'))}"
        ),
    ]


def _risk(data: dict[str, Any], *, compact: bool = False) -> list[dict[str, Any]]:
    business_date = data.get("v2", {}).get("businessDate", date.today().isoformat())
    rows = []
    for item in data.get("riskDashboard", []):
        base = [
            item.get("name"), item.get("value"), _source_date(item, business_date), _signal(item.get("signal")),
            item.get("normal"), item.get("warning"), item.get("danger"),
        ]
        if not compact:
            base.extend([item.get("score"), item.get("refreshStatus")])
        rows.append(base)
    headers = ["监控指标", "当前值", "数据截至日", "灯号", "正常区间", "预警区间", "危险区间"]
    if not compact:
        headers += ["量化分", "数据状态/说明"]
    return [heading("01｜市场环境与风控"), table(headers, rows)]


def _industry(data: dict[str, Any], *, compact: bool = False) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(data.get("industryWatch", [])[:10], 1):
        base = [idx, item.get("name"), item.get("score"), item.get("tier"), item.get("operation"), item.get("marketDate")]
        if compact:
            base += [item.get("nextSignal")]
        else:
            base += [item.get("prosperity"), item.get("heat"), item.get("risk"), item.get("etf"), item.get("news"), item.get("nextSignal"), item.get("refreshStatus")]
        rows.append(base)
    headers = ["排名", "行业/赛道", "综合分", "层级", "研究动作", "行情日期"]
    headers += ["下一确认条件"] if compact else ["景气", "热度", "风险", "跟踪指数/ETF", "市场确认", "下一确认条件", "数据状态"]
    return [heading("02｜行业赛道前10"), table(headers, rows)]


def _experts(data: dict[str, Any], *, compact: bool = False) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(data.get("expertViews", [])[:10], 1):
        base = [idx, item.get("name"), item.get("stance"), item.get("strength"), item.get("assets")]
        base += [item.get("view")] if compact else [item.get("style"), item.get("view"), item.get("refreshStatus")]
        rows.append(base)
    headers = ["序号", "机构/投资者", "最新立场", "证据强度", "映射资产"]
    headers += ["验证结论"] if compact else ["投资风格", "验证结论", "数据状态/边界"]
    return [heading("03｜全球机构与跨市场验证"), table(headers, rows)]


def _events(data: dict[str, Any], *, compact: bool = False) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(data.get("financeNews", [])[:10], 1):
        base = [idx, item.get("date"), item.get("category"), item.get("title"), item.get("direction"), item.get("impact")]
        base += [item.get("meaning"), item.get("action")] if compact else [item.get("meaning"), item.get("assets"), item.get("action"), item.get("watch"), item.get("source"), item.get("confidence")]
        rows.append(base)
    headers = ["排名", "日期", "类别", "重大事件", "方向", "影响"]
    headers += ["30秒结论", "当前动作"] if compact else ["30秒结论", "影响资产", "当前动作", "跟踪条件", "来源", "置信度"]
    return [heading("04｜重大财经事件（按影响排序前10）"), table(headers, rows)]


def _match_sector(data: dict[str, Any], theme: str) -> dict[str, Any] | None:
    keys = [key for key in str(theme).replace("/", " ").split() if len(key) >= 2]
    return next((item for item in data.get("industryWatch", []) if any(key in str(item.get("name", "")) for key in keys)), None)


def _holdings(data: dict[str, Any], stocks: list[dict[str, Any]], fund_order: list[str], *, compact: bool = False) -> list[dict[str, Any]]:
    business_date = data.get("v2", {}).get("businessDate", date.today().isoformat())
    stock_map = {str(item.get("code")): item for item in data.get("stockHoldings", [])}
    stock_rows = []
    for idx, item in enumerate(stocks, 1):
        quote = stock_map.get(str(item.get("code")), {})
        sector = _match_sector(data, item.get("theme", "")) or {}
        stock_rows.append([
            idx, item.get("code"), item.get("name"), item.get("theme"), quote.get("latestPrice", "待核验"),
            f"{quote.get('day', '待核验')}%", f"{quote.get('fiveDay', '待核验')}%",
            quote.get("marketDate", "待核验"), sector.get("score", "待核验"), quote.get("risk", "待核验"),
            quote.get("signal", "灰灯"), quote.get("direction", "数据不足"), item.get("watch"), item.get("invalid"),
        ])
    fund_map = {str(item.get("code")): item for item in data.get("fundHoldings", [])}
    fund_rows = []
    for idx, code in enumerate(fund_order, 1):
        item = fund_map.get(code, {"code": code})
        fund_rows.append([
            idx, item.get("code"), item.get("name"), item.get("type"), item.get("theme"), item.get("latestNav"),
            f"{item.get('day', '待核验')}%", f"{item.get('week', '待核验')}%", item.get("navDate") or business_date,
            item.get("risk"), item.get("decision"), item.get("reason"),
        ])
    blocks = [
        heading("05｜我的持仓跟踪"),
        heading("股票持仓（2只）", 3),
        table(
            ["序号", "代码", "名称", "对应赛道", "最新价", "日涨跌", "近5日", "行情日期", "赛道分", "风险", "风险灯", "趋势判断", "下一确认条件", "失效条件"],
            stock_rows,
        ),
        heading("基金持仓（12只）", 3),
        table(["序号", "代码", "名称", "类型", "主题", "最新净值", "日涨跌", "近1周", "净值日期", "风险", "方向", "判断依据"], fund_rows),
    ]
    return blocks


def page_blocks(page_no: str, data: dict[str, Any], stocks: list[dict[str, Any]], fund_order: list[str]) -> list[dict[str, Any]]:
    contract = data.get("v2", {})
    business_date = _text(contract.get("businessDate"))
    batch_id = _text(contract.get("batchId"))
    body: list[dict[str, Any]] = [_start_block(page_no, business_date, batch_id)]
    if page_no == "0":
        body += _summary(data) + _risk(data, compact=True) + _industry(data, compact=True) + _experts(data, compact=True) + _events(data, compact=True) + _holdings(data, stocks, fund_order, compact=True)
    elif page_no == "1":
        body += _summary(data) + _risk(data)
    elif page_no == "2":
        body += _summary(data) + _industry(data)
    elif page_no == "3":
        body += _summary(data) + _experts(data)
    elif page_no == "4":
        body += _summary(data) + _events(data)
    elif page_no == "5":
        body += _summary(data) + _holdings(data, stocks, fund_order)
    else:
        raise ValueError(f"unknown visible page number: {page_no}")
    body.append(_end_block())
    return body


def block_plain_text(block: dict[str, Any]) -> str:
    kind = block.get("type", "")
    payload = block.get(kind, {}) if kind else {}
    return "".join(part.get("plain_text", "") for part in payload.get("rich_text", []))


def _managed_range(blocks: list[dict[str, Any]]) -> tuple[int, int] | None:
    start = next((idx for idx, block in enumerate(blocks) if START_PREFIX in block_plain_text(block)), None)
    if start is None:
        return None
    end = next((idx for idx in range(start + 1, len(blocks)) if END_MARKER in block_plain_text(blocks[idx])), None)
    if end is None:
        raise RuntimeError("visible Notion page contains a start marker without an end marker")
    return start, end


def _remove_legacy_dashboard_snapshot(client: Any, page_id: str) -> int:
    """Remove the obsolete pre-managed page-0 snapshot, if it still exists.

    Older versions placed a full static dashboard after the managed end marker.
    Once a managed region existed, the bootstrap-only cleanup no longer removed
    that static copy, so users could see the current batch followed by stale
    July data.  The exact legacy section is gated by its first dashboard heading
    and ends before the Excel attachment heading.  Files and child pages are
    always preserved.
    """
    blocks = client.list_block_children(page_id)
    managed = _managed_range(blocks)
    if managed is None:
        return 0

    footer = next(
        (
            idx
            for idx in range(managed[1] + 1, len(blocks))
            if ATTACHMENT_HEADING in block_plain_text(blocks[idx])
        ),
        None,
    )
    if footer is None:
        return 0

    legacy_heading = next(
        (
            idx
            for idx in range(managed[1] + 1, footer)
            if any(prefix in block_plain_text(blocks[idx]) for prefix in LEGACY_DASHBOARD_PREFIXES)
        ),
        None,
    )
    if legacy_heading is None:
        return 0

    preserve_types = {"child_page", "file", "bookmark", "link_preview", "pdf"}
    removed = 0
    for block in blocks[managed[1] + 1:footer]:
        if block.get("type") in preserve_types:
            continue
        client.delete_block(block["id"])
        removed += 1
    return removed


def publish_page(client: Any, page_id: str, page_no: str, blocks: list[dict[str, Any]], business_date: str, batch_id: str) -> None:
    existing = client.list_block_children(page_id)
    managed = _managed_range(existing)
    old_ids: set[str] = set()
    if managed:
        old_ids = {block["id"] for block in existing[managed[0]: managed[1] + 1]}

    # Keep the first non-managed block as a stable page intro/link anchor.  New
    # content is inserted before the previous managed region, then verified,
    # and only afterwards is the old region removed.
    anchor = next((block for block in existing if block.get("id") not in old_ids), None)
    response = client.append_block_children(page_id, blocks, after=anchor.get("id") if anchor else None)
    inserted = response.get("results", [])
    if not inserted or START_PREFIX not in block_plain_text(inserted[0]):
        raise RuntimeError(f"visible page {page_no} did not return a valid managed start marker")

    refreshed = client.list_block_children(page_id)
    expected = f"页面{page_no}｜业务日期 {business_date}｜批次 {batch_id}"
    if not any(expected in block_plain_text(block) for block in refreshed):
        raise RuntimeError(f"visible page {page_no} write verification failed for {business_date}")

    for block_id in old_ids:
        client.delete_block(block_id)

    # Page 0 used to contain a second, non-managed static dashboard below the
    # latest snapshot. Remove that exact legacy copy on every run so only the
    # newest valid batch remains visible. Historical rows stay in 6A-6F/0A.
    if page_no == "0":
        _remove_legacy_dashboard_snapshot(client, page_id)

    # Bootstrap cleanup: remove obsolete static table/text blocks only after the
    # managed snapshot is confirmed. Child pages and files are never touched.
    if managed is None:
        inserted_ids = {block.get("id") for block in inserted}
        anchor_id = anchor.get("id") if anchor else None
        preserve_types = {"child_page", "file", "bookmark", "link_preview", "pdf"}
        for block in existing:
            if block.get("id") == anchor_id or block.get("id") in inserted_ids or block.get("type") in preserve_types:
                continue
            client.delete_block(block["id"])


def sync_visible_pages(client: Any, page_ids: dict[str, str], data: dict[str, Any], stocks: list[dict[str, Any]], fund_order: list[str]) -> dict[str, int]:
    contract = data.get("v2", {})
    business_date = _text(contract.get("businessDate"))
    batch_id = _text(contract.get("batchId"))
    if business_date == "待核验" or batch_id == "待核验":
        raise RuntimeError("visible page sync requires v2 businessDate and batchId")

    updated: dict[str, int] = {}
    # Detail pages first; dashboard last so it never advertises a batch whose
    # underlying visible pages were not published.
    for page_no in ("1", "2", "3", "4", "5", "0"):
        page_id = page_ids.get(page_no, "")
        if not page_id:
            raise RuntimeError(f"missing visible Notion page id for page {page_no}")
        publish_page(client, page_id, page_no, page_blocks(page_no, data, stocks, fund_order), business_date, batch_id)
        updated[page_no] = 1
    return updated
