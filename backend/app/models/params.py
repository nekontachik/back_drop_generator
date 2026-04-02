"""Pydantic schemas for render parameters (D-01 through D-05)."""

from __future__ import annotations

import random

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


class RenderParams(BaseModel):
    """Full render parameter schema (D-01, D-02, D-04, D-05).

    Shared base params + per-effect overrides. Designed to be populated
    by keyword matching in Phase 1 and by LLM output in Phase 4.
    """

    # Shared base params (D-02)
    bg_color: str = "#0a0a0a"
    primary_color: str = "#00ff88"
    accent_color: str = "#ff0066"
    intensity: float = Field(default=0.7, ge=0.0, le=1.0)
    speed: float = Field(default=0.5, ge=0.0, le=1.0)

    # Effect selection
    effect_name: str = "tunnel"

    # BPM and reproducibility
    bpm: int = Field(default=120, ge=60, le=200)
    seed: int = Field(default_factory=lambda: random.randint(0, 2**32 - 1))

    # Resolution
    width: int = 1920
    height: int = 1080
    fps: int = 30

    # Per-effect overrides (D-03)
    tunnel: TunnelParams = Field(default_factory=TunnelParams)
    fractal: FractalParams = Field(default_factory=FractalParams)
    particles: ParticleParams = Field(default_factory=ParticleParams)
    plasma: PlasmaParams = Field(default_factory=PlasmaParams)

    model_config = {"arbitrary_types_allowed": True}
