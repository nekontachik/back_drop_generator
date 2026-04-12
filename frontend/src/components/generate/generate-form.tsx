"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { submitGenerate } from "@/lib/api";
import type { BpmResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { AudioUpload } from "./audio-upload";
import { BpmInput } from "./bpm-input";
import { BlendControl } from "./blend-control";

interface GenerateFormProps {
  onPromptChange: (prompt: string) => void;
}

export function GenerateForm({ onPromptChange }: GenerateFormProps) {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [bpm, setBpm] = useState(120);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [detectedBpm, setDetectedBpm] = useState<BpmResult | null>(null);
  const [genreA, setGenreA] = useState("Techno");
  const [genreB, setGenreB] = useState("Ambient");
  const [blendRatio, setBlendRatio] = useState(70);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handlePromptChange(value: string) {
    setPrompt(value);
    onPromptChange(value);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("bpm", String(bpm));
    if (audioFile) {
      formData.append("bpm_override", String(bpm));
    }
    formData.append("blend_genre_a", genreA);
    formData.append("blend_genre_b", genreB);
    formData.append("blend_ratio", String(blendRatio));
    if (audioFile) formData.append("audio", audioFile);

    try {
      const res = await submitGenerate(formData);
      sessionStorage.setItem(`job-${res.job_id}`, JSON.stringify(res));
      if (res.audio_analysis) setDetectedBpm(res.audio_analysis.bpm);
      router.push(`/results/${res.job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Prompt */}
      <div className="space-y-2">
        <label htmlFor="prompt" className="block text-sm font-medium text-white">
          Visual Style Prompt
        </label>
        <textarea
          id="prompt"
          rows={3}
          value={prompt}
          onChange={(e) => handlePromptChange(e.target.value)}
          placeholder="Describe the visual style you want... (e.g., 'Neon tunnel pulsing to heavy techno beats')"
          className="bg-surface-elevated border border-white/10 rounded-lg px-4 py-3 text-white w-full resize-none focus:border-accent-amber focus:ring-1 focus:ring-accent-amber/50 focus:outline-none placeholder:text-white/30"
          required
        />
      </div>

      {/* Audio upload */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-white">
          Audio File{" "}
          <span className="text-xs text-white/40 font-normal">(optional — for BPM detection)</span>
        </label>
        <AudioUpload
          file={audioFile}
          onFileChange={(f) => {
            setAudioFile(f);
            if (!f) setDetectedBpm(null);
          }}
        />
      </div>

      {/* BPM */}
      <BpmInput value={bpm} onChange={setBpm} detectedBpm={detectedBpm} />

      {/* Blend control */}
      <BlendControl
        genreA={genreA}
        genreB={genreB}
        ratio={blendRatio}
        onGenreAChange={setGenreA}
        onGenreBChange={setGenreB}
        onRatioChange={setBlendRatio}
      />

      {/* Submit */}
      <div className="pt-2">
        <Button
          type="submit"
          size="lg"
          className="w-full"
          disabled={submitting || !prompt.trim()}
        >
          {submitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Submitting...
            </>
          ) : (
            "Generate Backdrop"
          )}
        </Button>

        {error && (
          <p className="mt-3 text-sm text-red-400 text-center">{error}</p>
        )}
      </div>
    </form>
  );
}
