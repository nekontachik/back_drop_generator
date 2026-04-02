"""TTL-based render file cleanup (D-18).

Scans the render directory for old mp4 files and deletes them.
Runs as a background loop during application lifespan.
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


async def cleanup_old_renders(
    render_dir: Path, ttl_seconds: int = 3600
) -> int:
    """Delete rendered mp4 files older than the TTL.

    Args:
        render_dir: Directory containing rendered mp4 files.
        ttl_seconds: Maximum age in seconds before deletion.

    Returns:
        Number of files deleted.
    """
    if not render_dir.exists():
        return 0

    now = time.time()
    deleted = 0

    for mp4_file in render_dir.glob("*.mp4"):
        try:
            age = now - mp4_file.stat().st_mtime
            if age > ttl_seconds:
                mp4_file.unlink()
                deleted += 1
                logger.info("Cleaned up old render: %s (age: %.0fs)", mp4_file.name, age)
        except OSError as exc:
            logger.warning("Failed to clean up %s: %s", mp4_file.name, exc)

    return deleted


async def start_cleanup_loop(
    render_dir: Path, ttl_seconds: int = 3600, interval: int = 300
) -> None:
    """Run cleanup on a recurring schedule.

    Args:
        render_dir: Directory containing rendered mp4 files.
        ttl_seconds: Maximum age in seconds before deletion.
        interval: Seconds between cleanup runs.
    """
    while True:
        await asyncio.sleep(interval)
        deleted = await cleanup_old_renders(render_dir, ttl_seconds)
        if deleted > 0:
            logger.info("Cleanup cycle removed %d file(s)", deleted)
