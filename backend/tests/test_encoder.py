"""Tests for ffmpeg pipe encoder."""

import subprocess
from pathlib import Path

import numpy as np
import pytest

from app.render.encoder import encode_frames


@pytest.fixture
def synthetic_frames() -> list[np.ndarray]:
    """Generate 10 synthetic 480x270 RGB frames."""
    rng = np.random.default_rng(42)
    return [
        rng.integers(0, 255, (270, 480, 3), dtype=np.uint8)
        for _ in range(10)
    ]


class TestEncodeFrames:
    """Tests for encode_frames."""

    def test_produces_valid_mp4(self, synthetic_frames, tmp_path: Path):
        """encode_frames with 10 synthetic frames produces a valid mp4."""
        output = tmp_path / "test.mp4"
        result = encode_frames(
            frames_iter=iter(synthetic_frames),
            output_path=str(output),
            width=480,
            height=270,
            fps=30,
            total_frames=len(synthetic_frames),
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0

    def test_h264_yuv420p_codec(self, synthetic_frames, tmp_path: Path):
        """ffprobe confirms H.264 codec and yuv420p pixel format."""
        output = tmp_path / "test.mp4"
        encode_frames(
            frames_iter=iter(synthetic_frames),
            output_path=str(output),
            width=480,
            height=270,
            fps=30,
            total_frames=len(synthetic_frames),
        )
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,pix_fmt",
                "-of", "csv=p=0",
                str(output),
            ],
            capture_output=True,
            text=True,
        )
        assert probe.returncode == 0
        probe_output = probe.stdout.strip()
        assert "h264" in probe_output
        assert "yuv420p" in probe_output

    def test_file_size_positive(self, synthetic_frames, tmp_path: Path):
        """Output file size is > 0 bytes."""
        output = tmp_path / "test.mp4"
        encode_frames(
            frames_iter=iter(synthetic_frames),
            output_path=str(output),
            width=480,
            height=270,
            fps=30,
            total_frames=len(synthetic_frames),
        )
        assert output.stat().st_size > 0

    def test_progress_callback(self, synthetic_frames, tmp_path: Path):
        """Progress tracking receives increasing values up to ~1.0."""
        output = tmp_path / "test.mp4"
        progress_values: list[float] = []

        def on_progress(value: float) -> None:
            progress_values.append(value)

        encode_frames(
            frames_iter=iter(synthetic_frames),
            output_path=str(output),
            width=480,
            height=270,
            fps=30,
            total_frames=len(synthetic_frames),
            progress_callback=on_progress,
        )
        assert len(progress_values) == len(synthetic_frames)
        assert progress_values[-1] >= 0.9
        # Values should be non-decreasing
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i - 1]
