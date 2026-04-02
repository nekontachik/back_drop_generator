"""Particle system visual effect (VFX-03).

Renders particles with connections and BPM explosions. Positions are
computed as pure functions of t (no accumulated state). All rendering
is vectorized NumPy.
"""

from __future__ import annotations

import numpy as np

from app.render.effects import register
from app.render.effects.base import BaseEffect


def _hex_to_rgb(hex_color: str) -> np.ndarray:
    """Convert '#RRGGBB' hex string to float RGB array."""
    h = hex_color.lstrip("#")
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.float64)


@register
class ParticleEffect(BaseEffect):
    """Particle system with connections and BPM explosions."""

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

        Particle positions are computed as f(t) using seeded RNG -- no
        accumulated state. The RNG is re-seeded each frame for
        reproducibility.
        """
        two_pi_t = 2.0 * np.pi * t

        # Parse colors
        bg = _hex_to_rgb(params.get("bg_color", "#0a0a0a"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff0066"))

        # Effect parameters
        intensity = params.get("intensity", 0.7)
        speed = params.get("speed", 0.5)
        count = min(params.get("count", 200), 200)  # cap at 200
        connection_dist = params.get("connection_dist", 0.15)

        # Generate fixed base properties from seeded RNG
        # Use a fresh RNG copy so we don't consume the shared state
        particle_rng = np.random.default_rng(rng.integers(0, 2**32))
        base_x = particle_rng.uniform(0.05, 0.95, count)
        base_y = particle_rng.uniform(0.05, 0.95, count)
        phase_per = particle_rng.uniform(0, 2 * np.pi, count)
        freq_per = particle_rng.uniform(0.5, 2.0, count)
        amplitude = particle_rng.uniform(0.02, 0.08, count)

        # Compute positions as f(t) -- pure function, no accumulation
        beat_mult = 1.0 + 2.0 * beat_intensity * intensity
        x_offset = amplitude * np.sin(two_pi_t * speed + phase_per) * beat_mult
        y_offset = amplitude * np.cos(two_pi_t * speed * freq_per) * beat_mult

        px = np.clip(base_x + x_offset, 0.0, 1.0)
        py = np.clip(base_y + y_offset, 0.0, 1.0)

        # Convert to pixel coordinates
        px_pix = (px * (width - 1)).astype(int)
        py_pix = (py * (height - 1)).astype(int)

        # Start with background
        frame = np.full((height, width, 3), bg, dtype=np.float64)

        # Draw connections (vectorized distance matrix)
        # Compute pairwise distances
        dx = px[:, None] - px[None, :]
        dy = py[:, None] - py[None, :]
        dists = np.sqrt(dx**2 + dy**2)

        # Find connected pairs (upper triangle to avoid duplicates)
        i_idx, j_idx = np.where(np.triu(dists < connection_dist, k=1))

        # Draw connection lines using Bresenham-like approach (vectorized)
        for idx in range(min(len(i_idx), 500)):  # cap lines drawn
            x0, y0 = px_pix[i_idx[idx]], py_pix[i_idx[idx]]
            x1, y1 = px_pix[j_idx[idx]], py_pix[j_idx[idx]]

            num_steps = max(abs(x1 - x0), abs(y1 - y0), 1)
            ts = np.linspace(0, 1, num_steps + 1)
            lx = np.clip((x0 + (x1 - x0) * ts).astype(int), 0, width - 1)
            ly = np.clip((y0 + (y1 - y0) * ts).astype(int), 0, height - 1)

            # Fade line based on distance
            dist_val = dists[i_idx[idx], j_idx[idx]]
            alpha = (1.0 - dist_val / connection_dist) * 0.4
            for c in range(3):
                frame[ly, lx, c] = frame[ly, lx, c] * (1 - alpha) + primary[c] * alpha

        # Draw particles as small circles
        radius_px = max(2, int(min(width, height) * 0.005))
        yy, xx = np.mgrid[-radius_px:radius_px + 1, -radius_px:radius_px + 1]
        circle_mask = (xx**2 + yy**2) <= radius_px**2

        # Mix primary and accent based on beat
        particle_color = primary * (1.0 - beat_intensity * intensity) + accent * beat_intensity * intensity

        for p in range(count):
            cx, cy = px_pix[p], py_pix[p]
            # Compute circle pixel positions
            draw_y = cy + yy[circle_mask]
            draw_x = cx + xx[circle_mask]
            # Clip to frame bounds
            valid = (draw_x >= 0) & (draw_x < width) & (draw_y >= 0) & (draw_y < height)
            if valid.any():
                frame[draw_y[valid], draw_x[valid]] = particle_color

        return np.clip(frame, 0, 255).astype(np.uint8)
