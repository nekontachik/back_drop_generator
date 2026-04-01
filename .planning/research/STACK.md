# Stack Research

**Domain:** AI-powered music-reactive video backdrop generation
**Researched:** 2026-04-01
**Confidence:** MEDIUM (versions from training data -- verify with `pip index versions <pkg>` before pinning)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | Backend language | 3.11 has significant performance gains; 3.12+ fine but verify library compat |
| FastAPI | ~0.115+ | API framework | Async-native, automatic OpenAPI docs, background task support, best Python API framework for this use case |
| Next.js | 14.x or 15.x | Frontend framework | App Router with Server Components, good streaming/SSE support, Vercel deployment is free tier |
| TypeScript | 5.x | Frontend language | Type safety, better DX, expected in portfolio projects |

### Video Rendering Pipeline

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| NumPy | ~2.0+ | Frame-level math | Core of all per-pixel computation -- fractals, particles, tunnel math all reduce to NumPy array ops |
| OpenCV (cv2) | ~4.10+ | Frame compositing + video encoding | Fast image manipulation, VideoWriter for mp4 encoding, hardware-accelerated where available |
| Pillow | ~10.x+ | Text overlays, image loading | Simpler API for non-math image ops; complement to OpenCV |

**Why NOT Manim:** Manim is designed for math explanation videos (3Blue1Brown style). Its Scene/Animation abstraction adds overhead without benefit for procedural visual effects. You would fight Manim's opinionated rendering pipeline to do custom per-frame pixel math. For abstract geometric effects (tunnel, fractal, particles, plasma), you want direct NumPy array manipulation piped to OpenCV's VideoWriter. This is faster, simpler, and gives full creative control.

**Why NOT MoviePy as primary renderer:** MoviePy is a video editing library (clip composition, transitions, text overlays). It wraps ffmpeg for encoding but adds abstraction layers you do not need. For programmatic frame-by-frame generation, go direct: generate NumPy frames, write with OpenCV. Use MoviePy only if you need post-processing (audio overlay onto final mp4).

**Recommended approach:** Generate each frame as a NumPy array (1080x1920x3 uint8), write frames to mp4 with `cv2.VideoWriter` or pipe to ffmpeg via subprocess. This gives maximum control for beat-synchronized effects.

### Audio Analysis

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| librosa | ~0.10+ | BPM detection, beat tracking, onset detection | De facto standard for music information retrieval in Python; well-documented, battle-tested |
| soundfile | ~0.12+ | Audio I/O backend | librosa's recommended backend; handles wav/flac/ogg natively |
| ffmpeg (system) | 6.x+ | Audio format conversion | Convert uploaded mp3/m4a to wav before librosa analysis; also used for final video encoding |

**librosa best practices for this project:**
- `librosa.beat.beat_track()` returns tempo + beat frame positions -- this is your core sync data
- `librosa.onset.onset_strength()` for per-frame energy envelope (drives effect intensity)
- `librosa.feature.spectral_centroid()` for brightness mapping to visual parameters
- Always load at `sr=22050` (librosa default) for beat detection -- higher sample rates waste CPU
- For short clips (30-60s), analysis completes in under 1 second -- no need to async this

### RAG / Vector Store

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| ChromaDB | ~0.5+ | Vector store for style documents | Embedded mode (no server), zero-config, perfect for small knowledge bases (<100 docs), pip install and go |
| sentence-transformers | ~3.0+ | Embedding model | `all-MiniLM-L6-v2` is fast/small/good-enough for genre descriptions; runs locally, no API cost |

**Why ChromaDB over pgvector:** Your knowledge base is ~5-20 genre style documents. pgvector requires PostgreSQL, which adds deployment complexity and cost (need a database server on Railway). ChromaDB runs embedded in your Python process with a local SQLite backend. For <1000 documents, ChromaDB is the right tool. pgvector is for production systems with millions of vectors.

**Why NOT Pinecone/Weaviate/Qdrant:** Managed vector databases are overkill. You have a tiny, static knowledge base. ChromaDB's embedded mode means zero network latency, zero cost, zero ops.

### LLM Integration

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| LangChain | ~0.3+ | LLM orchestration, RAG chain | Provides ChromaDB integration, prompt templates, output parsing -- all things you need |
| langchain-openai | ~0.2+ | OpenAI LLM provider | Clean integration with GPT-4o-mini for creative parameter blending |
| langchain-community | ~0.3+ | ChromaDB vectorstore wrapper | Bridges LangChain and ChromaDB |

**Why LangChain (not raw API calls):** For this project, LangChain provides genuine value:
1. ChromaDB retriever integration out of the box
2. Structured output parsing (LLM returns JSON with visual parameters)
3. Prompt templates with variable injection
4. Chain composition (retrieve docs -> format prompt -> call LLM -> parse output)

