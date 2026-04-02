# Phase 2: Audio Analysis & RAG Knowledge Base - Research

**Researched:** 2026-04-02
**Domain:** Audio analysis (librosa), vector search (ChromaDB), FastAPI file uploads
**Confidence:** HIGH

## Summary

This phase adds two independent subsystems to the existing FastAPI backend: (1) audio analysis via librosa for BPM detection, beat timestamps, and mood feature extraction, and (2) a ChromaDB-backed RAG knowledge base for genre-style document retrieval. Both integrate into the existing POST /generate endpoint and follow established project patterns (services in `app/services/`, models in `app/models/`, routers in `app/api/`).

The key technical challenges are: librosa on Python 3.13 requires manual installation of `standard-aifc` and `standard-sunau` packages; ChromaDB has moved to version 1.x with a Rust backend (significant API stability from 0.4+ onwards); FastAPI cannot combine UploadFile with Pydantic Form models, requiring separate function parameters; and librosa's `beat_track` returns tempo as an ndarray (not a scalar float), which needs explicit extraction.

**Primary recommendation:** Use librosa 0.11.0 directly (no LangChain for audio), ChromaDB 1.5.x with `PersistentClient` for embedded mode, and `langchain-chroma` 1.1.0 as the bridge for Phase 4 LLM integration. For this phase, use ChromaDB directly without LangChain wrappers since no LLM chain is needed yet.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Accept common web audio formats: mp3, wav, ogg, m4a. librosa handles all via ffmpeg backend.
- **D-02:** Octave-error correction: return detected BPM + half + double as alternatives. User picks the correct one via BPM override.
- **D-03:** Mood vector uses raw librosa values + human-readable semantic labels ("bright", "dark", "energetic", "mellow"). Features: spectral centroid, chroma, RMS energy, onset strength.
- **D-04:** Audio file size limit: 30-60 second clips. Reject files over a reasonable size limit (e.g., 10MB).
- **D-05:** Layered genre documents -- genre overview + sub-genre variants (e.g., techno + dark-techno + melodic-techno). Richer blending when LLM is added in Phase 4.
- **D-06:** ChromaDB embedded mode with default embedding model (all-MiniLM-L6-v2). Free, fast, sufficient for 15-30 docs.
- **D-07:** Seed from repo files on startup. Genre docs stored in a data/ folder, loaded and embedded when the app starts.
- **D-08:** Extend existing POST /generate endpoint with optional audio file field. Audio analyzed inline before render starts.
- **D-09:** BPM override via query param: POST /generate with bpm_override=128 skips audio-detected BPM and uses the provided value.
- **D-10:** BPM alternatives returned in job response: detected BPM + half + double, so frontend can show options.
- **D-11:** RAG retrieval exposed both internally (pipeline calls it) AND as public debug endpoint: GET /styles?prompt=... returns matched genre docs.

