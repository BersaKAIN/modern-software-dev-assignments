from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration settings."""

    # Database configuration
    db_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "data" / "app.db",
        description="Path to the SQLite database file",
    )

    # Frontend configuration
    frontend_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "frontend",
        description="Directory containing frontend files",
    )

    # Application configuration
    app_title: str = Field(default="Action Item Extractor", description="Application title")
    app_debug: bool = Field(default=False, description="Debug mode")

    @classmethod
    def from_env(cls) -> Settings:
        """Create settings from environment variables."""
        base_dir = Path(__file__).resolve().parents[1]
        return cls(
            db_path=Path(os.getenv("DB_PATH", str(base_dir / "data" / "app.db"))),
            frontend_dir=Path(os.getenv("FRONTEND_DIR", str(base_dir / "frontend"))),
            app_title=os.getenv("APP_TITLE", "Action Item Extractor"),
            app_debug=os.getenv("APP_DEBUG", "false").lower() == "true",
        )


# Global settings instance
settings = Settings.from_env()

