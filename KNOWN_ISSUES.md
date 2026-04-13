# Known Issues & Future Fixes

## UI / Frontend

- [ ] **Fullscreen preview on click not working** — clicking a gallery card does nothing; need to add a modal with fullscreen video player
- [ ] **No page transition animation** — sharp/instant transition between Gallery and Generate pages; needs smooth fade or slide
- [ ] **Matched Styles loads too slowly with no spinner** — RAG retrieval takes time but there's no loading indicator on the Generate page
- [ ] **Progress bar doesn't fill during generation** — bar stays empty; needs fake/estimated progress (e.g. 30% after 1min, 60% after 2min, 90% at 3min)
- [ ] **Generate page has no background** — page looks empty, only a centered form with no visual context; needs background video loop or animated gradient
- [ ] **HeroVideo src={undefined}** — hero section on Gallery shows gradient fallback only, no video playing in background
- [ ] **blend_source not displayed** — API returns `blend_source` ("llm" or "fallback") but UI never shows it
- [ ] **MoodVector labels not rendered** — computed by backend but never displayed to user
- [ ] **BPM chips UX unreachable** — redirect after first submit breaks the BPM chip flow

## Performance / Mobile

- [ ] **Large video files** — `fractal-ambient.mp4` is 20MB, `fractal-classical.mp4` is 14MB; need to compress with ffmpeg (`-crf 28 -preset slow`) to ~3-5MB each
- [ ] **Matched Styles on mobile** — appears below the form; consider collapsing it into an accordion on small screens for better UX

## Backend / Infrastructure

- [ ] **Render free tier memory limit** — 720p is a workaround; proper fix is either optimize memory usage or upgrade to paid tier for 1080p
- [ ] **No Anthropic API key** — LLM blending uses deterministic fallback; add key to unlock full AI-powered parameter generation
- [ ] **Cold start on Render free tier** — service sleeps after 15 min inactivity, first request takes ~30s

## GSD / Tech Debt

- [ ] **Missing VERIFICATION.md files** — 7 of 9 phases have no formal verification; audit score was 8/28 (functionality works, paperwork missing)
