"""Post-processing pipeline for rendered frames.

Adds cinematic quality to raw effect output: bloom (glow), vignette
(edge darkening), scanlines (retro CRT), and chromatic aberration.
All operations are vectorized NumPy/OpenCV for performance.
"""

from __future__ import annotations

import cv2
import numpy as np


def apply_bloom(frame: np.ndarray, intensity: float = 0.3, radius: int = 21) -> np.ndarray:
    """Add bloom/glow effect — bright areas bleed light outward.

    Args:
        frame: RGB uint8 frame (H, W, 3).
        intensity: Blend strength of the bloom [0.0, 1.0].
        radius: Gaussian blur kernel size (must be odd).

    Returns:
        Frame with bloom applied (uint8).
    """
    if intensity <= 0:
        return frame

    # Ensure odd kernel
    radius = radius | 1

    # Threshold: only bloom bright pixels
    f = frame.astype(np.float32)
    # Extract bright regions (above ~40% brightness)
    brightness = np.max(f, axis=2)
    mask = (brightness > 100).astype(np.float32)[:, :, np.newaxis]
    bright = f * mask

    # Blur the bright regions
    blurred = cv2.GaussianBlur(bright, (radius, radius), 0)

    # Additive blend
    result = f + blurred * intensity
    return np.clip(result, 0, 255).astype(np.uint8)


def apply_vignette(frame: np.ndarray, strength: float = 0.4) -> np.ndarray:
    """Darken frame edges for cinematic depth.

    Args:
        frame: RGB uint8 frame (H, W, 3).
        strength: How dark the edges get [0.0, 1.0].

    Returns:
        Frame with vignette (uint8).
    """
    if strength <= 0:
        return frame

    h, w = frame.shape[:2]
    # Create radial gradient
    y = np.linspace(-1, 1, h)
    x = np.linspace(-1, 1, w)
    xx, yy = np.meshgrid(x, y)
    radius = np.sqrt(xx**2 + yy**2)

    # Smooth falloff from center (1.0) to edges (dark)
    vignette = 1.0 - np.clip(radius - 0.5, 0, 1) * strength * 2
    vignette = np.clip(vignette, 1.0 - strength, 1.0)
    vignette = vignette[:, :, np.newaxis]

    return (frame.astype(np.float32) * vignette).astype(np.uint8)


def apply_scanlines(frame: np.ndarray, opacity: float = 0.15, spacing: int = 3) -> np.ndarray:
    """Add horizontal CRT scanline overlay.

    Args:
        frame: RGB uint8 frame (H, W, 3).
        opacity: How visible the scanlines are [0.0, 1.0].
        spacing: Pixel spacing between scanlines.

    Returns:
        Frame with scanlines (uint8).
    """
    if opacity <= 0:
        return frame

    h, w = frame.shape[:2]
    # Create scanline mask: darken every Nth row
    mask = np.ones((h, 1, 1), dtype=np.float32)
    mask[::spacing] = 1.0 - opacity

    return (frame.astype(np.float32) * mask).astype(np.uint8)


def apply_chromatic_aberration(frame: np.ndarray, offset: int = 2) -> np.ndarray:
    """Shift color channels slightly for RGB split effect.

    Args:
        frame: RGB uint8 frame (H, W, 3).
        offset: Pixel offset for R and B channels.

    Returns:
        Frame with chromatic aberration (uint8).
    """
    if offset <= 0:
        return frame

    result = frame.copy()
    h, w = frame.shape[:2]

    # Shift red channel right, blue channel left
    result[:, offset:, 0] = frame[:, :-offset, 0]  # R shifts right
    result[:, :-offset, 2] = frame[:, offset:, 2]  # B shifts left

    return result


def apply_glitch(
    frame: np.ndarray,
    beat_intensity: float,
    rng: np.random.Generator,
    threshold: float = 0.7,
    max_slices: int = 8,
    max_offset: int = 30,
) -> np.ndarray:
    """Beat-reactive horizontal glitch slices.

    Only triggers on strong beats (above threshold). Displaces horizontal
    bands of pixels left/right for a digital glitch aesthetic.

    Args:
        frame: RGB uint8 frame (H, W, 3).
        beat_intensity: Current beat value [0.0, 1.0].
        rng: Random generator for reproducible glitch positions.
        threshold: Beat intensity threshold to trigger glitch.
        max_slices: Maximum number of displaced bands.
        max_offset: Maximum horizontal pixel displacement.

    Returns:
        Glitched frame (uint8).
    """
    if beat_intensity < threshold:
        return frame

    h, w = frame.shape[:2]
    result = frame.copy()

    # Glitch strength scales with how far above threshold we are
    strength = (beat_intensity - threshold) / (1.0 - threshold)
    num_slices = max(1, int(max_slices * strength))
    offset_range = int(max_offset * strength)

    for _ in range(num_slices):
        # Random horizontal band
        y_start = rng.integers(0, h - 10)
        band_height = rng.integers(3, max(4, int(h * 0.05)))
        y_end = min(y_start + band_height, h)

        # Random horizontal offset
        offset = rng.integers(-offset_range, offset_range + 1)
        if offset == 0:
            continue

        band = frame[y_start:y_end].copy()
        if offset > 0:
            result[y_start:y_end, offset:] = band[:, :-offset]
            result[y_start:y_end, :offset] = band[:, -offset:]
        else:
            abs_off = abs(offset)
            result[y_start:y_end, :-abs_off] = band[:, abs_off:]
            result[y_start:y_end, -abs_off:] = band[:, :abs_off]

    return result


class PostProcessor:
    """Configurable post-processing chain for rendered frames.

    Usage:
        pp = PostProcessor(bloom=0.3, vignette=0.4, scanlines=0.15)
        processed = pp.process(raw_frame, beat_intensity, rng)
    """

    def __init__(
        self,
        bloom: float = 0.0,
        bloom_radius: int = 21,
        vignette: float = 0.0,
        scanlines: float = 0.0,
        scanline_spacing: int = 3,
        chromatic: int = 0,
        glitch: bool = False,
        glitch_threshold: float = 0.7,
    ):
        self.bloom = bloom
        self.bloom_radius = bloom_radius
        self.vignette = vignette
        self.scanlines = scanlines
        self.scanline_spacing = scanline_spacing
        self.chromatic = chromatic
        self.glitch = glitch
        self.glitch_threshold = glitch_threshold

    def process(
        self,
        frame: np.ndarray,
        beat_intensity: float = 0.0,
        rng: np.random.Generator | None = None,
    ) -> np.ndarray:
        """Apply all configured post-processing effects in order."""
        # Bloom first (works on raw bright pixels)
        if self.bloom > 0:
            frame = apply_bloom(frame, self.bloom, self.bloom_radius)

        # Glitch (beat-reactive, before vignette)
        if self.glitch and rng is not None:
            frame = apply_glitch(frame, beat_intensity, rng, self.glitch_threshold)

        # Chromatic aberration
        if self.chromatic > 0:
            frame = apply_chromatic_aberration(frame, self.chromatic)

        # Vignette (after everything else that adds light)
        if self.vignette > 0:
            frame = apply_vignette(frame, self.vignette)

        # Scanlines last (top overlay)
        if self.scanlines > 0:
            frame = apply_scanlines(frame, self.scanlines, self.scanline_spacing)

        return frame
