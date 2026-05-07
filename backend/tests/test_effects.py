"""Tests for visual effects (VFX-01 through VFX-04).

Verifies shape, dtype, visual content, registry presence, and
reproducibility for all 4 effects.
"""

from __future__ import annotations

import numpy as np
import pytest

# Import all effect modules to trigger @register decorators
from app.render.effects import EFFECT_REGISTRY
from app.render.effects import aurora as _aurora_mod  # noqa: F401
from app.render.effects import fractal as _fractal_mod  # noqa: F401
from app.render.effects import matrix_rain as _matrix_rain_mod  # noqa: F401
from app.render.effects import particles as _particles_mod  # noqa: F401
from app.render.effects import plasma as _plasma_mod  # noqa: F401
from app.render.effects import retro_grid as _retro_grid_mod  # noqa: F401
from app.render.effects import tunnel as _tunnel_mod  # noqa: F401
from app.render.effects import waveform as _waveform_mod  # noqa: F401


EFFECT_NAMES = [
    "tunnel", "fractal", "particles", "plasma",
    "retro_grid", "aurora", "waveform", "matrix_rain",
]
TEST_WIDTH = 480
TEST_HEIGHT = 270

DEFAULT_PARAMS = {
    "bg_color": "#0a0a0a",
    "primary_color": "#00ff88",
    "accent_color": "#ff0066",
    "intensity": 0.7,
    "speed": 0.5,
    # tunnel
    "twist_speed": 1.0,
    "ring_count": 8,
    # fractal
    "zoom_rate": 1.0,
    "c_param": complex(-0.7, 0.27015),
    # particles
    "count": 100,
    "connection_dist": 0.15,
    # plasma
    "layer_count": 4,
    "wave_freq": 3.0,
    # retro_grid
    "grid_density": 12,
    "sun_size": 0.18,
    "horizon_pos": 0.4,
    # aurora
    "band_count": 5,
    "wave_height": 0.3,
    # waveform
    "bar_count": 32,
    "mirror": True,
    "style": "pointed",
    # matrix_rain
    "column_count": 40,
    "drop_length": 15,
}


class TestEffectRegistry:
    """Test that all effects are registered."""

    def test_all_effects_registered(self) -> None:
        for name in EFFECT_NAMES:
            assert name in EFFECT_REGISTRY, f"Effect '{name}' not in EFFECT_REGISTRY"

    def test_registry_has_all_effects(self) -> None:
        assert len(EFFECT_REGISTRY) == len(EFFECT_NAMES)


class TestEffectRendering:
    """Test rendering output for each effect."""

    @pytest.mark.parametrize("effect_name", EFFECT_NAMES)
    @pytest.mark.parametrize("t", [0.0, 0.5])
    def test_output_shape_and_dtype(self, effect_name: str, t: float) -> None:
        effect = EFFECT_REGISTRY[effect_name]()
        rng = np.random.default_rng(42)
        frame = effect.render_frame(t, TEST_WIDTH, TEST_HEIGHT, DEFAULT_PARAMS, 0.5, rng)

        assert frame.shape == (TEST_HEIGHT, TEST_WIDTH, 3), (
            f"{effect_name} at t={t}: shape {frame.shape} != ({TEST_HEIGHT}, {TEST_WIDTH}, 3)"
        )
        assert frame.dtype == np.uint8, f"{effect_name} at t={t}: dtype {frame.dtype} != uint8"

    @pytest.mark.parametrize("effect_name", EFFECT_NAMES)
    def test_output_has_visual_content(self, effect_name: str) -> None:
        """Output should not be all zeros or all one color."""
        effect = EFFECT_REGISTRY[effect_name]()
        rng = np.random.default_rng(42)
        frame = effect.render_frame(0.25, TEST_WIDTH, TEST_HEIGHT, DEFAULT_PARAMS, 0.5, rng)

        # Not all zeros
        assert frame.sum() > 0, f"{effect_name}: frame is all zeros"

        # Not all one color: check that standard deviation is nonzero
        assert frame.std() > 1.0, f"{effect_name}: frame has no visual variation (std={frame.std():.2f})"


class TestReproducibility:
    """Test that same seed + params + t produces identical output."""

    @pytest.mark.parametrize("effect_name", EFFECT_NAMES)
    def test_same_seed_same_output(self, effect_name: str) -> None:
        effect = EFFECT_REGISTRY[effect_name]()

        rng1 = np.random.default_rng(42)
        frame1 = effect.render_frame(0.3, TEST_WIDTH, TEST_HEIGHT, DEFAULT_PARAMS, 0.5, rng1)

        rng2 = np.random.default_rng(42)
        frame2 = effect.render_frame(0.3, TEST_WIDTH, TEST_HEIGHT, DEFAULT_PARAMS, 0.5, rng2)

        np.testing.assert_array_equal(
            frame1, frame2, err_msg=f"{effect_name}: not reproducible with same seed"
        )
