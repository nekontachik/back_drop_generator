"""Application configuration via Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    render_dir: Path = Path("data/renders")
    chroma_persist_dir: Path = Path("data/chroma")
    render_ttl_seconds: int = 3600
    max_workers: int = 1
    default_width: int = 1280
    default_height: int = 720
    default_fps: int = 30
    anthropic_api_key: str | None = None

    # OpenRouter API key (preferred over direct Anthropic key)
    openrouter_api_key: str | None = None

    # Demo mode: skip actual rendering, return pre-generated example videos instantly
    # Set DEMO_MODE=false to enable real rendering (requires more RAM)
    demo_mode: bool = True
    frontend_url: str = "https://backdropgenerator.vercel.app"

    # CORS origins: set CORS_ORIGINS='["https://your-app.vercel.app"]' in production
    cors_origins: list[str] = ["http://localhost:3000"]

    # Server port
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
