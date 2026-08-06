"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { evidence } from "./dashboard-data";

type EvidenceView = "samples" | "strong" | "tracking" | "buy";

const viewCopy: Record<EvidenceView, { eyebrow: string; title: string; summary: string }> = {
  samples: {
    eyebrow: "INSTITUTION SAMPLE MATRIX",
    title: "机构样本全景",
    summary: "展示本批次纳入的全部公开机构观点；用于交叉佐证，不代表机构当日真实交易。",
  },
  strong: {
    eyebrow: "HIGH-WEIGHT EVIDENCE",
    title: "高权重证据 · 7项",
    summary: "仅保留证据强度为“高”或“中高”的样本，重点看观察方向及其对当前市场的含义。",
  },
  tracking: {
    eyebrow: "TRACKING SIGNAL",
    title: "待跟踪验证 · 1项",
    summary: "该信息尚未达到“已验证新增观点”标准，需要等待价格、资金或第二来源确认。",
  },
  buy: {
    eyebrow: "INDEPENDENT BUY TRIGGER",
    title: "独立买入信号 · 0项",
    summary: "机构观点只能佐证，不能单独触发买入；当前没有满足系统门槛的独立买入证据。",
  },
};

function EvidenceRows({ view }: { view: Exclude<EvidenceView, "buy"> }) {
  const rows = view === "strong" ? evidence.strongDetails : view === "tracking" ? evidence.trackingDetails : evidence.details;
  return (
    <div className={`nx-evidence-table nx-evidence-${view}`}>
      <div className="nx-evidence-table-head">
        <span>机构 / 投资人</span>
        <span>{view === "tracking" ? "验证状态" : "证据权重"}</span>
        <span>主要观察方向</span>
        <span>对当前市场的意义</span>
      </div>
      {rows.map((row) => (
        <div className="nx-evidence-table-row" key={row.name}>
          <strong>{row.name}</strong>
          <span className="nx-evidence-weight">{view === "tracking" ? row.stance : row.strength}</span>
          <span>{row.focus}</span>
          <span>{row.meaning}</span>
        </div>
      ))}
    </div>
  );
}

export function EvidenceTerminal() {
  const [view, setView] = useState<EvidenceView | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const lastTriggerRef = useRef<HTMLButtonElement | null>(null);

  const open = (next: EvidenceView, trigger: HTMLButtonElement) => {
    lastTriggerRef.current = trigger;
    setView(next);
  };

  const close = () => {
    setView(null);
    window.setTimeout(() => lastTriggerRef.current?.focus(), 0);
  };

  useEffect(() => {
    if (!view) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [view]);

  return (
    <>
      <div className="nx-validation-orbits">
        <div className="orbit o1" /><div className="orbit o2" /><div className="orbit o3" />
        <button className="v-core nx-evidence-trigger" type="button" onClick={(event) => open("tracking", event.currentTarget)} aria-label="查看待跟踪验证详情">
          <strong>{evidence.trackingCount}</strong><span>待跟踪</span>
        </button>
        <button className="sat s1 nx-evidence-trigger" type="button" onClick={(event) => open("samples", event.currentTarget)} aria-label="查看全部机构样本">
          机构样本<br /><b>{evidence.count}</b>
        </button>
        <button className="sat s2 nx-evidence-trigger" type="button" onClick={(event) => open("strong", event.currentTarget)} aria-label="查看高权重证据">
          高权重<br /><b>{evidence.strongCount}</b>
        </button>
        <button className="sat s3 nx-evidence-trigger" type="button" onClick={(event) => open("buy", event.currentTarget)} aria-label="查看独立买入信号">
          独立买入<br /><b>{evidence.independentBuyCount}</b>
        </button>
      </div>

      {view && createPortal(
        <div className="nx-evidence-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) close(); }}>
          <section className="nx-evidence-modal" role="dialog" aria-modal="true" aria-labelledby="nx-evidence-dialog-title">
            <div className="nx-evidence-scanline" />
            <header className="nx-evidence-modal-head">
              <div><span>{viewCopy[view].eyebrow}</span><h2 id="nx-evidence-dialog-title">{viewCopy[view].title}</h2><p>{viewCopy[view].summary}</p></div>
              <button ref={closeRef} type="button" onClick={close} aria-label="关闭证据详情">×</button>
            </header>

            {view === "buy" ? (
              <div className="nx-evidence-empty">
                <div><strong>0</strong><span>当前有效信号</span></div>
                <section>
                  <h3>系统放行至少需要同时满足：</h3>
                  <p><b>01</b> 至少两类相互独立的可靠来源指向一致。</p>
                  <p><b>02</b> 价格趋势、成交或资金参与出现确认。</p>
                  <p><b>03</b> 市场风险闸门未限制新增风险暴露。</p>
                </section>
              </div>
            ) : <EvidenceRows view={view} />}

            <footer><span>证据等级 ≠ 买入指令</span><strong>点击空白处或按 ESC 关闭</strong></footer>
          </section>
        </div>,
        document.body,
      )}
    </>
  );
}
