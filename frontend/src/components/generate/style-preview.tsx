"use client";

import { useState, useEffect } from "react";
import { getStyles } from "@/lib/api";
import type { StyleMatch } from "@/lib/types";
import { MonoLabel } from "@/components/ui/mono-label";
import { Badge } from "@/components/ui/badge";

interface StylePreviewProps {
  prompt: string;
  genreA?: string;
  genreB?: string;
  blend?: number;
  bpm?: number;
}

export function StylePreview({
  prompt,
  genreA = "Techno",
  genreB = "Ambient",
  blend = 70,
  bpm = 120,
}: StylePreviewProps) {
  const [styles, setStyles] = useState<StyleMatch[]>([]);
  const [loading, setLoading] = useState(false);

  const query = [prompt, genreA, genreB].filter(Boolean).join(" ").trim();

  useEffect(() => {
    if (!query || query.length < 3) {
      setStyles([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const results = await getStyles(query);
        setStyles(results);
      } catch {
        setStyles([]);
      } finally {
        setLoading(false);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="border border-border rounded-sm bg-surface-card p-3 flex flex-col gap-4">
      <div>
        <MonoLabel color="var(--color-primary)">preview</MonoLabel>
        <div
          className="mt-2 aspect-video border border-border rounded-sm flex items-center justify-center relative overflow-hidden"
          style={{ background: "var(--color-surface)" }}
        >
          <div
            className="absolute inset-0"
            style={{
              background:
                "radial-gradient(circle at 50% 50%, rgba(0, 170, 255, 0.15), transparent 70%)",
            }}
          />
          <MonoLabel>live_preview</MonoLabel>
        </div>
      </div>

      <div>
        <MonoLabel>parameters</MonoLabel>
        <dl className="mt-2 font-mono text-[11px] leading-loose text-text-muted">
          <div>
            <span className="text-text-dim">genre_a:</span>{" "}
            <span className="text-primary">{genreA.toLowerCase()}</span>
          </div>
          <div>
            <span className="text-text-dim">genre_b:</span>{" "}
            <span className="text-violet">{genreB.toLowerCase()}</span>
          </div>
          <div>
            <span className="text-text-dim">blend:</span> {blend}%
          </div>
          <div>
            <span className="text-text-dim">tempo:</span> {bpm} bpm
          </div>
          <div>
            <span className="text-text-dim">resolution:</span> 1080p
          </div>
          <div>
            <span className="text-text-dim">fps:</span> 30
          </div>
        </dl>
      </div>

      <div>
        <MonoLabel color="var(--color-primary)">matched_styles</MonoLabel>
        {loading && (
          <div className="mt-2 space-y-1">
            <div className="animate-pulse h-14 bg-surface-elevated rounded-sm" />
            <div className="animate-pulse h-14 bg-surface-elevated rounded-sm" />
          </div>
        )}
        {!loading && styles.length === 0 && (
          <p className="mt-2 font-mono text-[11px] text-text-dim">
            {prompt.length < 3
              ? "awaiting prompt..."
              : "no match — refine query"}
          </p>
        )}
        {!loading && styles.length > 0 && (
          <div className="mt-2 flex flex-col gap-2">
            {styles.map((style) => (
              <div
                key={style.id}
                className="border border-border rounded-sm p-2"
                style={{ background: "var(--color-surface)" }}
              >
                <div className="flex items-center justify-between mb-1">
                  <Badge>{style.genre.toUpperCase()}</Badge>
                  <span className="font-mono text-[10px] text-text-dim">
                    {Math.round((1 - style.distance) * 100)}%
                  </span>
                </div>
                <p className="font-mono text-[11px] text-text-muted leading-relaxed line-clamp-2">
                  {style.description}
                </p>
                {style.colors.length > 0 && (
                  <div className="flex items-center gap-1 mt-1.5">
                    {style.colors.slice(0, 5).map((color, i) => (
                      <span
                        key={i}
                        className="w-3 h-3 rounded-sm border border-border flex-shrink-0"
                        style={{ backgroundColor: color }}
                        title={color}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