### Claude's Discretion
- Genre doc file format (markdown vs YAML vs JSON) and exact authoring approach
- ChromaDB collection naming and metadata schema
- librosa parameter tuning (hop_length, etc.)
- Audio file validation and error handling details
- BPM visualization data format (for AUD-03 -- chart data structure)
- Exact mood label mapping thresholds

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INP-03 | User can upload a short audio clip (30-60s) for analysis | FastAPI UploadFile with separate Form parameters; ffmpeg converts to wav; 10MB limit via python-multipart |
| AUD-01 | librosa extracts tempo and beat timestamps from uploaded audio | `librosa.beat.beat_track(y=y, sr=22050, units='time')` returns tempo ndarray + beat positions |
| AUD-02 | librosa extracts spectral centroid, chroma, RMS energy, onset strength as mood vector | `librosa.feature.spectral_centroid`, `chroma_stft`, `rms`, `librosa.onset.onset_strength` |
| AUD-03 | BPM visualization chart displayed on results page | Return beat timestamps + onset strength envelope as JSON arrays for frontend charting |
| AUD-04 | User can override detected BPM (fix octave errors) | Return `bpm_detected`, `bpm_half`, `bpm_double` in response; accept `bpm_override` parameter |
| RAG-01 | ChromaDB knowledge base stores genre-style documents (colors, shapes, movement) | ChromaDB 1.5.x PersistentClient with genre docs seeded from `data/genres/` on startup |
| RAG-02 | RAG retrieves relevant style docs based on prompt + genre | `collection.query(query_texts=[prompt], n_results=3)` returns matched genre-style documents |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| librosa | 0.11.0 | BPM detection, beat tracking, feature extraction | De facto standard for MIR in Python; latest release supports Python 3.13 and NumPy 2.x |
| chromadb | ~1.5.5 | Embedded vector store for genre-style documents | Local embedded mode, zero-config, Rust backend since 1.0 for better performance |
| soundfile | ~0.13.1 | Audio I/O backend for librosa | librosa's recommended backend; handles wav/flac/ogg natively |
| standard-aifc | latest | Python 3.13 compatibility shim | Required by librosa on Python 3.13 (removed from stdlib) |
| standard-sunau | latest | Python 3.13 compatibility shim | Required by librosa on Python 3.13 (removed from stdlib) |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| langchain-chroma | 1.1.0 | LangChain-ChromaDB bridge | Install now but primary use in Phase 4 when LLM chain is added |
| python-multipart | ~0.0.22 (already installed) | File upload parsing | Required by FastAPI for multipart form data (already in pyproject.toml) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ChromaDB direct API | langchain-chroma wrapper | Direct API is simpler for Phase 2 (no LLM chain yet); wrapper adds value in Phase 4 |
| librosa 0.11.0 | librosa 0.10.2 | 0.10.2 has worse Python 3.13 support; 0.11.0 is current and stable |
| ChromaDB 1.5.x | ChromaDB 0.5.x (per CLAUDE.md) | CLAUDE.md says ~0.5+; actual latest is 1.5.5 with Rust backend. Use 1.x -- significantly better performance and actively maintained |
| sentence-transformers (explicit) | ChromaDB default embeddings | ChromaDB 1.x uses all-MiniLM-L6-v2 by default via its own embedding -- no need to install sentence-transformers separately unless custom model needed |

**Installation:**
```bash
cd backend
uv pip install librosa~=0.11.0 soundfile~=0.13.0 chromadb~=1.5.0 langchain-chroma~=1.1.0 standard-aifc standard-sunau
```

**Version verification:**
- librosa: 0.11.0 (latest, confirmed via PyPI 2026-04-02)
- chromadb: 1.5.5 (latest, confirmed via PyPI 2026-04-02)
- soundfile: 0.13.1 (latest, confirmed via PyPI 2026-04-02)
- langchain-chroma: 1.1.0 (latest, confirmed via PyPI 2026-04-02)

**IMPORTANT NOTE on sentence-transformers:** ChromaDB 1.x bundles its own default embedding (all-MiniLM-L6-v2) via `onnxruntime`. You do NOT need to install `sentence-transformers` (which pulls PyTorch ~2GB). If ChromaDB's bundled embedding doesn't work, fall back to installing `sentence-transformers` explicitly.

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── generate.py          # Extended: add UploadFile parameter
│   │   └── styles.py            # NEW: GET /styles?prompt=... debug endpoint
│   ├── models/
│   │   ├── api.py               # Extended: audio analysis response fields
│   │   ├── audio.py             # NEW: AudioAnalysis, MoodVector, BpmResult
│   │   └── params.py            # Unchanged -- RAG outputs fit existing schema
│   └── services/
│       ├── audio_analyzer.py    # NEW: librosa BPM + mood extraction
│       ├── rag_retriever.py     # NEW: ChromaDB init + query
│       ├── genre_seeder.py      # NEW: Load genre docs from data/ into ChromaDB
│       └── prompt_mapper.py     # Unchanged for now (RAG complements it)
├── data/
│   ├── renders/                 # Existing
│   └── genres/                  # NEW: genre-style YAML documents
│       ├── techno.yaml
│       ├── dark-techno.yaml
│       ├── house.yaml
│       ├── deep-house.yaml
│       ├── ambient.yaml
│       ├── psytrance.yaml
│       └── ...
└── tests/
    ├── test_audio_analyzer.py   # NEW
    ├── test_rag_retriever.py    # NEW
    └── fixtures/
        └── test_tone.wav        # NEW: generated sine wave for testing
