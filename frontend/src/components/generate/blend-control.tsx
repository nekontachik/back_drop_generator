"use client";

const GENRES = [
  "Techno",
  "Ambient",
  "EDM",
  "Jazz",
  "Hip Hop",
  "Classical",
  "Synthwave",
  "Drum & Bass",
  "House",
  "Trance",
];

interface BlendControlProps {
  genreA: string;
  genreB: string;
  ratio: number;
  onGenreAChange: (g: string) => void;
  onGenreBChange: (g: string) => void;
  onRatioChange: (r: number) => void;
}

export function BlendControl({
  genreA,
  genreB,
  ratio,
  onGenreAChange,
  onGenreBChange,
  onRatioChange,
}: BlendControlProps) {
  const selectClass =
    "bg-surface-elevated border border-white/10 rounded-lg px-4 py-2.5 text-white focus:border-accent-amber focus:outline-none w-full";

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-white">Style Blend</label>
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <select
            value={genreA}
            onChange={(e) => onGenreAChange(e.target.value)}
            className={selectClass}
          >
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-[2] flex flex-col items-center gap-1">
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={ratio}
            onChange={(e) => onRatioChange(Number(e.target.value))}
            className="w-full accent-amber h-1.5 rounded-full cursor-pointer"
            style={{ accentColor: "#f59e0b" }}
          />
          <div className="flex w-full justify-between text-xs text-white/40">
            <span>
              {genreA} {ratio}%
            </span>
            <span>
              {genreB} {100 - ratio}%
            </span>
          </div>
        </div>

        <div className="flex-1">
          <select
            value={genreB}
            onChange={(e) => onGenreBChange(e.target.value)}
            className={selectClass}
          >
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
