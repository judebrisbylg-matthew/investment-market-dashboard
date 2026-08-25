# 决策数据完整性防护 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task, with verification after every task.

**Goal:** 在不补历史、不新增数据源、不启用交易执行模型的前提下，阻止“回退/待核验”数据被展示为可行动结论；将字段完整度与决策可用性分开，并让大看板和 Notion 使用同一口径。

**Architecture:** 仍由 `cloud_daily_update.py` 生成唯一的数据质量契约。该契约先判断数据是否可用于决策，再生成受限的日报和 Module 7 雷达；导出器、网页与 Notion 只显示这个受限后的结果，不各自重新推断状态。

**Tech Stack:** Python 3.12 / 标准库 `unittest`、静态 JSON 导出、Next.js、Notion API 区块生成。

**Spec:** `docs/superpowers/specs/2026-08-25-decision-data-integrity-design.md`

## Global constraints

- 不补 2026-08-21 以前的历史数据；不新增行情源；不修改候选股票、ETF 或关系名册。
- 保留现有 `coverage`、`dataHealth` 字段以避免破坏旧消费者，但网页不再把 `coverage` 称为“数据健康”。新增字段是唯一的清晰展示口径。
- 所有“可行动”措辞仅在 `decisionStatus == "可用"` 时出现；`受限` 与 `不可用` 均采取 fail-closed 展示。
- 仅检查周末；法定节假日仍须由上游来源状态决定，不能伪造交易日判断。

## Task 1: Build an auditable data-quality contract and fail-closed daily/radar content

**Files:**
- Modify: `scripts/cloud_daily_update.py`
- Modify: `tests/test_module7_radar.py`

1. Add failing tests for the following contracts:
   - a payload with all display fields present but `blockingModules=["industry"]` has high `fieldCompleteness` and `decisionStatus == "不可用"`, with a readable industry fallback reason;
   - an industry fallback dated Saturday/Sunday is marked unresolved and does not contribute to industry availability;
   - when decision status is not available, `update_daily` contains no position/add/chase action phrases and instead explains that data must be verified;
   - `build_opportunity_radar` replaces each industry action with `仅研究快照，待核验` while retaining name, score, original market date, and fallback context.
2. Run `python3 -m unittest tests.test_module7_radar -v` from `automation-repo`; confirm the new tests fail for the missing quality boundary.
3. In `notion_v2_contract`, calculate existing coverage as `fieldCompleteness`, derive `dataQuality` with:
   - `fieldCompleteness`;
   - `blockingModules` and `degradedModules` from source status;
   - `decisionStatus`: `不可用` when a blocking module exists, `受限` when only degraded modules exist, otherwise `可用`;
   - `decisionReason` assembled from the actual blocking/degraded module names, never from inferred market direction.
4. Retain the legacy `coverage` value for compatibility, add `fieldCompleteness` and `dataQuality`, and keep `dataHealth` aligned with the availability state (`灰灯` for unavailable).
5. Add a small date-normalization helper used only by industry fallback handling: a fallback market date after the completed date or falling on Saturday/Sunday becomes `待核验`; its fallback message retains the original raw date for audit.
6. Make `update_daily` return a data-verification-only summary whenever `dataQuality.decisionStatus != "可用"`. It must not call the position/action text builders in that branch.
7. Make `build_opportunity_radar` carry `dataQuality`; in its unavailable/restricted branch, replace industry operations with the research-only wording and include the source/fallback status needed to explain why.
8. Re-run the focused test file until green.
9. Commit only these updater and test changes with message `fix: fail closed when decision data is unavailable`.

## Task 2: Export and render separate completeness and decision-availability states

**Files:**
- Modify: `scripts/generate_dashboard_data.py`
- Modify: `dashboard/app/page.tsx`
- Modify: `dashboard/app/globals.css` only if needed for existing layout classes
- Modify: `tests/test_module7_radar.py`

1. Add failing exporter/UI-source tests that assert:
   - dashboard data contains `fieldCompleteness`, `decisionStatus`, and `decisionReason`;
   - the page labels the percentage as `字段完整度`, separately renders `决策数据不可用`/reason, and no longer labels the percentage `数据健康`;
   - when all 20 coded candidates lack daily data, Module 7 renders `候选名册｜20/20 未接入日更数据` and does not show generic action rationale/trigger/invalid-condition text.
2. Run the focused test file and confirm failures are specific to absent export/render fields.
3. Update `dashboard_opportunity_radar` and main snapshot generation to export the new data-quality fields as explicit UI values. Preserve legacy serialized fields only for compatibility.
4. Update the dashboard summary card to show two distinct facts:
   - `字段完整度` percent;
   - `决策数据` state plus actual reason.
   Do not turn high completeness into a health claim.
5. In the Module 7 view, calculate the candidate count from `dataStatus == "候选代码待日更核验"`, render the exact catalog heading, retain code/name/theme/status/engine-off, and hide the three non-actionable explanatory lines for those candidates.
6. Use existing CSS conventions; add only the minimum class rules needed to keep the two quality facts legible.
7. Re-run focused tests, then `npm run build --prefix dashboard`.
8. Commit only exporter, dashboard, CSS, and related test changes with message `fix: distinguish field completeness from decision availability`.

## Task 3: Make Notion mirror the fail-closed contract and validate the release path

**Files:**
- Modify: `scripts/notion_visible_pages.py`
- Modify: `tests/test_module7_radar.py`
- Modify: `tests/test_module7_coded_action_radar.py`

1. Add failing tests that build page 7 from an unavailable contract and assert:
   - it displays the same `字段完整度` and decision-unavailable reason as the dashboard contract;
   - industry rows never contain legacy action phrases such as `建议加仓` or `暂不追高`;
   - coded stock/ETF sections use `候选名册｜20/20 未接入日更数据` and preserve codes without converting them to actions.
2. Run both Module 7 test files and confirm failures are only presentation-contract gaps.
3. Update `_opportunity_radar` / page-7 block construction to consume the already-sanitized radar and `dataQuality` fields. It must not recreate actions from raw `industryWatch` records.
4. Render completeness and decision availability as separate visible facts, and use the same coded-candidate catalog wording as the web dashboard.
5. Re-run all unit tests: `python3 -m unittest discover -s tests -v`.
6. Run the deterministic generation path without external writes:
   - `python3 scripts/cloud_daily_update.py --dry-run`;
   - `python3 scripts/generate_dashboard_data.py`;
   - `npm run build --prefix dashboard`.
   Inspect generated JSON to confirm an industry fallback produces `decisionStatus: 不可用`, a field-completeness percentage, no actionable daily text, and 20/20 Module 7 candidate catalog status.
7. Review `git diff --check` and `git status --short`; ensure no generated output, secrets, or user-owned files are staged.
8. Commit only Notion renderer and related tests with message `fix: mirror decision data safeguards in notion`.

## Final verification and handoff

1. Run `python3 -m unittest discover -s tests -v` and `npm run build --prefix dashboard` from the isolated worktree.
2. Compare the generated `dashboard/public/market-data.json` with the acceptance criteria in the spec; check that the same quality wording appears in the page source and Notion block test output.
3. Report separately:
   - code/test/build evidence;
   - any live source fetch limitation encountered during dry run;
   - files changed and commit IDs.
4. Do not push, merge, trigger Actions, or update Notion in this implementation plan. Those require a separate explicit release approval after the local checks pass.
