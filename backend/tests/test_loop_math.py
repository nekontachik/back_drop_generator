"""Tests for BPM-aligned loop math utilities."""

import numpy as np

from app.render.loop_math import (
    build_synthetic_beat_envelope,
    calculate_loop_params,
    frame_phase,
)


class TestCalculateLoopParams:
    """Tests for calculate_loop_params."""

    def test_120bpm_8bars(self):
        """120 BPM, 8 bars = 16 seconds, 16*30 = 480 frames."""
        total_frames, duration = calculate_loop_params(bpm=120, fps=30, target_bars=8)
        assert total_frames == 480
        assert duration == pytest.approx(16.0)

    def test_60bpm_clamps_to_max_30s(self):
        """60 BPM with 8 bars = 32s, should clamp down to <= 30s."""
        total_frames, duration = calculate_loop_params(bpm=60, fps=30)
        assert duration <= 30.0
        assert duration >= 8.0
        assert total_frames == round(duration * 30)

    def test_200bpm_at_least_8s(self):
        """200 BPM should produce at least 8 seconds."""
        total_frames, duration = calculate_loop_params(bpm=200, fps=30)
        assert duration >= 8.0
        assert total_frames == round(duration * 30)

    def test_returns_positive_frames(self):
        """All valid BPMs produce positive frame counts."""
        for bpm in [60, 90, 120, 150, 200]:
            total_frames, duration = calculate_loop_params(bpm=bpm, fps=30)
            assert total_frames > 0
            assert duration > 0


class TestFramePhase:
    """Tests for frame_phase."""

    def test_first_frame_is_zero(self):
        """frame_phase(0, N) == 0.0."""
        assert frame_phase(0, 480) == 0.0

    def test_last_frame_less_than_one(self):
        """frame_phase(N-1, N) < 1.0 for seamless loop."""
        assert frame_phase(479, 480) < 1.0

    def test_midpoint(self):
        """frame_phase at midpoint is 0.5."""
        assert frame_phase(240, 480) == pytest.approx(0.5)


class TestBuildSyntheticBeatEnvelope:
    """Tests for build_synthetic_beat_envelope."""

    def test_correct_length(self):
        """Envelope length matches total_frames."""
        total_frames, duration = calculate_loop_params(bpm=120, fps=30)
        envelope = build_synthetic_beat_envelope(total_frames, bpm=120, fps=30, loop_duration=duration)
        assert len(envelope) == total_frames

    def test_max_value_is_one(self):
        """Envelope peak is 1.0."""
        total_frames, duration = calculate_loop_params(bpm=120, fps=30)
        envelope = build_synthetic_beat_envelope(total_frames, bpm=120, fps=30, loop_duration=duration)
        assert np.max(envelope) == pytest.approx(1.0)

    def test_values_non_negative(self):
        """All envelope values >= 0."""
        total_frames, duration = calculate_loop_params(bpm=120, fps=30)
        envelope = build_synthetic_beat_envelope(total_frames, bpm=120, fps=30, loop_duration=duration)
        assert np.all(envelope >= 0.0)

    def test_returns_ndarray(self):
        """Return type is numpy ndarray."""
        total_frames, duration = calculate_loop_params(bpm=120, fps=30)
        envelope = build_synthetic_beat_envelope(total_frames, bpm=120, fps=30, loop_duration=duration)
        assert isinstance(envelope, np.ndarray)


import pytest
