# Module 7 Coded Action Radar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add a code-backed stock/ETF candidate universe and a three-column Module 7 action radar without converting archived demonstration data into current investment conclusions.

**Architecture:** cloud_daily_update.py owns the fixed code catalog and builds codedOpportunityRadar beside the existing opportunityRadar. The dashboard generator exports only its display-safe fields; the Next.js page and Notion managed region render the same stocks, code-to-code relationships, and ETFs.

**Tech Stack:** Python 3.12 standard library and unittest, Next.js 16 / React / TypeScript, GitHub Actions, Notion REST sync.

**Spec:** docs/superpowers/specs/2026-08-23-module-7-coded-action-radar-design.md

## Global Constraints

- Candidate codes and names are fixed to the 7C/7D catalog in the spec.
- Never import the archived 2026-08-14 demonstration scores, prices, rankings, triggers, or directions.
- Research statuses are exactly 深挖, 验证中, 候补, or 数据不足.
- Execution actions are exactly 重仓, 中仓, 分批浅仓, 暂不追高, or 退出观望 only when executionEligible is true.
- With no validated execution model, executionAction is null and the UI says 执行引擎未启用.
- Preserve opportunityRadar, fundHoldings, and all 7A–7I child pages.
- Keep business date, equity data date, and fund NAV date distinct.

---

### Task 1: Build the fixed code and relationship contract

**Files:**
- Modify: scripts/cloud_daily_update.py, immediately above and inside build_opportunity_radar.
- Create: tests/test_module7_coded_action_radar.py

**Interfaces:**
- Produces: build_coded_opportunity_radar(data: dict[str, Any], as_of: date) -> dict[str, Any].
- Produces: data["codedOpportunityRadar"] with stocks, etfs, relationships, executionEngineStatus, and businessDate.
- Consumes: data["v2"] for business date, market gate, and data health.

- [ ] **Step 1: Write the failing catalog test**

~~~python
def test_coded_radar_has_spec_codes_and_no_actions_without_model(self) -> None:
    radar = updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 21))
    self.assertEqual([item["code"] for item in radar["stocks"]], [
        "002230", "601138", "300308", "300502", "600584",
        "000977", "002463", "002475", "603986", "688041",
    ])
    self.assertEqual([item["code"] for item in radar["etfs"]], [
        "512720", "516010", "512880", "515220", "515880",
        "562500", "588000", "516960", "512760", "159819",
    ])
    candidates = radar["stocks"] + radar["etfs"]
    self.assertTrue(all(item["researchStatus"] == "数据不足" for item in candidates))
    self.assertTrue(all(item["executionEligible"] is False for item in candidates))
    self.assertTrue(all(item["executionAction"] is None for item in candidates))
~~~

- [ ] **Step 2: Run it and verify the expected red failure**

Run: python3 -m unittest tests.test_module7_coded_action_radar -v

Expected: AttributeError because build_coded_opportunity_radar does not exist.

- [ ] **Step 3: Implement the minimal contract**

Add STOCK_CANDIDATES, ETF_CANDIDATES, and CODED_RELATIONSHIPS constants with the exact spec codes, names, themes, and six relationships. Implement the builder in spec order. Each output candidate has code, name, assetType, theme, researchStatus="数据不足", executionEligible=False, executionAction=None, actionRationale, nextTrigger, invalidCondition, dataDate=None, and dataStatus="候选代码待日更核验". Each relationship has expressionStrategy=None and relationshipStatus="关系待验证".

Call the builder in main() and sync_notion_v2() immediately after building opportunityRadar.

- [ ] **Step 4: Add and run the relationship-integrity test**

~~~python
def test_every_relationship_links_catalog_codes(self) -> None:
    radar = updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 21))
    stock_codes = {item["code"] for item in radar["stocks"]}
    etf_codes = {item["code"] for item in radar["etfs"]}
    for relation in radar["relationships"]:
        self.assertTrue(set(relation["stockCodes"]).issubset(stock_codes))
        self.assertIn(relation["etfCode"], etf_codes)
        self.assertIsNone(relation["expressionStrategy"])
        self.assertEqual(relation["relationshipStatus"], "关系待验证")
~~~

Run: python3 -m unittest tests.test_module7_coded_action_radar -v

Expected: both tests pass.

- [ ] **Step 5: Commit**

~~~bash
git add scripts/cloud_daily_update.py tests/test_module7_coded_action_radar.py
git commit -m "feat: add coded module 7 candidate contract"
~~~

