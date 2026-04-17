"use client";

import { MonoLabel } from "@/components/ui/mono-label";

interface VideoPlayerProps {
  src: string | null;
  poster?: string;
  progress: number;
  status: string;
}

const STEPS = [
  { label: "audio_analysis", threshold: 0.15 },
  { label: "rag_retrieval", threshold: 0.30 },
  { label: "llm_blending", threshold: 0.50 },
  { label: "frame_render", threshold: 0.85 },
  { label: "encode_mp4", threshold: 0.95 },
];

export function VideoPlayer({ src, poster, progress, status }: VideoPlayerProps) {
  const isComplete = status === "complete";
  const isFailed = status === "failed";

  const idx = STEPS.findIndex((s) => progress < s.threshold);
  const currentStep = idx === -1 ? STEPS.length - 1 : Math.max(0, idx);
  const percent = Math.round(progress * 100);

  return (
    <div
      className="w-full aspect-video border border-border rounded-sm overflow-hidden relative flex items-center justify-center"
      style={{ background: "var(--color-surface-card)" }}
    >
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(0, 170, 255, 0.15), transparent 60%), radial-gradient(circle at 30% 70%, rgba(139, 92, 246, 0.12), transparent 50%)",
        }}
      />

      {isComplete && src ? (
        <video
          className="relative w-full h-full object-contain z-10"
          controls
          loop
          poster={poster}
        >
          <source src={src} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      ) : (
        <div className="text-center relative z-10">
          <div
            className="font-mono font-bold leading-none text-primary"
            style={{
              fontSize: "36px",
              textShadow: "0 0 30px rgba(0, 170, 255, 0.3)",
            }}
          >
            {isFailed ? "err" : `${percent}%`}
          </div>
          <div className="mt-2">
            <MonoLabel color="var(--color-text-muted)">
              {isFailed ? "pipeline_halted" : STEPS[currentStep]?.label}
            </MonoLabel>
          </div>
        </div>
      )}
    </div>
  );
}
