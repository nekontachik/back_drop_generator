"""API request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request body for POST /generate."""

    prompt: str
    bpm: int = Field(default=120, ge=60, le=200)
    width: int = 1920
    height: int = 1080
    seed: int | None = None


class GenerateResponse(BaseModel):
    """Response body for POST /generate."""

    job_id: str


class JobStatusResponse(BaseModel):
    """Response body for GET /jobs/{id}."""

    job_id: str
    status: str
    progress: float
    error: str | None = None
