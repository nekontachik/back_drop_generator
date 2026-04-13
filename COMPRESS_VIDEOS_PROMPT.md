# Claude Code Prompt — Compress Example Videos

Copy and paste this into Claude Code (terminal):

---

## Task: Compress pre-generated example videos in the Beat Visuals project

I have several large example video files in `frontend/public/examples/` that need to be compressed with ffmpeg to reduce load times. The videos are used as carousel demo items and the hero background loop.

**Current situation:**
- `fractal-ambient.mp4` — ~20MB
- `fractal-classical.mp4` — ~14MB
- Other files may also be large

**Target:** Each file compressed to ~3–5MB at 720p, keeping 30fps, suitable for web autoplay.

**Steps to complete:**

1. List all files in `frontend/public/examples/` with their sizes (`ls -lh frontend/public/examples/`).

2. For each `.mp4` file larger than 5MB, compress it in-place using:
   ```bash
   ffmpeg -i input.mp4 -vf scale=-2:720 -c:v libx264 -crf 28 -preset slow \
     -movflags +faststart -an -y output_compressed.mp4
   ```
   Then replace the original:
   ```bash
   mv output_compressed.mp4 input.mp4
   ```
   Use `-an` (no audio) since these are muted loops. `-movflags +faststart` puts the moov atom at the start for faster web streaming.

3. After compressing all files, re-run `ls -lh frontend/public/examples/` and confirm each file is under 6MB.

4. If ffmpeg is not installed: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux).

**Note:** Run this from the root of the `back_drop_generator` repo. The videos are muted (they're background loops), so audio tracks should be stripped with `-an`.

---
