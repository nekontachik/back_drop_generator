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
    BeatResponse,
    BlendMode,
    LayerConfig,
    ParticleParams,
    PlasmaParams,
    RenderParams,
    TunnelParams,
    FractalParams,
)

# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------
# Each preset is a dict of RenderParams kwargs. Layers are ordered
# bottom (background) → top (foreground).
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # ------------------------------------------------------------------
    # AMBIENT — plasma clouds + gentle breathing particles
    # ------------------------------------------------------------------
    "ambient": {
        "bg_color": "#0a0a2e",
        "primary_color": "#4488ff",
        "accent_color": "#88ccff",
        "intensity": 0.3,
        "speed": 0.2,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#223366",
                accent_color="#4488ff",
                intensity=0.2,
                speed=0.15,
                plasma=PlasmaParams(layer_count=5, wave_freq=2.0),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.6,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#4488ff",
                accent_color="#88ccff",
                intensity=0.3,
                speed=0.2,
                particles=ParticleParams(count=150, connection_dist=0.18),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DARK AMBIENT — near-black plasma + sparse dim particles
    # ------------------------------------------------------------------
    "dark-ambient": {
        "bg_color": "#050508",
        "primary_color": "#223355",
        "accent_color": "#445566",
        "intensity": 0.2,
        "speed": 0.1,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#111122",
                accent_color="#223344",
                intensity=0.15,
                speed=0.08,
                plasma=PlasmaParams(layer_count=3, wave_freq=1.5),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.35,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#223355",
                accent_color="#445566",
                intensity=0.2,
                speed=0.1,
                particles=ParticleParams(count=80, connection_dist=0.12),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # SYNTHWAVE — tunnel + plasma glow overlay
    # ------------------------------------------------------------------
    "synthwave": {
        "bg_color": "#1a0030",
        "primary_color": "#ff2299",
        "accent_color": "#00ffee",
        "intensity": 0.7,
        "speed": 0.6,
        "layers": [
            LayerConfig(
                effect_name="tunnel",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#ff2299",
                accent_color="#00ffee",
                intensity=0.7,
                speed=0.6,
                tunnel=TunnelParams(twist_speed=1.2, ring_count=10),
            ),
            LayerConfig(
                effect_name="plasma",
                opacity=0.3,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.add,
                primary_color="#ff2299",
                accent_color="#00ffee",
                intensity=0.4,
                speed=0.3,
                plasma=PlasmaParams(layer_count=3, wave_freq=2.5),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # TECHNO — tunnel base + particles on beat
    # ------------------------------------------------------------------
    "techno": {
        "bg_color": "#0a0a0a",
        "primary_color": "#00ff88",
        "accent_color": "#ff0066",
        "intensity": 0.8,
        "speed": 0.7,
        "layers": [
            LayerConfig(
                effect_name="tunnel",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#00ff88",
                accent_color="#ff0066",
                intensity=0.8,
                speed=0.7,
                tunnel=TunnelParams(twist_speed=1.5, ring_count=12),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.45,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#00ff88",
                accent_color="#ff0066",
                intensity=0.8,
                speed=0.6,
                particles=ParticleParams(count=120, connection_dist=0.1),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DARK TECHNO — fractal + sparse particles
    # ------------------------------------------------------------------
    "dark-techno": {
        "bg_color": "#050505",
        "primary_color": "#00cc66",
        "accent_color": "#cc0044",
        "intensity": 0.85,
        "speed": 0.75,
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#00cc66",
                accent_color="#cc0044",
                intensity=0.85,
                speed=0.7,
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.35,
                beat_response=BeatResponse.double,
                blend_mode=BlendMode.add,
                primary_color="#00cc66",
                accent_color="#cc0044",
                intensity=0.7,
                speed=0.8,
                particles=ParticleParams(count=80, connection_dist=0.08),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # MELODIC TECHNO — plasma base + tunnel overlay
    # ------------------------------------------------------------------
    "melodic-techno": {
        "bg_color": "#0a0a1e",
        "primary_color": "#6644ff",
        "accent_color": "#ff4488",
        "intensity": 0.65,
        "speed": 0.55,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#4422aa",
                accent_color="#6644ff",
                intensity=0.5,
                speed=0.4,
                plasma=PlasmaParams(layer_count=4, wave_freq=2.5),
            ),
            LayerConfig(
                effect_name="tunnel",
                opacity=0.5,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#6644ff",
                accent_color="#ff4488",
                intensity=0.65,
                speed=0.55,
                tunnel=TunnelParams(twist_speed=0.8, ring_count=8),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # HOUSE — warm plasma + bouncy particles
    # ------------------------------------------------------------------
    "house": {
        "bg_color": "#1a0a2e",
        "primary_color": "#ff6600",
        "accent_color": "#ffcc00",
        "intensity": 0.6,
        "speed": 0.5,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#cc4400",
                accent_color="#ff6600",
                intensity=0.5,
                speed=0.4,
                plasma=PlasmaParams(layer_count=4, wave_freq=3.0),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.55,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#ff6600",
                accent_color="#ffcc00",
                intensity=0.6,
                speed=0.5,
                particles=ParticleParams(count=150, connection_dist=0.14),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DEEP HOUSE — plasma only, smooth and warm
    # ------------------------------------------------------------------
    "deep-house": {
        "bg_color": "#0a0a1e",
        "primary_color": "#ff4488",
        "accent_color": "#44aaff",
        "intensity": 0.45,
        "speed": 0.35,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#cc2266",
                accent_color="#ff4488",
                intensity=0.4,
                speed=0.3,
                plasma=PlasmaParams(layer_count=5, wave_freq=2.0),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.4,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#ff4488",
                accent_color="#44aaff",
                intensity=0.45,
                speed=0.35,
                particles=ParticleParams(count=100, connection_dist=0.16),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # PSYTRANCE — fractal base + plasma glow
    # ------------------------------------------------------------------
    "psytrance": {
        "bg_color": "#0a002e",
        "primary_color": "#ff00ff",
        "accent_color": "#00ffff",
        "intensity": 0.9,
        "speed": 0.8,
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#ff00ff",
                accent_color="#00ffff",
                intensity=0.9,
                speed=0.8,
                fractal=FractalParams(zoom_rate=1.5),
            ),
            LayerConfig(
                effect_name="plasma",
                opacity=0.35,
                beat_response=BeatResponse.inverse,
                blend_mode=BlendMode.add,
                primary_color="#ff00ff",
                accent_color="#00ffff",
                intensity=0.6,
                speed=0.5,
                plasma=PlasmaParams(layer_count=3, wave_freq=4.0),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # DRUM AND BASS — explosive particles + plasma undertow
    # ------------------------------------------------------------------
    "drum-and-bass": {
        "bg_color": "#0a0a14",
        "primary_color": "#ff4400",
        "accent_color": "#00ffaa",
        "intensity": 0.85,
        "speed": 0.9,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#881100",
                accent_color="#ff4400",
                intensity=0.5,
                speed=0.4,
                plasma=PlasmaParams(layer_count=3, wave_freq=3.5),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.7,
                beat_response=BeatResponse.double,
                blend_mode=BlendMode.add,
                primary_color="#ff4400",
                accent_color="#00ffaa",
                intensity=0.85,
                speed=0.9,
                particles=ParticleParams(count=200, connection_dist=0.1),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # INDUSTRIAL — tunnel + fractal overlay
    # ------------------------------------------------------------------
    "industrial": {
        "bg_color": "#080808",
        "primary_color": "#aa4400",
        "accent_color": "#ff2200",
        "intensity": 0.8,
        "speed": 0.65,
        "layers": [
            LayerConfig(
                effect_name="tunnel",
                opacity=1.0,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.alpha,
                primary_color="#aa4400",
                accent_color="#ff2200",
                intensity=0.8,
                speed=0.65,
                tunnel=TunnelParams(twist_speed=2.0, ring_count=14),
            ),
            LayerConfig(
                effect_name="fractal",
                opacity=0.3,
                beat_response=BeatResponse.inverse,
                blend_mode=BlendMode.screen,
                primary_color="#aa4400",
                accent_color="#ff2200",
                intensity=0.6,
                speed=0.5,
            ),
        ],
    },
    # ------------------------------------------------------------------
    # EDM — plasma + particles, max energy
    # ------------------------------------------------------------------
    "edm": {
        "bg_color": "#0a001e",
        "primary_color": "#00aaff",
        "accent_color": "#ff00aa",
        "intensity": 0.75,
        "speed": 0.65,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#0066cc",
                accent_color="#00aaff",
                intensity=0.6,
                speed=0.5,
                plasma=PlasmaParams(layer_count=4, wave_freq=3.0),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.6,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.add,
                primary_color="#00aaff",
                accent_color="#ff00aa",
                intensity=0.75,
                speed=0.65,
                particles=ParticleParams(count=180, connection_dist=0.12),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # CLASSICAL — gentle fractal + soft particles
    # ------------------------------------------------------------------
    "classical": {
        "bg_color": "#0a0a14",
        "primary_color": "#ccaa44",
        "accent_color": "#ffddaa",
        "intensity": 0.35,
        "speed": 0.25,
        "layers": [
            LayerConfig(
                effect_name="fractal",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#ccaa44",
                accent_color="#ffddaa",
                intensity=0.3,
                speed=0.2,
                fractal=FractalParams(zoom_rate=0.5),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.35,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.screen,
                primary_color="#ccaa44",
                accent_color="#ffddaa",
                intensity=0.3,
                speed=0.2,
                particles=ParticleParams(count=80, connection_dist=0.2),
            ),
        ],
    },
    # ------------------------------------------------------------------
    # JAZZ — warm plasma + connected particles
    # ------------------------------------------------------------------
    "jazz": {
        "bg_color": "#0a0a0a",
        "primary_color": "#ff8844",
        "accent_color": "#44aaff",
        "intensity": 0.4,
        "speed": 0.35,
        "layers": [
            LayerConfig(
                effect_name="plasma",
                opacity=1.0,
                beat_response=BeatResponse.smooth,
                blend_mode=BlendMode.alpha,
                primary_color="#cc6622",
                accent_color="#ff8844",
                intensity=0.35,
                speed=0.3,
                plasma=PlasmaParams(layer_count=4, wave_freq=2.0),
            ),
            LayerConfig(
                effect_name="particles",
                opacity=0.5,
                beat_response=BeatResponse.normal,
                blend_mode=BlendMode.screen,
                primary_color="#ff8844",
                accent_color="#44aaff",
                intensity=0.4,
                speed=0.35,
                particles=ParticleParams(count=120, connection_dist=0.18),
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

    # effect_name for backward compat — use first layer's effect
    if "layers" in kwargs and kwargs["layers"]:
        kwargs["effect_name"] = kwargs["layers"][0].effect_name

    return RenderParams(**kwargs)


def list_presets() -> list[str]:
    """Return sorted list of available preset names."""
    return sorted(PRESETS.keys())
