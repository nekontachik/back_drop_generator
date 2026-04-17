"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { MonoLabel } from "@/components/ui/mono-label";
import { ProgressBar } from "@/components/results/progress-bar";
import { VideoPlayer } from "@/components/results/video-player";
import { ResultSidebar } from "@/components/results/result-sidebar";
import { getJobStream, getDownloadUrl } from "@/lib/api";
import type { AudioAnalysis, GenerateResponse, StyleMatch } from "@/lib/types";

export default function ResultsPage() {
  const params = useParams<{ id: string }>();
  const jobId = params.id;

  const [status, setStatus] = useState<string>("pending");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [audioAnalysis, setAudioAnalysis] = useState<AudioAnalysis | null>(null);
  const [matchedStyles, setMatchedStyles] = useState<StyleMatch[] | null>(null);
  const [creativeDescription, setCreativeDescription] = useState<string | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem(`job-${jobId}`);
    if (stored) {
      try {
        const data: GenerateResponse = JSON.parse(stored);
        // Session-storage hydration runs once on mount — safe to setState here.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setAudioAnalysis(data.audio_analysis);
        setMatchedStyles(data.matched_styles);
        setCreativeDescription(data.creative_description ?? null);
      } catch {
        // Ignore parse errors — graceful degradation
      }
      sessionStorage.removeItem(`job-${jobId}`);
    }
  }, [jobId]);

  useEffect(() => {
    const es = getJobStream(jobId);

    es.addEventListener("progress", (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      setProgress(data.progress);
      if (data.error) setError(data.error);
      if (data.status === "complete" || data.status === "failed") {
        es.close();
      }
    });

    es.addEventListener("error", () => {
      setError("Connection lost. Refresh to check status.");
      es.close();
    });

    return () => es.close();
  }, [jobId]);

  const isComplete = status === "complete";
  const isFailed = status === "failed";

  return (
    <main className="min-h-screen">
      <div className="max-w-[960px] mx-auto px-6 py-8">
        <div className="mb-6">
          <MonoLabel color="var(--color-primary)">module::render</MonoLabel>
          <h1 className="mt-1 text-2xl font-display font-bold text-text tracking-tight">
            {isComplete
              ? "Render Complete"
              : isFailed
                ? "Render Failed"
                : "Rendering..."}
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6">
          <div className="flex flex-col gap-3">
            <VideoPlayer
              src={isComplete ? getDownloadUrl(jobId) : null}
              progress={progress}
              status={status}
            />
            <ProgressBar progress={progress} status={status} />

            {isFailed && error && (
              <div className="border border-red-500/40 rounded-sm bg-red-950/20 p-3">
                <MonoLabel color="#ff6b6b">error</MonoLabel>
                <p className="mt-1 font-mono text-[12px] text-red-300 leading-relaxed">
                  {error}
                </p>
              </div>
            )}

            {isComplete && (
              <div className="flex flex-wrap gap-2">
                <a href={getDownloadUrl(jobId)} download>
                  <button
                    type="button"
                    className="font-mono uppercase tracking-wider text-[11px] font-bold px-6 py-3 border border-primary rounded-sm bg-primary text-[#050810] hover:bg-primary-bright active:bg-primary-muted transition-colors"
                    style={{ boxShadow: "0 0 18px rgba(0, 170, 255, 0.22)" }}
                  >
                    {"> "}download .mp4
                  </button>
                </a>
                <Link href="/generate">
                  <button
                    type="button"
                    className="font-mono uppercase tracking-wider text-[11px] px-6 py-3 border border-border rounded-sm bg-transparent text-text-muted hover:border-border-light hover:text-text transition-colors"
                  >
                    new render
                  </button>
                </Link>
              </div>
            )}

            {isFailed && (
              <div className="flex">
                <Link href="/generate">
                  <button
                    type="button"
                    className="font-mono uppercase tracking-wider text-[11px] px-6 py-3 border border-primary rounded-sm bg-transparent text-primary hover:bg-primary/10 transition-colors"
                  >
                    {"> "}try again
                  </button>
                </Link>
              </div>
            )}
          </div>

          <ResultSidebar
            audioAnalysis={audioAnalysis}
            matchedStyles={matchedStyles}
            creativeDescription={creativeDescription}
          />
        </div>
      </div>
    </main>
  );
}
