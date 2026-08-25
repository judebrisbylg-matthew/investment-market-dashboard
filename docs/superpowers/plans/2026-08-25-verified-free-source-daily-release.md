# 免费双源核验日更发布 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 仅在免费公开源的 P0 数据通过双源、交易日与时效校验后，发布同一批次到 GitHub Pages 与 Notion；否则在 07:15 前重试，最终保留最后已验证批次并公开失败状态。

**Architecture:** 采集层先把外部响应规范化为来源记录；纯校验层生成候选批次与发布决定；发布层只消费 `已验证发布` 的候选数据，或消费独立的失败状态。静态看板与 Notion 通过相同的 `batchId`、`releaseStatus` 和 `lastVerified*` 字段显示状态，不能各自推断“成功”。

**Tech Stack:** Python 3.12、标准库 `unittest`、urllib、GitHub Actions、Next.js、Notion API。

**Spec:** `docs/superpowers/specs/2026-08-25-free-source-verified-daily-release-design.md`

## Global Constraints

- 不采购商业数据、不回填历史、不启用 Module 7 执行模型、不改候选代码名册。
- UTC cron 必须为 `15 22 * * 0-4`；香港时间 06:15、06:35、06:55 重试，07:15 为不可逾越的截止时间。
- `runDate` 与 `businessDate` 分开：后者只能是交易日历中最近完成的 A 股开放日。
- P0 包含交易日历、2 只持仓股票、12 只基金、行业前 10 和风险闸门；P0 任一失败不发布新结论。
- P1/P2 可保留其原始日期，但不得在 P0 失败时产生新的行动语。
- 单元测试不得访问真实免费网页接口；真实接口只用于手动/Actions 预检，并且不得打印密钥。
- 不把不同接口路径但同一运营方计为双源；东方财富、腾讯、新浪的来源名称必须显式记录。

---

### Task 1: Freeze trading-day and public-source configuration

**Files:**
- Create: `data/a-share-trading-calendar-2026.json`
- Create: `data/fund-official-sources.json`
- Create: `data/industry-benchmark-map.json`
- Create: `tests/test_source_validation.py`
- Modify: `scripts/cloud_daily_update.py:35-145`

**Interfaces:**
- Produces `load_trading_calendar(path: Path) -> set[date]`, `business_date_for(run_at: datetime, open_days: set[date]) -> date`, and the CLI `python3 scripts/source_validation.py --check-config --no-write`.
- Produces configuration records with `code`, `source`, `url`, and `assetType`; later tasks pass these records to source adapters.

- [ ] **Step 1: Write failing calendar/config tests**

```python
def test_business_date_uses_explicit_open_days() -> None:
    open_days = {date(2026, 8, 21), date(2026, 8, 24)}
    self.assertEqual(
        validation.business_date_for(datetime(2026, 8, 25, 6, 15, tzinfo=HKT), open_days),
        date(2026, 8, 24),
    )

def test_fund_source_config_has_each_approved_fund_once() -> None:
    rows = validation.load_source_config(ROOT / "data/fund-official-sources.json")
    self.assertEqual({row["code"] for row in rows}, set(updater.FUND_ORDER))
    self.assertTrue(all(row["source"] == "基金管理人官网" for row in rows))
```

- [ ] **Step 2: Run the tests to confirm they fail because the calendar/config loaders do not exist**

Run: `python3 -m unittest tests.test_source_validation.SourceConfigTests -v`  
Expected: FAIL for missing `source_validation` module or missing loader functions.

- [ ] **Step 3: Add the minimal configuration and loaders**

Create `data/a-share-trading-calendar-2026.json` with this shape and fill every 2026 A-share open/closed day from the official exchange holiday notices before enabling the workflow:

```json
{"market":"A股","year":2026,"openDays":["2026-01-05"],"source":"上交所/深交所休市安排"}
```

Create one `fund-official-sources.json` row for each exact code in `FUND_ORDER`; each row must contain the manager’s direct official net-value URL, not a search URL:

```json
{"code":"012733","source":"基金管理人官网","url":"https://...","assetType":"指数/ETF联接","allowLagBusinessDays":0}
```

Create `industry-benchmark-map.json` records keyed by the canonical industry name; each record contains a non-empty `benchmarks` list of A-share index/ETF codes. Implement only the three loader/validator functions in new `scripts/source_validation.py`; before the A-share close (16:00 HKT), `business_date_for` starts from the previous calendar day, otherwise it starts from the run date, then walks backward through `open_days` and raises `ValueError` if no date exists within 10 calendar days. The CLI validates schema and makes HEAD/GET checks only; it neither writes data nor invokes Notion.

- [ ] **Step 4: Run the focused tests to confirm they pass**

Run: `python3 -m unittest tests.test_source_validation.SourceConfigTests -v`  
Expected: PASS; test data proves Monday 06:15 maps to the prior open day and all 12 configured fund codes are unique.

- [ ] **Step 5: Perform a non-mutating live preflight for source configuration**

Run: `python3 scripts/source_validation.py --check-config --no-write`  
Expected: one `OK` or `ERROR` line per manager URL and per industry benchmark; any error stops this plan before workflow changes.

- [ ] **Step 6: Commit the configuration and validation primitives**

```bash
git add data/a-share-trading-calendar-2026.json data/fund-official-sources.json data/industry-benchmark-map.json scripts/source_validation.py tests/test_source_validation.py scripts/cloud_daily_update.py
git commit -m "feat: add verified daily source configuration"
```

### Task 2: Normalize sources and enforce two-source P0 validation

**Files:**
- Modify: `scripts/source_validation.py`
- Modify: `scripts/cloud_daily_update.py:305-425,909-1055,1600-1800`
- Modify: `tests/test_source_validation.py`

**Interfaces:**
- Consumes config records from Task 1 and source responses normalized as dictionaries.
- Produces `QuoteRecord`, `ValidationIssue`, `validate_quote_pair(primary, secondary, business_date) -> list[ValidationIssue]`, `validate_fund_pair(primary, secondary, business_date, allowed_lag) -> list[ValidationIssue]`, and `validate_industry_rows(rows, benchmark_map, business_date) -> list[ValidationIssue]`.

- [ ] **Step 1: Write failing P0 validation tests**

```python
def test_quote_pair_rejects_disagreed_close() -> None:
    primary = {"source":"东方财富","code":"002837","date":"2026-08-24","close":42.00,"prevClose":41.00,"day":2.44}
    secondary = {"source":"腾讯财经","code":"002837","date":"2026-08-24","close":43.00,"prevClose":41.00,"day":4.88}
    issues = validation.validate_quote_pair(primary, secondary, date(2026, 8, 24))
    self.assertEqual(issues[0].field, "close")

def test_qdii_allows_configured_lag_but_domestic_fund_does_not() -> None:
    qdii_issues = validation.validate_fund_pair(
        {"code":"100055","date":"2026-08-18","nav":1.2345},
        {"code":"100055","date":"2026-08-18","nav":1.2345},
        date(2026, 8, 25), 5,
    )
    domestic_issues = validation.validate_fund_pair(
        {"code":"012733","date":"2026-08-18","nav":1.2345},
        {"code":"012733","date":"2026-08-18","nav":1.2345},
        date(2026, 8, 25), 0,
    )
    self.assertEqual(qdii_issues, [])
    self.assertEqual(domestic_issues[0].field, "navDate")
```

- [ ] **Step 2: Run the focused tests to confirm they fail**

Run: `python3 -m unittest tests.test_source_validation.P0ValidationTests -v`  
Expected: FAIL because pair validators and issue records are absent.

- [ ] **Step 3: Implement only pure validation rules and normalized adapters**

Add immutable `NamedTuple` or `dataclass` records in `source_validation.py`. Enforce exact limits: quote dates equal `businessDate`; close difference is at most `max(0.01, primary.close * 0.0015)`; day difference is at most `0.10`; ordinary funds have zero business-day lag; QDII uses its config value; all fund pairs reject NAV difference above `0.0001`; every selected industry has at least one configured benchmark and a verified `businessDate`.

