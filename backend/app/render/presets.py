"""Deterministic composition presets for each genre.

Each preset is a complete, tested layer recipe — colours, effects,
beat response modes, blend modes, and opacities. These are the source
of truth for "what genre X looks like". The LLM can suggest creative
variations, but presets are the safety net that never breaks.

Usage:
    from app.render.presets import get_preset, PRESETS

    params = get_preset("ambient", bpm=72)
    # → RenderParams with multi-layer composition, ready to render
"""

from __future__ import annotations

from app.models.params import (
    AuroraParams,
    BeatResponse,
    BlendMode,
    FractalParams,
    LayerConfig,
    MatrixRainParams,
    ParticleParams,
    PlasmaParams,
    PostProcessParams,
    RenderParams,
    RetroGridParams,
    TunnelParams,
    WaveformParams,
)

# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------
# Each preset is a dict of RenderParams kwargs. Layers are ordered
# bottom (background) → top (foreground).
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # ------------------------------------------------------------------
    # AMBIENT — aurora curtains + soft particles (ethereal, dreamy)
    # ------------------------------------------------------------------
    "ambient": {
        "bg_color": "#050518",
        "primary_color": "#4488ff",
        "accent_color": "#22ddaa",
        "intensity": 0.3,
        "speed": 0.2,
        "postprocess": PostProcessParams(bloom=0.45, vignette=0.5),
        "layers": [
            LayerConfig(
                effect_name="aurora",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#050518",
                primary_color="#4488ff",
                accent_color="#22ddaa",
                intensity=0.3,
                speed=0.2,
                aurora=AuroraParams(band_count=6, wave_height=0.35),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.4,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#88bbff",
                accent_color="#66eebb",
                intensity=0.2,
                speed=0.15,
                particles=ParticleParams(count=80, connection_dist=0.2),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DARK AMBIENT — slow fractal + near-black (minimal, foreboding)
    # ------------------------------------------------------------------
    "dark-ambient": {
        "bg_color": "#020204",
        "primary_color": "#1a2244",
        "accent_color": "#334466",
        "intensity": 0.2,
        "speed": 0.08,
        "postprocess": PostProcessParams(bloom=0.2, vignette=0.65),
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#020204",
                primary_color="#1a2244",
                accent_color="#334466",
                intensity=0.15,
                speed=0.06,
                fractal=FractalParams(zoom_rate=0.3),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.2,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#223355",
                accent_color="#445577",
                intensity=0.15,
                speed=0.05,
                particles=ParticleParams(count=40, connection_dist=0.25),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # SYNTHWAVE — retro grid + plasma glow (outrun aesthetic)
    # Completely distinct from techno: warm sunset, perspective grid,
    # dreamy plasma glow, scanlines, chromatic aberration
    # ------------------------------------------------------------------
    "synthwave": {
        "bg_color": "#0a001e",
        "primary_color": "#ff2299",
        "accent_color": "#00ffee",
        "intensity": 0.7,
        "speed": 0.5,
        "postprocess": PostProcessParams(
            bloom=0.35,
            vignette=0.4,
            scanlines=0.12,
            scanline_spacing=3,
            chromatic=2,
        ),
        "layers": [
            LayerConfig(
                effect_name="retro_grid",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#0a001e",
                primary_color="#ff2299",
                accent_color="#ffaa00",
                intensity=0.7,
                speed=0.5,
                retro_grid=RetroGridParams(grid_density=12, sun_size=0.2, horizon_pos=0.38),
            ),
            LayerConfig(
                effect_name="plasma",
                opacity=0.2,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.add,
                primary_color="#ff2299",
                accent_color="#00ffee",
                intensity=0.3,
                speed=0.25,
                plasma=PlasmaParams(layer_count=3, wave_freq=2.0),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # TECHNO — tunnel + particles + glitch (industrial, aggressive)
    # Hard geometry, glitch on beats, green/red contrast, bloom glow
    # ------------------------------------------------------------------
    "techno": {
        "bg_color": "#0a0a0a",
        "primary_color": "#00ff88",
        "accent_color": "#ff0066",
        "intensity": 0.8,
        "speed": 0.6,
        "postprocess": PostProcessParams(
            bloom=0.25,
            vignette=0.35,
            glitch=True,
            glitch_threshold=0.65,
            chromatic=1,
        ),
        "layers": [
            LayerConfig(
                effect_name="tunnel",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#00ff88",
                accent_color="#ff0066",
                intensity=0.8,
                speed=0.5,
                tunnel=TunnelParams(twist_speed=1.2, ring_count=8),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.5,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#00ff88",
                accent_color="#ff0066",
                intensity=0.8,
                speed=0.6,
                particles=ParticleParams(count=100, connection_dist=0.1),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DARK TECHNO — matrix rain + fractal (cyberpunk, dystopian)
    # ------------------------------------------------------------------
    "dark-techno": {
        "bg_color": "#000000",
        "primary_color": "#00cc44",
        "accent_color": "#cc0044",
        "intensity": 0.85,
        "speed": 0.7,
        "postprocess": PostProcessParams(
            bloom=0.2, vignette=0.45, glitch=True, glitch_threshold=0.6,
        ),
        "layers": [
            LayerConfig(
                effect_name="matrix_rain",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#000000",
                primary_color="#00cc44",
                accent_color="#88ffaa",
                intensity=0.8,
                speed=0.65,
                matrix_rain=MatrixRainParams(column_count=55, drop_length=20),
            ),
            LayerConfig(
                effect_name="fractal",
                opacity=0.25,
                beat_response=BeatResponse.inverse,
                blend_mode=BlendMode.screen,
                primary_color="#00aa33",
                accent_color="#cc0044",
                intensity=0.5,
                speed=0.5,
                fractal=FractalParams(zoom_rate=0.8),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # MELODIC TECHNO — aurora + tunnel (warm + mechanical = emotion)
    # ------------------------------------------------------------------
    "melodic-techno": {
        "bg_color": "#08061a",
        "primary_color": "#8844ff",
        "accent_color": "#ff4488",
        "intensity": 0.6,
        "speed": 0.45,
        "postprocess": PostProcessParams(bloom=0.35, vignette=0.4),
        "layers": [
            LayerConfig(
                effect_name="aurora",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#08061a",
                primary_color="#6633cc",
                accent_color="#ff4488",
                intensity=0.5,
                speed=0.35,
                aurora=AuroraParams(band_count=4, wave_height=0.25),
            ),
            LayerConfig(
                effect_name="tunnel",
                opacity=0.35,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#8844ff",
                accent_color="#ff4488",
                intensity=0.6,
                speed=0.45,
                tunnel=TunnelParams(twist_speed=0.6, ring_count=6),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # HOUSE — waveform bars + plasma (warm, bouncy, festival)
    # ------------------------------------------------------------------
    "house": {
        "bg_color": "#0a0510",
        "primary_color": "#ff6600",
        "accent_color": "#ffcc00",
        "intensity": 0.65,
        "speed": 0.5,
        "postprocess": PostProcessParams(bloom=0.3, vignette=0.3),
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#0a0510",
                primary_color="#441800",
                accent_color="#ff6600",
                intensity=0.3,
                speed=0.3,
                plasma=PlasmaParams(layer_count=3, wave_freq=2.0),
            ),
            LayerConfig(
                effect_name="waveform",
                opacity=0.65,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#ff6600",
                accent_color="#ffcc00",
                intensity=0.65,
                speed=0.5,
                waveform=WaveformParams(bar_count=40, mirror=True, style="pointed"),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DEEP HOUSE — plasma + tunnel (liquid, submerged, hypnotic depth)
    # Slow morphing plasma backdrop with a gentle tunnel vortex pulling
    # the viewer deeper — smooth, warm, underwater feel
    # ------------------------------------------------------------------
    "deep-house": {
        "bg_color": "#060612",
        "primary_color": "#ff4488",
        "accent_color": "#44aaff",
        "intensity": 0.4,
        "speed": 0.3,
        "postprocess": PostProcessParams(bloom=0.4, vignette=0.5),
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#060612",
                primary_color="#cc2266",
                accent_color="#44aaff",
                intensity=0.3,
                speed=0.2,
                plasma=PlasmaParams(layer_count=5, wave_freq=1.5),
            ),
            LayerConfig(
                effect_name="tunnel",
                opacity=0.35,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#ff4488",
                accent_color="#44aaff",
                intensity=0.3,
                speed=0.2,
                tunnel=TunnelParams(twist_speed=0.4, ring_count=5),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # PSYTRANCE — fractal + tunnel (psychedelic, trippy, intense)
    # ------------------------------------------------------------------
    "psytrance": {
        "bg_color": "#08002e",
        "primary_color": "#ff00ff",
        "accent_color": "#00ffff",
        "intensity": 0.9,
        "speed": 0.75,
        "postprocess": PostProcessParams(
            bloom=0.35, chromatic=3, vignette=0.3,
        ),
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#08002e",
                primary_color="#ff00ff",
                accent_color="#00ffff",
                intensity=0.9,
                speed=0.75,
                fractal=FractalParams(zoom_rate=1.5),
            ),
            LayerConfig(
                effect_name="tunnel",
                opacity=0.3,
                beat_response=BeatResponse.inverse,
                blend_mode=BlendMode.add,
                primary_color="#cc00cc",
                accent_color="#00cccc",
                intensity=0.6,
                speed=0.6,
                tunnel=TunnelParams(twist_speed=1.8, ring_count=6),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DRUM AND BASS — waveform + particles (explosive, fast, chaotic)
    # ------------------------------------------------------------------
    "drum-and-bass": {
        "bg_color": "#080404",
        "primary_color": "#ff4400",
        "accent_color": "#00ffaa",
        "intensity": 0.85,
        "speed": 0.85,
        "postprocess": PostProcessParams(
            bloom=0.25, glitch=True, glitch_threshold=0.55,
        ),
        "layers": [
            LayerConfig(
                effect_name="waveform",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#080404",
                primary_color="#ff4400",
                accent_color="#00ffaa",
                intensity=0.85,
                speed=0.85,
                waveform=WaveformParams(bar_count=64, mirror=True, style="flat"),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.5,
                beat_response=BeatResponse.double,
                blend_mode=BlendMode.add,
                primary_color="#ff4400",
                accent_color="#00ffaa",
                intensity=0.8,
                speed=0.9,
                particles=ParticleParams(count=150, connection_dist=0.08),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # INDUSTRIAL — matrix rain + tunnel (harsh, mechanical, dystopian)
    # ------------------------------------------------------------------
    "industrial": {
        "bg_color": "#050302",
        "primary_color": "#cc4400",
        "accent_color": "#ff2200",
        "intensity": 0.8,
        "speed": 0.6,
        "postprocess": PostProcessParams(
            bloom=0.15, vignette=0.5, glitch=True, glitch_threshold=0.5,
            scanlines=0.1, scanline_spacing=4,
        ),
        "layers": [
            LayerConfig(
                effect_name="matrix_rain",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#050302",
                primary_color="#cc4400",
                accent_color="#ff6600",
                intensity=0.7,
                speed=0.55,
                matrix_rain=MatrixRainParams(column_count=45, drop_length=15),
            ),
            LayerConfig(
                effect_name="tunnel",
                opacity=0.3,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#aa3300",
                accent_color="#ff2200",
                intensity=0.7,
                speed=0.6,
                tunnel=TunnelParams(twist_speed=1.8, ring_count=10),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # EDM — tunnel + waveform (festival laser tunnel with spectrum bars)
    # Forward-rushing geometric tunnel with mirrored spectrum analyzer —
    # neon blue/magenta, high energy, glitch on drops. Distinct from
    # synthwave (no retro grid/sun) and techno (different colors, waveform
    # overlay instead of particles).
    # ------------------------------------------------------------------
    "edm": {
        "bg_color": "#04001a",
        "primary_color": "#00ccff",
        "accent_color": "#ff00cc",
        "intensity": 0.85,
        "speed": 0.7,
        "postprocess": PostProcessParams(
            bloom=0.3, chromatic=2, glitch=True, glitch_threshold=0.7,
        ),
        "layers": [
            LayerConfig(
                effect_name="tunnel",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                bg_color="#04001a",
                primary_color="#00ccff",
                accent_color="#ff00cc",
                intensity=0.8,
                speed=0.65,
                tunnel=TunnelParams(twist_speed=0.8, ring_count=10),
            ),
            LayerConfig(
                effect_name="waveform",
                opacity=0.6,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#00ccff",
                accent_color="#ff00cc",
                intensity=0.85,
                speed=0.7,
                waveform=WaveformParams(bar_count=48, mirror=True, style="pointed"),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # CLASSICAL — plasma + aurora (cool orchestral — slow plasma clouds
    # with silver aurora curtains, deep blue/violet palette. Completely
    # distinct from jazz's warm amber fractals + waveform bars.)
    # ------------------------------------------------------------------
    "classical": {
        "bg_color": "#0a0a1e",
        "primary_color": "#8899cc",
        "accent_color": "#bb99dd",
        "intensity": 0.3,
        "speed": 0.15,
        "postprocess": PostProcessParams(bloom=0.5, vignette=0.6),
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#0a0a1e",
                primary_color="#334488",
                accent_color="#6644aa",
                intensity=0.25,
                speed=0.1,
                plasma=PlasmaParams(layer_count=5, wave_freq=1.2),
            ),
            LayerConfig(
                effect_name="aurora",
                opacity=0.4,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#8899cc",
                accent_color="#bb99dd",
                intensity=0.25,
                speed=0.12,
                aurora=AuroraParams(band_count=4, wave_height=0.4),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # JAZZ — waveform + fractal (smoky lounge — gentle equalizer bars
    # floating over a slow-breathing fractal, intimate and organic)
    # ------------------------------------------------------------------
    "jazz": {
        "bg_color": "#0a0604",
        "primary_color": "#ff8844",
        "accent_color": "#4488cc",
        "intensity": 0.4,
        "speed": 0.3,
        "postprocess": PostProcessParams(bloom=0.4, vignette=0.55),
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                bg_color="#0a0604",
                primary_color="#553311",
                accent_color="#4488cc",
                intensity=0.25,
                speed=0.12,
                fractal=FractalParams(zoom_rate=0.3),
            ),
            LayerConfig(
                effect_name="waveform",
                opacity=0.55,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#ff8844",
                accent_color="#4488cc",
                intensity=0.4,
                speed=0.25,
                waveform=WaveformParams(bar_count=24, mirror=False, style="pointed"),
            ),
        ],
    },
}

# Default preset when genre isn't recognized
DEFAULT_PRESET = "techno"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_preset(
    genre: str,
    bpm: int = 120,
    width: int = 1920,
    height: int = 1080,
    seed: int | None = None,
) -> RenderParams:
    """Build RenderParams from a named preset.

    Args:
        genre: Genre key (e.g. "ambient", "synthwave"). Falls back to
            DEFAULT_PRESET if unknown.
        bpm: Beats per minute.
        width: Frame width.
        height: Frame height.
        seed: Optional reproducibility seed.

    Returns:
        Fully populated RenderParams with layers from the preset.
    """
    preset = PRESETS.get(genre, PRESETS[DEFAULT_PRESET])

    kwargs = {
        **preset,
        "bpm": bpm,
        "width": width,
        "height": height,
    }
    if seed is not None:
        kwargs["seed"] = seed

    # Ensure postprocess is a PostProcessParams instance if present as dict
    if "postprocess" not in kwargs:
        kwargs["postprocess"] = PostProcessParams()

    # effect_name for backward compat — use first layer's effect
    if "layers" in kwargs and kwargs["layers"]:
        kwargs["effect_name"] = kwargs["layers"][0].effect_name

    return RenderParams(**kwargs)


def list_presets() -> list[str]:
    """Return sorted list of available preset names."""
    return sorted(PRESETS.keys())
