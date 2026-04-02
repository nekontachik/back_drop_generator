"""Generate and job status endpoints (D-10, D-11, D-17)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.config import settings
from app.models.api import GenerateRequest, GenerateResponse, JobStatusResponse
from app.models.job import JobStatus
from app.services.job_manager import get_job, create_job, update_job
from app.services.prompt_mapper import map_prompt_to_params
from app.worker import get_progress, submit_render

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Accept a prompt and BPM, start rendering, return job_id.

    Maps the text prompt to render parameters, creates a job,
    and submits it to the process pool worker.
    """
    render_params = map_prompt_to_params(
        request.prompt,
        request.bpm,
        request.width,
        request.height,
        request.seed,
    )

    job = create_job(render_params)

    # Ensure render directory exists
    settings.render_dir.mkdir(parents=True, exist_ok=True)

    # Submit to worker and mark as rendering
    submit_render(job.job_id, render_params, settings.render_dir)
    update_job(job.job_id, status=JobStatus.RENDERING)

    return GenerateResponse(job_id=job.job_id)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str) -> JobStatusResponse:
    """Get current status of a render job."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update progress from worker's shared counter
    progress = get_progress(job_id) if job.status == JobStatus.RENDERING else job.progress

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=progress,
        error=job.error,
    )


@router.get("/jobs/{job_id}/stream", response_class=EventSourceResponse)
async def job_stream(job_id: str) -> AsyncGenerator[ServerSentEvent]:
    """Stream job progress via Server-Sent Events.

    Yields SSE events with status and progress every 0.5 seconds
    until the job completes or fails.
    """
    job = get_job(job_id)
    if job is None:
        yield ServerSentEvent(
            data={"error": "Job not found"},
            event="error",
        )
        return

    while True:
        job = get_job(job_id)
        if job is None:
            yield ServerSentEvent(
                data={"error": "Job not found"},
                event="error",
            )
            return

        progress = (
            get_progress(job_id)
            if job.status == JobStatus.RENDERING
            else job.progress
        )

        yield ServerSentEvent(
            data={
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": round(progress, 4),
                "error": job.error,
            },
            event="progress",
        )

        if job.status in (JobStatus.COMPLETE, JobStatus.FAILED):
            return

        await asyncio.sleep(0.5)