```

### Pattern 1: Audio Analysis Service
**What:** Stateless service function that accepts audio bytes, runs librosa analysis, returns structured result.
**When to use:** Called from generate endpoint when audio file is provided.
**Example:**
```python
# Source: librosa 0.11.0 official docs
import librosa
import numpy as np
from io import BytesIO

def analyze_audio(audio_bytes: bytes) -> AudioAnalysis:
    """Analyze audio clip for BPM, beats, and mood features."""
    # Load audio at 22050 Hz (librosa default, optimal for beat detection)
    y, sr = librosa.load(BytesIO(audio_bytes), sr=22050)

    # Beat tracking -- tempo is ndarray, extract scalar
    tempo_arr, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo_arr[0]) if tempo_arr.ndim > 0 else float(tempo_arr)

    # Beat timestamps in seconds
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # Octave-error alternatives (D-02)
    bpm_result = BpmResult(
        detected=round(bpm),
        half=round(bpm / 2),
        double=round(bpm * 2),
    )

    # Mood features (D-03)
    spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    chroma = librosa.feature.chroma_stft(y=y, sr=sr).mean(axis=1).tolist()
    rms = float(np.mean(librosa.feature.rms(y=y)))
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_mean = float(np.mean(onset_env))

    # Onset envelope for visualization (AUD-03)
    onset_times = librosa.times_like(onset_env, sr=sr).tolist()
    onset_values = onset_env.tolist()

    return AudioAnalysis(
        bpm=bpm_result,
        beat_times=beat_times,
        mood=MoodVector(
            spectral_centroid=spectral_centroid,
            chroma=chroma,
            rms=rms,
            onset_strength=onset_mean,
            labels=classify_mood(spectral_centroid, rms, onset_mean),
        ),
        visualization=BpmVisualization(
            onset_times=onset_times,
            onset_values=onset_values,
            beat_times=beat_times,
        ),
    )
```

### Pattern 2: ChromaDB Genre Seeding on Startup
**What:** Load YAML genre docs from `data/genres/` and upsert into ChromaDB collection during app lifespan.
**When to use:** App startup (lifespan context manager in main.py).
**Example:**
```python
# Source: ChromaDB 1.x official docs
import chromadb
from pathlib import Path
import yaml

def init_genre_collection(persist_dir: str = "data/chroma") -> chromadb.Collection:
    """Initialize ChromaDB and seed genre documents."""
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name="genre_styles",
        metadata={"hnsw:space": "cosine"},
    )

    # Load and upsert genre docs from YAML files
    genres_dir = Path("data/genres")
    if genres_dir.exists():
        docs, ids, metadatas = [], [], []
        for yaml_file in sorted(genres_dir.glob("*.yaml")):
            genre_data = yaml.safe_load(yaml_file.read_text())
            docs.append(genre_data["description"])
            ids.append(genre_data["id"])
            metadatas.append({
                "genre": genre_data["genre"],
                "subgenre": genre_data.get("subgenre", ""),
                "colors": ",".join(genre_data.get("colors", [])),
                "shapes": ",".join(genre_data.get("shapes", [])),
                "movement": genre_data.get("movement", ""),
            })

        if docs:
            collection.upsert(documents=docs, ids=ids, metadatas=metadatas)

    return collection