### Task 2: Export the safe contract for the static dashboard

**Files:**
- Modify: scripts/generate_dashboard_data.py in dashboard_opportunity_radar and main().
- Modify: dashboard/app/dashboard-data.ts through the generator only.
- Modify: tests/test_module7_coded_action_radar.py

**Interfaces:**
- Produces: dashboard_coded_opportunity_radar(data: dict) -> dict.
- Produces: typed export codedOpportunityRadar.

- [ ] **Step 1: Write the failing exporter test**

~~~python
def test_dashboard_export_preserves_codes_and_null_actions(self) -> None:
    raw = {"codedOpportunityRadar": updater.build_coded_opportunity_radar({"v2": {}}, date(2026, 8, 21))}
    radar = generator.dashboard_coded_opportunity_radar(raw)
    self.assertEqual(radar["stocks"][0]["code"], "002230")
    self.assertEqual(radar["etfs"][-1]["code"], "159819")
    self.assertIsNone(radar["stocks"][0]["executionAction"])
    self.assertEqual(radar["executionEngineStatus"], "未启用")
~~~

- [ ] **Step 2: Run it and verify the expected red failure**

Run: python3 -m unittest tests.test_module7_coded_action_radar.OpportunityRadarTests.test_dashboard_export_preserves_codes_and_null_actions -v

Expected: AttributeError because dashboard_coded_opportunity_radar does not exist.

- [ ] **Step 3: Implement the exporter**

Add dashboard_coded_opportunity_radar. Export every candidate and relationship field required by the spec. In the generated TypeScript declaration, use nullable types for dataDate, executionAction, and expressionStrategy so the page cannot coerce an unavailable action into a label.

- [ ] **Step 4: Verify and commit**

~~~bash
python3 -m unittest tests.test_module7_coded_action_radar -v
python3 scripts/generate_dashboard_data.py
rg -n 'codedOpportunityRadar|002230|159819|未启用' dashboard/app/dashboard-data.ts
git add scripts/generate_dashboard_data.py dashboard/app/dashboard-data.ts tests/test_module7_coded_action_radar.py
git commit -m "feat: export coded opportunity radar"
~~~

Expected: all tests pass and the generated contract contains boundary codes plus null action support.

### Task 3: Render the three-column coded radar

**Files:**
- Modify: dashboard/app/page.tsx, import line and nx-opportunity section.
- Modify: dashboard/app/globals.css, opportunity layout classes.
- Modify: tests/test_module7_coded_action_radar.py

**Interfaces:**
- Consumes: codedOpportunityRadar from Task 2.
- Produces: desktop stock / relationship / ETF columns; mobile vertical order; a visible execution-engine boundary.

- [ ] **Step 1: Write the failing rendered-source test**

~~~python
def test_opportunity_page_has_three_coded_columns_and_engine_boundary(self) -> None:
    page = (Path(__file__).resolve().parents[1] / "dashboard/app/page.tsx").read_text(encoding="utf-8")
    self.assertIn("codedOpportunityRadar", page)
    self.assertIn("7C｜半年潜力股TOP10", page)
    self.assertIn("7E｜股票基金替代关系", page)
    self.assertIn("7D｜潜力基金ETF TOP10", page)
    self.assertIn("执行引擎未启用", page)
~~~

- [ ] **Step 2: Run it and verify the expected red failure**

Run: python3 -m unittest tests.test_module7_coded_action_radar.OpportunityRadarTests.test_opportunity_page_has_three_coded_columns_and_engine_boundary -v

Expected: assertion failure for codedOpportunityRadar.

- [ ] **Step 3: Implement the layout**

Import codedOpportunityRadar. Preserve the existing 06 title and research boundary. Add a system strip with business date, market gate, data health, and the engine status. Replace the current two panels with:
1. 7C｜半年潜力股TOP10: ten stock cards showing code, name, theme, research status, engine-not-enabled reason, next trigger, invalid condition, and data date.
2. 7E｜股票基金替代关系: all relationship rows showing stock codes, ETF code, relationship, and 关系待验证.
3. 7D｜潜力基金ETF TOP10: ten ETF cards using the same safe presentation.

Add a three-column CSS grid that becomes one ordered column at the existing mobile breakpoint. Reuse nx-glass and existing lamp/type tokens. Add no chart and no trading CTA.

- [ ] **Step 4: Verify and commit**

