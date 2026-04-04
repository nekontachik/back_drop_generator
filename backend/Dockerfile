# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system deps needed for building (gcc for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Install runtime system dependencies: ffmpeg for video encoding, libsndfile for soundfile/librosa
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Put venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY app/ app/
COPY data/ data/

# Create renders directory
RUN mkdir -p data/renders

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
