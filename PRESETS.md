# Preset Visual Reference

Each genre preset is designed to be **visually distinct** — unique effect combination, unique color palette, unique mood. No two presets share the same effect pair or color family.

## Showcase Presets (6 — displayed on landing page)

### Techno
- **Effects:** tunnel (base) + particles (overlay)
- **Colors:** `#0a0a0a` bg · `#00ff88` green · `#ff0066` red
- **Mood:** Industrial, aggressive, forward-rushing
- **Post-process:** glitch, bloom, chromatic aberration
- **Audio:** `samples/techno.mp3` (138 BPM)

### Ambient
- **Effects:** aurora (base) + particles (overlay)
- **Colors:** `#050518` bg · `#4488ff` blue · `#22ddaa` teal
- **Mood:** Ethereal, dreamy, floating
- **Post-process:** heavy bloom, vignette
- **Audio:** `samples/ambient.mp3` (72 BPM)

### EDM
- **Effects:** tunnel (base) + waveform (overlay)
- **Colors:** `#04001a` bg · `#00ccff` electric cyan · `#ff00cc` magenta
- **Mood:** Festival laser show, high energy, spectrum bars
- **Post-process:** glitch, bloom, chromatic aberration
- **Audio:** `samples/edm.mp3` (128 BPM)
- **Why not retro_grid:** Synthwave owns the retro grid + sun. EDM uses a geometric tunnel with mirrored spectrum bars for a completely different festival LED wall aesthetic.

### Jazz
- **Effects:** fractal (base) + waveform (overlay)
- **Colors:** `#0a0604` bg · `#ff8844` warm amber · `#4488cc` blue
- **Mood:** Smoky lounge, intimate, organic
- **Post-process:** bloom, heavy vignette
- **Audio:** `samples/jazz.mp3` (110 BPM)

### Synthwave
- **Effects:** retro_grid (base) + plasma (overlay)
- **Colors:** `#0a001e` bg · `#ff2299` hot pink · `#00ffee` cyan
- **Mood:** Outrun, retro, neon sunset
- **Post-process:** scanlines, bloom, chromatic aberration
- **Audio:** `samples/synthwave.mp3` (118 BPM)

### Classical
- **Effects:** plasma (base) + aurora (overlay)
- **Colors:** `#0a0a1e` bg · `#8899cc` silver-blue · `#bb99dd` cool violet
- **Mood:** Orchestral, elegant, atmospheric
- **Post-process:** heavy bloom, heavy vignette
- **Audio:** `samples/classical.mp3` (90 BPM)
- **Why not fractal/gold:** Jazz owns warm amber fractals. Classical uses cool blue/violet plasma clouds with silver aurora curtains — completely different color temperature.

## Extended Presets (8 — available via API)

| Genre | Base Effect | Overlay Effect | Primary Color | Mood |
|-------|-------------|----------------|---------------|------|
| Dark Ambient | fractal | particles | `#1a2244` navy | Minimal, foreboding |
| Dark Techno | matrix_rain | fractal | `#00cc44` green | Cyberpunk, dystopian |
| Melodic Techno | aurora | tunnel | `#8844ff` purple | Emotional, warm mechanical |
| House | plasma | waveform | `#ff6600` orange | Warm, bouncy, festival |
| Deep House | plasma | tunnel | `#ff4488` pink | Liquid, submerged, hypnotic |
| Psytrance | fractal | tunnel | `#ff00ff` magenta | Psychedelic, trippy |
| Drum and Bass | waveform | particles | `#ff4400` red-orange | Explosive, chaotic |
| Industrial | matrix_rain | tunnel | `#cc4400` dark orange | Harsh, mechanical |

## Distinctness Matrix

Every showcase genre uses a unique combination along three axes:

| Genre | Base Effect | Color Temperature | Energy |
|-------|-------------|-------------------|--------|
| Techno | tunnel | Cold (green/red) | High |
| Ambient | aurora | Cool (blue/teal) | Low |
| EDM | tunnel | Neon (cyan/magenta) | Very High |
| Jazz | fractal | Warm (amber/blue) | Low |
| Synthwave | retro_grid | Hot (pink/cyan) | Medium |
| Classical | plasma | Cool (silver/violet) | Very Low |

No two genres share the same base effect AND color family.

## Audio Samples

All 6 showcase genres have audio samples in `frontend/public/samples/`:
- `techno.mp3`, `ambient.mp3`, `edm.mp3`, `jazz.mp3`, `synthwave.mp3`, `classical.mp3`

The generation script uses real audio analysis (librosa beat detection) to create natural, irregular beat envelopes instead of synthetic BPM timing.

## Regenerating Videos

```bash
cd backend

# Regenerate all with real audio sync (default)
python scripts/generate_preset_demos.py

# Regenerate specific genres only
python scripts/generate_preset_demos.py --presets edm classical

# Force synthetic BPM (no audio)
python scripts/generate_preset_demos.py --no-audio

# Higher resolution
python scripts/generate_preset_demos.py --width 1920 --height 1080
```

Output: `frontend/public/examples/preset-{genre}.mp4`
