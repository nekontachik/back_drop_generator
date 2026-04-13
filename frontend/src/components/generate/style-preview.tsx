"use client";

import { useState, useEffect } from "react";
import { Zap } from "lucide-react";
import { getStyles } from "@/lib/api";
import type { StyleMatch } from "@/lib/types";
import { Card, CardHeader, CardContent } from "@/components/ui/card";

interface StylePreviewProps {
  prompt: string;
  genreA?: string;
  genreB?: string;
}

function SkeletonCard() {
  return (
    <div className="animate-pulse bg-surface-elevated rounded-xl h-32 border border-white/5" />
  );
}

export function StylePreview({ prompt, genreA, genreB }: StylePreviewProps) {
  const [styles, setStyles] = useState<StyleMatch[]>([]);
  const [loading, setLoading] = useState(false);

  // Build enriched query: prompt + genre context so RAG reflects current settings
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
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-accent-amber" />
        <h2 className="text-lg font-semibold text-white">Matched Styles</h2>
      </div>

      {loading && (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {!loading && (!prompt || prompt.length < 3) && (
        <p className="text-white/40 text-sm py-8 text-center">
          Start typing a prompt to see matched styles...
        </p>
      )}

      {!loading && styles.length === 0 && prompt.length >= 3 && (
        <p className="text-white/40 text-sm py-8 text-center">
          No styles matched. Try a different prompt.
        </p>
      )}

      {!loading && styles.length > 0 && (
        <div className="space-y-3">
          {styles.map((style) => (
            <Card key={style.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-lg font-semibold text-white">{style.genre}</h3>
                  <span className="text-xs text-accent-amber flex-shrink-0">
                    Match: {Math.round((1 - style.distance) * 100)}%
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-white/60">{style.description}</p>

                {style.colors.length > 0 && (
                  <div className="flex items-center gap-1.5">
                    {style.colors.map((color, i) => (
                      <span
                        key={i}
                        className="w-5 h-5 rounded-full border border-white/10 flex-shrink-0"
                        style={{ backgroundColor: color }}
                        title={color}
                      />
                    ))}
                  </div>
                )}

                {style.shapes.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {style.shapes.map((shape) => (
                      <span
                        key={shape}
                        className="px-2 py-0.5 rounded text-xs bg-white/5 border border-white/10 text-white/60"
                      >
                        {shape}
                      </span>
                    ))}
                  </div>
                )}

                {style.movement && (
                  <p className="text-xs text-white/40 italic">{style.movement}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
