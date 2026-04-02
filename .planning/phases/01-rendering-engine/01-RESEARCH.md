# Phase 1: Rendering Engine - Research

**Researched:** 2026-04-01
**Domain:** Python backend -- FastAPI, NumPy frame generation, ffmpeg encoding, SSE progress, ProcessPoolExecutor
**Confidence:** HIGH

## Summary

Phase 1 builds a FastAPI backend that accepts a text prompt and BPM, renders a seamless-loop BPM-synced video with 4 visual effects (tunnel, fractal, particles, plasma), and streams progress via SSE. No frontend, no LLM, no audio upload in this phase.

The core technical challenges are: (1) generating visually distinct effects as NumPy arrays with correct seamless-loop math, (2) piping frames to ffmpeg for H.264/yuv420p encoding that plays in all browsers, (3) running renders in a separate process via ProcessPoolExecutor so the FastAPI event loop stays responsive, and (4) reporting progress from the render process back to the SSE endpoint.

A key discovery during research: FastAPI 0.135.0+ ships with built-in `EventSourceResponse` (no external `sse-starlette` needed). The recommended progress-reporting pattern uses `multiprocessing.Value` as a shared progress counter between the render process and the SSE endpoint, avoiding Redis or any external dependency.

**Primary recommendation:** Build the 4 effects with pure NumPy math, pipe to ffmpeg via subprocess, use ProcessPoolExecutor with multiprocessing.Value for progress, and use FastAPI's built-in SSE support. Keep everything in-process with no Redis or external queue -- sufficient for this phase and the portfolio demo.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Hybrid parameter model -- shared base params + per-effect overrides
- **D-02:** Shared base params (5): bg_color, primary_color, accent_color, intensity (0-1), speed (0-1)
- **D-03:** Minimal per-effect overrides (1-2 each): tunnel(twist_speed, ring_count), fractal(zoom_rate, c_param), particles(count, connection_dist), plasma(layer_count, wave_freq)
- **D-04:** Design the full Pydantic RenderParams schema now with Phase 4 (LLM output) in mind -- Phase 1 populates it from keyword matching, Phase 4 from LLM, same schema
- **D-05:** Renders are reproducible -- include a random seed param. Same seed + same params = identical output
- **D-06:** Effects registered via registry pattern: dict mapping `{"tunnel": TunnelEffect, "fractal": FractalEffect, ...}`
- **D-07:** In Phase 1 (no LLM), effect selected via keyword cluster matching from text prompt
- **D-08:** Fallback when no keywords match: default to tunnel effect with neutral color palette
- **D-09:** Keyword clusters map to both effect selection AND color palette. 5 genres (techno, house, ambient, industrial, psytrance) each map to default effect + colors
- **D-10:** REST standard endpoints: POST /generate -> {job_id}, GET /jobs/{id} -> status/progress, GET /jobs/{id}/stream -> SSE, GET /jobs/{id}/download -> mp4 file, GET /health
- **D-11:** Progress via Server-Sent Events (SSE)
- **D-12:** Video files served directly from local disk via FastAPI FileResponse
- **D-13:** NumPy + ffmpeg pipe for frame generation (not cv2.VideoWriter)
- **D-14:** ProcessPoolExecutor for render isolation (not asyncio.to_thread)
- **D-15:** Seamless loop math: t = frame_index / total_frames, periodic functions (sin/cos), never let t reach 1.0
- **D-16:** Loop duration is BPM-aligned -- snaps to nearest complete musical phrase (e.g., 8 bars at given BPM)
- **D-17:** Resolution configurable via API param. Default 1080p (1920x1080 30fps), accept 480p for fast dev previews
- **D-18:** TTL-based file cleanup -- delete rendered files older than 1 hour

