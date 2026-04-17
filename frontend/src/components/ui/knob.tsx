"use client";

import * as React from "react";
import { MonoLabel } from "./mono-label";

const PRIMARY = "#00AAFF";

export interface KnobProps {
  value: number;
  label: string;
  size?: number;
  color?: string;
  onChange?: (value: number) => void;
}

export function Knob({
  value,
  label,
  size = 48,
  color = PRIMARY,
  onChange,
}: KnobProps) {
  const clamped = Math.min(1, Math.max(0, value));
  const angle = -135 + clamped * 270;
  const r = size / 2 - 6;
  const circumference = Math.PI * r * 2;
  const arcLength = clamped * Math.PI * r * 1.5;
  const dashOffset = Math.PI * r * 0.75;

  const indicatorX = size / 2 + Math.cos((angle * Math.PI) / 180) * (r - 2);
  const indicatorY = size / 2 + Math.sin((angle * Math.PI) / 180) * (r - 2);

  const dragStartRef = React.useRef<{ y: number; value: number } | null>(null);

  const handlePointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!onChange) return;
    (e.target as SVGSVGElement).setPointerCapture(e.pointerId);
    dragStartRef.current = { y: e.clientY, value: clamped };
  };

  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!onChange || !dragStartRef.current) return;
    const delta = (dragStartRef.current.y - e.clientY) / 150;
    const next = Math.min(1, Math.max(0, dragStartRef.current.value + delta));
    onChange(next);
  };

  const handlePointerUp = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!onChange) return;
    (e.target as SVGSVGElement).releasePointerCapture(e.pointerId);
    dragStartRef.current = null;
  };

  return (
    <div className="flex flex-col items-center gap-1.5">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        style={{
          touchAction: "none",
          cursor: onChange ? "ns-resize" : "default",
        }}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="2"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
        />
        <circle
          cx={indicatorX}
          cy={indicatorY}
          r="3"
          fill={color}
          style={{ filter: `drop-shadow(0 0 3px ${color})` }}
        />
        <text
          x={size / 2}
          y={size / 2 + 1}
          textAnchor="middle"
          dominantBaseline="middle"
          className="font-mono"
          fill="var(--color-text)"
          style={{ fontSize: "11px" }}
        >
          {Math.round(clamped * 100)}
        </text>
      </svg>
      <MonoLabel>{label}</MonoLabel>
    </div>
  );
}
