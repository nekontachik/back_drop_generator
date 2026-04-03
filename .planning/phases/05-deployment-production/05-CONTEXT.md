# Phase 5: Deployment & Production - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Deploy the complete application to production. Frontend on Vercel, backend on Railway with Docker. Pre-generate gallery examples. A recruiter visits the URL, browses the gallery, generates a backdrop, and downloads it. No new features — purely deployment, configuration, and gallery content.

</domain>

<decisions>
## Implementation Decisions

### Backend Deployment (Railway)
- **D-01:** Full Dockerfile with multi-stage build — builder stage installs all dependencies, runtime stage is slim. Includes ffmpeg, Python deps (librosa, chromadb, numpy, opencv-headless), and uvicorn.
- **D-02:** Local filesystem with TTL cleanup for rendered videos. Files lost on redeploy is acceptable for a demo — pre-generated gallery examples persist in Git LFS.
- **D-03:** ChromaDB re-seeds from YAML genre files on every startup. No persistent volume needed. Fast (~1-2 seconds for 10 docs).
- **D-04:** Environment variables on Railway: ANTHROPIC_API_KEY, CORS_ORIGINS (Vercel frontend URL), any other config from Pydantic Settings.

### Frontend Deployment (Vercel)
- **D-05:** NEXT_PUBLIC_API_URL environment variable set in Vercel dashboard. Different values for preview deploys vs production.
- **D-06:** Default Vercel/Railway URLs are fine — no custom domain needed. Free tier, zero config.
- **D-07:** Standard Next.js build and deploy via Vercel Git integration (push to main = deploy).

### Pre-Generated Gallery Content
- **D-08:** 4-6 pre-generated example videos — one per effect type (tunnel, fractal, particles, plasma) plus 1-2 genre blends to showcase variety.
- **D-09:** Videos stored in Git LFS in the repo. Always available, no external dependency. ~50-100MB total for 4-6 videos. GitHub free tier allows 1GB LFS.
- **D-10:** Each gallery example includes: MP4 file, the prompt that generated it, effect type, and genre metadata (for the hover-reveal on landing page).

### Claude's Discretion
- Exact Dockerfile structure and base image choice (python:3.12-slim or similar)
- Railway service configuration details
- CORS origin list format and configuration
- Health check endpoint configuration for Railway
- Git LFS setup and .gitattributes configuration
- Gallery example prompt/genre/effect combinations
- Vercel build settings and output configuration
- Any production logging configuration

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend code (to be containerized)
- `backend/app/main.py` — FastAPI app entry point, CORS middleware, lifespan (ChromaDB seeding)
- `backend/app/config.py` — Pydantic Settings with all environment variables
- `backend/app/services/genre_seeder.py` — ChromaDB seeding logic (runs on startup)
- `backend/app/services/cleanup.py` — TTL file cleanup service
- `backend/pyproject.toml` — Python dependencies to install in Docker

### Frontend code (to be deployed)
- Frontend directory (Phase 3 creates this) — Next.js app with App Router

### Project constraints
- `.planning/PROJECT.md` — $0-5/month hosting budget, Vercel free tier + Railway cheap tier
- `.planning/REQUIREMENTS.md` — DEP-01 (Vercel), DEP-02 (Railway $0-5/mo), DEP-03 (ChromaDB auto-seed)

### Prior phase decisions
- `.planning/phases/01-rendering-engine/01-CONTEXT.md` — D-18 (TTL file cleanup)
- `.planning/phases/02-audio-analysis-rag-knowledge-base/02-CONTEXT.md` — D-07 (seed from repo files on startup)
- `.planning/phases/03-frontend-application/03-CONTEXT.md` — Landing page gallery design, Next.js App Router structure
- `.planning/phases/04-llm-style-blending/04-CONTEXT.md` — D-04 (ANTHROPIC_API_KEY env var), D-10 (deterministic fallback without API key)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/services/genre_seeder.py` — Already handles ChromaDB seeding from YAML files on startup. DEP-03 is essentially implemented.
- `backend/app/services/cleanup.py` — TTL cleanup of rendered files already implemented.
- `backend/app/config.py` — Pydantic Settings already centralizes configuration via env vars.

### Established Patterns
- FastAPI app with lifespan events for startup/shutdown tasks
- Uvicorn as ASGI server — will be the Docker CMD
- ProcessPoolExecutor for render jobs — needs to work within Railway's container

### Integration Points
- CORS middleware in `main.py` needs production frontend URL added
- Config Settings needs CORS_ORIGINS field for production URL
- Frontend needs NEXT_PUBLIC_API_URL pointing to Railway backend
- Gallery videos need to be accessible from the frontend (either served by backend or included in frontend assets)

</code_context>

<specifics>
## Specific Ideas

- Gallery examples should cover the range of visual styles: one dark/industrial tunnel, one colorful psychedelic fractal, one ambient particles, one energetic plasma — plus a genre blend or two
- The prompts used for gallery examples should be memorable and descriptive — they show on hover and tell the recruiter what the tool can do
- Consider including the BPM used for each gallery example so the results page demo is complete

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-deployment-production*
*Context gathered: 2026-04-03*
