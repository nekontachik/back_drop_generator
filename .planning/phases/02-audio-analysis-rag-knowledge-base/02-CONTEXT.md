# Phase 2: Audio Analysis & RAG Knowledge Base - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Audio upload with librosa BPM detection + mood extraction, and ChromaDB genre knowledge base with RAG retrieval. Integrates into the existing FastAPI backend from Phase 1. No LLM blending (Phase 4), no frontend (Phase 3).

</domain>

<decisions>
## Implementation Decisions

### Audio Processing
- **D-01:** Accept common web audio formats: mp3, wav, ogg, m4a. librosa handles all via ffmpeg backend.
- **D-02:** Octave-error correction: return detected BPM + half + double as alternatives. User picks the correct one via BPM override.
- **D-03:** Mood vector uses raw librosa values + human-readable semantic labels ("bright", "dark", "energetic", "mellow"). Features: spectral centroid, chroma, RMS energy, onset strength.
- **D-04:** Audio file size limit: 30-60 second clips. Reject files over a reasonable size limit (e.g., 10MB).

### RAG Knowledge Base
- **D-05:** Layered genre documents — genre overview + sub-genre variants (e.g., techno + dark-techno + melodic-techno). Richer blending when LLM is added in Phase 4.
- **D-06:** ChromaDB embedded mode with default embedding model (all-MiniLM-L6-v2). Free, fast, sufficient for 15-30 docs.
- **D-07:** Seed from repo files on startup. Genre docs stored in a data/ folder, loaded and embedded when the app starts.

### API Integration
- **D-08:** Extend existing POST /generate endpoint with optional audio file field. Audio analyzed inline before render starts.
- **D-09:** BPM override via query param: POST /generate with bpm_override=128 skips audio-detected BPM and uses the provided value.
- **D-10:** BPM alternatives returned in job response: detected BPM + half + double, so frontend can show options.
- **D-11:** RAG retrieval exposed both internally (pipeline calls it) AND as public debug endpoint: GET /styles?prompt=... returns matched genre docs.

### Claude's Discretion
- Genre doc file format (markdown vs YAML vs JSON) and exact authoring approach
- ChromaDB collection naming and metadata schema
- librosa parameter tuning (hop_length, etc.)
- Audio file validation and error handling details
- BPM visualization data format (for AUD-03 — chart data structure)
- Exact mood label mapping thresholds

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing backend code
- `backend/app/models/params.py` — RenderParams schema that RAG output must integrate with
- `backend/app/models/api.py` — GenerateRequest that needs audio file field added
- `backend/app/services/prompt_mapper.py` — Current keyword mapper that RAG will complement
- `backend/app/api/generate.py` — Existing POST /generate endpoint to extend
- `backend/app/main.py` — FastAPI app for new router registration
- `backend/app/config.py` — Settings for new config values (ChromaDB path, audio limits)

### Research findings
- `.planning/research/STACK.md` — ChromaDB embedded mode, librosa patterns
- `.planning/research/ARCHITECTURE.md` — RAG integration pattern, data flow
- `.planning/research/PITFALLS.md` — librosa BPM octave errors, ChromaDB data loss on redeploy

### Phase 1 context
- `.planning/phases/01-rendering-engine/01-CONTEXT.md` — Prior decisions on RenderParams schema, API design, effect registry

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/models/params.py` — RenderParams with hybrid base+override model. RAG output must produce values compatible with this schema.
- `backend/app/services/prompt_mapper.py` — Keyword cluster mapper. RAG retrieval will complement this, and Phase 4 LLM will replace it.
- `backend/app/api/generate.py` — Existing endpoint handles POST /generate with prompt + BPM. Needs extension for file upload.
- `backend/app/config.py` — Pydantic Settings class for centralized config.

### Established Patterns
- FastAPI routers in `backend/app/api/` — new endpoints follow same pattern
- Pydantic models in `backend/app/models/` — new models go here
- Services in `backend/app/services/` — new services (audio analyzer, RAG retriever) go here
- Tests in `backend/tests/` — pytest with httpx AsyncClient

### Integration Points
- POST /generate endpoint needs multipart form data support for audio upload
- RenderParams needs no schema changes — RAG outputs values that fit existing fields
- New audio analysis service called from generate flow before render
- New RAG service called from generate flow to enhance prompt mapping
- ChromaDB initialized in app lifespan (like cleanup service)

</code_context>

<specifics>
## Specific Ideas

- BPM alternatives (detected + half + double) shown to user so they can correct octave errors
- Mood labels should be intuitive for musicians: "bright/dark", "energetic/mellow", "sparse/dense"
- Genre docs should be rich enough that "cyberpunk techno meets underwater ambient" retrieves useful blended parameters
- RAG debug endpoint useful for testing and for frontend to preview matched styles before rendering

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-audio-analysis-rag-knowledge-base*
*Context gathered: 2026-04-02*
