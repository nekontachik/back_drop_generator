"use client";

import { useEffect, useRef } from "react";

const BG = "#0A0C10";

/**
 * Animated background for the gallery hero.
 *
 * Renders a faint grid, slowly pulsing concentric rings, and a scanline.
 * One full pulse cycle ≈ 10s — barely perceptible, photo-sensitive safe.
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
