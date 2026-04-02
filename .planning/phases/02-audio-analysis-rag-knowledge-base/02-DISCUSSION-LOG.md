# Phase 2: Audio Analysis & RAG Knowledge Base - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-02
**Phase:** 02-audio-analysis-rag-knowledge-base
**Areas discussed:** Audio Processing, RAG Knowledge Base, API Integration

---

## Audio Processing

### Audio Formats

| Option | Description | Selected |
|--------|-------------|----------|
| Common web formats | mp3, wav, ogg, m4a — covers 95% of use cases | ✓ |
| WAV only | Simplest, no transcoding | |
| Any format | Accept anything ffmpeg decodes | |

**User's choice:** Common web formats (mp3, wav, ogg, m4a)

### Octave-Error Correction

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-correct heuristic | If <80 double, if >160 halve | |
| Show alternatives | Return detected + half + double as options | ✓ |
| You decide | Claude picks | |

**User's choice:** Show alternatives — user picks the right BPM

### Mood Vector Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Normalized 0-1 vector | Each feature normalized, simple for LLM | |
| Raw values + labels | Keep raw values with semantic labels | ✓ |
| You decide | Claude designs | |

**User's choice:** Raw values + human-readable labels

---

## RAG Knowledge Base

### Genre Doc Structure

| Option | Description | Selected |
|--------|-------------|----------|
| One doc per genre | 5 docs, each with full style info | |
| One doc per aspect | 15+ granular docs | |
| Layered docs | Genre overview + sub-genre variants | ✓ |

**User's choice:** Layered docs (genre + sub-genre variants)

### Embedding Model

| Option | Description | Selected |
|--------|-------------|----------|
| Default (all-MiniLM-L6-v2) | Free, fast, good enough for small KB | ✓ |
| OpenAI embeddings | Better quality but adds cost | |
| You decide | Claude picks | |

**User's choice:** Default ChromaDB embedding model

### Seeding Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Markdown files in repo | Genre docs as .md, seed on startup | |
| JSON/YAML config | Structured data files | |
| You decide | Claude picks most maintainable | ✓ |

**User's choice:** Claude's discretion

---

## API Integration

### Audio Upload Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Extend POST /generate | Add optional file field to existing endpoint | ✓ |
| Separate endpoint | POST /analyze-audio then POST /generate | |
| Two-step in one | POST /generate returns analysis first, then render | |

**User's choice:** Extend POST /generate with optional audio file field

### BPM Override Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Query param on generate | POST /generate with bpm_override=128 | ✓ |
| Separate confirm step | POST /analyze then PATCH to confirm | |
| You decide | Claude designs based on frontend needs | |

**User's choice:** Query param on generate

### RAG Endpoint

| Option | Description | Selected |
|--------|-------------|----------|
| Internal only | RAG called internally, no public API | |
| Public endpoint | GET /styles?prompt=... for debugging | |
| Both | Internal pipeline + debug endpoint | ✓ |

**User's choice:** Both internal and public debug endpoint

---

## Claude's Discretion

- Genre doc file format and authoring approach
- ChromaDB collection naming and metadata
- librosa parameter tuning
- Audio validation details
- BPM chart data format
- Mood label thresholds

## Deferred Ideas

None — discussion stayed within phase scope
