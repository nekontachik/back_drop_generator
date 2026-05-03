"""Render pipeline orchestrator.

Connects effect selection, frame generation, and ffmpeg encoding into a
single render_video function. Supports both single-effect and multi-layer
compositing modes. Frames are yielded one at a time via a generator --
never accumulated in a list.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from app.models.params import BeatResponse, BlendMode, LayerConfig, RenderParams
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


# ---------------------------------------------------------------------------
# Beat response transforms
# ---------------------------------------------------------------------------

def _smooth_envelope(envelope: np.ndarray, window: int = 5) -> np.ndarray:
    """Low-pass filter the beat envelope for gentle swells."""
    kernel = np.ones(window) / window
    # Pad with wrap for seamless loop continuity
    padded = np.concatenate([envelope[-window:], envelope, envelope[:window]])
    smoothed = np.convolve(padded, kernel, mode="same")
    return smoothed[window:-window]


def _double_envelope(envelope: np.ndarray, bpm: int, fps: int, loop_duration: float, total_frames: int) -> np.ndarray:
    """Build an envelope at 2× the BPM for double-time feel."""
    return build_synthetic_beat_envelope(total_frames, bpm * 2, fps, loop_duration)


def _apply_beat_response(
    raw_envelope: np.ndarray,
    response: BeatResponse,
    bpm: int,
    fps: int,
    loop_duration: float,
    total_frames: int,
) -> np.ndarray:
    """Transform the raw beat envelope according to a BeatResponse mode."""
    if response == BeatResponse.normal:
        return raw_envelope
    if response == BeatResponse.smooth:
        return _smooth_envelope(raw_envelope, window=7)
    if response == BeatResponse.inverse:
        return 1.0 - raw_envelope
    if response == BeatResponse.double:
        return _double_envelope(raw_envelope, bpm, fps, loop_duration, total_frames)
    return raw_envelope  # fallback


# ---------------------------------------------------------------------------
# Layer compositing
# ---------------------------------------------------------------------------

def _blend_layers(bottom: np.ndarray, top: np.ndarray, opacity: float, mode: BlendMode) -> np.ndarray:
    """Blend *top* onto *bottom* using the given mode and opacity.

    Both arrays are float64 [0, 255]. Result is float64 [0, 255].
    """
    if opacity <= 0.0:
        return bottom

    if mode == BlendMode.alpha:
        return bottom * (1.0 - opacity) + top * opacity

    if mode == BlendMode.add:
        return np.minimum(bottom + top * opacity, 255.0)

    if mode == BlendMode.screen:
        # screen: 1 - (1-a)*(1-b), scaled by opacity
        b_n = bottom / 255.0
        t_n = top / 255.0
        screened = 1.0 - (1.0 - b_n) * (1.0 - t_n)
        return bottom * (1.0 - opacity) + screened * 255.0 * opacity

    return bottom * (1.0 - opacity) + top * opacity  # fallback


def _build_layer_params(layer: LayerConfig, parent: RenderParams) -> dict:
    """Build the params dict for a single layer, inheriting from parent."""
    effect_params = getattr(layer, layer.effect_name).model_dump()
    effect_params.update(
        {
            "bg_color": layer.bg_color or parent.bg_color,
            "primary_color": layer.primary_color or parent.primary_color,
            "accent_color": layer.accent_color or parent.accent_color,
            "intensity": layer.intensity if layer.intensity is not None else parent.intensity,
            "speed": layer.speed if layer.speed is not None else parent.speed,
        }
    )
    return effect_params


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_video(
    params: RenderParams,
    output_path: str,
    progress_callback: Callable[[float], None] | None = None,
) -> str:
    """Render a video from parameters to an mp4 file.

    Supports two modes:
    - **Single-effect** (layers is empty): uses effect_name — backward
      compatible with existing code.
    - **Multi-layer compositing** (layers is non-empty): renders each
      layer independently and composites them bottom-to-top.

    Frames are yielded one at a time to avoid memory exhaustion.

    Args:
        params: Full render parameters including effect/layer selection.
        output_path: Destination path for the mp4 file.
        progress_callback: Optional callable receiving progress [0.0, 1.0].

    Returns:
        The output_path string.

    Raises:
        KeyError: If an effect_name is not in EFFECT_REGISTRY.
        RuntimeError: If ffmpeg encoding fails.
    """
    # Calculate loop timing
    total_frames, loop_duration = calculate_loop_params(params.bpm, params.fps)

    # Build raw beat envelope
    raw_envelope = build_synthetic_beat_envelope(
        total_frames, params.bpm, params.fps, loop_duration
    )

    # Create seeded RNG for reproducibility
    rng = np.random.default_rng(params.seed)

    # Decide mode: multi-layer vs single-effect
    use_layers = bool(params.layers)

    if use_layers:
        # -- Multi-layer compositing mode ---------------------------
        # Pre-build per-layer envelopes and effect instances
        layer_configs: list[tuple] = []  # (effect, params_dict, envelope, opacity, blend_mode)
        for layer in params.layers:
            effect_cls = EFFECT_REGISTRY[layer.effect_name]
            effect = effect_cls()
            lp = _build_layer_params(layer, params)
            env = _apply_beat_response(
                raw_envelope, layer.beat_response,
                params.bpm, params.fps, loop_duration, total_frames,
            )
            layer_configs.append((effect, lp, env, layer.opacity, layer.blend_mode))

        def frame_generator():
            for i in range(total_frames):
                t = frame_phase(i, total_frames)
                composite = None
                for effect, lp, env, opacity, blend_mode in layer_configs:
                    frame_rng = np.random.default_rng(rng.integers(0, 2**32))
                    layer_frame = effect.render_frame(
                        t, params.width, params.height, lp, env[i], frame_rng,
                    ).astype(np.float64)

                    if composite is None:
                        # First (bottom) layer — use as base regardless of opacity
                        composite = layer_frame
                    else:
                        composite = _blend_layers(composite, layer_frame, opacity, blend_mode)

                yield np.clip(composite, 0, 255).astype(np.uint8)

    else:
        # -- Single-effect mode (backward compatible) ---------------
        effect_cls = EFFECT_REGISTRY[params.effect_name]
        effect = effect_cls()

        effect_params = getattr(params, params.effect_name).model_dump()
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
            for i in range(total_frames):
                t = frame_phase(i, total_frames)
                frame_rng = np.random.default_rng(rng.integers(0, 2**32))
                frame = effect.render_frame(
                    t, params.width, params.height,
                    effect_params, raw_envelope[i], frame_rng,
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
