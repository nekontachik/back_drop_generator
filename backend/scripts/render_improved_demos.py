"""Render improved techno & synthwave demos at full quality.

Run this locally with the backend venv activated:
    cd backend
    python scripts/render_improved_demos.py

Optionally render with audio for real beat sync:
    python scripts/render_improved_demos.py --with-audio

Outputs go to the project root as demo_techno_v2.mp4 and demo_synthwave_v2.mp4
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.render.pipeline import render_video
from app.render.presets import get_preset


DEMOS = [
    {"genre": "techno", "bpm": 138, "audio": "../frontend/public/samples/techno.mp3"},
    {"genre": "synthwave", "bpm": 118, "audio": "../frontend/public/samples/synthwave.mp3"},
]


def render_with_audio(genre: str, audio_path: str, width: int, height: int, output_path: str):
    """Render using real audio analysis for beat envelope."""
    from app.services.audio_analyzer import AudioAnalyzer

    analyzer = AudioAnalyzer()
    result = analyzer.analyze(audio_path)
    bpm = result["bpm"]
    print(f"  Detected BPM: {bpm}")

    params = get_preset(genre, bpm=bpm, width=width, height=height, seed=42)
    render_video(params, output_path)


def render_synthetic(genre: str, bpm: int, width: int, height: int, output_path: str):
    """Render with synthetic beat envelope from BPM."""
    params = get_preset(genre, bpm=bpm, width=width, height=height, seed=42)
    render_video(params, output_path)


def main():
    parser = argparse.ArgumentParser(description="Render improved demos")
    parser.add_argument("--width", type=int, default=1280, help="Video width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, help="Video height (default: 720)")
    parser.add_argument("--with-audio", action="store_true", help="Use real audio for beat sync")
    parser.add_argument("--output-dir", default="..", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Rendering improved demos at {args.width}×{args.height}")
    print(f"Audio mode: {'real audio' if args.with_audio else 'synthetic BPM'}")
    print()

    for demo in DEMOS:
        genre = demo["genre"]
        output_path = str(output_dir / f"demo_{genre}_v2.mp4")
        print(f"[{genre.upper()}]")

        start = time.time()
        if args.with_audio:
            audio_path = str(Path(__file__).parent.parent / demo["audio"])
            render_with_audio(genre, audio_path, args.width, args.height, output_path)
        else:
            render_synthetic(genre, demo["bpm"], args.width, args.height, output_path)

        elapsed = time.time() - start
        size_kb = Path(output_path).stat().st_size // 1024
        print(f"  Done: {output_path} ({size_kb} KB, {elapsed:.1f}s)")
        print()

    print("All demos rendered!")
    print("To render with real audio beat sync: python scripts/render_improved_demos.py --with-audio")


if __name__ == "__main__":
    main()
