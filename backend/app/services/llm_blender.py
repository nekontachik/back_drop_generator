"""LLM style blending service for creative parameter generation.

Uses Claude 3.5 Haiku to creatively blend RAG-retrieved genre documents,
audio mood vectors, and user text prompts into validated RenderParams.
Falls back to deterministic keyword matching when LLM is unavailable.
"""

from __future__ import annotations

import json
import logging

from app.config import settings
from app.models.audio import MoodVector
from app.models.params import RenderParams
from app.services.prompt_mapper import map_prompt_to_params

logger = logging.getLogger(__name__)

# Valid effect names from EFFECT_REGISTRY
VALID_EFFECTS = ["tunnel", "fractal", "particles", "plasma"]

# Model to use — OpenRouter uses "anthropic/claude-3-5-haiku" format
_OPENROUTER_MODEL = "anthropic/claude-3-5-haiku"
_ANTHROPIC_MODEL = "claude-3-5-haiku-latest"
_MAX_TOKENS = 1024
_TEMPERATURE = 0.8
_TIMEOUT = 30.0


class BlendResult:
    """Result of the LLM (or fallback) style blending operation.

    Attributes:
        params: Validated RenderParams ready for the renderer.
        creative_description: 1-2 sentence human-readable description of the
            envisioned visual. Empty string when LLM is unavailable.
        source: Either "llm" (LLM produced the params) or "fallback"
            (deterministic fallback was used).
    """

    def __init__(
        self,
        params: RenderParams,
        creative_description: str,
        source: str,
    ) -> None:
        self.params = params
        self.creative_description = creative_description
        self.source = source

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"BlendResult(source={self.source!r}, "
            f"effect={self.params.effect_name!r}, "
            f"description={self.creative_description[:40]!r})"
        )


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def _build_prompt(
    prompt: str,
    genre_docs: list[dict],
    mood: MoodVector | None,
    blend_genres: tuple[str, str] | None,
    blend_ratio: int,
    bpm: int,
) -> tuple[str, str]:
    """Build the system and user prompts for the LLM blending call.

    Args:
        prompt: User's text description of the desired visual.
        genre_docs: RAG-retrieved genre documents (list of dicts with
            id, document, metadata, distance fields).
        mood: Optional audio mood vector from librosa analysis.
        blend_genres: Optional pair of genre names to blend ("Techno", "Ambient").
        blend_ratio: Percentage (0-100) for the first genre in blend_genres.
        bpm: Beats per minute from audio analysis or user input.

    Returns:
        Tuple of (system_prompt, user_prompt) strings.
    """
    system_prompt = (
        "You are a creative visual designer for music backdrops. "
        "Output ONLY valid JSON matching the schema provided. "
        "No markdown, no explanation, no code blocks — raw JSON only."
    )

    # Build genre docs section
    docs_section = ""
    for i, doc in enumerate(genre_docs, 1):
        docs_section += f"\nGenre Document {i}:\n"
        docs_section += f"  Genre: {doc.get('genre', 'unknown')}\n"
        docs_section += f"  Description: {doc.get('description', '')}\n"
        colors = doc.get("colors", [])
        if colors:
            docs_section += f"  Colors: {', '.join(colors)}\n"
        docs_section += f"  Intensity: {doc.get('intensity', 0.5)}\n"
        docs_section += f"  Speed: {doc.get('speed', 0.5)}\n"
        docs_section += f"  Effect preference: {doc.get('effect_preference', 'tunnel')}\n"

    # Blend instruction
    if blend_genres and len(blend_genres) == 2:
        genre_a, genre_b = blend_genres
        ratio_b = 100 - blend_ratio
        blend_section = (
            f"\nBlend instruction: {blend_ratio}% {genre_a} + {ratio_b}% {genre_b}. "
            f"Interpolate creatively between the genre documents. "
            f"Do NOT just copy one genre's values. "
            f"Blend colors, intensity, speed based on the ratio and mood.\n"
        )
    else:
        blend_section = (
            "\nBlend instruction: Creatively interpret the genre documents "
            "and user prompt to generate a unique visual style.\n"
        )

    # Audio mood section
    if mood is not None:
        mood_labels = ", ".join(mood.labels) if mood.labels else "neutral"
        mood_section = (
            f"\nAudio mood:\n"
            f"  Mood labels: {mood_labels}\n"
            f"  Spectral centroid (brightness): {mood.spectral_centroid:.1f} Hz\n"
            f"  RMS energy (loudness): {mood.rms:.4f}\n"
            f"  Onset strength (rhythmic density): {mood.onset_strength:.2f}\n"
            f"  BPM: {bpm}\n"
        )
    else:
        mood_section = f"\nAudio mood: Not available. BPM: {bpm}\n"

    # JSON schema
    schema_section = """
Output JSON schema (all fields required):
{
  "effect_name": "<one of: tunnel, fractal, particles, plasma>",
  "bg_color": "<hex color string, e.g. #0a0a0a>",
  "primary_color": "<hex color string>",
  "accent_color": "<hex color string>",
  "intensity": <float 0.0 to 1.0>,
  "speed": <float 0.0 to 1.0>,
  "creative_description": "<1-2 sentences describing the visual>"
}
"""

    user_prompt = (
        f"User's visual prompt: {prompt}\n"
        f"\nRetrieved genre style documents:{docs_section}"
        f"{blend_section}"
        f"{mood_section}"
        f"\nAvailable effects: {VALID_EFFECTS}"
        f"{schema_section}"
    )

    return system_prompt, user_prompt


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def blend_style(
    prompt: str,
    genre_docs: list[dict],
    mood: MoodVector | None,
    blend_genres: tuple[str, str] | None,
    blend_ratio: int,
    bpm: int,
    width: int = 1920,
    height: int = 1080,
    seed: int | None = None,
) -> BlendResult:
    """Blend style parameters using Claude LLM with deterministic fallback.

    Args:
        prompt: User's text description of the desired visual.
        genre_docs: RAG-retrieved genre documents.
        mood: Optional audio mood vector from librosa analysis.
        blend_genres: Optional pair of genre names ("Techno", "Ambient").
        blend_ratio: Percentage (0-100) for the first genre.
        bpm: Beats per minute.
        width: Video width in pixels.
        height: Video height in pixels.
        seed: Random seed for reproducibility.

    Returns:
        BlendResult with validated RenderParams, creative description, and source.
    """
    logger.info("LLM blend requested for prompt: %s", prompt[:50])

    # Determine which API key to use (OpenRouter takes priority)
    api_key = settings.openrouter_api_key or settings.anthropic_api_key
    if not api_key:
        logger.info("Using deterministic fallback (no API key configured)")
        return _deterministic_fallback(
            prompt=prompt,
            genre_docs=genre_docs,
            bpm=bpm,
            width=width,
            height=height,
            seed=seed,
        )

    system_prompt, user_prompt = _build_prompt(
        prompt=prompt,
        genre_docs=genre_docs,
        mood=mood,
        blend_genres=blend_genres,
        blend_ratio=blend_ratio,
        bpm=bpm,
    )

    # Use OpenAI-compatible client (works for both OpenRouter and Anthropic via openai SDK)
    try:
        from openai import OpenAI

        if settings.openrouter_api_key:
            client = OpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                timeout=_TIMEOUT,
            )
            model = _OPENROUTER_MODEL
        else:
            # Direct Anthropic via openai-compatible endpoint
            client = OpenAI(
                api_key=settings.anthropic_api_key,
                base_url="https://api.anthropic.com/v1",
                timeout=_TIMEOUT,
            )
            model = _ANTHROPIC_MODEL

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            max_tokens=_MAX_TOKENS,
            temperature=_TEMPERATURE,
            messages=messages,
        )
        result = _parse_openai_response(response, bpm=bpm, width=width, height=height, seed=seed)
        if result is not None:
            logger.info("LLM blend successful, effect=%s", result.params.effect_name)
            return result

        logger.error("LLM blend failed, falling back", exc_info=False)

    except Exception as exc:
        logger.error("LLM API error: %s, falling back", exc)

    # All paths failed — deterministic fallback
    return _deterministic_fallback(
        prompt=prompt,
        genre_docs=genre_docs,
        bpm=bpm,
        width=width,
        height=height,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def _parse_openai_response(
    response,
    *,
    bpm: int,
    width: int,
    height: int,
    seed: int | None,
) -> BlendResult | None:
    """Parse an OpenAI-compatible chat completion into a BlendResult."""
    try:
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(
                line for line in lines if not line.startswith("```")
            ).strip()
        data = json.loads(text)
    except (json.JSONDecodeError, IndexError, AttributeError):
        return None

    try:
        creative_description: str = data.pop("creative_description", "")
        effect_name: str = data.get("effect_name", "tunnel")
        if effect_name not in VALID_EFFECTS:
            return None

        params = RenderParams(
            effect_name=effect_name,
            bg_color=data.get("bg_color", "#0a0a0a"),
            primary_color=data.get("primary_color", "#00ff88"),
            accent_color=data.get("accent_color", "#ff0066"),
            intensity=float(data.get("intensity", 0.7)),
            speed=float(data.get("speed", 0.5)),
            bpm=bpm,
            width=width,
            height=height,
            **({} if seed is None else {"seed": seed}),
        )
        return BlendResult(
            params=params,
            creative_description=creative_description,
            source="llm",
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Deterministic fallback
# ---------------------------------------------------------------------------


def _deterministic_fallback(
    prompt: str,
    genre_docs: list[dict],
    bpm: int,
    width: int,
    height: int,
    seed: int | None,
) -> BlendResult:
    """Produce RenderParams via keyword matching when LLM is unavailable (D-10).

    Uses map_prompt_to_params() as the base, then overrides colors,
    intensity, and speed from the top genre doc's metadata when available.

    Args:
        prompt: User's text prompt.
        genre_docs: RAG-retrieved genre documents (may be empty).
        bpm: Beats per minute.
        width: Video width in pixels.
        height: Video height in pixels.
        seed: Random seed.

    Returns:
        BlendResult with source="fallback".
    """
    params = map_prompt_to_params(
        prompt=prompt,
        bpm=bpm,
        width=width,
        height=height,
        seed=seed,
    )

    # Override colors/intensity/speed from top genre doc when available
    if genre_docs:
        top_doc = genre_docs[0]
        colors = top_doc.get("colors", [])
        if len(colors) >= 3:
            params = params.model_copy(
                update={
                    "bg_color": colors[0],
                    "primary_color": colors[1],
                    "accent_color": colors[2],
                    "intensity": float(top_doc.get("intensity", params.intensity)),
                    "speed": float(top_doc.get("speed", params.speed)),
                }
            )
        elif len(colors) == 2:
            params = params.model_copy(
                update={
                    "primary_color": colors[0],
                    "accent_color": colors[1],
                }
            )

    return BlendResult(
        params=params,
        creative_description="Generated using style matching (LLM unavailable)",
        source="fallback",
    )
