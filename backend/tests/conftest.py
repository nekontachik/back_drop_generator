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
    """Generate a 10-second percussive signal as WAV bytes for testing.

    Uses sharp transient clicks at 120 BPM (every 0.5s) mixed with
    broadband noise bursts to give librosa's beat tracker strong onsets.
    """
    import soundfile as sf

    sr = 22050
    duration = 10.0
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Base tone
    signal = 0.1 * np.sin(2 * np.pi * 440.0 * t)

    # Add sharp clicks at 120 BPM (every 0.5 seconds) -- percussive transients
    beat_interval = 0.5  # 120 BPM
    click_duration = 0.02  # 20ms click
    click_samples = int(sr * click_duration)
    for beat_start in np.arange(0, duration, beat_interval):
        idx = int(beat_start * sr)
        end = min(idx + click_samples, n_samples)
        # White noise burst with exponential decay -- strong onset
        noise = np.random.default_rng(42).normal(0, 0.8, end - idx)
        decay = np.exp(-np.linspace(0, 5, end - idx))
        signal[idx:end] += noise * decay

    signal = signal.astype(np.float32)
    # Normalize to prevent clipping
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal = signal / peak * 0.9

    buf = io.BytesIO()
    sf.write(buf, signal, sr, format="WAV")
    return buf.getvalue()


@pytest.fixture
def chroma_collection(tmp_path):
    """Seeded ChromaDB collection in temp directory for testing."""
    from app.services.genre_seeder import init_genre_collection

    return init_genre_collection(str(tmp_path / "chroma"))


@pytest.fixture(autouse=True, scope="session")
def _seed_chroma_for_tests(tmp_path_factory):
    """Seed ChromaDB collection at session start so API tests can query styles.

    Uses autouse + session scope so the collection is available for all tests
    that import the FastAPI app (which registers the styles router).
    Gracefully skips seeding if chromadb is not installed (render/effect
    tests don't need it).
    """
    try:
        from app.services.genre_seeder import init_genre_collection
        from app.services.rag_retriever import set_collection
    except (ImportError, ModuleNotFoundError):
        # chromadb or other RAG deps not installed — render tests don't need it
        return

    chroma_dir = tmp_path_factory.mktemp("chroma_session")
    collection = init_genre_collection(str(chroma_dir))
    set_collection(collection)
