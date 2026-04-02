"""Seamless loop and render pipeline tests.

Verifies that all 4 effects produce seamless loops (first/last frame
pixel-close) and that the render pipeline produces valid mp4 files.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.models.params import RenderParams
from app.render.loop_math import (
    build_synthetic_beat_envelope,
    calculate_loop_params,
    frame_phase,
)

# Import effect modules to populate EFFECT_REGISTRY
from app.render.effects import EFFECT_REGISTRY
from app.render.effects import tunnel as _tunnel  # noqa: F401
from app.render.effects import fractal as _fractal  # noqa: F401
from app.render.effects import particles as _particles  # noqa: F401
from app.render.effects import plasma as _plasma  # noqa: F401

EFFECT_NAMES = ["tunnel", "fractal", "particles", "plasma"]
TEST_WIDTH = 480
TEST_HEIGHT = 270
TEST_BPM = 120
TEST_SEED = 42


class TestSeamlessLoop:
    """Pixel diff between first and last frames must be < 15."""

    @pytest.mark.parametrize("effect_name", EFFECT_NAMES)
    def test_seamless(self, effect_name: str) -> None:
        params = RenderParams(
            bpm=TEST_BPM,
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            seed=TEST_SEED,
            effect_name=effect_name,
        )

        effect_cls = EFFECT_REGISTRY[effect_name]
        effect = effect_cls()

        total_frames, loop_duration = calculate_loop_params(params.bpm, params.fps)
        envelope = build_synthetic_beat_envelope(
            total_frames, params.bpm, params.fps, loop_duration
        )

        # Get effect-specific params
        effect_params = getattr(params, effect_name).model_dump()
        effect_params.update({
            "bg_color": params.bg_color,
            "primary_color": params.primary_color,
            "accent_color": params.accent_color,
            "intensity": params.intensity,
            "speed": params.speed,
        })

        rng_first = np.random.default_rng(params.seed)
        first_frame = effect.render_frame(
            frame_phase(0, total_frames),
            params.width,
            params.height,
            effect_params,
            envelope[0],
            rng_first,
        )

        rng_last = np.random.default_rng(params.seed)
        last_frame = effect.render_frame(
            frame_phase(total_frames - 1, total_frames),
            params.width,
            params.height,
            effect_params,
            envelope[total_frames - 1],
            rng_last,
        )

        mean_diff = np.mean(np.abs(first_frame.astype(float) - last_frame.astype(float)))
        assert mean_diff < 15.0, (
            f"{effect_name}: seamless loop failed, mean pixel diff = {mean_diff:.2f} (threshold 15.0)"
        )


class TestRenderPipeline:
    """Test that render_video produces valid mp4 files."""

    def test_render_video_produces_file(self) -> None:
        from app.render.pipeline import render_video

        params = RenderParams(
            bpm=TEST_BPM,
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            seed=TEST_SEED,
            effect_name="tunnel",
        )

        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "test_output.mp4")
            result = render_video(params, output_path)

            assert Path(result).exists(), "render_video did not produce a file"
            assert Path(result).stat().st_size > 0, "render_video produced empty file"

    def test_render_video_progress(self) -> None:
        from app.render.pipeline import render_video

        params = RenderParams(
            bpm=TEST_BPM,
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            seed=TEST_SEED,
            effect_name="plasma",
        )

        progress_values: list[float] = []

        def track_progress(value: float) -> None:
            progress_values.append(value)

        with tempfile.TemporaryDirectory() as tmp:
            output_path = str(Path(tmp) / "test_progress.mp4")
            render_video(params, output_path, progress_callback=track_progress)

            assert len(progress_values) > 0, "No progress updates received"
            assert progress_values[-1] > 0.9, (
                f"Final progress {progress_values[-1]:.2f} not near 1.0"
            )
