"""Generate demo videos directly from hardcoded presets — no API, no LLM.

Renders each preset at 1280×720 30fps locally using the render pipeline.
Output goes to frontend/public/examples/ for demo mode.

Usage:
    cd backend
    python scripts/generate_preset_demos.py
    python scripts/generate_preset_demos.py --presets ambient synthwave techno
    python scripts/generate_preset_demos.py --width 1920 --height 1080
    python scripts/generate_preset_demos.py --skip-existing
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.render.pipeline import render_video
from app.render.presets import PRESETS, get_preset, list_presets

# Genre → BPM mapping (typical tempo for each genre)
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


def _filename_for_genre(genre: str) -> str:
    """Build output filename from genre name."""
    return f"preset-{genre}.mp4"


def render_preset(
    genre: str,
    output_dir: Path,
    width: int,
    height: int,
    skip_existing: bool,
) -> bool:
    """Render one preset to mp4. Returns True on success."""
    filename = _filename_for_genre(genre)
    output_path = output_dir / filename

    if skip_existing and output_path.exists():
        print(f"  SKIP  {filename} (already exists)")
        return True

    bpm = GENRE_BPM.get(genre, 120)
    params = get_preset(genre, bpm=bpm, width=width, height=height, seed=42)

    print(f"\n  Rendering {filename}...")
    print(f"    Genre: {genre}  BPM: {bpm}  Layers: {len(params.layers)}")
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
        render_video(params, str(output_path), progress_callback=progress_cb)
    except Exception as exc:
        print(f"\n    ERROR: {exc}")
        return False

    elapsed = time.monotonic() - start
    size_kb = output_path.stat().st_size // 1024
    print(f"\n    Done: {size_kb} KB in {elapsed:.1f}s")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate demo videos from hardcoded presets (no API needed)."
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
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    presets_to_render = args.presets or list_presets()

    # Validate preset names
    for name in presets_to_render:
        if name not in PRESETS:
            print(f"ERROR: Unknown preset '{name}'. Available: {list_presets()}")
            sys.exit(1)

    print(f"Preset Demo Generator")
    print(f"  Output:     {output_dir.resolve()}")
    print(f"  Resolution: {args.width}×{args.height}")
    print(f"  Presets:    {len(presets_to_render)}")

    results: list[tuple[str, bool]] = []
    total_start = time.monotonic()

    for genre in presets_to_render:
        success = render_preset(
            genre=genre,
            output_dir=output_dir,
            width=args.width,
            height=args.height,
            skip_existing=args.skip_existing,
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
