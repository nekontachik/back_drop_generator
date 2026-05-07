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
        """Render a tunnel frame at phase t.

        Improved: smoother animation, beat-reactive morphing of ring count
        and twist, thicker ring lines, reduced strobing.
        """
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

        # Beat-reactive morphing: ring count and twist pulse with beat
        # Ring count breathes: expands on beat hit
        ring_morph = ring_count + beat_intensity * intensity * 3.0
        # Twist intensifies on beat
        twist_morph = twist_speed * (1.0 + beat_intensity * 0.5)

        # Coordinate grid: normalized [-1, 1]
        y_coords, x_coords = np.mgrid[-1:1:complex(0, height), -1:1:complex(0, width)]

        # Polar coordinates
        radius = np.sqrt(x_coords**2 + y_coords**2)
        angle = np.arctan2(y_coords, x_coords)

        # Avoid division by zero at center
        radius_safe = np.maximum(radius, 0.001)

        # Depth illusion: 1/radius creates tunnel perspective
        depth = 1.0 / radius_safe

        # Twist: modulate angle over time (smoother — use cos for variety)
        twisted_angle = angle + twist_morph * np.sin(two_pi_t) + 0.3 * np.cos(two_pi_t * 2)

        # Ring pattern: SLOWER movement (reduced from *4.0 to *1.5)
        # Also use smoothstep-like shape for thicker, less harsh rings
        ring_raw = np.sin(ring_morph * depth + two_pi_t * speed * 1.5)
        # Smooth the rings: raise to power for thicker bands
        ring_pattern = np.abs(ring_raw) ** 0.6 * np.sign(ring_raw)

        # Angular pattern: spiral arms (slower, more organic)
        spiral_arms = 4.0  # number of spiral arms
        angular_pattern = np.sin(twisted_angle * spiral_arms + depth * 2.0 + two_pi_t * speed)

        # Combine patterns: ring dominates, angular adds detail
        combined = (ring_pattern * 0.55 + angular_pattern * 0.3 + 1.0) / 2.0
        # Add a secondary slower modulation for visual richness
        slow_pulse = 0.5 + 0.5 * np.sin(two_pi_t * 0.5 + depth * 0.5)
        combined = combined * (0.7 + 0.3 * slow_pulse)

        # Perspective darkening: smooth falloff toward edges
        perspective = np.clip(1.0 - radius * 0.8, 0.0, 1.0)
        # Add depth glow: brighter toward center (tunnel depth)
        center_glow = np.exp(-radius * 2.0) * 0.3

        # Color mixing
        frame = np.zeros((height, width, 3), dtype=np.float64)
        # Beat flash: smooth ramp, not hard threshold
        flash_strength = (beat_intensity ** 1.5) * intensity * 0.5
        for c in range(3):
            base_color = bg[c] + (primary[c] - bg[c]) * combined * perspective
            # Center glow in accent color
            base_color = base_color + accent[c] * center_glow
            # BPM flash: accent color pulses on beat
            frame[:, :, c] = base_color + (accent[c] - base_color) * flash_strength

        return np.clip(frame, 0, 255).astype(np.uint8)
