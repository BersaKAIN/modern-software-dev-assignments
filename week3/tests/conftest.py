"""Test fixtures for MCP Notion Server tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from server.tools.notion import NotionClient
from server.tools.rate_limiter import RateLimiter


class MockConfig:
    """Mock configuration for testing."""
    NOTION_API_KEY = "test_api_key"
    NOTION_API_BASE_URL = "https://api.notion.com/v1"
    NOTION_API_VERSION = "2022-06-28"
    HTTP_TIMEOUT = 5.0
    RATE_LIMIT_REQUESTS_PER_SECOND = 100.0
    RATE_LIMIT_WARNING_THRESHOLD = 0.8


@pytest.fixture
def mock_rate_limiter():
    """Create a mock rate limiter that doesn't actually limit."""
    limiter = RateLimiter(requests_per_second=100.0)
    # Mock the acquire method to return immediately
    limiter.acquire = AsyncMock(return_value=None)
    limiter.handle_rate_limit_error = AsyncMock()
    return limiter


@pytest.fixture
def notion_client(mock_rate_limiter):
    """Create a NotionClient instance for testing."""
    return NotionClient(
        config=MockConfig,
        rate_limiter=mock_rate_limiter,
    )


@pytest.fixture
def sample_page_response():
    """Sample Notion page response."""
    return {
        "object": "page",
        "id": "12345678-1234-1234-1234-123456789abc",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "Test Page",
                        }
                    }
                ]
            }
        },
    }


@pytest.fixture
def sample_create_page_response():
    """Sample Notion create page response."""
    return {
        "object": "page",
        "id": "87654321-4321-4321-4321-cba987654321",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "New Test Page",
                        }
                    }
                ]
            }
        },
    }


@pytest.fixture
def test_page_id():
    """Test page ID."""
    return "12345678-1234-1234-1234-123456789abc"


@pytest.fixture
def test_parent_id():
    """Test parent page ID."""
    return "parent-1234-1234-1234-123456789abc"
