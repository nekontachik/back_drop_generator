"use client";

import { useEffect, useRef } from "react";

const BG = "#0A0C10";

/**
 * Animated background for the gallery hero.
 *
 * v2 — accessibility + comfort pass:
 *  - Slowed the animation clock ~7× vs v1 so the pulse is barely perceptible
 *    instead of stroboscopic. One full cycle ≈ 10s.
 *  - Pulse amplitude reduced from 0..1 (sin^4) to 0.45..0.55 (gentle sine).
 *  - Particles use fixed alpha — no flicker.
 *  - Scanline travels ~2.5× slower and is more transparent.
 *  - Honors prefers-reduced-motion: renders one static frame, no rAF loop.
 */
export function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const cv = canvasRef.current;
    if (!cv) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;

    let id = 0;
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Equalizer state: heights update every ~90 frames (~1.5s), render stays static between
    const EQ_BARS = 20;
    const EQ_UPDATE_INTERVAL = 90;
    let eqSegCounts = new Array(EQ_BARS).fill(0);
    let eqLastUpdate = -EQ_UPDATE_INTERVAL; // force first update

    const resize = () => {
      cv.width = cv.offsetWidth * 2;
      cv.height = cv.offsetHeight * 2;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(2, 2);
    };
    resize();

    const draw = () => {
      const w = cv.offsetWidth;
      const h = cv.offsetHeight;

      // Very slow clock — pulses barely perceptible, photo-sensitive safe.
      const t = frameRef.current * 0.0012;
      frameRef.current++;

      // Background fill
      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, w, h);

      // Faint grid
      ctx.strokeStyle = "rgba(0,170,255,0.035)";
      ctx.lineWidth = 0.5;
      for (let x = 0; x < w; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // LED-style equalizer — visible bars, heights update every ~1.5s.
      const segH = 4;
      const segGap = 2;
      const segStep = segH + segGap;
      const maxSegs = Math.floor((h * 0.35) / segStep);
      const eqBarW = Math.floor(w / EQ_BARS);
      const frame = frameRef.current - 1;

      // Recalculate bar heights infrequently
      if (frame - eqLastUpdate >= EQ_UPDATE_INTERVAL) {
        eqLastUpdate = frame;
        const eqT = frame * 0.0012 * 0.12;
        for (let i = 0; i < EQ_BARS; i++) {
          const level =
            Math.sin(eqT + i * 1.1) * 0.35 +
            Math.sin(eqT * 0.6 + i * 0.7) * 0.15 + 0.5;
          eqSegCounts[i] = Math.round(level * maxSegs);
        }
      }

      // Render cached bar heights with visible opacity
      for (let i = 0; i < EQ_BARS; i++) {
        const x = i * eqBarW;
        const segs = eqSegCounts[i];
        for (let s = 0; s < segs; s++) {
          const y = h - (s + 1) * segStep;
          // Fade out toward the top — bottom segments brighter
          const fade = 1.0 - (s / maxSegs) * 0.6;
          const a = 0.1 * fade;
          ctx.fillStyle =
            i % 3 === 0
              ? `rgba(0,170,255,${a})`
              : i % 3 === 1
                ? `rgba(139,92,246,${a})`
                : `rgba(0,255,136,${a * 0.8})`;
          ctx.fillRect(x + 3, y, eqBarW - 6, segH);
        }
      }

      // Extremely slow pulse — one cycle ≈ 10s, oscillates 0.45..0.55.
      const phase = t * 0.35;
      const pulse = 0.5 + 0.05 * Math.sin(phase * Math.PI * 2);
      const cx = w / 2;
      const cy = h / 2;
      const baseR = 100 + pulse * 6;

      // Concentric distorted rings
      for (let ring = 0; ring < 4; ring++) {
        const r = baseR + ring * 35;
        const a = 0.09 - ring * 0.018;
        ctx.beginPath();
        for (let ang = 0; ang < Math.PI * 2; ang += 0.02) {
          const n =
            Math.sin(ang * 8 + t * 2) * 3 * pulse +
            Math.sin(ang * 3 - t) * 2;
          const px = cx + Math.cos(ang) * (r + n);
          const py = cy + Math.sin(ang) * (r + n);
          if (ang === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.strokeStyle =
          ring % 2 === 0
            ? `rgba(0,170,255,${a})`
            : `rgba(139,92,246,${a * 0.7})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      // Particles — constant brightness (no flicker), slow drift only.
      for (let i = 0; i < 35; i++) {
        const s = i * 137.508;
        const px = (Math.sin(s + t * 0.3) * 0.5 + 0.5) * w * 0.8 + w * 0.1;
        const py = (Math.cos(s * 0.7 + t * 0.2) * 0.5 + 0.5) * h * 0.8 + h * 0.1;
        const sz = 1.3 + Math.sin(s + t * 0.5) * 0.4;
        const a = 0.18; // fixed
        ctx.fillStyle =
          i % 4 === 0
            ? `rgba(0,170,255,${a})`
            : i % 4 === 1
              ? `rgba(0,255,136,${a * 0.5})`
              : i % 4 === 2
                ? `rgba(139,92,246,${a * 0.6})`
                : `rgba(0,170,255,${a * 0.3})`;
        ctx.beginPath();
        ctx.arc(px, py, sz, 0, Math.PI * 2);
        ctx.fill();
      }

      // Slow, faint scanline
      const scanY = (t * 12) % h;
      ctx.fillStyle = "rgba(0,170,255,0.02)";
      ctx.fillRect(0, scanY, w, 2);

      if (!reduced) id = requestAnimationFrame(draw);
    };

    draw();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(id);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 h-full w-full opacity-70"
      aria-hidden
    />
  );
}
