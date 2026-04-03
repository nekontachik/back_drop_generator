# Phase 3: Frontend Application - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Next.js frontend for the backdrop generator. Users browse a gallery of pre-generated examples, submit generation requests via a form, watch real-time render progress, and view/download results. Connects to the existing FastAPI backend API. No new backend features — this is purely the frontend layer.

</domain>

<decisions>
## Implementation Decisions

### Gallery & Landing Page
- **D-01:** Hero video auto-playing at the top with a horizontal scrolling carousel of other examples below. Cinematic first impression.
- **D-02:** "Try it yourself" CTA overlay on the hero video with semi-transparent backdrop. Impossible to miss.
- **D-03:** Carousel cards show the prompt text on hover. Clean by default, discoverable on interaction.
- **D-04:** Multi-page structure with Next.js App Router: Landing (/), Generate (/generate), Results (/results/:id). Clean URLs, each page focused.

### Generate Form UX
- **D-05:** Two-column split layout. Left side: form fields. Right side: live preview of matched styles from GET /styles as user types.
- **D-06:** Style blend control: two genre dropdowns + single slider for blend ratio between them. Simple and clear for two-genre blending.
- **D-07:** Audio upload and manual BPM field coexist. Upload auto-fills detected BPM but user can always override by typing. No disabling either field.
- **D-08:** Debounced live preview — calls GET /styles after 500ms pause as user types. Right panel updates with matched genre docs, colors, and shape keywords in real-time.

### Progress & Results Page
- **D-09:** Animated horizontal progress bar with status text phases: "Analyzing audio..." -> "Generating frames..." -> "Encoding video..." SSE-driven from backend.
- **D-10:** BPM visualization: energy timeline (onset strength over time) with dots/pulses at beat positions. Lighter than full waveform, fits the aesthetic.
- **D-11:** Results layout: large video player (60-70% width) with sidebar showing BPM chart, genre matches, parameters used, and download button.

### Visual Identity & Polish
- **D-12:** Dark theme only. No light mode toggle. Videos pop against dark backgrounds. Natural fit for music/VJ culture.
- **D-13:** Club / concert aesthetic: rich blacks with warm accent colors (amber, magenta), subtle grain textures, concert-poster typography. Feels like a real event tool.
- **D-14:** Subtle animation — tasteful hover effects and smooth loading transitions. No page transitions or scroll animations. Professional restraint.

### Claude's Discretion
- Charting library choice for BPM visualization (lightweight option preferred)
- Exact Tailwind color palette values for the club aesthetic
- Component structure and file organization
- Form validation UX and error states
- Video player controls (native HTML5 vs custom)
- Responsive breakpoints and mobile layout
- How carousel scrolling works (arrows, drag, auto)
- Audio upload dropzone appearance and drag-and-drop behavior
- Typography choices (font family, weights)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend API (integration surface)
- `backend/app/api/generate.py` — POST /generate (multipart: prompt, bpm, audio, bpm_override), GET /jobs/{id}, GET /jobs/{id}/stream (SSE)
- `backend/app/api/download.py` — GET /jobs/{id}/download (MP4 file)
- `backend/app/api/styles.py` — GET /styles?prompt=... (RAG style preview)
- `backend/app/models/api.py` — GenerateResponse, JobStatusResponse schemas (defines what frontend receives)
- `backend/app/models/audio.py` — AudioAnalysis, BpmResult, MoodVector, BpmVisualization (chart data structure)

### Backend config
- `backend/app/config.py` — Backend settings (host, port, CORS)
- `backend/app/main.py` — CORS middleware config, API prefix

### Project context
- `.planning/PROJECT.md` — Core value, constraints, target audience
- `.planning/REQUIREMENTS.md` — FE-01, FE-02, FE-03, FE-04

### Prior phase decisions
- `.planning/phases/01-rendering-engine/01-CONTEXT.md` — API design decisions (D-10 through D-18)
- `.planning/phases/02-audio-analysis-rag-knowledge-base/02-CONTEXT.md` — Audio upload, BPM alternatives, RAG endpoint decisions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No frontend code exists yet — this is a greenfield Next.js build
- Backend API is fully built with 6 endpoints ready for frontend consumption
- Genre YAML docs in `backend/data/genres/` define the style vocabulary the frontend will display

### Established Patterns
- Backend uses FastAPI with Pydantic models — response schemas are well-defined
- SSE streaming via `sse-starlette` EventSourceResponse — standard EventSource API on frontend
- Multipart form-data for POST /generate — need matching FormData on frontend

### Integration Points
- CORS must be configured on backend to allow frontend origin (localhost:3000 dev, Vercel domain prod)
- SSE connection: `new EventSource('/jobs/{id}/stream')` for progress updates
- File download: direct link to GET /jobs/{id}/download or fetch + blob URL
- Style preview: GET /styles?prompt=... returns array of genre match objects

</code_context>

<specifics>
## Specific Ideas

- Hero video should auto-play muted — browsers block autoplay with sound
- Carousel examples should showcase different genres/effects to demonstrate range
- The two-column generate form with live style preview is the key differentiator — makes the tool feel intelligent
- BPM alternatives (detected + half + double) should be clickable chips/buttons, not a dropdown
- Energy timeline chart should use the same accent colors as the site theme (amber, magenta)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-frontend-application*
*Context gathered: 2026-04-03*
