# Investment Market Dashboard

投资研究中心数字看板的独立静态站点仓库。

本仓库只负责托管数字看板页面，不存放 Codex skill、不存放其他业务项目，也不和 `fashion-image-tryon`、`fashion-nano-tryon` 等仓库混用。

## 当前定位

这个看板是“投资研究中心”的可视化入口，用来把 Notion 里的 6 个模块压缩成一个适合每天快速判断的数字化界面：

1. 每日简报：只看当天是进攻、防守还是等待。
2. 风控仪表盘：查看宏观与市场风险红绿灯。
3. 行业观察池：跟踪核心主线和候补轮动赛道。
4. 全球投资专家观点追踪：用外部高手观点做校验。
5. 我的基金持仓跟踪：用真实持仓做复盘和动作判断。
6. 每日财经新闻：跟踪全球高影响财经新闻，并辅助判断行情变量。

## 访问方式

当前仓库为 public，用于保证 GitHub Pages 地址可以正常打开。

GitHub Pages 地址：

```text
https://judebrisbylg-matthew.github.io/investment-market-dashboard/
```

当前推荐访问方式：

1. 直接打开 GitHub Pages 地址查看线上看板。
2. 本地打开 `index.html` 预览看板。
3. 每天自动更新后，将最新 `data/market-data.json` 和页面文件推送到这个仓库，使线上看板刷新。

说明：

- 当前 GitHub 账号计划不支持 private 仓库直接启用 GitHub Pages。
- 如果未来要同时满足“仓库私有”和“网页可访问”，需要升级 GitHub Pages 权限，或改用带登录保护的托管方案。

## 目录结构

```text
.
├── .github/
│   └── workflows/
│       └── daily-update.yml     # GitHub Actions 每天 05:00 HKT 自动更新
├── index.html                  # 数字看板主页面
├── src/
│   ├── standalone.css          # 页面样式，包含 PC/手机响应式布局
│   └── standalone.js           # 看板渲染逻辑
├── data/
│   └── market-data.json        # 每天自动生成的最新看板数据
├── scripts/
│   └── cloud_daily_update.py   # 云端更新 JSON、基金数据和 Notion 的脚本
├── docs/
│   └── GITHUB_ACTIONS_DEPLOYMENT.md
├── .nojekyll                   # 避免 GitHub Pages 按 Jekyll 处理静态资源
└── README.md                   # 当前说明文档
```

## GitHub Actions 云端自动更新

现在推荐使用 GitHub Actions 作为正式的每日更新入口，而不是依赖本机 Codex 一直在线。

自动更新规则：

```text
每天 05:00 HKT 自动执行
```

对应工作流：

```text
.github/workflows/daily-update.yml
```

对应脚本：

```text
scripts/cloud_daily_update.py
```

详细部署说明：

```text
docs/GITHUB_ACTIONS_DEPLOYMENT.md
```

云端任务会做 3 件事：

1. 更新 `data/market-data.json`，让 GitHub Pages 数字看板刷新。
2. 抓取基金最新净值、净值日期、日涨跌和近一周表现。
3. 使用 Notion API 按唯一键 upsert 6 个既有数据库，不新建重复子页面。

必须配置 GitHub Secrets：

```text
NOTION_TOKEN
NOTION_DB_DAILY
NOTION_DB_RISK
NOTION_DB_INDUSTRY
NOTION_DB_EXPERTS
NOTION_DB_FUNDS
NOTION_DB_NEWS
```

如果 Secret 没配齐，工作流会失败，不会假装更新成功。

## 数据来源

看板数据来自本地“投资研究中心/分析表格”里的 Excel 文件，再同步到 `data/market-data.json`。

核心表格包括：

- `1.每日简报.xlsx`
- `2.风控仪表盘.xlsx`
- `3.行业观察池.xlsx`
- `4.全球投资专家观点追踪.xlsx`
- `5.我的基金持仓跟踪.xlsx`
- `6.每日财经新闻.xlsx`

原则：

- 不能只改日期，必须同步真实最新数据。
- Notion 页面和本地 Excel 是主要工作台。
- GitHub Pages 看板是可视化展示层。
- `market-data.json` 是看板读取的最终结构化数据。

## 每日更新流程

每天凌晨 5:00 的自动流程应该按这个顺序执行：

