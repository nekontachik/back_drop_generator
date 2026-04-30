"""Tests for LLM blender service (llm_blender.py).

Covers: deterministic fallback, LLM success path, retry on invalid JSON,
fallback on API error, mood influence in prompt, blend ratio in prompt,
and creative_description in result.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.audio import MoodVector


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

VALID_LLM_JSON = json.dumps(
    {
        "effect_name": "tunnel",
        "bg_color": "#1a0a2e",
        "primary_color": "#ff6600",
        "accent_color": "#00ff88",
        "intensity": 0.75,
        "speed": 0.6,
        "creative_description": "A deep amber tunnel pulsing with neon green flashes",
    }
)

SAMPLE_GENRE_DOCS = [
    {
        "id": "techno-core",
        "document": "Techno: dark, industrial, mechanical rhythms.",
        "metadata": {
            "genre": "techno",
            "colors": ["#0a0a0a", "#00ff88", "#ff0066"],
            "shapes": ["tunnel", "grid"],
            "movement": "fast_forward",
            "intensity": 0.8,
            "speed": 0.7,
            "effect_preference": "tunnel",
        },
        "distance": 0.1,
    },
    {
        "id": "ambient-drift",
        "document": "Ambient: soft, floating, dreamy soundscapes.",
        "metadata": {
            "genre": "ambient",
            "colors": ["#0a0a2e", "#4488ff", "#88ccff"],
            "shapes": ["particles", "clouds"],
            "movement": "slow_drift",
            "intensity": 0.3,
            "speed": 0.2,
            "effect_preference": "particles",
        },
        "distance": 0.3,
    },
]

SAMPLE_MOOD = MoodVector(
    spectral_centroid=3000.0,
    chroma=[0.1] * 12,
    rms=0.15,
    onset_strength=2.5,
    labels=["bright", "energetic", "dense"],
)


def _make_mock_message(content: str) -> MagicMock:
    """Build a mock anthropic Message object with text content."""
    msg = MagicMock()
    text_block = MagicMock()
    text_block.text = content
    msg.content = [text_block]
    return msg


# ---------------------------------------------------------------------------
# Test 1: Deterministic fallback when ANTHROPIC_API_KEY is None
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fallback_when_no_api_key():
    """When anthropic_api_key is None, blend_style returns valid RenderParams
    without calling the LLM."""
    from app.services.llm_blender import blend_style, BlendResult
    from app.models.params import RenderParams

    with patch("app.services.llm_blender.settings") as mock_settings:
        mock_settings.anthropic_api_key = None

        result = await blend_style(
            prompt="dark techno warehouse",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=SAMPLE_MOOD,
            blend_genres=("Techno", "Ambient"),
            blend_ratio=70,
            bpm=128,
        )

    assert isinstance(result, BlendResult)
    assert isinstance(result.params, RenderParams)
    assert result.source == "fallback"
    assert result.creative_description != ""


# ---------------------------------------------------------------------------
# Test 2: LLM success path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_llm_success_path():
    """When API key is set and LLM returns valid JSON, populate RenderParams
    from LLM output."""
    from app.services.llm_blender import blend_style, BlendResult
    from app.models.params import RenderParams

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_message(VALID_LLM_JSON)

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        result = await blend_style(
            prompt="amber tunnel with neon",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=SAMPLE_MOOD,
            blend_genres=("Techno", "Ambient"),
            blend_ratio=70,
            bpm=128,
        )

    assert isinstance(result, BlendResult)
    assert isinstance(result.params, RenderParams)
    assert result.source == "llm"
    assert result.params.effect_name == "tunnel"
    assert result.params.primary_color == "#ff6600"
    assert result.creative_description == "A deep amber tunnel pulsing with neon green flashes"


# ---------------------------------------------------------------------------
# Test 3: LLM returns invalid JSON twice → fallback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_json_retries_then_fallback():
    """When LLM returns garbage JSON twice, fall back to deterministic params."""
    from app.services.llm_blender import blend_style, BlendResult

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_message("not valid json at all")

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        result = await blend_style(
            prompt="dark warehouse",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=140,
        )

    assert isinstance(result, BlendResult)
    assert result.source == "fallback"
    # LLM was called at least twice (initial + retry)
    assert mock_client.messages.create.call_count >= 2


# ---------------------------------------------------------------------------
# Test 4: LLM API error → fallback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_api_error_falls_back():
    """When anthropic raises an APIError, fall back gracefully."""
    import anthropic as anthropic_lib
    from app.services.llm_blender import blend_style, BlendResult

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic_lib.APIError(
        message="rate limit exceeded",
        request=MagicMock(),
        body=None,
    )

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        result = await blend_style(
            prompt="techno industrial",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=130,
        )

    assert isinstance(result, BlendResult)
    assert result.source == "fallback"


# ---------------------------------------------------------------------------
# Test 5: Mood vector labels appear in prompt sent to LLM
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mood_labels_in_prompt():
    """Audio mood semantic labels (bright, energetic, dense) appear in the
    prompt sent to the LLM."""
    from app.services.llm_blender import blend_style

    captured_calls = []
    mock_client = MagicMock()

    def capture_and_return(**kwargs):
        captured_calls.append(kwargs)
        return _make_mock_message(VALID_LLM_JSON)

    mock_client.messages.create.side_effect = capture_and_return

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        await blend_style(
            prompt="bright energy",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=SAMPLE_MOOD,
            blend_genres=None,
            blend_ratio=50,
            bpm=128,
        )

    assert captured_calls, "LLM was not called"
    # Inspect the messages sent to the API
    messages = captured_calls[0]["messages"]
    full_prompt_text = " ".join(
        m["content"] for m in messages if isinstance(m.get("content"), str)
    )
    assert "bright" in full_prompt_text or "energetic" in full_prompt_text or "dense" in full_prompt_text


# ---------------------------------------------------------------------------
# Test 6: Blend ratio percentages appear in prompt
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_blend_ratio_in_prompt():
    """Blend ratio (e.g. '70% Techno' and '30% Ambient') appear in the prompt."""
    from app.services.llm_blender import blend_style

    captured_calls = []
    mock_client = MagicMock()

    def capture_and_return(**kwargs):
        captured_calls.append(kwargs)
        return _make_mock_message(VALID_LLM_JSON)

    mock_client.messages.create.side_effect = capture_and_return

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        await blend_style(
            prompt="techno ambient blend",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=None,
            blend_genres=("Techno", "Ambient"),
            blend_ratio=70,
            bpm=128,
        )

    assert captured_calls, "LLM was not called"
    messages = captured_calls[0]["messages"]
    full_prompt_text = " ".join(
        m["content"] for m in messages if isinstance(m.get("content"), str)
    )
    assert "70" in full_prompt_text
    assert "Techno" in full_prompt_text
    assert "Ambient" in full_prompt_text


# ---------------------------------------------------------------------------
# Test 7: creative_description is returned from LLM response
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_creative_description_returned():
    """BlendResult includes creative_description from LLM output."""
    from app.services.llm_blender import blend_style

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_mock_message(VALID_LLM_JSON)

    with (
        patch("app.services.llm_blender.settings") as mock_settings,
        patch("app.services.llm_blender.anthropic.Anthropic", return_value=mock_client),
    ):
        mock_settings.anthropic_api_key = "sk-ant-test-key"

        result = await blend_style(
            prompt="deep amber tunnel",
            genre_docs=SAMPLE_GENRE_DOCS,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=128,
        )

    assert result.source == "llm"
    assert "amber" in result.creative_description.lower() or len(result.creative_description) > 5


# ---------------------------------------------------------------------------
# Test 8: Fallback uses effect_preference from RAG genre doc
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fallback_uses_effect_preference_from_rag():
    """Deterministic fallback should use effect_preference from the top RAG
    genre doc instead of relying solely on keyword matching."""
    from app.services.llm_blender import blend_style, BlendResult

    # Genre doc says effect_preference = "particles" (ambient)
    ambient_docs = [
        {
            "id": "ambient-drift",
            "genre": "ambient",
            "description": "Ambient: soft, floating, dreamy soundscapes.",
            "colors": ["#0a0a2e", "#4488ff", "#88ccff"],
            "intensity": 0.3,
            "speed": 0.2,
            "effect_preference": "particles",
        },
    ]

    with patch("app.services.llm_blender.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        mock_settings.openrouter_api_key = None

        result = await blend_style(
            prompt="gentle flowing visuals",
            genre_docs=ambient_docs,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=72,
        )

    assert isinstance(result, BlendResult)
    assert result.source == "fallback"
    assert result.params.effect_name == "particles"


# ---------------------------------------------------------------------------
# Test 9: Each genre doc maps to correct effect in fallback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "effect_preference,genre",
    [
        ("tunnel", "techno"),
        ("fractal", "psytrance"),
        ("particles", "ambient"),
        ("plasma", "house"),
    ],
)
async def test_fallback_effect_per_genre(effect_preference, genre):
    """Each genre's effect_preference should be applied in fallback mode."""
    from app.services.llm_blender import blend_style

    docs = [
        {
            "id": f"{genre}-test",
            "genre": genre,
            "description": f"{genre} style document",
            "colors": ["#0a0a0a", "#00ff88", "#ff0066"],
            "intensity": 0.5,
            "speed": 0.5,
            "effect_preference": effect_preference,
        },
    ]

    with patch("app.services.llm_blender.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        mock_settings.openrouter_api_key = None

        result = await blend_style(
            prompt="some generic visual prompt",
            genre_docs=docs,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=120,
        )

    assert result.params.effect_name == effect_preference, (
        f"Expected effect '{effect_preference}' for genre '{genre}', "
        f"got '{result.params.effect_name}'"
    )


# ---------------------------------------------------------------------------
# Test 10: Invalid effect_preference is ignored
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fallback_ignores_invalid_effect_preference():
    """If effect_preference is not in VALID_EFFECTS, fall back to keyword
    matching instead of using the invalid value."""
    from app.services.llm_blender import blend_style

    docs = [
        {
            "id": "bad-effect",
            "genre": "techno",
            "description": "Techno style",
            "colors": ["#0a0a0a", "#00ff88", "#ff0066"],
            "intensity": 0.7,
            "speed": 0.7,
            "effect_preference": "nonexistent_effect",
        },
    ]

    with patch("app.services.llm_blender.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        mock_settings.openrouter_api_key = None

        result = await blend_style(
            prompt="dark techno warehouse",
            genre_docs=docs,
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=138,
        )

    # Should NOT be "nonexistent_effect"
    assert result.params.effect_name in ["tunnel", "fractal", "particles", "plasma"]
    assert result.params.effect_name != "nonexistent_effect"


# ---------------------------------------------------------------------------
# Test 11: Empty genre_docs falls back to keyword matching
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fallback_no_genre_docs():
    """When genre_docs is empty, fall back to keyword matching from prompt."""
    from app.services.llm_blender import blend_style

    with patch("app.services.llm_blender.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        mock_settings.openrouter_api_key = None

        result = await blend_style(
            prompt="dark techno warehouse",
            genre_docs=[],
            mood=None,
            blend_genres=None,
            blend_ratio=50,
            bpm=138,
        )

    assert result.source == "fallback"
    # "techno" keyword should match to tunnel via prompt_mapper
    assert result.params.effect_name == "tunnel"