### Claude's Discretion
- Exact ffmpeg encoding flags and pipe implementation
- Internal job state machine design (pending/rendering/complete/failed)
- Error handling and retry strategy for failed renders
- Exact keyword cluster contents beyond the examples given
- File storage directory structure and naming
- Health endpoint detail level

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INP-01 | User can enter a text prompt describing desired visual style | FastAPI POST endpoint with Pydantic model; keyword cluster matching maps prompt to effect + palette |
| INP-02 | User can manually enter BPM (60-200 range) | Pydantic Field with ge=60, le=200 validation; BPM drives loop duration calculation |
| VFX-01 | 3D tunnel with perspective, twisting, BPM flashes | NumPy meshgrid + polar coordinate math; twist_speed and ring_count as per-effect params |
| VFX-02 | Julia Set fractal morphing and zooming | NumPy complex plane iteration; zoom_rate and c_param as per-effect params |
| VFX-03 | Particle system with gravity, connections, BPM explosions | NumPy array of particle positions + velocities; seeded random for reproducibility |
| VFX-04 | Plasma waves -- multi-layered slow waves | NumPy sin/cos sum patterns; layer_count and wave_freq as per-effect params |
| RND-01 | Renders seamless-loop mp4 (last frame connects to first frame) | t = frame_index / total_frames with sin(2*pi*t) cyclic functions; validated by frame diff test |
| RND-02 | Output at 1080p 30fps via H.264 + yuv420p (ffmpeg) | ffmpeg subprocess pipe with -c:v libx264 -pix_fmt yuv420p -movflags +faststart |
| RND-03 | Async render queue with progress reporting via SSE | ProcessPoolExecutor + multiprocessing.Value for progress; FastAPI built-in EventSourceResponse |
| RND-04 | Render runs in separate process (ProcessPoolExecutor) | loop.run_in_executor(ProcessPoolExecutor(1), render_fn, params); GIL-free CPU isolation |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Budget:** $0-5/month hosting
- **Tech stack (backend):** Python -- FastAPI
- **Render time:** No GPU -- async queue with progress bar
- **Security:** No eval/exec on user input
- **Content:** Abstract geometric graphics only
- **GSD Workflow:** All changes through GSD commands

## Standard Stack

### Core (Phase 1 only)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.13 | Runtime | Installed on system; NumPy 2.4.x confirmed compatible |
| FastAPI | >=0.135.0 | API framework + built-in SSE | 0.135.0 added native EventSourceResponse; latest is 0.135.3 |
| Pydantic | >=2.12 | Request/response validation, RenderParams schema | FastAPI requires Pydantic v2; latest is 2.12.5 |
| NumPy | >=2.4 | Frame-level pixel math for all 4 effects | Core of all per-pixel computation; latest 2.4.4 supports Python 3.13 |
| uvicorn | >=0.42 | ASGI server | Production server for FastAPI; latest is 0.42.0 |
| ffmpeg (system) | 7.1.1 | Video encoding (H.264/yuv420p) | Already installed via Homebrew; piped via subprocess |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| opencv-python-headless | >=4.13 | Color space conversion (RGB->BGR if needed), optional image ops | Only if color conversion is needed; NOT for VideoWriter |
| python-multipart | latest | Form data parsing for POST /generate | Required by FastAPI for Form() parameters |
| python-dotenv | latest | Load .env for local development | Configuration management |

### Development

| Library | Version | Purpose |
|---------|---------|---------|
| pytest | >=9.0 | Test framework; latest 9.0.2 |
| pytest-asyncio | >=1.3 | Async endpoint testing; latest 1.3.0 |
| httpx | >=0.28 | FastAPI TestClient; latest 0.28.1 |
| ruff | >=0.15 | Linting + formatting; latest 0.15.8 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI built-in SSE | sse-starlette 3.3.4 | External dep; FastAPI 0.135+ has native support -- use built-in |
| ProcessPoolExecutor | ARQ + Redis | Adds Redis dependency; overkill for single-instance portfolio demo |
| multiprocessing.Value for progress | Redis pub/sub | External dependency; shared Value is sufficient for single-machine |
| opencv-python-headless | Pillow | OpenCV faster for array ops; Pillow better for text -- may not need either |
| numpy only | scipy for signal processing | scipy adds heavy dependency; sin/cos math is sufficient for 4 effects |

**Installation:**

```bash
# Create project with uv
uv init backend && cd backend
uv add "fastapi>=0.135.0" "uvicorn[standard]>=0.42" "pydantic>=2.12" "numpy>=2.4" python-multipart python-dotenv
uv add --dev "pytest>=9.0" "pytest-asyncio>=1.3" "httpx>=0.28" "ruff>=0.15"
```

