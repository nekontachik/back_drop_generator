# Project Research Summary

**Project:** Beat Visuals — AI-Powered Music-Reactive Video Backdrop Generator
**Domain:** AI video generation / music visualization / creative tooling
**Researched:** 2026-04-01
**Confidence:** MEDIUM

## Executive Summary

Beat Visuals occupies a genuine gap in the market: no existing tool combines text-prompt-driven style selection, true BPM-structural synchronization, and seamless-loop MP4 export in a zero-friction web interface. Professional VJ tools (Resolume, VDMX) own real-time GPU rendering but cost hundreds of dollars and require days to learn. AI video generators (Runway, Kaiber) accept text prompts but do not perform true beat-grid sync. Consumer visualizers (Synesthesia, Milkdrop) sync to audio but use fixed presets with no prompt input. The product's unique position is: type a genre/mood description, optionally upload a 30-60 second audio clip, and receive a beat-synchronized seamless loop in minutes, from a web browser with no account required.

The recommended technical approach is a Python/FastAPI backend deployed on Railway with a Next.js frontend on Vercel. The rendering pipeline is the core: NumPy array frame generation piped to ffmpeg (H.264) is faster and more controllable than Manim or MoviePy. Audio analysis via librosa provides BPM detection and beat grids. A small ChromaDB embedded vector store (5-20 genre style documents) grounds an LLM (GPT-4o-mini via LangChain) that blends retrieved style parameters into a structured JSON render configuration. The AI's role is creative parameter synthesis, not pixel generation — this keeps rendering CPU-bound and fast, avoiding the GPU cost and quality inconsistency of diffusion models. For MVP on a budget constraint, start with FastAPI BackgroundTasks + ProcessPoolExecutor; upgrade to ARQ + Redis only when multi-user scale demands it.

The two highest-risk architectural decisions must be made correctly in Phase 1: (1) CPU-bound rendering must run in a separate process from FastAPI via ProcessPoolExecutor — not a thread pool — to avoid blocking the event loop and causing platform health-check timeouts; (2) seamless loop continuity requires all frame parameters to be derived as `t = frame_index / total_frames` (never accumulated), ensuring frame[N-1] wraps cleanly to frame[0]. A third systemic risk is that ChromaDB data is ephemeral on container platforms — the knowledge base must seed itself on startup from source files committed to the repository. Getting all three right from the start prevents costly refactors later.

## Key Findings

### Recommended Stack

The backend is Python 3.11+ with FastAPI as the API framework, using NumPy + OpenCV (headless) for per-frame rendering and ffmpeg subprocess piping for H.264 encoding. librosa handles audio analysis (BPM detection, beat timestamps, onset strength). ChromaDB in embedded mode serves the RAG vector store; sentence-transformers with `all-MiniLM-L6-v2` provides embeddings with no API cost. LangChain (0.3.x) orchestrates the RAG-to-LLM chain with structured Pydantic output parsing. The frontend is Next.js 14/15 with TypeScript, Tailwind CSS, shadcn/ui components, and react-dropzone for audio upload; progress updates flow via Server-Sent Events (SSE).

**Core technologies:**
- Python 3.11+ / FastAPI: async API server, Pydantic v2 models, background task support, automatic OpenAPI docs
- NumPy + OpenCV (headless) + ffmpeg: direct frame-level rendering at maximum speed and creative control; `opencv-python-headless` on servers
- librosa (~0.10+): de facto standard for BPM detection, beat tracking, onset strength; always load at `sr=22050, mono=True`
- ChromaDB (embedded, ~0.5+): zero-config local vector store for 5-20 genre style documents; no separate database server required
- sentence-transformers `all-MiniLM-L6-v2`: local embeddings, no API cost; pre-download in Docker build to avoid cold-start timeouts
- LangChain (~0.3.x) + GPT-4o-mini: RAG chain with `with_structured_output()` and Pydantic validators; pin all langchain packages to same minor version
- Next.js 14/15 + TypeScript + Tailwind + shadcn/ui: frontend with SSE EventSource hook for progress
- ARQ + Redis (optional upgrade): async task queue; use only when BackgroundTasks + ProcessPoolExecutor hits limits

**Version flags to verify before pinning:** librosa ~0.10 + NumPy 2.x compatibility requires explicit verification; LangChain 0.3.x ChromaDB integration API surface changes frequently; sentence-transformers pulls PyTorch (~2GB Docker image — use onnxruntime for smaller images).

### Expected Features

