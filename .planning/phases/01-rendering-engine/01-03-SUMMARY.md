---
phase: 01-rendering-engine
plan: 03
subsystem: api
tags: [fastapi, sse, processpool, multiprocessing, cors, rest-api]

# Dependency graph
requires:
  - phase: 01-rendering-engine/01
    provides: "Pydantic models, prompt mapper, config"
  - phase: 01-rendering-engine/02
    provides: "render_video pipeline with progress_callback"
provides:
  - "POST /generate endpoint accepting prompt+BPM, returning job_id"
  - "GET /jobs/{id} status endpoint with live progress"
  - "GET /jobs/{id}/stream SSE progress event stream"
  - "GET /jobs/{id}/download mp4 file download"
  - "GET /health non-blocking health check"
  - "In-memory job manager (create/get/update/list)"
  - "ProcessPoolExecutor worker with Manager-based progress sharing"
  - "TTL-based render file cleanup background service"
affects: [frontend, deployment, audio-analysis]

# Tech tracking
tech-stack:
  added: [fastapi-sse, multiprocessing.Manager, httpx-async-testing]
  patterns: [process-pool-render-worker, manager-dict-progress, sse-generator-endpoint, lifespan-cleanup-loop]

key-files:
  created:
    - backend/app/main.py
    - backend/app/api/__init__.py
    - backend/app/api/generate.py
    - backend/app/api/health.py
    - backend/app/api/download.py
    - backend/app/services/job_manager.py
    - backend/app/worker.py
    - backend/app/services/cleanup.py
    - backend/tests/test_api.py
  modified: []

key-decisions:
  - "Used multiprocessing.Manager dict instead of multiprocessing.Value for cross-process progress (Value cannot be pickled for ProcessPoolExecutor)"
  - "Used FastAPI native SSE with response_class=EventSourceResponse and ServerSentEvent yielding (not sse-starlette)"
  - "Callback bridge pattern: multiprocessing.Manager dict in worker wraps render_video's progress_callback interface"

patterns-established:
  - "Process worker pattern: serialize params via model_dump(), reconstruct in child process"
  - "SSE endpoint pattern: async generator yielding ServerSentEvent with response_class=EventSourceResponse"
  - "Lifespan pattern: asynccontextmanager for startup/shutdown with background cleanup task"

requirements-completed: [INP-01, INP-02, RND-03, RND-04]

# Metrics
duration: 35min
completed: 2026-04-02
---

# Phase 01 Plan 03: API Layer Summary

**FastAPI REST API with ProcessPoolExecutor rendering, SSE progress streaming, and non-blocking health check**

## Performance

- **Duration:** 35 min
- **Started:** 2026-04-02T13:03:14Z
- **Completed:** 2026-04-02T13:38:45Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Complete REST API: POST /generate, GET /jobs/{id}, GET /jobs/{id}/stream (SSE), GET /jobs/{id}/download, GET /health
- Process-isolated rendering via ProcessPoolExecutor with real-time progress via multiprocessing.Manager
- Health endpoint responds in under 1 second during active full-resolution render
- 8 integration tests covering full render flow, SSE streaming, BPM validation, download, and non-blocking health

## Task Commits

Each task was committed atomically:

1. **Task 1: Job manager, worker with ProcessPoolExecutor, and file cleanup service** - `ff9b624` (feat)
2. **Task 2: FastAPI app with all endpoints, SSE streaming, and integration tests** - `92cbb5f` (feat)

## Files Created/Modified
- `backend/app/main.py` - FastAPI app with CORS, lifespan, router includes
- `backend/app/api/__init__.py` - API package init
- `backend/app/api/generate.py` - POST /generate, GET /jobs/{id}, GET /jobs/{id}/stream endpoints
- `backend/app/api/health.py` - GET /health endpoint
- `backend/app/api/download.py` - GET /jobs/{id}/download with FileResponse
- `backend/app/services/job_manager.py` - In-memory job store with create/get/update/list
- `backend/app/worker.py` - ProcessPoolExecutor with Manager-based progress sharing
- `backend/app/services/cleanup.py` - TTL-based mp4 file cleanup background loop
- `backend/tests/test_api.py` - 8 integration tests (health, generate, BPM validation, status, SSE, download, non-blocking)