**Version verification:** All versions confirmed against PyPI on 2026-04-01. FastAPI 0.135.3, NumPy 2.4.4, Pydantic 2.12.5, uvicorn 0.42.0, pytest 9.0.2, pytest-asyncio 1.3.0, httpx 0.28.1, ruff 0.15.8.

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, lifespan, routes
│   ├── config.py               # Pydantic Settings (paths, defaults)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── generate.py         # POST /generate, GET /jobs/{id}, GET /jobs/{id}/stream
│   │   ├── health.py           # GET /health
│   │   └── download.py         # GET /jobs/{id}/download
│   ├── models/
│   │   ├── __init__.py
│   │   ├── params.py           # RenderParams, EffectParams (Pydantic)
│   │   ├── job.py              # JobState, JobStatus enum
│   │   └── api.py              # Request/Response models
│   ├── render/
│   │   ├── __init__.py
│   │   ├── pipeline.py         # Orchestrate: select effect -> generate frames -> encode
│   │   ├── encoder.py          # ffmpeg pipe: frames -> mp4
│   │   ├── loop_math.py        # BPM-aligned duration, frame count, phase calculation
│   │   └── effects/
│   │       ├── __init__.py     # EFFECT_REGISTRY dict
│   │       ├── base.py         # BaseEffect ABC
│   │       ├── tunnel.py       # 3D tunnel effect
│   │       ├── fractal.py      # Julia Set fractal
│   │       ├── particles.py    # Particle system
│   │       └── plasma.py       # Plasma waves
│   ├── services/
│   │   ├── __init__.py
│   │   ├── job_manager.py      # In-memory job store, create/update/get
│   │   ├── prompt_mapper.py    # Keyword cluster matching -> effect + palette
│   │   └── cleanup.py          # TTL-based file cleanup background task
│   └── worker.py               # ProcessPoolExecutor wrapper, progress reporting
├── data/
│   └── renders/                # Output mp4 files (gitignored)
├── tests/
│   ├── conftest.py             # Shared fixtures (app client, temp dirs)
│   ├── test_api.py             # Endpoint integration tests
│   ├── test_effects.py         # Each effect renders without error
│   ├── test_loop_math.py       # Frame count, duration, phase calculations
│   ├── test_encoder.py         # ffmpeg pipe produces valid H.264
│   ├── test_seamless.py        # Frame[0] vs frame[N-1] pixel diff
│   └── test_prompt_mapper.py   # Keyword matching returns correct effect
├── pyproject.toml
└── .env.example
```

### Pattern 1: ProcessPoolExecutor with Shared Progress

**What:** Submit render work to a ProcessPoolExecutor. Use multiprocessing.Value as shared memory for progress reporting. The SSE endpoint polls this value.

**When to use:** Every render request. This is the core concurrency pattern.

**Example:**

```python
# worker.py
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# Module-level executor (created once, reused)
_executor = ProcessPoolExecutor(max_workers=1)

# Shared progress values keyed by job_id
_progress_values: dict[str, multiprocessing.Value] = {}

def submit_render(job_id: str, params: dict) -> None:
    progress = multiprocessing.Value('d', 0.0)  # double, shared between processes
    _progress_values[job_id] = progress
    future = _executor.submit(_render_in_process, job_id, params, progress)
    future.add_done_callback(lambda f: _on_render_complete(job_id, f))

def _render_in_process(job_id: str, params: dict, progress: multiprocessing.Value) -> str:
    """Runs in separate process -- has its own GIL."""
    from app.render.pipeline import render_video
    return render_video(job_id, params, progress_callback=progress)

def get_progress(job_id: str) -> float:
    val = _progress_values.get(job_id)
    return val.value if val else 0.0
```

**Key insight:** multiprocessing.Value is passed to the child process and both parent and child can read/write it. The SSE endpoint in the parent process reads progress; the render loop in the child process writes it. No Redis needed.

### Pattern 2: Built-in FastAPI SSE for Progress Streaming

**What:** Use FastAPI 0.135+ EventSourceResponse to stream job progress.

**When to use:** GET /jobs/{id}/stream endpoint.

```python
# api/generate.py
from collections.abc import AsyncIterable
from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent
from app.services.job_manager import get_job
from app.worker import get_progress
import asyncio

router = APIRouter()

@router.get("/jobs/{job_id}/stream", response_class=EventSourceResponse)
async def stream_progress(job_id: str) -> AsyncIterable[ServerSentEvent]:
    while True:
        job = get_job(job_id)
        if not job:
            yield ServerSentEvent(data='{"error": "Job not found"}', event="error")
            return
        progress = get_progress(job_id)
        yield ServerSentEvent(
            data=job.model_dump_json(),
            event=job.status.value,
        )
        if job.status in ("complete", "failed"):
            return
        await asyncio.sleep(0.5)