```

### Pattern 3: FastAPI File Upload with Form Fields
**What:** FastAPI cannot combine UploadFile inside a Pydantic Form model. Use separate function parameters.
**When to use:** Extending POST /generate to accept optional audio file.
**Example:**
```python
# Source: FastAPI official docs on file uploads
from fastapi import UploadFile, File, Form

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    prompt: str = Form(...),
    bpm: int = Form(120),
    bpm_override: int | None = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    seed: int | None = Form(None),
    audio: UploadFile | None = File(None),
) -> GenerateResponse:
    """Accept prompt + optional audio, start rendering."""
    audio_analysis = None
    if audio is not None:
        audio_bytes = await audio.read()
        validate_audio(audio_bytes, audio.filename)
        audio_analysis = analyze_audio(audio_bytes)

    # Use bpm_override if provided, else audio-detected, else form bpm
    effective_bpm = bpm_override or (audio_analysis.bpm.detected if audio_analysis else bpm)
    ...
```

### Pattern 4: Genre Document YAML Format
**What:** YAML files in `data/genres/` describe visual style parameters for each genre/subgenre.
**When to use:** Authoring genre knowledge base documents.
**Example:**
```yaml
# data/genres/techno.yaml
id: "techno-core"
genre: "techno"
subgenre: ""
description: >
  Techno: dark, industrial, mechanical rhythms. Deep bass-driven patterns
  with sharp geometric visuals. Monochrome with neon accent flashes.
  Tunnel perspectives, grid lines, strobing on beat drops. High energy,
  relentless forward motion. Think Berlin warehouse at 3am.
colors:
  - "#0a0a0a"   # deep black background
  - "#00ff88"   # neon green primary
  - "#ff0066"   # hot pink accent
shapes:
  - "tunnel"
  - "grid"
  - "sharp_geometry"
