---
phase: 04-llm-style-blending
plan: 01
subsystem: api
tags: [anthropic, llm, rag, pydantic, python, fallback, tdd]

requires:
  - phase: 03-frontend-application
    provides: frontend consuming API endpoints
  - phase: 02-audio-rag
    provides: MoodVector model, RenderParams model, RAG retriever, prompt_mapper

provides:
  - LLM blending service (blend_style async function)
  - BlendResult model with params + creative_description + source
  - Deterministic fallback via map_prompt_to_params when LLM unavailable
  - ANTHROPIC_API_KEY optional config field in Settings

affects: [04-llm-style-blending, deployment, api-integration]

tech-stack:
  added: [anthropic>=0.40]
  patterns:
    - "LLM-with-fallback: try LLM -> retry on bad JSON -> fall back to deterministic"
    - "BlendResult data class wraps params + metadata (source, description)"
    - "Settings.anthropic_api_key: str | None = None for optional LLM gating"

key-files:
  created:
    - backend/app/services/llm_blender.py
    - backend/tests/test_llm_blender.py
  modified:
    - backend/pyproject.toml
    - backend/app/config.py
    - backend/.env.example

key-decisions:
  - "Used anthropic SDK directly (not LangChain wrapper) — simpler, fewer moving parts for single-call use case"
  - "claude-3-5-haiku-latest for cost/speed balance at 0.8 temperature for creative output"
  - "BlendResult is a plain Python class (not Pydantic BaseModel) — params field is already validated RenderParams"
  - "Retry on invalid JSON with stricter prompt appended to conversation history (not a fresh call)"
  - "Fallback overrides colors/intensity/speed from top RAG doc when genre_docs available"

patterns-established:
  - "LLM fallback: check settings.anthropic_api_key at call time (not import time)"
  - "Prompt structure: user prompt + RAG docs + blend instruction + mood context + schema + available effects"
  - "APIError catch-all: anthropic.APIError, anthropic.APITimeoutError, Exception — all trigger fallback"

requirements-completed: [LLM-01, LLM-02, LLM-03]

duration: 27min
completed: 2026-04-03
---

# Phase 04 Plan 01: LLM Style Blending Service Summary

**Claude 3.5 Haiku blending service with retry logic, mood-aware prompts, and deterministic fallback to keyword matching when API key absent**

## Performance

- **Duration:** 27 min
- **Started:** 2026-04-03T18:59:21Z
- **Completed:** 2026-04-03T19:26:29Z
- **Tasks:** 2
- **Files modified:** 5 (modified) + 2 (created) = 7

## Accomplishments

- Installed anthropic SDK and added optional `anthropic_api_key` to Settings with None default
- Created `blend_style()` async function: LLM call with retry on invalid JSON, fallback on error
- BlendResult model returns validated RenderParams + creative_description + source tag
- Prompt builder injects mood vector labels (bright/energetic/dense), blend ratio percentages, RAG docs, and JSON schema
- 7 TDD tests covering all paths: fallback, success, retry, API error, mood/blend ratio in prompt, creative description

## Task Commits

Each task was committed atomically:

1. **Task 1: Add anthropic SDK and ANTHROPIC_API_KEY config** - `b29d734` (feat)
2. **Task 2: Create LLM blender service with fallback and tests** - `5632fb0` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `backend/app/services/llm_blender.py` - LLM blending service: blend_style(), _build_prompt(), _deterministic_fallback(), _parse_response()
- `backend/tests/test_llm_blender.py` - 7 pytest-asyncio tests covering all execution paths
- `backend/pyproject.toml` - Added anthropic>=0.40 dependency
- `backend/app/config.py` - Added `anthropic_api_key: str | None = None` to Settings
- `backend/.env.example` - Added ANTHROPIC_API_KEY comment and placeholder
- `backend/uv.lock` - Updated with anthropic 0.89.0 and transitive deps

## Decisions Made

- Used anthropic SDK directly rather than LangChain wrapper — single-call use case doesn't need LangChain overhead, simpler to test with mocks
- claude-3-5-haiku-latest selected for cost/speed at temperature 0.8 — creative enough without being unpredictable
- BlendResult as plain class (not Pydantic BaseModel) since params field is already validated RenderParams
- Retry strategy: append invalid response + correction request to conversation history (not a fresh call) — gives model context about what went wrong

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `uv pip install -e .` failed due to setuptools flat-layout discovery conflict (app/ and data/ both exist). Resolved by installing anthropic directly with `uv pip install "anthropic>=0.40"` and running tests via `uv run python -m pytest` which uses the .venv correctly.
- 2 pre-existing test failures in `test_api.py` (test_styles_endpoint, test_styles_endpoint_custom_count) — ChromaDB session scope issue unrelated to this plan. Logged as out-of-scope, not fixed.

## Known Stubs

None — blend_style() returns real RenderParams from either LLM or keyword fallback. No placeholder data flows to UI rendering.

## Next Phase Readiness

- LLM blender service is importable and ready for integration into the render pipeline
- blend_style() needs to be wired into the POST /generate endpoint (Plan 04-02)
- ANTHROPIC_API_KEY can be set in .env to enable real LLM calls; runs in fallback mode without it

---
*Phase: 04-llm-style-blending*
*Completed: 2026-04-03*
