"use client";

interface ProgressBarProps {
  progress: number; // 0.0 to 1.0
  status: string;
}

function getStatusText(progress: number, status: string): string {
  if (status === "failed") return "Generation failed";
  if (status === "pending") return "Queued...";
  if (progress < 0.1) return "Analyzing audio...";
  if (progress < 0.85) return "Generating frames...";
  if (progress < 1.0) return "Encoding video...";
  return "Complete!";
}

export function ProgressBar({ progress, status }: ProgressBarProps) {
  const percentage = Math.round(progress * 100);
  const statusText = getStatusText(progress, status);

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-white/70">{statusText}</span>
        <span className="text-sm font-mono text-accent-amber">{percentage}%</span>
      </div>
      <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out bg-gradient-to-r from-accent-amber to-accent-magenta"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
