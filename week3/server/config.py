"""Configuration management for the MCP Notion Server."""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration for Notion API integration."""

    # Notion API configuration
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
    NOTION_API_BASE_URL: str = "https://api.notion.com/v1"
    NOTION_API_VERSION: str = "2022-06-28"

    # HTTP client configuration
    HTTP_TIMEOUT: float = 30.0  # seconds
    HTTP_MAX_RETRIES: int = 3

    # Rate limiting configuration
    RATE_LIMIT_REQUESTS_PER_SECOND: float = 3.0
    RATE_LIMIT_WARNING_THRESHOLD: float = 0.8  # Warn at 80% of limit

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        if not cls.NOTION_API_KEY:
            raise ValueError(
                "NOTION_API_KEY environment variable is required. "
                "Please set it in your environment or .env file."
            )

    @classmethod
    def get_headers(cls) -> dict[str, str]:
        """Get HTTP headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {cls.NOTION_API_KEY}",
            "Notion-Version": cls.NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

