import type { CSSProperties } from "react";
import type { Metadata } from "next";
import { events, evidence, funds, risks, sectors, snapshot, stocks } from "./dashboard-data";

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
            <header><span>系统市场闸门 / RISK GATE</span><Lamp tone={healthTone} text={snapshot.dataHealth} /></header>
            <div className="nx-summary-gate-body">
              <div className="nx-summary-ring" style={{ "--risk": snapshot.riskScore } as CSSProperties}><div><strong>{snapshot.riskScore}</strong><span>/ 100</span><small>{snapshot.marketGate}</small></div></div>
              <div><h2>{snapshot.daily.action}</h2><p>{snapshot.daily.positionAdvice}</p></div>
            </div>
            <footer><span><i className="nx-dot nx-green" />{snapshot.lightCounts.green} 绿</span><span><i className="nx-dot nx-yellow" />{snapshot.lightCounts.yellow} 黄</span><span><i className="nx-dot nx-red" />{snapshot.lightCounts.red} 红</span><span><i className="nx-dot nx-gray" />{snapshot.lightCounts.gray} 灰</span></footer>
          </article>

          <article className="nx-glass nx-summary-action">
            <header><span>今日总动作 / ACTION</span><b>{snapshot.daily.action}</b></header>
            <h2>{marketGate === "风险允许" ? "研究优先，" : "控制节奏，"}<em>{snapshot.daily.action}</em></h2>
            <p>{snapshot.daily.needAction}</p>
            <div><span><b>01</b>不追高</span><span><b>02</b>看确认</span><span><b>03</b>守纪律</span></div>
          </article>

          <article className="nx-glass nx-summary-fresh">
            <header><span>数据新鲜度 / FRESHNESS</span><Lamp tone={healthTone} text={snapshot.dataHealth} /></header>
            <div>{snapshot.freshness.map(({name,date,width}) => <div className="nx-summary-stream" key={name}><span>{name}</span><i><b style={{ width: `${width}%` }} /></i><strong>{date}</strong></div>)}</div>
            <small>数据截至 {snapshot.asOf}；过期或待核验字段自动降级</small>
          </article>

          <article className="nx-glass nx-summary-modules">
            <header><span>五模块脉冲 / MODULES</span><b>5 MODULES</b></header>
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
          <header className="nx-section-head"><div><span>01 / MARKET RISK MATRIX</span><h2>风险雷达阵列</h2></div><p>12项日常指标 · 2项硬闸门</p></header>
          <div className="nx-risk-board">
            <article className="nx-glass nx-risk-radar"><div className="nx-radar-grid"><i /><i /><i /><i /></div><div className="nx-radar-shape" /><div className="nx-radar-label r1">流动性 74</div><div className="nx-radar-label r2">波动 54</div><div className="nx-radar-label r3">趋势 22</div><div className="nx-radar-label r4">宽度 9</div><div className="nx-radar-label r5">估值 75</div><strong>风险偏高</strong><small>趋势与宽度构成主要约束</small></article>
            <div className="nx-risk-cells">{risks.map(([name,value,signal,threshold,refresh,sourceDate],i) => <article className={`nx-risk-cell nx-edge-${signal}`} key={name}><header><span>{String(i+1).padStart(2,"0")}</span><Lamp tone={signal as Tone} text={lightText(String(signal))} /></header><h3>{name}</h3><strong>{value}</strong><p>{refresh}</p><footer>正常 {threshold} · 截至 {sourceDate}</footer></article>)}</div>
          </div>
        </section>

        <section className="nx-section" id="nx-sector">
          <header className="nx-section-head"><div><span>02 / SECTOR SIGNAL MATRIX</span><h2>赛道动能矩阵 · 前10</h2></div><p>研究评分与执行许可分离</p></header>
          <div className="nx-sector-matrix nx-glass">
            <div className="nx-matrix-head"><span>排名 / 赛道</span><span>趋势 25</span><span>资金 25</span><span>基本面 25</span><span>高频 10</span><span>估值 15</span><span>综合 100</span><span>执行灯</span></div>
            {sectors.map((s,i) => <div className="nx-matrix-row" key={s.name} title={s.proxy}><div><i>{String(i+1).padStart(2,"0")}</i><span><b>{s.name}</b><small>{s.risk}</small></span></div><Meter value={s.trend} max={25} tone="cyan" /><Meter value={s.flow} max={25} tone="blue" /><Meter value={s.fundamental} max={25} tone="purple" /><Meter value={s.hf} max={10} tone="pink" /><Meter value={s.value} max={15} tone="yellow" /><strong>{s.score}</strong><Lamp tone={s.execute as Tone} text={executeText(String(s.execute))} /></div>)}
          </div>
        </section>

        <section className="nx-section nx-evidence-events" id="nx-evidence">
          <article className="nx-glass nx-validation"><header><div><span>03 / CROSS-MARKET</span><h2>证据验证舱</h2></div><Lamp tone="gray" text="只作佐证" /></header><div className="nx-validation-orbits"><div className="orbit o1" /><div className="orbit o2" /><div className="orbit o3" /><div className="v-core"><strong>{evidence.newCount}</strong><span>新增观点</span></div><span className="sat s1">机构样本<br /><b>{evidence.count}</b></span><span className="sat s2">高强度<br /><b>{evidence.strongCount}</b></span><span className="sat s3">独立买入<br /><b>0</b></span></div><div className="nx-validation-copy"><p><b>重点框架</b> {evidence.leading.join("、") || "暂无新增可靠观点"}</p><p><b>使用边界</b> 无可靠新增时明确标注，不把旧观点包装成新资金流。</p><small>{evidence.note}</small></div></article>
          <article className="nx-glass nx-event-radar" id="nx-events"><header><div><span>04 / EVENT IMPACT</span><h2>市场事件雷达 · 前10</h2></div><Lamp tone="green" text="已刷新" /></header><div className="nx-event-list">{events.map((event,i) => { const direction = Number(event.direction); return <div key={event.title} title={event.watch}><i>{String(i+1).padStart(2,"0")}</i><span><b>{event.title}</b><small>{event.source} · {event.confidence}置信度 · {event.date}</small></span><strong className={direction < 0 ? "negative" : direction > 0 ? "positive" : "neutral"}>{direction > 0 ? "利多" : direction < 0 ? "利空" : "观察"}</strong><em style={{ "--impact": event.priority * 10 } as CSSProperties}><u /></em></div> })}</div></article>
        </section>

        <section className="nx-section" id="nx-holdings">
          <header className="nx-section-head"><div><span>05 / PORTFOLIO RISK BAY</span><h2>持仓风险舱</h2></div><p>2只股票 · 12只基金 · 不推断真实交易</p></header>
          <div className="nx-holding-grid">
            <article className="nx-glass nx-stock-bay"><header><span>股票持仓 / STOCKS</span><strong>02</strong></header>{stocks.map(stock => <div className="nx-stock-row" key={stock.code}><div><small>{stock.code} · 截至 {stock.marketDate}</small><b>{stock.name}</b><span>{stock.sector}</span></div><div className="nx-stock-move"><strong>{stock.day === "待核验" ? "—" : `${Number(stock.day) > 0 ? "+" : ""}${stock.day}%`}</strong><small>5日 {stock.fiveDay}%</small></div><Lamp tone={stock.signal as Tone} text={stockLampText(String(stock.signal))} /><p>最新价 {stock.latestPrice} · {stock.direction}；{stock.watch}</p></div>)}</article>
            <article className="nx-glass nx-fund-bay"><header><span>基金持仓 / FUNDS</span><strong>{funds.length}</strong></header><div className="nx-fund-cloud">{funds.map(fund => <div className={fund.risk === "高" ? "risk" : ""} key={fund.code}><span><i>{fund.code}</i><b>{fund.name}</b><small>{fund.sector} · 截至 {fund.date}</small></span><strong>{fund.day > 0 ? "+" : ""}{fund.day}%</strong><Lamp tone={fund.risk === "高" ? "red" : "yellow"} text={fund.risk === "高" ? "高风险" : fund.decision} /><p>近1周 {fund.week}% · {fund.direction}</p></div>)}</div></article>
          </div>
        </section>

        <section className="nx-guide"><span>SYSTEM DISCIPLINE</span><h2>灰灯不判断 · 红灯先控险 · 黄灯不追高 · 绿灯只进入研究</h2><p>只有执行灯持续为绿、数据日期同步且没有反证时，才允许小量验证。</p></section>
        <footer className="nx-footer"><span>投资研究中心 2.0 · QUANT DASHBOARD</span><span>数据是证据，不是答案</span></footer>
      </section>
    </main>
  );
}

function Meter({ value, max, tone }: { value: number; max: number; tone: string }) {
  return <span className="nx-meter"><i className={`tone-${tone}`} style={{ width: `${Math.round(value/max*100)}%` }} /><small>{value}</small></span>;
}
