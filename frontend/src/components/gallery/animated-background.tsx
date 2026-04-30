"use client";

import { useEffect, useRef } from "react";

const BG = "#0A0C10";

/**
 * Animated background for the gallery hero.
 *
 * Beat-synced pulsing rings, faint grid, floating particles, and scanline.
 * Simulates 128 BPM pulse using sin^4 for a sharp "kick" feel.
 * Honors prefers-reduced-motion: renders one static frame, no rAF loop.
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
      const t = frameRef.current * 0.008;
      frameRef.current++;

      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, w, h);

      // Grid lines — cold blue tint
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

      // Pulsing circles synced to "beat"
      const bpm = 128;
      const beatPhase = (t * bpm) / 60;
      const pulse = Math.pow(Math.max(0, Math.sin(beatPhase * Math.PI)), 4);

      const cx = w / 2;
      const cy = h / 2;
      const baseR = 80 + pulse * 30;

      // Concentric distorted rings
      for (let ring = 0; ring < 4; ring++) {
        const r = baseR + ring * 35;
        const a = 0.14 - ring * 0.028;
        ctx.beginPath();
        for (let ang = 0; ang < Math.PI * 2; ang += 0.02) {
          const n =
            Math.sin(ang * 8 + t * 2) * 6 * pulse +
            Math.sin(ang * 3 - t) * 4;
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

      // Floating particles — brightness pulses with the beat
      for (let i = 0; i < 35; i++) {
        const s = i * 137.508;
        const px = (Math.sin(s + t * 0.3) * 0.5 + 0.5) * w * 0.8 + w * 0.1;
        const py = (Math.cos(s * 0.7 + t * 0.2) * 0.5 + 0.5) * h * 0.8 + h * 0.1;
        const sz = 1.5 + Math.sin(s + t) * 0.8;
        const a = 0.15 + pulse * 0.2;
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

      // Scan line
      const scanY = (t * 30) % h;
      ctx.fillStyle = "rgba(0,170,255,0.025)";
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