Add `fetch_tencent_quote(symbol)` and `fetch_sina_quote(symbol)` in `cloud_daily_update.py`, each returning the shared normalized record or raising a source-specific exception. Do not change daily scoring in this task. Add `source` to current 东方财富 stock/fund records and retain the raw date returned by each source.

- [ ] **Step 4: Run focused tests and regression tests**

Run: `python3 -m unittest tests.test_source_validation.P0ValidationTests tests.test_module7_radar -v`  
Expected: PASS; a single-source, divergent or stale P0 record cannot pass validation.

- [ ] **Step 5: Commit source normalization and P0 validation**

```bash
git add scripts/source_validation.py scripts/cloud_daily_update.py tests/test_source_validation.py
git commit -m "feat: validate critical market data across free sources"
```

### Task 3: Create candidate batches, retry only failed sources, and preserve the last release

**Files:**
- Create: `data/last-run-status.json`
- Modify: `scripts/cloud_daily_update.py:2296-2330,3300-3325`
- Modify: `scripts/source_validation.py`
- Modify: `tests/test_daily_release.py`

**Interfaces:**
- Consumes `ValidationIssue` from Task 2 and the last verified `market-data.json` payload.
- Produces `ReleaseDecision(status: Literal["已验证发布", "待重试", "发布失败"], failed_modules: list[str], failed_fields: list[str])`, `collect_candidate(...)`, `retry_until_deadline(...)`, and `write_run_status(...)`.

- [ ] **Step 1: Write failing candidate/retry tests with a deterministic clock**

```python
def test_failed_candidate_keeps_last_verified_payload_after_deadline() -> None:
    last_verified = {"v2": {"batchId": "verified-20260824", "businessDate": "2026-08-24", "releaseStatus": "已验证发布"}}
    outcome = release.retry_until_deadline(
        run_at=hkt("2026-08-25T06:15:00"),
        collect=lambda _: release.CandidateResult(data={}, issues=[release.issue("industry", "boardScan")]),
        last_verified=last_verified,
        sleep=lambda _: None,
    )
    self.assertEqual(outcome.decision.status, "发布失败")
    self.assertEqual(outcome.published_data, last_verified)
    self.assertEqual(outcome.status["lastVerifiedBatchId"], "verified-20260824")

def test_candidate_publishes_when_second_attempt_has_no_p0_issues() -> None:
    outcomes = iter([[release.issue("stocks", "002837")], []])
    result = release.retry_until_deadline(hkt("2026-08-25T06:15:00"), lambda _: release.CandidateResult({}, next(outcomes)), {"v2": {}}, lambda _: None)
    self.assertEqual(result.decision.status, "已验证发布")
    self.assertEqual(result.attempts, 2)
```

- [ ] **Step 2: Run the candidate/retry tests to confirm they fail**

Run: `python3 -m unittest tests.test_daily_release.CandidateReleaseTests -v`  
Expected: FAIL because the candidate/retry API does not exist.

- [ ] **Step 3: Implement the release boundary without changing published data on failure**

Move current `build_dashboard()` orchestration behind `collect_candidate(run_at, business_date, configs)`. Add a pure retry coordinator that invokes collection at the exact attempt offsets `[0, 20, 40, 60]` minutes and stops all collection once the HKT deadline is reached. It retries only source keys returned in `ValidationIssue.source` and reruns the dependent P0 validator.

On success, attach `v2.releaseStatus = "已验证发布"`, `runDate`, `businessDate`, `attempt`, and source validation summaries to the candidate. On deadline failure, do not call `DATA_PATH.write_text`; write only `data/last-run-status.json` with the exact fields defined in the spec and return the unmodified last verified payload to the publisher.

- [ ] **Step 4: Run focused and full Python tests**

Run: `python3 -m unittest tests.test_daily_release tests.test_source_validation -v && python3 -m unittest discover -s tests -v`  
Expected: PASS; no test performs a real network request and the 07:15 result preserves the last verified batch.

