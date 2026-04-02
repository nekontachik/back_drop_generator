"""Process-isolated render worker.

Submits render jobs to a ProcessPoolExecutor so that CPU-heavy
rendering does not block the FastAPI event loop (D-14, RND-04).
Uses multiprocessing.Value for cross-process progress reporting.
"""

from __future__ import annotations

import asyncio
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from app.models.params import RenderParams

logger = logging.getLogger(__name__)

_executor = ProcessPoolExecutor(max_workers=1)
_progress_values: dict[str, multiprocessing.Value] = {}


def _render_in_process(
    params_dict: dict, output_path: str, progress_value: multiprocessing.Value
) -> str:
    """Execute render in a child process.

    IMPORTANT: This runs in a CHILD process. All imports must happen
    inside the function body to avoid pickling issues.

    Args:
        params_dict: Serialized RenderParams (via model_dump).
        output_path: Destination path for the mp4.
        progress_value: Shared multiprocessing.Value for progress [0.0, 1.0].

    Returns:
        The output_path string.
    """
    from app.models.params import RenderParams as _RenderParams
    from app.render.pipeline import render_video

    params = _RenderParams(**params_dict)

    def progress_callback(value: float) -> None:
        progress_value.value = value

    render_video(params, output_path, progress_callback)
    return output_path


def submit_render(job_id: str, params: RenderParams, output_dir: Path) -> None:
    """Submit a render job to the process pool.

    Creates a shared progress counter, submits the render function to
    the executor, and sets up a done callback to update job status.

    Args:
        job_id: Unique job identifier.
        params: Render parameters.
        output_dir: Directory for output mp4 files.
    """
    progress = multiprocessing.Value("d", 0.0)
    _progress_values[job_id] = progress
    output_path = str(output_dir / f"{job_id}.mp4")

    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(
        _executor,
        _render_in_process,
        params.model_dump(),
        output_path,
        progress,
    )

    def _on_done(fut: asyncio.Future) -> None:
        """Handle render completion or failure."""
        from app.services.job_manager import update_job
        from app.models.job import JobStatus

        try:
            result_path = fut.result()
            update_job(
                job_id,
                status=JobStatus.COMPLETE,
                progress=1.0,
                output_path=result_path,
            )
            logger.info("Job %s completed: %s", job_id, result_path)
        except Exception as exc:
            update_job(
                job_id,
                status=JobStatus.FAILED,
                error=str(exc),
            )
            logger.error("Job %s failed: %s", job_id, exc)
        finally:
            cleanup_progress(job_id)

    future.add_done_callback(lambda fut: loop.call_soon_threadsafe(_on_done, fut))


def get_progress(job_id: str) -> float:
    """Get current progress for a job.

    Returns:
        Progress value between 0.0 and 1.0, or 0.0 if job not tracked.
    """
    pv = _progress_values.get(job_id)
    if pv is not None:
        return pv.value
    return 0.0


def cleanup_progress(job_id: str) -> None:
    """Remove progress tracking for a completed/failed job."""
    _progress_values.pop(job_id, None)