movement: "fast_forward"
intensity: 0.8
speed: 0.7
effect_preference: "tunnel"
```

### Anti-Patterns to Avoid
- **Putting audio analysis in the endpoint handler directly:** Extract to a service function for testability and reuse.
- **Using `chromadb.Client()` (in-memory):** Use `PersistentClient` so genre embeddings survive restarts (D-07 requires seeding from files, but persistence avoids re-embedding on every startup).
- **Converting GenerateRequest to use Form() globally:** This changes the existing JSON API. Instead, the endpoint now accepts multipart form data, which is a breaking change from the Phase 1 JSON body. Document this clearly.
- **Installing sentence-transformers explicitly:** ChromaDB 1.x includes default embeddings via onnxruntime. Only install sentence-transformers if the default fails.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| BPM detection | Custom autocorrelation | `librosa.beat.beat_track()` | Handles edge cases (silence, variable tempo, multi-channel) |
| Audio format conversion | Manual ffmpeg subprocess | `librosa.load()` with ffmpeg backend | librosa handles format detection and conversion internally |
| Text embedding | Custom word2vec/TFIDF | ChromaDB default embeddings (all-MiniLM-L6-v2) | Battle-tested, zero config, semantic similarity out of the box |
| Audio file validation | Manual header parsing | Check file extension + let librosa.load() fail gracefully | librosa raises clear errors for unsupported formats |
| Onset strength envelope | Manual spectral flux | `librosa.onset.onset_strength()` | Handles normalization, hop alignment, spectrogram computation |

## Common Pitfalls

### Pitfall 1: librosa beat_track Returns ndarray, Not Float
**What goes wrong:** `tempo, beats = librosa.beat.beat_track(y=y, sr=sr)` -- `tempo` is a 1D ndarray with one element, not a float. Code like `round(tempo)` will return an ndarray, not an int.
**Why it happens:** Changed in librosa 0.10+ for consistency with multi-channel input.
**How to avoid:** Always extract: `bpm = float(tempo[0])` or `bpm = float(tempo.item())`.
**Warning signs:** Pydantic validation errors when assigning tempo to an `int` field.

### Pitfall 2: POST /generate Changes from JSON to Multipart
**What goes wrong:** Adding `UploadFile` to the endpoint forces it to accept `multipart/form-data` instead of `application/json`. Existing tests using JSON bodies will break.
**Why it happens:** FastAPI cannot mix JSON body with file uploads. When any parameter uses `File()` or `Form()`, the entire request becomes form-encoded.
**How to avoid:** Update all tests to use multipart form encoding. Consider whether to keep a JSON-only path (no audio) alongside the multipart path.
**Warning signs:** 422 validation errors from existing test suite.

### Pitfall 3: ChromaDB Default Embedding Requires onnxruntime
**What goes wrong:** `chromadb.PersistentClient()` works, but `collection.add()` fails because the default embedding function needs `onnxruntime` or `onnxruntime-silicon` (on Apple Silicon).
**Why it happens:** ChromaDB 1.x uses a built-in embedding but it requires onnxruntime at runtime.
**How to avoid:** Install `chromadb` with its default dependencies -- it should pull onnxruntime. If not, install explicitly: `pip install onnxruntime` (or `onnxruntime-silicon` on M-series Mac).
**Warning signs:** Import errors or runtime errors mentioning onnxruntime during collection.add().

### Pitfall 4: Python 3.13 Removed aifc and sunau from stdlib
**What goes wrong:** librosa imports fail with `ModuleNotFoundError: No module named 'aifc'` on Python 3.13.
**Why it happens:** Python 3.13 removed `aifc` and `sunau` modules from the standard library.
**How to avoid:** Install `standard-aifc` and `standard-sunau` packages explicitly.
**Warning signs:** Import error on first `import librosa` call.

### Pitfall 5: Large Audio Files Block the Event Loop
**What goes wrong:** librosa analysis on a 60-second audio file takes 0.5-1 second. If called directly in an async endpoint, it blocks the FastAPI event loop.
**Why it happens:** librosa is synchronous CPU-bound computation.
**How to avoid:** Wrap in `asyncio.to_thread(analyze_audio, audio_bytes)` to run in a thread pool. For 30-60s clips this is fast enough; no need for process pool.
**Warning signs:** Other requests hanging during audio analysis.

### Pitfall 6: ChromaDB Upsert vs Add on Restart
**What goes wrong:** Using `collection.add()` on app restart with existing persisted data raises duplicate ID errors.
**Why it happens:** PersistentClient retains data between restarts; add() rejects duplicate IDs.
**How to avoid:** Always use `collection.upsert()` for seeding -- idempotent, handles both insert and update.
**Warning signs:** `chromadb.errors.DuplicateIDError` on second app startup.

## Code Examples

### librosa Feature Extraction for Mood Vector (AUD-02)
```python
# Source: librosa 0.11.0 docs - feature extraction
import librosa
import numpy as np

def extract_mood_features(y: np.ndarray, sr: int = 22050) -> dict:
    """Extract mood-relevant features from audio signal."""
    # Spectral centroid -- perceived "brightness" (Hz)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = float(np.mean(centroid))

    # Chroma -- 12 pitch classes, indicates harmonic content
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1).tolist()  # 12-element list

    # RMS energy -- overall loudness/energy
    rms = librosa.feature.rms(y=y)
    rms_mean = float(np.mean(rms))

    # Onset strength -- transient/attack density
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_mean = float(np.mean(onset_env))

    return {
        "spectral_centroid": centroid_mean,
        "chroma": chroma_mean,
        "rms": rms_mean,
        "onset_strength": onset_mean,
    }
```

### Mood Label Classification (D-03, Claude's Discretion)
```python
def classify_mood(centroid: float, rms: float, onset: float) -> list[str]:
    """Map raw features to human-readable mood labels.

    Thresholds based on typical ranges for 22050 Hz sample rate:
    - spectral_centroid: 1000-4000 Hz range (low=dark, high=bright)
    - rms: 0.01-0.3 range (low=mellow, high=energetic)
    - onset_strength: 0.5-5.0 range (low=sparse, high=dense)
    """
    labels = []

    # Brightness axis
    if centroid > 2500:
        labels.append("bright")
    else:
        labels.append("dark")

    # Energy axis
    if rms > 0.1:
        labels.append("energetic")
    else:
        labels.append("mellow")

    # Density axis
    if onset > 2.0:
        labels.append("dense")
    else:
        labels.append("sparse")

    return labels
