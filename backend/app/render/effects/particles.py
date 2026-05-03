"""Particle system visual effect (VFX-03).

Renders particles with connections and beat-synced breathing. Particles
breathe outward on each beat and drift back between beats. Positions are
computed as pure functions of t and beat_intensity (no accumulated state).
All rendering is vectorized NumPy.
"""

from __future__ import annotations

import numpy as np

from app.render.effects import register
from app.render.effects.base import BaseEffect


def _hex_to_rgb(hex_color: str) -> np.ndarray:
    """Convert '#RRGGBB' hex string to float RGB array."""
    h = hex_color.lstrip("#")
    if not h:
        return np.array([0.0, 0.0, 0.0], dtype=np.float64)
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.float64)


@register
class ParticleEffect(BaseEffect):
    """Particle system with connections and beat-synced breathing."""

    @property
    def name(self) -> str:
        return "particles"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a particle frame at phase t.

        Movement model — two layers:
        1. **Drift**: gentle sinusoidal wander (slow, organic)
        2. **Breathe**: radial push outward from centre, driven by
           beat_intensity. On each beat particles expand; between beats
           they relax back. This is what the viewer *sees* as sync.

        Both are pure f(t, beat_intensity) — no accumulated state.
        """
        two_pi_t = 2.0 * np.pi * t

        # -- colours ------------------------------------------------
        bg = _hex_to_rgb(params.get("bg_color", "#0a0a0a"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff0066"))

        # -- parameters ---------------------------------------------
        intensity = params.get("intensity", 0.7)
        speed = params.get("speed", 0.5)
        count = min(params.get("count", 200), 200)
        connection_dist = params.get("connection_dist", 0.15)

        # -- stable per-particle properties (seeded) ----------------
        particle_rng = np.random.default_rng(rng.integers(0, 2**32))
        base_x = particle_rng.uniform(0.1, 0.9, count)
        base_y = particle_rng.uniform(0.1, 0.9, count)
        phase_per = particle_rng.uniform(0, 2 * np.pi, count)
        freq_per = particle_rng.uniform(0.5, 1.5, count)
        drift_amp = particle_rng.uniform(0.01, 0.04, count)
        # Per-particle radial direction for breathing (random angle)
        breathe_angle = particle_rng.uniform(0, 2 * np.pi, count)

        # -- Layer 1: gentle drift (slow sinusoidal wander) ---------
        drift_x = drift_amp * np.sin(two_pi_t * speed * 0.5 + phase_per)
        drift_y = drift_amp * np.cos(two_pi_t * speed * 0.5 * freq_per)

        # -- Layer 2: beat breathing (radial push) ------------------
        # beat_intensity is 0–1, peaking on beat, decaying between.
        # Smooth it with a power curve for snappier attack, softer tail.
        breath = beat_intensity ** 0.7  # sharpen the peak slightly
        breathe_radius = breath * intensity * 0.12  # max ~12% of screen
        breathe_x = breathe_radius * np.cos(breathe_angle)
        breathe_y = breathe_radius * np.sin(breathe_angle)

        # -- combine ------------------------------------------------
        px = np.clip(base_x + drift_x + breathe_x, 0.0, 1.0)
        py = np.clip(base_y + drift_y + breathe_y, 0.0, 1.0)

        # Pixel coordinates
        px_pix = (px * (width - 1)).astype(int)
        py_pix = (py * (height - 1)).astype(int)

        # -- background ---------------------------------------------
        frame = np.full((height, width, 3), bg, dtype=np.float64)

        # -- connections (vectorized distance matrix) ----------------
        dx = px[:, None] - px[None, :]
        dy = py[:, None] - py[None, :]
        dists = np.sqrt(dx**2 + dy**2)

        # Connection distance also breathes — on beat, particles are
        # further apart so allow wider connections to keep the mesh.
        conn_threshold = connection_dist * (1.0 + 0.5 * breath)
        i_idx, j_idx = np.where(np.triu(dists < conn_threshold, k=1))

        # Line opacity also reacts to beat — brighter on hit
        base_line_alpha = 0.3 + 0.3 * breath
        for idx in range(min(len(i_idx), 500)):
            x0, y0 = px_pix[i_idx[idx]], py_pix[i_idx[idx]]
            x1, y1 = px_pix[j_idx[idx]], py_pix[j_idx[idx]]

            num_steps = max(abs(x1 - x0), abs(y1 - y0), 1)
            ts = np.linspace(0, 1, num_steps + 1)
            lx = np.clip((x0 + (x1 - x0) * ts).astype(int), 0, width - 1)
            ly = np.clip((y0 + (y1 - y0) * ts).astype(int), 0, height - 1)

            dist_val = dists[i_idx[idx], j_idx[idx]]
            alpha = (1.0 - dist_val / conn_threshold) * base_line_alpha
            # Lines shift toward accent on beat
            line_color = primary * (1.0 - breath * 0.5) + accent * (breath * 0.5)
            for c in range(3):
                frame[ly, lx, c] = frame[ly, lx, c] * (1 - alpha) + line_color[c] * alpha

        # -- particles (circles) ------------------------------------
        # Particle size also breathes — bigger on beat
        base_radius = max(2, int(min(width, height) * 0.004))
        beat_radius = base_radius + int(breath * intensity * min(width, height) * 0.004)
        radius_px = max(base_radius, beat_radius)
        yy, xx = np.mgrid[-radius_px:radius_px + 1, -radius_px:radius_px + 1]
        circle_mask = (xx**2 + yy**2) <= radius_px**2

        # Colour shifts from primary → accent on beat
        particle_color = primary * (1.0 - breath * intensity) + accent * (breath * intensity)

        # Glow alpha — particles are brighter on beat
        particle_alpha = 0.7 + 0.3 * breath

        for p in range(count):
            cx, cy = px_pix[p], py_pix[p]
            draw_y = cy + yy[circle_mask]
            draw_x = cx + xx[circle_mask]
            valid = (draw_x >= 0) & (draw_x < width) & (draw_y >= 0) & (draw_y < height)
            if valid.any():
                for c in range(3):
                    frame[draw_y[valid], draw_x[valid], c] = (
                        frame[draw_y[valid], draw_x[valid], c] * (1 - particle_alpha)
                        + particle_color[c] * particle_alpha
                    )

        return np.clip(frame, 0, 255).astype(np.uint8)
