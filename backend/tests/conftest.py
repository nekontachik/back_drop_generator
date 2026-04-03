"""Shared pytest fixtures."""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def render_output_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for render output."""
    out = tmp_path / "renders"
    out.mkdir()
    return out


@pytest.fixture
def sine_wave_bytes() -> bytes:
    """Generate a 5-second 440Hz sine wave as WAV bytes for testing.

    Includes amplitude modulation at 2Hz (120 BPM) for beat detection.
    """
    import soundfile as sf

    sr = 22050
    duration = 5.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 120 BPM = 2Hz beat, add amplitude modulation for beat detection
    beat_env = 0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)
    signal = (beat_env * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    # Write WAV format
    buf = io.BytesIO()
    sf.write(buf, signal, sr, format="WAV")
    return buf.getvalue()
