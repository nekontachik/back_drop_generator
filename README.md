# Beat Visuals — AI Backdrop Generator

Generate animated video backdrops synced to music. Upload an audio clip or describe a visual style — the system analyzes BPM, retrieves genre-matched styles via RAG, uses an LLM to creatively blend visual parameters, and renders a seamless 1080p 30fps mp4 loop synchronized to the beat.

**Live demo:** [beat-visuals.vercel.app](https://beat-visuals.vercel.app)

---

## How It Works

```
Audio Upload → librosa BPM/beat detection → ChromaDB genre RAG retrieval
    → Claude 3.5 Haiku creative parameter blending → NumPy + OpenCV frame rendering → mp4 encode
```

1. **Audio analysis** — librosa extracts BPM, beat positions, onset strength, and spectral features to build a mood vector
2. **RAG retrieval** — ChromaDB semantic search matches the detected genre against a curated style knowledge base
3. **LLM blending** — Claude 3.5 Haiku creatively combines RAG results, mood data, and user prompts into render parameters (with deterministic fallback)
4. **Video rendering** — NumPy array math generates frames (tunnel, fractal, particles, plasma effects) composited via OpenCV, synced to beat timing
5. **Encoding** — OpenCV VideoWriter produces a seamless looping mp4

## Tech Stack

### Backend (Python)

| Component | Technology |
|-----------|-----------|
| API | FastAPI with async endpoints |
| Audio analysis | librosa — BPM detection, beat tracking, spectral features |
| Vector store | ChromaDB (embedded) — genre-style document retrieval |
| LLM | Claude 3.5 Haiku via Anthropic SDK (OpenRouter compatible) |
| Rendering | NumPy + OpenCV — frame-level math, compositing, video encoding |
| Validation | Pydantic v2 models throughout |

### Frontend (TypeScript)

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router, React 19) |
| Styling | Tailwind CSS v4 |
| Design | Custom TE × Ableton-inspired UI — knob controls, channel strips, monospace labels |

## Visual Effects

Four procedural effect engines, each driven by beat-synced parameters:

- **Tunnel** — infinite depth tunnel with neon rings and perspective distortion
- **Fractal** — morphing fractal patterns with color evolution
- **Particles** — explosive particle systems reacting to beat energy
- **Plasma** — flowing plasma waves with spectral color mapping

Effects support multi-layer compositing with per-layer beat breathing for dynamic visuals.

## Project Structure

```
backend/
├── app/
│   ├── api/            # FastAPI endpoints (analyze, generate, download, health)
│   ├── models/         # Pydantic models (audio, params, job, API schemas)
│   ├── render/
│   │   ├── effects/    # Tunnel, fractal, particles, plasma renderers
│   │   ├── pipeline.py # Main render pipeline orchestrator
│   │   ├── encoder.py  # OpenCV video encoding
│   │   └── presets.py  # Genre-specific multi-layer presets
│   └── services/       # Audio analyzer, RAG retriever, LLM blender, job manager
├── data/               # ChromaDB genre-style documents
└── tests/

frontend/
├── src/
│   ├── app/            # Next.js pages (gallery, generate, results)
│   ├── components/
│   │   ├── gallery/    # Hero video, carousel, session table
│   │   ├── generate/   # Terminal-style form, knobs, channel strips
│   │   ├── results/    # Pipeline progress, video player, sidebar
│   │   ├── layout/     # Header, page transitions
│   │   └── ui/         # Button, Card, Badge, Knob, MonoLabel
│   └── lib/            # API client, types, utilities
```

## Setup

### Prerequisites

- Python 3.13+
- Node.js 20+
- ffmpeg (for audio format conversion)

### Backend

```bash
cd backend
uv sync                      # install dependencies
cp .env.example .env         # add your ANTHROPIC_API_KEY
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for LLM blending |
| `OPENROUTER_API_KEY` | No | Alternative LLM provider |
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL for the frontend |

The system includes a deterministic fallback — if no API key is configured, it uses keyword-based parameter mapping instead of LLM blending.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Upload audio, get BPM + mood analysis |
| `POST` | `/api/generate` | Start video generation job |
| `GET` | `/api/generate/{job_id}` | Poll job status + progress |
| `GET` | `/api/download/{job_id}` | Download rendered mp4 |
| `GET` | `/api/styles` | List available genre styles from RAG |
| `GET` | `/api/health` | Health check |

## License

MIT
