# Beat Visuals — AI Backdrop Generator

## What This Is

A tool that generates animated video backdrops for concerts and parties. Users describe a visual style via text prompt and/or upload a short audio clip — the system analyzes BPM, retrieves genre-matched style parameters via RAG, uses an LLM to creatively blend visual parameters, and renders a seamless 1080p 30fps mp4 loop synchronized to the beat. Built as a portfolio project demonstrating AI Engineering skills.

## Core Value

A recruiter visits the site, sees a generated video backdrop synced to music, understands the idea, clicks GitHub, and sees clean code showcasing librosa + RAG + LLM integration + programmatic animation.

## Requirements

### Validated

- ✓ User can enter a text prompt describing desired visual style — Phase 1
- ✓ User can manually enter BPM as alternative to audio upload — Phase 1
- ✓ Python renders a seamless-loop mp4 video synchronized to beats (1080p, 30fps) — Phase 1
- ✓ Multiple visual effects: 3D tunnel, Julia fractal, particle system, plasma waves — Phase 1
- ✓ FastAPI backend with async rendering queue and progress tracking — Phase 1

### Active

- [ ] User can optionally upload a short audio clip (30-60s) for BPM analysis
- [ ] librosa analyzes audio: tempo, beat timestamps, tempo map
- [ ] RAG layer retrieves style documents from knowledge base (genre to colors, shapes, movement)
- [ ] LLM creatively blends parameters from retrieved style docs (not just fixed selection)
- [ ] Next.js frontend with gallery of pre-generated examples and "Try it yourself" CTA
- [ ] Video player, BPM visualization chart, download button on results page
- [ ] Deployed: Vercel (frontend) + Railway/Render (backend)

### Out of Scope

- Real-time rendering / live VJ control — GPU required, out of budget
- Mobile app — web-first, portfolio doesn't need native
- User accounts / authentication — unnecessary for portfolio demo
- Video longer than 30 seconds — render time constraint
- Characters, logos, or copyrighted imagery — only abstract geometric visuals
- Payment / monetization — portfolio project, not a product

## Context

- **Purpose:** Portfolio project for career transition into AI Engineering
- **Target audience (site visitors):** Recruiters and hiring managers evaluating AI engineering skills
- **Target audience (product):** VJs, event promoters, DJs who need custom backdrop loops
- **Domain knowledge:** User has music/VJ culture expertise
- **Prototype exists:** Visual effects confirmed working (tunnel, fractal, particles, grid, plasma, glitch)
- **Render time reality:** Python without GPU renders 30-sec loop in 1-3 minutes; async queue + progress bar handles this
- **RAG knowledge base:** Genre-specific documents mapping genre to colors, shapes, movement patterns (techno, house, ambient, industrial, psytrance)
- **LLM role:** Creative blending — LLM can mix genres, invent novel combinations beyond predefined docs
- **Audio input:** Short clips (30-60s), enough for BPM detection via librosa
- **Output:** Seamless loops — last frame connects to first frame for continuous playback
- **Landing page:** Gallery of pre-generated examples showcasing different genres, plus generate form

## Constraints

- **Budget:** $0-5/month hosting (Vercel free tier + Railway/Render cheap tier)
- **Tech stack (backend):** Python — FastAPI, librosa, Manim/MoviePy, ChromaDB/pgvector, LangChain
- **Tech stack (frontend):** Next.js + TypeScript
- **Render time:** No GPU — async queue with progress bar, pre-generated examples for instant demo
- **Security:** If LLM generates executable code, must run in isolated environment (Docker minimum)
- **Content:** Abstract geometric graphics only — no characters or logos

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Creative LLM blending over fixed params | More compelling demo, shows real AI integration | — Pending |
| Short clip input (30-60s) over full track | Sufficient for BPM detection, faster upload, simpler | — Pending |
| Seamless loops | Professional quality, shows technical depth | — Pending |
| Gallery + generate landing page | Hooks visitors with examples, then lets them try | — Pending |
| 1080p 30fps output | Balance between quality and render time | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-02 after Phase 1 completion*
