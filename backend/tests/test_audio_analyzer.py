"""Tests for audio analysis service (AUD-01 through AUD-04)."""

from __future__ import annotations

import pytest

from app.models.audio import AudioAnalysis, BpmResult, BpmVisualization, MoodVector
from app.services.audio_analyzer import analyze_audio, classify_mood, validate_audio


class TestAnalyzeAudio:
    """Tests for analyze_audio() function."""

    def test_returns_audio_analysis(self, sine_wave_bytes: bytes) -> None:
        """analyze_audio returns an AudioAnalysis instance."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result, AudioAnalysis)

    def test_bpm_detected_in_range(self, sine_wave_bytes: bytes) -> None:
        """BPM detected is an int between 60 and 200."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.bpm.detected, int)
        assert 60 <= result.bpm.detected <= 200

    def test_bpm_half_and_double(self, sine_wave_bytes: bytes) -> None:
        """bpm.half == bpm.detected // 2 and bpm.double == bpm.detected * 2."""
        result = analyze_audio(sine_wave_bytes)
        assert result.bpm.half == result.bpm.detected // 2
        assert result.bpm.double == result.bpm.detected * 2

    def test_beat_times_non_empty(self, sine_wave_bytes: bytes) -> None:
        """beat_times is a non-empty list of floats."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.beat_times, list)
        assert len(result.beat_times) > 0
        assert all(isinstance(t, float) for t in result.beat_times)

    def test_mood_spectral_centroid(self, sine_wave_bytes: bytes) -> None:
        """Mood has spectral_centroid as float."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.mood.spectral_centroid, float)

    def test_mood_chroma(self, sine_wave_bytes: bytes) -> None:
        """Mood has chroma as list of 12 floats."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.mood.chroma, list)
        assert len(result.mood.chroma) == 12
        assert all(isinstance(c, float) for c in result.mood.chroma)

    def test_mood_rms(self, sine_wave_bytes: bytes) -> None:
        """Mood has rms as float."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.mood.rms, float)

    def test_mood_onset_strength(self, sine_wave_bytes: bytes) -> None:
        """Mood has onset_strength as float."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.mood.onset_strength, float)

    def test_mood_labels_valid(self, sine_wave_bytes: bytes) -> None:
        """Mood labels are from the valid label set."""
        result = analyze_audio(sine_wave_bytes)
        valid_labels = {"bright", "dark", "energetic", "mellow", "dense", "sparse"}
        assert isinstance(result.mood.labels, list)
        assert all(label in valid_labels for label in result.mood.labels)

    def test_visualization_onset_times_and_values(self, sine_wave_bytes: bytes) -> None:
        """Visualization has onset_times and onset_values of equal length."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.visualization.onset_times, list)
        assert isinstance(result.visualization.onset_values, list)
        assert len(result.visualization.onset_times) == len(result.visualization.onset_values)

    def test_visualization_beat_times(self, sine_wave_bytes: bytes) -> None:
        """Visualization has beat_times as a non-empty list of floats."""
        result = analyze_audio(sine_wave_bytes)
        assert isinstance(result.visualization.beat_times, list)
        assert len(result.visualization.beat_times) > 0


class TestValidateAudio:
    """Tests for validate_audio() function."""

    def test_rejects_oversized_file(self) -> None:
        """Raises ValueError for files over 10MB."""
        big_bytes = b"\x00" * (10 * 1024 * 1024 + 1)
        with pytest.raises(ValueError, match="10MB"):
            validate_audio(big_bytes, "test.wav")

    def test_rejects_non_audio_extension(self) -> None:
        """Raises ValueError for non-audio file extensions."""
        with pytest.raises(ValueError, match="audio"):
            validate_audio(b"data", "test.txt")

    def test_accepts_mp3(self) -> None:
        """Does not raise for .mp3 files."""
        validate_audio(b"data", "song.mp3")

    def test_accepts_wav(self) -> None:
        """Does not raise for .wav files."""
        validate_audio(b"data", "song.wav")

    def test_accepts_ogg(self) -> None:
        """Does not raise for .ogg files."""
        validate_audio(b"data", "song.ogg")

    def test_accepts_m4a(self) -> None:
        """Does not raise for .m4a files."""
        validate_audio(b"data", "song.m4a")


class TestClassifyMood:
    """Tests for classify_mood() function."""

    def test_bright_energetic_dense(self) -> None:
        """High centroid + high RMS + high onset -> bright, energetic, dense."""
        labels = classify_mood(centroid=3000, rms=0.2, onset=3.0)
        assert labels == ["bright", "energetic", "dense"]

    def test_dark_mellow_sparse(self) -> None:
        """Low centroid + low RMS + low onset -> dark, mellow, sparse."""
        labels = classify_mood(centroid=1500, rms=0.05, onset=1.0)
        assert labels == ["dark", "mellow", "sparse"]
