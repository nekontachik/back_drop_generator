# Phase 3: Frontend Application - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-03
**Phase:** 03-frontend-application
**Areas discussed:** Gallery & landing page, Generate form UX, Progress & results page, Visual identity & polish

---

## Gallery & Landing Page

| Option | Description | Selected |
|--------|-------------|----------|
| Video grid with autoplay on hover | Cards in a responsive grid, static thumbnails until hovered | |
| Hero video + carousel below | One large showcase video auto-playing, carousel of others below | ✓ |
| Full-bleed video wall | All videos autoplay simultaneously in tiled layout | |
| You decide | Claude picks | |

**User's choice:** Hero video + carousel below

| Option | Description | Selected |
|--------|-------------|----------|
| Overlay on hero video | CTA button on top of hero with semi-transparent backdrop | ✓ |
| Below hero, above carousel | Clean separation, standard SaaS flow | |
| Sticky floating button | Always-visible floating CTA | |
| You decide | Claude picks | |

**User's choice:** Overlay on hero video

| Option | Description | Selected |
|--------|-------------|----------|
| Genre tag + effect name | Small genre chip and effect type on each card | |
| Prompt text shown on hover | Clean by default, reveals prompt on hover | ✓ |
| Minimal — just videos | No metadata, pure visual impact | |
| You decide | Claude picks | |

**User's choice:** Prompt text shown on hover

| Option | Description | Selected |
|--------|-------------|----------|
| Single page with sections | One long page, scroll-based | |
| Multi-page with router | Separate pages: Landing, Generate, Results | ✓ |
| You decide | Claude picks | |

**User's choice:** Multi-page with router

---

## Generate Form UX

| Option | Description | Selected |
|--------|-------------|----------|
| Single column, step-by-step | One field at a time with transitions | |
| All fields visible at once | Classic form layout | |
| Two-column split | Left: form, Right: live preview of matched styles | ✓ |
| You decide | Claude picks | |

**User's choice:** Two-column split

| Option | Description | Selected |
|--------|-------------|----------|
| Multi-select tags with weight sliders | Pick 1-3 genre tags, adjust sliders | |
| Freeform in the prompt | No explicit control, LLM interprets | |
| Dropdown + single slider | Two genre dropdowns, one blend slider | ✓ |
| You decide | Claude picks | |

**User's choice:** Dropdown + single slider

| Option | Description | Selected |
|--------|-------------|----------|
| Upload replaces manual BPM | Upload auto-fills, manual disabled | |
| Both always available | Coexist, upload auto-fills but manual always editable | ✓ |
| Toggle: manual or upload | Radio switches between modes | |

**User's choice:** Both always available

| Option | Description | Selected |
|--------|-------------|----------|
| Debounced live preview | Calls GET /styles after 500ms pause, updates right panel | ✓ |
| Preview button | User clicks button to fetch | |
| After submit only | No preview, simpler | |

**User's choice:** Debounced live preview

---

## Progress & Results Page

| Option | Description | Selected |
|--------|-------------|----------|
| Animated progress bar + status text | Horizontal bar with phase labels | ✓ |
| Circular/radial progress | Centered circle with percentage | |
| Frame-by-frame preview | Show frames as produced | |
| You decide | Claude picks | |

**User's choice:** Animated progress bar + status text

| Option | Description | Selected |
|--------|-------------|----------|
| Waveform with beat markers | Audio waveform with vertical beat lines | |
| Energy timeline with beat dots | Smooth energy curve with dot pulses at beats | ✓ |
| Minimal stats display | Just BPM number, confidence, beat count | |
| You decide | Claude picks | |

**User's choice:** Energy timeline with beat dots

| Option | Description | Selected |
|--------|-------------|----------|
| Video dominant + sidebar info | 60-70% video, sidebar with chart/download | ✓ |
| Stacked sections | Full-width video, sections below | |
| Tabbed sections below video | Video on top, tabs below | |
| You decide | Claude picks | |

**User's choice:** Video dominant + sidebar info

---

## Visual Identity & Polish

| Option | Description | Selected |
|--------|-------------|----------|
| Dark theme only | Dark background, neon accents, no light mode | ✓ |
| Dark with light mode toggle | Dark default with optional light | |
| Adaptive | Auto-detect OS preference | |
| You decide | Claude picks | |

**User's choice:** Dark theme only

| Option | Description | Selected |
|--------|-------------|----------|
| Cyberpunk / neon | Deep blacks, electric blues/purples, neon green | |
| Clean minimal dark | Dark grays, white text, subtle accent | |
| Club / concert aesthetic | Rich blacks, warm accents (amber, magenta), grain, concert typography | ✓ |
| You decide | Claude picks | |

**User's choice:** Club / concert aesthetic

| Option | Description | Selected |
|--------|-------------|----------|
| Generous | Page transitions, hover effects, micro-interactions | |
| Subtle | Hover states and loading transitions only | ✓ |
| Minimal | Functional only | |
| You decide | Claude picks | |

**User's choice:** Subtle — hover states and loading transitions only

---

## Claude's Discretion

- Charting library choice for BPM visualization
- Exact Tailwind color palette values
- Component structure and file organization
- Form validation UX and error states
- Video player controls
- Responsive breakpoints and mobile layout
- Carousel scrolling mechanism
- Audio upload dropzone appearance
- Typography choices

## Deferred Ideas

None — discussion stayed within phase scope
