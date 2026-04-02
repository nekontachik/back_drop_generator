"""Shared pytest fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def render_output_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for render output."""
    out = tmp_path / "renders"
    out.mkdir()
    return out
