"use client";

import { useState } from "react";
import { HeroVideo } from "@/components/gallery/hero-video";
import { Carousel } from "@/components/gallery/carousel";
import { SessionTable } from "@/components/gallery/session-table";
import { MonoLabel } from "@/components/ui/mono-label";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  {
    id: "1",
    src: "/examples/preset-techno.mp4",
    prompt: "Neon tunnel pulsing to heavy techno beats",
    genre: "Techno",
    effect: "tunnel",
    bpm: 138,
  },
  {
    id: "2",
    src: "/examples/fractal-ambient.mp4",
    prompt: "Ethereal fractal morphing in soft ambient hues",
    genre: "Ambient",
    effect: "fractal",
    bpm: 72,
  },
  {
    id: "3",
    src: "/examples/particles-edm.mp4",
    prompt: "Explosive particle storm synced to EDM drops",
    genre: "EDM",
    effect: "particles",
    bpm: 128,
  },
  {
    id: "4",
    src: "/examples/plasma-jazz.mp4",
    prompt: "Smooth plasma waves flowing with jazz rhythms",
    genre: "Jazz",
    effect: "plasma",
    bpm: 110,
  },
  {
    id: "5",
    src: "/examples/preset-synthwave.mp4",
    prompt: "Retro synthwave tunnel with neon grids",
    genre: "Synthwave",
    effect: "tunnel",
    bpm: 118,
  },
  {
    id: "6",
    src: "/examples/fractal-classical.mp4",
    prompt: "Elegant fractal bloom following classical dynamics",
    genre: "Classical",
    effect: "fractal",
    bpm: 90,
  },
];

type ViewMode = "table" | "cards";

export default function GalleryPage() {
  const [viewMode, setViewMode] = useState<ViewMode>("table");

  return (
    <main className="min-h-screen">
      <HeroVideo />

      <section className="px-6 lg:px-12 py-8">
        <div className="flex items-baseline justify-between mb-4">
          <div className="flex items-baseline gap-3">
            <MonoLabel color="var(--color-primary)">examples</MonoLabel>
            <MonoLabel>{EXAMPLES.length} clips loaded</MonoLabel>
          </div>
          <div className="flex gap-0.5">
            {(["table", "cards"] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setViewMode(mode)}
                aria-pressed={viewMode === mode}
                className={cn(
                  "font-mono text-[11px] uppercase tracking-wider px-3 py-1 rounded-sm border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50",
                  viewMode === mode
                    ? "border-primary bg-primary/15 text-primary"
                    : "border-border bg-transparent text-text-muted hover:border-border-light hover:text-text"
                )}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {viewMode === "table" ? (
          <SessionTable items={EXAMPLES} />
        ) : (
          <Carousel items={EXAMPLES} />
        )}
      </section>
    </main>
  );
}
