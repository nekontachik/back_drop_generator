"""Integration tests: end-to-end render pipeline verification.

Tests that each genre preset produces a valid mp4 file with correct
properties (resolution, frame count, duration), that beat envelope
aligns with BPM, and that post-processing pipeline works correctly.

Uses tiny resolution (64×48) and short loops for speed.
Full-resolution renders are tested via generate_preset_demos.py.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import numpy as np
import pytest

# Trigger all effect registrations
from app.render.effects import EFFECT_REGISTRY
from app.render.effects import aurora as _a  # noqa: F401
from app.render.effects import fractal as _f  # noqa: F401
from app.render.effects import matrix_rain as _mr  # noqa: F401
from app.render.effects import particles as _p  # noqa: F401
from app.render.effects import plasma as _pl  # noqa: F401
from app.render.effects import retro_grid as _rg  # noqa: F401
from app.render.effects import tunnel as _t  # noqa: F401
from app.render.effects import waveform as _wf  # noqa: F401
from app.render.loop_math import build_synthetic_beat_envelope, calculate_loop_params
from app.render.pipeline import render_video
from app.render.postprocess import (
    PostProcessor,
    apply_bloom,
    apply_chromatic_aberration,
    apply_glitch,
    apply_scanlines,
    apply_vignette,
)
from app.render.presets import PRESETS, get_preset

W, H = 64, 48
SEED = 42


# ===================================================================
# FIXTURES
# ===================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"

AUDIO_FIXTURES = {
    "techno": {"file": "techno_10s.mp3", "expected_bpm_range": (130, 150)},
    "synthwave": {"file": "synthwave_10s.mp3", "expected_bpm_range": (110, 130)},
    "ambient": {"file": "ambient_10s.mp3", "expected_bpm_range": (60, 100)},
    "edm": {"file": "edm_10s.mp3", "expected_bpm_range": (120, 140)},
    "jazz": {"file": "jazz_10s.mp3", "expected_bpm_range": (90, 130)},
    "classical": {"file": "classical_10s.mp3", "expected_bpm_range": (70, 120)},
}


def _ffprobe_duration(path: str) -> float:
    """Get video duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def _ffprobe_resolution(path: str) -> tuple[int, int]:
    """Get video width,height via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    w, h = result.stdout.strip().split(",")
    return int(w), int(h)


# ===================================================================
# 1. POST-PROCESSING UNIT TESTS
# ===================================================================

class TestPostProcessing:
    """Verify each post-processing effect works correctly."""

    @pytest.fixture()
    def sample_frame(self):
        """Generate a simple gradient test frame."""
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        # Horizontal gradient: black to white
        for x in range(W):
            val = int(255 * x / W)
            frame[:, x, :] = val
        return frame

    def test_bloom_brightens_frame(self, sample_frame):
        result = apply_bloom(sample_frame, intensity=0.5, radius=5)
        assert result.dtype == np.uint8
        assert result.shape == sample_frame.shape
        # Bloom should brighten (or at least not darken) bright areas
        bright_region = sample_frame[:, W // 2:, :]
        bright_result = result[:, W // 2:, :]
        assert bright_result.mean() >= bright_region.mean() - 1

    def test_bloom_zero_is_identity(self, sample_frame):
        result = apply_bloom(sample_frame, intensity=0.0)
        np.testing.assert_array_equal(result, sample_frame)

    def test_vignette_darkens_edges(self, sample_frame):
        result = apply_vignette(sample_frame, strength=0.5)
        assert result.dtype == np.uint8
        # Corners should be darker than center
        center = result[H // 2, W // 2].mean()
        corner = result[0, 0].mean()
        assert center >= corner, "Vignette should darken corners"

    def test_vignette_zero_is_identity(self, sample_frame):
        result = apply_vignette(sample_frame, strength=0.0)
        np.testing.assert_array_equal(result, sample_frame)

    def test_scanlines_darken_rows(self, sample_frame):
        result = apply_scanlines(sample_frame, opacity=0.3, spacing=2)
        assert result.dtype == np.uint8
        # Every 2nd row should be darker
        assert result.mean() < sample_frame.mean()

    def test_chromatic_aberration_shifts_channels(self, sample_frame):
        result = apply_chromatic_aberration(sample_frame, offset=3)
        assert result.dtype == np.uint8
        # R and B channels should differ from original (shifted)
        assert not np.array_equal(result[:, :, 0], sample_frame[:, :, 0])
        assert not np.array_equal(result[:, :, 2], sample_frame[:, :, 2])

    def test_glitch_only_on_strong_beat(self, sample_frame):
        rng = np.random.default_rng(42)
        # Weak beat: no change
        result_weak = apply_glitch(sample_frame, 0.3, rng, threshold=0.7)
        np.testing.assert_array_equal(result_weak, sample_frame)

        # Strong beat: should modify frame
        rng2 = np.random.default_rng(42)
        result_strong = apply_glitch(sample_frame, 0.9, rng2, threshold=0.7)
        assert not np.array_equal(result_strong, sample_frame), (
            "Glitch should modify frame on strong beat"
        )

    def test_postprocessor_chain(self, sample_frame):
        """Full chain should not crash and produce valid output."""
        pp = PostProcessor(
            bloom=0.3, vignette=0.4, scanlines=0.1,
            chromatic=2, glitch=True, glitch_threshold=0.5,
        )
        result = pp.process(sample_frame, beat_intensity=0.8,
                            rng=np.random.default_rng(42))
        assert result.shape == sample_frame.shape
        assert result.dtype == np.uint8


# ===================================================================
# 2. FULL PIPELINE: EVERY PRESET RENDERS TO VALID MP4
# ===================================================================

class TestPresetFullRender:
    """Each preset must produce a valid mp4 file."""

    @pytest.mark.parametrize("genre", list(PRESETS.keys()))
    def test_preset_renders_to_mp4(self, genre, tmp_path):
        """Render a complete (tiny) video and verify output file."""
        params = get_preset(genre, bpm=120, width=W, height=H, seed=SEED)
        output = str(tmp_path / f"{genre}.mp4")
        render_video(params, output)

        assert os.path.exists(output), f"Output file not created for {genre}"
        assert os.path.getsize(output) > 1000, f"Output file too small for {genre}"

    @pytest.mark.parametrize("genre", list(PRESETS.keys()))
    def test_preset_output_is_valid_mp4(self, genre, tmp_path):
        """ffprobe should be able to read the output."""
        params = get_preset(genre, bpm=120, width=W, height=H, seed=SEED)
        output = str(tmp_path / f"{genre}.mp4")
        render_video(params, output)

        duration = _ffprobe_duration(output)
        assert duration > 1.0, f"Video too short: {duration}s"
        assert duration < 35.0, f"Video too long: {duration}s"

        w, h = _ffprobe_resolution(output)
        assert w == W, f"Wrong width: {w} != {W}"
        assert h == H, f"Wrong height: {h} != {H}"


# ===================================================================
# 3. GENRE VISUAL IDENTITY: PRESETS USE DISTINCT EFFECTS
# ===================================================================

class TestGenreDistinctness:
    """Verify that genres use different effect combinations."""

    def test_no_two_genres_use_same_effect_combo(self):
        """Each genre should have a unique combination of effects + post-processing."""
        combos: dict[str, list[str]] = {}
        for genre in PRESETS:
            params = get_preset(genre, bpm=120, width=W, height=H, seed=SEED)
            effects = tuple(l.effect_name for l in params.layers)
            pp = params.postprocess
            # Include key post-processing flags in the signature
            sig = f"{effects}|glitch={pp.glitch}|scan={pp.scanlines > 0}|chrom={pp.chromatic > 0}"
            if sig in combos:
                # Allow same combo only if colors are very different
                pass  # Soft check — main goal is the combo list for inspection
            combos[sig] = combos.get(sig, []) + [genre]

        # Every genre must have a unique effect combination
        for sig, genres in combos.items():
            assert len(genres) == 1, (
                f"Genres share the same effect combination: {genres} → {sig}"
            )

    def test_techno_and_synthwave_are_distinct(self):
        """The original problem: techno and synthwave must use different base effects."""
        techno = get_preset("techno", bpm=138, width=W, height=H)
        synthwave = get_preset("synthwave", bpm=118, width=W, height=H)

        techno_effects = {l.effect_name for l in techno.layers}
        synthwave_effects = {l.effect_name for l in synthwave.layers}

        assert techno_effects != synthwave_effects, (
            f"Techno ({techno_effects}) and synthwave ({synthwave_effects}) "
            "should use different effect sets"
        )

    def test_all_effects_are_used(self):
        """Every registered effect should appear in at least one preset."""
        used_effects: set[str] = set()
        for genre in PRESETS:
            params = get_preset(genre, bpm=120, width=W, height=H)
            for layer in params.layers:
                used_effects.add(layer.effect_name)

        registered = set(EFFECT_REGISTRY.keys())
        unused = registered - used_effects
        assert len(unused) == 0, f"Effects not used in any preset: {unused}"


# ===================================================================
# 4. BEAT ENVELOPE ALIGNMENT
# ===================================================================

class TestBeatAlignment:
    """Verify beat envelope peaks align with expected BPM positions."""

    @pytest.mark.parametrize("bpm", [120, 138, 174])
    def test_beat_peaks_match_bpm(self, bpm):
        """Number of strong peaks should roughly match expected beat count."""
        total_frames, loop_duration = calculate_loop_params(bpm)
        envelope = build_synthetic_beat_envelope(total_frames, bpm, 30, loop_duration)

        # Count peaks (frames where envelope > 0.95)
        peaks = np.sum(envelope > 0.95)
        expected_beats = int(loop_duration * bpm / 60)

        # Allow some tolerance (±2 beats)
        assert abs(peaks - expected_beats) <= 2, (
            f"BPM={bpm}: expected ~{expected_beats} peaks, got {peaks}"
        )

    def test_envelope_length_matches_frames(self):
        total_frames, loop_duration = calculate_loop_params(120)
        envelope = build_synthetic_beat_envelope(total_frames, 120, 30, loop_duration)
        assert len(envelope) == total_frames


# ===================================================================
# 5. AUDIO ANALYSIS (requires librosa + audio fixtures)
# ===================================================================

class TestAudioAnalysis:
    """Test BPM detection on real audio clips.

    Skips if librosa or audio fixtures are not available.
    """

    @pytest.fixture(autouse=True)
    def _check_deps(self):
        pytest.importorskip("librosa")
        pytest.importorskip("soundfile")
        if not FIXTURES_DIR.exists():
            pytest.skip("Audio fixtures not found")

    @pytest.mark.parametrize(
        "genre,fixture",
        [(g, f) for g, f in AUDIO_FIXTURES.items()],
        ids=list(AUDIO_FIXTURES.keys()),
    )
    def test_bpm_detection_in_range(self, genre, fixture):
        """Detected BPM should be within expected range for the genre."""
        audio_path = FIXTURES_DIR / fixture["file"]
        if not audio_path.exists():
            pytest.skip(f"Audio fixture {audio_path} not found")

        from app.services.audio_analyzer import AudioAnalyzer

        analyzer = AudioAnalyzer()
        result = analyzer.analyze(str(audio_path))

        bpm = result["bpm"]
        lo, hi = fixture["expected_bpm_range"]

        # BPM detection can return octave multiples — also accept half/double
        valid = (
            lo <= bpm <= hi
            or lo <= bpm / 2 <= hi
            or lo <= bpm * 2 <= hi
        )
        assert valid, (
            f"{genre}: detected BPM={bpm}, expected range [{lo}, {hi}] "
            f"(or half/double)"
        )


# ===================================================================
# 6. RENDER WITH AUDIO BEAT SYNC (end-to-end)
# ===================================================================

class TestRenderWithAudio:
    """End-to-end: analyze audio → render video → verify output."""

    @pytest.fixture(autouse=True)
    def _check_deps(self):
        pytest.importorskip("librosa")
        pytest.importorskip("soundfile")

    def test_techno_audio_to_video(self, tmp_path):
        """Full pipeline: audio analysis → preset → render → valid mp4."""
        audio_path = FIXTURES_DIR / "techno_10s.mp3"
        if not audio_path.exists():
            pytest.skip("Techno audio fixture not found")

        from app.services.audio_analyzer import AudioAnalyzer

        analyzer = AudioAnalyzer()
        result = analyzer.analyze(str(audio_path))
        bpm = result["bpm"]

        params = get_preset("techno", bpm=bpm, width=W, height=H, seed=SEED)
        output = str(tmp_path / "techno_from_audio.mp4")
        render_video(params, output)

        assert os.path.exists(output)
        assert os.path.getsize(output) > 1000
        duration = _ffprobe_duration(output)
        assert 5.0 < duration < 35.0
