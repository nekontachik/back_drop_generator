"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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

  // Load generation response data stored by generate form before redirect.
  // If missing (e.g., user navigated directly), audio analysis and styles
  // simply won't be shown — the page degrades gracefully.
  useEffect(() => {
    const stored = sessionStorage.getItem(`job-${jobId}`);
    if (stored) {
      try {
        const data: GenerateResponse = JSON.parse(stored);
        setAudioAnalysis(data.audio_analysis);
        setMatchedStyles(data.matched_styles);
        setCreativeDescription(data.creative_description ?? null);
      } catch {
        // Ignore parse errors — graceful degradation
      }
      sessionStorage.removeItem(`job-${jobId}`);
    }
  }, [jobId]);

  // SSE connection for real-time render progress (FE-04)
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
      // EventSource will attempt to reconnect automatically, but if the
      // server is unreachable we surface a message and stop retrying.
      setError("Connection lost. Refresh to check status.");
      es.close();
    });

    return () => es.close();
  }, [jobId]);

  const isRendering = status === "pending" || status === "rendering";
  const isFailed = status === "failed";
  const isComplete = status === "complete";

  return (
    <main className="max-w-7xl mx-auto px-6 lg:px-12 py-8">
      {isRendering && (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-display font-semibold text-white">
              Generating Your Backdrop...
            </h1>
            <p className="text-white/50 text-sm">
              AI is blending your style parameters. Almost there.
            </p>
          </div>
          <div className="w-full max-w-xl">
            <ProgressBar progress={progress} status={status} />
          </div>
        </div>
      )}

      {isFailed && (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
          <Card className="w-full max-w-lg border-red-500/30 bg-red-950/20">
            <CardContent className="pt-6">
              <div className="flex flex-col gap-3 text-center">
                <p className="text-lg font-semibold text-red-400">Generation Failed</p>
                <p className="text-sm text-white/60">
                  {error ?? "An unexpected error occurred during rendering."}
                </p>
              </div>
            </CardContent>
          </Card>
          <Link href="/generate">
            <Button variant="outline" size="lg">
              Try Again
            </Button>
          </Link>
        </div>
      )}

      {isComplete && (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_350px] gap-6">
          <div className="flex flex-col gap-4">
            <h1 className="text-2xl font-display font-semibold text-white">
              Your Backdrop is Ready
            </h1>
            <VideoPlayer src={getDownloadUrl(jobId)} />
          </div>
          <ResultSidebar
            jobId={jobId}
            audioAnalysis={audioAnalysis}
            matchedStyles={matchedStyles}
            creativeDescription={creativeDescription}
          />
        </div>
      )}
    </main>
  );
}
