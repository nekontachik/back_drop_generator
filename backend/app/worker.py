"""Process-isolated render worker.

Submits render jobs to a ProcessPoolExecutor so that CPU-heavy
rendering does not block the FastAPI event loop (D-14, RND-04).
Uses multiprocessing.Manager for cross-process progress reporting.
"""

from __future__ import annotations

import asyncio
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.managers import DictProxy
from pathlib import Path

from app.models.params import RenderParams

logger = logging.getLogger(__name__)

_executor = ProcessPoolExecutor(max_workers=1)
_manager = multiprocessing.Manager()
_progress_dict: DictProxy = _manager.dict()


def _render_in_process(
    params_dict: dict, output_path: str, progress_dict: DictProxy, job_id: str
) -> str:
    """Execute render in a child process.

    IMPORTANT: This runs in a CHILD process. All imports must happen
    inside the function body to avoid pickling issues.

    Args:
        params_dict: Serialized RenderParams (via model_dump).
        output_path: Destination path for the mp4.
        progress_dict: Manager-backed shared dict for progress reporting.
        job_id: Job identifier used as key in progress_dict.

    Returns:
        The output_path string.
    """
    from app.models.params import RenderParams as _RenderParams
    from app.render.pipeline import render_video

    params = _RenderParams(**params_dict)

    def progress_callback(value: float) -> None:
        progress_dict[job_id] = value

    render_video(params, output_path, progress_callback)
    return output_path


def submit_render(job_id: str, params: RenderParams, output_dir: Path) -> None:
    """Submit a render job to the process pool.

    Stores a progress entry in the shared Manager dict, submits the
    render function to the executor, and sets up a done callback to
    update job status.

    Args:
        job_id: Unique job identifier.
        params: Render parameters.
        output_dir: Directory for output mp4 files.
    """
    _progress_dict[job_id] = 0.0
    output_path = str(output_dir / f"{job_id}.mp4")

    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(
        _executor,
        _render_in_process,
        params.model_dump(),
        output_path,
        _progress_dict,
        job_id,
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
    return _progress_dict.get(job_id, 0.0)


def cleanup_progress(job_id: str) -> None:
    """Remove progress tracking for a completed/failed job."""
    _progress_dict.pop(job_id, None)
