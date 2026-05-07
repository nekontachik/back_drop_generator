"""Matrix digital rain visual effect.

Renders cascading vertical streams of characters/symbols falling
down the screen, like the iconic Matrix code rain. Characters
brighten on beats and fall speed syncs to BPM. Perfect for
dark techno, industrial, cyberpunk aesthetics.
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
class MatrixRainEffect(BaseEffect):
    """Digital rain columns with beat-reactive brightness."""

    @property
    def name(self) -> str:
        return "matrix_rain"

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

        bg = _hex_to_rgb(params.get("bg_color", "#000000"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff41"))
        accent = _hex_to_rgb(params.get("accent_color", "#88ffaa"))

        speed = params.get("speed", 0.5)
        intensity = params.get("intensity", 0.7)
        column_count = params.get("column_count", 60)
        drop_length = params.get("drop_length", 18)

        frame = np.zeros((height, width, 3), dtype=np.float64)
        for c in range(3):
            frame[:, :, c] = bg[c]

        # Seeded column properties
        col_rng = np.random.default_rng(42)
        col_speeds = col_rng.uniform(0.3, 1.0, column_count)
        col_offsets = col_rng.uniform(0, 1.0, column_count)
        col_lengths = col_rng.integers(
            max(5, drop_length // 2), drop_length + 5, column_count
        )
        col_brightness = col_rng.uniform(0.4, 1.0, column_count)

        # Cell size for the "character" grid
        cell_w = max(4, width // column_count)
        cell_h = max(6, int(cell_w * 1.4))
        rows = height // cell_h

        for col_idx in range(column_count):
            col_x = int((col_idx + 0.5) * (width / column_count))
            if col_x >= width:
                continue

            # Drop head position (scrolling down)
            scroll_speed = col_speeds[col_idx] * speed * 2.0
            head_pos = (t * scroll_speed * rows + col_offsets[col_idx] * rows) % (rows + col_lengths[col_idx])
            head_row = int(head_pos)

            length = col_lengths[col_idx]

            for char_idx in range(length):
                row = head_row - char_idx
                if row < 0 or row >= rows:
                    continue

                y = row * cell_h
                x_start = max(0, col_x - cell_w // 2)
                x_end = min(width, col_x + cell_w // 2)

                if y + cell_h > height:
                    continue

                # Brightness: head is brightest, fades toward tail
                fade = 1.0 - (char_idx / length)
                fade = fade ** 1.5  # sharper falloff

                # Beat boost: head chars flash brighter
                beat_boost = beat_intensity * intensity * (1.0 - char_idx / length) * 0.5

                brightness = (fade * col_brightness[col_idx] + beat_boost) * intensity

                # Head character is accent color (white-ish), rest are primary
                if char_idx == 0:
                    color = accent * min(brightness * 1.3, 1.0)
                else:
                    color = primary * brightness

                # Draw a simple block (simulating a character cell)
                # Add some per-cell variation for visual interest
                cell_rng = np.random.default_rng(col_idx * 1000 + row + int(t * 10) % 5)
                cell_pattern = cell_rng.random((cell_h, x_end - x_start))
                # Threshold pattern to create "character" shapes
                char_threshold = 0.35 + 0.2 * fade
                cell_mask = cell_pattern > char_threshold

                for c in range(3):
                    cell_region = frame[y:y + cell_h, x_start:x_end, c]
                    cell_region[cell_mask] = np.maximum(
                        cell_region[cell_mask],
                        color[c],
                    )

        # Subtle scan line effect (built into the rain aesthetic)
        scan_pos = int((t * speed * 3) % 1.0 * height)
        scan_range = 30
        for dy in range(-scan_range, scan_range):
            row = (scan_pos + dy) % height
            scan_alpha = (1.0 - abs(dy) / scan_range) * 0.08 * (0.5 + beat_intensity * 0.5)
            for c in range(3):
                frame[row, :, c] += primary[c] * scan_alpha

        return np.clip(frame, 0, 255).astype(np.uint8)
