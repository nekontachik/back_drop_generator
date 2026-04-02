"""Render pipeline orchestrator.

Connects effect selection, frame generation, and ffmpeg encoding into a
single render_video function. Frames are yielded one at a time via a
generator -- never accumulated in a list.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from app.models.params import RenderParams
from app.render.effects import EFFECT_REGISTRY

# Import effect modules to trigger @register decorators
from app.render.effects import fractal as _fractal  # noqa: F401
from app.render.effects import particles as _particles  # noqa: F401
from app.render.effects import plasma as _plasma  # noqa: F401
from app.render.effects import tunnel as _tunnel  # noqa: F401
from app.render.encoder import encode_frames
from app.render.loop_math import (
    build_synthetic_beat_envelope,
    calculate_loop_params,
    frame_phase,
)


def render_video(
    params: RenderParams,
    output_path: str,
    progress_callback: Callable[[float], None] | None = None,
) -> str:
    """Render a video from parameters to an mp4 file.

    Orchestrates effect lookup, frame generation, and ffmpeg encoding.
    Frames are yielded one at a time to avoid memory exhaustion.

    Args:
        params: Full render parameters including effect selection.
        output_path: Destination path for the mp4 file.
        progress_callback: Optional callable receiving progress [0.0, 1.0].

    Returns:
        The output_path string.

    Raises:
        KeyError: If params.effect_name is not in EFFECT_REGISTRY.
        RuntimeError: If ffmpeg encoding fails.
    """
    # Look up and instantiate effect
    effect_cls = EFFECT_REGISTRY[params.effect_name]
    effect = effect_cls()

    # Calculate loop timing
    total_frames, loop_duration = calculate_loop_params(params.bpm, params.fps)

    # Build beat envelope
    envelope = build_synthetic_beat_envelope(
        total_frames, params.bpm, params.fps, loop_duration
    )

    # Create seeded RNG for reproducibility
    rng = np.random.default_rng(params.seed)

    # Get effect-specific params dict
    effect_params = getattr(params, params.effect_name).model_dump()
    # Merge shared base params
    effect_params.update(
        {
            "bg_color": params.bg_color,
            "primary_color": params.primary_color,
            "accent_color": params.accent_color,
            "intensity": params.intensity,
            "speed": params.speed,
        }
    )

    def frame_generator():
        """Yield one frame at a time -- never accumulate in a list."""
        for i in range(total_frames):
            t = frame_phase(i, total_frames)
            # Create a fresh RNG per frame from the base seed for reproducibility
            frame_rng = np.random.default_rng(rng.integers(0, 2**32))
            frame = effect.render_frame(
                t,
                params.width,
                params.height,
                effect_params,
                envelope[i],
                frame_rng,
            )
            yield frame

    # Encode frames to mp4
    return encode_frames(
        frame_generator(),
        output_path,
        params.width,
        params.height,
        params.fps,
        total_frames,
        progress_callback,
    )
