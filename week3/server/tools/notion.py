"""Notion API client wrapper."""

import logging
import uuid
from typing import Any, Optional, Type, TYPE_CHECKING

import httpx

from server.tools.rate_limiter import RateLimiter

if TYPE_CHECKING:
    from server.config import Config

logger = logging.getLogger(__name__)


class NotionAPIError(Exception):
    """Base exception for Notion API errors."""

    pass


class NotionClient:
    """Client for interacting with the Notion API."""

    def __init__(
        self,
        config: Type["Config"],
        rate_limiter: Optional[RateLimiter] = None,
    ):
        """
        Initialize Notion client.

        Args:
            config: Configuration class
            rate_limiter: Optional rate limiter instance
        """
        self.config = config
        self.api_key = config.NOTION_API_KEY
        self.base_url = config.NOTION_API_BASE_URL
        self.timeout = config.HTTP_TIMEOUT
        
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=config.RATE_LIMIT_REQUESTS_PER_SECOND,
            warning_threshold=config.RATE_LIMIT_WARNING_THRESHOLD,
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": config.NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Notion API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/pages")
            data: Optional request body data

        Returns:
            JSON response data

        Raises:
            NotionAPIError: For API errors, network failures, or timeouts
        """
        url = f"{self.base_url}{endpoint}"

        # Acquire rate limit token
        warning = await self.rate_limiter.acquire()
        if warning:
            logger.warning(warning)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = float(retry_after) if retry_after else None
                    await self.rate_limiter.handle_rate_limit_error(retry_seconds)
                    # Retry the request once
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self.headers,
                        json=data,
                    )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as e:
            raise NotionAPIError(
                f"Request to Notion API timed out after {self.timeout}s: {str(e)}"
            ) from e
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("message", str(e))
            except Exception:
                error_detail = e.response.text or str(e)

            raise NotionAPIError(
                f"Notion API error ({e.response.status_code}): {error_detail}"
            ) from e
        except httpx.RequestError as e:
            raise NotionAPIError(
                f"Network error connecting to Notion API: {str(e)}"
            ) from e
        except Exception as e:
            raise NotionAPIError(f"Unexpected error: {str(e)}") from e

    async def retrieve_page(self, page_id: str) -> dict[str, Any]:
        """
        Retrieve a Notion page by ID.

        Args:
            page_id: The ID of the page to retrieve

        Returns:
            Page object with properties, content, and metadata

        Raises:
            NotionAPIError: If the page cannot be retrieved
        """
        if not page_id or not page_id.strip():
            raise NotionAPIError("Page ID is required and cannot be empty")

        # Canonicalize page ID to standard dashed UUID
        try:
            page_id = str(uuid.UUID(page_id))
        except ValueError:
            # If not a valid UUID, pass it through (Notion might return a better error, or it's a legacy ID)
            pass

        try:
            result = await self._make_request("GET", f"/pages/{page_id}")
            if not result:
                raise NotionAPIError("Received empty response from Notion API")
            return result
        except NotionAPIError:
            raise
        except Exception as e:
            raise NotionAPIError(f"Failed to retrieve page {page_id}: {str(e)}") from e

    async def create_page(
        self,
        parent_id: str,
        title: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Create a new Notion page.

        Args:
            parent_id: The ID of the parent page or database
            title: The title of the new page
            properties: Optional additional page properties

        Returns:
            Created page object with ID

        Raises:
            NotionAPIError: If the page cannot be created
        """
        if not parent_id or not parent_id.strip():
            raise NotionAPIError("Parent ID is required and cannot be empty")
        if not title or not title.strip():
            raise NotionAPIError("Title is required and cannot be empty")

        # Canonicalize parent ID to standard dashed UUID
        try:
            parent_id = str(uuid.UUID(parent_id))
        except ValueError:
            pass

        # Build request body
        request_data: dict[str, Any] = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title,
                            }
                        }
                    ]
                }
            },
        }

        # Add additional properties if provided
        if properties:
            request_data["properties"].update(properties)

        try:
            result = await self._make_request("POST", "/pages", data=request_data)
            if not result:
                raise NotionAPIError("Received empty response from Notion API")
            return result
        except NotionAPIError:
            raise
        except Exception as e:
            raise NotionAPIError(
                f"Failed to create page with title '{title}': {str(e)}"
            ) from e
