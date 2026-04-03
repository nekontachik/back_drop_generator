---
phase: 03-frontend-application
plan: "01"
subsystem: ui
tags: [nextjs, typescript, tailwind, react, api-client, dark-theme]

requires:
  - phase: 02-audio-analysis-rag-knowledge-base
    provides: Backend FastAPI API with all 6 endpoints (generate, jobs, styles, download, health, SSE stream)

provides:
  - Next.js 16 frontend app scaffolded in frontend/ directory
  - Tailwind v4 dark theme with club/concert color palette (accent-amber, accent-magenta, surface)
  - TypeScript types mirroring backend Pydantic models
  - API client functions for all 5 backend endpoints
  - Gallery landing page with hero video (gradient fallback) and example carousel
  - Shared Header with Beat Visuals branding and nav links

affects: [03-02, 03-03, 04-llm-style-blending]

tech-stack:
  added:
    - Next.js 16.2.2 (App Router)
    - Tailwind CSS v4 with @tailwindcss/postcss
    - TypeScript 5.x
    - Inter + Space Grotesk (Google Fonts)
    - class-variance-authority (CVA for button variants)
    - clsx + tailwind-merge (cn() utility)
    - lucide-react (icons)
    - react-dropzone (prepared for generate form)
  patterns:
    - Tailwind v4 CSS-based theme config via @theme in globals.css (no tailwind.config.ts)
    - CVA for component variants (Button)
    - "use client" directive on interactive components using hooks/event handlers
    - Graceful video fallback: gradient background when video src missing

key-files:
  created:
    - frontend/src/lib/types.ts
    - frontend/src/lib/api.ts
    - frontend/src/lib/utils.ts
    - frontend/src/components/ui/button.tsx
    - frontend/src/components/ui/card.tsx
    - frontend/src/components/layout/header.tsx
    - frontend/src/components/gallery/hero-video.tsx
    - frontend/src/components/gallery/carousel.tsx
    - frontend/src/app/page.tsx
    - frontend/.env.local
  modified:
    - frontend/src/app/layout.tsx
    - frontend/src/app/globals.css

key-decisions:
  - "Tailwind v4 uses CSS-based @theme config in globals.css instead of tailwind.config.ts — no config file needed"
  - "Next.js 16 is installed (latest), uses App Router with standard patterns from prior versions"
  - "Hero video shows gradient fallback (amber/magenta radial gradient) when no src provided — prevents empty black box"
  - "Video placeholder srcs in EXAMPLES array are stubs — intentional, flagged for pre-generation before deployment"

patterns-established:
  - "Client components requiring hooks/event handlers declared with 'use client' at top of file"
  - "API client imports types from @/lib/types — single source of truth for response shapes"
  - "Tailwind custom colors (accent-amber, surface, etc.) defined as CSS variables in @theme block"

requirements-completed: [FE-01]

duration: 28min
completed: "2026-04-03"
---

# Phase 03 Plan 01: Frontend Scaffold and Gallery Landing Page Summary

**Next.js 16 frontend with Tailwind v4 dark club theme, API client mirroring backend models, and gallery landing page with hero video and horizontal carousel**

## Performance

- **Duration:** 28 min
- **Started:** 2026-04-03T14:26:17Z
- **Completed:** 2026-04-03T14:54:00Z
- **Tasks:** 2
- **Files modified:** 13

## Accomplishments
- Scaffolded full Next.js 16 app with TypeScript, Tailwind v4, ESLint configured
- Built API client with all 5 endpoint functions ready for Plans 02 and 03
- TypeScript types mirroring all backend Pydantic models (AudioAnalysis, BpmResult, MoodVector, etc.)
- Gallery landing page with hero section (gradient fallback + CTA overlay) and horizontal scrolling carousel
- Dark concert aesthetic: accent-amber, accent-magenta, and surface colors with subtle grain texture

## Task Commits

1. **Task 1: Scaffold Next.js project with dark theme, Tailwind, types, and API client** - `800700d` (feat)
2. **Task 2: Build gallery landing page with hero video and example carousel (FE-01)** - `8aa4a1e` (feat)

