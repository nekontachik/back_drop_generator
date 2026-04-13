"""Fractal (Julia set) visual effect (VFX-02).

Renders a Julia set with cyclic morphing of the c parameter and zoom.
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
class FractalEffect(BaseEffect):
    """Julia set fractal with cyclic morphing and zoom."""

    @property
    def name(self) -> str:
        return "fractal"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a Julia set frame at phase t."""
        two_pi_t = 2.0 * np.pi * t

        # Parse colors
        bg = _hex_to_rgb(params.get("bg_color", "#0a0a0a"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff0066"))

        # Effect parameters
        intensity = params.get("intensity", 0.7)
        speed = params.get("speed", 0.5)
        zoom_rate = params.get("zoom_rate", 1.0)
        c_param = params.get("c_param", complex(-0.7, 0.27015))
        if isinstance(c_param, dict):
            c_param = complex(c_param.get("real", -0.7), c_param.get("imag", 0.27015))

        max_iter = 64

        # Cyclic zoom
        zoom = 1.0 + zoom_rate * 0.5 * np.sin(two_pi_t * speed)

        # Complex plane grid
        aspect = width / height
        re = np.linspace(-aspect / zoom, aspect / zoom, width)
        im = np.linspace(-1.0 / zoom, 1.0 / zoom, height)
        re_grid, im_grid = np.meshgrid(re, im)
        z = re_grid + 1j * im_grid

        # Morphing c parameter: cyclic variation
        c_real = c_param.real + 0.1 * np.sin(two_pi_t * speed)
        c_imag = c_param.imag + 0.1 * np.cos(two_pi_t * speed)
        c = complex(c_real, c_imag)

        # Julia set iteration (vectorized)
        escape_count = np.zeros((height, width), dtype=np.float64)
        mask = np.ones((height, width), dtype=bool)

        for i in range(max_iter):
            z[mask] = z[mask] ** 2 + c
            escaped = mask & (np.abs(z) > 2.0)
            # Smooth escape count
            escape_count[escaped] = i + 1 - np.log2(np.log2(np.abs(z[escaped]) + 1e-10))
            mask[escaped] = False
            if not mask.any():
                break

        # Normalize escape count to [0, 1]
        max_count = max(np.max(escape_count), 1.0)
        normalized = escape_count / max_count

        # Color: lerp between bg and primary based on escape
        frame = np.zeros((height, width, 3), dtype=np.float64)
        flash_strength = beat_intensity * intensity * 0.3  # moderate flash for seamless continuity
        for ch in range(3):
            base_color = bg[ch] + (primary[ch] - bg[ch]) * normalized
            # BPM flash: boost brightness toward accent
            flash = base_color + (accent[ch] - base_color) * flash_strength
            frame[:, :, ch] = flash

        return np.clip(frame, 0, 255).astype(np.uint8)