**Must have (table stakes) — v1 launch:**
- Text prompt input — every AI tool has this; users look for it first
- Manual BPM entry — simpler than audio upload; builds core beat sync before librosa is integrated
- 3-4 visual effects (tunnel, fractal, particles, plasma) — minimum variety to feel like a real product
- Seamless loop rendering at 1080p 30fps — the core technical deliverable
- Async render queue with SSE progress indicator — renders take 1-3 min; no feedback = users think it is broken
- MP4 download — users need the output file
- Pre-generated gallery on landing page — instant proof-of-concept, no waiting required
- Basic video player on results page — users preview before downloading

**Should have (differentiators) — v1.x after core pipeline is stable:**
- Audio clip upload with librosa BPM extraction — the true differentiator vs. every competitor
- RAG knowledge base with LLM style blending — the AI engineering showcase; demonstrates RAG + LLM integration in a coherent pipeline
- Additional effects (perspective grid, glitch/scanlines) — proves the effect plugin architecture is extensible
- Onset strength / energy mapping for dynamic intensity — makes beat sync feel alive, not mechanical

**Defer to v2+:**
- Variable BPM / tempo map support — complex librosa usage, rare for electronic music
- Effect layering / compositing — architectural complexity with diminishing portfolio returns
- Resolution options (720p, 4K) — 4K render times impractical on CPU
- API endpoint for programmatic generation — only if external integrators emerge

**Hard anti-features — do not build:**
- Real-time VJ mode — requires GPU, fundamentally different architecture, owned by Resolume/VDMX
- Diffusion model pixel generation (Stable Diffusion, etc.) — GPU cost, slow, hard to seamlessly loop
- User accounts — authentication, GDPR, session management all out of scope for portfolio
- Full-track analysis (5+ min songs) — CPU render times become unacceptably long

### Architecture Approach

The system is a client-server split: Next.js on Vercel handles the frontend (gallery, generate form, progress view, result player); FastAPI on Railway handles the API, job management, and the render worker. The render worker is the critical component and must run in a separate process from the FastAPI event loop. The worker's internal pipeline is strictly linear: Audio Analyzer (librosa) → RAG Retriever (ChromaDB) → LLM Blender (LangChain) → Video Renderer (NumPy + ffmpeg). Progress state flows from worker back to API via an in-memory dict (MVP) or Redis pub/sub (production), then streams to the frontend via SSE. ChromaDB genre knowledge lives as YAML/JSON source files in the repo and is seeded into the embedded database on startup via a FastAPI lifespan handler.

**Major components:**
1. FastAPI API Layer — thin HTTP routing; validates input with Pydantic; returns job IDs immediately; no business logic in routes
2. Job Manager + Progress Store — tracks render state transitions (pending → analyzing → retrieving → blending → rendering → encoding → complete); in-memory dict for MVP, Redis pub/sub for production
3. Render Worker (separate process via ProcessPoolExecutor or ARQ) — orchestrates the full pipeline; must never share a process with FastAPI
4. Audio Analyzer (librosa) — extracts BPM, beat timestamps, onset strength; always use `sr=22050, mono=True`; save uploaded files to tempfile with UUID filename before passing to librosa
5. RAG Retriever (ChromaDB + sentence-transformers) — retrieves genre style documents matching user prompt; loads model once at startup into `app.state`; seeds collection from repo files on startup if missing
6. LLM Blender (LangChain + GPT-4o-mini) — outputs structured `RenderParams` via `with_structured_output()` with Pydantic validators; always falls back to genre defaults on parse failure
7. Video Renderer (NumPy + ffmpeg) — vectorized frame generation (no Python pixel loops); pipes raw RGB frames to ffmpeg subprocess for H.264/yuv420p encoding; pre-allocates single frame buffer
8. Effect Plugin System — each effect (tunnel, fractal, particles, plasma, grid, glitch) extends a common abstract base class; LLM selects effect via `effect_type` field in RenderParams
9. Next.js Frontend — gallery Server Component with lazy-loaded videos; generate form Client Component with react-dropzone; `use-render-progress` hook encapsulating SSE EventSource logic

### Critical Pitfalls

1. **CPU rendering blocks FastAPI event loop** — use `ProcessPoolExecutor` (not the default `ThreadPoolExecutor`) for render tasks from day one; NumPy does not fully release the GIL during Python-level loop logic. Verify by hitting the health endpoint every second during an active render — zero timeouts required.

