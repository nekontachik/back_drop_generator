# Phase 1: Rendering Engine - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

FastAPI backend that accepts a text prompt and BPM, renders a seamless-loop BPM-synced video with any of 4 visual effects (tunnel, fractal, particles, plasma), and reports progress via SSE — all without blocking the server. No frontend, no LLM, no audio upload in this phase.

</domain>

<decisions>
## Implementation Decisions

### Effect Parameter Schema
- **D-01:** Hybrid parameter model — shared base params + per-effect overrides
- **D-02:** Shared base params (5): bg_color, primary_color, accent_color, intensity (0-1), speed (0-1)
- **D-03:** Minimal per-effect overrides (1-2 each): tunnel(twist_speed, ring_count), fractal(zoom_rate, c_param), particles(count, connection_dist), plasma(layer_count, wave_freq)
- **D-04:** Design the full Pydantic RenderParams schema now with Phase 4 (LLM output) in mind — Phase 1 populates it from keyword matching, Phase 4 from LLM, same schema
- **D-05:** Renders are reproducible — include a random seed param. Same seed + same params = identical output.

### Effect Selection & Registration
- **D-06:** Effects registered via registry pattern: dict mapping `{"tunnel": TunnelEffect, "fractal": FractalEffect, ...}`. Easy to add new effects later.
- **D-07:** In Phase 1 (no LLM), effect selected via keyword cluster matching from text prompt. Multiple keywords per effect: tunnel=[dark, deep, industrial, techno], fractal=[psychedelic, trippy, complex, psy], etc.
- **D-08:** Fallback when no keywords match: default to tunnel effect with neutral color palette (most visually impressive)
- **D-09:** Keyword clusters map to both effect selection AND color palette. 5 genres (techno, house, ambient, industrial, psytrance) each map to default effect + colors from RAG genre docs.

### API Design
- **D-10:** REST standard endpoints: POST /generate -> {job_id}, GET /jobs/{id} -> status/progress, GET /jobs/{id}/download -> mp4 file, GET /health
- **D-11:** Progress via Server-Sent Events: GET /jobs/{id}/stream -> SSE with progress percentage. Real-time, no polling.
- **D-12:** Video files served directly from local disk via FastAPI FileResponse. Simple, sufficient for demo scale.

### Rendering Pipeline
- **D-13:** NumPy + ffmpeg pipe for frame generation (not cv2.VideoWriter). Research-validated for H.264/yuv420p cross-browser compatibility.
- **D-14:** ProcessPoolExecutor for render isolation (not asyncio.to_thread). Research-validated to avoid GIL blocking.
- **D-15:** Seamless loop math: t = frame_index / total_frames, periodic functions (sin/cos), never let t reach 1.0. Research-validated.

### Loop Duration & Resolution
- **D-16:** Loop duration is BPM-aligned — snaps to nearest complete musical phrase (e.g., 8 bars at given BPM). Musically correct, variable length.
- **D-17:** Resolution configurable via API param. Default 1080p (1920x1080 30fps), accept 480p for fast dev previews. ~4x faster iteration at 480p.
- **D-18:** TTL-based file cleanup — delete rendered files older than 1 hour. Background task sweeps periodically.

### Claude's Discretion
- Exact ffmpeg encoding flags and pipe implementation
- Internal job state machine design (pending/rendering/complete/failed)
- Error handling and retry strategy for failed renders
- Exact keyword cluster contents beyond the examples given
- File storage directory structure and naming
- Health endpoint detail level

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Research findings
- `.planning/research/STACK.md` — Technology recommendations: NumPy+OpenCV rendering, ffmpeg piping, FastAPI async patterns
- `.planning/research/ARCHITECTURE.md` — System structure, component boundaries, render pipeline design, data flow
- `.planning/research/PITFALLS.md` — Domain pitfalls: GIL blocking, seamless loop math, codec compatibility, memory management
- `.planning/research/SUMMARY.md` — Executive summary with phase ordering rationale

### Project context
- `.planning/PROJECT.md` — Core value, constraints, key decisions
- `.planning/REQUIREMENTS.md` — Phase 1 requirements: INP-01, INP-02, VFX-01-04, RND-01-04

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code

### Established Patterns
- None — patterns will be established in this phase

### Integration Points
- Phase 2 (Audio Analysis & RAG) will feed BPM data and genre-style documents into this rendering pipeline
- Phase 4 (LLM Style Blending) will populate the same RenderParams schema that Phase 1 populates via keyword matching

</code_context>

<specifics>
## Specific Ideas

- Effect selection in Phase 4 will be done by LLM analyzing the prompt — Phase 1 keyword matching is a bridge to that
- The Pydantic schema should be forward-compatible: Phase 1 fills a subset, Phase 4 fills the full thing
- BPM-aligned duration means the loop length is musically meaningful — e.g., at 120 BPM, 8 bars = 16 seconds

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-rendering-engine*
*Context gathered: 2026-04-02*
