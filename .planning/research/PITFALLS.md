# Pitfalls Research

**Domain:** AI-powered music-reactive video backdrop generation
**Researched:** 2026-04-01
**Confidence:** MEDIUM (based on training data knowledge of librosa, FastAPI, OpenCV, ChromaDB, LangChain, Next.js; web search unavailable for verification)

## Critical Pitfalls

### Pitfall 1: CPU-Bound Rendering Blocks the FastAPI Event Loop

**What goes wrong:**
Generating frames via NumPy/OpenCV is pure CPU work. If the render function runs in the same process as FastAPI -- even via `asyncio.to_thread()` -- the GIL contention degrades API responsiveness. With `BackgroundTasks`, a 1-3 minute render starves the event loop: health checks time out, SSE progress streams stall, and on Railway/Render the platform may kill the process thinking it is unresponsive.

**Why it happens:**
Developers assume `asyncio.to_thread()` fully isolates CPU work. It moves the function to a thread pool, but NumPy releases the GIL only during C-level array operations. Python-level loop logic (frame iteration, parameter interpolation, writing frames) still holds the GIL. The event loop thread competes for it.

**How to avoid:**
1. Use `multiprocessing` or `ProcessPoolExecutor` instead of threading for the render worker. A separate process has its own GIL.
2. Or use ARQ with a separate worker process (recommended in STACK.md). The worker runs independently from the API process.
3. If starting with `BackgroundTasks` for MVP, use `ProcessPoolExecutor` instead of the default `ThreadPoolExecutor`: `loop.run_in_executor(ProcessPoolExecutor(max_workers=1), render_fn, params)`.
4. Set a generous request timeout and configure Railway's health check path to a lightweight endpoint separate from rendering.

**Warning signs:**
- SSE progress updates freeze mid-render, then burst multiple updates at once
- API health checks return 503 during active renders
- Railway/Render restarts the container during rendering
- Second render request hangs while first is in progress

**Phase to address:**
Phase 1 (core rendering). Validate single-process viability immediately. If progress streams stall during a test render, switch to `ProcessPoolExecutor` or subprocess model before building more features on top.

---

### Pitfall 2: Seamless Loop Discontinuity at the Wrap Point

**What goes wrong:**
The video's last frame must connect smoothly to its first frame. Most implementations get visual continuity wrong: there is a visible "pop" or stutter when the video loops. This is the single most visible quality issue -- a recruiter watching a demo will immediately notice a loop glitch.

**Why it happens:**
Three common mistakes:
1. **Off-by-one frame count.** If BPM=120 and you want a 4-beat loop at 30fps, you need exactly 60 frames (indices 0 through 59). Frame 60 would be identical to frame 0, causing a duplicate-frame stutter on loop.
2. **Linear parameter interpolation without circular wrapping.** If a hue animates from 0 to 360, frame 0 has hue=0 and the last frame has hue=360 -- but these are the same value, causing a stall. The parameter must reach `360 * (N-1)/N` on the last frame.
3. **Accumulated floating-point drift.** Incrementing `t += dt` each frame accumulates error. By frame 900 (30s at 30fps), `t` drifts from `frame_index * dt` enough to cause visible misalignment with beat positions.

**How to avoid:**
1. Calculate frame count as `frames = round(loop_duration * fps)`. Generate frames 0 through `frames - 1`. Frame `frames` is never rendered; it is logically identical to frame 0.
2. Parameterize all animations as `t = frame_index / total_frames` where t ranges [0, 1). Never let t reach 1.0. Use `2 * pi * t` for circular motions.
3. Never accumulate `t += dt`. Always compute `t = frame_index / total_frames` from the frame index directly.
4. Automated test: render a loop, compare pixel difference between frame[0] and frame[N-1]. It should be comparable to the difference between any two adjacent frames.

**Warning signs:**
- Visible "pop" when video loops in the browser player
- Pixel diff between frame[0] and frame[N-1] is significantly larger than diff between frame[0] and frame[1]
- Hue/position/scale "freezes" for a frame at the loop point

**Phase to address:**
Phase 1 (core rendering). Build the loop math correctly from the start. Write a unit test that asserts frame continuity (mean absolute pixel difference between frame 0 and last frame is within 2x of average consecutive-frame difference). Run this test on every effect type.

---

### Pitfall 3: librosa BPM Detection Returns Half or Double Tempo

