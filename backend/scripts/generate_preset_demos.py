"""Generate demo videos from presets with real audio beat sync.

Renders each preset at 1280×720 30fps using real audio samples for
natural beat timing. Falls back to synthetic BPM if no audio file exists.
Output goes to frontend/public/examples/ for demo mode.

Usage:
    cd backend
    python scripts/generate_preset_demos.py
    python scripts/generate_preset_demos.py --presets ambient synthwave techno
    python scripts/generate_preset_demos.py --width 1920 --height 1080
    python scripts/generate_preset_demos.py --skip-existing
    python scripts/generate_preset_demos.py --no-audio   # force synthetic BPM
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.render.encoder import mux_audio
from app.render.pipeline import render_video
from app.render.presets import PRESETS, get_preset, list_presets

# Genre → BPM mapping (fallback when no audio file is available)
GENRE_BPM: dict[str, int] = {
    "ambient": 72,
    "dark-ambient": 65,
    "synthwave": 118,
    "techno": 138,
    "dark-techno": 142,
    "melodic-techno": 124,
    "house": 124,
    "deep-house": 120,
    "psytrance": 145,
    "drum-and-bass": 174,
    "industrial": 130,
    "edm": 128,
    "classical": 90,
    "jazz": 110,
}

# Audio sample directory (relative to backend/)
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "samples"


def _find_audio(genre: str) -> Path | None:
    """Find an audio sample for this genre."""
    for ext in (".mp3", ".wav", ".ogg"):
        path = SAMPLES_DIR / f"{genre}{ext}"
        if path.exists():
            return path
    return None


def _analyze_audio(audio_path: Path) -> tuple[int, list[float]]:
    """Analyze audio file, return (bpm, beat_times)."""
    from app.services.audio_analyzer import analyze_audio

    audio_bytes = audio_path.read_bytes()
    result = analyze_audio(audio_bytes)
    return result.bpm.detected, result.beat_times


def _filename_for_genre(genre: str) -> str:
    """Build output filename from genre name."""
    return f"preset-{genre}.mp4"


def render_preset(
    genre: str,
    output_dir: Path,
    width: int,
    height: int,
    skip_existing: bool,
    use_audio: bool,
) -> bool:
    """Render one preset to mp4. Returns True on success."""
    filename = _filename_for_genre(genre)
    output_path = output_dir / filename

    if skip_existing and output_path.exists():
        print(f"  SKIP  {filename} (already exists)")
        return True

    # Try to use real audio for beat sync
    beat_times: list[float] | None = None
    bpm = GENRE_BPM.get(genre, 120)
    audio_path = _find_audio(genre) if use_audio else None

    if audio_path:
        try:
            detected_bpm, beat_times = _analyze_audio(audio_path)
            bpm = detected_bpm
            print(f"\n  Rendering {filename} (audio: {audio_path.name}, BPM: {bpm})...")
        except Exception as exc:
            print(f"\n  Audio analysis failed for {genre}: {exc}")
            print(f"  Falling back to synthetic BPM {bpm}")
            beat_times = None
    else:
        mode = "no audio file" if use_audio else "audio disabled"
        print(f"\n  Rendering {filename} (synthetic BPM: {bpm}, {mode})...")

    params = get_preset(genre, bpm=bpm, width=width, height=height, seed=42)

    print(f"    Genre: {genre}  BPM: {bpm}  Layers: {len(params.layers)}  "
          f"Audio: {'real' if beat_times else 'synthetic'}")
    for i, layer in enumerate(params.layers):
        print(f"    Layer {i}: {layer.effect_name}  opacity={layer.opacity}  "
              f"beat={layer.beat_response.value}  blend={layer.blend_mode.value}")

    start = time.monotonic()

    def progress_cb(p: float) -> None:
        bar_len = 30
        filled = int(bar_len * p)
        bar = "█" * filled + "░" * (bar_len - filled)
        elapsed = time.monotonic() - start
        print(f"\r    [{bar}] {p*100:5.1f}%  {elapsed:.0f}s", end="", flush=True)

    try:
        render_video(
            params,
            str(output_path),
            progress_callback=progress_cb,
            beat_times=beat_times,
        )
    except Exception as exc:
        print(f"\n    ERROR: {exc}")
        return False

    # Mux audio into the video if we have an audio file
    if audio_path:
        try:
            print(f"\n    Muxing audio: {audio_path.name}...")
            mux_audio(str(output_path), str(audio_path))
            print(f"    Audio muxed successfully")
        except Exception as exc:
            print(f"    WARNING: Audio mux failed ({exc}), video-only output kept")

    elapsed = time.monotonic() - start
    size_kb = output_path.stat().st_size // 1024
    print(f"\n    Done: {size_kb} KB in {elapsed:.1f}s")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate demo videos from presets with real audio beat sync."
    )
    parser.add_argument(
        "--output-dir",
        default="../frontend/public/examples",
        help="Output directory (default: ../frontend/public/examples)",
    )
    parser.add_argument(
        "--presets",
        nargs="*",
        default=None,
        help="Specific presets to render (default: all)",
    )
    parser.add_argument(
        "--width", type=int, default=1280, help="Video width (default: 1280)",
    )
    parser.add_argument(
        "--height", type=int, default=720, help="Video height (default: 720)",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip if output file already exists",
    )
    parser.add_argument(
        "--no-audio", action="store_true",
        help="Force synthetic BPM (ignore audio samples)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    presets_to_render = args.presets or list_presets()

    # Validate preset names
    for name in presets_to_render:
        if name not in PRESETS:
            print(f"ERROR: Unknown preset '{name}'. Available: {list_presets()}")
            sys.exit(1)

    use_audio = not args.no_audio

    print(f"Preset Demo Generator")
    print(f"  Output:     {output_dir.resolve()}")
    print(f"  Resolution: {args.width}×{args.height}")
    print(f"  Presets:    {len(presets_to_render)}")
    print(f"  Audio:      {'real samples' if use_audio else 'synthetic BPM'}")
    if use_audio:
        print(f"  Samples:    {SAMPLES_DIR}")

    results: list[tuple[str, bool]] = []
    total_start = time.monotonic()

    for genre in presets_to_render:
        success = render_preset(
            genre=genre,
            output_dir=output_dir,
            width=args.width,
            height=args.height,
            skip_existing=args.skip_existing,
            use_audio=use_audio,
        )
        results.append((genre, success))

    total_elapsed = time.monotonic() - total_start

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    ok = 0
    for genre, success in results:
        filename = _filename_for_genre(genre)
        path = output_dir / filename
        if success and path.exists():
            size_kb = path.stat().st_size // 1024
            print(f"  OK    {filename:30s} {size_kb:6d} KB")
            ok += 1
        elif success:
            print(f"  SKIP  {filename}")
            ok += 1
        else:
            print(f"  FAIL  {filename}")

    print(f"\n{ok}/{len(presets_to_render)} videos in {total_elapsed:.0f}s")
    print(f"Output: {output_dir.resolve()}")

    if ok < len(presets_to_render):
        sys.exit(1)


if __name__ == "__main__":
    main()
