"""API request/response models."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.audio import AudioAnalysis


class GenerateResponse(BaseModel):
    """Response body for POST /generate."""

    job_id: str
    audio_analysis: AudioAnalysis | None = None
    matched_styles: list[dict] | None = None
    creative_description: str | None = None  # LLM's visual description (D-07)
    blend_source: str | None = None  # "llm" or "fallback"


class JobStatusResponse(BaseModel):
    """Response body for GET /jobs/{id}."""

    job_id: str
    status: str
    progress: float
    error: str | None = None