- [ ] **Step 5: Commit candidate batching and retry policy**

```bash
git add data/last-run-status.json scripts/cloud_daily_update.py scripts/source_validation.py tests/test_daily_release.py
git commit -m "feat: retain verified batches when daily validation fails"
```

### Task 4: Render release status consistently in the dashboard and Notion

**Files:**
- Modify: `scripts/generate_dashboard_data.py`
- Modify: `dashboard/app/page.tsx`
- Modify: `dashboard/app/globals.css`
- Modify: `scripts/notion_visible_pages.py`
- Modify: `tests/test_daily_release.py`
- Modify: `tests/test_module7_radar.py`
- Modify: `tests/test_module7_coded_action_radar.py`

**Interfaces:**
- Consumes `v2.releaseStatus`, `v2.batchId`, `v2.businessDate`, `last-run-status.json` and existing fail-closed `dataQuality`.
- Produces dashboard snapshot fields `releaseStatus`, `lastVerifiedBusinessDate`, `failedModules`, `failedFields`, and Notion managed blocks with the same values.

- [ ] **Step 1: Write failing UI-contract and Notion-block tests**

```python
def test_failed_run_exports_last_verified_batch_without_action_text() -> None:
    payload = {"v2": {"batchId": "verified-20260824", "businessDate": "2026-08-24", "releaseStatus": "已验证发布"}}
    status = {"releaseStatus": "发布失败", "businessDate": "2026-08-25", "failedFields": ["industry.boardScan"], "lastVerifiedBusinessDate": "2026-08-24"}
    snapshot = generator.dashboard_snapshot(payload, status)
    self.assertEqual(snapshot["releaseStatus"], "发布失败")
    self.assertEqual(snapshot["lastVerifiedBusinessDate"], "2026-08-24")
    self.assertEqual(snapshot["daily"]["action"], "数据核验")

def test_notion_failure_blocks_keep_verified_batch_and_name_failed_field() -> None:
    blocks = visible.failure_status_blocks({"failedFields": ["industry.boardScan"], "lastVerifiedBusinessDate": "2026-08-24"})
    self.assertIn("industry.boardScan", flatten_blocks(blocks))
    self.assertIn("最后已验证业务日期 2026-08-24", flatten_blocks(blocks))
```

- [ ] **Step 2: Run the display tests to confirm they fail**

Run: `python3 -m unittest tests.test_daily_release.ReleaseDisplayTests -v`  
Expected: FAIL because release-status export and Notion failure blocks are absent.

- [ ] **Step 3: Implement status-first display**

Make `generate_dashboard_data.py` read `data/last-run-status.json` when present and export it with the current verified snapshot. In `page.tsx`, render a dedicated top-level release banner before market-gate content: `已验证发布` shows batch/date; `发布失败` shows failed modules, failed fields, last verified date and `数据核验` without stock/fund/sector action language. Keep the existing field-completeness and decision-status distinction.

Add `failure_status_blocks(status)` to `notion_visible_pages.py`; it must insert a managed failure callout before the prior verified region and must not delete the prior verified data blocks. On success, render release status and batch ID in the same managed region.

- [ ] **Step 4: Run display tests, all tests and the production build**

Run: `python3 -m unittest tests.test_daily_release.ReleaseDisplayTests tests.test_module7_radar tests.test_module7_coded_action_radar -v && python3 -m unittest discover -s tests -v && npm run build --prefix dashboard`  
Expected: PASS; the built page typechecks with failure and success contracts.

- [ ] **Step 5: Commit release-status display**

```bash
git add scripts/generate_dashboard_data.py dashboard/app/page.tsx dashboard/app/globals.css scripts/notion_visible_pages.py tests/test_daily_release.py tests/test_module7_radar.py tests/test_module7_coded_action_radar.py dashboard/app/dashboard-data.ts
git commit -m "feat: show verified release status across dashboard and notion"
```

