# GitHub Actions 云端自动更新部署说明

这份说明用于把“投资研究中心”从本机 Codex 定时任务迁移到 GitHub Actions。迁移后，即使本机没有打开 Codex，GitHub 也会每天自动执行更新。

## 一、最终目标

每天 05:00 HKT 自动完成：

1. 更新 `data/market-data.json`
2. 同步 GitHub Pages 数字看板
3. 用 Notion API 更新“投资研究中心”下 6 个既有数据库
4. 不新建重复子页面
5. 不生成日期版副本文件
6. 不只改日期，必须保留真实来源日期或滞后说明

线上看板地址：

```text
https://judebrisbylg-matthew.github.io/investment-market-dashboard/
```

## 二、仓库定位

仓库：

```text
judebrisbylg-matthew/investment-market-dashboard
```

这个仓库只放投资研究中心数字看板和云端自动更新脚本，不放任何 fashion try-on skill，也不和其他项目混在一起。

关键文件：

```text
.github/workflows/daily-update.yml      # GitHub Actions 定时任务
scripts/cloud_daily_update.py           # 云端更新脚本
data/market-data.json                   # 数字看板读取的数据
index.html                              # GitHub Pages 主页面
src/standalone.css                      # 静态样式
src/standalone.js                       # 静态渲染脚本
docs/GITHUB_ACTIONS_DEPLOYMENT.md       # 本说明
```

## 三、定时规则

GitHub Actions 使用 UTC 时间。

```yaml
cron: "0 21 * * *"
```

含义：

```text
UTC 每天 21:00 = 香港/北京时间次日 05:00
```

也就是说，你本地不需要打开 Codex，GitHub 会在每天凌晨 5 点执行。

## 四、Notion 同步方式

脚本不会每天新建页面。它只更新你已经建好的 6 个数据库：

1. `1.每日简报`
2. `2.风控仪表盘`
3. `3.行业观察池`
4. `4.全球投资专家观点追踪`
5. `5.我的基金持仓跟踪`
6. `6.每日财经新闻`

### 唯一键规则

| 模块 | 唯一键 | 行为 |
| --- | --- | --- |
| 每日简报 | 日期 | 当天已存在则更新，不存在则新增当天记录 |
| 风控仪表盘 | 更新日期 + 监控指标 | 同一指标当天只保留一条 |
| 行业观察池 | 更新日期 + 行业/赛道 | 同一赛道当天只保留一条 |
| 全球投资专家观点追踪 | 更新日期 + 专家/机构 | 同一专家当天只保留一条 |
| 我的基金持仓跟踪 | 报表更新日期 + 基金代码 | 同一基金当天只保留一条 |
| 每日财经新闻 | 新闻日期 + 新闻标题 | 同一新闻当天只保留一条 |

### 手工字段保护

脚本只写入它能识别的自动字段。你后续在 Notion 里新增的人工判断、备注、复盘结论，不会被脚本主动清空。

如果你改了字段名，脚本会跳过无法识别的字段，而不是乱写到别的列里。字段名大改之后，需要同步修改 `scripts/cloud_daily_update.py` 的字段映射。

## 五、必须配置的 GitHub Secrets

进入 GitHub 仓库：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

需要添加：

```text
NOTION_TOKEN
NOTION_DB_DAILY
NOTION_DB_RISK
NOTION_DB_INDUSTRY
NOTION_DB_EXPERTS
NOTION_DB_FUNDS
NOTION_DB_NEWS
```

说明：

| Secret | 内容 |
| --- | --- |
| `NOTION_TOKEN` | Notion integration token |
| `NOTION_DB_DAILY` | `1.每日简报` 的 database id |
| `NOTION_DB_RISK` | `2.风控仪表盘` 的 database id |
| `NOTION_DB_INDUSTRY` | `3.行业观察池` 的 database id |
| `NOTION_DB_EXPERTS` | `4.全球投资专家观点追踪` 的 database id |
| `NOTION_DB_FUNDS` | `5.我的基金持仓跟踪` 的 database id |
| `NOTION_DB_NEWS` | `6.每日财经新闻` 的 database id |

当前工作流里 `REQUIRE_NOTION=true`。如果这些 Secret 没配齐，任务会失败，而不是假装更新成功。

