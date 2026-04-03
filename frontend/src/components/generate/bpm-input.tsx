"use client";

import type { BpmResult } from "@/lib/types";

interface BpmInputProps {
  value: number;
  onChange: (bpm: number) => void;
  detectedBpm?: BpmResult | null;
}

export function BpmInput({ value, onChange, detectedBpm }: BpmInputProps) {
  const chips: { label: string; bpm: number }[] = detectedBpm
    ? [
        { label: "detected", bpm: Math.round(detectedBpm.detected) },
        { label: "half", bpm: Math.round(detectedBpm.half) },
        { label: "double", bpm: Math.round(detectedBpm.double) },
      ]
    : [];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-white">
        BPM
        <span className="ml-2 text-xs text-white/40 font-normal">
          60–200 beats per minute
        </span>
      </label>
      <input
        type="number"
        min={60}
        max={200}
        step={1}
        value={value}
        onChange={(e) => {
          const v = parseInt(e.target.value, 10);
          if (!isNaN(v)) onChange(Math.min(200, Math.max(60, v)));
        }}
        className="w-full bg-surface-elevated border border-white/10 rounded-lg px-4 py-2.5 text-white focus:border-accent-amber focus:ring-1 focus:ring-accent-amber/50 focus:outline-none"
      />
      {chips.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {chips.map(({ label, bpm }) => (
            <button
              key={label}
              type="button"
              onClick={() => onChange(bpm)}
              className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                value === bpm
                  ? "bg-accent-amber/20 border-accent-amber text-accent-amber"
                  : "border-white/10 text-white/60 hover:border-accent-amber hover:text-white"
              }`}
            >
              {label}: {bpm}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
