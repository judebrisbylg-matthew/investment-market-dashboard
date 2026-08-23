import type { CSSProperties } from "react";
import type { Metadata } from "next";
import { codedOpportunityRadar, events, evidence, funds, risks, sectors, snapshot, stocks } from "./dashboard-data";
import { EvidenceTerminal } from "./evidence-terminal";
import { LabelTip } from "./info-tip";

export const metadata: Metadata = {
  title: "每日综合大看板｜投资研究中心 2.0",
  description: "以量化决策网络为核心的科技增强型投资研究指挥舱。",
};

type Tone = "cyan" | "purple" | "green" | "yellow" | "red" | "gray";

function Lamp({ tone, text }: { tone: Tone; text: string }) {
  return <span className={`nx-lamp nx-${tone}`}><i />{text}</span>;
}

function lightText(value: string) {
  return value === "red" ? "红灯" : value === "yellow" ? "黄灯" : value === "gray" ? "灰灯" : "绿灯";
}

function executeText(value: string) {
  return value === "green" ? "研究" : value === "red" ? "停止" : value === "gray" ? "数据不足" : "等待";
}

function stockLampText(value: string) {
  return value === "red" ? "高风险" : value === "yellow" ? "观察" : value === "green" ? "偏强" : "数据不足";
}

function riskHelp(name: string) {
  if (name.includes("美债收益率")) return "全球无风险利率与资产估值的折现锚。持续上升会压低成长股估值，并提高企业融资成本。";
  if (name.includes("北向资金")) return "观察境外资金参与A股的方向与持续性。单日流入流出噪声较大，应结合月度口径和市场趋势判断。";
  if (name.includes("美联储")) return "观察美联储政策、利率路径和资产负债表方向。偏鹰或流动性收缩通常压制高估值资产，偏鸽则有助于风险偏好修复。";
  if (name.includes("美元指数")) return "衡量美元相对主要货币的强弱。美元快速走强通常压制非美资产、商品及新兴市场流动性。";
  if (name.includes("实际利率")) return "名义利率扣除通胀后的真实资金成本。实际利率越高，黄金和高估值成长资产承压通常越明显。";
  if (name.includes("信用利差")) return "衡量企业债相对国债的额外风险补偿。利差扩大说明信用压力升高，风险偏好可能恶化。";
  if (name.includes("VIX")) return "美股隐含波动率指标，是全球避险情绪温度计。快速上升意味着市场对短期波动和尾部风险的定价增加。";
  if (name.includes("全球流动性")) return "观察主要央行资产负债表与美元流动性的合成变化。改善通常利好风险资产，但不是独立买入信号。";
  if (name.includes("A股成交") || name.includes("两市成交")) return "衡量A股交易活跃度与增量资金承接。成交放大需同时观察上涨家数和趋势，避免把放量下跌误判为资金进攻。";
  if (name.includes("港股成交")) return "衡量港股市场的资金承接与交易活跃度。应与南向资金、外资行为和恒生指数趋势一起判断。";
  if (name.includes("轮动")) return "衡量强势行业的数量、持续性和扩散程度。少数赛道独强代表结构性行情，不能等同于全面风险偏好改善。";
  if (name.includes("估值")) return "判断核心资产的拥挤程度和安全边际。估值偏高会降低赔率，但不能脱离盈利趋势单独使用。";
  return "用于判断市场风险承受能力的量化指标。需结合灯号阈值、数据日期及其他指标共同解读，不能单独触发交易。";
}

