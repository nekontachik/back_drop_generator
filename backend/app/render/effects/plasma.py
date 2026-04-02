"""Plasma waves visual effect (VFX-04).

Renders multi-layered slow plasma waves with BPM-reactive distortion.
All rendering is vectorized NumPy.
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
class PlasmaEffect(BaseEffect):
    """Multi-layered plasma waves with BPM distortion."""

    @property
    def name(self) -> str:
        return "plasma"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a plasma frame at phase t."""
        two_pi_t = 2.0 * np.pi * t

        # Parse colors
        bg = _hex_to_rgb(params.get("bg_color", "#0a0a0a"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff0066"))

        # Effect parameters
        speed = params.get("speed", 0.5)
        intensity = params.get("intensity", 0.7)
        layer_count = params.get("layer_count", 4)
        wave_freq = params.get("wave_freq", 3.0)

        # Coordinate grid normalized to [-1, 1]
        y_coords, x_coords = np.mgrid[-1:1:complex(0, height), -1:1:complex(0, width)]

        # Sum multiple sin/cos layers (wave_freq is constant for seamless continuity)
        # Temporal frequency must be integer multiple of 2*pi*t for seamless loops
        # Round speed to nearest integer >= 1 to ensure full cycle completion
        temporal_freq = max(1, round(speed * 2))
        plasma_sum = np.zeros((height, width), dtype=np.float64)
        for i in range(layer_count):
            layer_idx = i + 1
            plasma_sum += np.sin(
                wave_freq * x_coords * layer_idx
                + two_pi_t * temporal_freq
            )
            plasma_sum += np.cos(
                wave_freq * y_coords * layer_idx
                + two_pi_t * temporal_freq
            )

        # Normalize to [0, 1]
        # Each layer contributes 2 terms in [-1, 1], so range is [-2*layer_count, 2*layer_count]
        max_range = 2.0 * layer_count
        normalized = (plasma_sum + max_range) / (2.0 * max_range)
        normalized = np.clip(normalized, 0.0, 1.0)

        # Color: lerp between primary and accent based on plasma value
        # BPM: gentle brightness flash toward accent (moderated for seamless continuity)
        flash_strength = beat_intensity * intensity * 0.25
        frame = np.zeros((height, width, 3), dtype=np.float64)
        for c in range(3):
            # Primary-accent gradient
            color_mix = primary[c] + (accent[c] - primary[c]) * normalized
            # Blend with background at low intensity regions
            low_region = 1.0 - normalized  # inverted: 1 where plasma is low
            base = color_mix * (1.0 - low_region * (1.0 - intensity)) + bg[c] * low_region * (1.0 - intensity)
            # Apply BPM flash
            base = base + (accent[c] - base) * flash_strength
            frame[:, :, c] = base

        return np.clip(frame, 0, 255).astype(np.uint8)
