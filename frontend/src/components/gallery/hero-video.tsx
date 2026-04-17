"use client";

import Link from "next/link";
import { AnimatedBackground } from "./animated-background";
import { MonoLabel } from "@/components/ui/mono-label";

interface HeroVideoProps {
  src?: string;
  posterSrc?: string;
}

export function HeroVideo({ src, posterSrc }: HeroVideoProps) {
  return (
    <section className="relative h-[70vh] overflow-hidden bg-surface">
      {/* Base gradient — subtle blue-tinted radial */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at 30% 50%, rgba(0,170,255,0.12) 0%, transparent 60%), radial-gradient(ellipse at 70% 50%, rgba(139,92,246,0.08) 0%, transparent 60%), #0A0C10",
        }}
        aria-hidden="true"
      />

      {/* Animated canvas — hidden on mobile for performance */}
      <AnimatedBackground className="hidden sm:block" />

      {/* Video on top when available (semi-transparent, hidden on mobile) */}
      {src && (
        <video
          className="absolute inset-0 w-full h-full object-cover hidden sm:block opacity-60 mix-blend-screen"
          autoPlay
          muted
          loop
          playsInline
          preload="none"
          poster={posterSrc}
          aria-hidden="true"
        >
          <source src={src} type="video/mp4" />
        </video>
      )}

      {/* Scan lines overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
        }}
        aria-hidden="true"
      />

      {/* Bottom fade for CTA legibility */}
      <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/60 to-transparent" />

      {/* CTA */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-center pb-16 px-6">
        <div
          className="rounded-sm border border-border backdrop-blur-md px-8 py-6 text-center max-w-lg w-full"
          style={{ background: "rgba(10,12,16,0.6)" }}
        >
          <MonoLabel
            color="var(--color-primary)"
            className="!text-[11px] block mb-3"
          >
            sys.beat_visuals v0.1.0
          </MonoLabel>
          <h1 className="font-display font-bold text-3xl sm:text-4xl text-text mb-3 tracking-tight leading-[1.1]">
            AI-Powered
            <br />
            <span className="text-primary">Beat Visuals</span>
          </h1>
          <p className="font-mono text-xs text-text-muted mb-6 leading-relaxed">
            generate synced video backdrops
            <br />
            for concerts &amp; parties
          </p>
          <Link
            href="/generate"
            className="inline-flex items-center justify-center font-mono text-[11px] font-bold uppercase tracking-wider px-6 py-3 rounded-sm bg-primary text-[#050810] hover:bg-primary-bright transition-colors"
            style={{ letterSpacing: "0.06em" }}
          >
            {"> "}initialize generator
          </Link>
        </div>
      </div>

      {/* Bottom status bar */}
      <div className="absolute bottom-0 left-0 right-0 px-6 py-2 hidden sm:flex justify-between items-center border-t border-border/60">
        <MonoLabel color="var(--color-green)">● system.online</MonoLabel>
        <MonoLabel>librosa + rag + llm + opencv</MonoLabel>
        <MonoLabel>1080p · 30fps · mp4</MonoLabel>
      </div>
    </section>
  );
}
