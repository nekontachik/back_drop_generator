"use client";

import { useState } from "react";
import { GenerateForm } from "@/components/generate/generate-form";
import { StylePreview } from "@/components/generate/style-preview";

export default function GeneratePage() {
  const [prompt, setPrompt] = useState("");

  return (
    <main className="min-h-screen">
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
          <GenerateForm onPromptChange={setPrompt} />
        </div>

        {/* Right column: live style preview */}
        <div className="lg:sticky lg:top-20 h-fit">
          <StylePreview prompt={prompt} />
        </div>
      </div>
    </main>
  );
}
