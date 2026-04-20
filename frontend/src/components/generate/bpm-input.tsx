"use client";

import { useState, type ReactNode } from "react";
import { MonoLabel } from "@/components/ui/mono-label";
import { Knob } from "@/components/ui/knob";
import type { BpmResult } from "@/lib/types";

const QUICK_BPMS = [64, 90, 110, 128, 140, 174];

interface BpmInputProps {
  value: number;
  onChange: (bpm: number) => void;
  detectedBpm?: BpmResult | null;
  audioSlot?: ReactNode;
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
}: BpmInputProps) {
  const [intensity, setIntensity] = useState(0.65);
  const [complexity, setComplexity] = useState(0.4);

  return (
    <div className="border border-border rounded-sm bg-surface-card p-4">
      <MonoLabel color="var(--color-primary)">tempo_config</MonoLabel>

      <div className="flex flex-wrap items-end gap-6 mt-3">
        <div>
          <div
            className="font-mono font-bold leading-none text-primary"
            style={{
              fontSize: "48px",
              letterSpacing: "-0.03em",
              textShadow: "0 0 20px rgba(0, 170, 255, 0.3)",
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

        <div className="flex gap-3 ml-auto">
          <Knob
            value={intensity}
            label="intensity"
            size={48}
            onChange={setIntensity}
          />
          <Knob
            value={complexity}
            label="complexity"
            size={48}
            color="#8B5CF6"
            onChange={setComplexity}
          />
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