2. **Seamless loop discontinuity at the wrap point** — always derive `t = frame_index / total_frames` where t is in range [0, 1), never reaching 1.0; never accumulate `t += dt`. Write an automated pixel-diff test asserting that the difference between frame[0] and frame[N-1] is within 2x of average consecutive-frame difference. Run on every effect type.

3. **librosa BPM returns half or double the actual tempo** — implement octave-error correction (BPM < 80 → double; BPM > 200 → halve); use `start_bpm=128` to bias toward electronic music range; always display detected BPM and allow user correction. This is a fundamental limitation of BPM detection, not a librosa bug.

4. **LLM returns unparseable or out-of-range parameters** — use LangChain `with_structured_output()` with a Pydantic model containing range validators (`ge=0.0, le=1.0`, regex for hex colors); implement fallback to deterministic genre defaults on any parse failure; never let raw LLM output reach the renderer.

5. **ChromaDB data lost on container redeployment** — never rely on container filesystem persistence; store all style documents as files in the repo; implement `ensure_knowledge_base()` as a FastAPI lifespan startup function; test by deleting the ChromaDB directory locally and restarting — app must self-heal in <1 second.

6. **Video unplayable in Safari/iOS** — `cv2.VideoWriter` with `'mp4v'` fourcc produces MPEG-4 Part 2, which Chrome plays but Safari does not; always pipe raw frames to ffmpeg with `-c:v libx264 -pix_fmt yuv420p`; verify with `ffprobe` during Phase 1, not at the end.

7. **LLM generating executable code** — the LLM must output only JSON parameters that select and configure predefined effect functions; never use `eval()` or `exec()` on any string derived from user input or LLM output; `grep -r "eval\|exec"` must return zero hits on code paths connected to user/LLM input.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Rendering Foundation

**Rationale:** The rendering engine is the highest-risk component with the most pitfalls (event loop blocking, seamless loop math, H.264 browser compatibility). Everything else in the system depends on a working renderer. Validate the pipeline structure and all three Phase 1 pitfalls before building features on top. A working gallery with pre-generated examples also delivers immediate portfolio value before the full pipeline exists.

**Delivers:** NumPy frame generation piped to ffmpeg producing browser-compatible seamless loops at 1080p 30fps; async job queue with SSE progress reporting; working gallery page with pre-generated examples; manual BPM input wired to frame timing

**Addresses from FEATURES.md:** 3-4 visual effects (tunnel, fractal, particles, plasma), seamless loop rendering, async progress indicator, MP4 download, pre-generated gallery, video player

**Avoids from PITFALLS.md:** CPU event loop blocking (ProcessPoolExecutor from day one), seamless loop discontinuity (t = frame_index/total_frames from day one, automated pixel-diff test), Safari H.264 incompatibility (ffmpeg pipe from day one, not cv2.VideoWriter)

**Tech from STACK.md:** NumPy, opencv-python-headless, ffmpeg, FastAPI BackgroundTasks + ProcessPoolExecutor, SSE StreamingResponse, Next.js gallery + video player

### Phase 2: Audio Analysis and RAG Knowledge Base

**Rationale:** Audio analysis (librosa) and the RAG knowledge base (ChromaDB) are medium-complexity, independently testable, and well-isolated from each other. Both are prerequisites for the LLM layer in Phase 3. Manual BPM entry from Phase 1 remains as a fallback. Build these together since they share no dependencies and both feed into Phase 3.

**Delivers:** Audio clip upload with BPM extraction, beat grid, and onset strength; octave-error correction heuristic with user override UI; ChromaDB genre knowledge base that seeds itself on startup from repo files; RAG retrieval returning relevant style documents for a text prompt

**Addresses from FEATURES.md:** Audio clip upload + librosa BPM detection, BPM visualization, RAG knowledge base

**Avoids from PITFALLS.md:** librosa BPM octave errors (correction heuristic + user override), ChromaDB data loss on deploy (seed-on-startup from repo source files), sentence-transformers cold start timeout (pre-download model in Dockerfile), librosa UploadFile handling (save to tempfile with UUID, convert to wav via ffmpeg before passing to librosa), LangChain startup re-embedding (load existing collection, not from_documents on every startup)

**Tech from STACK.md:** librosa, soundfile, ffmpeg audio conversion, ChromaDB embedded, sentence-transformers (all-MiniLM-L6-v2), python-multipart

### Phase 3: LLM Style Blending

