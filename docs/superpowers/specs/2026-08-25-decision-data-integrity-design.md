# 决策数据完整性与止损展示设计

## 目标

在不接入新行情源、不补历史数据、不启用执行模型的前提下，阻止回退或待核验数据被呈现为当日行动指导，并让大看板与 Notion 使用相同、可解释的数据质量口径。

## 范围

- 保留现有数据抓取、候选代码池、赛道列表、基金持仓与 0–5 模块。
- 模块 7 保留 7C 股票代码、7E 关系和 7D ETF 代码，但明确作为候选名册；当前 20/20 候选没有日更行情时，不展示伪行动。
- 不新增股票/ETF 行情源、交易模型、回测、仓位算法或历史回填。

## 数据质量合同

现有 `v2.coverage` 改名为 `fieldCompleteness`（字段完整度），只说明字段是否存在，不能再被界面标为“数据健康”。

新增只读质量字段：

```ts
type DataQuality = {
  fieldCompleteness: number;
  blockingModules: string[];
  degradedModules: string[];
  decisionStatus: "可用" | "受限" | "不可用";
  decisionReason: string;
};
```

判定规则：

1. `sourceStatus.blockingModules` 非空时，`decisionStatus="不可用"`；市场闸门为“数据不足”。
2. 没有阻断、但任一模块状态为沿用/待核验时，`decisionStatus="受限"`。
3. 只有没有阻断且没有降级模块时，`decisionStatus="可用"`。
4. 页面总览显示“字段完整度”，同时单独显示决策状态和阻断原因；不再把完整度百分比称为数据健康。

## 止损展示规则

当 `decisionStatus` 不是“可用”时：

- 赛道表的执行灯保持灰灯；任何 `operation` 行动词都不作为当日结论展示。
- `opportunityRadar.industries[].operation` 输出固定文案“仅研究快照，待核验”，保留名称、历史分数、原始市场日期和回退原因。
- 日度摘要不得拼接“建议加仓”等赛道操作词；它只能显示“控制节奏，等待数据核验”与阻断模块名称。
- Notion 页面 7 使用同一份降级后的 `opportunityRadar`，不再将旧操作词写入“研究动作”。
- 模块 7 代码区的标题显示“候选名册｜20/20 未接入日更数据”，卡片仅保留代码、名称、主题、数据状态和“执行引擎未启用”；隐藏“依据 / 下一触发 / 失效条件”这些目前只会重复占位文案的内容。

## 交易日与回退数据

- 行业回退的 `marketDate` 必须不晚于 `latest_completed_market_date(as_of)`，且不得是周末。
- 不满足条件的旧赛道记录不计入可用性，也不输出其排名、分数或操作词；页面仅显示“赛道数据待核验”。
- 已有的真实基金净值、持仓行情和慢频宏观数据仍可展示其来源日期；它们不因行业阻断而被删除。

## 涉及文件

- `scripts/cloud_daily_update.py`：生成质量合同、交易日回退校验、灰灯时清除行动文案。
- `scripts/generate_dashboard_data.py`：导出质量合同与候选名册展示字段。
- `dashboard/app/page.tsx`、`dashboard/app/globals.css`：替换误导性“数据健康 96%”文案，显示阻断原因和候选名册降级态。
- `scripts/notion_visible_pages.py`：用同一降级文案同步页面 7。
- `tests/test_module7_radar.py`、`tests/test_module7_coded_action_radar.py`：覆盖合同、行动禁用、非交易日回退及 Notion/页面文案。

## 验收标准

1. 当行业源回退时，总览不得出现“数据健康 96%”；必须显示“字段完整度 96%”及“决策数据不可用：行业数据回退”。
2. 当市场闸门为“数据不足”时，页面与 Notion 不得出现“建议加仓”“暂不追高”等行动词。
3. 周末日期不会成为赛道的有效市场日期或可用性依据。
4. 模块 7 在无日更行情时明确显示“候选名册｜20/20 未接入日更数据”，且不显示五类执行动作。
5. 现有基金、持仓、风险来源日期继续展示，不被伪装为当日数据。
6. Python 全量测试、静态构建、日更干跑与 Notion 块测试通过。