**What goes wrong:**
`librosa.beat.beat_track()` frequently returns tempo that is half or double the actual BPM. A 140 BPM psytrance track may be detected as 70 BPM (half-time) or 280 BPM. The visual animation then runs at completely wrong speed.

**Why it happens:**
BPM detection is fundamentally ambiguous: a pattern repeating every 2 beats is also valid at double the period. librosa's autocorrelation-based algorithm can lock onto a harmonic or subharmonic of the true tempo. This is worse for genres with sparse kick patterns (ambient, dub) or very fast patterns (drum & bass, psytrance above 160 BPM).

**How to avoid:**
1. Use `librosa.beat.beat_track(y=y, sr=sr, start_bpm=128)` to bias the detector toward electronic music range.
2. Implement octave-error correction: if detected BPM < 80, try doubling; if > 200, try halving. Most electronic music sits in 90-180 BPM.
3. Let the user confirm/override BPM after detection. Show the detected value and allow tap-correction or manual entry. The project already plans manual BPM entry -- make it a first-class UX element, not a hidden fallback.
4. Use `librosa.feature.tempo()` (which returns multiple candidates with strengths) to present the top 2-3 candidates.

**Warning signs:**
- Visuals feel "sluggish" or "frantic" compared to the audio
- Detected BPM is below 80 or above 200 for electronic music
- Beat markers from `beat_track()` land between actual beats when plotted against the waveform

**Phase to address:**
Phase 2 (audio analysis). Do not ship BPM detection as a black box. Always show detected BPM, allow override. Build the octave-correction heuristic before integrating with rendering.

---

### Pitfall 4: LLM Returns Unparseable or Out-of-Range Visual Parameters

**What goes wrong:**
The LLM is asked to return a JSON object with visual parameters (colors as hex, speed as float 0-1, shape counts as integers). It returns malformed JSON, hallucinated field names, values outside expected ranges (`speed: 5.0` instead of `0.0-1.0`), or wraps JSON in markdown code fences that break the parser.

**Why it happens:**
LLMs are probabilistic text generators, not structured data APIs. Even GPT-4o-mini with function calling occasionally returns mistyped fields, omits required keys, or adds commentary outside the JSON block.

**How to avoid:**
1. Use LangChain's `with_structured_output()` on the ChatOpenAI model with a Pydantic model defining the exact schema. This uses OpenAI's function calling / JSON mode.
2. Define a Pydantic model with validators: `speed: float = Field(ge=0.0, le=1.0)`, `primary_color: str = Field(pattern=r'^#[0-9a-fA-F]{6}$')`.
3. Implement a fallback: if parsing fails after 1 retry, use deterministic defaults derived from genre. Log the failure.
4. Never let raw LLM output reach the renderer. Always pass through the Pydantic validation layer.

**Warning signs:**
- Render crashes with `KeyError` or `TypeError` on parameter access
- Rendered output looks identical regardless of prompt (always hitting fallback defaults)
- Error rate on LLM parsing exceeds 10% of requests

**Phase to address:**
Phase 3 (LLM integration). Build the Pydantic parameter model and validation layer before connecting the LLM. Test with 50+ prompt variations. Measure parse success rate.

---

### Pitfall 5: LLM Generating Executable Code Instead of Parameters

**What goes wrong:**
If the system allows the LLM to generate executable Python code (custom animation functions, math expressions), arbitrary code execution becomes possible. An adversarial prompt could cause the LLM to emit `os.system('rm -rf /')`.

**Why it happens:**
The temptation is strong: "the AI writes the animation code!" It feels powerful for a portfolio demo. Developers think "it's just math expressions" and use `eval()` or `exec()` on LLM output.

**How to avoid:**
1. **Do not let the LLM generate executable code.** Have it output structured parameters (JSON) that select and configure predefined effect functions. The creativity is in parameter blending, not code generation.
2. If you must allow dynamic expressions, use a safe evaluator (`asteval` or `simpleeval`) that only permits math operations on numbers.
3. Never use `eval()`, `exec()`, or `subprocess` with LLM-generated strings.
4. This is an architecture decision, not a bolt-on security fix. Get it right at design time.

**Warning signs:**
- Any use of `eval()` or `exec()` on strings derived from user input or LLM output
- LLM prompt says "generate a Python function" instead of "return these parameters as JSON"
- No input sanitization between LLM response and rendering code

