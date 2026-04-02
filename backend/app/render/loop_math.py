"""BPM-aligned loop duration and frame phase calculation (D-15, D-16).

Loop duration snaps to complete musical phrases (bars) at the given BPM,
clamped to 8-30 seconds. Frame phase uses t = frame_index / total_frames
for seamless loops.
"""

from __future__ import annotations

import numpy as np


def calculate_loop_params(
    bpm: int, fps: int = 30, target_bars: int = 8
) -> tuple[int, float]:
    """Calculate BPM-aligned loop duration and total frame count.

    Args:
        bpm: Beats per minute (60-200).
        fps: Frames per second (default 30).
        target_bars: Target number of musical bars (default 8).

    Returns:
        Tuple of (total_frames, loop_duration_seconds).
    """
    beats_per_bar = 4
    beat_duration = 60.0 / bpm
    bar_duration = beat_duration * beats_per_bar

    # Start with target bars and adjust to stay within 8-30 seconds
    bars = target_bars
    loop_duration = bars * bar_duration

    # Clamp: reduce bars if too long
    while loop_duration > 30.0 and bars > 4:
        bars -= 1
        loop_duration = bars * bar_duration

    # Clamp: increase bars if too short
    while loop_duration < 8.0 and bars < 16:
        bars += 1
        loop_duration = bars * bar_duration

    total_frames = round(loop_duration * fps)
    return total_frames, loop_duration


def frame_phase(frame_index: int, total_frames: int) -> float:
    """Calculate normalized phase for a frame (0.0 to <1.0).

    This is the core seamless loop primitive: t never reaches 1.0,
    ensuring the last frame connects to the first.

    Args:
        frame_index: Current frame (0-based).
        total_frames: Total frames in the loop.

    Returns:
        Phase value in [0.0, 1.0).
    """
    return frame_index / total_frames


def build_synthetic_beat_envelope(
    total_frames: int,
    bpm: int,
    fps: int,
    loop_duration: float,
    decay: float = 0.85,
) -> np.ndarray:
    """Build a synthetic beat envelope from BPM.

    Creates an array where beat positions have value 1.0 and values
    decay exponentially between beats.

    Args:
        total_frames: Number of frames in the loop.
        bpm: Beats per minute.
        fps: Frames per second.
        loop_duration: Total loop duration in seconds.
        decay: Exponential decay factor between beats.

    Returns:
        Array of shape (total_frames,) with values in [0.0, 1.0].
    """
    envelope = np.zeros(total_frames, dtype=np.float64)

    beat_interval_seconds = 60.0 / bpm
    num_beats = int(loop_duration / beat_interval_seconds)

    # Place beat peaks
    beat_frames: list[int] = []
    for i in range(num_beats):
        beat_time = i * beat_interval_seconds
        beat_frame = int(beat_time * fps)
        if beat_frame < total_frames:
            beat_frames.append(beat_frame)

    # Fill envelope with exponential decay from each beat
    for beat_frame in beat_frames:
        for f in range(total_frames):
            # Distance from nearest beat (wrapping around for seamless loop)
            dist = min(
                abs(f - beat_frame),
                abs(f - beat_frame + total_frames),
                abs(f - beat_frame - total_frames),
            )
            value = decay**dist
            envelope[f] = max(envelope[f], value)

    # Normalize so max is exactly 1.0
    max_val = np.max(envelope)
    if max_val > 0:
        envelope = envelope / max_val

    return envelope
