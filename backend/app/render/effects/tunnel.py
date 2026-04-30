"""Tunnel visual effect (VFX-01).

Creates a 3D tunnel with perspective, concentric rings, twist animation,
and BPM-synced color flashes. All rendering is vectorized NumPy.
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
class TunnelEffect(BaseEffect):
    """3D tunnel with perspective rings and BPM flash."""

    @property
    def name(self) -> str:
        return "tunnel"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a tunnel frame at phase t."""
        two_pi_t = 2.0 * np.pi * t

        # Parse colors
        bg = _hex_to_rgb(params.get("bg_color", "#0a0a0a"))
        primary = _hex_to_rgb(params.get("primary_color", "#00ff88"))
        accent = _hex_to_rgb(params.get("accent_color", "#ff0066"))

        # Effect parameters
        speed = params.get("speed", 0.5)
        intensity = params.get("intensity", 0.7)
        twist_speed = params.get("twist_speed", 1.0)
        ring_count = params.get("ring_count", 8)

        # Coordinate grid: normalized [-1, 1]
        y_coords, x_coords = np.mgrid[-1:1:complex(0, height), -1:1:complex(0, width)]

        # Polar coordinates
        radius = np.sqrt(x_coords**2 + y_coords**2)
        angle = np.arctan2(y_coords, x_coords)

        # Avoid division by zero at center
        radius_safe = np.maximum(radius, 0.001)

        # Depth illusion: 1/radius creates tunnel perspective
        depth = 1.0 / radius_safe

        # Twist: modulate angle over time
        twisted_angle = angle + twist_speed * np.sin(two_pi_t)

        # Ring pattern: concentric rings moving through tunnel
        ring_pattern = np.sin(ring_count * depth + two_pi_t * speed * 4.0)

        # Angular pattern for visual complexity
        angular_pattern = np.sin(twisted_angle * 3.0 + two_pi_t * speed * 2.0)

        # Combine patterns: normalized to [0, 1]
        combined = (ring_pattern * 0.6 + angular_pattern * 0.4 + 1.0) / 2.0

        # Perspective darkening: fade toward edges
        perspective = np.clip(1.0 - radius, 0.0, 1.0)

        # Color mixing: primary drives the base look, accent only flashes on beat peaks
        frame = np.zeros((height, width, 3), dtype=np.float64)
        # Sharpen beat: only flash above a threshold, then remap to 0..1
        flash_raw = np.clip((beat_intensity - 0.5) * 2.0, 0.0, 1.0)
        flash_strength = flash_raw * flash_raw * intensity * 0.6
        for c in range(3):
            base_color = bg[c] + (primary[c] - bg[c]) * combined * perspective
            # BPM flash: accent only appears on strong beats, not constantly
            frame[:, :, c] = base_color + (accent[c] - base_color) * flash_strength

        return np.clip(frame, 0, 255).astype(np.uint8)
