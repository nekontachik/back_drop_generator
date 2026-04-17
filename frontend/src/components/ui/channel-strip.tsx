"use client";

import * as React from "react";
import { MonoLabel } from "./mono-label";

const PRIMARY = "#00AAFF";

export interface ChannelStripProps {
  label: string;
  value: number;
  color?: string;
  active?: boolean;
}

export function ChannelStrip({
  label,
  value,
  color = PRIMARY,
  active = true,
}: ChannelStripProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div
      className="flex flex-col items-center gap-1.5 px-1.5 py-2 rounded-sm border min-w-[54px]"
      style={{
        background: active ? `${color}08` : "transparent",
        borderColor: active ? `${color}30` : "var(--color-border)",
      }}
    >
      <div className="relative w-1 h-10 rounded-[2px] overflow-hidden bg-border">
        <div
          className="absolute bottom-0 w-full rounded-[2px]"
          style={{
            height: `${clamped}%`,
            background: color,
            boxShadow: `0 0 6px ${color}60`,
          }}
        />
      </div>
      <MonoLabel color={active ? color : undefined}>{label}</MonoLabel>
    </div>
  );
}
