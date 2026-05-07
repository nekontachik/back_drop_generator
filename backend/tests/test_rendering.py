"""Structural rendering tests.

These tests verify *behaviour*, not pixels. They answer questions like:
- Do particles actually move more when beat_intensity is high?
- Does additive blending produce brighter output than alpha?
- Is the smooth envelope actually smoother than the normal one?
- Do all presets render without crashing?
- Does compositing produce the expected frame shape?

Every test renders at tiny resolution (64×48) for speed. No ffmpeg
needed — we test render_frame and pipeline helpers directly.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.models.params import (
    BeatResponse,
    BlendMode,
    LayerConfig,
    ParticleParams,
    PlasmaParams,
    RenderParams,
    TunnelParams,
)
from app.render.effects import EFFECT_REGISTRY

# Trigger effect registration
from app.render.effects import aurora as _a  # noqa: F401
from app.render.effects import fractal as _f  # noqa: F401
from app.render.effects import matrix_rain as _mr  # noqa: F401
from app.render.effects import particles as _p  # noqa: F401
from app.render.effects import plasma as _pl  # noqa: F401
from app.render.effects import retro_grid as _rg  # noqa: F401
from app.render.effects import tunnel as _t  # noqa: F401
from app.render.effects import waveform as _wf  # noqa: F401
from app.render.loop_math import build_synthetic_beat_envelope, calculate_loop_params
from app.render.pipeline import _apply_beat_response, _blend_layers
from app.render.presets import PRESETS, get_preset, list_presets

# ---------------------------------------------------------------------------
# Constants for fast test rendering
# ---------------------------------------------------------------------------
W, H = 64, 48
BPM = 120
FPS = 30
SEED = 42


def _make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def _base_params() -> dict:
    return {
        "bg_color": "#0a0a0a",
        "primary_color": "#00ff88",
        "accent_color": "#ff0066",
        "intensity": 0.7,
        "speed": 0.5,
        "count": 100,
        "connection_dist": 0.15,
        "twist_speed": 1.0,
        "ring_count": 8,
        "zoom_rate": 1.0,
        "c_param": complex(-0.7, 0.27015),
        "layer_count": 4,
        "wave_freq": 3.0,
    }


# ===================================================================
# 1. PARTICLE BEAT BREATHING
# ===================================================================

class TestParticleBreathing:
    """Verify particles respond to beat_intensity."""

    def _render_particles(self, beat_intensity: float) -> np.ndarray:
        effect = EFFECT_REGISTRY["particles"]()
        return effect.render_frame(
            t=0.25,
            width=W,
            height=H,
            params=_base_params(),
            beat_intensity=beat_intensity,
            rng=_make_rng(),
        )

    def test_frame_shape_and_dtype(self):
        """Rendered frame must be (H, W, 3) uint8."""
        frame = self._render_particles(0.5)
        assert frame.shape == (H, W, 3)
        assert frame.dtype == np.uint8

    def test_beat_makes_frame_brighter(self):
        """High beat_intensity should produce a brighter frame on average
        (particles are bigger, more opaque, connections brighter)."""
        frame_quiet = self._render_particles(0.0)
        frame_loud = self._render_particles(1.0)
        assert frame_loud.mean() > frame_quiet.mean(), (
            f"Loud frame (mean={frame_loud.mean():.1f}) should be brighter "
            f"than quiet frame (mean={frame_quiet.mean():.1f})"
        )

    def test_particle_displacement_increases_with_beat(self):
        """Non-background pixel positions should differ more from base
        positions when beat_intensity is high vs low."""
        # Render at t=0 with different beat intensities
        effect = EFFECT_REGISTRY["particles"]()
        params = _base_params()

        # Count non-background pixels as proxy for particle spread
        frame_lo = effect.render_frame(0.0, W, H, params, 0.0, _make_rng())
        frame_hi = effect.render_frame(0.0, W, H, params, 1.0, _make_rng())

        bg = np.array([10, 10, 10], dtype=np.uint8)  # #0a0a0a
        lit_lo = np.sum(np.any(np.abs(frame_lo.astype(int) - bg.astype(int)) > 15, axis=-1))
        lit_hi = np.sum(np.any(np.abs(frame_hi.astype(int) - bg.astype(int)) > 15, axis=-1))

        assert lit_hi >= lit_lo, (
            f"High beat should light up at least as many pixels ({lit_hi}) "
            f"as low beat ({lit_lo})"
        )

    def test_colour_shifts_toward_accent_on_beat(self):
        """On beat, particle colour should shift toward accent (#ff0066)."""
        frame_quiet = self._render_particles(0.0)
        frame_loud = self._render_particles(1.0)

        # Accent is #ff0066 → R=255, G=0, B=102
        # Primary is #00ff88 → R=0, G=255, B=136
        # On beat: more red, less green
        mean_r_quiet = frame_quiet[:, :, 0].mean()
        mean_r_loud = frame_loud[:, :, 0].mean()
        assert mean_r_loud > mean_r_quiet, (
            "Red channel should increase on beat (shift toward accent)"
        )


# ===================================================================
# 2. BEAT ENVELOPE TRANSFORMS
# ===================================================================

class TestBeatEnvelope:
    """Verify beat response transforms produce expected characteristics."""

    @pytest.fixture()
    def envelope_data(self):
        total_frames, loop_duration = calculate_loop_params(BPM, FPS)
        raw = build_synthetic_beat_envelope(total_frames, BPM, FPS, loop_duration)
        return raw, total_frames, loop_duration

    def test_normal_is_identity(self, envelope_data):
        raw, tf, ld = envelope_data
        result = _apply_beat_response(raw, BeatResponse.normal, BPM, FPS, ld, tf)
        np.testing.assert_array_equal(result, raw)

    def test_smooth_has_lower_variance(self, envelope_data):
        """Smooth envelope should have less variance than normal."""
        raw, tf, ld = envelope_data
        smooth = _apply_beat_response(raw, BeatResponse.smooth, BPM, FPS, ld, tf)
        assert smooth.var() < raw.var(), (
            f"Smooth variance ({smooth.var():.4f}) should be < "
            f"raw variance ({raw.var():.4f})"
        )

    def test_smooth_preserves_range(self, envelope_data):
        """Smooth should stay in [0, 1] range."""
        raw, tf, ld = envelope_data
        smooth = _apply_beat_response(raw, BeatResponse.smooth, BPM, FPS, ld, tf)
        assert smooth.min() >= 0.0
        assert smooth.max() <= 1.01  # small float tolerance

    def test_inverse_is_complement(self, envelope_data):
        """Inverse should be 1.0 - raw."""
        raw, tf, ld = envelope_data
        inv = _apply_beat_response(raw, BeatResponse.inverse, BPM, FPS, ld, tf)
        np.testing.assert_allclose(inv, 1.0 - raw)

    def test_double_has_more_peaks(self, envelope_data):
        """Double should have roughly twice as many beat peaks."""
        raw, tf, ld = envelope_data
        dbl = _apply_beat_response(raw, BeatResponse.double, BPM, FPS, ld, tf)

        # Count peaks: frames where value > 0.9
        peaks_raw = np.sum(raw > 0.9)
        peaks_dbl = np.sum(dbl > 0.9)
        assert peaks_dbl > peaks_raw, (
            f"Double should have more peaks ({peaks_dbl}) than normal ({peaks_raw})"
        )


# ===================================================================
# 3. BLEND MODES
# ===================================================================

class TestBlendModes:
    """Verify compositing blend modes produce expected results."""

    @pytest.fixture()
    def layers(self):
        bottom = np.full((H, W, 3), 100.0, dtype=np.float64)
        top = np.full((H, W, 3), 150.0, dtype=np.float64)
        return bottom, top

    def test_alpha_blend_50_percent(self, layers):
        bottom, top = layers
        result = _blend_layers(bottom, top, 0.5, BlendMode.alpha)
        expected = 100.0 * 0.5 + 150.0 * 0.5  # 125
        np.testing.assert_allclose(result, expected, atol=0.01)

    def test_alpha_blend_zero_opacity_unchanged(self, layers):
        bottom, top = layers
        result = _blend_layers(bottom, top, 0.0, BlendMode.alpha)
        np.testing.assert_array_equal(result, bottom)

    def test_additive_is_brighter(self, layers):
        """Additive blend should be brighter than alpha blend."""
        bottom, top = layers
        alpha_result = _blend_layers(bottom, top, 0.5, BlendMode.alpha)
        add_result = _blend_layers(bottom, top, 0.5, BlendMode.add)
        assert add_result.mean() > alpha_result.mean(), (
            "Additive blend should be brighter than alpha blend"
        )

    def test_additive_clamped_at_255(self):
        """Additive blend must not exceed 255."""
        bottom = np.full((H, W, 3), 200.0, dtype=np.float64)
        top = np.full((H, W, 3), 200.0, dtype=np.float64)
        result = _blend_layers(bottom, top, 1.0, BlendMode.add)
        assert result.max() <= 255.0

    def test_screen_brighter_than_alpha(self, layers):
        """Screen blend should be brighter than alpha blend."""
        bottom, top = layers
        alpha_result = _blend_layers(bottom, top, 0.5, BlendMode.alpha)
        screen_result = _blend_layers(bottom, top, 0.5, BlendMode.screen)
        assert screen_result.mean() >= alpha_result.mean(), (
            "Screen blend should be at least as bright as alpha blend"
        )

    def test_screen_stays_in_range(self, layers):
        """Screen blend should not exceed 255."""
        bottom, top = layers
        result = _blend_layers(bottom, top, 1.0, BlendMode.screen)
        assert result.max() <= 255.01


# ===================================================================
# 4. ALL EFFECTS RENDER WITHOUT ERRORS
# ===================================================================

class TestAllEffectsRender:
    """Smoke tests — every registered effect produces valid frames."""

    @pytest.mark.parametrize("effect_name", list(EFFECT_REGISTRY.keys()))
    def test_effect_renders_valid_frame(self, effect_name):
        effect = EFFECT_REGISTRY[effect_name]()
        frame = effect.render_frame(
            t=0.5,
            width=W,
            height=H,
            params=_base_params(),
            beat_intensity=0.7,
            rng=_make_rng(),
        )
        assert frame.shape == (H, W, 3), f"Wrong shape: {frame.shape}"
        assert frame.dtype == np.uint8, f"Wrong dtype: {frame.dtype}"
        assert frame.max() > 0, "Frame is completely black"

    @pytest.mark.parametrize("effect_name", list(EFFECT_REGISTRY.keys()))
    def test_effect_deterministic_with_same_seed(self, effect_name):
        """Same t + same seed → identical frame."""
        effect = EFFECT_REGISTRY[effect_name]()
        params = _base_params()
        f1 = effect.render_frame(0.3, W, H, params, 0.5, _make_rng(123))
        f2 = effect.render_frame(0.3, W, H, params, 0.5, _make_rng(123))
        np.testing.assert_array_equal(f1, f2)

    @pytest.mark.parametrize("effect_name", list(EFFECT_REGISTRY.keys()))
    def test_different_t_produces_different_frame(self, effect_name):
        """Different t values should produce visually different frames."""
        effect = EFFECT_REGISTRY[effect_name]()
        params = _base_params()
        # Use t=0.0 vs t=0.3 (not 0.5) to avoid grid-scroll aliasing where
        # scroll distance is an exact integer at some grid_density values.
        f1 = effect.render_frame(0.0, W, H, params, 0.5, _make_rng())
        f2 = effect.render_frame(0.3, W, H, params, 0.5, _make_rng())
        assert not np.array_equal(f1, f2), "Frames at t=0 and t=0.3 should differ"


# ===================================================================
# 5. PRESETS
# ===================================================================

class TestPresets:
    """Verify presets are well-formed and renderable."""

    def test_all_genres_have_presets(self):
        """Every genre YAML should have a matching preset."""
        expected_genres = [
            "ambient", "dark-ambient", "synthwave", "techno",
            "dark-techno", "melodic-techno", "house", "deep-house",
            "psytrance", "drum-and-bass", "industrial", "edm",
            "classical", "jazz",
        ]
        for genre in expected_genres:
            assert genre in PRESETS, f"Missing preset for genre '{genre}'"

    def test_every_preset_has_layers(self):
        """Each preset should define at least one layer."""
        for name, preset in PRESETS.items():
            layers = preset.get("layers", [])
            assert len(layers) >= 1, f"Preset '{name}' has no layers"

    def test_every_preset_builds_valid_renderparams(self):
        """get_preset should return valid RenderParams for every genre."""
        for genre in PRESETS:
            params = get_preset(genre, bpm=120, width=W, height=H, seed=SEED)
            assert isinstance(params, RenderParams)
            assert len(params.layers) >= 1
            assert params.bpm == 120
            assert params.width == W

    @pytest.mark.parametrize("genre", list(PRESETS.keys()))
    def test_preset_layer_effects_are_registered(self, genre):
        """Every effect_name in preset layers must exist in EFFECT_REGISTRY."""
        preset = PRESETS[genre]
        for layer in preset["layers"]:
            assert layer.effect_name in EFFECT_REGISTRY, (
                f"Preset '{genre}' references unregistered effect '{layer.effect_name}'"
            )

    @pytest.mark.parametrize("genre", list(PRESETS.keys()))
    def test_preset_renders_all_layers(self, genre):
        """Render each layer from the preset and verify valid output."""
        params = get_preset(genre, bpm=BPM, width=W, height=H, seed=SEED)
        total_frames, loop_duration = calculate_loop_params(params.bpm, params.fps)
        envelope = build_synthetic_beat_envelope(total_frames, params.bpm, params.fps, loop_duration)

        rng = np.random.default_rng(SEED)
        for layer in params.layers:
            effect = EFFECT_REGISTRY[layer.effect_name]()
            # Build params dict for this layer
            lp = {
                "bg_color": layer.bg_color or params.bg_color,
                "primary_color": layer.primary_color or params.primary_color,
                "accent_color": layer.accent_color or params.accent_color,
                "intensity": layer.intensity if layer.intensity is not None else params.intensity,
                "speed": layer.speed if layer.speed is not None else params.speed,
            }
            lp.update(getattr(layer, layer.effect_name).model_dump())

            frame = effect.render_frame(
                t=0.25,
                width=W,
                height=H,
                params=lp,
                beat_intensity=envelope[5],
                rng=np.random.default_rng(rng.integers(0, 2**32)),
            )
            assert frame.shape == (H, W, 3), (
                f"Genre '{genre}', layer '{layer.effect_name}': bad shape {frame.shape}"
            )
            assert frame.dtype == np.uint8

    def test_unknown_genre_falls_back_to_default(self):
        """Unknown genre should return default preset, not crash."""
        params = get_preset("nonexistent_genre_xyz", bpm=120)
        assert isinstance(params, RenderParams)
        assert len(params.layers) >= 1

    def test_list_presets_returns_sorted(self):
        result = list_presets()
        assert result == sorted(result)
        assert len(result) == len(PRESETS)


# ===================================================================
# 6. COMPOSITING INTEGRATION
# ===================================================================

class TestCompositing:
    """Test that multi-layer compositing produces expected results."""

    def test_two_layer_composite_shape(self):
        """Compositing two layers should produce valid (H, W, 3) uint8."""
        bottom = np.full((H, W, 3), 50.0, dtype=np.float64)
        top = np.full((H, W, 3), 200.0, dtype=np.float64)
        result = _blend_layers(bottom, top, 0.5, BlendMode.alpha)
        assert result.shape == (H, W, 3)

    def test_additive_glow_effect(self):
        """Plasma base + particles additive should be brighter than plasma alone."""
        plasma_effect = EFFECT_REGISTRY["plasma"]()
        particle_effect = EFFECT_REGISTRY["particles"]()
        params = _base_params()

        plasma_frame = plasma_effect.render_frame(
            0.25, W, H, params, 0.5, _make_rng(1)
        ).astype(np.float64)

        particle_frame = particle_effect.render_frame(
            0.25, W, H, params, 0.5, _make_rng(2)
        ).astype(np.float64)

        composite = _blend_layers(plasma_frame, particle_frame, 0.5, BlendMode.add)
        # Additive: composite >= plasma_frame (adding can only increase or equal)
        assert composite.mean() >= plasma_frame.mean() - 1.0, (
            "Additive composite should be at least as bright as base layer"
        )

    def test_opacity_zero_preserves_base(self):
        """Layer with opacity=0 should not affect the result."""
        base = np.random.default_rng(42).integers(0, 256, (H, W, 3)).astype(np.float64)
        overlay = np.full((H, W, 3), 255.0, dtype=np.float64)
        result = _blend_layers(base, overlay, 0.0, BlendMode.alpha)
        np.testing.assert_array_equal(result, base)


# ===================================================================
# 7. LOOP MATH INVARIANTS
# ===================================================================

class TestLoopMath:
    """Verify loop timing and envelope properties."""

    @pytest.mark.parametrize("bpm", [60, 90, 120, 140, 180, 200])
    def test_loop_duration_in_range(self, bpm):
        """Loop duration must be 8-30 seconds for any valid BPM."""
        total_frames, duration = calculate_loop_params(bpm)
        assert 8.0 <= duration <= 30.0, f"BPM={bpm}: duration={duration:.1f}s out of range"

    @pytest.mark.parametrize("bpm", [60, 120, 180])
    def test_envelope_peaks_at_one(self, bpm):
        """Envelope max should be exactly 1.0."""
        tf, ld = calculate_loop_params(bpm)
        env = build_synthetic_beat_envelope(tf, bpm, FPS, ld)
        assert abs(env.max() - 1.0) < 1e-10

    @pytest.mark.parametrize("bpm", [60, 120, 180])
    def test_envelope_min_above_zero(self, bpm):
        """Envelope min should be >= 0."""
        tf, ld = calculate_loop_params(bpm)
        env = build_synthetic_beat_envelope(tf, bpm, FPS, ld)
        assert env.min() >= 0.0

    def test_envelope_seamless_loop(self):
        """First and last frames should have similar envelope values
        (seamless loop property)."""
        tf, ld = calculate_loop_params(BPM)
        env = build_synthetic_beat_envelope(tf, BPM, FPS, ld)
        # Difference between first and last should be small.
        # At 120 BPM / 30 FPS the last frame is 1 frame from a beat,
        # so decay = 0.85^1 = 0.85 → diff = 0.15. Allow up to one
        # full decay step.
        assert abs(env[0] - env[-1]) <= 1.0 - 0.85 + 1e-9, (
            f"Loop seam: first={env[0]:.3f}, last={env[-1]:.3f}"
        )
