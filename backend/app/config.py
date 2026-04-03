"""Application configuration via Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    render_dir: Path = Path("data/renders")
    chroma_persist_dir: Path = Path("data/chroma")
    render_ttl_seconds: int = 3600
    max_workers: int = 1
    default_width: int = 1920
    default_height: int = 1080
    default_fps: int = 30
    anthropic_api_key: str | None = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
