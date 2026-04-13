"use client";

import { useEffect, useState } from "react";

interface ProgressBarProps {
  progress: number; // 0.0 to 1.0 — real backend progress
  status: string;
}

const STATUS_STEPS = [
  { threshold: 0.15, label: "Analyzing your prompt..." },
  { threshold: 0.35, label: "Matching genre styles..." },
  { threshold: 0.60, label: "Blending visual parameters..." },
  { threshold: 0.80, label: "Generating frames..." },
  { threshold: 0.95, label: "Encoding video..." },
  { threshold: 1.00, label: "Finalizing..." },
];

function getStatusLabel(displayed: number, status: string): string {
  if (status === "failed") return "Generation failed";
  if (status === "complete" || displayed >= 1.0) return "Complete!";
  for (const step of STATUS_STEPS) {
    if (displayed < step.threshold) return step.label;
  }
  return "Processing...";
}

export function ProgressBar({ progress, status }: ProgressBarProps) {
  // Fake progress: smoothly animate toward real progress, never go backward
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    if (status === "complete" || status === "failed") {
      setDisplayed(status === "complete" ? 1.0 : displayed);
      return;
    }

    // If backend reports higher progress, snap to it
    const target = Math.max(progress, displayed);

    // Fake advancement: increment by ~1% every 800ms until we hit real progress
    const interval = setInterval(() => {
      setDisplayed((prev) => {
        const fakeTarget = Math.min(prev + 0.012, 0.92); // max fake is 92%
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

  // On complete — jump to 100%
  useEffect(() => {
    if (status === "complete") setDisplayed(1.0);
  }, [status]);

  const percentage = Math.round(displayed * 100);
  const label = getStatusLabel(displayed, status);

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-white/70">{label}</span>
        <span className="text-sm font-mono text-accent-amber">{percentage}%</span>
      </div>
      <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out bg-gradient-to-r from-accent-amber to-accent-magenta"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
