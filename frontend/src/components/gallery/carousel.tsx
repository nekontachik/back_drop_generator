"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, X, Maximize2 } from "lucide-react";
import { Card } from "@/components/ui/card";

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
      <section className="px-6 lg:px-12 py-12">
        <h2 className="font-display font-semibold text-2xl text-white mb-6">
          Example Generations
        </h2>

        <div className="relative">
          <button
            onClick={scrollLeft}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 bg-surface-elevated border border-white/10 rounded-full p-2 text-white/60 hover:text-white hover:bg-surface-card transition-colors hidden md:flex items-center justify-center"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          <div
            ref={containerRef}
            className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide"
          >
            {items.map((item) => (
              <Card
                key={item.id}
                className="snap-start flex-shrink-0 w-[300px] group relative cursor-pointer"
                onClick={() => setSelected(item)}
              >
                <div className="relative aspect-video bg-surface-elevated overflow-hidden rounded-xl">
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
                      background: `radial-gradient(ellipse at center, rgba(245,158,11,0.08) 0%, #141414 100%)`,
                    }}
                  />

                  {/* Genre badge */}
                  <div className="absolute top-3 left-3">
                    <span className="bg-black/60 backdrop-blur-sm text-accent-amber text-xs font-medium px-2 py-1 rounded-md">
                      {item.genre}
                    </span>
                  </div>

                  {/* Fullscreen hint on hover */}
                  <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="bg-black/60 backdrop-blur-sm p-1.5 rounded-md flex items-center justify-center">
                      <Maximize2 className="w-3.5 h-3.5 text-white/70" />
                    </span>
                  </div>

                  {/* Prompt overlay on hover */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent px-3 py-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <p className="text-white text-xs leading-snug line-clamp-2">
                      {item.prompt}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <button
            onClick={scrollRight}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 bg-surface-elevated border border-white/10 rounded-full p-2 text-white/60 hover:text-white hover:bg-surface-card transition-colors hidden md:flex items-center justify-center"
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
              className="absolute -top-10 right-0 text-white/60 hover:text-white transition-colors flex items-center gap-1.5 text-sm"
            >
              <X className="w-4 h-4" /> Close
            </button>

            {/* Video */}
            <div className="relative aspect-video rounded-xl overflow-hidden bg-black">
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
              <div>
                <span className="text-accent-amber text-sm font-medium">{selected.genre}</span>
                {selected.bpm && (
                  <span className="ml-3 text-white/40 text-sm">{selected.bpm} BPM</span>
                )}
              </div>
              <p className="text-white/50 text-sm text-right max-w-xs truncate">{selected.prompt}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
