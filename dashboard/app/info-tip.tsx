"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

type Align = "left" | "center" | "right";
type Position = { left: number; top: number; placement: "top" | "bottom" };

export function InfoTip({ text, align = "center" }: { text: string; align?: Align }) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const tooltipRef = useRef<HTMLSpanElement>(null);
  const pinnedRef = useRef(false);
  const tooltipId = useId();
  const [open, setOpen] = useState(false);
  const [position, setPosition] = useState<Position>({ left: 0, top: 0, placement: "bottom" });

  const updatePosition = useCallback(() => {
    const button = buttonRef.current;
    if (!button) return;
    const rect = button.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const tooltipWidth = Math.min(340, viewportWidth - 32);
    const tooltipHeight = tooltipRef.current?.offsetHeight ?? 126;
    const halfWidth = tooltipWidth / 2;
    const preferredLeft = align === "left" ? rect.left + halfWidth : align === "right" ? rect.right - halfWidth : rect.left + rect.width / 2;
    const left = Math.max(16 + halfWidth, Math.min(viewportWidth - 16 - halfWidth, preferredLeft));
    const fitsBelow = rect.bottom + 12 + tooltipHeight <= viewportHeight - 16;
    setPosition({
      left,
      top: fitsBelow ? rect.bottom + 10 : rect.top - 10,
      placement: fitsBelow ? "bottom" : "top",
    });
  }, [align]);

  const show = () => {
    updatePosition();
    setOpen(true);
  };

  const hide = () => {
    pinnedRef.current = false;
    setOpen(false);
  };

  useLayoutEffect(() => {
    if (open) updatePosition();
  }, [open, text, updatePosition]);

  useEffect(() => {
    if (!open) return;
    const reposition = () => updatePosition();
    const close = (event: PointerEvent) => {
      if (!buttonRef.current?.contains(event.target as Node)) hide();
    };
    window.addEventListener("resize", reposition);
    window.addEventListener("scroll", reposition, true);
    document.addEventListener("pointerdown", close);
    return () => {
      window.removeEventListener("resize", reposition);
      window.removeEventListener("scroll", reposition, true);
      document.removeEventListener("pointerdown", close);
    };
  }, [open, updatePosition]);

  return (
    <span className="nx-info-tip">
      <button
        ref={buttonRef}
        type="button"
        aria-label="查看指标说明"
        aria-expanded={open}
        aria-describedby={open ? tooltipId : undefined}
        onMouseEnter={show}
        onMouseLeave={() => { if (!pinnedRef.current) setOpen(false); }}
        onFocus={show}
        onBlur={() => { if (!pinnedRef.current) setOpen(false); }}
        onPointerDown={(event) => {
          event.stopPropagation();
          pinnedRef.current = !pinnedRef.current;
          if (pinnedRef.current) show(); else setOpen(false);
        }}
      >i</button>
      {open && createPortal(
        <span
          ref={tooltipRef}
          id={tooltipId}
          className="nx-floating-tooltip"
          role="tooltip"
          data-placement={position.placement}
          style={{ left: position.left, top: position.top }}
        >{text}</span>,
        document.body,
      )}
    </span>
  );
}

export function LabelTip({ label, text, align = "center" }: { label: string; text: string; align?: Align }) {
  return <span className="nx-label-tip"><span>{label}</span><InfoTip text={text} align={align} /></span>;
}
