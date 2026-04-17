"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, X, Maximize2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MonoLabel } from "@/components/ui/mono-label";
import { genreColor } from "@/lib/genre-colors";

interface CarouselItem {
  id: string;
  src: string;
  prompt: string;
  genre: string;
  effect?: string;
  bpm?: number;
}

interface CarouselProps {
  items: CarouselItem[];
}

export function Carousel({ items }: CarouselProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState<CarouselItem | null>(null);

  function scrollLeft() {
    containerRef.current?.scrollBy({ left: -320, behavior: "smooth" });
  }

  function scrollRight() {
    containerRef.current?.scrollBy({ left: 320, behavior: "smooth" });
  }

  function handleMouseEnter(e: React.MouseEvent<HTMLVideoElement>) {
    e.currentTarget.play().catch(() => {});
  }

  function handleMouseLeave(e: React.MouseEvent<HTMLVideoElement>) {
    e.currentTarget.pause();
    e.currentTarget.currentTime = 0;
  }

  // Close modal on Escape
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") setSelected(null);
  }, []);

  useEffect(() => {
    if (selected) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [selected, handleKeyDown]);

  return (
    <>
      <section>
        <div className="relative">
          <button
            onClick={scrollLeft}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 bg-surface-elevated border border-border rounded-sm p-2 text-text-muted hover:text-primary hover:border-primary transition-colors hidden md:flex items-center justify-center"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          <div
            ref={containerRef}
            className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide"
          >
            {items.map((item) => {
              const color = genreColor(item.genre);
              return (
                <Card
                  key={item.id}
                  className="snap-start flex-shrink-0 w-[300px] group relative cursor-pointer"
                  onClick={() => setSelected(item)}
                >
                  <div className="relative aspect-video bg-surface-elevated overflow-hidden rounded-sm">
                    <video
                      className="w-full h-full object-cover"
                      muted
                      loop
                      playsInline
                      preload="none"
                      onMouseEnter={handleMouseEnter}
                      onMouseLeave={handleMouseLeave}
                      aria-label={item.prompt}
                    >
                      <source src={item.src} type="video/mp4" />
                    </video>

                    <div
                      className="absolute inset-0 -z-10"
                      style={{
                        background: `radial-gradient(ellipse at center, ${color}15 0%, #12151C 100%)`,
                      }}
                    />

                    {/* Genre badge */}
                    <div className="absolute top-3 left-3">
                      <Badge color={color}>{item.genre}</Badge>
                    </div>

                    {/* Fullscreen hint on hover */}
                    <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="bg-surface/80 backdrop-blur-sm p-1.5 rounded-sm border border-border flex items-center justify-center">
                        <Maximize2 className="w-3.5 h-3.5 text-text-muted" />
                      </span>
                    </div>

                    {/* Prompt overlay on hover */}
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-surface to-transparent px-3 py-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <p className="text-text text-xs leading-snug line-clamp-2 font-mono">
                        {item.prompt}
                      </p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          <button
            onClick={scrollRight}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 bg-surface-elevated border border-border rounded-sm p-2 text-text-muted hover:text-primary hover:border-primary transition-colors hidden md:flex items-center justify-center"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Fullscreen modal */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="relative w-full max-w-4xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setSelected(null)}
              className="absolute -top-10 right-0 text-text-muted hover:text-text transition-colors flex items-center gap-1.5 text-sm font-mono"
            >
              <X className="w-4 h-4" /> close
            </button>

            {/* Video */}
            <div className="relative aspect-video rounded-sm overflow-hidden bg-black border border-border">
              <video
                className="w-full h-full object-cover"
                autoPlay
                muted
                loop
                playsInline
                controls
              >
                <source src={selected.src} type="video/mp4" />
              </video>
            </div>

            {/* Info */}
            <div className="mt-3 flex items-center justify-between px-1">
              <div className="flex items-center gap-3">
                <Badge color={genreColor(selected.genre)}>{selected.genre}</Badge>
                {selected.bpm && <MonoLabel>{selected.bpm} bpm</MonoLabel>}
              </div>
              <p className="text-text-muted text-sm text-right max-w-xs truncate font-mono">
                {selected.prompt}
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