Without LangChain, you would reimplement these four things manually. For a portfolio project demonstrating AI engineering, LangChain is expected and appropriate.

**Why NOT LlamaIndex:** LlamaIndex is document-centric (ingest PDFs, build indexes). Your knowledge base is hand-authored style documents, not ingested content. LangChain's chain abstraction maps better to your retrieve-blend-render pipeline.

**LLM choice:** GPT-4o-mini via OpenAI API. Cheap (~$0.15/1M input tokens), fast, good at structured JSON output. For creative parameter blending (mixing colors, shapes, movement patterns), it is more than sufficient. Keep the API key as an environment variable; provide a fallback mode with hardcoded defaults for when API is unavailable.

### Task Queue / Background Processing

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| ARQ | ~0.26+ | Async task queue | Lightweight Redis-backed queue built on asyncio; natural fit with FastAPI's async model |
| Redis | 7.x | Task broker + result store | Required by ARQ; also useful for SSE progress updates |

**Why ARQ over Celery:** Celery is the standard Python task queue but it is synchronous (threading/multiprocessing model). ARQ is async-native, much lighter weight, and designed for exactly this pattern: FastAPI enqueues a render job, ARQ worker picks it up, progress updates flow through Redis pub/sub. For a single-worker deployment on Railway, ARQ is simpler to configure and deploy.

**Why NOT FastAPI BackgroundTasks:** FastAPI's built-in `BackgroundTasks` runs in the same process. A 1-3 minute render would block the event loop (even in a thread, it consumes a thread pool slot). A separate worker process is the correct pattern for CPU-bound rendering.

**Alternative if Redis is too expensive:** Use FastAPI BackgroundTasks with `asyncio.to_thread()` for the render function, and in-memory progress tracking via a dict. This works for a portfolio demo with 1-2 concurrent users but does not scale. Start here, upgrade to ARQ+Redis when deploying.

### Frontend Libraries

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| Next.js | 14.x or 15.x | React framework | App Router, Server Components, API routes, Vercel deploy |
| Tailwind CSS | 3.x or 4.x | Styling | Utility-first, fast iteration, good for portfolio projects |
| shadcn/ui | latest | UI components | Not a dependency -- copied into project. Gives polished components without library lock-in |
| react-dropzone | ~14.x | File upload widget | Drag-and-drop upload with progress, widely used |
| Hls.js or native `<video>` | -- | Video playback | Native `<video>` element handles mp4 fine; no special library needed |

**Progress tracking pattern:** Use Server-Sent Events (SSE) from FastAPI to Next.js. The frontend opens an EventSource connection to `/api/render/{job_id}/progress`. FastAPI streams progress updates (0-100%) as the render proceeds. This is simpler than WebSockets for unidirectional updates.

**File upload pattern:** Upload audio to FastAPI via multipart form data. Use Next.js API route as a proxy if CORS is an issue, or configure CORS on FastAPI directly (simpler). Show upload progress via `XMLHttpRequest` or `fetch` with `ReadableStream`.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | 2.x | Data validation, settings | FastAPI uses it natively; define render params as Pydantic models |
| python-multipart | ~0.0.9+ | File upload parsing | Required by FastAPI for file uploads |
| uvicorn | ~0.30+ | ASGI server | Production server for FastAPI |
| python-dotenv | ~1.0+ | Environment variables | Load .env for API keys in development |
| httpx | ~0.27+ | Async HTTP client | For calling OpenAI API if not using LangChain's wrapper |
| pytest | ~8.x | Testing | Backend test framework |
| pytest-asyncio | ~0.24+ | Async test support | Testing FastAPI async endpoints and ARQ workers |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Python package manager | Faster than pip, good lockfile support; use `uv pip install` and `uv.lock` |
| Ruff | Linting + formatting | Replaces flake8+black+isort; single tool, very fast |
| Docker | Local development + deployment | Containerize backend with ffmpeg; Railway deploys Docker images |
| Pre-commit | Git hooks | Run ruff, type checks before commit |
| Pyright / mypy | Type checking | Pyright is faster; use strict mode for portfolio quality |

## Installation

```bash
# Backend (Python) -- using uv
uv init backend && cd backend
uv add fastapi uvicorn python-multipart python-dotenv pydantic
uv add librosa soundfile numpy opencv-python pillow
uv add chromadb sentence-transformers langchain langchain-openai langchain-community
uv add arq redis  # if using task queue
uv add --dev pytest pytest-asyncio ruff pyright httpx

# Frontend (Next.js)
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
cd frontend
npx shadcn@latest init
npm install react-dropzone
```

