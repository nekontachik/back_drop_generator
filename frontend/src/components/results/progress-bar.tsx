"use client";

import { useEffect, useState } from "react";
import { MonoLabel } from "@/components/ui/mono-label";

interface ProgressBarProps {
  progress: number; // 0.0 to 1.0 — real backend progress
  status: string;
}

const STEPS = [
  { label: "audio_analysis", threshold: 15 },
  { label: "rag_retrieval", threshold: 30 },
  { label: "llm_blending", threshold: 50 },
  { label: "frame_render", threshold: 85 },
  { label: "encode_mp4", threshold: 95 },
];

export function ProgressBar({ progress, status }: ProgressBarProps) {
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    if (status === "complete" || status === "failed") {
      setDisplayed(status === "complete" ? 1.0 : displayed);
      return;
    }

    const target = Math.max(progress, displayed);

    const interval = setInterval(() => {
      setDisplayed((prev) => {
        const fakeTarget = Math.min(prev + 0.012, 0.92);
        const next = Math.max(fakeTarget, target);
        if (next >= 0.99) {
          clearInterval(interval);
          return next;
        }
        return next;
      });
    }, 800);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [progress, status]);

  useEffect(() => {
    if (status === "complete") setDisplayed(1.0);
  }, [status]);

  const percent = Math.round(displayed * 100);
  const done = status === "complete";
  const failed = status === "failed";

  return (
    <div className="border border-border rounded-sm bg-surface-card p-3">
      <div className="flex items-center justify-between mb-2">
        <MonoLabel color="var(--color-primary)">pipeline</MonoLabel>
        <MonoLabel>
          {done ? "complete" : failed ? "halted" : `${percent}%`}
        </MonoLabel>
      </div>

      <div
        className="h-1 rounded-[2px] overflow-hidden mb-3"
        style={{ background: "var(--color-surface-elevated)" }}
      >
        <div
          className="h-full transition-[width] duration-300 ease-out"
          style={{
            width: `${percent}%`,
            background: done
              ? "var(--color-green)"
              : failed
                ? "#ff6b6b"
                : "linear-gradient(90deg, var(--color-primary), var(--color-violet))",
            boxShadow: done
              ? "0 0 10px rgba(0, 255, 136, 0.3)"
              : failed
                ? "0 0 10px rgba(255, 107, 107, 0.25)"
                : "0 0 10px rgba(0, 170, 255, 0.3)",
          }}
        />
      </div>

      <div className="flex flex-wrap gap-x-3 gap-y-1.5 justify-between">
        {STEPS.map((step, i) => {
          const stepDone = percent >= step.threshold;
          const prevThreshold = i === 0 ? 0 : STEPS[i - 1].threshold;
          const isCurrent = !stepDone && percent >= prevThreshold && !failed;
          const dotColor = stepDone
            ? "var(--color-green)"
            : isCurrent
              ? "var(--color-primary)"
              : "var(--color-border)";
          const textColor = stepDone
            ? "var(--color-green)"
            : isCurrent
              ? "var(--color-primary)"
              : "var(--color-text-dim)";
          return (
            <div key={step.label} className="flex items-center gap-1.5">
              <span
                className="inline-block w-1.5 h-1.5 rounded-[1px]"
                style={{
                  background: dotColor,
                  boxShadow: isCurrent
                    ? "0 0 6px var(--color-primary)"
                    : "none",
                }}
              />
              <MonoLabel color={textColor}>{step.label}</MonoLabel>
            </div>
          );
        })}
      </div>
    </div>
  );
}
