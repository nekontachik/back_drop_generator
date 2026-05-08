"""ffmpeg pipe encoder for H.264/yuv420p mp4 output (D-13, RND-02).

Pipes raw RGB24 frames from NumPy arrays directly into ffmpeg's stdin,
producing a cross-browser-compatible H.264 mp4 with faststart flag.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Iterable

import numpy as np


def create_ffmpeg_pipe(
    output_path: str,
    width: int,
    height: int,
    fps: int = 30,
) -> subprocess.Popen:
    """Create an ffmpeg subprocess that accepts raw RGB frames on stdin.

    Args:
        output_path: Path for the output mp4 file.
        width: Frame width in pixels.
        height: Frame height in pixels.
        fps: Frames per second (default 30).

    Returns:
        A Popen instance with stdin=PIPE and stderr=PIPE.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-loglevel", "error",
        output_path,
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)


def encode_frames(
    frames_iter: Iterable[np.ndarray],
    output_path: str,
    width: int,
    height: int,
    fps: int = 30,
    total_frames: int = 0,
    progress_callback: Callable[[float], None] | None = None,
) -> str:
    """Encode an iterable of RGB NumPy frames into an H.264 mp4 file.

    Args:
        frames_iter: Iterable of uint8 RGB frames with shape (height, width, 3).
        output_path: Path for the output mp4 file.
        width: Frame width in pixels.
        height: Frame height in pixels.
        fps: Frames per second (default 30).
        total_frames: Total number of frames (for progress calculation).
        progress_callback: Optional callable receiving progress float [0.0, 1.0].

    Returns:
        The output_path string.

    Raises:
        RuntimeError: If ffmpeg exits with a non-zero return code.
    """
    proc = create_ffmpeg_pipe(output_path, width, height, fps)

    try:
        for i, frame in enumerate(frames_iter):
            # Ensure contiguous uint8 RGB
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            if not frame.data.contiguous:
                frame = np.ascontiguousarray(frame)

            proc.stdin.write(frame.tobytes())

            if progress_callback is not None and total_frames > 0:
                progress_callback((i + 1) / total_frames)
    finally:
        proc.stdin.close()

    proc.wait()

    if proc.returncode != 0:
        stderr = proc.stderr.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg exited with code {proc.returncode}: {stderr}")

    return output_path


def mux_audio(
    video_path: str,
    audio_path: str,
    output_path: str | None = None,
) -> str:
    """Mux an audio track into a video file using ffmpeg.

    Trims or loops the audio to match the video duration. The video
    stream is copied (no re-encoding). If output_path is None, replaces
    the original video file in-place.

    Args:
        video_path: Path to the video-only mp4.
        audio_path: Path to the audio file (mp3/wav/ogg).
        output_path: Path for the muxed output. Defaults to replacing
            the input video.

    Returns:
        The output path.

    Raises:
        RuntimeError: If ffmpeg exits with a non-zero return code.
    """
    import shutil
    import tempfile

    replace_in_place = output_path is None
    if replace_in_place:
        # Write to temp file, then move back
        fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
        import os
        os.close(fd)
        dest = tmp_path
    else:
        dest = output_path

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        "-loglevel", "error",
        dest,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        if replace_in_place:
            os.unlink(tmp_path)
        raise RuntimeError(f"ffmpeg mux failed: {result.stderr}")

    if replace_in_place:
        shutil.move(tmp_path, video_path)
        return video_path

    return dest
