# Phase 4: LLM Style Blending - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the LLM into the generation pipeline. Text prompt + audio mood vector + RAG-retrieved genre docs feed into Claude 3.5 Haiku, which creatively blends style parameters and outputs structured JSON that drives the renderer. LLM replaces the keyword-based prompt_mapper. Includes fallback mode for no-API-key operation.

</domain>

<decisions>
## Implementation Decisions

### LLM Model & Integration
- **D-01:** Claude 3.5 Haiku via Anthropic as the blending LLM. Fast, cheap (~$0.25/1M input tokens), strong at structured JSON output.
- **D-02:** Raw Anthropic Python SDK (`anthropic` package) — no LangChain. Single-prompt use case doesn't justify the abstraction. Direct `client.messages.create()` calls.
- **D-03:** No response caching. Every request hits the LLM for unique creative output each time.
- **D-04:** API key via `ANTHROPIC_API_KEY` environment variable, loaded through existing Pydantic Settings config.

### Prompt Engineering & Chain Design
- **D-05:** Grounded creative blending — LLM interpolates within values found in retrieved genre docs. Not pure passthrough, not unconstrained invention. "70% techno + 30% ambient" produces blended colors/shapes that exist on a spectrum between the two genre docs.
- **D-06:** Full context in the prompt: RAG-retrieved genre docs, audio mood vector + semantic labels, user's blend ratio, available effect list with valid parameter ranges. LLM has everything it needs to output valid parameters.
- **D-07:** LLM also returns a 1-2 sentence creative description of the envisioned visual (e.g., "A pulsing tunnel of deep amber transitioning to cold steel blues"). Displayed on the results page.
- **D-08:** LLM output is structured JSON matching the RenderParams Pydantic schema. Effect name must be from the effect registry. All numeric values must be within specified ranges.

### Fallback & Validation
- **D-09:** On invalid LLM output (bad JSON, Pydantic validation failure): retry once with stricter instructions. If still invalid, fall back to best-matching genre doc's default parameters. User always gets a result, never an error from LLM failure.
- **D-10:** Deterministic fallback mode when ANTHROPIC_API_KEY is not set. Skip LLM entirely, use existing keyword prompt_mapper + RAG retrieval to produce parameters. Site works for demos without API cost.
- **D-11:** LLM errors (rate limits, API down, timeout) also trigger fallback to deterministic mode for that request. Log the error but don't crash.

### Claude's Discretion
- Exact prompt template wording and structure
- Temperature setting for the LLM call
- How mood vector values map to prompt context (raw numbers vs semantic descriptions)
- Pipeline wiring details — how LLM service replaces prompt_mapper in the generate flow
- Whether blend ratio is passed as percentages or normalized weights
- Timeout duration for LLM API calls
- Logging verbosity for LLM calls (for debugging and portfolio demo)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### RenderParams schema (LLM output target)
- `backend/app/models/params.py` — RenderParams with base params + per-effect overrides. LLM JSON output must validate against this schema.

### Current prompt mapping (being replaced)
- `backend/app/services/prompt_mapper.py` — Keyword cluster mapper. LLM replaces this for the primary path; kept as deterministic fallback.

### RAG retrieval (LLM input)
- `backend/app/services/rag_retriever.py` — `query_styles()` returns genre-matched docs. LLM receives these as blending context.
- `backend/data/genres/*.yaml` — 10 genre YAML docs with colors, shapes, movement. These are what the LLM blends.

### Audio analysis (LLM input)
- `backend/app/models/audio.py` — AudioAnalysis, MoodVector with spectral_centroid, chroma, rms_energy, onset_strength + semantic labels
- `backend/app/services/audio_analyzer.py` — `analyze_audio()` produces the mood vector

### API integration point
- `backend/app/api/generate.py` — POST /generate endpoint where LLM call is wired in
- `backend/app/main.py` — App lifespan for any LLM client initialization
- `backend/app/config.py` — Settings class for ANTHROPIC_API_KEY

### Effect registry
- `backend/app/render/effects/__init__.py` — Effect registry dict (tunnel, fractal, particles, plasma). LLM must pick from these.

### Prior phase decisions
- `.planning/phases/01-rendering-engine/01-CONTEXT.md` — D-04 (schema designed for Phase 4), D-07 (keyword matching as bridge)
- `.planning/phases/02-audio-analysis-rag-knowledge-base/02-CONTEXT.md` — D-05 (layered genre docs), D-11 (RAG debug endpoint)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/services/prompt_mapper.py` — GenreProfile dataclass with keywords, effect, colors. Becomes the deterministic fallback.
- `backend/app/services/rag_retriever.py` — `query_styles(prompt, n_results)` returns ranked genre matches. Ready to feed into LLM prompt.
- `backend/app/models/params.py` — Full RenderParams schema with validation. LLM output parses directly into this.
- `backend/app/models/audio.py` — MoodVector with `classify_mood()` for semantic labels. Ready for prompt context.

### Established Patterns
- Services in `backend/app/services/` — new LLM service follows same pattern
- Pydantic Settings in `backend/app/config.py` — add ANTHROPIC_API_KEY here
- Effect registry in `backend/app/render/effects/__init__.py` — LLM must reference these names

### Integration Points
- `generate.py` currently calls `prompt_mapper.map_prompt()` to get RenderParams. LLM service replaces this call.
- Mood vector from `audio_analyzer.analyze_audio()` is already in the generate flow — just needs to be passed to LLM.
- RAG results from `rag_retriever.query_styles()` already called in generate flow — pass to LLM instead of discarding.

</code_context>

<specifics>
## Specific Ideas

- The creative description from the LLM adds personality to the results page — "A pulsing tunnel of deep amber transitioning to cold steel blues" makes it feel AI-powered
- Deterministic fallback means the site works at hackathons/demos without burning API credits
- Grounded creativity (interpolating within RAG values) ensures visuals are always aesthetically coherent — no random garbage colors
- The prompt should include exact Pydantic field names and types so the LLM outputs valid JSON on the first try

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-llm-style-blending*
*Context gathered: 2026-04-03*