**Phase to address:**
Phase 3 (LLM integration). Design the LLM interface as parameter output from the start.

---

### Pitfall 6: ChromaDB Data Loss on Container Redeployment

**What goes wrong:**
ChromaDB embedded mode stores data on the local filesystem. Railway/Render deploys create fresh containers. The ChromaDB directory is wiped. RAG returns empty results, the LLM gets no context, rendered output uses only fallback defaults.

**Why it happens:**
Works locally where the filesystem persists between runs. Deploy to a container platform, ephemeral filesystem deletes everything. Developers do not discover this until the first production deployment.

**How to avoid:**
1. **Treat the knowledge base as code, not data.** Store genre style documents as JSON/YAML files in the repo.
2. Implement `ensure_knowledge_base()` on FastAPI startup (lifespan context manager). Check if the ChromaDB collection exists; if not, seed from source files. This runs in <1 second for 5-20 documents.
3. Never rely on ChromaDB file persistence in production. Always be able to rebuild from repo files.

**Warning signs:**
- RAG retrieval returns 0 results after deployment
- LLM produces generic/random outputs because it received no style context
- Works locally but fails in production
- ChromaDB `persist_directory` points to a path inside the container

**Phase to address:**
Phase 2 (RAG setup). Build seed-on-startup from day one. Test by deleting the ChromaDB directory locally and restarting -- the app should self-heal.

---

### Pitfall 7: Video Files Unplayable in Safari/iOS

**What goes wrong:**
OpenCV's `cv2.VideoWriter` with the `'mp4v'` fourcc produces MPEG-4 Part 2 codec, not H.264. Chrome plays it; Safari, iOS, and many mobile browsers refuse. The video element shows a blank frame or an error.

**Why it happens:**
`cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920,1080))` is the most common example in tutorials. It produces a valid mp4 container but with the wrong codec for web playback.

**How to avoid:**
1. Use ffmpeg subprocess piping instead: `ffmpeg -f rawvideo -pix_fmt bgr24 -s 1920x1080 -r 30 -i pipe: -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p output.mp4`. This produces H.264 baseline profile with yuv420p, universally playable.
2. Verify with `ffprobe output.mp4` -- the video stream should show `h264 (High)` or `h264 (Baseline)`, and pixel format should be `yuv420p`.
3. Test on actual Safari (macOS or iOS) during the rendering phase, not at the end.

**Warning signs:**
- Video plays in Chrome but shows blank/error in Safari
- `ffprobe` shows `mpeg4` codec instead of `h264`
- Pixel format is `yuv444p` instead of `yuv420p`

