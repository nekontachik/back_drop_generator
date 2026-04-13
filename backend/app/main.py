"""FastAPI application entry point.

Wires together CORS, lifespan, and all route modules.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import download, generate, health, styles
from app.config import settings
from app.services.cleanup import start_cleanup_loop
from app.services.genre_seeder import init_genre_collection
from app.services.rag_retriever import set_collection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: startup and shutdown hooks."""
    # Startup: ensure render directory exists
    settings.render_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Render directory: %s", settings.render_dir.resolve())

    # Seed ChromaDB genre collection (D-07)
    collection = init_genre_collection(str(settings.chroma_persist_dir))
    set_collection(collection)
    logger.info("ChromaDB seeded: %d genre documents", collection.count())

    # Start background cleanup loop
    cleanup_task = asyncio.create_task(
        start_cleanup_loop(
            settings.render_dir,
            ttl_seconds=settings.render_ttl_seconds,
        )
    )

    yield

    # Shutdown: cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Beat Visuals API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: allow all origins for portfolio/demo deployment
# SSE streams require allow_origins=["*"] to work correctly across all browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(health.router)
app.include_router(generate.router)
app.include_router(download.router)
app.include_router(styles.router)
