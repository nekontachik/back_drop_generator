---
phase: 05-deployment-production
plan: 01
subsystem: infra
tags: [docker, fastapi, cors, railway, uvicorn, chromadb, librosa, pyyaml, soundfile, opencv]

# Dependency graph
requires:
  - phase: 04-llm-style-blending
    provides: anthropic SDK integration, FastAPI backend with /generate endpoint, config.py Settings
provides:
  - Multi-stage Dockerfile for Railway deployment with ffmpeg and libsndfile
  - Complete pyproject.toml dependency list including chromadb, librosa, pyyaml, soundfile
  - Configurable CORS via CORS_ORIGINS environment variable
  - .env.example documenting all backend environment variables
affects: [05-02-frontend-vercel]

# Tech tracking
tech-stack:
  added: [docker multi-stage build, uv sync in container, ffmpeg system dep, libsndfile system dep]
  patterns:
    - Multi-stage Docker build: builder stage installs deps with uv, runtime stage is slim with system deps
    - Pydantic Settings JSON list parsing: CORS_ORIGINS env var as JSON string parsed to list[str] automatically

key-files:
  created:
    - backend/Dockerfile
    - backend/.dockerignore
    - backend/.env.example
    - .planning/phases/05-deployment-production/deferred-items.md
  modified:
    - backend/pyproject.toml
    - backend/app/config.py
    - backend/app/main.py

key-decisions:
  - "Multi-stage Docker build: builder with build-essential + uv, runtime with ffmpeg + libsndfile only — minimizes final image size"
  - "CORS_ORIGINS as JSON list env var: Pydantic Settings parses JSON strings to list[str] natively — no custom parsing needed"
  - "Port field in Settings for Railway PORT injection: defaults to 8000 for local dev"

patterns-established:
  - "Docker multi-stage: COPY --from=builder /app/.venv /app/.venv pattern for uv virtual environments"
  - "Settings.cors_origins list defaults to localhost:3000, overridden in production via env var"

requirements-completed: [DEP-02, DEP-03]

# Metrics
duration: 15min
completed: 2026-04-04
---

# Phase 05 Plan 01: Backend Railway Deployment Prep Summary

**Multi-stage Dockerfile with ffmpeg + uv, complete pyproject.toml deps, and configurable CORS via CORS_ORIGINS env var for Railway deployment**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-04-04T05:45:30Z
- **Completed:** 2026-04-04T06:00:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Fixed pyproject.toml — added chromadb, librosa, pyyaml, soundfile, opencv-python-headless (all were imported but not declared)
- Created multi-stage Dockerfile with ffmpeg, libsndfile, uv sync, HEALTHCHECK, and genre YAML data included for ChromaDB auto-seeding
- Updated CORS middleware from wildcard `["*"]` to `settings.cors_origins` (configurable via `CORS_ORIGINS` env var)
- Created .env.example documenting all 8 environment variables with comments

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix pyproject.toml deps and create multi-stage Dockerfile** - `a1c29f1` (feat)
2. **Task 2: Update CORS to configurable origins and add .env.example** - `debb40b` (feat)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified
- `backend/pyproject.toml` - Added 5 missing runtime deps: chromadb, librosa, opencv-python-headless, pyyaml, soundfile
- `backend/Dockerfile` - Multi-stage build: builder (uv + python deps) + runtime (ffmpeg, libsndfile, app code)
- `backend/.dockerignore` - Excludes .env, renders, chroma, dev artifacts from Docker context
- `backend/app/config.py` - Added cors_origins list[str] and port int fields to Settings
- `backend/app/main.py` - CORS middleware now uses settings.cors_origins instead of wildcard
- `backend/.env.example` - Documents ANTHROPIC_API_KEY, CORS_ORIGINS, PORT, RENDER_DIR, CHROMA_PERSIST_DIR

## Decisions Made
- Multi-stage Docker build keeps runtime image slim by installing build-essential only in builder stage
- Pydantic Settings automatically parses JSON list strings from env vars — `CORS_ORIGINS='["https://app.vercel.app"]'` works without custom parsing
- `COPY data/ data/` in Dockerfile ensures genre YAML files are present for ChromaDB auto-seeding at startup
- uv.lock file required in Dockerfile COPY step for `uv sync --frozen` to work

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Pre-existing test failures (out of scope): `test_sse_progress` and `test_download_after_render` fail with "invalid literal for int() with base 16: ''" in `worker.py:100` — hex color parsing bug unrelated to this plan's changes. 100/102 tests pass. Logged to `deferred-items.md`.

## User Setup Required

**Railway deployment requires manual environment variable configuration:**

Set these in Railway dashboard for your backend service:
- `ANTHROPIC_API_KEY` — from https://console.anthropic.com/settings/keys
- `CORS_ORIGINS` — JSON list with your Vercel frontend URL, e.g. `["https://your-app.vercel.app"]`
- `PORT` — Railway injects this automatically (no action needed)

## Next Phase Readiness
- Backend container is deployment-ready for Railway
- Phase 05-02 can proceed: frontend Vercel deployment and environment wiring
- Blocker for full deployment: ANTHROPIC_API_KEY must be set in Railway dashboard

---
*Phase: 05-deployment-production*
*Completed: 2026-04-04*

## Self-Check: PASSED

- FOUND: backend/Dockerfile
- FOUND: backend/.dockerignore
- FOUND: backend/.env.example
- FOUND: .planning/phases/05-deployment-production/05-01-SUMMARY.md
- Commits verified: a1c29f1 (Task 1), debb40b (Task 2)
