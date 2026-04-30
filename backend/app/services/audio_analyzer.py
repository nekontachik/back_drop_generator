"""Audio analysis service using librosa (AUD-01 through AUD-04).

Stateless service functions for BPM detection, mood feature extraction,
and beat visualization data from uploaded audio clips.
"""

from __future__ import annotations

from io import BytesIO

import librosa
import numpy as np

from app.models.audio import AudioAnalysis, BpmResult, BpmVisualization, MoodVector

# Accepted audio file extensions (D-01)
_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}

# Maximum audio file size: 10MB (D-04)
_MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_audio(audio_bytes: bytes, filename: str | None = None) -> None:
    """Validate audio file size and format.

    Args:
        audio_bytes: Raw audio file bytes.
        filename: Original filename for extension checking.

    Raises:
        ValueError: If file exceeds 10MB or has non-audio extension.
    """
    if len(audio_bytes) > _MAX_FILE_SIZE:
        raise ValueError(
            f"Audio file exceeds 10MB limit ({len(audio_bytes)} bytes)"
        )

    if filename is not None:
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in _AUDIO_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format '{ext}'. "
                f"Accepted: {', '.join(sorted(_AUDIO_EXTENSIONS))}"
            )


def classify_mood(centroid: float, rms: float, onset: float) -> list[str]:
    """Map raw audio features to human-readable mood labels.

    Thresholds based on typical ranges for 11025 Hz sample rate:
    - spectral_centroid: 1000-4000 Hz (low=dark, high=bright)
    - rms: 0.01-0.3 (low=mellow, high=energetic)
    - onset_strength: 0.5-5.0 (low=sparse, high=dense)

    Args:
        centroid: Mean spectral centroid in Hz.
        rms: Mean RMS energy.
        onset: Mean onset strength.

    Returns:
        List of 3 labels: brightness, energy, density.
    """
    labels: list[str] = []

    # Brightness axis
    labels.append("bright" if centroid > 2500 else "dark")

    # Energy axis
    labels.append("energetic" if rms > 0.1 else "mellow")

    # Density axis
    labels.append("dense" if onset > 2.0 else "sparse")

    return labels


def analyze_audio(audio_bytes: bytes) -> AudioAnalysis:
    """Analyze audio clip for BPM, beats, and mood features.

    Loads audio at 22050 Hz (librosa default, optimal for beat detection),
    extracts BPM with octave alternatives, mood vector, and visualization data.

    Args:
        audio_bytes: Raw audio file bytes (WAV, MP3, OGG, or M4A).

    Returns:
        AudioAnalysis with BPM, beat times, mood vector, and visualization data.
    """
    # Load first 30 seconds at 11025 Hz — minimal RAM footprint for free-tier hosting
    # 30s is sufficient for BPM detection and mood classification
    y, sr = librosa.load(BytesIO(audio_bytes), sr=11025, duration=30.0)

    # Beat tracking -- tempo may be ndarray or float depending on librosa version
    tempo_arr, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if hasattr(tempo_arr, "ndim") and tempo_arr.ndim > 0:
        bpm = float(tempo_arr[0])
    else:
        bpm = float(tempo_arr)

    # Beat timestamps in seconds
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # Octave-error alternatives (D-02)
    bpm_result = BpmResult(
        detected=round(bpm),
        half=round(bpm) // 2,
        double=round(bpm) * 2,
    )

    # Mood features (D-03)
    spectral_centroid = float(
        np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    )
    chroma = librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1).tolist()
    rms = float(np.mean(librosa.feature.rms(y=y)))

    # Onset envelope for visualization and mood (AUD-03)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_mean = float(np.mean(onset_env))

    # Visualization data
    onset_times = librosa.times_like(onset_env, sr=sr).tolist()
    onset_values = onset_env.tolist()

    visualization = BpmVisualization(
        onset_times=onset_times,
        onset_values=onset_values,
        beat_times=beat_times,
    )

    mood = MoodVector(
        spectral_centroid=spectral_centroid,
        chroma=chroma,
        rms=rms,
        onset_strength=onset_mean,
        labels=classify_mood(spectral_centroid, rms, onset_mean),
    )

    return AudioAnalysis(
        bpm=bpm_result,
        beat_times=beat_times,
        mood=mood,
        visualization=visualization,
    )
