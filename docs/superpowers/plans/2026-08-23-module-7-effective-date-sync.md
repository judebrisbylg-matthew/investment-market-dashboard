# Module 7 Effective-Date Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start publishing a current, non-backfilled Module 7 radar snapshot on every successful daily run.

**Architecture:** Build an auditable `opportunityRadar` object only from the already-refreshed daily payload, then include its coverage in the v2 contract. Extend the managed Notion-page publisher with a page-7 renderer and only update the delimited system region on the existing Module 7 parent page.

**Tech Stack:** Python 3.12 standard library, GitHub Actions, Notion REST API.

**Spec:** `docs/superpowers/specs/2026-08-23-module-7-effective-date-sync-design.md`

## Global Constraints

- Do not backfill or overwrite Module 7 content dated before 2026-08-23.
- Preserve child pages 7A-7I and all non-managed Notion content.
- Keep missing or unverified opportunity data grey; do not emit action signals.
- Display business date separately from source market dates.

---

### Task 1: Define the module-7 payload and contract coverage

**Files:**
- Create: `tests/test_module7_radar.py`
- Modify: `scripts/cloud_daily_update.py`

**Interfaces:**
- Produces: `build_opportunity_radar(data: dict[str, Any], as_of: date) -> dict[str, Any]`
- Produces: `data["v2"]["moduleCoverage"]["7"]: float`

- [ ] **Step 1: Write the failing test**

```python
def test_opportunity_radar_uses_run_date_but_retains_market_dates():
    data = {"industryWatch": [{"name": "AI芯片/半导体", "score": 82, "marketDate": "2026-08-21"}], "fundHoldings": [{"code": "004432", "name": "南方有色金属ETF联接A", "navDate": "2026-08-21"}], "v2": {"marketGate": "风险允许", "dataHealth": "绿灯"}}
    radar = updater.build_opportunity_radar(data, date(2026, 8, 24))
    assert radar["businessDate"] == "2026-08-24"
    assert radar["industries"][0]["marketDate"] == "2026-08-21"
    assert radar["executionStatus"] == "灰灯"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_module7_radar.py -v`

Expected: FAIL because `build_opportunity_radar` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
def build_opportunity_radar(data, as_of):
    return {"businessDate": as_of.isoformat(), "executionStatus": "灰灯", "industries": data.get("industryWatch", [])[:10], "funds": data.get("fundHoldings", [])}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_module7_radar.py -v`

Expected: PASS.

### Task 2: Publish a delimited Module 7 parent-page snapshot

**Files:**
- Modify: `scripts/notion_visible_pages.py`
- Modify: `tests/test_module7_radar.py`

**Interfaces:**
- Consumes: `data["opportunityRadar"]`.
- Produces: `page_blocks("7", ...)` with a page-7 business-date marker and grey execution status.

- [ ] **Step 1: Write the failing test**

```python
def test_module7_blocks_show_business_date_and_gray_execution_boundary():
    blocks = visible.page_blocks("7", sample_data_with_radar(), [], [])
    text = " ".join(visible.block_plain_text(block) for block in blocks)
    assert "页面7｜业务日期 2026-08-24" in text
    assert "执行灰灯" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_module7_radar.py -v`

Expected: FAIL because page `7` is unknown.

- [ ] **Step 3: Write minimal implementation**

```python
elif page_no == "7":
    body += _opportunity_radar(data)
```

Extend `sync_visible_pages` to publish page `7` before page `0`, and extend `NotionConfig` with `page_opportunity_radar` using the existing page id.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_module7_radar.py -v`

Expected: PASS.

### Task 3: Guard daily automation and record the decision

**Files:**
- Modify: `.github/workflows/daily-update.yml`
- Modify: `00_核心分析交接与决策台账.md`

**Interfaces:**
- Consumes: `data["v2"]["moduleCoverage"]["7"]` and `data["opportunityRadar"]`.
- Produces: workflow failure if module 7 is absent or claims a non-grey execution state without a validated model.

- [ ] **Step 1: Add failing validation assertions locally**

```python
assert "7" in contract.get("moduleCoverage", {}), contract
radar = data.get("opportunityRadar", {})
assert radar.get("businessDate") == contract.get("businessDate"), radar
assert radar.get("executionStatus") == "灰灯", radar
```

- [ ] **Step 2: Run the updater test suite to verify the assertions fail before implementation**

Run: `python -m unittest tests/test_module7_radar.py -v`

Expected: FAIL before Tasks 1 and 2 are complete.

- [ ] **Step 3: Add the workflow assertions and append a dated decision-table row**

```markdown
| 2026-08-23 | 模块7自下一有效交易日进入自动快照同步；不回填历史；缺失数据维持灰灯 | automation-repo 日更链路 | 已执行 | 下一次日更后回读 Notion 与看板 |
```

- [ ] **Step 4: Run compact verification**

Run: `python -m unittest tests/test_module7_radar.py -v && python -m py_compile scripts/cloud_daily_update.py scripts/notion_visible_pages.py`

Expected: all tests pass and both scripts compile.
