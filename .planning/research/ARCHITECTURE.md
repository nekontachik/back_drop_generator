# Architecture Research

**Domain:** AI-powered music-reactive video backdrop generation
**Researched:** 2026-04-01
**Confidence:** MEDIUM (patterns are well-established; specific library integration APIs need verification)

## System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js on Vercel)                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │ Gallery  │  │ Generate │  │ Progress  │  │ Result/Player    │   │
│  │ Page     │  │ Form     │  │ View      │  │ + Download       │   │
│  └──────────┘  └────┬─────┘  └─────┬─────┘  └──────────────────┘   │
│                     │  POST         │ SSE EventSource                │
├─────────────────────┼──────────────┼────────────────────────────────┤
│                     ▼              ▼                                 │
│              BACKEND (FastAPI on Railway/Render)                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     API Layer (FastAPI)                       │   │
│  │  POST /generate  GET /progress/{id}  GET /videos/{id}        │   │
│  └────────┬─────────────────┬───────────────────┬──────────────┘   │
│           │                 │                   │                    │
│  ┌────────▼────────┐  ┌────▼──────┐  ┌────────▼───────────────┐   │
│  │  Job Manager    │  │  Progress │  │  Static File Serving   │   │
│  │  (enqueue +     │  │  Store    │  │  (rendered videos)     │   │
│  │   track jobs)   │  │  (Redis   │  │                        │   │
│  └────────┬────────┘  │  or dict) │  └────────────────────────┘   │
│           │           └───────────┘                                 │
│  ┌────────▼────────────────────────────────────────────────────┐   │
│  │                 RENDER WORKER (separate process)             │   │
│  │                                                              │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐  │   │
│  │  │  Audio    │  │  RAG      │  │  LLM      │  │  Video  │  │   │
│  │  │  Analyzer │→ │  Retriever│→ │  Blender  │→ │  Render │  │   │
│  │  │ (librosa) │  │ (ChromaDB)│  │(LangChain)│  │ (NumPy+ │  │   │
│  │  └───────────┘  └───────────┘  └───────────┘  │  OpenCV)│  │   │
│  │                                                └─────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    DATA STORES                               │   │
│  │  ┌───────────┐  ┌──────────────┐  ┌─────────────────────┐  │   │
│  │  │  ChromaDB │  │  File System │  │  Redis (optional)   │  │   │
│  │  │  (styles) │  │  (videos +   │  │  (job queue +       │  │   │
│  │  │           │  │   uploads)   │  │   progress pub/sub) │  │   │
│  │  └───────────┘  └──────────────┘  └─────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Gallery Page | Display pre-generated example backdrops; landing page hook | Next.js Server Component, static data or fetched from backend |
| Generate Form | Collect text prompt, optional audio upload, manual BPM | Client Component with react-dropzone, form validation |
| Progress View | Show render progress in real-time | EventSource SSE connection to backend |
| Result/Player | Display finished video with player, BPM chart, download | Native `<video>` element, download link |
| API Layer | Route requests, validate input, manage CORS | FastAPI with Pydantic models |
| Job Manager | Create render jobs, track state, enqueue to worker | In-memory dict (MVP) or ARQ + Redis (production) |
| Progress Store | Store and broadcast render progress (0-100%) | In-memory dict with SSE polling, or Redis pub/sub |
| Audio Analyzer | Extract BPM, beat timestamps, energy envelope from audio | librosa: beat_track, onset_strength, spectral_centroid |
| RAG Retriever | Match user prompt + genre to style documents | ChromaDB embedded + sentence-transformers embeddings |
| LLM Blender | Creatively combine retrieved style params into render config | LangChain LCEL chain with structured JSON output |
| Video Renderer | Generate frames and encode to seamless mp4 loop | NumPy array generation + cv2.VideoWriter or ffmpeg pipe |
| Static File Serving | Serve rendered videos and pre-generated examples | FastAPI StaticFiles mount or Nginx in production |