## Decisions Made
- Used `multiprocessing.Manager().dict()` instead of `multiprocessing.Value` for cross-process progress sharing because `Value` objects cannot be pickled for `ProcessPoolExecutor` (they require fork-based inheritance). Manager proxies are pickle-safe.
- Used FastAPI's built-in SSE support (`response_class=EventSourceResponse` with `ServerSentEvent` yields) rather than the external `sse-starlette` library, since FastAPI 0.135+ includes native SSE.
- Created a callback bridge in the worker: the Manager dict entry is updated by a closure that matches `render_video`'s `progress_callback: Callable[[float], None]` interface.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] multiprocessing.Value cannot be pickled for ProcessPoolExecutor**
- **Found during:** Task 2 (integration test execution)
- **Issue:** `multiprocessing.Value` objects can only be shared via fork inheritance, not pickling. ProcessPoolExecutor pickles arguments, causing "Synchronized objects should only be shared between processes through inheritance" error.
- **Fix:** Replaced `multiprocessing.Value` with `multiprocessing.Manager().dict()` which creates pickle-safe proxy objects.
- **Files modified:** backend/app/worker.py
- **Verification:** All 8 integration tests pass including SSE progress streaming
- **Committed in:** 92cbb5f (Task 2 commit)

**2. [Rule 1 - Bug] render_video uses progress_callback, not multiprocessing.Value directly**
- **Found during:** Task 1 (reading pipeline.py interface)
- **Issue:** Plan assumed `render_video` accepts `multiprocessing.Value` but it actually accepts `progress_callback: Callable[[float], None]`. Worker needed a bridge.
- **Fix:** Created callback closure that writes to Manager dict, passed as `progress_callback` to `render_video`.
- **Files modified:** backend/app/worker.py
- **Verification:** Progress values stream correctly through SSE
- **Committed in:** ff9b624 (Task 1 commit)

**3. [Rule 1 - Bug] pytest-asyncio strict mode requires @pytest_asyncio.fixture**
- **Found during:** Task 2 (test execution)
- **Issue:** Async fixture with `@pytest.fixture` fails in strict mode -- needs `@pytest_asyncio.fixture` decorator.
- **Fix:** Changed decorator to `@pytest_asyncio.fixture`
- **Files modified:** backend/tests/test_api.py
- **Verification:** All 8 tests pass
- **Committed in:** 92cbb5f (Task 2 commit)

**4. [Rule 1 - Bug] EventSourceResponse wrapping vs response_class pattern**
- **Found during:** Task 2 (SSE test execution)
- **Issue:** Wrapping generator in `EventSourceResponse(generator())` caused ServerSentEvent.encode() AttributeError. FastAPI expects the endpoint itself to be a generator with `response_class=EventSourceResponse`.
- **Fix:** Changed endpoint from returning `EventSourceResponse(generator())` to being an async generator with `response_class=EventSourceResponse` decorator.
- **Files modified:** backend/app/api/generate.py
- **Verification:** SSE events stream correctly in tests
- **Committed in:** 92cbb5f (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (4 Rule 1 bugs)
**Impact on plan:** All fixes necessary for correct cross-process communication and SSE streaming. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 01 (rendering-engine) is complete: models, effects, encoder, pipeline, API, and tests all working
- Full render pipeline accessible via REST API with SSE progress streaming
- Ready for Phase 02 (Audio Analysis & RAG) to add librosa BPM detection and genre-based style retrieval
- Ready for Phase 03 (Frontend) to consume the API endpoints

---
*Phase: 01-rendering-engine*
*Completed: 2026-04-02*
