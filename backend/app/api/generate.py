"""Generate and job status endpoints (D-10, D-11, D-17)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.config import settings
from app.models.api import GenerateResponse, JobStatusResponse
from app.models.audio import AudioAnalysis
from app.models.job import JobStatus
from app.services.audio_analyzer import analyze_audio, validate_audio
from app.services.job_manager import create_job, get_job, update_job
from app.services.prompt_mapper import map_prompt_to_params
from app.services.rag_retriever import get_collection, query_styles
from app.worker import get_progress, submit_render

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    prompt: str = Form(...),
    bpm: int = Form(120),
    bpm_override: int | None = Form(None),
    width: int = Form(1920),
    height: int = Form(1080),
    seed: int | None = Form(None),
    audio: UploadFile | None = File(None),
) -> GenerateResponse:
    """Accept a prompt and optional audio file, start rendering, return job_id.

    Maps the text prompt to render parameters, optionally analyzes uploaded
    audio for BPM detection and mood features, queries RAG for matched
    genre styles, creates a job, and submits it to the process pool worker.

    The endpoint uses multipart/form-data to support file upload alongside
    form fields. All parameters are Form() fields; audio is an optional File().
    """
    audio_analysis: AudioAnalysis | None = None

    # Handle optional audio upload
    if audio is not None:
        audio_bytes = await audio.read()
        try:
            validate_audio(audio_bytes, audio.filename)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        try:
            # Run librosa analysis in thread pool to avoid blocking event loop
            audio_analysis = await asyncio.to_thread(analyze_audio, audio_bytes)
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"Audio analysis failed: {exc}"
            )

    # Determine effective BPM (D-09: bpm_override > detected > form default)
    if bpm_override is not None:
        effective_bpm = bpm_override
    elif audio_analysis is not None:
        effective_bpm = audio_analysis.bpm.detected
    else:
        effective_bpm = bpm

    # Validate effective BPM range
    if not (60 <= effective_bpm <= 200):
        raise HTTPException(
            status_code=422,
            detail=f"BPM must be between 60 and 200, got {effective_bpm}",
        )

    # Query RAG for matched genre styles (graceful fallback if not initialized)
    matched_styles: list[dict] | None = None
    try:
        collection = get_collection()
        matched_styles = query_styles(collection, prompt, n_results=3)
    except RuntimeError:
        logger.warning("ChromaDB not initialized, skipping RAG retrieval")

    render_params = map_prompt_to_params(
        prompt,
        effective_bpm,
        width,
        height,
        seed,
    )

    job = create_job(render_params)

    # Ensure render directory exists
    settings.render_dir.mkdir(parents=True, exist_ok=True)

    # Submit to worker and mark as rendering
    submit_render(job.job_id, render_params, settings.render_dir)
    update_job(job.job_id, status=JobStatus.RENDERING)

    return GenerateResponse(
        job_id=job.job_id,
        audio_analysis=audio_analysis,
        matched_styles=matched_styles,
    )


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
