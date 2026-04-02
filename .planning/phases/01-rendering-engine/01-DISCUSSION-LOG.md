# Phase 1: Rendering Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-02
**Phase:** 01-rendering-engine
**Areas discussed:** Effect Parameters, API Design, Loop & Render

---

## Effect Parameters

### Parameter Schema

| Option | Description | Selected |
|--------|-------------|----------|
| Shared schema | One RenderParams model — all effects read from it | |
| Per-effect presets | Each effect has its own param set | |
| Hybrid | Shared base params + per-effect overrides for unique properties | ✓ |

**User's choice:** Hybrid
**Notes:** Shared base (colors, speed, intensity) with per-effect overrides for unique properties

### Effect Selection

| Option | Description | Selected |
|--------|-------------|----------|
| User picks from list | Dropdown/selector in the generate form | |
| LLM picks from prompt | LLM analyzes prompt and selects best-matching effect | ✓ |
| Random with seed | Effect assigned randomly | |

**User's choice:** LLM picks from prompt
**Notes:** In Phase 1 (no LLM), keyword matching bridges to this

### Color Source (Phase 1)

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded per genre | Map prompt keywords to preset palettes | ✓ |
| Random palette | Generate harmonious random colors | |
| User picks colors | Color picker in the form | |

**User's choice:** Hardcoded per genre

### Phase 1 Effect Selection Fallback

| Option | Description | Selected |
|--------|-------------|----------|
| Keyword matching | Parse prompt for keyword clusters per effect | ✓ |
| API param | Require explicit effect_type field | |
| Default + override | Default to tunnel, allow optional override | |

**User's choice:** Keyword matching (clusters of keywords per effect)

### Base Parameters

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal core | bg_color, primary_color, accent_color, intensity, speed (5 params) | ✓ |
| Extended | Above + secondary_color, pulse_strength, complexity, grain, glow (10 params) | |
| You decide | Claude picks | |

**User's choice:** Minimal core (5 params)

### Per-Effect Overrides

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal overrides | 1-2 unique params per effect | ✓ |
| Rich overrides | 3-5 unique params per effect | |
| You decide | Claude designs | |

**User's choice:** Minimal overrides

### Reproducibility

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, with seed | Same seed + params = identical output | ✓ |
| No, always random | Some randomness in each render | |

**User's choice:** Yes, with seed

### Keyword Mapping Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Simple genre map | 5 genres each map to default effect + palette | |
| Keyword clusters | Multiple keywords per effect | ✓ |
| You decide | Claude designs the mapping | |

**User's choice:** Keyword clusters

### Fallback on No Match

| Option | Description | Selected |
|--------|-------------|----------|
| Random fallback | Pick random effect + neutral palette | |
| Default effect | Fall back to tunnel (most impressive) + neutral palette | ✓ |
| Error message | Return 400 | |

**User's choice:** Default to tunnel

### Schema Design Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Design for Phase 4 | Full Pydantic schema now, populate subset in Phase 1 | ✓ |
| Phase 1 only | Minimal schema, refactor later | |
| You decide | Claude judges | |

**User's choice:** Design for Phase 4

### Effect Registration

| Option | Description | Selected |
|--------|-------------|----------|
| Registry pattern | Effects register in a dict | ✓ |
| Enum + factory | EffectType enum with factory function | |
| You decide | Claude picks | |

**User's choice:** Registry pattern

---

## API Design

### Endpoint Structure

| Option | Description | Selected |
|--------|-------------|----------|
| REST standard | POST /generate, GET /jobs/{id}, GET /jobs/{id}/download, GET /health | ✓ |
| Minimal | POST /generate, GET /jobs/{id} (includes download URL), GET /health | |
| You decide | Claude designs | |

**User's choice:** REST standard (4 endpoints)

### Progress Updates

| Option | Description | Selected |
|--------|-------------|----------|
| SSE | GET /jobs/{id}/stream -> Server-Sent Events | ✓ |
| Polling | Frontend polls GET /jobs/{id} every 2s | |
| WebSocket | Bidirectional connection | |

**User's choice:** SSE

### File Serving

| Option | Description | Selected |
|--------|-------------|----------|
| Direct file serve | FastAPI FileResponse from local disk | ✓ |
| Signed URLs | Temp download URL with expiry | |
| You decide | Claude picks | |

**User's choice:** Direct file serve

---

## Loop & Render

### Loop Duration

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed 10 seconds | Fast render, all loops same length | |
| User configurable | User picks 10s/20s/30s | |
| BPM-aligned | Duration snaps to nearest complete phrase (e.g., 8 bars) | ✓ |

**User's choice:** BPM-aligned

### Dev/Preview Mode

| Option | Description | Selected |
|--------|-------------|----------|
| 480p dev mode | Render at 480p during dev, 1080p for prod | |
| Always 1080p | Consistent output from day one | |
| Both via param | API accepts resolution param, default 1080p | ✓ |

**User's choice:** Both via API param

### File Cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| TTL-based | Delete files older than 1 hour, background sweep | ✓ |
| On-demand only | Keep until disk fills, clean oldest | |
| You decide | Claude picks | |

**User's choice:** TTL-based (1 hour)

---

## Claude's Discretion

- ffmpeg encoding flags and pipe implementation
- Internal job state machine design
- Error handling and retry strategy
- Exact keyword cluster contents
- File storage directory structure
- Health endpoint detail level

## Deferred Ideas

None — discussion stayed within phase scope
