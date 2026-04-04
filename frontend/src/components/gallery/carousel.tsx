"use client";

import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
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

/**
 * Horizontally scrolling carousel of example video cards (D-03).
 * Cards show prompt text on hover. Videos preview on hover.
 * Arrow buttons for keyboard/click navigation.
 */
export function Carousel({ items }: CarouselProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  function scrollLeft() {
    containerRef.current?.scrollBy({ left: -320, behavior: "smooth" });
  }

  function scrollRight() {
    containerRef.current?.scrollBy({ left: 320, behavior: "smooth" });
  }

  function handleMouseEnter(e: React.MouseEvent<HTMLVideoElement>) {
    const video = e.currentTarget;
    video.play().catch(() => {
      // Autoplay may be blocked; silently ignore
    });
  }

  function handleMouseLeave(e: React.MouseEvent<HTMLVideoElement>) {
    const video = e.currentTarget;
    video.pause();
    video.currentTime = 0;
  }

  return (
    <section className="px-6 lg:px-12 py-12">
      <h2 className="font-display font-semibold text-2xl text-white mb-6">
        Example Generations
      </h2>

      <div className="relative">
        {/* Left arrow */}
        <button
          onClick={scrollLeft}
          className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 bg-surface-elevated border border-white/10 rounded-full p-2 text-white/60 hover:text-white hover:bg-surface-card transition-colors hidden md:flex items-center justify-center"
          aria-label="Scroll left"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        {/* Scrollable container */}
        <div
          ref={containerRef}
          className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide"
        >
          {items.map((item) => (
            <Card
              key={item.id}
              className="snap-start flex-shrink-0 w-[300px] group relative cursor-pointer"
            >
              {/* Video with hover-to-preview */}
              <div className="relative aspect-video bg-surface-elevated overflow-hidden">
                <video
                  className="w-full h-full object-cover"
                  muted
                  loop
                  playsInline
                  preload="metadata"
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                  aria-label={item.prompt}
                >
                  <source src={item.src} type="video/mp4" />
                </video>

                {/* Fallback gradient when video not loaded */}
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

                {/* Hover overlay showing prompt text (D-03) */}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent px-3 py-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <p className="text-white text-xs leading-snug line-clamp-2">
                    {item.prompt}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Right arrow */}
        <button
          onClick={scrollRight}
          className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 bg-surface-elevated border border-white/10 rounded-full p-2 text-white/60 hover:text-white hover:bg-surface-card transition-colors hidden md:flex items-center justify-center"
          aria-label="Scroll right"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </section>
  );
}
