"use client";

import { MonoLabel } from "@/components/ui/mono-label";
import { Badge } from "@/components/ui/badge";
import { BpmChart } from "./bpm-chart";
import type { AudioAnalysis, StyleMatch } from "@/lib/types";

interface ResultSidebarProps {
  audioAnalysis: AudioAnalysis | null;
  matchedStyles: StyleMatch[] | null;
  creativeDescription: string | null;
}

// Cycle through palette accents for multiple matched styles.
const STYLE_COLORS = ["#00AAFF", "#8B5CF6", "#00FF88", "#33BBFF", "#FF3399"];

export function ResultSidebar({
  audioAnalysis,
  matchedStyles,
  creativeDescription,
}: ResultSidebarProps) {
  return (
    <div className="border border-border rounded-sm bg-surface-card p-3 flex flex-col gap-4 h-fit">
      {creativeDescription && (
        <div>
          <MonoLabel color="var(--color-violet)">ai_vision</MonoLabel>
          <p className="mt-2 font-sans text-[13px] text-text-muted leading-relaxed">
            {creativeDescription}
          </p>
        </div>
      )}

      {matchedStyles && matchedStyles.length > 0 && (
        <div>
          <MonoLabel color="var(--color-primary)">matched_styles</MonoLabel>
          <div className="flex flex-wrap gap-1 mt-2">
            {matchedStyles.map((style, i) => (
              <Badge
                key={style.id}
                color={STYLE_COLORS[i % STYLE_COLORS.length]}
              >
                {style.genre.toUpperCase()}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {audioAnalysis?.visualization && (
        <div>
          <MonoLabel color="var(--color-primary)">beat_map</MonoLabel>
          <div className="mt-2">
            <BpmChart visualization={audioAnalysis.visualization} />
          </div>
        </div>
      )}

      <div>
        <MonoLabel color="var(--color-primary)">render_info</MonoLabel>
        <dl className="mt-2 font-mono text-[11px] leading-loose text-text-muted">
          <div>
            <span className="text-text-dim">resolution:</span> 1920×1080
          </div>
          <div>
            <span className="text-text-dim">fps:</span> 30
          </div>
          <div>
            <span className="text-text-dim">duration:</span> 30s loop
          </div>
          <div>
            <span className="text-text-dim">codec:</span> h264
          </div>
          <div>
            <span className="text-text-dim">size:</span> ~12mb
          </div>
        </dl>
      </div>
    </div>
  );
}