## Files Created/Modified
- `frontend/src/lib/types.ts` - TypeScript interfaces mirroring all backend Pydantic models
- `frontend/src/lib/api.ts` - API client: submitGenerate, getJobStatus, getJobStream, getStyles, getDownloadUrl
- `frontend/src/lib/utils.ts` - cn() utility (clsx + tailwind-merge)
- `frontend/src/components/ui/button.tsx` - Button with CVA variants (default=amber, outline, ghost, magenta)
- `frontend/src/components/ui/card.tsx` - Card with surface-card bg and white/5 border
- `frontend/src/components/layout/header.tsx` - Sticky header with Beat Visuals logo, active-link underline
- `frontend/src/components/gallery/hero-video.tsx` - Auto-play muted video, gradient fallback, CTA overlay
- `frontend/src/components/gallery/carousel.tsx` - Horizontal snap scroll, hover-to-preview, prompt overlay
- `frontend/src/app/page.tsx` - Landing page composing HeroVideo + Carousel with 6 example stubs
- `frontend/src/app/layout.tsx` - Root layout with Inter + Space Grotesk, dark class, Header
- `frontend/src/app/globals.css` - Tailwind v4 @theme with accent-amber/magenta/surface palette
- `frontend/.env.local` - NEXT_PUBLIC_API_URL=http://localhost:8000

## Decisions Made
- **Tailwind v4 @theme in CSS**: Tailwind v4 replaces `tailwind.config.ts` with CSS-based `@theme` blocks in globals.css. Custom colors defined as CSS variables (e.g., `--color-accent-amber`), which become Tailwind utility classes automatically.
- **Gradient fallback for hero**: When no video src is provided, a radial gradient (amber 15% + magenta 10%) renders in the hero section rather than an empty black box — CTA is always visible.
- **"use client" directive**: Header (uses usePathname), HeroVideo (may need video controls), and Carousel (refs + event handlers) are all client components.
- **Next.js 16**: The scaffolded version is 16.2.2, which per the AGENTS.md note "may differ from training data." Verified conventions using the bundled docs in node_modules/next/dist/docs/.

## Deviations from Plan

### Auto-fixed Issues

None. All plan instructions were applicable as-is.

**1. [Rule 3 - Adaptation] Tailwind v4 CSS config instead of tailwind.config.ts**
- **Found during:** Task 1 (Scaffold)
- **Issue:** Plan specified creating `tailwind.config.ts`, but create-next-app generated Tailwind v4 which uses CSS-based @theme — there is no tailwind.config.ts in Tailwind v4
- **Fix:** Defined all custom colors (accent-amber, accent-magenta, surface) inside `@theme inline` block in globals.css using CSS custom properties
- **Files modified:** frontend/src/app/globals.css
- **Verification:** `npm run build` passes, custom colors work in components
- **Committed in:** 800700d (Task 1 commit)

---

**Total deviations:** 1 adaptation (Tailwind v4 config approach)
**Impact on plan:** Colors and theme work identically. No scope creep. All acceptance criteria satisfied.

## Known Stubs

| Stub | File | Line | Reason |
|------|------|------|--------|
| `/examples/tunnel-techno.mp4` | `frontend/src/app/page.tsx` | 12 | Placeholder — pre-generated videos not yet created |
| `/examples/fractal-ambient.mp4` | `frontend/src/app/page.tsx` | 18 | Placeholder — pre-generated videos not yet created |
| `/examples/particles-edm.mp4` | `frontend/src/app/page.tsx` | 24 | Placeholder — pre-generated videos not yet created |
| `/examples/plasma-jazz.mp4` | `frontend/src/app/page.tsx` | 30 | Placeholder — pre-generated videos not yet created |
| `/examples/tunnel-synthwave.mp4` | `frontend/src/app/page.tsx` | 36 | Placeholder — pre-generated videos not yet created |
| `/examples/fractal-classical.mp4` | `frontend/src/app/page.tsx` | 42 | Placeholder — pre-generated videos not yet created |
| `src={undefined}` (HeroVideo) | `frontend/src/app/page.tsx` | 57 | Hero uses gradient fallback until real video generated |

**Resolution:** All example videos will be generated in Phase 4 or 5 using the backend rendering pipeline. The HeroVideo component handles missing src gracefully with an amber/magenta gradient fallback. The plan explicitly states "Replace with pre-generated videos from backend before deployment."

## Issues Encountered
- create-next-app installed Next.js 16.2.2 (not 14.x/15.x as per CLAUDE.md tech stack). AGENTS.md in the frontend warns that API conventions may differ. Checked bundled docs at node_modules/next/dist/docs/ — App Router conventions are identical to prior versions for the features used in this plan.

## Next Phase Readiness
- API client ready for Plan 02 (generate form) and Plan 03 (results page) to import directly
- TypeScript types cover all response shapes Plans 02/03 need
- Shared UI components (Button, Card) ready for reuse
- Header includes /generate nav link — ready when Plan 02 creates the generate route
- No blockers for Plan 02

---
*Phase: 03-frontend-application*
*Completed: 2026-04-03*
