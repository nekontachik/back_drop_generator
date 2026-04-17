"use client";

import { useEffect, useRef } from "react";

const BG = "#0A0C10";

export function AnimatedBackground({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    let animId = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * 2;
      canvas.height = canvas.offsetHeight * 2;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(2, 2);
    };
    resize();

    const draw = () => {
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;
      const t = frameRef.current * 0.008;
      frameRef.current++;

      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, w, h);

      // Grid lines — cold blue tint
      ctx.strokeStyle = "rgba(0,170,255,0.035)";
      ctx.lineWidth = 0.5;
      const gridSize = 40;
      for (let x = 0; x < w; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += gridSize) {
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

      for (let ring = 0; ring < 4; ring++) {
        const r = baseR + ring * 35;
        const alpha = 0.14 - ring * 0.028;
        ctx.beginPath();
        for (let a = 0; a < Math.PI * 2; a += 0.02) {
          const noise =
            Math.sin(a * 8 + t * 2) * 6 * pulse + Math.sin(a * 3 - t) * 4;
          const px = cx + Math.cos(a) * (r + noise);
          const py = cy + Math.sin(a) * (r + noise);
          if (a === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.strokeStyle =
          ring % 2 === 0
            ? `rgba(0, 170, 255, ${alpha})`
            : `rgba(139, 92, 246, ${alpha * 0.7})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      // Floating data particles
      for (let i = 0; i < 35; i++) {
        const seed = i * 137.508;
        const px = (Math.sin(seed + t * 0.3) * 0.5 + 0.5) * w * 0.8 + w * 0.1;
        const py =
          (Math.cos(seed * 0.7 + t * 0.2) * 0.5 + 0.5) * h * 0.8 + h * 0.1;
        const size = 1.5 + Math.sin(seed + t) * 0.8;
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
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fill();
      }

      // Scan line
      const scanY = (t * 30) % h;
      ctx.fillStyle = "rgba(0,170,255,0.025)";
      ctx.fillRect(0, scanY, w, 2);

      animId = requestAnimationFrame(draw);
    };

    draw();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        opacity: 0.7,
      }}
      aria-hidden="true"
    />
  );
}
