---
phase: 03-frontend-application
plan: 02
subsystem: ui
tags: [next.js, react, typescript, react-dropzone, tailwind, rag, debounce]

# Dependency graph
requires:
  - phase: 03-01
    provides: API client (submitGenerate, getStyles), TypeScript types, UI components (Button, Card), globals.css theme
  - phase: 02-audio-analysis-rag-knowledge-base
    provides: GET /styles endpoint for RAG-based style matching, POST /generate multipart endpoint
provides:
  - Generate form page at /generate with two-column layout
  - AudioUpload component with react-dropzone drag-and-drop
  - BpmInput component with detected-BPM alternative chips
  - BlendControl component with two genre dropdowns and ratio slider
  - StylePreview component with debounced 500ms live style matching
  - GenerateForm wired to submitGenerate, redirects to /results/{jobId}
affects: [03-03, results-page, deployment]

# Tech tracking
tech-stack:
  added: [react-dropzone (already installed)]
  patterns: [lifted state for cross-component prompt sharing, debounced API calls with useEffect cleanup, client component composition]

key-files:
  created:
    - frontend/src/app/generate/page.tsx
    - frontend/src/components/generate/generate-form.tsx
    - frontend/src/components/generate/style-preview.tsx
    - frontend/src/components/generate/audio-upload.tsx
    - frontend/src/components/generate/bpm-input.tsx
    - frontend/src/components/generate/blend-control.tsx
  modified: []

key-decisions:
  - "Prompt state lifted to generate/page.tsx so both GenerateForm and StylePreview receive it without prop drilling through form"
  - "StylePreview skips fetch when prompt.length < 3 to avoid noisy results on short inputs"
  - "BPM chips show rounded integers (Math.round) for cleaner UI"

patterns-established:
  - "Debounce pattern: useEffect with setTimeout + cleanup return (500ms) for live search/preview"
  - "File upload pattern: react-dropzone useDropzone hook with accept MIME types object syntax"
  - "State lifting pattern: parent page.tsx manages shared state, passes callbacks to form child"

requirements-completed: [FE-02]

# Metrics
duration: 17min
completed: 2026-04-03
---

# Phase 3 Plan 02: Generate Form Page Summary

**Two-column generate page at /generate with prompt textarea, audio dropzone, BPM input with detected-BPM chips, genre blend control, and 500ms debounced live style preview from RAG**

## Performance

- **Duration:** 17 min
- **Started:** 2026-04-03T15:00:44Z
- **Completed:** 2026-04-03T15:17:09Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Three sub-components: AudioUpload (react-dropzone), BpmInput (number + chips), BlendControl (selects + range slider)
- GenerateForm: collects all fields, submits multipart FormData to POST /generate, redirects to /results/{jobId}
- StylePreview: debounced getStyles fetch, skeleton loading state, color swatches, shape tags, match percentage
- Generate page: two-column grid, prompt state lifted from form to page so StylePreview stays in sync
- Full build passes with TypeScript strict mode

## Task Commits

1. **Task 1: Audio upload, BPM input, and blend control sub-components** - `ac682e9` (feat)
2. **Task 2: Generate form page with two-column layout and live style preview** - `889f76f` (feat)

## Files Created/Modified

- `frontend/src/app/generate/page.tsx` - Two-column client page, manages prompt state
- `frontend/src/components/generate/generate-form.tsx` - Main form with all fields and submit logic
- `frontend/src/components/generate/style-preview.tsx` - Live RAG preview with debounce
- `frontend/src/components/generate/audio-upload.tsx` - Drag-and-drop audio file input
- `frontend/src/components/generate/bpm-input.tsx` - BPM number input with detected alternatives
- `frontend/src/components/generate/blend-control.tsx` - Two genre dropdowns + blend ratio slider

## Decisions Made

- Prompt state lifted to generate/page.tsx (client component) so both GenerateForm and StylePreview can receive it — avoids prop drilling or a shared context for this simple case.
- StylePreview skips the debounced fetch entirely when prompt.length < 3, preventing noisy/irrelevant matches on minimal input.
- BPM chip values use Math.round for clean display (librosa may return float tempo values).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- /generate page fully functional: form renders, validates, submits to backend, redirects
- StylePreview wired to GET /styles — works when backend is running
- Plan 03-03 (results page) can now build on /results/{jobId} redirect target
- No blockers for next plan

## Self-Check: PASSED

All 6 files verified present. Both commits (ac682e9, 889f76f) verified in git log.

---
*Phase: 03-frontend-application*
*Completed: 2026-04-03*