## Recommended Project Structure

```
beat-visuals/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app, CORS, lifespan, static mounts
│   │   ├── config.py               # Pydantic Settings (env vars, paths)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── generate.py     # POST /generate, GET /progress/{id}
│   │   │   │   ├── gallery.py      # GET /gallery (list pre-generated)
│   │   │   │   └── videos.py       # GET /videos/{id} (serve video files)
│   │   │   └── deps.py             # Shared dependencies (ChromaDB client, etc.)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── audio.py            # librosa analysis: BPM, beats, energy
│   │   │   ├── rag.py              # ChromaDB retriever, embedding setup
│   │   │   ├── llm.py              # LangChain chain: prompt + parse JSON output
│   │   │   └── models.py           # Pydantic models: RenderParams, JobStatus, etc.
│   │   ├── render/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py         # Orchestrate: analyze -> retrieve -> blend -> render
│   │   │   ├── effects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py         # Abstract base effect class
│   │   │   │   ├── tunnel.py       # 3D tunnel effect
│   │   │   │   ├── fractal.py      # Julia fractal
│   │   │   │   ├── particles.py    # Particle system
│   │   │   │   ├── grid.py         # Perspective grid
│   │   │   │   ├── plasma.py       # Plasma waves
│   │   │   │   └── glitch.py       # Glitch/scanlines
│   │   │   ├── composer.py         # Layer/blend multiple effects per frame
│   │   │   └── encoder.py          # Frame array -> mp4 file (cv2/ffmpeg)
│   │   ├── worker.py               # ARQ worker definition (or BackgroundTasks fallback)
│   │   └── jobs.py                 # Job state management, progress tracking
│   ├── knowledge/
│   │   ├── styles/
│   │   │   ├── techno.md           # Genre style document
│   │   │   ├── house.md
│   │   │   ├── ambient.md
│   │   │   ├── industrial.md
│   │   │   └── psytrance.md
│   │   └── seed_db.py              # Script to load style docs into ChromaDB
│   ├── data/
│   │   ├── chromadb/               # ChromaDB persistent storage
│   │   ├── uploads/                # Temporary audio uploads
│   │   ├── renders/                # Output video files
│   │   └── gallery/                # Pre-generated example videos
│   ├── tests/
│   │   ├── test_audio.py
│   │   ├── test_rag.py
│   │   ├── test_llm.py
│   │   ├── test_render.py
│   │   └── test_api.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing page with gallery
│   │   │   ├── generate/
│   │   │   │   └── page.tsx        # Generate form
│   │   │   ├── result/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx    # Progress + result view
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── gallery-grid.tsx
│   │   │   ├── generate-form.tsx
│   │   │   ├── audio-upload.tsx
│   │   │   ├── progress-bar.tsx
│   │   │   ├── video-player.tsx
│   │   │   └── bpm-chart.tsx
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   └── types.ts            # Shared TypeScript types
│   │   └── hooks/
│   │       └── use-render-progress.ts  # SSE hook
│   ├── public/
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
└── docker-compose.yml              # Backend + Redis (dev environment)
```

### Structure Rationale

- **backend/app/core/:** Isolated domain logic (audio, RAG, LLM) with no HTTP dependencies. Each module is independently testable. This is the "business logic" layer.
- **backend/app/render/:** Separated from core because rendering is the CPU-intensive hot path. The pipeline module orchestrates core modules. Effects are pluggable via a base class pattern.
- **backend/app/api/:** Thin HTTP layer. Routes call core/render modules. No business logic in route handlers.
- **backend/knowledge/:** Style documents live alongside code but outside the app package. Treated as data, not code. seed_db.py is a one-time setup script.
- **backend/data/:** Runtime data (uploads, renders, ChromaDB storage). Gitignored except for gallery pre-generated examples.
- **frontend/src/hooks/:** Custom hooks encapsulate SSE connection logic, keeping components clean.

## Architectural Patterns

