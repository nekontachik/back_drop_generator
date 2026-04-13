# Known Issues & Future Fixes

## UI / Frontend

- [x] **Fullscreen preview on click not working** — fixed: fullscreen modal with video+controls+info, ESC to close, body scroll lock
- [x] **No page transition animation** — fixed: fade + subtle slide-up on route change via PageTransition wrapper
- [x] **Progress bar doesn't fill during generation** — fixed: fake/estimated progress with status labels and smooth animation
- [x] **Generate page has no background** — fixed: animated radial gradient (amber/indigo/pink)
- [x] **HeroVideo src={undefined}** — fixed: set to `/examples/particles-edm.mp4`, hidden on mobile with gradient fallback
- [ ] **Matched Styles loads too slowly with no spinner** — RAG retrieval takes time but there's no loading indicator on the Generate page
- [ ] **blend_source not displayed** — API returns `blend_source` ("llm" or "fallback") but UI never shows it
- [ ] **MoodVector labels not rendered** — computed by backend but never displayed to user
- [ ] **BPM chips UX unreachable** — redirect after first submit breaks the BPM chip flow

## Performance / Mobile

- [ ] **Large video files** — `fractal-ambient.mp4` is 20MB, `fractal-classical.mp4` is 14MB; see `COMPRESS_VIDEOS_PROMPT.md` for Claude Code instructions to compress with ffmpeg (`-crf 28 -preset slow`) to ~3-5MB each
- [ ] **Matched Styles on mobile** — appears below the form; consider collapsing it into an accordion on small screens for better UX

## Backend / Infrastructure

- [ ] **Render free tier memory limit** — 720p is a workaround; proper fix is either optimize memory usage or upgrade to paid tier for 1080p
- [ ] **No Anthropic API key** — LLM blending uses deterministic fallback; add key to unlock full AI-powered parameter generation
- [ ] **Cold start on Render free tier** — service sleeps after 15 min inactivity, first request takes ~30s

## GSD / Tech Debt

- [ ] **Missing VERIFICATION.md files** — 7 of 9 phases have no formal verification; audit score was 8/28 (functionality works, paperwork missing)