```

### Pattern 3: Seamless Loop with Cyclic Phase

**What:** All effect parameters are functions of t in [0, 1) mapped through sin(2*pi*t) or cos(2*pi*t).

**When to use:** Every frame of every effect. This is non-negotiable for seamless looping.

```python
# render/loop_math.py
import math

def calculate_loop_params(bpm: int, fps: int = 30, target_bars: int = 8) -> tuple[int, float]:
    """Calculate frame count for perfect BPM-aligned loop.
    
    Returns (total_frames, loop_duration_seconds).
    """
    beats_per_bar = 4
    beat_duration = 60.0 / bpm
    bar_duration = beat_duration * beats_per_bar
    loop_duration = target_bars * bar_duration
    total_frames = round(loop_duration * fps)
    return total_frames, loop_duration

def frame_phase(frame_index: int, total_frames: int) -> float:
    """Normalized phase [0, 1) for seamless looping. Never reaches 1.0."""
    return frame_index / total_frames
```

### Pattern 4: Effect Registry with BaseEffect ABC

**What:** Each effect implements a `render_frame` method. Registry maps name string to class.

```python
# render/effects/base.py
from abc import ABC, abstractmethod
import numpy as np

class BaseEffect(ABC):
    @abstractmethod
    def render_frame(
        self,
        t: float,                    # phase [0, 1)
        width: int, height: int,     # resolution
        params: dict,                # effect-specific params
        beat_intensity: float,       # [0, 1] BPM pulse at this frame
        rng: np.random.Generator,    # seeded RNG for reproducibility
    ) -> np.ndarray:
        """Return (height, width, 3) uint8 RGB array."""
        ...

    @property
    @abstractmethod
    def name(self) -> str: ...

# render/effects/__init__.py
EFFECT_REGISTRY: dict[str, type[BaseEffect]] = {}

def register(cls: type[BaseEffect]) -> type[BaseEffect]:
    EFFECT_REGISTRY[cls().name] = cls
    return cls
```

### Pattern 5: ffmpeg Pipe Encoding

**What:** Pipe raw RGB frames to ffmpeg stdin for H.264 encoding.

```python
# render/encoder.py
import subprocess