**Rationale:** The LLM layer depends on both the renderer (Phase 1 delivers RenderParams schema) and the RAG knowledge base (Phase 2 delivers the retriever). With both proven, wire the LangChain LCEL chain. Deferring LangChain integration until the RenderParams Pydantic model is stable reduces the surface area affected by LangChain API changes.

**Delivers:** Full AI pipeline end-to-end: text prompt → RAG retrieval → LLM parameter blending → validated RenderParams → renderer; deterministic fallback mode producing watchable output when OpenAI API is unavailable; measured parse success rate > 95% across 50+ prompt variations

**Addresses from FEATURES.md:** AI-driven style blending, genre-aware generation, LLM creative parameter synthesis as core differentiator

**Avoids from PITFALLS.md:** LLM output parsing failures (Pydantic `with_structured_output()` with range validators, fallback defaults), code execution security (LLM outputs JSON only, no eval/exec), ChromaDB startup re-embedding (load existing collection), rate limits and API key exposure (key in backend .env only, never in NEXT_PUBLIC_*)

**Tech from STACK.md:** LangChain ~0.3.x, langchain-openai, langchain-community, GPT-4o-mini, Pydantic v2 with Field validators

### Phase 4: API Hardening and Deployment

**Rationale:** Cross-origin CORS issues, cold start problems, disk exhaustion, and rate limiting are all invisible during local development. Surface and fix production-specific issues before investing effort in frontend polish. Full deployment verification (frontend on Vercel, backend on Railway) must happen in this phase.

**Delivers:** Production-ready API with IP-based rate limiting (slowapi), file type and size validation, UUID-based filenames (no path traversal), render file cleanup (TTL-based, 1-hour default), CORS correctly configured for SSE + Range requests across Vercel→Railway, Docker image with pre-downloaded sentence-transformers model, cold start < 10 seconds

**Addresses from FEATURES.md:** Zero-setup web interface (no broken CORS), video serving correctness, format support breadth

**Avoids from PITFALLS.md:** CORS breaking SSE and video Range requests in production, rate limiting abuse (3 renders/hour/IP), disk exhaustion from accumulated renders, path traversal via user-provided filenames, Vercel SSE proxy timeout (frontend connects directly to Railway backend for SSE, never proxied), cold start > 10 seconds, sentence-transformers model download on first request

**Tech from STACK.md:** slowapi, python-multipart validation, Docker multi-stage build, Railway deployment, Vercel deployment with Next.js rewrite rules

### Phase 5: Frontend Polish and UX

**Rationale:** With the backend fully working end-to-end in production, complete the frontend experience to recruiter and user quality standards. The frontend is standard Next.js patterns with low technical risk; polish here is about execution quality, not architectural decisions.

**Delivers:** Gallery with poster images and lazy-loaded videos (Lighthouse > 80); generate form with clickable example prompts and prominent BPM edit UI; responsive layout that works on mobile browsers (viewing); polished progress labels by stage ("Analyzing audio... Generating frames 45/900... Encoding..."); helpful error messages for all failure cases (corrupt file, empty prompt, API down, render timeout); autoplay-looping video player (`muted playsInline autoPlay loop`)

**Addresses from FEATURES.md:** Frictionless UX with zero learning curve, example prompts to reduce blank-input paralysis, visible beat sync feedback, mobile viewing compatibility

**Avoids from PITFALLS.md:** Video autoplay failing (muted + playsInline required), gallery slow first load (poster images + lazy load + pre-compressed gallery videos), upload format rejection confusion (clear supported-formats list, accept all common audio formats), empty prompt confusion (3-4 clickable example prompts), user expectations mismatch (clear "generates abstract geometric visuals" description above form)

### Phase Ordering Rationale

- **Renderer first:** Frame generation is the highest-risk, most custom component. The seamless loop math, ffmpeg encoding flags, and process isolation must be proven before any other feature builds on top of them.
- **Audio and RAG together:** Both are prerequisite data layers for the LLM. Neither depends on the other. Grouping them shortens the time before Phase 3 can begin.
- **LLM after the stable RenderParams schema:** LangChain's API surface changes frequently. Deferring integration until the Pydantic output model is defined and stable reduces the chance of needing to rework the LLM layer when the renderer schema changes.
- **Deployment before frontend polish:** CORS, cold start, and disk exhaustion are all invisible locally. These must be surfaced and fixed before polishing the frontend, not discovered by a recruiter watching a broken demo.
- **MVP shortcut (budget):** For a portfolio demo with under 5 concurrent users, use FastAPI BackgroundTasks + ProcessPoolExecutor instead of ARQ + Redis throughout all phases. Upgrade only if concurrent demand warrants the Redis infrastructure cost.

