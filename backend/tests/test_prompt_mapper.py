"""Tests for keyword-based prompt mapper."""

import re

from app.models.params import RenderParams
from app.services.prompt_mapper import map_prompt_to_params


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class TestPromptMapper:
    """Tests for map_prompt_to_params."""

    def test_tunnel_keywords(self):
        """'dark industrial tunnel' maps to tunnel effect."""
        params = map_prompt_to_params("dark industrial tunnel")
        assert params.effect_name == "tunnel"

    def test_fractal_keywords(self):
        """'psychedelic fractal trippy' maps to fractal effect."""
        params = map_prompt_to_params("psychedelic fractal trippy")
        assert params.effect_name == "fractal"

    def test_particles_keywords(self):
        """'floating particles ambient' maps to particles effect."""
        params = map_prompt_to_params("floating particles ambient")
        assert params.effect_name == "particles"

    def test_plasma_keywords(self):
        """'wavy plasma colorful' maps to plasma effect (via house genre)."""
        params = map_prompt_to_params("wavy plasma groovy funky")
        assert params.effect_name == "plasma"

    def test_fallback_to_tunnel(self):
        """Unknown words fall back to tunnel (D-08)."""
        params = map_prompt_to_params("random nonsense words")
        assert params.effect_name == "tunnel"

    def test_returns_render_params(self):
        """Return type is RenderParams."""
        params = map_prompt_to_params("dark techno")
        assert isinstance(params, RenderParams)

    def test_hex_colors(self):
        """Returned params have valid hex color strings."""
        params = map_prompt_to_params("dark techno")
        assert HEX_COLOR_RE.match(params.primary_color)
        assert HEX_COLOR_RE.match(params.bg_color)
        assert HEX_COLOR_RE.match(params.accent_color)

    def test_bpm_passthrough(self):
        """BPM parameter is passed through to RenderParams."""
        params = map_prompt_to_params("dark techno", bpm=140)
        assert params.bpm == 140

    def test_seed_passthrough(self):
        """Seed parameter is passed through to RenderParams."""
        params = map_prompt_to_params("dark techno", seed=42)
        assert params.seed == 42

    def test_default_seed_generated(self):
        """When no seed provided, a random seed is assigned."""
        params = map_prompt_to_params("dark techno")
        assert isinstance(params.seed, int)