**Phase to address:**
Phase 1 (core rendering). Use ffmpeg piping from the start. Do not use cv2.VideoWriter for the final output.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `BackgroundTasks` + `ProcessPoolExecutor` instead of ARQ+Redis | No Redis dependency, simpler deploy | No job persistence, no retry on failure, no multi-worker scaling | MVP / portfolio demo with <5 concurrent users |
| In-memory progress dict instead of Redis pub/sub | Zero infrastructure, works single-instance | Lost on restart, no multi-instance, potential memory leak if not cleaned | Portfolio demo only. Add TTL-based cleanup (delete entries older than 1 hour). |
| Hardcoded genre defaults in Python dicts | No ChromaDB dependency for early prototyping | Cannot do similarity search, no creative blending from context | Only during Phase 1 effect development. Replace in Phase 2. |
| `eval()` for math expressions from LLM | Enables dynamic formula-based effects | Catastrophic security hole | Never. Use `simpleeval` if needed. |
| Local filesystem for rendered videos | No object storage setup | Disk exhaustion, files lost on redeploy, no CDN | MVP only. Move to Cloudflare R2 before public launch. |
| Skipping audio format validation | Fewer deps, faster upload path | librosa/soundfile crash on corrupt or unsupported formats with cryptic errors | Never. Always validate before processing. |
| Single-file FastAPI app | Fast to start coding | Impossible to test, hard to refactor once >500 lines | Only for initial proof-of-concept. Split into modules before Phase 2. |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| librosa + uploaded audio | Passing raw `UploadFile.file` to `librosa.load()`. The file object may not be seekable after first read, or librosa may not recognize the format. | Save to `tempfile.NamedTemporaryFile(suffix='.wav')`, convert non-wav to wav via `ffmpeg -i input.ext -ar 22050 -ac 1 output.wav`, then pass the path to librosa. |
| ChromaDB + sentence-transformers on deploy | ChromaDB auto-downloads the embedding model on first query. On Railway, this downloads ~90MB on first request, causing a timeout. | Pre-download the model in Docker build: `RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`. Or pre-compute embeddings at build time. |
| OpenCV VideoWriter + browser playback | Using `'mp4v'` fourcc produces MPEG-4 Part 2 (not H.264). Chrome plays it; Safari does not. | Pipe frames to ffmpeg: `ffmpeg -f rawvideo -pix_fmt bgr24 ... -c:v libx264 -pix_fmt yuv420p output.mp4`. |
| LangChain + ChromaDB startup | `Chroma.from_documents()` re-embeds all documents on every startup (5-10 seconds wasted, collection re-created). | Use `Chroma(persist_directory=..., embedding_function=...)` to load existing. Only call `from_documents()` when collection is missing or documents changed. Use a version hash check. |
| Next.js `<video>` + cross-origin backend | Range requests (needed for seeking) fail across origins. Autoplay blocked without `muted`. | Ensure FastAPI returns `Content-Type: video/mp4`, `Accept-Ranges: bytes`, handles `Range` headers. Use `<video playsInline muted autoPlay loop>`. Configure CORS to allow Range headers. |
| FastAPI SSE + Vercel proxy | SSE connection drops after 25-30 seconds because Vercel serverless functions have execution time limits. | Do not proxy SSE through Vercel. Frontend connects directly to Railway backend for SSE. Or use polling as a simpler alternative (poll every 2 seconds for progress). |
| librosa + stereo audio | `librosa.load()` mixes to mono by default, which is correct. But if `mono=False` is accidentally set, `beat_track()` receives a 2D array and fails or produces wrong results. | Always use `librosa.load(path, sr=22050, mono=True)` explicitly. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Python loops over pixels instead of vectorized NumPy | Render takes 30+ minutes for 30s video | All pixel operations must be vectorized. Never `for x in range(1920): for y in range(1080):`. Use `np.meshgrid()` + vectorized math. | Immediately -- 1000x performance difference |
| Allocating new NumPy array per frame | Memory spikes to 5+ GB, GC pauses | Pre-allocate one `np.zeros((1080, 1920, 3), dtype=np.uint8)` frame buffer, rewrite it each frame | After ~100 frames (6MB/frame * 900 = 5.4GB allocated then GC'd) |
| Loading sentence-transformers per request | Each RAG query takes 3-5 seconds instead of ~50ms | Load model once at startup in `app.state.embedder`. Reuse for all requests. | First request -- obvious but easy to miss |
| ffmpeg re-encoding video to add audio track | Render takes 1-3 min, audio overlay adds another 1-2 min | Use `ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -shortest output.mp4`. The `-c:v copy` skips re-encoding, only muxes audio. | Always -- doubles total pipeline time |
| Serving video through Vercel serverless | Vercel has ~4.5MB response body limit on serverless functions | Serve video directly from Railway/Render backend URL. Frontend links to backend download endpoint, never proxies the file. | Any video over 4.5MB (most 1080p 30s videos) |
| Computing spectral features per frame | librosa called 900 times instead of once | Pre-compute all features into arrays indexed by frame number. `onset_env = librosa.onset.onset_strength(y=y, sr=sr)` returns the full envelope in one call. Map frames with `librosa.frames_to_time()`. | Render balloons from 1 min to 10+ min |
| No render output cleanup | Disk fills after 100-500 renders (5-20MB each) | Implement file lifecycle: TTL-based cleanup (delete after 1 hour), max storage cap (500MB), background cleanup every 10 minutes. | After 1-5GB of renders accumulate on a platform with limited disk |
| Generating 1080p for all test/dev renders | Dev iteration is painfully slow (1-3 min per test) | Use 480p (854x480) for development, 1080p only for final output and CI tests. Add a `resolution` parameter to the render function. | Immediately during development |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| No file type validation on audio upload | Users upload executables, zip bombs, multi-GB files. Server wastes CPU or crashes. | Validate: (1) extension whitelist (.mp3/.wav/.ogg/.flac/.m4a), (2) size limit (10MB), (3) `ffprobe` to verify it is actually audio before processing. |
| User-provided filenames in filesystem paths | Path traversal: `../../etc/passwd` reads/overwrites arbitrary files. | Never use original filename. Generate UUID: `f"{uuid4()}.wav"`. Store in dedicated temp directory. |
| OpenAI API key in frontend or git | Key stolen, attacker runs up your bill. | Key only in backend `.env`, never in `NEXT_PUBLIC_*`. Add `.env` to `.gitignore`. Use platform env vars on Railway. |
| No rate limiting on render endpoint | Bot queues hundreds of renders, exhausts CPU and disk. | IP-based rate limit: 3 renders per hour per IP. Use `slowapi` library with FastAPI. |
| Serving uploaded/generated files from app origin | Uploaded files could contain HTML/JS; serving inline enables XSS. | Serve with `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff`. Or serve from a different subdomain. |
| `eval()`/`exec()` on any user or LLM derived string | Arbitrary code execution, full server compromise. | Use structured JSON output from LLM. `grep -r "eval\|exec"` should return zero hits on any path connected to user/LLM input. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress feedback during 1-3 min render | User thinks app is broken, refreshes, queues duplicates | Progress bar with percentage and stage labels: "Analyzing audio... Generating frames (45/900)... Encoding video..." |
| BPM detection wrong with no correction UI | Visuals out of sync with music, user has no recourse | Always show detected BPM prominently. Provide editable number input with +/- buttons. "Detected: 140 BPM [Edit]" |
| Video does not autoplay or loop | User sees static frame, does not understand product | `<video autoPlay loop muted playsInline>`. `muted` required for autoplay in Chrome/Safari. Add visible play button fallback. |
| Gallery loads slowly on first visit | First impression ruined by buffering | Pre-generate gallery videos. Use poster images (first frame thumbnail). Lazy-load videos below the fold. Compress gallery videos more aggressively than user-generated ones. |
| Upload rejects common formats | User has .m4a from iPhone, gets cryptic error | Accept all common formats. Convert to wav on backend. Show clear supported-formats list on error. |
| Empty text prompt input with no guidance | User stares at blank input, unsure what to type | Provide 3-4 clickable example prompts: "Dark industrial warehouse with red strobes", "Dreamy ambient waves in blue and purple" |
| No indication of what the system can/cannot do | User expects photorealistic video, gets abstract geometry | Set expectations clearly above the form: "Generates abstract geometric visuals synchronized to your music's BPM" with example thumbnails |

## "Looks Done But Isn't" Checklist

- [ ] **Seamless loop:** Video plays once fine. But loop it 3x back-to-back and watch the junctions. Test every effect type.
- [ ] **BPM sync accuracy:** Beats "sort of" align. But tap along -- are pulses exactly on beats or 50-100ms off? Verify against a metronome.
- [ ] **Browser compatibility:** Plays in Chrome. Does it play in Safari? Firefox? iOS Safari? Verify H.264 baseline, yuv420p with ffprobe.
- [ ] **Audio format handling:** WAV works. Does mp3? m4a? What about 44.1kHz vs 48kHz? Stereo vs mono? Test each.
- [ ] **LLM fallback path:** Works with valid API key. What happens when key is expired, API is down, or rate-limited? Does fallback produce a watchable video?
- [ ] **Mobile viewport:** Desktop gallery looks great. Do video players break on mobile? Test on phone-sized viewport with actual playback.
- [ ] **Error messages:** Happy path works. Upload corrupt file, submit empty prompt, let render timeout -- does the user see a helpful error or a stack trace?
- [ ] **CORS in production:** Works locally (same origin). Works with frontend on Vercel and backend on Railway? Test cross-origin upload, SSE, and download.
- [ ] **Gallery in production:** Gallery renders from local files in dev. After deploy, are gallery videos accessible? Are they in the container, a CDN, or fetched from backend?
- [ ] **Cold start:** Railway/Render may sleep idle containers. First request after sleep imports librosa (2-5s), downloads models, seeds ChromaDB. Total cold start could be 15-30 seconds. Test and optimize.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Loop discontinuity | LOW | Fix frame math (`t = frame_index / total_frames`), re-render. No architecture change. |
| LLM output parsing failures | LOW | Add Pydantic validation layer + fallback defaults. Existing renders unaffected. |
| ChromaDB data lost on deploy | LOW | Implement seed-on-startup from repo files. 30-minute fix. |
| Event loop blocking from CPU rendering | MEDIUM | Refactor to ProcessPoolExecutor or subprocess. Requires IPC for progress reporting. 1-2 day refactor. |
| Video unplayable in Safari | MEDIUM | Switch from cv2.VideoWriter to ffmpeg pipe. Must re-render all gallery examples. Half-day fix. |
| Disk exhaustion from renders | LOW | Add cleanup task with file TTL. Restart container to clear. 1-hour fix. |
| BPM octave errors | LOW | Add octave-correction heuristic + user override UI. No architecture impact. |
| eval/exec on LLM output discovered in production | HIGH | Full audit of all code paths. Replace code generation with structured params. 2-3 day refactor if deeply embedded. Prevention is 100x cheaper. |
| Sentence-transformers model download on first request | LOW | Add model download to Dockerfile. Or switch to pre-computed embeddings. 1-hour fix. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| CPU rendering blocks event loop | Phase 1 - Core Rendering | Run render while hitting health endpoint every second. Zero timeouts = pass. |
| Seamless loop discontinuity | Phase 1 - Core Rendering | Automated test: pixel diff frame[0] vs frame[N-1] within 2x of avg consecutive diff, per effect. |
| Video browser compatibility (H.264) | Phase 1 - Core Rendering | ffprobe shows h264 codec + yuv420p. Manual test in Safari + iOS. |
| NumPy vectorization / memory | Phase 1 - Core Rendering | 30s 1080p render completes in <3 min. Peak memory <1GB. |
| Audio format handling | Phase 2 - Audio Analysis | Upload test: .mp3, .wav, .m4a, .ogg, .flac all produce valid BPM result. |
| librosa BPM half/double detection | Phase 2 - Audio Analysis | Test 10 tracks across genres. Detected BPM within 5% of known BPM for 8/10. |
| ChromaDB data loss on deploy | Phase 2 - RAG Setup | Delete ChromaDB dir, restart app, RAG returns correct results immediately. |
| LLM output parsing failures | Phase 3 - LLM Integration | 50 varied prompts, parse success >95%. Fallback valid 100%. |
| Code execution security | Phase 3 - LLM Integration | `grep -r "eval\|exec"` returns zero hits on user/LLM input paths. |
| CORS in production | Phase 4 - API & Deployment | Full integration test: cross-origin upload + render + progress + download. |
| Rate limiting | Phase 4 - API & Deployment | 10 requests in 1 min from same IP; requests 4+ rejected with 429. |
| File storage exhaustion | Phase 4 - API & Deployment | After 20 test renders, total storage <200MB. Cleanup verified. |
| Video serving (not through Vercel) | Phase 4 - API & Deployment | Download link points to backend, file size >4.5MB downloads successfully. |
| Gallery performance | Phase 5 - Frontend & Polish | Lighthouse >80 on gallery page. Videos use poster images, lazy-load. |
| Cold start time | Phase 4 - API & Deployment | Container cold start <10 seconds. Model pre-loaded in Docker image. |

## Sources

- Training data knowledge of librosa BPM detection ambiguity (well-documented in MIR literature, octave errors are a known fundamental limitation)
- Training data knowledge of OpenCV VideoWriter codec issues (mp4v vs H.264 is a persistent cross-browser problem)
- Training data knowledge of FastAPI async patterns and Python GIL behavior with NumPy
- Training data knowledge of ChromaDB embedded mode limitations on ephemeral container filesystems
- Training data knowledge of LangChain structured output and Pydantic integration
- Training data knowledge of Next.js video handling and Vercel platform constraints
- Known browser autoplay policies (muted required for autoplay in Chrome 66+, Safari 11+)
- Known Railway/Render platform constraints (ephemeral storage, health check behavior)

**Confidence notes:**
- Critical pitfalls 1-7: HIGH confidence these are real, persistent issues. They are well-documented across these ecosystems.
- Specific API details (e.g., exact LangChain `with_structured_output()` signature, Vercel body size limits): Should be verified against current docs before implementation.
- Platform-specific limits (Railway disk, Vercel response size): Verify against current pricing/plan docs as these change.

---
*Pitfalls research for: AI-powered music-reactive video backdrop generation*
*Researched: 2026-04-01*