### Task 5: Publish through the corrected schedule and reconcile Notion state

**Files:**
- Modify: `.github/workflows/daily-update.yml`
- Modify: `scripts/cloud_daily_update.py:3028-3275`
- Modify: `tests/test_daily_release.py`

**Interfaces:**
- Consumes `ReleaseDecision` from Task 3 and the display status contract from Task 4.
- Produces an Actions sequence that skips publish on `发布失败`, publishes only `已验证发布`, and reconciles Notion after the Git push outcome.

- [ ] **Step 1: Write failing workflow/reconciliation tests**

```python
def test_workflow_uses_hong_kong_monday_to_friday_cron() -> None:
    workflow = (ROOT / ".github/workflows/daily-update.yml").read_text()
    self.assertIn('cron: "15 22 * * 0-4"', workflow)
    self.assertIn("timeout-minutes: 75", workflow)

def test_failed_decision_does_not_call_verified_notion_sync() -> None:
    calls = []
    release.publish_decision(release.ReleaseDecision("发布失败", [], ["industry.boardScan"]), sync_verified=lambda _: calls.append("notion"), write_data=lambda _: calls.append("data"))
    self.assertEqual(calls, [])
```

- [ ] **Step 2: Run tests to confirm the schedule and publish guard fail**

Run: `python3 -m unittest tests.test_daily_release.WorkflowReleaseTests -v`  
Expected: FAIL because cron remains `1-5`, timeout is 20, and publish guard is absent.

- [ ] **Step 3: Implement the workflow and Notion state sequence**

Change the cron to `15 22 * * 0-4`, set `timeout-minutes: 75`, and have the update step invoke `python scripts/cloud_daily_update.py --deadline-hkt 07:15`. Make the script exit with a non-zero code only for internal/contract errors; a validated `发布失败` writes `last-run-status.json`, rebuilds the dashboard failure banner and exits zero so Actions can commit the status without replacing `market-data.json`.

For `已验证发布`, call `sync_notion_v2` with `releaseStatus="发布中"`, build and push the static site, then call a narrow Notion status updater that changes the same `batchId` to `已验证发布`. If the post-push Notion status update fails, write `last-run-status.json` with `notionReconciliation` failure and leave the candidate visibly `发布中`; the next run must reconcile that same batch before collecting a new one.

- [ ] **Step 4: Run deterministic local release simulations**

Run: `python3 scripts/cloud_daily_update.py --simulate p0-failure --deadline-hkt 07:15 --dry-run`  
Expected: no write to `data/market-data.json`; generated status reports `发布失败` and the last verified batch ID.

Run: `python3 scripts/cloud_daily_update.py --simulate verified-success --deadline-hkt 07:15 --dry-run`  
Expected: candidate reports `已验证发布` with a single batch ID; no real Notion request is made.

- [ ] **Step 5: Run full release verification and commit**

Run: `python3 -m unittest discover -s tests -v && python3 scripts/generate_dashboard_data.py && npm run build --prefix dashboard && git diff --check`  
Expected: PASS; working tree contains only intended source/config/generated dashboard changes.

```bash
git add .github/workflows/daily-update.yml scripts/cloud_daily_update.py tests/test_daily_release.py data/last-run-status.json dashboard/app/dashboard-data.ts
git commit -m "feat: publish only verified daily market batches"
```

## Final verification and release boundary

- [ ] Run all unit tests, both deterministic simulations and `npm run build --prefix dashboard` in the isolated worktree.
- [ ] Run `python3 scripts/cloud_daily_update.py --dry-run --deadline-hkt 07:15` once against live public sources. Record source failures without writing data or Notion.
- [ ] Inspect `market-data.json`, `last-run-status.json`, generated dashboard data and Notion block fixtures for one matching `batchId` and absence of action words on failure.
- [ ] Run `git diff --check` and `git status --short`; do not stage secrets, `node_modules`, generated cache, or user-owned files.
- [ ] Do not push, merge, manually dispatch Actions or write to Notion until the user gives a separate release approval after local verification.
