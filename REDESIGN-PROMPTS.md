# Beat Visuals Redesign — Claude Code Prompts

Copy-paste each prompt into Claude Code sequentially. Each phase builds on the previous one. After each phase, review changes and commit before moving to the next.

Reference mockup: `beat-visuals-redesign.jsx` (in project root)

---

## Phase 1: Design Tokens & globals.css

```
Redesign the color palette and typography for Beat Visuals. This is Phase 1 of a full UI redesign — we're moving from an amber/magenta concert theme to an electric blue / cyan sci-fi terminal aesthetic inspired by Teenage Engineering × Ableton.

Reference the design mockup in `beat-visuals-redesign.jsx` at project root — the `T` (tokens) object at the top has the exact values.

### Changes to `frontend/src/app/globals.css`:

Replace the @theme inline block with new design tokens:
- `--color-accent-amber` → `--color-primary: #00AAFF` (electric blue)
- `--color-accent-amber-light` → `--color-primary-bright: #33BBFF`
- `--color-accent-amber-dark` → `--color-primary-muted: #0088CC`
- `--color-accent-magenta` → `--color-violet: #8B5CF6`
- `--color-accent-magenta-light` → `--color-violet-light: #A78BFA`
- `--color-accent-magenta-dark` → `--color-violet-dark: #7C3AED`
- Add `--color-green: #00FF88`
- Add `--color-pink: #FF3399`
- `--color-surface: #0A0C10` (blue-tinted dark, was #0a0a0a)
- `--color-surface-card: #12151C` (was #141414)
- `--color-surface-elevated: #1A1E28` (was #1a1a1a)
- Add `--color-border: #252A36`
- Add `--color-border-light: #353B4A`
- Add mono font: `--font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace`

Update `:root` vars:
- `--background: #0A0C10`
- `--foreground: #E2E8F0`

Update `body` background-color to `#0A0C10`, color to `#E2E8F0`.
Keep the grain texture SVG but it should feel subtle on the new blue-tinted background.
Update `body::before` background-color to `#0A0C10`.

### Changes to `frontend/src/app/layout.tsx`:

Add JetBrains Mono from Google Fonts (next/font/google):
```ts
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono" });
```
Add the variable class to the html element alongside existing fonts.
Update the `--font-mono` CSS custom property to reference it.

### Important:
- Do NOT change any component files yet — only globals.css and layout.tsx
- Keep all existing CSS class names working (other components still reference accent-amber etc, they'll be updated in later phases)
- Add the NEW token names alongside the old ones for now so nothing breaks
- Commit with message: "feat(design): phase 1 — new electric blue design tokens and typography"
```

---

## Phase 2: Shared UI Components

```
Phase 2 of Beat Visuals redesign: update shared UI components to use the new electric blue palette.

Reference mockup: `beat-visuals-redesign.jsx` — see HardwareButton, MonoLabel, and Badge components.

### Update `frontend/src/components/ui/button.tsx`:

Restyle the Button component variants:
- `default` variant: change from amber (`bg-accent-amber`) to electric blue (`bg-primary text-[#050810]`). Hover state: `bg-primary-bright`.
- `outline` variant: border-primary, text-primary, hover bg-primary/10
- `ghost` variant: text-primary hover, bg-primary/10 hover
- Replace `magenta` variant with `violet`: bg-violet, text-white, hover bg-violet-light
- Add new `hardware` variant: transparent bg, border-border, mono font, uppercase, text-[11px], tracking-wider, 3px radius. Active state: border-primary, bg-primary/15, text-primary.
- All buttons: reduce border-radius to rounded-sm (3-4px) from current rounded-lg

### Update `frontend/src/components/ui/card.tsx`:

- Change border color from `border-white/5` to `border-border`
- Change background from `bg-surface-card` to new surface-card value
- Keep the same structure (Card, CardHeader, CardContent, CardFooter)

### Create `frontend/src/components/ui/mono-label.tsx`:

New component matching mockup's MonoLabel:
```tsx
interface MonoLabelProps {
  children: React.ReactNode;
  color?: string;
  className?: string;
}
```
- font-mono, text-[10px], tracking-widest, uppercase
- Default color: text-dim (var(--color-text-dim) or text-[#4A5568])
- Accept color prop to override

### Create `frontend/src/components/ui/badge.tsx`:

New component matching mockup's Badge:
- font-mono, text-[10px], px-2, py-0.5
- Border: 1px solid with color at 25% opacity
- Background: color at 6% opacity
- Text color matches the passed color prop
- Default color: primary blue

- Commit: "feat(design): phase 2 — restyle Button/Card, add MonoLabel and Badge components"
```

---

## Phase 3: Hardware Components (Knob, ChannelStrip)

```
Phase 3 of Beat Visuals redesign: create new hardware-inspired UI components.

Reference mockup: `beat-visuals-redesign.jsx` — see Knob and ChannelStrip components for exact SVG math and styling.

### Create `frontend/src/components/ui/knob.tsx`:

SVG-based rotary knob control. Props:
```tsx
interface KnobProps {
  value: number;       // 0-1
  label: string;
  size?: number;       // px, default 48
  color?: string;      // default: primary blue #00AAFF
  onChange?: (value: number) => void;  // optional interactivity
}
```

Visual structure (copy the SVG math from the mockup's Knob component):
- Outer track circle (stroke: border color)
- Value arc (stroke: color prop, with drop-shadow glow)
- Indicator dot at current angle position
- Center text showing value as percentage
- Label below using MonoLabel

The angle math: -135° to +135° range (270° total sweep).
Value arc uses strokeDasharray calculation from the mockup.

### Create `frontend/src/components/ui/channel-strip.tsx`:

Vertical meter bar inspired by Ableton's channel strip. Props:
```tsx
interface ChannelStripProps {
  label: string;
  value: number;       // 0-100 percentage
  color?: string;      // default: primary blue
  active?: boolean;    // default: true
}
```

Visual structure:
- Container: flex column, center aligned, padding, bordered
- Vertical meter: 4px wide, 40px tall, background track with filled portion from bottom
- Fill has box-shadow glow matching color
- MonoLabel below with label text
- When active: subtle color-tinted background, brighter border

Both components should be "use client" and use Tailwind classes where possible, inline styles only for dynamic values (color props, calculated positions).

- Commit: "feat(design): phase 3 — add Knob and ChannelStrip hardware components"
```

---

## Phase 4: Header Redesign

```
Phase 4 of Beat Visuals redesign: completely restyle the navigation header.

Reference mockup: `beat-visuals-redesign.jsx` — see the header section in the App Shell component at the bottom of the file.

### Rewrite `frontend/src/components/layout/header.tsx`:

Replace the current header with a hardware-device-style top bar:

**Logo (left side):**
- Replace text "Beat Visuals" with a square mark: 20×20px box, 2px border in primary blue (#00AAFF), 2px border-radius, containing "BV" in mono font 10px bold
- Next to it: "beat_visuals" in mono font 12px, font-weight 600, letter-spacing 0.04em
- Clicking logo navigates to "/"

**Navigation (center):**
- Replace current text links with hardware toggle buttons
- Each nav item: mono font, 11px, uppercase, letter-spacing 0.04em, padding 6px 14px
- Inactive: border-border, transparent bg, text-muted
- Active: border-primary, bg-primary/15 (glow), text-primary
- Items: "gallery" (/), "generate" (/generate), "output" (/results) — note "output" is new label for results
- Buttons sit flush with 2px gap between them

**Status indicators (right side):**
- Green dot (6px, #00FF88) with box-shadow glow + "api" MonoLabel in muted text
- "v0.1.0" MonoLabel in dim text

**Header bar itself:**
- Height: 48px (down from 56px/14*4)
- Background: rgba(10,12,16,0.92) with backdrop-blur-md
- Border-bottom: 1px solid border color (#252A36)
- Sticky top-0 z-50

Keep using usePathname() for active state detection. The "output" link should match any path starting with "/results".

- Commit: "feat(design): phase 4 — hardware-style header with BV logo mark"
```

---

## Phase 5: Landing Page — Animated Canvas Background

```
Phase 5 of Beat Visuals redesign: add the animated canvas background to the landing page hero section.

Reference mockup: `beat-visuals-redesign.jsx` — see the AnimatedBackground component (full canvas implementation is there, copy the draw logic).

### Create `frontend/src/components/gallery/animated-background.tsx`:

"use client" component with canvas element. Copy the EXACT draw logic from the mockup's AnimatedBackground function — it has:
1. Blue-tinted grid lines (rgba(0,170,255,0.035))
2. Beat-synced pulsing rings (128 BPM, alternating blue/violet)
3. Floating data particles (35 particles in blue/green/violet)
4. Scan line effect (blue tint)

Important details from the mockup:
- Canvas uses 2x resolution (retina): `canvas.width = canvas.offsetWidth * 2`
- Uses requestAnimationFrame loop with cleanup
- Handles window resize
- Opacity 0.7 on the canvas element
- Uses the exact color values from the T tokens object

### Update `frontend/src/components/gallery/hero-video.tsx`:

- Add AnimatedBackground as a layer BEHIND the video element (z-index ordering)
- The canvas is always visible; video plays on top when available (semi-transparent)
- Add scan lines CSS overlay on top of everything: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)`
- Update gradient overlay colors from amber/magenta to blue-tinted
- Update CTA box: use new bg with backdrop-blur, border-border, rounded-sm (3px)
- Update CTA heading to show "AI-Powered" / "Beat Visuals" (blue) split
- Update CTA subtitle to mono font
- Replace Button with hardware primary button style
- Add bottom status bar: absolute bottom, flex between, mono 10px, showing "● system.online", "librosa + rag + llm + opencv", "1080p · 30fps · mp4"

- Hide canvas on mobile (sm:block) to save performance, just like the video

- Commit: "feat(design): phase 5 — animated canvas background for landing hero"
```

---

## Phase 6: Landing Page — Session Table + View Toggle

```
Phase 6 of Beat Visuals redesign: add Ableton-style session table for examples, keep carousel, add toggle.

Reference mockup: `beat-visuals-redesign.jsx` — see the examples grid in LandingPage component.

### Create `frontend/src/components/gallery/session-table.tsx`:

"use client" component. Props: same `items` array the Carousel uses (id, src, prompt, genre, effect, bpm).

Structure (matching mockup):
- Header row: grid with columns `40px 1fr 90px 70px 60px 48px` — headers: #, prompt, genre, effect, bpm, ▶
- All headers use MonoLabel component
- Data rows: same grid, each row has:
  - Row number (01, 02...) in mono, dim
  - Prompt text in sans font, truncated with ellipsis
  - Genre as Badge component with per-genre color mapping:
    - Techno → primary blue, Ambient → green, EDM → violet, Jazz → primaryBright, Synthwave → pink, Classical → violet
  - Effect in mono, dim
  - BPM in mono, highlights on hover
  - Play button: 24px square, bordered, shows ▶
- Row hover: background tints with the genre's color at 3% opacity, text brightens
- Border-bottom on each row, cursor pointer

### Update `frontend/src/components/gallery/carousel.tsx`:

- Update colors: replace any amber/magenta references with primary blue / violet
- Update badge colors to match the new genre color mapping
- Keep functionality intact

### Update `frontend/src/app/page.tsx`:

Add view toggle between table and carousel:
- Make page "use client"
- Add state: `viewMode: "table" | "cards"` (default: "table")
- Section header with flex between:
  - Left: MonoLabel "examples" in primary + MonoLabel "{count} clips loaded"
  - Right: two small hardware toggle buttons — "table" and "cards"
- Render SessionTable when viewMode is "table", Carousel when "cards"
- Keep HeroVideo at the top unchanged

- Commit: "feat(design): phase 6 — session table view with carousel toggle"
```

---

## Phase 7: Generate Page Redesign

```
Phase 7 of Beat Visuals redesign: restyle the entire generate page with terminal/hardware aesthetic.

Reference mockup: `beat-visuals-redesign.jsx` — see the full GeneratePage component. This is the biggest phase.

### Update `frontend/src/app/generate/page.tsx`:

- Replace animated gradient background with flat surface bg (remove the radial-gradient div)
- Add page header: MonoLabel "module::generate" in primary blue, then h1 "Create Backdrop"
- Keep two-column grid layout but update gap and max-width to 960px centered

### Rewrite `frontend/src/components/generate/generate-form.tsx`:

Major restyle — the form becomes a vertical stack of "panels":

**Prompt panel:**
- Container: border-border, rounded-sm, bg-surface-card
- Header bar: padding 8px 12px, border-bottom, flex between — MonoLabel "visual_prompt" in primary + MonoLabel showing "{length}/500"
- Textarea: mono font, 13px, transparent bg, no border, placeholder "> describe your visual style..."

**Style blend panel:**
- Header: MonoLabel "style_blend" + MonoLabel showing "GenreA × GenreB"
- Genre A section: MonoLabel "channel_a" then grid of hardware buttons for all genres
- Crossfader slider: blue→violet gradient fill, square thumb (16px, 2px border-radius, border-primary), percentage labels on each side
- Genre B section: same layout as A

**Tempo config panel:**
- MonoLabel "tempo_config" header
- Big BPM display: mono font, 48px, bold, primary blue, text-shadow glow — just the number
- MonoLabel "bpm" below the number
- Quick-select hardware buttons: 64, 90, 110, 128, 140, 174
- Knob controls on the right: "intensity" (blue) and "complexity" (violet) — use the new Knob component
- Audio upload zone below: dashed border, centered text "drop audio file or click to upload", file types listed

**Submit button:**
- Full-width hardware primary button: "> execute render pipeline"

### Update `frontend/src/components/generate/style-preview.tsx`:

Restyle as the right sidebar panel:
- MonoLabel "preview" header
- 16:9 preview area with border, bg-surface, radial gradient glow
- Parameter readout section: MonoLabel "parameters", then mono key:value pairs (genre_a, genre_b, blend, tempo, resolution, fps) — genre values colored (a=primary, b=violet)
- Channel strip meters section: MonoLabel "levels", then 4 ChannelStrip components (bass, mid, high, fx) with blue/violet/green colors

### Update supporting components as needed:
- `blend-control.tsx` — may be integrated into generate-form or restyled in place
- `bpm-input.tsx` — replace with the big-number + buttons layout
- `audio-upload.tsx` — restyle the dropzone with mono text and dashed border

The form should still call the same API functions and handle the same state — only the visual presentation changes.

- Commit: "feat(design): phase 7 — terminal-style generate page with hardware controls"
```

---

## Phase 8: Results Page Redesign

```
Phase 8 of Beat Visuals redesign: restyle the results/render page.

Reference mockup: `beat-visuals-redesign.jsx` — see the full ResultsPage component.

### Update `frontend/src/app/results/[id]/page.tsx`:

- Add page header: MonoLabel "module::render" in primary blue
- Update h1 to toggle between "Rendering..." and "Render Complete"
- Keep the grid layout (1fr 280px) but apply new max-width 960px centered

### Update `frontend/src/components/results/progress-bar.tsx`:

Major restyle to pipeline view:
- Container: border-border, rounded-sm, bg-surface-card, padding 12px
- Header: MonoLabel "pipeline" in primary + MonoLabel showing percentage or "complete"
- Progress bar: 4px height, bg-elevated track, gradient fill blue→violet (or solid green when done)
- Box-shadow glow on the fill (primaryGlow when rendering, greenGlow when done)
- Step indicators below: flex row with 5 named steps:
  - audio_analysis (threshold: 15%)
  - rag_retrieval (threshold: 30%)
  - llm_blending (threshold: 50%)
  - frame_render (threshold: 85%)
  - encode_mp4 (threshold: 95%)
- Each step: 6px square dot + MonoLabel
  - Done: green dot, green text
  - Active: primary blue dot with box-shadow glow, blue text
  - Pending: border-color dot, dim text

### Update `frontend/src/components/results/video-player.tsx`:

- Wrap in bordered container matching new style
- Add blue/violet radial gradient background behind video
- When not yet loaded: show play button circle (56px, border-primary, bg-primaryGlow)

### Update `frontend/src/components/results/result-sidebar.tsx`:

Restyle to match mockup's right panel:
- "ai_vision" section: MonoLabel in VIOLET (not blue — this is the AI/creative accent), paragraph in sans 13px
- "matched_styles" section: MonoLabel in primary, flex row of Badge components
- "beat_map" section: MonoLabel in primary, keep the SVG chart but update stroke color to primary blue
- "render_info" section: MonoLabel in primary, mono key:value readout (resolution, fps, duration, codec, size)
- Action buttons: hardware primary "download .mp4" + outline "new render"

### Update `frontend/src/components/results/bpm-chart.tsx`:

- Update polyline stroke from amber to primary blue (#00AAFF)
- Update beat marker lines to primary blue at 20% opacity
- Keep the same SVG structure and math

- Commit: "feat(design): phase 8 — pipeline progress view and restyled results page"
```

---

## Phase 9: Polish & Transitions

```
Phase 9 of Beat Visuals redesign: polish pass across the entire app.

### `frontend/src/components/layout/page-transition.tsx`:
- Keep the fade-in/slide-up animation
- Adjust timing if needed (220ms ease-out is fine)
- Ensure it works with the new darker background

### Global polish (check every component file):

**Hover/focus/active states:**
- All interactive elements should have `transition: all 0.12-0.15s ease`
- Focus rings: use primary blue at 50% opacity (ring-primary/50)
- Hover on buttons: slight brightness increase
- Hover on cards/rows: subtle background tint

**Responsive breakpoints:**
- Mobile (< 640px): stack all grid layouts to single column
- Hide canvas AnimatedBackground on mobile (`hidden sm:block`)
- Session table: on mobile, hide effect and play columns, show only #, prompt, genre, bpm
- Generate page: stack form and preview vertically
- Results page: stack video and sidebar vertically
- Header: on mobile, maybe hide status indicators, keep logo and nav

**Typography consistency check:**
- All labels/headers: MonoLabel (mono, 10px, uppercase, tracking)
- All body text: sans font (Space Grotesk)
- All data/values: mono font (JetBrains Mono)
- All section headings: sans font, bold

**Color consistency:**
- Primary blue (#00AAFF) for: interactive elements, active states, primary labels, main data
- Violet (#8B5CF6) for: AI/creative elements, secondary controls, channel_b, complexity knob
- Green (#00FF88) for: success states, online indicators, "done" states
- Pink (#FF3399) for: occasional genre highlights only (Synthwave badge)
- Remove ALL remaining amber/magenta references

**Scrollbar:**
- Keep scrollbar-hide utility
- Consider adding custom scrollbar styling with primary blue thumb on dark track

- Commit: "feat(design): phase 9 — responsive polish and interaction states"
```

---

## Phase 10: Verify & Test

```
Phase 10 of Beat Visuals redesign: final verification.

Run the following checks:

1. Start the dev server: `cd frontend && npm run dev`

2. TypeScript: `npx tsc --noEmit` — fix any type errors

3. Visual check all 3 pages:
   - Landing: animated canvas renders, session table shows data, toggle switches to carousel, hero CTA works
   - Generate: all panels render, genre buttons select, blend slider works, BPM buttons work, knobs display, textarea accepts input, submit button navigates
   - Results: progress animation runs, pipeline steps light up in sequence, video area shows completion state, sidebar data displays correctly

4. Mobile responsive: check at 375px width that all layouts stack properly and nothing overflows

5. Check that no amber/magenta/orange colors remain anywhere in the codebase:
   `grep -r "amber\|magenta\|#f59e0b\|#ec4899\|#fbbf24\|#f472b6\|#d97706\|#db2777" frontend/src/`

6. Compare against the design mockup `beat-visuals-redesign.jsx` — the overall feel should match: dark blue-tinted background, electric blue accents, monospace labels, hardware controls, terminal aesthetic.

7. If all looks good, do a final commit: "feat(design): phase 10 — redesign verification complete"

Report any issues found.
```

---

## Quick Reference: Color Cheat Sheet

| Token | Hex | Usage |
|-------|-----|-------|
| primary | #00AAFF | Main accent, buttons, active states, labels |
| primary-bright | #33BBFF | Hover states |
| primary-muted | #0088CC | Pressed states |
| violet | #8B5CF6 | AI/creative, secondary controls |
| green | #00FF88 | Success, online, completed |
| pink | #FF3399 | Genre highlight (Synthwave) |
| surface | #0A0C10 | Page background |
| surface-card | #12151C | Card/panel background |
| surface-elevated | #1A1E28 | Elevated elements |
| border | #252A36 | Default borders |
| border-light | #353B4A | Lighter borders |
| text | #E2E8F0 | Primary text |
| text-muted | #8892A4 | Secondary text |
| text-dim | #4A5568 | Tertiary/label text |
