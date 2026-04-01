<!-- GSD:project-start source:PROJECT.md -->
## Project

**Beat Visuals — AI Backdrop Generator**

A tool that generates animated video backdrops for concerts and parties. Users describe a visual style via text prompt and/or upload a short audio clip — the system analyzes BPM, retrieves genre-matched style parameters via RAG, uses an LLM to creatively blend visual parameters, and renders a seamless 1080p 30fps mp4 loop synchronized to the beat. Built as a portfolio project demonstrating AI Engineering skills.

**Core Value:** A recruiter visits the site, sees a generated video backdrop synced to music, understands the idea, clicks GitHub, and sees clean code showcasing librosa + RAG + LLM integration + programmatic animation.

### Constraints

- **Budget:** $0-5/month hosting (Vercel free tier + Railway/Render cheap tier)
- **Tech stack (backend):** Python — FastAPI, librosa, Manim/MoviePy, ChromaDB/pgvector, LangChain
- **Tech stack (frontend):** Next.js + TypeScript
- **Render time:** No GPU — async queue with progress bar, pre-generated examples for instant demo
- **Security:** If LLM generates executable code, must run in isolated environment (Docker minimum)
- **Content:** Abstract geometric graphics only — no characters or logos
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

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
### Audio Analysis
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| librosa | ~0.10+ | BPM detection, beat tracking, onset detection | De facto standard for music information retrieval in Python; well-documented, battle-tested |
| soundfile | ~0.12+ | Audio I/O backend | librosa's recommended backend; handles wav/flac/ogg natively |
| ffmpeg (system) | 6.x+ | Audio format conversion | Convert uploaded mp3/m4a to wav before librosa analysis; also used for final video encoding |
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
### LLM Integration
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| LangChain | ~0.3+ | LLM orchestration, RAG chain | Provides ChromaDB integration, prompt templates, output parsing -- all things you need |
| langchain-openai | ~0.2+ | OpenAI LLM provider | Clean integration with GPT-4o-mini for creative parameter blending |
| langchain-community | ~0.3+ | ChromaDB vectorstore wrapper | Bridges LangChain and ChromaDB |
### Task Queue / Background Processing
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| ARQ | ~0.26+ | Async task queue | Lightweight Redis-backed queue built on asyncio; natural fit with FastAPI's async model |
| Redis | 7.x | Task broker + result store | Required by ARQ; also useful for SSE progress updates |
### Frontend Libraries
| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| Next.js | 14.x or 15.x | React framework | App Router, Server Components, API routes, Vercel deploy |
| Tailwind CSS | 3.x or 4.x | Styling | Utility-first, fast iteration, good for portfolio projects |
| shadcn/ui | latest | UI components | Not a dependency -- copied into project. Gives polished components without library lock-in |
| react-dropzone | ~14.x | File upload widget | Drag-and-drop upload with progress, widely used |
| Hls.js or native `<video>` | -- | Video playback | Native `<video>` element handles mp4 fine; no special library needed |
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
# Backend (Python) -- using uv
# Frontend (Next.js)
# System dependencies (macOS)
# System dependencies (Docker / Linux)
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
- Skip Redis + ARQ; use FastAPI `BackgroundTasks` with `asyncio.to_thread()`
- Store progress in an in-memory dict (works for single-instance)
- Use ChromaDB embedded (no database server needed)
- Total cost: $0-5/month
- Add Redis + ARQ for proper task queue
- Consider pgvector if knowledge base grows past 100 documents
- Add S3/R2 for video storage instead of local filesystem
- Add rate limiting to prevent abuse
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
## Sources
- Training data knowledge (cutoff: early 2025) -- MEDIUM confidence
- All version numbers are approximate and MUST be verified with `pip index versions <pkg>` or PyPI before pinning
- Architecture patterns based on established FastAPI + async queue patterns
- Manim vs MoviePy assessment based on library design philosophy and API surface
- [ ] Pin exact versions after running `pip index versions` for each package
- [ ] Verify librosa + NumPy 2.x compatibility
- [ ] Verify LangChain 0.3.x ChromaDB integration API (LangChain API changes frequently)
- [ ] Check Next.js 15 stable status and App Router SSE support
- [ ] Confirm ARQ is actively maintained (check GitHub last commit date)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
