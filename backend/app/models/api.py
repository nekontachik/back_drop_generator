"""API request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.audio import AudioAnalysis


class GenerateRequest(BaseModel):
    """Request body for POST /generate.

    NOTE: This model is kept for documentation/reference but is no longer
    used as the endpoint parameter directly. The POST /generate endpoint
    uses individual Form() + File() parameters for multipart/form-data support.
    """

    prompt: str
    bpm: int = Field(default=120, ge=60, le=200)
    width: int = 1920
    height: int = 1080
    seed: int | None = None


class GenerateResponse(BaseModel):
    """Response body for POST /generate."""

    job_id: str
    audio_analysis: AudioAnalysis | None = None
    matched_styles: list[dict] | None = None


class JobStatusResponse(BaseModel):
    """Response body for GET /jobs/{id}."""

    job_id: str
    status: str
    progress: float
    error: str | None = None
