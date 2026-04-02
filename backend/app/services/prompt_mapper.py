"""Keyword-based prompt mapper (D-07, D-08, D-09).

Maps a text prompt to effect selection and color palette via keyword
cluster matching. Fallback to tunnel with neutral palette when no
keywords match.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.params import RenderParams


@dataclass(frozen=True)
class GenreProfile:
    """A genre's keyword cluster, default effect, and color palette."""

    keywords: list[str]
    effect: str
    bg_color: str
    primary_color: str
    accent_color: str


# Five genre keyword clusters (D-09)
GENRE_PROFILES: dict[str, GenreProfile] = {
    "techno": GenreProfile(
        keywords=["techno", "dark", "industrial", "mechanical", "hard", "rave"],
        effect="tunnel",
        bg_color="#0a0a0a",
        primary_color="#00ff88",
        accent_color="#ff0066",
    ),
    "house": GenreProfile(
        keywords=["house", "groovy", "funky", "deep", "warm", "soulful"],
        effect="plasma",
        bg_color="#1a0a2e",
        primary_color="#ff6600",
        accent_color="#ffcc00",
    ),
    "ambient": GenreProfile(
        keywords=["ambient", "floating", "dreamy", "calm", "ethereal", "soft"],
        effect="particles",
        bg_color="#0a0a2e",
        primary_color="#4488ff",
        accent_color="#88ccff",
    ),
    "industrial": GenreProfile(
        keywords=["industrial", "harsh", "noise", "distorted", "raw", "gritty"],
        effect="tunnel",
        bg_color="#0a0a0a",
        primary_color="#ff2200",
        accent_color="#ffaa00",
    ),
    "psytrance": GenreProfile(
        keywords=["psychedelic", "trippy", "psy", "fractal", "complex", "acid"],
        effect="fractal",
        bg_color="#0a002e",
        primary_color="#ff00ff",
        accent_color="#00ffff",
    ),
}

# Default fallback (D-08): tunnel with neutral palette
_FALLBACK_EFFECT = "tunnel"
_FALLBACK_COLORS = ("#0a0a0a", "#00ff88", "#ff0066")


def map_prompt_to_params(
    prompt: str,
    bpm: int = 120,
    width: int = 1920,
    height: int = 1080,
    seed: int | None = None,
) -> RenderParams:
    """Map a text prompt to RenderParams via keyword cluster matching.

    Lowercase the prompt, split into words, count keyword matches per
    genre, and pick the highest-scoring genre. If no matches, fall back
    to tunnel with neutral palette (D-08).

    Args:
        prompt: User's text prompt describing desired visual style.
        bpm: Beats per minute (default 120).
        width: Video width in pixels.
        height: Video height in pixels.
        seed: Random seed for reproducibility (None = auto-generate).

    Returns:
        A populated RenderParams instance.
    """
    words = prompt.lower().split()

    # Score each genre by keyword matches
    best_genre: str | None = None
    best_score = 0

    for genre_name, profile in GENRE_PROFILES.items():
        score = sum(1 for word in words if word in profile.keywords)
        if score > best_score:
            best_score = score
            best_genre = genre_name

    # Build params from matched genre or fallback
    if best_genre is not None and best_score > 0:
        profile = GENRE_PROFILES[best_genre]
        effect_name = profile.effect
        bg_color = profile.bg_color
        primary_color = profile.primary_color
        accent_color = profile.accent_color
    else:
        effect_name = _FALLBACK_EFFECT
        bg_color, primary_color, accent_color = _FALLBACK_COLORS

    kwargs: dict = {
        "effect_name": effect_name,
        "bg_color": bg_color,
        "primary_color": primary_color,
        "accent_color": accent_color,
        "bpm": bpm,
        "width": width,
        "height": height,
    }

    if seed is not None:
        kwargs["seed"] = seed

    return RenderParams(**kwargs)
