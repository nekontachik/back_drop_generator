"""Waveform / spectrum visualizer effect.

Renders vertical bars that react to beat intensity — like an audio
spectrum analyzer or equalizer display. Bars pulse up on beats and
decay smoothly. Great for EDM, drum & bass, house, and any
high-energy genres.
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
class WaveformEffect(BaseEffect):
    """Audio spectrum bars with beat-reactive heights."""

    @property
    def name(self) -> str:
        return "waveform"

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

        bg = _hex_to_rgb(params.get("bg_color", "#0a0a14"))
        primary = _hex_to_rgb(params.get("primary_color", "#00aaff"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff00aa"))

        speed = params.get("speed", 0.5)
        intensity = params.get("intensity", 0.7)
        bar_count = params.get("bar_count", 48)
        mirror = params.get("mirror", True)
        style = params.get("style", "pointed")  # "pointed" or "flat"

        frame = np.zeros((height, width, 3), dtype=np.float64)
        for c in range(3):
            frame[:, :, c] = bg[c]

        # Generate per-bar "frequency" heights using seeded sine patterns
        bar_rng = np.random.default_rng(42)
        bar_phases = bar_rng.uniform(0, 2 * np.pi, bar_count)
        bar_freqs = bar_rng.uniform(0.5, 2.0, bar_count)
        bar_base_heights = bar_rng.uniform(0.15, 0.4, bar_count)

        # Bar geometry
        total_bar_width = width * 0.85
        bar_spacing = total_bar_width / bar_count
        bar_width_px = max(2, int(bar_spacing * 0.7))
        start_x = int((width - total_bar_width) / 2)

        # Center Y for mirrored mode
        center_y = height // 2 if mirror else height

        for i in range(bar_count):
            # Animated height: base oscillation + beat pulse
            base_h = bar_base_heights[i] * (
                0.3 + 0.7 * (0.5 + 0.5 * np.sin(two_pi_t * speed * bar_freqs[i] + bar_phases[i]))
            )
            # Beat makes bars jump
            beat_boost = beat_intensity * intensity * 0.6
            # Different bars respond to beat at different phases
            # (simulates frequency bands)
            bar_beat_phase = i / bar_count * np.pi * 2
            local_beat = beat_intensity * (0.5 + 0.5 * np.sin(bar_beat_phase + two_pi_t * 4))
            beat_boost = local_beat * intensity * 0.5

            total_h = np.clip(base_h + beat_boost, 0.05, 0.9)

            # Pixel coordinates
            bar_x_start = start_x + int(i * bar_spacing)
            bar_x_end = min(bar_x_start + bar_width_px, width)

            if mirror:
                # Mirror from center
                bar_height_px = int(total_h * height * 0.45)
                y_top = max(0, center_y - bar_height_px)
                y_bottom = min(height, center_y + bar_height_px)
            else:
                bar_height_px = int(total_h * height * 0.8)
                y_top = height - bar_height_px
                y_bottom = height

            if bar_x_start >= width or y_top >= y_bottom:
                continue

            # Color gradient along bar height (primary at base, accent at tip)
            bar_h = y_bottom - y_top
            if bar_h <= 0:
                continue

            y_indices = np.arange(y_top, y_bottom)
            if mirror:
                # Distance from center normalized
                grad = np.abs(y_indices - center_y).astype(np.float64) / max(bar_height_px, 1)
            else:
                grad = (y_bottom - y_indices).astype(np.float64) / max(bar_h, 1)

            grad = np.clip(grad, 0, 1)

            # Pointed tip: fade out at the edges
            if style == "pointed":
                tip_fade = np.clip(1.0 - (grad - 0.7) * 3.33, 0.3, 1.0)
            else:
                tip_fade = np.ones_like(grad)

            for c in range(3):
                color = primary[c] * (1.0 - grad) + accent[c] * grad
                color *= tip_fade
                # Beat brightens the whole bar
                color *= (0.7 + 0.3 * beat_intensity)
                frame[y_top:y_bottom, bar_x_start:bar_x_end, c] = np.maximum(
                    frame[y_top:y_bottom, bar_x_start:bar_x_end, c],
                    color[:, np.newaxis],
                )

            # Glow at bar edges (subtle)
            glow_width = max(1, bar_width_px // 3)
            glow_x_start = max(0, bar_x_start - glow_width)
            glow_x_end = min(width, bar_x_end + glow_width)
            glow_alpha = 0.15 * beat_intensity
            for c in range(3):
                glow_color = (primary[c] + accent[c]) * 0.5 * glow_alpha
                frame[y_top:y_bottom, glow_x_start:bar_x_start, c] += glow_color * 0.5
                frame[y_top:y_bottom, bar_x_end:glow_x_end, c] += glow_color * 0.5

        # Horizontal center line for mirrored mode
        if mirror:
            line_alpha = 0.2 + 0.3 * beat_intensity
            for c in range(3):
                frame[center_y - 1:center_y + 1, :, c] = (
                    frame[center_y - 1:center_y + 1, :, c] * (1 - line_alpha)
                    + primary[c] * line_alpha
                )

        return np.clip(frame, 0, 255).astype(np.uint8)
