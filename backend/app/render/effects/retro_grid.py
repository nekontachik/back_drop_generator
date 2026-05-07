"""Retro grid (Outrun/Synthwave) visual effect.

Renders a perspective-correct grid floor rushing toward the viewer,
with a glowing horizon sun and optional star field. The iconic
synthwave/outrun/vaporwave aesthetic.
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
class RetroGridEffect(BaseEffect):
    """Perspective grid floor with horizon sun — synthwave aesthetic."""

    @property
    def name(self) -> str:
        return "retro_grid"

    def render_frame(
        self,
        t: float,
        width: int,
        height: int,
        params: dict,
        beat_intensity: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Render a retro grid frame at phase t."""
        two_pi_t = 2.0 * np.pi * t

        # Parse colors
        bg = _hex_to_rgb(params.get("bg_color", "#0a001e"))
        primary = _hex_to_rgb(params.get("primary_color", "#ff2299"))
        accent = _hex_to_rgb(params.get("accent_color", "#00ffee"))

        # Parameters
        speed = params.get("speed", 0.5)
        intensity = params.get("intensity", 0.7)
        grid_density = params.get("grid_density", 12)
        sun_size = params.get("sun_size", 0.18)
        horizon_pos = params.get("horizon_pos", 0.4)  # 0=top, 1=bottom

        # Create frame
        frame = np.zeros((height, width, 3), dtype=np.float64)

        # Coordinate grids
        horizon_y = int(height * horizon_pos)

        # ---- SKY (gradient from dark to primary near horizon) ----
        sky_grad = np.linspace(0, 1, horizon_y)[:, np.newaxis]
        for c in range(3):
            frame[:horizon_y, :, c] = bg[c] * (1.0 - sky_grad * 0.5) + primary[c] * sky_grad * 0.15

        # ---- SUN (semicircle at horizon) ----
        sun_center_x = width // 2
        sun_center_y = horizon_y
        sun_radius_px = int(min(width, height) * sun_size)

        # Sun glow expands on beat
        beat_expand = 1.0 + beat_intensity * intensity * 0.3
        effective_radius = sun_radius_px * beat_expand

        # Draw sun with horizontal stripe cutouts (retro sun style)
        yy_sun = np.arange(max(0, sun_center_y - sun_radius_px), sun_center_y)
        xx_sun = np.arange(0, width)
        if len(yy_sun) > 0:
            yy_g, xx_g = np.meshgrid(yy_sun, xx_sun, indexing="ij")
            dist = np.sqrt((xx_g - sun_center_x) ** 2 + (yy_g - sun_center_y) ** 2)
            sun_mask = dist < effective_radius

            # Horizontal stripe gaps (retro sun look)
            stripe_period = max(4, sun_radius_px // 6)
            stripe_mask = ((sun_center_y - yy_g) % stripe_period) > (stripe_period // 3)
            # Only apply stripes to bottom half of sun
            bottom_half = yy_g > (sun_center_y - sun_radius_px * 0.5)
            stripe_mask = stripe_mask | ~bottom_half
            sun_mask = sun_mask & stripe_mask

            # Sun color: gradient from accent (top) to primary (bottom)
            sun_gradient = (sun_center_y - yy_g).astype(np.float64) / max(sun_radius_px, 1)
            sun_gradient = np.clip(sun_gradient, 0, 1)

            for c in range(3):
                sun_color = accent[c] * sun_gradient + primary[c] * (1.0 - sun_gradient)
                frame[yy_g[sun_mask], xx_g[sun_mask], c] = sun_color[sun_mask]

            # Sun glow (soft bloom around sun)
            glow_mask = (dist < effective_radius * 1.8) & ~sun_mask
            glow_strength = 1.0 - dist[glow_mask] / (effective_radius * 1.8)
            glow_strength = glow_strength ** 2 * 0.4
            for c in range(3):
                glow_color = (accent[c] + primary[c]) * 0.5
                frame[yy_g[glow_mask], xx_g[glow_mask], c] += glow_color * glow_strength

        # ---- GRID FLOOR (perspective projection) ----
        # The grid occupies bottom portion (below horizon)
        floor_height = height - horizon_y
        if floor_height > 0:
            # Normalized floor coordinates
            floor_y = np.arange(horizon_y, height)
            floor_x = np.arange(0, width)
            fy, fx = np.meshgrid(floor_y, floor_x, indexing="ij")

            # Perspective depth: closer to horizon = further away
            # Map floor_y from horizon (far) to bottom (near)
            depth = (fy - horizon_y).astype(np.float64) / floor_height
            depth = np.clip(depth, 0.001, 1.0)

            # Perspective-correct world coordinates
            world_z = 1.0 / depth  # z goes from 1 (near) to inf (far)
            world_x = (fx - width / 2) / (width / 2) * world_z

            # Scrolling: grid moves toward viewer over time
            scroll = t * speed * grid_density * 4.0
            world_z_scrolled = world_z + scroll

            # Grid lines: use fract of world coordinates
            # Horizontal lines (z-axis)
            z_frac = np.mod(world_z_scrolled, 1.0)
            z_line = np.exp(-((z_frac - 0.5) ** 2) / 0.003)  # Gaussian line shape

            # Vertical lines (x-axis)
            x_spacing = grid_density * 0.3
            x_frac = np.mod(world_x * x_spacing, 1.0)
            x_line = np.exp(-((x_frac - 0.5) ** 2) / 0.003)

            # Combine: any grid line visible
            grid_value = np.maximum(z_line, x_line)

            # Fade with distance (far lines are dimmer)
            distance_fade = np.clip(1.0 - (1.0 / world_z) * 0.3, 0.1, 1.0)
            # Also fade very close lines slightly
            near_fade = np.clip(depth * 3, 0, 1)
            grid_value = grid_value * distance_fade * near_fade

            # Beat pulse: grid brightens on beat
            grid_brightness = 0.6 + beat_intensity * intensity * 0.4

            # Grid color (primary with accent highlights on beat)
            grid_color = primary * (1.0 - beat_intensity * 0.4) + accent * (beat_intensity * 0.4)

            # Apply grid to floor area
            for c in range(3):
                # Dark floor base
                floor_base = bg[c] * 0.3
                # Grid line contribution
                frame[horizon_y:, :, c] = floor_base + grid_color[c] * grid_value * grid_brightness

            # Horizon glow line
            glow_rows = min(8, floor_height)
            glow_fade = np.exp(-np.arange(glow_rows).astype(np.float64) * 0.5)
            for r in range(glow_rows):
                row_idx = horizon_y + r
                if row_idx < height:
                    glow_strength_r = glow_fade[r] * 0.5 * (0.7 + beat_intensity * 0.3)
                    for c in range(3):
                        frame[row_idx, :, c] = np.maximum(
                            frame[row_idx, :, c],
                            primary[c] * glow_strength_r,
                        )

        return np.clip(frame, 0, 255).astype(np.uint8)