```

### ChromaDB Query for RAG Retrieval (RAG-02)
```python
# Source: ChromaDB 1.x official docs
def query_styles(collection, prompt: str, n_results: int = 3) -> list[dict]:
    """Query genre-style documents by text prompt."""
    results = collection.query(
        query_texts=[prompt],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    styles = []
    for i in range(len(results["ids"][0])):
        styles.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return styles
```

### BPM Visualization Data (AUD-03)
```python
def build_visualization_data(y, sr, beat_frames, onset_env):
    """Build JSON-serializable visualization data for frontend charts."""
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    onset_times = librosa.times_like(onset_env, sr=sr).tolist()
    onset_values = onset_env.tolist()

    return {
        "beat_times": beat_times,          # x-positions for beat markers
        "onset_envelope": {
            "times": onset_times,          # x-axis: time in seconds
            "values": onset_values,        # y-axis: onset strength
        },
        "duration": float(len(y) / sr),   # total audio duration
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ChromaDB 0.5.x | ChromaDB 1.5.x (Rust backend) | 2025 | Much better performance; same Python API for basic operations |
| `langchain-community` Chroma wrapper | `langchain-chroma` dedicated package | langchain-community 0.2.9 | Old wrapper deprecated; use `langchain-chroma` package |
| librosa 0.10.x | librosa 0.11.0 | March 2025 | Python 3.13 support, NumPy 2.x compat |
| `chromadb.Client()` + `.persist()` | `chromadb.PersistentClient(path=...)` | ChromaDB 0.4.0 | Auto-persistence, no manual persist() call needed |
| `beat_track` returns float tempo | Returns ndarray tempo | librosa 0.10+ | Must extract `float(tempo[0])` |
| sentence-transformers required | ChromaDB bundles onnxruntime embeddings | ChromaDB 1.0+ | No need for 2GB PyTorch dependency for default embeddings |

## Open Questions

1. **ChromaDB onnxruntime on Apple Silicon**
   - What we know: ChromaDB 1.x needs onnxruntime for default embeddings. Apple Silicon may need `onnxruntime-silicon`.
   - What's unclear: Whether `pip install chromadb` auto-selects the right variant on macOS ARM64.
   - Recommendation: Test during installation. If default fails, install `onnxruntime-silicon` explicitly.

2. **Mood label thresholds**
   - What we know: Spectral centroid, RMS, onset strength have typical ranges but vary by genre.
   - What's unclear: Exact threshold values for "bright/dark", "energetic/mellow", "sparse/dense" labels.
   - Recommendation: Start with reasonable defaults, tune with real audio samples. This is Claude's discretion per CONTEXT.md.

3. **POST /generate migration from JSON to multipart**
   - What we know: Adding UploadFile forces multipart/form-data, breaking existing JSON API.
   - What's unclear: Whether to maintain backward compatibility with a separate JSON endpoint.
   - Recommendation: Switch to multipart entirely. Audio is optional (File(None)). Update all tests. Phase 1 had no external consumers relying on JSON body format.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | Yes | 3.13.1 | -- |
| ffmpeg | Audio format conversion (librosa backend) | Yes | 7.1.1 | -- |
| Redis | Not needed in Phase 2 (Phase 1 uses in-memory) | Yes | 7.2.7 | -- |
| librosa | Audio analysis | No (not installed) | -- | Must install |
| chromadb | RAG vector store | No (not installed) | -- | Must install |
| soundfile | librosa audio I/O | No (not installed) | -- | Must install |

**Missing dependencies with no fallback:**
- librosa, chromadb, soundfile must be installed via pip/uv

**Missing dependencies with fallback:**
- None -- all missing items must be installed

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio 0.24+ |
| Config file | `backend/pyproject.toml` (implicit) |
| Quick run command | `cd backend && python -m pytest tests/ -x -q` |
| Full suite command | `cd backend && python -m pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INP-03 | Audio file upload accepted via multipart form | integration | `pytest tests/test_api.py::test_generate_with_audio -x` | No -- Wave 0 |
| AUD-01 | BPM + beat timestamps extracted from audio | unit | `pytest tests/test_audio_analyzer.py::test_bpm_detection -x` | No -- Wave 0 |
| AUD-02 | Mood features (centroid, chroma, RMS, onset) extracted | unit | `pytest tests/test_audio_analyzer.py::test_mood_extraction -x` | No -- Wave 0 |
| AUD-03 | Visualization data returned (onset envelope + beat markers) | unit | `pytest tests/test_audio_analyzer.py::test_visualization_data -x` | No -- Wave 0 |
| AUD-04 | BPM override replaces detected BPM | integration | `pytest tests/test_api.py::test_bpm_override -x` | No -- Wave 0 |
| RAG-01 | ChromaDB collection seeded with genre docs | unit | `pytest tests/test_rag_retriever.py::test_genre_seeding -x` | No -- Wave 0 |
| RAG-02 | Query returns relevant genre-style documents | unit | `pytest tests/test_rag_retriever.py::test_style_query -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && python -m pytest tests/ -x -q`
- **Per wave merge:** `cd backend && python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_audio_analyzer.py` -- covers AUD-01, AUD-02, AUD-03
- [ ] `tests/test_rag_retriever.py` -- covers RAG-01, RAG-02
- [ ] `tests/test_api.py` -- extend with INP-03, AUD-04 tests
- [ ] `tests/fixtures/test_tone.wav` -- generated sine wave fixture for audio tests (use numpy to generate programmatically in conftest)
- [ ] `tests/conftest.py` -- add ChromaDB temporary client fixture, audio fixture
- [ ] Install phase 2 dependencies: `uv pip install librosa chromadb soundfile standard-aifc standard-sunau`

## Sources

### Primary (HIGH confidence)
- [librosa 0.11.0 official docs](https://librosa.org/doc/main/generated/librosa.beat.beat_track.html) - beat_track API, return types, parameters
- [librosa feature extraction docs](https://librosa.org/doc/0.11.0/feature.html) - spectral_centroid, chroma_stft, rms APIs
- [ChromaDB getting started](https://docs.trychroma.com/docs/overview/getting-started) - PersistentClient, collection API, query
- [ChromaDB migration guide](https://docs.trychroma.com/docs/overview/migration) - 0.x to 1.x breaking changes
- [FastAPI file upload docs](https://fastapi.tiangolo.com/tutorial/request-form-models/) - UploadFile + Form() pattern
- PyPI version checks (2026-04-02): librosa 0.11.0, chromadb 1.5.5, soundfile 0.13.1, langchain-chroma 1.1.0

### Secondary (MEDIUM confidence)
- [librosa Python 3.13 issue](https://github.com/librosa/librosa/issues/1883) - standard-aifc/standard-sunau requirement
- [librosa tempo ndarray issue](https://github.com/librosa/librosa/issues/1867) - tempo return type change
- [langchain-chroma API docs](https://api.python.langchain.com/en/latest/vectorstores/langchain_chroma.vectorstores.Chroma.html) - deprecated langchain-community wrapper

### Tertiary (LOW confidence)
- Mood label thresholds (spectral centroid, RMS, onset ranges) -- based on training data knowledge, not empirically verified for this project's audio domain

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all versions verified via PyPI, APIs verified via official docs
- Architecture: HIGH - follows established project patterns, FastAPI file upload well-documented
- Pitfalls: HIGH - librosa ndarray issue, Python 3.13 compat, ChromaDB API changes all verified via official sources
- Mood thresholds: LOW - need empirical tuning with real audio samples

**Research date:** 2026-04-02
**Valid until:** 2026-05-02 (stable libraries, 30-day validity)
