"use client";

import { useState } from "react";
import { GenerateForm } from "@/components/generate/generate-form";
import { StylePreview } from "@/components/generate/style-preview";
import { MonoLabel } from "@/components/ui/mono-label";

export default function GeneratePage() {
  const [prompt, setPrompt] = useState("");
  const [genreA, setGenreA] = useState("Techno");
  const [genreB, setGenreB] = useState("Ambient");
  const [blend, setBlend] = useState(70);
  const [bpm, setBpm] = useState(120);

  return (
    <main className="min-h-screen">
      <div className="max-w-[960px] mx-auto px-6 py-8">
        <div className="mb-6">
          <MonoLabel color="var(--color-primary)">module::generate</MonoLabel>
          <h1 className="mt-1 text-2xl font-display font-bold text-text tracking-tight">
            Create Backdrop
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6">
          <div>
            <GenerateForm
              onPromptChange={setPrompt}
              onGenreAChange={setGenreA}
              onGenreBChange={setGenreB}
              onBlendChange={setBlend}
              onBpmChange={setBpm}
            />
          </div>

          <div className="lg:sticky lg:top-20 h-fit">
            <StylePreview
              prompt={prompt}
              genreA={genreA}
              genreB={genreB}
              blend={blend}
              bpm={bpm}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
