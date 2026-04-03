"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

interface HeroVideoProps {
  src?: string;
  posterSrc?: string;
}

/**
 * Hero video section at the top of the landing page.
 * Auto-plays muted (required by browsers) with CTA overlay (D-01, D-02).
 * Gracefully falls back to gradient background when no video is available.
 */
export function HeroVideo({ src, posterSrc }: HeroVideoProps) {
  return (
    <section className="relative h-[70vh] overflow-hidden bg-surface">
      {/* Video or gradient fallback */}
      {src ? (
        <video
          className="absolute inset-0 w-full h-full object-cover"
          autoPlay
          muted
          loop
          playsInline
          poster={posterSrc}
          aria-hidden="true"
        >
          <source src={src} type="video/mp4" />
        </video>
      ) : (
        /* Gradient fallback when video is not yet available */
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse at 30% 50%, rgba(245,158,11,0.15) 0%, transparent 60%), radial-gradient(ellipse at 70% 50%, rgba(236,72,153,0.1) 0%, transparent 60%), #0a0a0a",
          }}
          aria-hidden="true"
        />
      )}

      {/* Bottom gradient overlay for CTA legibility */}
      <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/60 to-transparent" />

      {/* CTA overlay — positioned absolute bottom-center on the gradient (D-02) */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-center pb-12 px-6">
        <div className="bg-black/40 backdrop-blur-sm rounded-2xl px-8 py-6 text-center max-w-lg w-full">
          <h1 className="font-display font-bold text-3xl text-white mb-2 tracking-tight">
            AI-Powered Backdrops
          </h1>
          <p className="text-white/70 text-base mb-5">
            Generate synced visuals for concerts and parties
          </p>
          <Link href="/generate">
            <Button size="lg" className="font-display font-semibold">
              Try it yourself
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
