"""Aurora (Northern Lights) visual effect.

Renders flowing, organic colored bands that undulate vertically —
reminiscent of the aurora borealis. Uses layered sine waves with
varying frequencies and phases to create smooth, flowing curtains
of light. Perfect for ambient, jazz, classical, deep house.
"""

from __future__ import annotations

import numpy as np

from app.render.effects import register
from app.render.effects.base import BaseEffect


def _hex_to_rgb(hex_color: str) -> np.ndarray:
    h = hex_color.lstrip("#")
    if not h:
        return np.array([0.0, 0.0, 0.0], dtype=np.float64)
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.float64)


@register
class AuroraEffect(BaseEffect):
    """Flowing aurora curtains with beat-reactive brightness."""

    @property
    def name(self) -> str:
        return "aurora"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        two_pi_t = 2.0 * np.pi * t

        bg = _hex_to_rgb(params.get("bg_color", "#050510"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#4488ff"))

        speed = params.get("speed", 0.3)
        intensity = params.get("intensity", 0.5)
        band_count = params.get("band_count", 5)
        wave_height = params.get("wave_height", 0.3)

        # Normalized coordinates
        y_norm = np.linspace(0, 1, height)[:, np.newaxis]  # (H, 1)
        x_norm = np.linspace(-1, 1, width)[np.newaxis, :]  # (1, W)

        frame = np.zeros((height, width, 3), dtype=np.float64)
        # Fill background
        for c in range(3):
            frame[:, :, c] = bg[c]

        # Build aurora bands — each band is a horizontal curtain
        # that undulates vertically with sine waves
        aurora = np.zeros((height, width), dtype=np.float64)

        for i in range(band_count):
            band_idx = i + 1
            # Each band has a different base height and wave pattern
            base_y = 0.2 + 0.12 * i  # bands spread vertically
            freq_x = 1.5 + i * 0.7  # horizontal wave frequency
            freq_t = speed * (1.0 + i * 0.3)  # temporal speed variation

            # Curtain shape: sine wave that determines where the band sits
            curtain_y = base_y + wave_height * np.sin(
                freq_x * x_norm * np.pi + two_pi_t * freq_t
            )
            # Beat makes curtains wave more dramatically
            curtain_y += beat_intensity * intensity * 0.08 * np.sin(
                x_norm * np.pi * 3 + two_pi_t * 2
            )

            # Band thickness and falloff
            thickness = 0.06 + beat_intensity * 0.03
            dist_from_curtain = np.abs(y_norm - curtain_y)
            band_value = np.exp(-(dist_from_curtain ** 2) / (2 * thickness ** 2))

            # Horizontal variation (bands aren't uniform brightness)
            horiz_var = 0.5 + 0.5 * np.sin(x_norm * np.pi * (2 + i) + two_pi_t * speed * 0.5)
            band_value *= horiz_var

            aurora += band_value * (0.8 / band_count)

        aurora = np.clip(aurora, 0, 1)

        # Color: gradient from primary at bottom to accent at top
        # with beat shifting the balance
        beat_shift = beat_intensity * intensity * 0.4
        color_gradient = y_norm  # 0 at top, 1 at bottom

        for c in range(3):
            color = (
                primary[c] * (1.0 - color_gradient) * (1.0 - beat_shift)
                + accent[c] * color_gradient * (1.0 + beat_shift * 0.5)
            )
            # Apply aurora mask
            frame[:, :, c] = bg[c] + (color - bg[c]) * aurora

            # Add subtle vertical glow at aurora peaks
            bright_boost = aurora ** 2 * beat_intensity * intensity * 0.3
            frame[:, :, c] += 255 * bright_boost * (primary[c] / 255.0)

        return np.clip(frame, 0, 255).astype(np.uint8)
