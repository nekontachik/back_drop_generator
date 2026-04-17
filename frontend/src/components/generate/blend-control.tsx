"use client";

import { MonoLabel } from "@/components/ui/mono-label";

const GENRES = [
  "Techno",
  "Ambient",
  "EDM",
  "Jazz",
  "Synthwave",
  "Classical",
  "DnB",
  "House",
  "Lo-fi",
  "Metal",
];

interface BlendControlProps {
  genreA: string;
  genreB: string;
  ratio: number;
  onGenreAChange: (g: string) => void;
  onGenreBChange: (g: string) => void;
  onRatioChange: (r: number) => void;
}

function HardwareButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      data-active={active}
      className="font-mono uppercase tracking-wider text-[11px] px-3 py-1.5 border border-border rounded-sm bg-transparent text-text-muted hover:border-border-light hover:text-text data-[active=true]:border-primary data-[active=true]:bg-primary/15 data-[active=true]:text-primary transition-colors"
    >
      {children}
    </button>
  );
}

export function BlendControl({
  genreA,
  genreB,
  ratio,
  onGenreAChange,
  onGenreBChange,
  onRatioChange,
}: BlendControlProps) {
  return (
    <div className="border border-border rounded-sm bg-surface-card p-4">
      <div className="flex items-center justify-between mb-3">
        <MonoLabel color="var(--color-primary)">style_blend</MonoLabel>
        <MonoLabel>
          {genreA} × {genreB}
        </MonoLabel>
      </div>

      <MonoLabel className="block mb-1.5">channel_a</MonoLabel>
      <div className="flex flex-wrap gap-1 mb-4">
        {GENRES.map((g) => (
          <HardwareButton
            key={`a-${g}`}
            active={genreA === g}
            onClick={() => onGenreAChange(g)}
          >
            {g}
          </HardwareButton>
        ))}
      </div>

      <div className="flex items-center gap-3 my-2">
        <MonoLabel color="var(--color-primary)">{100 - ratio}%</MonoLabel>
        <div
          className="flex-1 h-1.5 bg-surface-elevated rounded-[3px] relative cursor-pointer"
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const pct = Math.round(
              ((e.clientX - rect.left) / rect.width) * 100
            );
            onRatioChange(Math.max(0, Math.min(100, pct)));
          }}
        >
          <div
            className="absolute left-0 top-0 h-full rounded-[3px]"
            style={{
              width: `${ratio}%`,
              background:
                "linear-gradient(90deg, var(--color-primary), var(--color-violet))",
              boxShadow: "0 0 8px rgba(0, 170, 255, 0.2)",
            }}
          />
          <div
            className="absolute top-[-5px] w-4 h-4 bg-surface border-2 border-primary rounded-[2px]"
            style={{
              left: `${ratio}%`,
              transform: "translateX(-50%)",
            }}
          />
        </div>
        <MonoLabel color="var(--color-violet)">{ratio}%</MonoLabel>
      </div>

      <MonoLabel className="block mb-1.5 mt-3">channel_b</MonoLabel>
      <div className="flex flex-wrap gap-1">
        {GENRES.map((g) => (
          <HardwareButton
            key={`b-${g}`}
            active={genreB === g}
            onClick={() => onGenreBChange(g)}
          >
            {g}
          </HardwareButton>
        ))}
      </div>
    </div>
  );
}
