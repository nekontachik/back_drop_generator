"""In-memory job state management.

Provides create/get/update/list operations for render jobs.
Stores all state in a module-level dict (single-instance deployment).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.job import JobState, JobStatus
from app.models.params import RenderParams

_jobs: dict[str, JobState] = {}


def create_job(params: RenderParams) -> JobState:
    """Create a new job with PENDING status.

    Args:
        params: Render parameters for this job.

    Returns:
        The newly created JobState.
    """
    job_id = str(uuid4())
    job = JobState(
        job_id=job_id,
        status=JobStatus.PENDING,
        progress=0.0,
        created_at=datetime.now(timezone.utc),
        params=params,
    )
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> JobState | None:
    """Get a job by ID, or None if not found."""
    return _jobs.get(job_id)


def update_job(job_id: str, **kwargs: object) -> JobState | None:
    """Update fields on an existing job.

    Args:
        job_id: The job to update.
        **kwargs: Fields to update (status, progress, error, output_path).

    Returns:
        The updated JobState, or None if job not found.
    """
    job = _jobs.get(job_id)
    if job is None:
        return None

    # Build updated model with new field values
    updated = job.model_copy(update=kwargs)
    _jobs[job_id] = updated
    return updated


def list_jobs() -> list[JobState]:
    """Return all jobs."""
    return list(_jobs.values())
