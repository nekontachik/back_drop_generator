"""Integration tests for the FastAPI API layer."""

from __future__ import annotations

import asyncio
import json
import time

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    """Async HTTP client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health(client: httpx.AsyncClient):
    """GET /health returns 200 with status ok."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_returns_job_id(client: httpx.AsyncClient):
    """POST /generate returns a job_id (INP-01)."""
    resp = await client.post(
        "/generate",
        json={"prompt": "dark techno tunnel", "bpm": 120, "width": 480, "height": 270},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    assert len(data["job_id"]) > 0


@pytest.mark.asyncio
async def test_bpm_validation(client: httpx.AsyncClient):
    """BPM must be between 60 and 200 (INP-02)."""
    # Too low
    resp = await client.post(
        "/generate", json={"prompt": "test", "bpm": 59, "width": 480, "height": 270}
    )
    assert resp.status_code == 422

    # Too high
    resp = await client.post(
        "/generate", json={"prompt": "test", "bpm": 201, "width": 480, "height": 270}
    )
    assert resp.status_code == 422

    # Valid
    resp = await client.post(
        "/generate", json={"prompt": "test", "bpm": 120, "width": 480, "height": 270}
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Job status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_status(client: httpx.AsyncClient):
    """GET /jobs/{id} returns valid status."""
    resp = await client.post(
        "/generate",
        json={"prompt": "dark techno", "bpm": 120, "width": 480, "height": 270},
    )
    job_id = resp.json()["job_id"]

    resp = await client.get(f"/jobs/{job_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["pending", "rendering", "complete", "failed"]


@pytest.mark.asyncio
async def test_job_not_found(client: httpx.AsyncClient):
    """GET /jobs/{id} returns 404 for nonexistent job."""
    resp = await client.get("/jobs/nonexistent-id")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# SSE progress streaming
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_sse_progress(client: httpx.AsyncClient):
    """SSE stream delivers progress events until complete (RND-03)."""
    # Start a small render
    resp = await client.post(
        "/generate",
        json={"prompt": "dark techno", "bpm": 120, "width": 480, "height": 270},
    )
    job_id = resp.json()["job_id"]

    # Collect SSE events
    events = []
    async with client.stream("GET", f"/jobs/{job_id}/stream") as stream:
        buffer = ""
        async for chunk in stream.aiter_text():
            buffer += chunk
            # Parse SSE format: lines starting with "data:" and "event:"
            while "\n\n" in buffer:
                block, buffer = buffer.split("\n\n", 1)
                event_data = None
                event_type = None
                for line in block.strip().split("\n"):
                    if line.startswith("data:"):
                        event_data = line[len("data:"):].strip()
                    elif line.startswith("event:"):
                        event_type = line[len("event:"):].strip()
                if event_data:
                    parsed = json.loads(event_data)
                    events.append({"type": event_type, "data": parsed})
                    if parsed.get("status") in ("complete", "failed"):
                        break
            # Check if we got a terminal event
            if events and events[-1]["data"].get("status") in ("complete", "failed"):
                break

    assert len(events) > 0, "Should receive at least one SSE event"
    # At least one event should have progress > 0
    has_progress = any(e["data"].get("progress", 0) > 0 for e in events)
    assert has_progress, "Should have at least one event with progress > 0"
    # Final event should be complete
    assert events[-1]["data"]["status"] == "complete"


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_download_after_render(client: httpx.AsyncClient):
    """Download endpoint serves mp4 after render completes."""
    # Start render
    resp = await client.post(
        "/generate",
        json={"prompt": "dark techno", "bpm": 120, "width": 480, "height": 270},
    )
    job_id = resp.json()["job_id"]

    # Poll until complete
    for _ in range(240):
        resp = await client.get(f"/jobs/{job_id}")
        data = resp.json()
        if data["status"] == "complete":
            break
        if data["status"] == "failed":
            pytest.fail(f"Job failed: {data.get('error')}")
        await asyncio.sleep(0.5)
    else:
        pytest.fail("Job did not complete within timeout")

    # Download
    resp = await client.get(f"/jobs/{job_id}/download")
    assert resp.status_code == 200
    assert "video/mp4" in resp.headers.get("content-type", "")


# ---------------------------------------------------------------------------
# Health during render (non-blocking)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_health_during_render(client: httpx.AsyncClient):
    """Health endpoint responds within 1 second during active render (RND-04)."""
    # Start a full-resolution render to keep the worker busy
    resp = await client.post(
        "/generate",
        json={"prompt": "dark techno", "bpm": 120, "width": 1920, "height": 1080},
    )
    assert resp.status_code == 200

    # Immediately check health -- should not be blocked
    start = time.monotonic()
    resp = await client.get("/health")
    elapsed = time.monotonic() - start

    assert resp.status_code == 200
    assert elapsed < 1.0, f"Health took {elapsed:.2f}s (should be < 1s)"
