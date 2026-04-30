"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { X, Volume2, VolumeX } from "lucide-react";
import { MonoLabel } from "@/components/ui/mono-label";
import { Badge } from "@/components/ui/badge";
import { genreColor } from "@/lib/genre-colors";

interface SessionItem {
  id: string;
  src: string;
  prompt: string;
  genre: string;
  effect?: string;
  bpm?: number;
}

interface SessionTableProps {
  items: SessionItem[];
}

const GRID_CLASSES =
  "grid grid-cols-[30px_1fr_72px_48px] sm:grid-cols-[40px_1fr_90px_70px_60px_48px] gap-px";

function ModalVideo({ src }: { src: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [isMuted, setIsMuted] = useState(true);

  function toggleMute() {
    if (ref.current) {
      ref.current.muted = !ref.current.muted;
      setIsMuted(ref.current.muted);
    }
  }

  return (
    <div className="relative aspect-video rounded-sm overflow-hidden bg-black border border-border">
      <video
        ref={ref}
        className="w-full h-full object-cover"
        autoPlay
        muted
        loop
        playsInline
        controls
      >
        <source src={src} type="video/mp4" />
      </video>
      <button
        onClick={toggleMute}
        className="absolute top-3 right-3 z-10 w-8 h-8 rounded-sm bg-black/60 border border-border flex items-center justify-center text-text-muted hover:text-primary hover:border-primary transition-colors"
        aria-label={isMuted ? "Unmute" : "Mute"}
      >
        {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
      </button>
    </div>
  );
}

export function SessionTable({ items }: SessionTableProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const [selected, setSelected] = useState<SessionItem | null>(null);

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
      <div className="flex flex-col gap-px">
        {/* Column headers */}
        <div className={`${GRID_CLASSES} py-1.5 border-b border-border`}>
          <MonoLabel className="text-center">#</MonoLabel>
          <MonoLabel>prompt</MonoLabel>
          <MonoLabel>genre</MonoLabel>
          <MonoLabel className="hidden sm:block">effect</MonoLabel>
          <MonoLabel>bpm</MonoLabel>
          <MonoLabel className="hidden sm:block text-center">▶</MonoLabel>
        </div>

        {items.map((ex, i) => {
          const color = genreColor(ex.genre);
          const isHovered = hovered === i;
          return (
            <div
              key={ex.id}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => setSelected(ex)}
              className={`${GRID_CLASSES} py-2.5 border-b border-border cursor-pointer items-center transition-colors`}
              style={{
                background: isHovered ? `${color}08` : "transparent",
              }}
            >
              <span className="font-mono text-[11px] text-text-dim text-center">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span
                className="font-sans text-[13px] overflow-hidden text-ellipsis whitespace-nowrap transition-colors"
                style={{
                  color: isHovered
                    ? "var(--color-text)"
                    : "var(--color-text-muted)",
                }}
              >
                {ex.prompt}
              </span>
              <Badge color={color}>{ex.genre}</Badge>
              <span className="hidden sm:inline font-mono text-[11px] text-text-dim">
                {ex.effect}
              </span>
              <span
                className="font-mono text-xs transition-colors"
                style={{
                  color: isHovered ? color : "var(--color-text-muted)",
                }}
              >
                {ex.bpm}
              </span>
              <div className="hidden sm:block text-center">
                <span
                  className="inline-block w-6 h-6 rounded-sm border text-[10px] leading-[22px] text-center transition-all"
                  style={{
                    borderColor: isHovered ? color : "var(--color-border)",
                    color: isHovered ? color : "var(--color-text-dim)",
                    background: isHovered ? `${color}15` : "transparent",
                  }}
                >
                  ▶
                </span>
              </div>
            </div>
          );
        })}
      </div>

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
            <button
              onClick={() => setSelected(null)}
              className="absolute -top-10 right-0 text-text-muted hover:text-text transition-colors flex items-center gap-1.5 text-sm font-mono"
            >
              <X className="w-4 h-4" /> close
            </button>
            <ModalVideo src={selected.src} />
            <div className="mt-3 flex items-center justify-between px-1">
              <div className="flex items-center gap-3">
                <Badge color={genreColor(selected.genre)}>
                  {selected.genre}
                </Badge>
                {selected.bpm && (
                  <MonoLabel>{selected.bpm} bpm</MonoLabel>
                )}
              </div>
              <p className="text-text-muted text-sm font-mono truncate max-w-xs">
                {selected.prompt}
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