export default function ConceptB() {
  const moduleNodes = snapshot.moduleStatus;
  const marketGate = String(snapshot.marketGate);
  const dataHealth = String(snapshot.dataHealth);
  const healthTone: Tone = dataHealth === "绿灯" ? "green" : dataHealth === "灰灯" ? "gray" : "yellow";
  return (
    <main className="nexus-dashboard">
      <aside className="nx-rail">
        <a className="nx-logo" href="#nx-top"><b>IQ</b><span>投资研究<br />中心 2.0</span></a>
        <nav aria-label="每日综合大看板导航">
          <a className="active" href="#nx-top"><i>00</i><span>总控</span></a>
          <a href="#nx-risk"><i>01</i><span>风控</span></a>
          <a href="#nx-sector"><i>02</i><span>赛道</span></a>
          <a href="#nx-evidence"><i>03</i><span>验证</span></a>
          <a href="#nx-events"><i>04</i><span>事件</span></a>
          <a href="#nx-holdings"><i>05</i><span>持仓</span></a>
          <a href="#nx-opportunity"><i>06</i><span>机会</span></a>
        </nav>
        <div className="nx-rail-health"><div className="nx-mini-ring"><strong>{snapshot.coverage}%</strong></div><span>数据健康</span><small>{snapshot.dataHealth} · {snapshot.businessDate}</small></div>
      </aside>

      <section className="nx-workspace" id="nx-top">
        <header className="nx-header">
          <div><span className="nx-overline">DAILY QUANT DECISION SYSTEM</span><h1>每日综合大看板</h1><p>投资研究中心 2.0 · QUANT DASHBOARD</p></div>
          <div className="nx-header-tools"><div><b>06:15</b><span>HKT</span></div><small>{snapshot.businessDate}<br />自动批次</small></div>
        </header>

        <section className="nx-summary-grid">
          <article className="nx-glass nx-summary-gate">
            <header><LabelTip label="系统市场闸门 / RISK GATE" text="由12项风控指标、数据健康度与硬性门槛共同决定总风险上限。它管‘能承担多少风险’，不直接代表市场看空或看多。" align="left" /><Lamp tone={healthTone} text={snapshot.dataHealth} /></header>
            <div className="nx-summary-gate-body">
              <div className="nx-summary-ring" style={{ "--risk": snapshot.riskScore } as CSSProperties}><div><strong>{snapshot.riskScore}</strong><span>/ 100</span><small>{snapshot.marketGate}</small></div></div>
              <div><h2>{snapshot.daily.action}</h2><p>{snapshot.daily.positionAdvice}</p></div>
            </div>
            <footer><span><i className="nx-dot nx-green" />{snapshot.lightCounts.green} 绿</span><span><i className="nx-dot nx-yellow" />{snapshot.lightCounts.yellow} 黄</span><span><i className="nx-dot nx-red" />{snapshot.lightCounts.red} 红</span><span><i className="nx-dot nx-gray" />{snapshot.lightCounts.gray} 灰</span></footer>
          </article>

          <article className="nx-glass nx-summary-action">
            <header><LabelTip label="今日总动作 / ACTION" text="综合风控闸门、赛道执行灯和持仓风险后的方向提示。它是研究约束，不是自动交易指令。" align="left" /><b>{snapshot.daily.action}</b></header>
            <h2>{marketGate === "风险允许" ? "研究优先，" : "控制节奏，"}<em>{snapshot.daily.action}</em></h2>
            <p>{snapshot.daily.needAction}</p>
            <div><span><b>01</b>不追高</span><span><b>02</b>看确认</span><span><b>03</b>守纪律</span></div>
          </article>

          <article className="nx-glass nx-summary-fresh">
            <header><LabelTip label="数据新鲜度 / FRESHNESS" text="检查五大模块的业务日期是否同步。过期、待核验或缺失时自动降级，防止用旧数据做当日判断。" align="left" /><Lamp tone={healthTone} text={snapshot.dataHealth} /></header>
            <div>{snapshot.freshness.map(({name,date,width}) => <div className="nx-summary-stream" key={name}><span>{name}</span><i><b style={{ width: `${width}%` }} /></i><strong>{date}</strong></div>)}</div>
            <small>数据截至 {snapshot.asOf}；过期或待核验字段自动降级</small>
          </article>

          <article className="nx-glass nx-summary-modules">
            <header><LabelTip label="五模块脉冲 / MODULES" text="快速汇总风控、赛道、验证、事件和持仓的当前状态。任一核心模块降级，都会收紧今日执行边界。" align="right" /><b>5 MODULES</b></header>
            <div className="nx-module-ring"><div><strong>{snapshot.lightCounts.yellow + snapshot.lightCounts.red}</strong><span>项风险关注</span></div></div>
            <div className="nx-module-status">{moduleNodes.map(node => <span key={node.code}>{node.name}<b className={`nx-${node.tone}`}>{node.state}</b></span>)}</div>
          </article>
        </section>

        <section className="nx-decision-strip">
          <div><span>01</span><p><b>今天能不能承担风险？</b>{snapshot.daily.marketJudgement}</p></div>
          <div><span>02</span><p><b>优先研究谁？</b>{snapshot.daily.nextReview}</p></div>
          <div><span>03</span><p><b>现有持仓先看什么？</b>{snapshot.daily.riskPoint}</p></div>
        </section>

        <section className="nx-section" id="nx-risk">
          <header className="nx-section-head"><div><span>01 / MARKET RISK MATRIX</span><h2>风险雷达阵列</h2></div><p><LabelTip label="12项日常指标 · 2项硬闸门" text="绿灯=未限制风险暴露；黄灯=限制新增；红灯=停止新增或降风险；灰灯=数据不足。硬闸门可以覆盖普通指标的结论。" align="right" /></p></header>
          <div className="nx-risk-board">
            <article className="nx-glass nx-risk-radar"><div className="nx-radar-grid"><i /><i /><i /><i /></div><div className="nx-radar-shape" /><div className="nx-radar-label r1">流动性 74</div><div className="nx-radar-label r2">波动 54</div><div className="nx-radar-label r3">趋势 22</div><div className="nx-radar-label r4">宽度 9</div><div className="nx-radar-label r5">估值 75</div><strong>风险偏高</strong><small>趋势与宽度构成主要约束</small></article>
            <div className="nx-risk-cells">{risks.map(([name,value,signal,threshold,refresh,sourceDate],i) => <article className={`nx-risk-cell nx-edge-${signal}`} key={name}><header><span>{String(i+1).padStart(2,"0")}</span><Lamp tone={signal as Tone} text={lightText(String(signal))} /></header><h3><LabelTip label={String(name)} text={riskHelp(String(name))} align="left" /></h3><strong>{value}</strong><p>{refresh}</p><footer>正常 {threshold} · 截至 {sourceDate}</footer></article>)}</div>
          </div>
        </section>

        <section className="nx-section" id="nx-sector">
          <header className="nx-section-head"><div><span>02 / SECTOR SIGNAL MATRIX</span><h2>赛道动能矩阵 · 前10</h2></div><p><LabelTip label="研究评分与执行许可分离" text="高分只表示值得优先研究。若总市场闸门未放行，执行灯仍可以是黄灯、红灯或灰灯。" align="right" /></p></header>
          <div className="nx-sector-matrix nx-glass">
            <div className="nx-matrix-head">
              <LabelTip label="排名 / 赛道" text="前10按上游赛道动态评分排序，综合当日板块强弱、市场广度、资金和催化。右侧‘综合100’是研究质量分，不直接决定名次。" align="left" />
              <LabelTip label="趋势 25" text={"作用：判断价格、市场广度和成交是否确认上涨方向。\n算法：赛道动态总分 × 25%。\n区间：19–25强；14–18观察；0–13弱。\n边界：行情过期时降级，不能用新闻替代价格确认。"} />
              <LabelTip label="资金 25" text={"作用：判断上涨是否获得量价和参与热度支持。\n算法：热度分 × 25%。\n区间：19–25强；14–18观察；0–13弱。\n边界：目前是量价与热度代理，不等于真实ETF申赎。"} />
              <LabelTip label="基本面 25" text={"作用：判断订单、盈利和产业景气能否支撑行情。\n算法：景气分 × 25%。\n区间：19–25强；14–18观察；0–13弱。\n边界：缺少一致预期数据时标记为代理，不伪造业绩证据。"} />
              <LabelTip label="高频 10" text={"作用：捕捉订单、政策、产品及价格的最新边际变化。\n算法：有效新增证据命中数，最高10分。\n区间：8–10强；6–7观察；0–5弱。\n边界：旧新闻不重复计分；没有新增证据可以为0分。"} />
              <LabelTip label="估值 15" text={"作用：判断安全边际、拥挤程度和当前赔率。\n算法：（100－风险分）× 15%。\n区间：12–15强；9–11观察；0–8弱。\n边界：目前是风险与价格分位代理，不等于完整PE/PB估值。"} />
              <LabelTip label="综合 100" text={"作用：汇总五因子，用于赛道横向比较和研究排序。\n算法：趋势＋资金＋基本面＋高频＋估值。\n区间：≥75绿灯；55–74黄灯；＜55红灯。\n边界：分数高只代表研究优先，不等于可以买入。"} />
              <LabelTip label="执行灯" text={"作用：把研究结果转换为最终行动约束。\n规则：综合研究灯＋市场闸门＋数据覆盖率共同决定。\n绿灯：条件较完整，可进入行动候选，仍需分批。\n灰灯：数据不足或过期，暂停判断，不执行操作。"} align="right" />
            </div>
            {sectors.map((s,i) => <div className="nx-matrix-row" key={s.name} title={s.proxy}><div><i>{String(i+1).padStart(2,"0")}</i><span><b>{s.name}</b><small>{s.risk}</small></span></div><Meter value={s.trend} max={25} tone="cyan" /><Meter value={s.flow} max={25} tone="blue" /><Meter value={s.fundamental} max={25} tone="purple" /><Meter value={s.hf} max={10} tone="pink" /><Meter value={s.value} max={15} tone="yellow" /><strong>{s.score}</strong><Lamp tone={s.execute as Tone} text={executeText(String(s.execute))} /></div>)}
          </div>
        </section>

        <section className="nx-section nx-evidence-events" id="nx-evidence">
          <article className="nx-glass nx-validation"><header><div><span>03 / CROSS-MARKET</span><h2><LabelTip label="证据验证舱" text="用机构公开观点、跨市场价格和多来源一致性对主判断做佐证或反证。它不独立生成买入信号。" align="left" /></h2></div><Lamp tone="gray" text="只作佐证" /></header><EvidenceTerminal /><div className="nx-validation-copy"><p><b>重点框架</b> {evidence.leading.join("、") || "暂无新增可靠观点"}</p><p><b>使用边界</b> 无可靠新增时明确标注，不把旧观点包装成新资金流。</p><small>{evidence.note}</small></div></article>
          <article className="nx-glass nx-event-radar" id="nx-events"><header><div><span>04 / EVENT IMPACT</span><h2><LabelTip label="市场事件雷达 · 前10" text="按对折现率、流动性、盈利预期和风险偏好的潜在影响排序。‘利多/利空’表示方向，不代表必然发生。" align="left" /></h2></div><Lamp tone="green" text="已刷新" /></header><div className="nx-event-list">{events.map((event,i) => { const direction = Number(event.direction); return <div key={event.title} title={event.watch}><i>{String(i+1).padStart(2,"0")}</i><span><b>{event.title}</b><small>{event.source} · {event.confidence}置信度 · {event.date}</small></span><strong className={direction < 0 ? "negative" : direction > 0 ? "positive" : "neutral"}>{direction > 0 ? "利多" : direction < 0 ? "利空" : "观察"}</strong><em style={{ "--impact": event.priority * 10 } as CSSProperties}><u /></em></div> })}</div></article>
        </section>

        <section className="nx-section" id="nx-holdings">
          <header className="nx-section-head"><div><span>05 / PORTFOLIO RISK BAY</span><h2>持仓风险舱</h2></div><p><LabelTip label="2只股票 · 12只基金 · 不推断真实交易" text="只根据用户已确认的持仓清单跟踪市场表现和风险。系统不知道未同步的加减仓，因此不推断仓位金额或自动下单。" align="right" /></p></header>
          <div className="nx-holding-grid">
            <article className="nx-glass nx-stock-bay"><header><span>股票持仓 / STOCKS</span><strong>02</strong></header>{stocks.map(stock => <div className="nx-stock-row" key={stock.code}><div><small>{stock.code} · 截至 {stock.marketDate}</small><b>{stock.name}</b><span>{stock.sector}</span></div><div className="nx-stock-move"><strong>{String(stock.day) === "待核验" ? "—" : `${Number(stock.day) > 0 ? "+" : ""}${stock.day}%`}</strong><small>5日 {stock.fiveDay}%</small></div><Lamp tone={stock.signal as Tone} text={stockLampText(String(stock.signal))} /><p>最新价 {stock.latestPrice} · {stock.direction}；{stock.watch}</p></div>)}</article>
            <article className="nx-glass nx-fund-bay"><header><span>基金持仓 / FUNDS</span><strong>{funds.length}</strong></header><div className="nx-fund-cloud">{funds.map(fund => <div className={fund.risk === "高" ? "risk" : ""} key={fund.code}><span><i>{fund.code}</i><b>{fund.name}</b><small>{fund.sector} · 截至 {fund.date}</small></span><strong>{fund.day > 0 ? "+" : ""}{fund.day}%</strong><Lamp tone={fund.risk === "高" ? "red" : "yellow"} text={fund.risk === "高" ? "高风险" : fund.decision} /><p>近1周 {fund.week}% · {fund.direction}</p></div>)}</div></article>
          </div>
        </section>

        <section className="nx-section" id="nx-opportunity">
          <header className="nx-section-head"><div><span>06 / OPPORTUNITY RADAR</span><h2>新机会雷达</h2></div><p><LabelTip label="代码候选池与行动边界" text="候选代码和替代表达用于研究追踪。没有独立验证的执行模型时，卡片只显示系统未启用，绝不把研究状态伪装成买卖动作。" align="right" /></p></header>
          <div className="nx-opportunity-strip nx-glass"><span>业务日期 {codedOpportunityRadar.businessDate}</span><span>市场闸门 {codedOpportunityRadar.marketGate}</span><span>数据健康 {codedOpportunityRadar.dataHealth}</span><Lamp tone="gray" text="执行引擎未启用" /></div>
          <div className="nx-coded-radar-grid">
            <article className="nx-glass nx-coded-column"><header><span>7C｜半年潜力股TOP10</span><strong>{codedOpportunityRadar.stocks.length}</strong></header><div className="nx-coded-cards">{codedOpportunityRadar.stocks.map(candidate => <article className="nx-coded-card" key={candidate.code}><small>{candidate.code} · {candidate.assetType}</small><b>{candidate.name}</b><span>{candidate.theme}</span><div><Lamp tone="gray" text={candidate.researchStatus} /><Lamp tone="gray" text={candidate.executionAction ?? "执行引擎未启用"} /></div><p><b>依据</b>{candidate.actionRationale}</p><p><b>下一触发</b>{candidate.nextTrigger}</p><p><b>失效条件</b>{candidate.invalidCondition}</p><footer>数据日期 {candidate.dataDate ?? "待日更核验"} · {candidate.dataStatus}</footer></article>)}</div></article>
            <article className="nx-glass nx-coded-column nx-coded-relationships"><header><span>7E｜股票基金替代关系</span><strong>{codedOpportunityRadar.relationships.length}</strong></header><div>{codedOpportunityRadar.relationships.map((relation, index) => <article className="nx-relation-card" key={`${relation.etfCode}-${index}`}><small>股票候选</small><b>{relation.stockCodes.join(" · ")}</b><i>→</i><small>ETF 候选 {relation.etfCode}</small><p>{relation.relationship}</p><Lamp tone="gray" text={relation.expressionStrategy ?? relation.relationshipStatus} /></article>)}</div><footer>{codedOpportunityRadar.executionBoundary}</footer></article>
            <article className="nx-glass nx-coded-column"><header><span>7D｜潜力基金ETF TOP10</span><strong>{codedOpportunityRadar.etfs.length}</strong></header><div className="nx-coded-cards">{codedOpportunityRadar.etfs.map(candidate => <article className="nx-coded-card" key={candidate.code}><small>{candidate.code} · {candidate.assetType}</small><b>{candidate.name}</b><span>{candidate.theme}</span><div><Lamp tone="gray" text={candidate.researchStatus} /><Lamp tone="gray" text={candidate.executionAction ?? "执行引擎未启用"} /></div><p><b>依据</b>{candidate.actionRationale}</p><p><b>下一触发</b>{candidate.nextTrigger}</p><p><b>失效条件</b>{candidate.invalidCondition}</p><footer>数据日期 {candidate.dataDate ?? "待日更核验"} · {candidate.dataStatus}</footer></article>)}</div></article>
          </div>
        </section>

        <section className="nx-guide"><span>SYSTEM DISCIPLINE</span><h2>灰灯不判断 · 红灯先控险 · 黄灯不追高 · 绿灯只进入研究</h2><p>只有执行灯持续为绿、数据日期同步且没有反证时，才允许小量验证。</p></section>
        <footer className="nx-footer">
          <div className="nx-footer-rights">
            <span>投资研究中心 2.0 · QUANT DASHBOARD</span>
            <strong>© 2026 陈一铭 · 保留所有权利</strong>
            <small>本看板的原创架构、分析逻辑及视觉设计著作权归陈一铭所有；第三方数据权利归原始来源方所有。未经授权，不得复制、转载或用于商业用途。</small>
          </div>
          <span>数据是证据，不是答案</span>
        </footer>
      </section>
    </main>
  );
}

function Meter({ value, max, tone }: { value: number; max: number; tone: string }) {
  return <span className="nx-meter"><i className={`tone-${tone}`} style={{ width: `${Math.round(value/max*100)}%` }} /><small>{value}</small></span>;
}