```bash
# System dependencies (macOS)
brew install ffmpeg redis

# System dependencies (Docker / Linux)
apt-get install ffmpeg
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| NumPy + OpenCV (frame rendering) | Manim | If you want mathematical animation with LaTeX; not suited for abstract VFX |
| NumPy + OpenCV (frame rendering) | MoviePy | If you need video editing (clip splicing, transitions); not for frame generation |
| ChromaDB (embedded) | pgvector | If you already have PostgreSQL in your stack or need >10K documents |
| ChromaDB (embedded) | FAISS | If you need pure in-memory speed and no persistence; ChromaDB is simpler |
| LangChain | Raw OpenAI SDK | If your chain is trivially simple (single prompt, no RAG); LangChain overhead not worth it |
| LangChain | LlamaIndex | If your RAG involves document ingestion/chunking from PDFs/websites |
| ARQ | Celery | If you need complex task routing, priorities, or multi-broker support |
| ARQ | Dramatiq | If you prefer synchronous workers; good Celery alternative but still sync |
| Server-Sent Events | WebSockets | If you need bidirectional communication (e.g., cancel render, live parameter tweaking) |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Manim | Designed for math explainer videos, not procedural VFX; opinionated pipeline fights custom frame generation | NumPy + OpenCV direct frame rendering |
| Pygame for rendering | Requires display surface, not designed for headless server rendering | NumPy arrays + cv2.VideoWriter |
| Pinecone / Weaviate / Qdrant | Managed vector DBs are overkill for 5-20 style documents; add cost, latency, vendor lock-in | ChromaDB embedded |
| Flask | Synchronous, no native async support, no automatic OpenAPI docs | FastAPI |
| Celery (for this project) | Heavy dependency (requires broker config, worker management); ARQ is lighter for single-worker async | ARQ or FastAPI BackgroundTasks |
| MoviePy as primary renderer | Adds abstraction layer between you and frames; slower than direct NumPy+OpenCV | Use MoviePy only for final audio overlay if needed |
| LangGraph | Overkill for a linear retrieve-blend-render chain; adds complexity without benefit here | LangChain LCEL chains |

## Stack Patterns by Variant

**If deploying on Railway free/hobby tier (budget constraint):**
- Skip Redis + ARQ; use FastAPI `BackgroundTasks` with `asyncio.to_thread()`
- Store progress in an in-memory dict (works for single-instance)
- Use ChromaDB embedded (no database server needed)
- Total cost: $0-5/month

**If scaling beyond portfolio demo:**
- Add Redis + ARQ for proper task queue
- Consider pgvector if knowledge base grows past 100 documents
- Add S3/R2 for video storage instead of local filesystem
- Add rate limiting to prevent abuse

**If LLM API costs are a concern:**
- GPT-4o-mini is already cheap (~$0.15/1M input tokens)
- Cache LLM responses for identical prompt+genre combinations
- Provide fallback mode with deterministic parameter selection (no LLM call)

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| librosa ~0.10 | NumPy <2.1 | librosa has historically lagged behind NumPy major releases; verify compat |
| FastAPI ~0.115 | Pydantic 2.x | FastAPI 0.100+ requires Pydantic v2; do not use Pydantic v1 |
| LangChain ~0.3 | langchain-core ~0.3, langchain-community ~0.3 | Version alignment matters; pin all langchain packages to same minor |
| sentence-transformers | torch ~2.x | Pulls in PyTorch; adds ~2GB to Docker image; consider using `onnxruntime` for smaller images |
| OpenCV (headless) | Use `opencv-python-headless` | On servers, use headless variant -- avoids GUI dependencies |

**Docker image size warning:** sentence-transformers pulls in PyTorch (~2GB). For deployment, consider:
1. Using `opencv-python-headless` instead of `opencv-python` (saves ~100MB)
2. Using `onnxruntime` + `optimum` instead of PyTorch for embeddings (saves ~1.5GB)
3. Multi-stage Docker build to minimize final image

## Sources

- Training data knowledge (cutoff: early 2025) -- MEDIUM confidence
- All version numbers are approximate and MUST be verified with `pip index versions <pkg>` or PyPI before pinning
- Architecture patterns based on established FastAPI + async queue patterns
- Manim vs MoviePy assessment based on library design philosophy and API surface

**Verification needed before implementation:**
- [ ] Pin exact versions after running `pip index versions` for each package
- [ ] Verify librosa + NumPy 2.x compatibility
- [ ] Verify LangChain 0.3.x ChromaDB integration API (LangChain API changes frequently)
- [ ] Check Next.js 15 stable status and App Router SSE support
- [ ] Confirm ARQ is actively maintained (check GitHub last commit date)

---
*Stack research for: AI-powered music-reactive video backdrop generation*
*Researched: 2026-04-01*
