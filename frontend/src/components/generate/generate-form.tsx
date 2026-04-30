"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Loader2, ChevronDown } from "lucide-react";
import { submitGenerate, analyzeAudio } from "@/lib/api";
import type { BpmResult } from "@/lib/types";
import { MonoLabel } from "@/components/ui/mono-label";
import { AudioUpload } from "./audio-upload";
import { BpmInput } from "./bpm-input";
import { BlendControl } from "./blend-control";

const MAX_PROMPT = 500;

function CollapsibleSection({
  label,
  hint,
  children,
  defaultOpen = false,
}: {
  label: string;
  hint: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border border-border rounded-sm bg-surface-card overflow-hidden transition-colors">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-elevated transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
      >
        <div className="flex items-center gap-3">
          <MonoLabel color={open ? "var(--color-primary)" : undefined}>
            {open ? "−" : "+"} {label}
          </MonoLabel>
          {!open && (
            <span className="font-mono text-[10px] text-text-dim">
              {hint}
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-3.5 h-3.5 text-text-dim transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      {open && <div className="px-0">{children}</div>}
    </div>
  );
}

interface GenerateFormProps {
  onPromptChange: (prompt: string) => void;
  onGenreAChange?: (genre: string) => void;
  onGenreBChange?: (genre: string) => void;
  onBlendChange?: (ratio: number) => void;
  onBpmChange?: (bpm: number) => void;
}

export function GenerateForm({
  onPromptChange,
  onGenreAChange,
  onGenreBChange,
  onBlendChange,
  onBpmChange,
}: GenerateFormProps) {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [bpm, setBpm] = useState(120);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [detectedBpm, setDetectedBpm] = useState<BpmResult | null>(null);
  const [genreA, setGenreA] = useState("Techno");
  const [genreB, setGenreB] = useState("Ambient");
  const [blendRatio, setBlendRatio] = useState(70);
  const [bpmTouched, setBpmTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handlePromptChange(value: string) {
    const trimmed = value.slice(0, MAX_PROMPT);
    setPrompt(trimmed);
    onPromptChange(trimmed);
  }

  function handleGenreAChange(g: string) {
    setGenreA(g);
    onGenreAChange?.(g);
  }

  function handleGenreBChange(g: string) {
    setGenreB(g);
    onGenreBChange?.(g);
  }

  function handleBlendChange(r: number) {
    setBlendRatio(r);
    onBlendChange?.(r);
  }

  function handleBpmChange(v: number) {
    setBpm(v);
    setBpmTouched(true);
    onBpmChange?.(v);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("bpm", String(bpm));
    if (audioFile && bpmTouched) {
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
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="border border-border rounded-sm bg-surface-card overflow-hidden focus-within:border-primary/50 transition-colors">
        <div className="flex items-center justify-between px-3 py-2 border-b border-border">
          <MonoLabel color="var(--color-primary)">visual_prompt</MonoLabel>
          <MonoLabel>
            {prompt.length}/{MAX_PROMPT}
          </MonoLabel>
        </div>
        <textarea
          id="prompt"
          rows={4}
          value={prompt}
          onChange={(e) => handlePromptChange(e.target.value)}
          placeholder="> describe your visual style or upload audio below..."
          className="block w-full bg-transparent border-0 px-3 py-3 text-text font-mono text-[13px] leading-relaxed resize-y focus:outline-none placeholder:text-text-dim"
        />
      </div>

      <CollapsibleSection
        label="style_blend"
        hint={`${genreA.toLowerCase()} × ${genreB.toLowerCase()} · ${blendRatio}%`}
      >
        <BlendControl
          genreA={genreA}
          genreB={genreB}
          ratio={blendRatio}
          onGenreAChange={handleGenreAChange}
          onGenreBChange={handleGenreBChange}
          onRatioChange={handleBlendChange}
          embedded
        />
      </CollapsibleSection>

      <CollapsibleSection
        label="tempo_&_audio"
        hint={`${bpm} bpm${audioFile ? " · " + audioFile.name : ""}`}
      >
        <BpmInput
          value={bpm}
          onChange={handleBpmChange}
          detectedBpm={detectedBpm}
          embedded
          audioSlot={
            <AudioUpload
              file={audioFile}
              analyzing={analyzing}
              onFileChange={async (f) => {
                setAudioFile(f);
                if (!f) {
                  setDetectedBpm(null);
                  setBpmTouched(false);
                  return;
                }
                // Analyze audio and auto-fill prompt + BPM
                setAnalyzing(true);
                setError(null);
                try {
                  const result = await analyzeAudio(f);
                  setDetectedBpm(result.analysis.bpm);
                  setBpm(result.analysis.bpm.detected);
                  onBpmChange?.(result.analysis.bpm.detected);
                  if (!prompt.trim()) {
                    const suggested = result.suggested_prompt.slice(0, MAX_PROMPT);
                    setPrompt(suggested);
                    onPromptChange(suggested);
                  }
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Audio analysis failed");
                } finally {
                  setAnalyzing(false);
                }
              }}
            />
          }
        />
      </CollapsibleSection>

      <button
        type="submit"
        disabled={submitting || (!prompt.trim() && !audioFile)}
        className="w-full font-mono uppercase tracking-wider text-[11px] font-bold px-6 py-3 border border-primary rounded-sm bg-primary text-[#050810] hover:bg-primary-bright active:bg-primary-muted disabled:opacity-50 disabled:pointer-events-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
        style={{ boxShadow: "0 0 18px rgba(0, 170, 255, 0.22)" }}
      >
        {submitting ? (
          <span className="inline-flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            submitting...
          </span>
        ) : (
          "> execute render pipeline"
        )}
      </button>

      {error && (
        <p className="font-mono text-[11px] text-red-400 text-center">
          ! {error}
        </p>
      )}
    </form>
  );
}