### Research Flags

Phases likely needing deeper `/gsd:research-phase` during planning:
- **Phase 3 (LLM Integration):** LangChain 0.3.x ChromaDB integration API changes across minor versions; verify `with_structured_output()` signature, `Chroma` constructor, and LCEL chain composition against current docs before writing implementation tasks.
- **Phase 4 (Deployment):** Railway and Render platform constraints (disk allocation, cold start behavior, health check path configuration, build timeout for large Docker images) change with platform pricing; verify current Railway hobby plan specs.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Core Rendering):** NumPy + ffmpeg piping is well-documented; ProcessPoolExecutor pattern is established; seamless loop math is fully specified in ARCHITECTURE.md.
- **Phase 2 (Audio Analysis):** librosa BPM API is stable and well-documented; ChromaDB embedded seeding pattern is straightforward.
- **Phase 5 (Frontend):** Next.js App Router + Tailwind + shadcn/ui is a well-documented standard stack; SSE EventSource in React is a known pattern.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core library choices are well-founded and appropriate. Specific version numbers are approximate and must be verified with `pip index versions` before pinning. librosa + NumPy 2.x compat and sentence-transformers Docker image size need explicit pre-implementation verification. |
| Features | MEDIUM | Competitive landscape for mature products (Resolume, VDMX, Synesthesia) is HIGH confidence — these are stable, well-known feature sets. AI video tool space (Kaiber) is LOW confidence — that space evolves rapidly and training data is likely stale. |
| Architecture | MEDIUM | Async job queue, SSE progress, RAG + LLM chain, and seamless loop math are all well-established patterns. Specific LangChain LCEL and ChromaDB integration API needs verification against current docs before Phase 3 planning. |
| Pitfalls | HIGH | All 7 critical pitfalls are real, persistent, well-documented issues in these specific ecosystems. Prevention strategies are proven. Platform-specific limits (Vercel response size, Railway disk) should be re-verified against current plan documentation. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Exact package versions:** All versions in STACK.md are approximate. Run `pip index versions <pkg>` for librosa, all LangChain packages, ChromaDB, and sentence-transformers before writing pyproject.toml. Explicitly verify librosa + NumPy 2.x compatibility.
- **LangChain ChromaDB integration API:** LangChain's ChromaDB integration has changed across minor versions; verify the exact constructor, retriever API, and `with_structured_output()` signature against current docs before planning Phase 3 tasks.
- **Competitor feature drift:** The competitive analysis for Kaiber and Synesthesia is based on training data from before May 2025. Verify current feature sets against live product pages before finalizing landing page competitive positioning copy.
- **ARQ maintenance status:** STACK.md recommends ARQ as the async task queue upgrade path. Verify the GitHub repo is actively maintained (recent commit activity) before committing to it for the Phase 4 upgrade path.
- **Railway/Render current plan limits:** Disk allocation, cold start behavior, and health check configuration change with platform pricing. Verify Phase 4 assumptions against current Railway docs before planning deployment tasks.

## Sources

### Primary (HIGH confidence)
- Training data: librosa BPM octave-error ambiguity — fundamental MIR limitation, well-documented
- Training data: OpenCV VideoWriter mp4v vs H.264 cross-browser issue — persistent, widely documented cross-browser problem
- Training data: Python GIL behavior with NumPy and FastAPI async patterns — well-understood runtime behavior
- Training data: ChromaDB embedded mode limitations on ephemeral container filesystems — documented deployment pattern
- Training data: Resolume Arena, VDMX, Synesthesia core feature sets — mature products with stable, well-known feature sets
- Training data: Browser autoplay policies (muted required, Chrome 66+, Safari 11+) — stable browser behavior

### Secondary (MEDIUM confidence)
- Training data: LangChain structured output, Pydantic integration patterns, LCEL chain composition (pre-May 2025)
- Training data: Next.js App Router SSE support and Vercel platform constraints (pre-May 2025)
- Training data: ChromaDB, sentence-transformers, ARQ API surfaces (pre-May 2025)
- Training data: Railway/Render platform behavior and limits (pre-May 2025)

### Tertiary (LOW confidence)
- Training data: Kaiber AI video features — AI video generation space evolves rapidly, likely stale
- Inferred: ARQ active maintenance status — needs GitHub verification before adoption

---
*Research completed: 2026-04-01*
*Ready for roadmap: yes*