def create_ffmpeg_pipe(output_path: str, width: int, height: int, fps: int = 30):
    cmd = [
        "ffmpeg", "-y",
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
```

### Anti-Patterns to Avoid

- **cv2.VideoWriter for final output:** Produces MPEG-4 Part 2 (mp4v codec), not H.264. Safari will not play it. Use ffmpeg pipe instead.
- **asyncio.to_thread for renders:** NumPy GIL contention still degrades event loop. Use ProcessPoolExecutor.
- **Storing all frames in memory:** 900 frames at 1080p = 5.4GB. Pipe one frame at a time to ffmpeg.
- **Accumulating t += dt:** Floating-point drift. Always compute t = frame_index / total_frames.
- **Linear parameters with crossfade looping:** Visible artifacts at loop point. Use cyclic sin/cos functions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Video encoding (H.264) | Custom encoder or cv2.VideoWriter | ffmpeg subprocess pipe | ffmpeg handles codec complexity, yuv420p conversion, faststart |
| SSE protocol | Manual StreamingResponse with text formatting | FastAPI built-in EventSourceResponse | Handles keep-alive, cache headers, proxy buffering prevention |
| Process isolation | Custom multiprocessing.Process management | ProcessPoolExecutor | Handles process lifecycle, exception propagation, cleanup |
| Shared progress counter | File-based or socket-based IPC | multiprocessing.Value | Atomic, fast, zero-config shared memory |
| JSON validation | Manual dict checking | Pydantic models with Field validators | Type safety, automatic OpenAPI docs, error messages |
| UUID generation | Custom ID scheme | uuid4() | Globally unique, no collisions |

**Key insight:** This phase has no exotic dependencies. The entire stack is stdlib Python + NumPy + FastAPI + ffmpeg. Avoid adding libraries for problems that stdlib solves.

## Common Pitfalls

### Pitfall 1: GIL Contention Blocks SSE During Render

**What goes wrong:** Using asyncio.to_thread() instead of ProcessPoolExecutor. NumPy Python-level code holds the GIL. SSE endpoint stalls, health checks timeout.
**Why it happens:** Developers assume threads are sufficient for CPU isolation. NumPy only releases GIL during C-level array ops, not Python loop logic.
**How to avoid:** Use ProcessPoolExecutor(max_workers=1). Decision D-14 mandates this.
**Warning signs:** SSE progress freezes mid-render then bursts; health endpoint returns >1s during render.

### Pitfall 2: Seamless Loop Discontinuity

**What goes wrong:** Visible "pop" at loop point when video repeats.
**Why it happens:** Off-by-one frame count (rendering frame N which equals frame 0), or using linear parameters instead of cyclic sin/cos.
**How to avoid:** t = frame_index / total_frames, range [0, 1), use sin(2*pi*t). Automated pixel-diff test between frame[0] and frame[N-1].
**Warning signs:** Mean pixel diff between first and last frame is >2x the average consecutive-frame diff.

### Pitfall 3: Safari/iOS Cannot Play Video

**What goes wrong:** cv2.VideoWriter produces MPEG-4 Part 2 codec. Chrome plays it; Safari shows blank.
**Why it happens:** Most OpenCV tutorials use fourcc('mp4v') which is not H.264.
**How to avoid:** ffmpeg pipe with -c:v libx264 -pix_fmt yuv420p. Verify with ffprobe. Decision D-13 mandates this.
**Warning signs:** ffprobe shows "mpeg4" codec or "yuv444p" pixel format.

### Pitfall 4: Python Loops Over Pixels (30+ Minute Renders)

**What goes wrong:** Nested for-loops over pixel coordinates instead of vectorized NumPy operations.
**Why it happens:** Translating math formulas literally to Python without vectorization.
**How to avoid:** Use np.meshgrid() to create coordinate grids, then apply vectorized operations. Never `for x in range(width): for y in range(height):`.
**Warning signs:** 480p render takes >30 seconds for a 10-second clip (should be <5 seconds).

### Pitfall 5: Memory Exhaustion from Frame Accumulation

**What goes wrong:** Collecting all frames in a list before encoding.
**Why it happens:** Seems simpler to generate all frames then encode. But 900 frames * 6MB = 5.4GB.
**How to avoid:** Generate one frame, write to ffmpeg stdin, discard, repeat. Pre-allocate a single frame buffer and rewrite it.
**Warning signs:** Memory usage climbs linearly during render; OOM after ~100 frames at 1080p.

### Pitfall 6: Particle System Breaks Seamless Looping

**What goes wrong:** Particle positions are stateful (position += velocity). State at frame[N-1] does not match frame[0], breaking the loop.
**Why it happens:** Particles are inherently simulation-based, unlike mathematical effects (tunnel, fractal, plasma) where position is a pure function of t.
**How to avoid:** Use the seeded RNG + phase to deterministically compute particle positions as a function of t, not as accumulated state. Alternative: pre-compute all particle positions for the full loop at init time, ensuring pos[0] == pos[N] (wrap the trajectory).
**Warning signs:** Particles "jump" at loop point.

### Pitfall 7: BPM-Aligned Duration Produces Awkward Lengths

**What goes wrong:** At low BPM (60), 8 bars = 32 seconds. At high BPM (200), 8 bars = 9.6 seconds. Very long or very short videos.
**Why it happens:** Fixed bar count with variable BPM.
**How to avoid:** Clamp loop duration to a reasonable range (8-30 seconds). Adjust bar count to keep duration in range: min 4 bars, max 16 bars. Decision D-16 says "snap to nearest complete musical phrase" -- this means the bar count should be variable.
**Warning signs:** Generated video is >30s or <5s.

## Code Examples

### BPM-Synced Beat Intensity (no audio analysis in Phase 1)

In Phase 1, BPM is provided manually (no librosa). Generate a synthetic beat envelope:

```python
# render/loop_math.py
import numpy as np

def build_synthetic_beat_envelope(
    total_frames: int,
    bpm: int,
    fps: int = 30,
    loop_duration: float = 16.0,
    decay: float = 0.85,
) -> np.ndarray:
    """Create per-frame beat intensity from BPM alone (no audio).
    Peaks at each beat, exponentially decays."""
    beat_period = 60.0 / bpm
    beat_times = np.arange(0, loop_duration, beat_period)
    
    envelope = np.zeros(total_frames)
    for bt in beat_times:
        frame_idx = int(bt * fps)
        if 0 <= frame_idx < total_frames:
            envelope[frame_idx] = 1.0
    
    # Forward pass: exponential decay between beats
    for i in range(1, total_frames):
        if envelope[i] < envelope[i - 1] * decay:
            envelope[i] = envelope[i - 1] * decay
    
    return envelope
```

### Tunnel Effect Skeleton (Vectorized NumPy)

```python
# render/effects/tunnel.py
import numpy as np
from app.render.effects.base import BaseEffect
from app.render.effects import register

@register
class TunnelEffect(BaseEffect):
    name = "tunnel"
    
    def render_frame(self, t, width, height, params, beat_intensity, rng):
        # Create coordinate grid centered at (0,0)
        y_coords, x_coords = np.mgrid[-1:1:height*1j, -1:1:width*1j]
        
        # Polar coordinates
        radius = np.sqrt(x_coords**2 + y_coords**2) + 1e-6
        angle = np.arctan2(y_coords, x_coords)
        
        phase = t * 2 * np.pi
        twist = params.get("twist_speed", 0.5)
        ring_count = params.get("ring_count", 8)
        speed = params.get("speed", 0.5)
        
        # Tunnel depth illusion: modulate by 1/radius
        depth = 1.0 / radius
        tunnel_z = depth * ring_count + phase * speed
        tunnel_angle = angle + phase * twist
        
        # Color channels from tunnel coordinates
        r = (np.sin(tunnel_z) * 0.5 + 0.5)
        g = (np.sin(tunnel_angle * 3 + phase) * 0.5 + 0.5)
        b = (np.cos(tunnel_z + tunnel_angle) * 0.5 + 0.5)
        
        # Beat flash: brighten on beat
        flash = 1.0 + beat_intensity * 0.5
        
        frame = np.stack([r, g, b], axis=-1) * flash
        frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
        return frame
```

### Keyword Cluster Matching (Phase 1 prompt -> effect)

```python
# services/prompt_mapper.py
GENRE_CLUSTERS = {
    "techno": {
        "keywords": ["dark", "deep", "industrial", "techno", "warehouse", "minimal"],
        "effect": "tunnel",
        "palette": {"bg_color": "#0a0a0a", "primary_color": "#ff3333", "accent_color": "#ffffff"},
    },
    "psytrance": {
        "keywords": ["psychedelic", "trippy", "complex", "psy", "goa", "acid"],
        "effect": "fractal",
        "palette": {"bg_color": "#0a001a", "primary_color": "#ff00ff", "accent_color": "#00ffff"},
    },
    "house": {
        "keywords": ["house", "funky", "groove", "disco", "soulful", "warm"],
        "effect": "particles",
        "palette": {"bg_color": "#1a0a00", "primary_color": "#ffaa00", "accent_color": "#ff6600"},
    },
    "ambient": {
        "keywords": ["ambient", "chill", "dreamy", "ethereal", "calm", "space"],
        "effect": "plasma",
        "palette": {"bg_color": "#000a1a", "primary_color": "#3366ff", "accent_color": "#9933ff"},
    },
    "industrial": {
        "keywords": ["industrial", "harsh", "metal", "noise", "aggressive", "hard"],
        "effect": "tunnel",
        "palette": {"bg_color": "#0a0a0a", "primary_color": "#cc0000", "accent_color": "#333333"},
    },
}

def match_prompt(prompt: str) -> tuple[str, dict]:
    """Returns (effect_name, palette_dict). Falls back to tunnel with neutral palette."""
    prompt_lower = prompt.lower()
    best_genre = None
    best_score = 0
    for genre, config in GENRE_CLUSTERS.items():
        score = sum(1 for kw in config["keywords"] if kw in prompt_lower)
        if score > best_score:
            best_score = score
            best_genre = genre
    if best_genre:
        config = GENRE_CLUSTERS[best_genre]
        return config["effect"], config["palette"]
    # D-08: fallback to tunnel with neutral palette
    return "tunnel", {"bg_color": "#111111", "primary_color": "#4488ff", "accent_color": "#ffffff"}
```

### Pydantic RenderParams Schema (Phase 4 forward-compatible)

```python
# models/params.py
from pydantic import BaseModel, Field
from typing import Literal

class BaseRenderParams(BaseModel):
    """Shared params across all effects. Phase 1 populates via keyword matching."""
    bg_color: str = Field(default="#0a0a0a", pattern=r'^#[0-9a-fA-F]{6}$')
    primary_color: str = Field(default="#ff3333", pattern=r'^#[0-9a-fA-F]{6}$')
    accent_color: str = Field(default="#ffffff", pattern=r'^#[0-9a-fA-F]{6}$')
    intensity: float = Field(default=0.7, ge=0.0, le=1.0)
    speed: float = Field(default=0.5, ge=0.0, le=1.0)

class TunnelParams(BaseModel):
    twist_speed: float = Field(default=0.5, ge=0.0, le=2.0)
    ring_count: int = Field(default=8, ge=2, le=20)

class FractalParams(BaseModel):
    zoom_rate: float = Field(default=0.5, ge=0.1, le=2.0)
    c_param: float = Field(default=0.7885, ge=0.0, le=2.0)

class ParticlesParams(BaseModel):
    count: int = Field(default=100, ge=10, le=500)
    connection_dist: float = Field(default=0.15, ge=0.05, le=0.5)

class PlasmaParams(BaseModel):
    layer_count: int = Field(default=4, ge=2, le=8)
    wave_freq: float = Field(default=3.0, ge=1.0, le=10.0)

class RenderRequest(BaseModel):
    """API request model."""
    prompt: str = Field(..., min_length=1, max_length=500)
    bpm: int = Field(default=120, ge=60, le=200)
    resolution: Literal["480p", "1080p"] = "1080p"
    seed: int | None = Field(default=None, description="Random seed for reproducibility")

class RenderParams(BaseModel):
    """Full render params -- Phase 1 fills subset, Phase 4 fills all via LLM."""
    effect_type: str
    base: BaseRenderParams = BaseRenderParams()
    tunnel: TunnelParams | None = None
    fractal: FractalParams | None = None
    particles: ParticlesParams | None = None
    plasma: PlasmaParams | None = None
    bpm: int = 120
    resolution: Literal["480p", "1080p"] = "1080p"
    seed: int = 42
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| sse-starlette for FastAPI SSE | FastAPI built-in EventSourceResponse | FastAPI 0.135.0 (2026) | One fewer dependency; native integration with FastAPI typing |
| cv2.VideoWriter for mp4 | ffmpeg subprocess pipe | Always best practice | Cross-browser H.264/yuv420p compatibility |
| Pydantic v1 | Pydantic v2 | 2023 | FastAPI 0.100+ requires v2; different validator syntax |
| asyncio.to_thread for CPU work | ProcessPoolExecutor | Always best practice for NumPy | True GIL isolation |

**Deprecated/outdated:**
- `sse-starlette`: Still works but redundant with FastAPI 0.135+
- `cv2.VideoWriter` for web video: Produces wrong codec for Safari
- Pydantic v1 `@validator`: Replaced by v2 `@field_validator`

## Open Questions

1. **Particle system seamless looping strategy**
   - What we know: Tunnel, fractal, and plasma are pure functions of phase (t). Particles are simulation-based.
   - What's unclear: Best approach to make particle trajectories loop seamlessly without visible discontinuity.
   - Recommendation: Pre-compute full particle trajectories as closed curves (e.g., Lissajous figures parameterized by t). Each particle follows a deterministic cyclic path. More constrained visually but guarantees seamless loop.

2. **multiprocessing.Value pickling with ProcessPoolExecutor**
   - What we know: multiprocessing.Value works with fork-based multiprocessing. macOS defaults to "spawn" since Python 3.8.
   - What's unclear: Whether Value is picklable for spawn-based ProcessPoolExecutor on macOS.
   - Recommendation: Test early. Fallback: use multiprocessing.Manager().Value() which works across spawn, or use a file-based progress mechanism. Alternative: use `multiprocessing.Process` directly instead of ProcessPoolExecutor for more control over the shared state.

3. **ffmpeg pipe buffer size for 1080p**
   - What we know: Each 1080p RGB frame is 1920*1080*3 = ~6MB written to stdin.
   - What's unclear: Whether default pipe buffer can handle this throughput without blocking.
   - Recommendation: ffmpeg reads stdin continuously. The OS pipe buffer (typically 64KB-1MB) will cause the write to block briefly while ffmpeg processes, which is fine -- it acts as natural backpressure. No action needed, but monitor for hangs.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime | Yes | 3.13.1 | -- |
| ffmpeg | Video encoding (RND-02) | Yes | 7.1.1 | -- |
| uv | Package management | Yes | 0.6.9 | pip3 24.3.1 also available |
| git | Version control | Yes | 2.50.1 | -- |
| Node.js | Not needed Phase 1 | Yes | 20.17.0 | -- |

**Missing dependencies with no fallback:** None -- all required tools are installed.

**Missing dependencies with fallback:** None.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| Config file | None -- Wave 0 creates pyproject.toml [tool.pytest.ini_options] |
| Quick run command | `cd backend && uv run pytest tests/ -x --timeout=30` |
| Full suite command | `cd backend && uv run pytest tests/ -v --timeout=120` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INP-01 | POST /generate accepts prompt, returns job_id | integration | `pytest tests/test_api.py::test_generate_returns_job_id -x` | Wave 0 |
| INP-02 | POST /generate validates BPM 60-200 | unit | `pytest tests/test_api.py::test_bpm_validation -x` | Wave 0 |
| VFX-01 | Tunnel effect renders without error | unit | `pytest tests/test_effects.py::test_tunnel_renders -x` | Wave 0 |
| VFX-02 | Fractal effect renders without error | unit | `pytest tests/test_effects.py::test_fractal_renders -x` | Wave 0 |
| VFX-03 | Particles effect renders without error | unit | `pytest tests/test_effects.py::test_particles_renders -x` | Wave 0 |
| VFX-04 | Plasma effect renders without error | unit | `pytest tests/test_effects.py::test_plasma_renders -x` | Wave 0 |
| RND-01 | Seamless loop: frame[0] ~ frame[N-1] | unit | `pytest tests/test_seamless.py -x` | Wave 0 |
| RND-02 | Output is H.264/yuv420p (ffprobe check) | integration | `pytest tests/test_encoder.py::test_output_codec -x` | Wave 0 |
| RND-03 | SSE streams progress 0->100 | integration | `pytest tests/test_api.py::test_sse_progress -x` | Wave 0 |
| RND-04 | Health endpoint responds <1s during render | integration | `pytest tests/test_api.py::test_health_during_render -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `cd backend && uv run pytest tests/ -x --timeout=30`
- **Per wave merge:** `cd backend && uv run pytest tests/ -v --timeout=120`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `backend/pyproject.toml` -- project config with [tool.pytest.ini_options]
- [ ] `backend/tests/conftest.py` -- shared fixtures (FastAPI test client, temp render dir)
- [ ] `backend/tests/test_api.py` -- endpoint tests for INP-01, INP-02, RND-03, RND-04
- [ ] `backend/tests/test_effects.py` -- renders each effect at 480p, asserts shape + dtype
- [ ] `backend/tests/test_seamless.py` -- pixel diff test per effect
- [ ] `backend/tests/test_encoder.py` -- ffprobe validates H.264 output
- [ ] `backend/tests/test_loop_math.py` -- frame count and phase calculations
- [ ] `backend/tests/test_prompt_mapper.py` -- keyword matching correctness
- [ ] Framework install: `uv add --dev pytest pytest-asyncio httpx`

## Sources

### Primary (HIGH confidence)
- [FastAPI SSE documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/) -- EventSourceResponse built into FastAPI 0.135.0+
- PyPI version registry (pip3 index versions) -- all version numbers verified 2026-04-01
- [NumPy news](https://numpy.org/news/) -- NumPy 2.4.x supports Python 3.13
- [Python multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html) -- Value, ProcessPoolExecutor patterns

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md` -- project stack research (training-data based, versions now verified)
- `.planning/research/ARCHITECTURE.md` -- project architecture patterns
- `.planning/research/PITFALLS.md` -- domain pitfalls catalogue
- [GeeksforGeeks: Multiprocessing in FastAPI](https://www.geeksforgeeks.org/python/multiprocessing-in-fastapi/) -- ProcessPoolExecutor + FastAPI patterns
- [Super Fast Python: ProcessPoolExecutor progress](https://superfastpython.com/processpoolexecutor-show-progress/) -- progress reporting patterns

### Tertiary (LOW confidence)
- Tunnel/fractal/particles/plasma math -- based on training data knowledge of procedural graphics. Implementations must be tested empirically for visual quality.
- multiprocessing.Value with spawn on macOS -- needs empirical verification (see Open Questions #2)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all versions verified against PyPI, FastAPI SSE confirmed via official docs
- Architecture: HIGH -- patterns are well-established (ProcessPoolExecutor, ffmpeg pipe, effect registry)
- Pitfalls: HIGH -- GIL blocking, loop math, codec issues are well-documented domain problems
- Effect implementations: MEDIUM -- math patterns from training data, need visual testing
- ProcessPoolExecutor + multiprocessing.Value on macOS spawn: LOW -- needs empirical test

**Research date:** 2026-04-01
**Valid until:** 2026-05-01 (stable domain, no fast-moving dependencies)
