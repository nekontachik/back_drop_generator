"use client";

import { useState } from "react";
import { GenerateForm } from "@/components/generate/generate-form";
import { StylePreview } from "@/components/generate/style-preview";

export default function GeneratePage() {
  const [prompt, setPrompt] = useState("");
  const [genreA, setGenreA] = useState("Techno");
  const [genreB, setGenreB] = useState("Ambient");

  return (
    <main className="relative min-h-screen">
      {/* Animated gradient background */}
      <div
        className="fixed inset-0 -z-10 pointer-events-none"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse at 20% 50%, rgba(245,158,11,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 60% 80%, rgba(236,72,153,0.06) 0%, transparent 50%), #0a0a0a",
        }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 px-6 lg:px-12 py-8">
        {/* Left column: form */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-display font-bold text-white">
              Create Your Backdrop
            </h1>
            <p className="mt-2 text-white/60">
              Describe your visual style and let AI generate a synced backdrop for your event.
            </p>
          </div>
          <GenerateForm
            onPromptChange={setPrompt}
            onGenreAChange={setGenreA}
            onGenreBChange={setGenreB}
          />
        </div>

        {/* Right column: live style preview — on mobile shows below form */}
        <div className="lg:sticky lg:top-20 h-fit">
          <StylePreview prompt={prompt} genreA={genreA} genreB={genreB} />
        </div>
      </div>
    </main>
  );
}
