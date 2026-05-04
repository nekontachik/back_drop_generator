# Beat Visuals — AI Backdrop Generator

Generate animated video backdrops synced to music. Upload an audio clip or describe a visual style — the system analyzes BPM, retrieves genre-matched styles via RAG, uses an LLM to creatively blend visual parameters, and renders a seamless 1080p 30fps mp4 loop synchronized to the beat.

**[Live Demo →](https://beat-visuals.vercel.app)**

![Next.js](https://img.shields.io/badge/Next.js_16-black?logo=next.js) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python_3.13-3776AB?logo=python&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 16 / React 19 / Tailwind v4)                │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐     │
│  │ Gallery  │  │ Generate     │  │ Results               │     │
│  │ Hero +   │  │ Audio upload │  │ Pipeline progress     │     │
│  │ Examples │  │ Prompt input │  │ Video player + params │     │
│  └──────────┘  └──────┬───────┘  └───────────┬───────────┘     │
└────────────────────────┼─────────────────────┼─────────────────┘
                         │ POST /generate      │ GET /generate/{id}
┌────────────────────────┼─────────────────────┼─────────────────┐
│  Backend (FastAPI)     ▼                     │                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Pipeline                             │   │
│  │                                                         │   │
│  │  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────┐ │   │
│  │  │ librosa │──▶│ ChromaDB │──▶│ Claude   │──▶│Render│ │   │
│  │  │ BPM +   │   │ RAG      │   │ 3.5 Haiku│   │Engine│ │   │
│  │  │ mood    │   │ retrieval│   │ blending │   │      │ │   │
│  │  └─────────┘   └──────────┘   └──────────┘   └──────┘ │   │
│  │                                                   │     │   │
│  │  4 effects: tunnel │ fractal │ particles │ plasma │     │   │
│  │  Multi-layer compositing with beat breathing      │     │   │
│  └───────────────────────────────────────────────────┼─────┘   │
│                                                      ▼         │
│                                              1080p 30fps mp4   │
└────────────────────────────────────────────────────────────────┘
```

## Key Engineering Decisions

**RAG for style selection, not hardcoded rules.** Genre-to-visual mapping uses ChromaDB semantic search over curated style documents. This means the system can handle prompts like "melancholic ambient with industrial textures" by retrieving and blending multiple relevant style entries, rather than requiring an exact genre match.

**LLM as creative parameter blender with structured output.** Claude 3.5 Haiku receives RAG results + audio mood vectors + user prompt and outputs validated `RenderParams` (Pydantic v2 model with typed layer configs). The LLM doesn't generate code — it fills a parameter schema that the render engine executes. This keeps LLM output deterministic and safe.

**Deterministic fallback path.** Every feature works without an API key. A keyword-based `prompt_mapper` + hand-tuned `presets.py` (12 genre presets with multi-layer compositions) ensure the app always produces output. The LLM path improves creativity; the fallback guarantees reliability.

**Frame-level rendering with NumPy, no GPU required.** Each frame is a pure NumPy array operation — tunnel perspective math, fractal iteration, particle physics, plasma wave functions. OpenCV composites layers and encodes to mp4. Runs on free-tier hosting (Railway/Render) without GPU.

**Beat-synced animation via librosa analysis.** `beat_track()` gives beat positions, `onset_strength()` drives per-frame intensity, `spectral_centroid()` maps to color brightness. Each render layer has its own `BeatResponse` mode (hard, normal, smooth) controlling how aggressively it reacts to beats.

**Multi-layer compositing system.** Each genre preset defines 2-3 visual layers with independent effects, colors, opacities, and blend modes (alpha, screen, additive). Layers have per-layer beat breathing — e.g., ambient uses smooth plasma background + gently pulsing particle foreground.

## Tech Stack

### Backend — Python

FastAPI async API, librosa audio analysis (BPM, beats, spectral features, mood vectors), ChromaDB embedded vector store for genre-style RAG, Claude 3.5 Haiku via Anthropic SDK for creative parameter blending, NumPy + OpenCV headless for frame-level rendering and video encoding, Pydantic v2 for all data validation. Tested with pytest + pytest-asyncio.

### Frontend — TypeScript

Next.js 16 with App Router and React 19, Tailwind CSS v4, custom hardware-inspired UI (rotary knob controls, channel strip meters, monospace terminal labels). SSE-based progress tracking during renders. Responsive design with canvas-animated hero background.

## Project Structure

```
backend/
├── app/
│   ├── api/            # FastAPI endpoints (analyze, generate, download, health)
│   ├── models/         # Pydantic v2 models (audio, params, job, API schemas)
│   ├── render/
│   │   ├── effects/    # 4 effect engines (tunnel, fractal, particles, plasma)
│   │   ├── pipeline.py # Multi-layer compositing orchestrator
│   │   ├── encoder.py  # OpenCV video encoding with loop math
│   │   └── presets.py  # 12 genre presets — tested multi-layer compositions
│   └── services/
│       ├── audio_analyzer.py  # librosa BPM + mood vector extraction
│       ├── rag_retriever.py   # ChromaDB semantic search
│       ├── llm_blender.py     # Claude parameter blending + fallback
│       ├── prompt_mapper.py   # Deterministic keyword→params mapping
│       └── job_manager.py     # Async job lifecycle + progress
├── data/               # Genre-style documents for ChromaDB
└── tests/

frontend/
├── src/
│   ├── app/            # Pages: gallery, generate, results/[id]
│   ├── components/
│   │   ├── gallery/    # Animated hero, carousel, session table
│   │   ├── generate/   # Terminal form, SVG knobs, channel strips
│   │   ├── results/    # Pipeline progress, video player, sidebar
│   │   └── ui/         # Design system: Button, Card, Knob, MonoLabel
│   └── lib/            # API client, types, genre color mapping
```

## Running Locally

### Prerequisites

Python 3.13+, Node.js 20+, ffmpeg

### Backend

```bash
cd backend
uv sync
cp .env.example .env         # add ANTHROPIC_API_KEY (optional — fallback works without it)
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Upload audio → BPM + mood analysis |
| `POST` | `/api/generate` | Start video generation job |
| `GET` | `/api/generate/{job_id}` | Poll job status + progress |
| `GET` | `/api/download/{job_id}` | Download rendered mp4 |
| `GET` | `/api/styles` | List genre styles from RAG store |
| `GET` | `/api/health` | Health check |

## License

MIT
