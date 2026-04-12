---
phase: 07-fix-data-contract-bpm-override
plan: 01
subsystem: api
tags: [chromadb, rag, llm, langchain, typescript, nextjs, fastapi]

# Dependency graph
requires:
  - phase: 06-fix-integration-bugs
    provides: hex color parsing guard, sessionStorage key fix, bpm_override wiring scaffold
provides:
  - Flat query_styles() return matching frontend StyleMatch interface
  - Updated LLM blender reading from flat dict structure
  - bpm_override sent on first submit whenever audio file is attached
affects: [frontend style preview cards, results sidebar matched-styles, audio BPM override]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - query_styles() returns flat dicts matching TypeScript interface (no nested metadata layer)
    - LLM blender reads genre/description/colors directly from doc root (no doc.metadata indirection)

key-files:
  created: []
  modified:
    - backend/app/services/rag_retriever.py
    - backend/app/services/llm_blender.py
    - backend/tests/test_rag_retriever.py
    - backend/tests/test_api.py
    - frontend/src/components/generate/generate-form.tsx

key-decisions:
  - "Flatten at retrieval boundary (query_styles return) not storage — no ChromaDB migration required"
  - "bpm_override sent whenever audioFile present (not gated on detectedBpm) — backend detected BPM takes precedence when user hasn't changed the slider"

patterns-established:
  - "StyleMatch interface contract: {id, genre, description, colors, shapes, movement, intensity, speed, distance} — all flat at root"

requirements-completed: [RAG-02, FE-02, AUD-04]

# Metrics
duration: 34min
completed: 2026-04-12
---

# Phase 07 Plan 01: Fix Data Contract & BPM Override Summary

**Flattened query_styles() return dict to match TypeScript StyleMatch interface and fixed bpm_override guard to send on first audio submit**

## Performance

- **Duration:** 34 min
- **Started:** 2026-04-12T06:33:52Z
- **Completed:** 2026-04-12T07:07:52Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- query_styles() now returns flat dicts {id, genre, description, colors, shapes, movement, intensity, speed, effect_preference, distance} matching the frontend StyleMatch TypeScript interface exactly — style preview cards and results sidebar will now display genre, color swatches, and shape tags correctly
- LLM blender _build_prompt() and _deterministic_fallback() updated to read genre/description/colors/intensity/speed directly from flat doc root (removed nested metadata layer)
- bpm_override FormData field now sent whenever audioFile is present — previously gated on `detectedBpm` which is only populated after the API response, making BPM chip selection (half/double tempo) never apply on first submit
- All 103 backend tests pass including updated test_rag_retriever.py and test_api.py assertions

## Task Commits

Each task was committed atomically:

1. **Task 1: Flatten query_styles() return dict and update all backend consumers** - `ac9bdd3` (feat)
2. **Task 2: Fix bpm_override guard to send on first submit** - `a97f9ad` (fix)
3. **Auto-fix: update test_styles_endpoint to assert flat dict structure** - `8f2e4db` (fix)

**Plan metadata:** (committed with state update docs)

_Note: Task 1 was executed with TDD flow (RED → GREEN)_

## Files Created/Modified
- `backend/app/services/rag_retriever.py` - query_styles() returns flat dicts matching StyleMatch interface
- `backend/app/services/llm_blender.py` - _build_prompt() and _deterministic_fallback() read from flat doc root
- `backend/tests/test_rag_retriever.py` - Updated assertions: flat keys, renamed test, added test_colors_and_shapes_are_lists
- `backend/tests/test_api.py` - Updated test_styles_endpoint assertions to flat structure
- `frontend/src/components/generate/generate-form.tsx` - bpm_override guard simplified to `if (audioFile)`

## Decisions Made
- Flatten at retrieval boundary (query_styles return) not storage — no ChromaDB migration required, existing seeder unchanged
- bpm_override sent whenever audioFile present — if user hasn't changed the BPM slider, default (120) is sent which is acceptable since backend's librosa-detected BPM will be used in analysis; the override only matters when user has actively applied a half/double chip

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_api.py::test_styles_endpoint still referenced old nested structure**
- **Found during:** Full backend test suite run after Task 1 commit
- **Issue:** test_api.py line 311-313 asserted `"document"` and `"metadata"` keys and `data[0]["metadata"]["genre"]` — all referencing the old nested structure that was just removed
- **Fix:** Updated assertions to check flat keys: `description`, `genre`, `colors`, `shapes`
- **Files modified:** `backend/tests/test_api.py`
- **Verification:** Full 103-test suite passes
- **Committed in:** `8f2e4db`

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug, stale test assertions after data contract change)
**Impact on plan:** Auto-fix necessary for test correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed test_api.py stale assertions.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 3 v1.0 milestone audit gaps (RAG-02, FE-02, AUD-04) are now closed
- Style preview cards have correct data contract — frontend can display genre, colors, shapes
- BPM override sends on first audio submit
- 103 backend tests pass, frontend builds cleanly
- v1.0 milestone is ready for completion audit

---
*Phase: 07-fix-data-contract-bpm-override*
*Completed: 2026-04-12*
