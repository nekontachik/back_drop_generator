"""Pydantic schemas for render parameters (D-01 through D-05).

Supports both single-effect mode (effect_name) and multi-layer
compositing mode (layers list). When layers is non-empty it takes
precedence over effect_name.
"""

from __future__ import annotations

import random
from enum import Enum

from pydantic import BaseModel, Field


class TunnelParams(BaseModel):
    """Per-effect overrides for tunnel effect (D-03)."""

    twist_speed: float = 1.0
    ring_count: int = 8


class FractalParams(BaseModel):
    """Per-effect overrides for fractal (Julia set) effect (D-03)."""

    zoom_rate: float = 1.0
    c_param: complex = complex(-0.7, 0.27015)


class ParticleParams(BaseModel):
    """Per-effect overrides for particle system effect (D-03)."""

    count: int = 200
    connection_dist: float = 0.15


class PlasmaParams(BaseModel):
    """Per-effect overrides for plasma waves effect (D-03)."""

    layer_count: int = 4
    wave_freq: float = 3.0


class RetroGridParams(BaseModel):
    """Per-effect overrides for retro grid (synthwave) effect."""

    grid_density: int = 12
    sun_size: float = 0.18
    horizon_pos: float = 0.4


class AuroraParams(BaseModel):
    """Per-effect overrides for aurora (northern lights) effect."""

    band_count: int = 5
    wave_height: float = 0.3


class WaveformParams(BaseModel):
    """Per-effect overrides for waveform (spectrum bars) effect."""

    bar_count: int = 48
    mirror: bool = True
    style: str = "pointed"  # "pointed" or "flat"


class MatrixRainParams(BaseModel):
    """Per-effect overrides for matrix rain effect."""

    column_count: int = 60
    drop_length: int = 18


class PostProcessParams(BaseModel):
    """Post-processing configuration for a preset."""

    bloom: float = Field(default=0.0, ge=0.0, le=1.0)
    bloom_radius: int = 21
    vignette: float = Field(default=0.0, ge=0.0, le=1.0)
    scanlines: float = Field(default=0.0, ge=0.0, le=1.0)
    scanline_spacing: int = 3
    chromatic: int = Field(default=0, ge=0, le=8)
    glitch: bool = False
    glitch_threshold: float = 0.7


class BeatResponse(str, Enum):
    """How a layer reacts to the beat envelope.

    - normal:   raw beat_intensity as-is (sharp attack, exp decay).
    - smooth:   low-pass filtered beat — gentle swells for backgrounds.
    - inverse:  1 - beat_intensity — quiet on beat, active between.
    - double:   twice-speed perceived rhythm (half beat interval).
    """

    normal = "normal"
    smooth = "smooth"
    inverse = "inverse"
    double = "double"


class BlendMode(str, Enum):
    """Compositing blend mode between layers.

    - alpha:    standard opacity blend (bottom * (1-a) + top * a).
    - add:      additive (clamp to 255) — great for glows.
    - screen:   1 - (1-a)*(1-b) — brightens without blowing out.
    """

    alpha = "alpha"
    add = "add"
    screen = "screen"


class LayerConfig(BaseModel):
    """Configuration for one compositing layer.

    Each layer picks an effect, its own colours, and how it reacts
    to the beat. Layers are rendered bottom-to-top; the first layer
    in the list is the background.
    """

    effect_name: str = "plasma"
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    beat_response: BeatResponse = BeatResponse.normal
    blend_mode: BlendMode = BlendMode.alpha

    # Optional per-layer colour overrides — if None, inherit from parent
    bg_color: str | None = None
    primary_color: str | None = None
    accent_color: str | None = None
    intensity: float | None = Field(default=None, ge=0.0, le=1.0)
    speed: float | None = Field(default=None, ge=0.0, le=1.0)

    # Per-effect overrides (only the matching one is used)
    tunnel: TunnelParams = Field(default_factory=TunnelParams)
    fractal: FractalParams = Field(default_factory=FractalParams)
    particles: ParticleParams = Field(default_factory=ParticleParams)
    plasma: PlasmaParams = Field(default_factory=PlasmaParams)
    retro_grid: RetroGridParams = Field(default_factory=RetroGridParams)
    aurora: AuroraParams = Field(default_factory=AuroraParams)
    waveform: WaveformParams = Field(default_factory=WaveformParams)
    matrix_rain: MatrixRainParams = Field(default_factory=MatrixRainParams)

    model_config = {"arbitrary_types_allowed": True}


class RenderParams(BaseModel):
    """Full render parameter schema (D-01, D-02, D-04, D-05).

    Shared base params + per-effect overrides. Designed to be populated
    by keyword matching in Phase 1 and by LLM output in Phase 4.

    When ``layers`` is non-empty, multi-layer compositing is used and
    ``effect_name`` is ignored. Otherwise falls back to single-effect
    mode for backward compatibility.
    """

    # Shared base params (D-02)
    bg_color: str = "#0a0a0a"
    primary_color: str = "#00ff88"
    accent_color: str = "#ff0066"
    intensity: float = Field(default=0.7, ge=0.0, le=1.0)
    speed: float = Field(default=0.5, ge=0.0, le=1.0)

    # Single-effect mode (legacy / simple)
    effect_name: str = "tunnel"

    # Multi-layer compositing mode
    layers: list[LayerConfig] = Field(default_factory=list)

    # BPM and reproducibility
    bpm: int = Field(default=120, ge=60, le=200)
    seed: int = Field(default_factory=lambda: random.randint(0, 2**32 - 1))

    # Resolution
    width: int = 1920
    height: int = 1080
    fps: int = 30

    # Per-effect overrides (D-03) — used in single-effect mode
    tunnel: TunnelParams = Field(default_factory=TunnelParams)
    fractal: FractalParams = Field(default_factory=FractalParams)
    particles: ParticleParams = Field(default_factory=ParticleParams)
    plasma: PlasmaParams = Field(default_factory=PlasmaParams)
    retro_grid: RetroGridParams = Field(default_factory=RetroGridParams)
    aurora: AuroraParams = Field(default_factory=AuroraParams)
    waveform: WaveformParams = Field(default_factory=WaveformParams)
    matrix_rain: MatrixRainParams = Field(default_factory=MatrixRainParams)

    # Post-processing configuration
    postprocess: PostProcessParams = Field(default_factory=PostProcessParams)

    model_config = {"arbitrary_types_allowed": True}