### Pattern 1: Async Job Queue with Progress Reporting

**What:** Client submits a render request, receives a job ID immediately, then subscribes to progress updates via SSE. The actual render runs in a separate worker process (or background thread for MVP).

**When to use:** Any operation taking more than a few seconds. Video rendering takes 1-3 minutes.

**Trade-offs:** Adds complexity (job state management, worker process) but is essential for UX. Without it, HTTP requests timeout and users get no feedback.

**Implementation (two tiers):**

```python
# === Tier 1: MVP (no Redis, single process) ===
# backend/app/jobs.py
import asyncio
from uuid import uuid4
from pydantic import BaseModel
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    RETRIEVING = "retrieving"
    BLENDING = "blending"
    RENDERING = "rendering"
    ENCODING = "encoding"
    COMPLETE = "complete"
    FAILED = "failed"

class JobState(BaseModel):
    id: str
    status: JobStatus
    progress: float = 0.0  # 0-100
    stage_detail: str = ""
    result_url: str | None = None
    error: str | None = None

# In-memory store (fine for single-instance portfolio demo)
_jobs: dict[str, JobState] = {}

def create_job() -> JobState:
    job = JobState(id=str(uuid4()), status=JobStatus.PENDING)
    _jobs[job.id] = job
    return job

def update_job(job_id: str, **kwargs) -> None:
    if job_id in _jobs:
        for k, v in kwargs.items():
            setattr(_jobs[job_id], k, v)

def get_job(job_id: str) -> JobState | None:
    return _jobs.get(job_id)
```

```python
# === Tier 1: FastAPI route with BackgroundTasks ===
# backend/app/api/routes/generate.py
import asyncio
from fastapi import APIRouter, BackgroundTasks, UploadFile, Form
from fastapi.responses import StreamingResponse
from app.jobs import create_job, get_job, update_job, JobStatus

router = APIRouter()

@router.post("/generate")
async def generate(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    bpm: int | None = Form(None),
    audio: UploadFile | None = None,
):
    job = create_job()
    background_tasks.add_task(run_pipeline, job.id, prompt, bpm, audio)
    return {"job_id": job.id}

async def run_pipeline(job_id: str, prompt: str, bpm: int | None, audio):
    """Runs in background thread via asyncio.to_thread for CPU-bound work."""
    # Each stage updates progress -- see Data Flow section below
    ...

@router.get("/progress/{job_id}")
async def progress_stream(job_id: str):
    """SSE endpoint streaming progress updates."""
    async def event_generator():
        while True:
            job = get_job(job_id)
            if not job:
                yield f"event: error\ndata: Job not found\n\n"
                return
            yield f"data: {job.model_dump_json()}\n\n"
            if job.status in (JobStatus.COMPLETE, JobStatus.FAILED):
                return
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

```python
# === Tier 2: ARQ + Redis (production) ===
# backend/app/worker.py
from arq import create_pool
from arq.connections import RedisSettings
from app.render.pipeline import render_pipeline

async def render_job(ctx, job_id: str, prompt: str, bpm: int | None,
                     audio_path: str | None):
    redis = ctx["redis"]
    await render_pipeline(job_id, prompt, bpm, audio_path,
                          progress_callback=redis)

class WorkerSettings:
    functions = [render_job]
    redis_settings = RedisSettings()
    max_jobs = 1  # CPU-bound, one at a time
    job_timeout = 300  # 5 minute max
```

### Pattern 2: RAG Retrieval with Structured LLM Output

**What:** User prompt + detected genre retrieves relevant style documents from ChromaDB. Retrieved docs are injected into an LLM prompt that produces a structured JSON parameter set for the video renderer.

**When to use:** Every render request. The RAG + LLM chain is the "creative brain" of the system.

**Trade-offs:** Adds LLM API latency (~1-3s) and cost (~$0.001/request with GPT-4o-mini). Benefit: creative parameter combinations that a rules engine cannot produce. Fallback mode with deterministic defaults handles API failures.

```python
# backend/app/core/rag.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

