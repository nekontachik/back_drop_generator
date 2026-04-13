# Known Issues & Future Fixes

## UI / Frontend

- [ ] **Fullscreen preview on click not working** — clicking a gallery card does nothing; need to add a modal with fullscreen video player
- [ ] **HeroVideo src={undefined}** — hero section shows gradient fallback only, no video playing in background
- [ ] **blend_source not displayed** — API returns `blend_source` ("llm" or "fallback") but UI never shows it
- [ ] **MoodVector labels not rendered** — computed by backend but never displayed to user
- [ ] **BPM chips UX unreachable** — redirect after first submit breaks the BPM chip flow

## Backend / Infrastructure

- [ ] **Render free tier memory limit** — 720p is a workaround; proper fix is either optimize memory usage or upgrade to paid tier for 1080p
- [ ] **No Anthropic API key** — LLM blending uses deterministic fallback; add key to unlock full AI-powered parameter generation
- [ ] **Cold start on Render free tier** — service sleeps after 15 min inactivity, first request takes ~30s

## GSD / Tech Debt

- [ ] **Missing VERIFICATION.md files** — 7 of 9 phases have no formal verification; audit score was 8/28 (functionality works, paperwork missing)