1. 拉取/整理当天最新财经新闻。
2. 更新 6 个 Excel 表格里的当天数据。
3. 同步更新 Notion 里的 6 个子页面。
4. 从 Excel 或云端数据源重新生成 `data/market-data.json`。
5. 检查数字看板核心字段是否真实更新：
   - 日期
   - 今日灯号
   - 进攻/防守/等待
   - 风控红绿灯
   - 行业主线排序
   - 基金日涨跌、最新净值、最大回撤
   - 财经新闻排序、影响方向、影响级别、时间维度
6. 提交并推送本仓库，使 GitHub Pages 自动刷新。

本机 Codex 仍可用于手动复核和临时修正；正式定时任务以后以 GitHub Actions 为准。

## 推荐命令

从本地项目重新生成看板数据：

```bash
python3 market-dashboard/scripts/sync_dashboard_from_xlsx.py
```

进入本仓库并提交更新：

```bash
git status
git add index.html src/standalone.css src/standalone.js data/market-data.json README.md
git commit -m "Update dashboard data"
git push origin main
```

如果当天数据没有变化，不需要制造空提交。

## 更新判断标准

每天更新后至少检查 4 件事：

1. 页面顶部日期是否为当天。
2. 每日简报的灯号和动作判断是否与 Notion 一致。
3. 行业观察池是否按“核心主线在上、候补轮动在下”展示。
4. 我的基金持仓跟踪是否显示日涨跌，而不是周涨跌。

## 展示规则

### 风控仪表盘

- 展示风险温度、红绿灯统计、关键宏观指标。
- 空白区域尽量压缩，不做大面积装饰。
- 重点看美债、油价、美元指数、实际利率、信用利差、VIX、A股成交、估值分位。

### 行业观察池

- 只跟踪当前市场最相关的主线，不按持仓倒推。
- 分为“核心主线”和“候补轮动”。
- 候选池不固定。每天先扫描东方财富全市场概念板块和行业板块，再结合新闻、涨跌幅、上涨家数占比、主力净流入、换手活跃度、估值和风险重新排序。
- 同类题材只保留最强代表，避免机器人、减速器、人形机器人等高度重叠概念重复占位。
- 持仓基金只用于验证强弱，不得反向决定候选赛道。
- 全市场扫描会自动重试三次。休市或接口仍异常时，只沿用最近交易日的行业排名并明确标注原行情日期；其余五个模块继续更新，不能因单一数据源故障而整套停摆。
- 单日涨幅过大的板块默认转为“继续观察/止盈跟踪”，不能仅凭一天领涨直接给出“建议加仓”。

### 全球投资专家观点追踪

- 不把专家观点当作买卖指令。
- 只用于校验自己的判断是否偏离主流风险认知。
- 需要展示观点方向、证据强度和与当前判断是否一致。

### 我的基金持仓跟踪

- 重点展示日涨跌、最新净值、最大回撤和操作语言。
- 涨跌柱状图使用红色表示上涨，绿色表示下跌，符合国内金融视觉习惯。
- 每个基金号旁边要标注所属板块，避免只看代码看不出风险来源。

### 每日财经新闻

- 每天只保留影响力最大的 10 条。
- 新闻要服务于行情判断，不做普通资讯堆叠。
- 重点字段包括新闻类别、影响资产、影响方向、影响级别、时间维度、对应投资抓手、是否纳入每日简报。

## 移动端要求

页面必须同时适配 PC 和手机：

- PC 端适合横向总览。
- 手机端采用纵向卡片布局。
- 图表不能横向溢出。
- 关键卡片优先展示：每日判断、风控、行业主线、基金持仓、财经新闻。

## 仓库权限

当前状态：

- 仓库 visibility：public，用于保证 GitHub Pages 正常访问
- 用途：个人私享看板源码和数据托管
- 不开放 issue、wiki、discussion 作为协作入口
- 不与其他 skill 仓库混放
- 如果后续改回 private，当前 GitHub Pages 地址会失效

## 注意事项

- 本看板只用于市场观察、风险管理和复盘。
- 不构成确定性投资建议。
- 自动化更新必须校验真实数据来源，不能仅更新日期。
- 若 GitHub Pages 对私有仓库访问控制不能满足要求，应迁移到带登录权限的托管方式。