def get_retriever():
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./data/chromadb")
    collection = client.get_or_create_collection("styles", embedding_function=ef)
    return collection

def retrieve_styles(collection, query: str, n_results: int = 3) -> list[str]:
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]
```

```python
# backend/app/core/llm.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.models import RenderParams

BLEND_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a visual designer for music-reactive video backdrops.
Given style reference documents and a user's creative prompt, output a JSON
parameter set for the video renderer.

You MUST output valid JSON matching this schema:
{schema}

Style references:
{style_docs}

Audio analysis:
- BPM: {bpm}
- Energy profile: {energy_profile}
"""),
    ("human", "{user_prompt}"),
])

def create_blend_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)
    parser = JsonOutputParser(pydantic_object=RenderParams)
    chain = BLEND_PROMPT | llm | parser
    return chain
```

```python
# backend/app/core/models.py
from pydantic import BaseModel, Field

class ColorPalette(BaseModel):
    primary: str = Field(description="Hex color, e.g. #FF00FF")
    secondary: str
    accent: str
    background: str

class RenderParams(BaseModel):
    """Parameters the LLM produces for the video renderer."""
    effect_type: str = Field(
        description="One of: tunnel, fractal, particles, grid, plasma, glitch"
    )
    color_palette: ColorPalette
    movement_speed: float = Field(ge=0.1, le=5.0,
                                   description="Base movement multiplier")
    beat_reactivity: float = Field(ge=0.0, le=1.0,
                                    description="How much beats affect visuals")
    complexity: float = Field(ge=0.1, le=1.0,
                               description="Detail level of the effect")
    glow_intensity: float = Field(ge=0.0, le=1.0)
    secondary_effect: str | None = Field(
        default=None, description="Optional overlay effect"
    )
    creative_notes: str = Field(
        description="Brief description of the visual mood"
    )
```

### Pattern 3: Seamless Loop Video Rendering

**What:** Generate N frames as NumPy arrays where frame[N-1] visually connects back to frame[0]. Encode to mp4 with ffmpeg subprocess pipe.

**When to use:** Every render. Seamless looping is a core product requirement.

**Trade-offs:** Constrains effect design (all effects must support cyclic parameterization). Worth it for professional quality output.

**Seamless loop technique:**

```python
# backend/app/render/pipeline.py
import numpy as np

def calculate_loop_params(bpm: int, fps: int = 30, max_duration: float = 30.0):
    """Calculate frame count for perfect beat-aligned loop."""
    beat_period = 60.0 / bpm  # seconds per beat
    # Find number of beats that fits close to desired duration
    # Must be multiple of 4 for musical phrasing
    beats_in_loop = max(4, round(max_duration / beat_period / 4) * 4)
    loop_duration = beats_in_loop * beat_period
    total_frames = int(loop_duration * fps)
    return total_frames, loop_duration, beats_in_loop

def render_frame(effect, t: float, loop_duration: float, params,
                 beat_times: list[float], energy: float) -> np.ndarray:
    """
    Render single frame.
    t is normalized [0, 1) through the loop cycle.
    All effect parameters use cyclic functions of t:
    sin(2*pi*t), cos(2*pi*t) ensure seamless wrapping.
    """
    phase = t * 2 * np.pi
    frame = effect.render(phase, params, energy)
    return frame  # shape: (1080, 1920, 3), dtype: uint8
```

```python
# backend/app/render/encoder.py
import subprocess
import numpy as np

def encode_with_ffmpeg(frames_iter, output_path: str, fps: int = 30,
                       width: int = 1920, height: int = 1080):
    """
    Pipe frames to ffmpeg -- H.264 codec, small files, web-compatible.
    Frames are piped one at a time to avoid holding all in memory.
    """
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}", "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "23", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",  # enables progressive download
        output_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for frame in frames_iter:
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.read().decode()}")
```

### Pattern 4: Effect Plugin Architecture

**What:** Each visual effect implements a common interface. The pipeline selects and composes effects based on LLM output.

**When to use:** Whenever adding new visual effects. Keeps render pipeline decoupled from specific effects.

**Trade-offs:** Slight over-engineering for 6 effects, but essential for maintainability and portfolio presentation (demonstrates good software design).

```python
# backend/app/render/effects/base.py
from abc import ABC, abstractmethod
import numpy as np
from app.core.models import RenderParams

class BaseEffect(ABC):
    """All visual effects implement this interface."""

    @abstractmethod
    def render(self, phase: float, params: RenderParams,
               energy: float, beat_pulse: float) -> np.ndarray:
        """
        Render a single frame.

        Args:
            phase: Cyclic phase [0, 2*pi) through the loop
            params: LLM-generated render parameters
            energy: Audio energy at this moment [0, 1]
            beat_pulse: Beat intensity at this moment [0, 1]

        Returns:
            Frame as (height, width, 3) uint8 RGB array
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Effect identifier matching RenderParams.effect_type."""
        ...

# Registry
EFFECT_REGISTRY: dict[str, type[BaseEffect]] = {}

def register_effect(cls: type[BaseEffect]) -> type[BaseEffect]:
    instance = cls()
    EFFECT_REGISTRY[instance.name] = cls
    return cls
```

### Pattern 5: Beat-Sync Envelope Mapping

**What:** Map librosa beat timestamps to a per-frame "beat intensity" array that peaks at each beat and decays exponentially. This drives visual reactivity.

**When to use:** Connecting audio analysis to rendering. Every effect reads from this envelope.

```python
# backend/app/core/audio.py
import numpy as np
import librosa

def analyze_audio(file_path: str, sr: int = 22050):
    y, sr = librosa.load(file_path, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # Normalize onset envelope to [0, 1]
    onset_env = onset_env / (onset_env.max() + 1e-6)
    return {
        "bpm": float(tempo),
        "beat_times": beat_times.tolist(),
        "onset_envelope": onset_env.tolist(),
    }

def build_beat_envelope(beat_times: list[float], total_frames: int,
                        fps: int = 30, decay: float = 0.85) -> np.ndarray:
    """Create per-frame beat intensity: peaks at beats, exponential decay."""
    envelope = np.zeros(total_frames)
    for bt in beat_times:
        frame_idx = int(bt * fps)
        if 0 <= frame_idx < total_frames:
            envelope[frame_idx] = 1.0
    # Forward pass: exponential decay
    for i in range(1, total_frames):
        if envelope[i] < envelope[i - 1] * decay:
            envelope[i] = envelope[i - 1] * decay
    return envelope
```

## Data Flow

### Primary Flow: Generate Request

```
User fills form (prompt + optional audio + optional BPM)
    |
    v
[Frontend] POST /generate (multipart: prompt, bpm, audio file)
    |
    v
[API Layer] Validates input via Pydantic
    | Creates job (status=PENDING), returns job_id
    | Saves uploaded audio to data/uploads/{job_id}.wav
    | Enqueues render task (BackgroundTasks or ARQ)
    |
    v
[Frontend] Opens SSE: GET /progress/{job_id}
    | Renders progress bar, updates on each event
    |
    v (in worker process)
[Audio Analyzer] -- status=ANALYZING, progress=10%
    | librosa.beat.beat_track() -> tempo, beat_frames
    | librosa.onset.onset_strength() -> energy_envelope
    | Output: AudioAnalysis(bpm, beat_times, energy_curve)
    |
    v
[RAG Retriever] -- status=RETRIEVING, progress=25%
    | ChromaDB.query(user_prompt, n_results=3)
    | Output: list[str] (style document contents)
    |
    v
[LLM Blender] -- status=BLENDING, progress=35%
    | LangChain chain: style_docs + prompt + audio_analysis -> RenderParams JSON
    | Validate with Pydantic (retry once if invalid)
    | Output: RenderParams
    |
    v
[Video Renderer] -- status=RENDERING, progress=40-90%
    | Calculate loop params (beat-aligned frame count)
    | For each frame:
    |   compute phase = frame_idx / total_frames
    |   lookup energy + beat_pulse at this timestamp
    |   effect.render(phase, params, energy, beat_pulse) -> frame array
    |   Pipe frame to ffmpeg stdin
    |   Progress = 40 + (frame_idx / total_frames * 50)
    |
    v
[Encoder] -- status=ENCODING, progress=90-98%
    | ffmpeg finishes encoding (close stdin, wait for process)
    | Output: data/renders/{job_id}.mp4
    |
    v
[Job Complete] -- status=COMPLETE, progress=100%
    | result_url = /videos/{job_id}.mp4
    |
    v
[Frontend] SSE receives COMPLETE event
    | Navigates to /result/{job_id}
    | Shows video player + download button
```

### Secondary Flow: Gallery (Pre-generated)

```
[Build time / admin script]
    | Pre-render 6-10 example videos with curated prompts
    | Store in data/gallery/ with metadata JSON
    |
    v
[Frontend] GET /gallery
    | Returns list of { id, title, genre, bpm, thumbnail_url, video_url }
    |
    v
[Gallery Page] Renders grid of video thumbnails
    | Click -> plays inline or navigates to detail view
```

### SSE Progress Communication Detail

```
Frontend (EventSource)              Backend (SSE endpoint)
    |                                    |
    | -- GET /progress/{id} ---------->  |
    |                                    | Check job state
    |  <-- data: {"status":"analyzing",  |
    |           "progress":10} --------  |
    |                                    | (500ms later)
    |  <-- data: {"status":"rendering",  |
    |           "progress":55} --------  |
    |                                    |
    |  <-- data: {"status":"complete",   |
    |           "progress":100,          |
    |           "result_url":"..."} --   |
    |                                    |
    | -- (connection closes) ----------  |
```

### Key Data Flows

1. **Audio to Analysis:** Audio file (wav) passes through librosa, producing structured data (BPM, beat timestamps as float array, energy envelope as float array). Pure computation, no I/O after initial file read. Completes in under 1 second for 30-60s clips.

2. **Analysis + Prompt to Parameters:** The RAG retriever and LLM blender transform unstructured input (text prompt, genre) into a structured RenderParams object. This is the "AI" core of the system. Latency: 1-3 seconds (dominated by LLM API call).

3. **Parameters to Frames to Video:** RenderParams drives the frame generator. Each frame is a pure function of (phase, params, energy, beat_pulse) -- no state between frames except the cyclic phase. Frames are piped directly to ffmpeg, never stored in memory as a list. Peak memory: 1 frame (~6MB) + ffmpeg buffer. Latency: 1-3 minutes for 30s at 1080p 30fps.

4. **Progress to Frontend:** Progress updates flow from the worker (who knows the current render stage) through the progress store (dict or Redis) to the SSE endpoint, which the frontend consumes via EventSource. Updates every 500ms.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-5 concurrent users (portfolio) | Single process, in-memory job store, local filesystem. BackgroundTasks with asyncio.to_thread(). This is the MVP target. |
| 5-50 concurrent users | Add Redis + ARQ. Separate worker process. Add job timeout and cleanup cron. Still local filesystem for videos. |
| 50+ concurrent users | Multiple ARQ workers. S3/R2 for video storage. CDN for serving. Rate limiting. Job priority queue. Database for job metadata. |

### Scaling Priorities

1. **First bottleneck: CPU saturation.** One render takes 1-3 minutes of CPU. With BackgroundTasks, the second render queues behind the first. Solution: ARQ worker with `max_jobs=1` and visible queue position in the UI. For the portfolio demo, showing "You are #2 in queue" is acceptable and honest.

2. **Second bottleneck: Disk space.** Each 30s 1080p H.264 video is ~5-15MB. At 100 renders, that is 0.5-1.5GB. Solution: cleanup job that deletes renders older than 24 hours. Pre-generated gallery examples are permanent.

3. **Third bottleneck: LLM API costs.** At ~$0.001/request with GPT-4o-mini, this only matters at high volume. Solution: cache LLM responses keyed on (prompt_hash, bpm_bucket, top_style_docs_hash). Most demo visitors will try similar prompts.

## Anti-Patterns

### Anti-Pattern 1: LLM Generates Code Instead of Parameters

**What people do:** Ask the LLM to write Python code for the visual effect, then exec() it.
**Why it's wrong:** Security nightmare (arbitrary code execution). Unpredictable output. Hard to validate. The LLM is not a reliable NumPy programmer.
**Do this instead:** LLM outputs a structured JSON parameter set (RenderParams). All rendering code is pre-written and tested. The LLM is a "creative director" choosing parameters, not a "programmer" writing code.

### Anti-Pattern 2: Rendering in the Request Handler

**What people do:** Put the render loop directly in the POST /generate handler.
**Why it's wrong:** HTTP connections timeout (typically 30-60s on reverse proxies). Even if the server does not timeout, the client has no progress feedback. The user stares at a spinner for 3 minutes.
**Do this instead:** Return job_id immediately. Render in background. Stream progress via SSE.

### Anti-Pattern 3: Storing All Frames in Memory

**What people do:** Generate all 900 frames (30s * 30fps) as a list of NumPy arrays, then encode.
**Why it's wrong:** Each 1080p frame is ~6MB (1920*1080*3 bytes). 900 frames = ~5.4GB RAM. Server will OOM.
**Do this instead:** Generate frames one at a time, pipe directly to ffmpeg stdin. Peak memory = 1 frame (~6MB) + ffmpeg buffer.

### Anti-Pattern 4: Non-Cyclic Effect Parameters (Fake Looping)

**What people do:** Use linear time (t from 0 to duration) for effect parameters, then try to crossfade the last few frames to match the first.
**Why it's wrong:** Crossfade-based looping creates visible artifacts (ghosting, double exposure). It never looks truly seamless.
**Do this instead:** All effect parameters must be functions of sin(2*pi*t/loop_duration) or cos(2*pi*t/loop_duration). When t wraps from end to start, the math is inherently continuous. Design every effect around cyclic phase, not linear time.

### Anti-Pattern 5: Over-Abstracted Effect Pipeline

**What people do:** Build a complex node-graph / compositor system for effects before writing a single effect.
**Why it's wrong:** Premature abstraction for a portfolio project. YAGNI for 6 effects.
**Do this instead:** Simple effect registry with render() interface. Compose effects by alpha-blending their output arrays. Add abstraction only when the 6th effect reveals a pattern the base class does not cover.

### Anti-Pattern 6: Storing Videos in a Database

**What people do:** Put rendered mp4 files in PostgreSQL or similar.
**Why it's wrong:** Wastes database resources, slow retrieval, unnecessary complexity.
**Do this instead:** Store on local filesystem. Serve via FastAPI FileResponse or StaticFiles mount. Move to S3/R2 only if scaling beyond a single server.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI API (GPT-4o-mini) | LangChain ChatOpenAI, async | API key via env var. Implement fallback to deterministic defaults if API fails or key is missing. Cache responses by input hash. |
| Vercel (frontend hosting) | Git push deploys | Free tier. Configure rewrites for API proxy or use CORS on FastAPI. |
| Railway/Render (backend hosting) | Docker image deploy | Needs ffmpeg in Docker image. Persistent volume for data/ directory. Single dyno/container. |
| Redis (optional) | ARQ connection, pub/sub | Railway Redis add-on. Skip entirely for MVP; use in-memory fallback. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend <-> API Layer | HTTP REST + SSE | CORS configured on FastAPI. Multipart upload for audio. JSON for everything else. SSE for progress. |
| API Layer <-> Worker | In-memory dict (MVP) or Redis/ARQ (production) | Job state is the shared contract. Worker writes progress; API reads and streams it. |
| Worker <-> Core Modules | Direct Python function calls | audio.analyze(), rag.retrieve(), llm.blend() are plain functions. No network boundary. |
| Worker <-> File System | Local disk reads/writes | Uploads read from data/uploads/. Renders written to data/renders/. Cleanup cron deletes old files. |
| Core <-> ChromaDB | ChromaDB Python client (in-process) | No network hop. SQLite-backed. Loaded once at startup, queried per request. |

## Build Order (Dependencies)

The system has clear dependency chains that dictate phase ordering:

```
Phase 1: Core Rendering (no AI needed)
    Effect base class + 1-2 effects (tunnel, fractal)
    Frame -> mp4 encoder (ffmpeg pipe)
    Seamless loop math (cyclic phase)
    Can demo: hardcoded params -> video file via CLI script

Phase 2: Audio Analysis
    librosa integration (BPM, beats, energy)
    Beat envelope mapping
    Can demo: audio file -> beat-synced video with hardcoded style

Phase 3: RAG + LLM Pipeline
    ChromaDB setup + style documents authored
    LangChain chain (retrieve -> blend -> RenderParams)
    LLM fallback mode (deterministic defaults)
    Can demo: prompt + audio -> AI-parameterized video via CLI

Phase 4: API Layer + Job Management
    FastAPI endpoints (generate, progress, videos, gallery)
    Background task execution with progress tracking
    SSE progress streaming
    File upload handling
    Can demo: curl/Postman -> submit job -> poll progress -> download video

Phase 5: Frontend
    Next.js app with gallery, generate form, progress view, result player
    SSE hook for real-time progress
    Audio upload with drag-and-drop
    Can demo: full user flow in browser

Phase 6: Polish + Deploy
    Pre-generate gallery examples (6-10 curated videos)
    Docker containerization (backend + ffmpeg)
    Deploy to Vercel (frontend) + Railway (backend)
    Error handling, input validation edge cases, cleanup cron
    Rate limiting if exposing publicly
```

**Why this order:**
- Phases 1-3 build the core pipeline bottom-up. Each phase is independently testable with CLI scripts before any HTTP layer exists.
- Phase 4 wraps the pipeline in HTTP. Cannot build meaningful API tests without the pipeline existing.
- Phase 5 is UI over the API. Cannot build this without the API existing.
- Phase 6 is integration and deployment. Requires everything else working.

**Key insight:** The render pipeline (Phases 1-3) represents ~70% of the technical complexity. The API and frontend are relatively straightforward wrappers. Invest the most design and testing time in the rendering and AI pipeline. The first three phases can all be validated with simple Python scripts before touching HTTP or React.

## Sources

- FastAPI background tasks and SSE patterns: based on FastAPI documentation patterns and established async Python architecture (MEDIUM confidence -- verify SSE response headers with current FastAPI docs)
- ARQ task queue patterns: based on ARQ library design (MEDIUM confidence -- verify ARQ is actively maintained before adopting)
- ChromaDB embedded mode: well-documented pattern for small knowledge bases (MEDIUM confidence -- verify current Python API, especially embedding function interface)
- LangChain LCEL chain composition: based on LangChain 0.3.x patterns (LOW confidence -- LangChain API changes frequently, verify current chain and output parser syntax)
- NumPy + ffmpeg pipe rendering: established pattern for programmatic video generation (HIGH confidence -- stable approach, no library API dependency)
- Seamless loop via cyclic phase: standard technique in procedural animation (HIGH confidence -- pure math, no library dependency)
- SSE via EventSource: web standard, well-supported in all browsers (HIGH confidence)
- Beat envelope mapping with librosa: standard MIR pattern (HIGH confidence -- librosa API is stable)

---
*Architecture research for: AI-powered music-reactive video backdrop generation*
*Researched: 2026-04-01*