~~~bash
python3 -m unittest tests.test_module7_coded_action_radar -v
npm run build --prefix dashboard
git add dashboard/app/page.tsx dashboard/app/globals.css tests/test_module7_coded_action_radar.py
git commit -m "feat: render coded module 7 action radar"
~~~

Expected: tests pass and Next.js produces a successful static build.

### Task 4: Sync the contract to Notion and validate the workflow

**Files:**
- Modify: scripts/notion_visible_pages.py in _opportunity_radar.
- Modify: .github/workflows/daily-update.yml in the existing Python contract validation step.
- Modify: tests/test_module7_coded_action_radar.py

**Interfaces:**
- Consumes: data["codedOpportunityRadar"].
- Produces: managed Module 7 Notion blocks and workflow assertions for catalog integrity.

- [ ] **Step 1: Write the failing Notion-block test**

~~~python
def test_module7_notion_blocks_show_code_pools_without_fake_actions(self) -> None:
    data = {"v2": {"businessDate": "2026-08-21", "batchId": "test"}, "opportunityRadar": {"businessDate": "2026-08-21"}}
    data["codedOpportunityRadar"] = updater.build_coded_opportunity_radar(data, date(2026, 8, 21))
    text = " ".join(self.block_text(block) for block in visible.page_blocks("7", data, [], []))
    self.assertIn("7C｜半年潜力股TOP10", text)
    self.assertIn("002230", text)
    self.assertIn("7E｜股票基金替代关系", text)
    self.assertIn("512760", text)
    self.assertIn("7D｜潜力基金ETF TOP10", text)
    self.assertIn("执行引擎未启用", text)
    self.assertNotIn("重仓", text)
~~~

- [ ] **Step 2: Run it and verify the expected red failure**

Run: python3 -m unittest tests.test_module7_coded_action_radar.OpportunityRadarTests.test_module7_notion_blocks_show_code_pools_without_fake_actions -v

Expected: assertion failure for 7C｜半年潜力股TOP10.

- [ ] **Step 3: Implement the Notion tables and workflow checks**

Keep existing industry and fund-watch tables. Append 7C stock, 7E relationship, and 7D ETF tables. For each candidate render its executionAction when non-null; otherwise render 执行引擎未启用. In the workflow validation block, assert exactly ten six-digit stock codes, ten six-digit ETF codes, valid relationships, and that no candidate has an action when executionEngineStatus equals 未启用.

- [ ] **Step 4: Run the full local proof and commit**

~~~bash
python3 -m unittest discover -s tests -v
python3 scripts/cloud_daily_update.py --dry-run
python3 scripts/generate_dashboard_data.py
npm run build --prefix dashboard
git diff --check
git add scripts/notion_visible_pages.py .github/workflows/daily-update.yml tests/test_module7_coded_action_radar.py dashboard/app/dashboard-data.ts
git commit -m "feat: sync coded action radar to notion"
~~~

Expected: all tests pass; dry run does not write Notion; static build passes; whitespace check is clean.

### Task 5: Publish and read back both live surfaces

**Files:**
- Modify: /Users/chenyiming/Desktop/Codex 项目/金融投资中心/00_核心分析交接与决策台账.md after live verification.
- No application source changes expected.

**Interfaces:**
- Consumes: merged main and the Daily Investment Center Update workflow.
- Produces: successful workflow, updated managed Module 7 Notion page, updated public GitHub Pages dashboard, and a ledger evidence row.

- [ ] **Step 1: Rebase and publish the feature branch**

~~~bash
git fetch origin main
git rebase origin/main
git push -u origin codex/add-coded-module7-action-radar
~~~

Expected: no conflict and a clean diff against origin/main.

- [ ] **Step 2: Create, review, and merge one pull request**

Verify with git diff origin/main...HEAD --check. Create a pull request titled “feat: add coded module 7 action radar”, merge only after the Task 4 checks pass.

- [ ] **Step 3: Run and verify the production workflow**

Dispatch Daily Investment Center Update on main. Wait for terminal success. Read back the Module 7 Notion page and public dashboard. Both must contain 7C｜半年潜力股TOP10, 002230, 7E｜股票基金替代关系, 512760, 7D｜潜力基金ETF TOP10, and 执行引擎未启用. Neither may display a five-category action while the execution engine is disabled.

- [ ] **Step 4: Record evidence in the handoff ledger**

Add one ledger row with the merged commit, workflow URL, verified business date, and this fact: the coded candidate catalog is live; execution actions remain disabled pending an independently validated execution model.
