"""Job state models for render queue tracking."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.models.params import RenderParams


class JobStatus(str, Enum):
    """Render job lifecycle states."""

    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETE = "complete"
    FAILED = "failed"


class JobState(BaseModel):
    """Full state of a render job."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    error: str | None = None
    output_path: str | None = None
    created_at: datetime
    params: RenderParams