## 六、Notion Token 获取方式

1. 打开 Notion Integrations 页面
2. 新建一个 internal integration
3. 复制 integration token
4. 把 token 填入 GitHub Secret：`NOTION_TOKEN`
5. 回到 Notion，把“投资研究中心”和 6 个数据库 share 给这个 integration

如果没有 share，GitHub Actions 会报 Notion 权限错误。

## 七、Database ID 获取方式

打开每个 Notion 数据库页面，复制 URL。

一般 URL 里会有一段 32 位 ID，例如：

```text
https://www.notion.so/xxx/57a88e4152f547eb9171078d1702aa5d?v=...
```

整理为：

```text
57a88e41-52f5-47eb-9171-078d1702aa5d
```

填到对应的 GitHub Secret。

## 八、当前云端脚本的数据能力

### 已自动抓取

`5.我的基金持仓跟踪` 会通过东方财富/天天基金公开接口抓取基金净值：

- 最新净值
- 净值日期
- 日涨跌
- 近一周涨跌
- 操作语言
- 操作原因

目前包含 13 只基金：

```text
013180, 004432, 006751, 100055, 014344, 012733, 519704,
018896, 018125, 023531, 018734, 377240, 007818
```

### 保守复核/沿用

以下数据会沿用当前结构并写入当天复核日期：

- 风控仪表盘
- 行业观察池
- 全球投资专家观点追踪
- 每日财经新闻

原因是这些模块依赖新闻、研究判断和多源交叉验证，不能用单一免费接口简单替代。脚本不会编造无法确认的事实；抓不到可靠来源时，会保留待核验或来源滞后说明。

后续如果要做到完全云端实时新闻抓取，建议接入稳定新闻源或付费数据源，例如：

- Reuters/Bloomberg 授权源
- 官方机构 RSS
- CNBC/WSJ/Barron's 等稳定订阅源
- 东方财富/财联社/证券时报等中文财经源

## 九、手动运行

在 GitHub 页面：

```text
Actions -> Daily Investment Center Update -> Run workflow
```

手动触发后检查：

1. Actions 是否绿色成功
2. `data/market-data.json` 是否出现新提交
3. GitHub Pages 是否正常打开
4. Notion 6 个数据库是否出现当天记录
5. 是否没有重复页面、重复数据库、重复同名记录

## 十、失败排查

### 1. Actions 红色失败

优先看日志里是否有：

```text
missing Notion secrets
```

这代表 Secret 没配齐。

### 2. Notion 403 或 object not found

通常是：

- database id 填错
- integration 没有被 share 到 Notion 页面
- token 填错

### 3. GitHub Pages 页面空白

检查：

- `index.html` 是否直接引用 `src/standalone.css` 和 `src/standalone.js`
- `data/market-data.json` 是否存在
- 浏览器是否缓存旧文件

当前页面已使用：

```text
./src/standalone.css?v=...
./src/standalone.js?v=...
fetch("./data/market-data.json?t=" + Date.now(), { cache: "no-store" })
```

这是为了避免 GitHub Pages 缓存导致白屏或旧数据。

### 4. Notion 有空字段

原因通常是 Notion 字段名和脚本字段映射不一致。

处理方式：

1. 先确认 Notion 表头没有被改名
2. 再改 `scripts/cloud_daily_update.py` 里的字段映射
3. 不要让脚本自动猜字段，避免写错列

### 5. 某天基金净值没更新

基金公司或 QDII 可能延迟披露。正确做法是：

- `报表更新日期` 写当天
- `净值日期` 写真实披露日期
- 操作原因里说明数据来源滞后

不能把旧净值伪装成当天净值。

## 十一、日常维护规则

1. Notion 页面结构可以改，但字段名大改后要同步改脚本。
2. 每日新增数据必须按唯一键覆盖，不能重复创建子页面。
3. GitHub Pages 只负责展示，不作为人工编辑入口。
4. 如果看板白屏，优先检查 JSON 和静态资源缓存。
5. 如果财经新闻质量不够，优先升级新闻源，而不是让脚本编造。

## 十二、当前仍需人工完成

需要在 GitHub 仓库 Secrets 里填入 Notion token 和 6 个 database id。

这一步完成后，GitHub Actions 才能真正无本机依赖地每天同步 Notion。
