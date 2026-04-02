# Roadmap: Beat Visuals -- AI Backdrop Generator

## Overview

This roadmap delivers a working AI-powered backdrop generator in five phases. The rendering engine comes first because every other feature depends on it -- you cannot test audio sync, LLM blending, or frontend integration without a working renderer. Audio analysis and RAG follow immediately to complete the full backend pipeline (rendering + audio + knowledge base). The frontend then builds on top of a fully functional backend. LLM integration wires the full AI pipeline. Deployment puts it live for recruiters to experience.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Rendering Engine** - FastAPI backend with 4 visual effects, seamless loop rendering, async queue, and manual input
- [ ] **Phase 2: Audio Analysis & RAG Knowledge Base** - librosa audio extraction, BPM visualization, ChromaDB genre store, and RAG retrieval
- [ ] **Phase 3: Frontend Application** - Next.js app with gallery, generate form, results page, and SSE progress
- [ ] **Phase 4: LLM Style Blending** - Full AI pipeline from prompt to validated render parameters via RAG + LLM
- [ ] **Phase 5: Deployment & Production** - Frontend on Vercel, backend on Railway, ChromaDB self-seeding on startup

## Phase Details

### Phase 1: Rendering Engine
**Goal**: A working backend API that accepts a text prompt and BPM, renders a seamless-loop video with any of 4 visual effects, and reports progress -- all without blocking the server
**Depends on**: Nothing (first phase)
**Requirements**: INP-01, INP-02, VFX-01, VFX-02, VFX-03, VFX-04, RND-01, RND-02, RND-03, RND-04
**Success Criteria** (what must be TRUE):
  1. User can submit a text prompt and BPM value via API and receive a job ID
  2. Rendered MP4 plays correctly in Chrome and Safari (H.264/yuv420p) with no visual discontinuity at the loop point
  3. All 4 effects (tunnel, fractal, particles, plasma) produce visually distinct output synchronized to the provided BPM
  4. Health endpoint responds within 1 second while a render is actively running (proves ProcessPoolExecutor isolation)
  5. SSE endpoint streams progress updates from pending through complete for an active render job
**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md -- Project scaffold, Pydantic schemas, loop math, encoder, base effect, prompt mapper
- [ ] 01-02-PLAN.md -- 4 visual effects (tunnel, fractal, particles, plasma) and render pipeline
- [ ] 01-03-PLAN.md -- FastAPI API, job manager, ProcessPoolExecutor worker, SSE streaming, cleanup

### Phase 2: Audio Analysis & RAG Knowledge Base
**Goal**: Users can upload audio clips for automatic BPM detection and mood analysis, and the system retrieves genre-matched style parameters from a knowledge base
**Depends on**: Phase 1
**Requirements**: INP-03, AUD-01, AUD-02, AUD-03, AUD-04, RAG-01, RAG-02
**Success Criteria** (what must be TRUE):
  1. User uploads a 30-60 second audio clip and receives accurate BPM detection (with octave-error correction) and beat timestamps
  2. Results page displays a BPM visualization chart showing detected beats and audio energy
  3. User can override the detected BPM if the automatic detection is wrong
  4. RAG retrieval returns relevant genre-style documents (colors, shapes, movement) when given a text prompt
  5. ChromaDB knowledge base contains genre-style documents and is queryable via the API
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD

### Phase 3: Frontend Application
**Goal**: Users interact with the backdrop generator through a polished web interface -- browsing a gallery, submitting generation requests, watching progress, and downloading results
**Depends on**: Phase 1 (optionally Phase 2 for audio upload UI)
**Requirements**: FE-01, FE-02, FE-03, FE-04
**Success Criteria** (what must be TRUE):
  1. Landing page displays a gallery of pre-generated example videos with a visible "Try it yourself" call to action
  2. User can fill out a generate form (text prompt, BPM, audio upload field, style blend controls) and submit it to the backend
  3. Results page shows a video player with the rendered output, a BPM visualization chart, and a download button that delivers the MP4
  4. Progress indicator updates in real-time during rendering, driven by SSE from the backend
**Plans**: TBD
**UI hint**: yes

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: LLM Style Blending
**Goal**: The full AI pipeline works end-to-end -- text prompt and audio analysis feed into RAG retrieval, the LLM creatively blends retrieved style parameters, and the output drives the renderer
**Depends on**: Phase 1, Phase 2
**Requirements**: INP-04, LLM-01, LLM-02, LLM-03
**Success Criteria** (what must be TRUE):
  1. User can set a style blend ratio (e.g., "70% techno + 30% ambient") and the LLM incorporates it into parameter generation
  2. LLM produces creative parameter combinations that differ meaningfully from the raw retrieved style documents (not just passthrough)
  3. LLM output is structured JSON validated by Pydantic schema -- invalid outputs fall back to genre defaults without crashing
  4. Audio mood vector (spectral centroid, energy, chroma) visibly influences the generated visual parameters
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: Deployment & Production
**Goal**: The complete application is live on the internet -- frontend on Vercel, backend on Railway -- and a recruiter can visit the URL, browse the gallery, generate a backdrop, and download it
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4
**Requirements**: DEP-01, DEP-02, DEP-03
**Success Criteria** (what must be TRUE):
  1. Frontend loads at a public Vercel URL and the gallery displays pre-generated examples
  2. Backend responds at a public Railway URL and handles generate requests from the Vercel frontend (CORS configured correctly)
  3. ChromaDB knowledge base seeds itself automatically from repo files on backend startup -- no manual setup required
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
(Phase 2 and Phase 3 may execute in parallel as both depend only on Phase 1)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Rendering Engine | 0/3 | Planning complete | - |
| 2. Audio Analysis & RAG | 0/2 | Not started | - |
| 3. Frontend Application | 0/2 | Not started | - |
| 4. LLM Style Blending | 0/2 | Not started | - |
| 5. Deployment & Production | 0/2 | Not started | - |
