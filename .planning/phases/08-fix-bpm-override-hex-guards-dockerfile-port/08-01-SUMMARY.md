---
phase: 08-fix-bpm-override-hex-guards-dockerfile-port
plan: 01
subsystem: api
tags: [bpm, audio, hex-color, docker, railway, fastapi, react]

# Dependency graph
requires:
  - phase: 07
    provides: bpm_override form data submission and query_styles dict contract
  - phase: 05
    provides: Dockerfile multi-stage build structure
provides:
  - bpmTouched flag in generate-form.tsx so bpm_override only sent on explicit user slider interaction
  - hex guard (if not h:) in fractal.py, particles.py, plasma.py matching tunnel.py pattern
  - Dockerfile CMD reads Railway PORT env var with ${PORT:-8000} fallback
  - Dead code removed: getJobStatus from api.ts, GenerateRequest from models/api.py
affects: [deployment, frontend, rendering-pipeline]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - bpmTouched boolean state pattern for distinguishing default vs user-changed slider values
    - Shell-form Dockerfile CMD with ${VAR:-default} for Railway env var injection

key-files:
  created: []
  modified:
    - frontend/src/components/generate/generate-form.tsx
    - backend/app/render/effects/fractal.py
    - backend/app/render/effects/particles.py
    - backend/app/render/effects/plasma.py
    - backend/Dockerfile
    - frontend/src/lib/api.ts
    - backend/app/models/api.py

key-decisions:
  - "bpmTouched state initialized false, set true only on BpmInput onChange — prevents bpm_override being sent on first audio submit"
  - "Reset bpmTouched to false when audio file removed — keeps form state consistent across upload/remove cycles"
  - "Shell-form Dockerfile CMD (not exec-form) required for ${PORT:-8000} shell variable expansion"

patterns-established:
  - "bpmTouched pattern: track whether user has explicitly changed a default-valued input before including it in form submission"
  - "Hex guard pattern: lstrip('#') then 'if not h: return black' before int conversion — consistent across all 4 effects"

requirements-completed: [AUD-04, DEP-02]

# Metrics
duration: 12min
completed: 2026-04-13
---

# Phase 8 Plan 01: Fix BPM Override, Hex Guards, Dockerfile PORT Summary

**bpmTouched flag prevents librosa BPM from being silenced on first submit; empty-hex guard standardized across all 4 effects; Dockerfile now reads Railway PORT env var**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-13T04:47:00Z
- **Completed:** 2026-04-13T04:59:18Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Fixed AUD-04: `bpm_override` only sent when user explicitly changes BPM slider via `bpmTouched` state; librosa-detected BPM drives rendering on first audio submit
- Fixed DEP-02: Dockerfile CMD uses shell form `${PORT:-8000}` so Railway's injected PORT env var is respected; HEALTHCHECK also reads PORT dynamically
- Hardened 3 effect renderers (fractal, particles, plasma) with empty-string hex guard matching tunnel.py pattern — all 4 effects now handle empty/malformed hex identically
- Removed dead code: `getJobStatus` function from `frontend/src/lib/api.ts` and `GenerateRequest` class + `Field` import from `backend/app/models/api.py`

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix bpm_override logic and hex color guards** - `0790480` (fix)
2. **Task 2: Fix Dockerfile PORT and remove dead code** - `665bae8` (fix)

**Plan metadata:** (docs commit below)

## Files Created/Modified
- `frontend/src/components/generate/generate-form.tsx` - Added bpmTouched state; conditioned bpm_override submission; wired BpmInput onChange; reset on file removal
- `backend/app/render/effects/fractal.py` - Added `if not h: return black` guard in _hex_to_rgb
- `backend/app/render/effects/particles.py` - Added `if not h: return black` guard in _hex_to_rgb
- `backend/app/render/effects/plasma.py` - Added `if not h: return black` guard in _hex_to_rgb
- `backend/Dockerfile` - Shell-form CMD with ${PORT:-8000}; HEALTHCHECK reads PORT from os.environ
- `frontend/src/lib/api.ts` - Removed getJobStatus function and JobStatusResponse import
- `backend/app/models/api.py` - Removed GenerateRequest class and Field import

## Decisions Made
- bpmTouched state initialized to false and reset to false when audio file is removed — this ensures that removing and re-uploading audio resets to "let librosa decide" behavior
- Shell-form Dockerfile CMD required (not exec-form array) because exec-form does not perform shell variable expansion; `${PORT:-8000}` only works in shell form
- `JobStatusResponse` type kept in `types.ts` (not deleted) since it is a type definition file — only the import in `api.ts` was removed alongside the deleted function

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None - no stubs in modified files that affect plan goal.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- AUD-04 and DEP-02 gaps from v1.0 milestone audit are now closed
- All 4 effects handle empty hex strings identically — rendering pipeline is hardened
- Dockerfile is production-ready for Railway deployment with dynamic PORT
- v1.0 milestone should be re-audited to confirm all gaps closed

## Self-Check: PASSED

- SUMMARY.md: FOUND
- generate-form.tsx: FOUND (bpmTouched pattern verified)
- fractal.py, particles.py, plasma.py: FOUND (hex guards verified)
- Dockerfile: FOUND (PORT env var verified)
- Task 1 commit 0790480: FOUND
- Task 2 commit 665bae8: FOUND

---
*Phase: 08-fix-bpm-override-hex-guards-dockerfile-port*
*Completed: 2026-04-13*
