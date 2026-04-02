"""Download endpoint for completed renders (D-10, D-12)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.job import JobStatus
from app.services.job_manager import get_job

router = APIRouter()


@router.get("/jobs/{job_id}/download")
async def download(job_id: str) -> FileResponse:
    """Download the rendered mp4 for a completed job.

    Returns 404 if job not found, not complete, or file missing.
    """
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(
            status_code=404, detail=f"Job not complete (status: {job.status.value})"
        )

    if job.output_path is None or not Path(job.output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        job.output_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
    )
