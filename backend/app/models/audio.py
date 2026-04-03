"""Pydantic schemas for audio analysis results (AUD-01 through AUD-04)."""

from __future__ import annotations

from pydantic import BaseModel


class BpmResult(BaseModel):
    """BPM detection result with octave alternatives (D-02)."""

    detected: int
    half: int
    double: int


class MoodVector(BaseModel):
    """Mood feature vector from audio analysis (D-03).

    Raw librosa values plus human-readable semantic labels.
    """

    spectral_centroid: float
    chroma: list[float]  # 12 pitch classes
    rms: float
    onset_strength: float
    labels: list[str]  # ["bright"/"dark", "energetic"/"mellow", "dense"/"sparse"]


class BpmVisualization(BaseModel):
    """Visualization data for BPM chart (AUD-03)."""

    onset_times: list[float]
    onset_values: list[float]
    beat_times: list[float]


class AudioAnalysis(BaseModel):
    """Complete audio analysis result."""

    bpm: BpmResult
    beat_times: list[float]
    mood: MoodVector
    visualization: BpmVisualization
