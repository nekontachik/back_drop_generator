# Requirements: Beat Visuals -- AI Backdrop Generator

**Defined:** 2026-04-01
**Core Value:** A recruiter visits the site, sees a generated video backdrop synced to music, understands the idea, clicks GitHub, and sees clean code showcasing librosa + RAG + LLM integration + programmatic animation.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Input

- [x] **INP-01**: User can enter a text prompt describing desired visual style
- [x] **INP-02**: User can manually enter BPM (60-200 range)
- [x] **INP-03**: User can upload a short audio clip (30-60s) for analysis
- [ ] **INP-04**: User can set style blend ratio (e.g. "70% techno + 30% ambient")

### Audio Analysis

- [x] **AUD-01**: librosa extracts tempo and beat timestamps from uploaded audio
- [x] **AUD-02**: librosa extracts spectral centroid, chroma, RMS energy, onset strength as mood vector
- [x] **AUD-03**: BPM visualization chart displayed on results page
- [x] **AUD-04**: User can override detected BPM (fix octave errors)

### AI Pipeline

- [x] **RAG-01**: ChromaDB knowledge base stores genre-style documents (colors, shapes, movement)
- [x] **RAG-02**: RAG retrieves relevant style docs based on prompt + genre
- [x] **LLM-01**: LLM creatively blends parameters from retrieved docs (not fixed selection)
- [x] **LLM-02**: LLM incorporates mood vector from audio analysis into parameter blending
- [x] **LLM-03**: LLM outputs structured JSON parameters validated by Pydantic schema

### Visual Effects

- [x] **VFX-01**: 3D tunnel with perspective, twisting, BPM flashes
- [x] **VFX-02**: Julia Set fractal morphing and zooming
- [x] **VFX-03**: Particle system with gravity, connections, BPM explosions
- [x] **VFX-04**: Plasma waves -- multi-layered slow waves

### Rendering

- [x] **RND-01**: Renders seamless-loop mp4 (last frame connects to first frame)
- [x] **RND-02**: Output at 1080p 30fps via H.264 + yuv420p (ffmpeg)
- [x] **RND-03**: Async render queue with progress reporting via SSE
- [x] **RND-04**: Render runs in separate process (ProcessPoolExecutor)

### Frontend

- [x] **FE-01**: Gallery landing page with pre-generated examples and "Try it yourself" CTA
- [x] **FE-02**: Generate form: text prompt, BPM input, audio upload, style blend controls
- [x] **FE-03**: Results page: video player, BPM chart, download button
- [x] **FE-04**: Progress indicator during render (SSE-driven)

### Deployment

- [ ] **DEP-01**: Frontend deployed to Vercel
- [ ] **DEP-02**: Backend deployed to Railway/Render ($0-5/month)
- [ ] **DEP-03**: ChromaDB seeded from repo files on startup

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Visual Effects

- **VFX-05**: Perspective grid with horizon and pulsation
- **VFX-06**: Glitch + scanlines (industrial style)
- **VFX-07**: Effect layering / compositing (combine effects)

### Advanced Input

- **INP-05**: Image-to-style via Vision API (upload reference image)
- **INP-06**: Tempo map support (variable BPM within a track)

### Frontend

- **FE-05**: Live WebGL gallery on landing page
- **FE-06**: Resolution options (720p, 1080p, 4K)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time rendering / live VJ mode | Requires GPU, fundamentally different architecture, budget constraint ($0-5/mo) |
| AI image generation (Stable Diffusion) | GPU-intensive, expensive to host, competes with Runway/Pika |
| User accounts / authentication | Unnecessary for portfolio demo |
| Full-track analysis (3-5 min songs) | Render time scales linearly, storage/bandwidth costs |
| Custom effect editor / shader playground | Massive scope increase, ShaderToy exists |
| Mobile app | Web-first, responsive design sufficient for viewing |
| Social features (sharing, likes, community) | Moderation burden, storage costs, beyond portfolio scope |
| Frequency-band reactivity (bass/mid/treble) | UI complexity, mood vector covers dynamic intensity |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INP-01 | Phase 1: Rendering Engine | Complete |
| INP-02 | Phase 1: Rendering Engine | Complete |
| INP-03 | Phase 2: Audio Analysis & RAG | Complete |
| INP-04 | Phase 4: LLM Style Blending | Pending |
| AUD-01 | Phase 2: Audio Analysis & RAG | Complete |
| AUD-02 | Phase 2: Audio Analysis & RAG | Complete |
| AUD-03 | Phase 2: Audio Analysis & RAG | Complete |
| AUD-04 | Phase 2: Audio Analysis & RAG | Complete |
| RAG-01 | Phase 2: Audio Analysis & RAG | Complete |
| RAG-02 | Phase 2: Audio Analysis & RAG | Complete |
| LLM-01 | Phase 4: LLM Style Blending | Complete |
| LLM-02 | Phase 4: LLM Style Blending | Complete |
| LLM-03 | Phase 4: LLM Style Blending | Complete |
| VFX-01 | Phase 1: Rendering Engine | Complete |
| VFX-02 | Phase 1: Rendering Engine | Complete |
| VFX-03 | Phase 1: Rendering Engine | Complete |
| VFX-04 | Phase 1: Rendering Engine | Complete |
| RND-01 | Phase 1: Rendering Engine | Complete |
| RND-02 | Phase 1: Rendering Engine | Complete |
| RND-03 | Phase 1: Rendering Engine | Complete |
| RND-04 | Phase 1: Rendering Engine | Complete |
| FE-01 | Phase 3: Frontend Application | Complete |
| FE-02 | Phase 3: Frontend Application | Complete |
| FE-03 | Phase 3: Frontend Application | Complete |
| FE-04 | Phase 3: Frontend Application | Complete |
| DEP-01 | Phase 5: Deployment & Production | Pending |
| DEP-02 | Phase 5: Deployment & Production | Pending |
| DEP-03 | Phase 5: Deployment & Production | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0

---
*Requirements defined: 2026-04-01*
*Last updated: 2026-04-01 after roadmap revision (phases 2 and 3 swapped)*
