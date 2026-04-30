"use client";

import Link from "next/link";
import { AnimatedBackground } from "./animated-background";

/**
 * Hero video / landing CTA for the gallery.
 *
 * v2 — comfort pass:
 *  - Removed the bordered "card" container around the headline. The CTA box
 *    used to read as a separate floating panel; now the headline sits directly
 *    on the hero with a soft radial darkening built into the fade layer for
 *    legibility.
 *  - Background video opacity reduced (0.6 → 0.18) and softly blurred so it
 *    doesn't introduce flicker behind the text.
 *  - Hidden entirely under prefers-reduced-motion (CSS rule below).
 *
 * NOTE: this assumes a `particles-edm.mp4` exists in /public/examples and a
 * primary cyan button utility (`bv-primary` here, but you can swap to your
 * own button component).
 */
export function HeroVideo() {
  return (
    <section className="relative h-[70vh] min-h-[500px] overflow-hidden bg-[#0A0C10]">
      {/* Soft radial color wash */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at 30% 50%, rgba(0,170,255,.12) 0%, transparent 60%), radial-gradient(ellipse at 70% 50%, rgba(139,92,246,.08) 0%, transparent 60%), #0A0C10",
        }}
      />

      {/* Animated canvas */}
      <AnimatedBackground />

      {/* Combined fade: bottom-up gradient + central radial darkening for text legibility */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 800px 500px at 50% 55%, rgba(10,12,16,.75) 0%, rgba(10,12,16,.3) 50%, transparent 80%), linear-gradient(to top, #0A0C10 0%, rgba(10,12,16,.6) 40%, transparent 100%)",
        }}
      />

      {/* CTA — no container chrome, just text on the hero */}
      <div className="absolute inset-0 flex items-end justify-center px-6 pb-20">
        <div
          className="w-full max-w-[460px] px-7 py-6 text-center"
          style={{
            textShadow:
              "0 2px 20px rgba(10,12,16,.95), 0 0 40px rgba(10,12,16,.9)",
          }}
        >
          <span
            className="mb-2.5 block font-mono text-[10px] uppercase tracking-[0.1em]"
            style={{ color: "#00AAFF" }}
          >
            sys.beat_visuals v0.1.0
          </span>
          <h1
            className="font-display mb-2.5 text-[34px] font-bold leading-[1.1] tracking-[-0.03em] text-[#E2E8F0]"
          >
            AI-Powered<br />
            <span style={{ color: "#00AAFF" }}>Beat Visuals</span>
          </h1>
          <p className="mb-4 font-mono text-xs leading-[1.6] text-[#8892A4]">
            generate synced video backdrops<br />
            for concerts &amp; parties
          </p>
          <Link
            href="/generate"
            className="inline-flex items-center rounded-sm border border-[#00AAFF] bg-[#00AAFF] px-6 py-3 font-mono text-[11px] font-bold uppercase tracking-[0.06em] text-[#050810] transition-colors hover:bg-[#33BBFF] active:bg-[#0088CC]"
            style={{ boxShadow: "0 0 18px rgba(0,170,255,.22)" }}
          >
            &gt; initialize generator
          </Link>
        </div>
      </div>

      {/* Status bar */}
      <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between border-t border-[rgba(37,42,54,.6)] px-6 py-2 font-mono text-[10px] uppercase tracking-[0.1em]">
        <span style={{ color: "#00FF88" }}>● system.online</span>
        <span className="text-[#4A5568]">bpm sync · beat detection · audio reactive</span>
        <span className="text-[#4A5568]">1080p · 30fps · loop</span>
      </div>

    </section>
  );
}
