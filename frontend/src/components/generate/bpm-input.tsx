"use client";

import { type ReactNode } from "react";
import { MonoLabel } from "@/components/ui/mono-label";
import type { BpmResult } from "@/lib/types";

const QUICK_BPMS = [64, 90, 110, 128, 140, 174];

interface BpmInputProps {
  value: number;
  onChange: (bpm: number) => void;
  detectedBpm?: BpmResult | null;
  audioSlot?: ReactNode;
  embedded?: boolean;
}

function HardwareButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      data-active={active}
      className="font-mono uppercase tracking-wider text-[11px] px-3 py-1.5 border border-border rounded-sm bg-transparent text-text-muted hover:border-border-light hover:text-text data-[active=true]:border-primary data-[active=true]:bg-primary/15 data-[active=true]:text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
    >
      {children}
    </button>
  );
}

export function BpmInput({
  value,
  onChange,
  detectedBpm,
  audioSlot,
  embedded,
}: BpmInputProps) {
  return (
    <div className={embedded ? "p-4" : "border border-border rounded-sm bg-surface-card p-4"}>
      {!embedded && <MonoLabel color="var(--color-primary)">tempo_config</MonoLabel>}

      <div className="flex flex-wrap items-end gap-6 mt-3">
        <div>
          <div
            className="font-mono font-bold leading-none text-primary"
            style={{
              fontSize: "48px",
              letterSpacing: "-0.03em",
              textShadow: "0 0 20px rgba(0, 170, 255, 0.3)",
              fontVariantNumeric: "tabular-nums",
              minWidth: "3ch",
            }}
          >
            {value}
          </div>
          <MonoLabel>bpm</MonoLabel>
        </div>

        <div className="flex flex-wrap gap-1 pb-1">
          {QUICK_BPMS.map((b) => (
            <HardwareButton
              key={b}
              active={value === b}
              onClick={() => onChange(b)}
            >
              {b}
            </HardwareButton>
          ))}
        </div>

      </div>

      {detectedBpm && (
        <div className="mt-3 pt-3 border-t border-border">
          <MonoLabel className="block mb-1.5">detected_candidates</MonoLabel>
          <div className="flex flex-wrap gap-1">
            {[
              { label: "detected", bpm: Math.round(detectedBpm.detected) },
              { label: "half", bpm: Math.round(detectedBpm.half) },
              { label: "double", bpm: Math.round(detectedBpm.double) },
            ].map(({ label, bpm }) => (
              <HardwareButton
                key={label}
                active={value === bpm}
                onClick={() => onChange(bpm)}
              >
                {label}:{bpm}
              </HardwareButton>
            ))}
          </div>
        </div>
      )}

      {audioSlot && <div className="mt-4">{audioSlot}</div>}
    </div>
  );
}
