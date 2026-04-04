"""Generate pre-built gallery example videos by calling the local backend API.

Usage:
    cd backend && python scripts/generate_gallery.py
    cd backend && python scripts/generate_gallery.py --skip-existing
    cd backend && python scripts/generate_gallery.py --api-url http://localhost:8000 --output-dir ../frontend/public/examples
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx

EXAMPLES = [
    {
        "filename": "tunnel-techno.mp4",
        "prompt": "Neon tunnel pulsing to heavy techno beats",
        "bpm": 138,
        "effect": "tunnel",
    },
    {
        "filename": "fractal-ambient.mp4",
        "prompt": "Ethereal fractal morphing in soft ambient hues",
        "bpm": 72,
        "effect": "fractal",
    },
    {
        "filename": "particles-edm.mp4",
        "prompt": "Explosive particle storm synced to EDM drops",
        "bpm": 128,
        "effect": "particles",
    },
    {
        "filename": "plasma-jazz.mp4",
        "prompt": "Smooth plasma waves flowing with jazz rhythms",
        "bpm": 110,
        "effect": "plasma",
    },
    {
        "filename": "tunnel-synthwave.mp4",
        "prompt": "Retro synthwave tunnel with neon grids",
        "bpm": 118,
        "effect": "tunnel",
    },
    {
        "filename": "fractal-classical.mp4",
        "prompt": "Elegant fractal bloom following classical dynamics",
        "bpm": 90,
        "effect": "fractal",
    },
]


def generate_example(
    example: dict,
    api_url: str,
    output_dir: Path,
    skip_existing: bool,
    client: httpx.Client,
) -> bool:
    """Generate a single example video via the backend API.

    Returns True if the video was generated successfully, False otherwise.
    """
    output_path = output_dir / example["filename"]

    if skip_existing and output_path.exists():
        print(f"  Skipping {example['filename']} (already exists)")
        return True

    print(f"\n  Generating {example['filename']}...")
    print(f"    Prompt: {example['prompt']}")
    print(f"    BPM: {example['bpm']}  Effect: {example['effect']}")

    # Submit generation request
    try:
        response = client.post(
            f"{api_url}/generate",
            data={
                "prompt": example["prompt"],
                "bpm": str(example["bpm"]),
                "effect": example["effect"],
                "width": "1920",
                "height": "1080",
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"    ERROR: Backend returned {exc.response.status_code}: {exc.response.text}")
        return False
    except httpx.RequestError as exc:
        print(f"    ERROR: Could not connect to backend at {api_url}: {exc}")
        return False

    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"    Job ID: {job_id}")

    # Poll for completion
    start = time.monotonic()
    last_progress = -1
    while True:
        try:
            status_resp = client.get(f"{api_url}/jobs/{job_id}", timeout=10.0)
            status_resp.raise_for_status()
        except httpx.RequestError as exc:
            print(f"    ERROR: Status poll failed: {exc}")
            return False

        status_data = status_resp.json()
        status = status_data["status"]
        progress = int(status_data.get("progress", 0) * 100)

        if progress != last_progress:
            elapsed = time.monotonic() - start
            print(f"    [{elapsed:5.1f}s] {status} {progress}%", flush=True)
            last_progress = progress

        if status == "complete":
            break
        if status == "failed":
            error = status_data.get("error", "unknown error")
            print(f"    ERROR: Job failed: {error}")
            return False

        time.sleep(2)

    # Download the rendered video
    try:
        download_resp = client.get(f"{api_url}/jobs/{job_id}/download", timeout=60.0)
        download_resp.raise_for_status()
    except httpx.RequestError as exc:
        print(f"    ERROR: Download failed: {exc}")
        return False

    output_path.write_bytes(download_resp.content)
    size_kb = output_path.stat().st_size // 1024
    print(f"    Saved: {output_path} ({size_kb} KB)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate pre-built gallery example videos via the local backend API."
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--output-dir",
        default="../frontend/public/examples",
        help="Output directory for generated MP4 files (default: ../frontend/public/examples)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip generation if the output file already exists",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Gallery Generator")
    print(f"  API URL:    {args.api_url}")
    print(f"  Output dir: {output_dir.resolve()}")
    print(f"  Examples:   {len(EXAMPLES)}")
    print(f"  Skip existing: {args.skip_existing}")

    # Verify backend is reachable
    try:
        with httpx.Client() as probe:
            probe.get(f"{args.api_url}/health", timeout=5.0)
    except httpx.RequestError:
        # /health may not exist — that's fine, errors will surface per-example
        pass

    results: list[tuple[str, bool]] = []
    with httpx.Client() as client:
        for example in EXAMPLES:
            success = generate_example(
                example=example,
                api_url=args.api_url,
                output_dir=output_dir,
                skip_existing=args.skip_existing,
                client=client,
            )
            results.append((example["filename"], success))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    success_count = 0
    for filename, success in results:
        output_path = output_dir / filename
        if success and output_path.exists():
            size_kb = output_path.stat().st_size // 1024
            print(f"  OK  {filename} ({size_kb} KB)")
            success_count += 1
        elif success:
            print(f"  OK  {filename} (skipped)")
            success_count += 1
        else:
            print(f"  FAIL  {filename}")

    print(f"\n{success_count}/{len(EXAMPLES)} videos ready in {output_dir.resolve()}")

    if success_count < len(EXAMPLES):
        sys.exit(1)


if __name__ == "__main__":
    main()
