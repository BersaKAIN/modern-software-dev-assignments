"""Tests for creating Notion pages."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from server.tools.notion import NotionClient, NotionAPIError


@pytest.mark.asyncio
async def test_create_page_success(
    notion_client, sample_create_page_response, test_parent_id
):
    """
    Test successfully creating a page.

    Success conditions:
    - Page is created successfully
    - Response contains expected page data
    - Request body is correctly formatted
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_create_page_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await notion_client.create_page(
            parent_id=test_parent_id,
            title="New Test Page",
        )

        assert result == sample_create_page_response
        # Verify the request was made correctly
        call_args = mock_client_instance.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["url"] == "https://api.notion.com/v1/pages"
        request_data = call_args.kwargs["json"]
        assert request_data["parent"]["page_id"] == test_parent_id
        assert request_data["properties"]["title"]["title"][0]["text"]["content"] == "New Test Page"


@pytest.mark.asyncio
async def test_create_page_with_properties(
    notion_client, sample_create_page_response, test_parent_id
):
    """
    Test creating a page with additional properties.

    Success conditions:
    - Page is created with custom properties
    - Properties are included in request body
    """
    custom_properties = {
        "Status": {
            "select": {
                "name": "In Progress",
            }
        }
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_create_page_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await notion_client.create_page(
            parent_id=test_parent_id,
            title="Page with Properties",
            properties=custom_properties,
        )

        assert result == sample_create_page_response
        # Verify properties were included
        call_args = mock_client_instance.request.call_args
        request_data = call_args[1]["json"]
        assert "Status" in request_data["properties"]


@pytest.mark.asyncio
async def test_create_page_retrieve_created_page(
    notion_client, sample_create_page_response, test_parent_id
):
    """
    Test creating a page and then retrieving it.

    Success conditions:
    - Page is created successfully
    - Created page can be retrieved using its ID
    """
    created_page_id = sample_create_page_response["id"]

    with patch("httpx.AsyncClient") as mock_client:
        # Mock create response
        create_response = MagicMock()
        create_response.json.return_value = sample_create_page_response
        create_response.status_code = 200
        create_response.raise_for_status = MagicMock()

        # Mock retrieve response (same page)
        retrieve_response = MagicMock()
        retrieve_response.json.return_value = sample_create_page_response
        retrieve_response.status_code = 200
        retrieve_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        # First call is create, second is retrieve
        mock_client_instance.request = AsyncMock(
            side_effect=[create_response, retrieve_response]
        )
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        # Create page
        created_page = await notion_client.create_page(
            parent_id=test_parent_id,
            title="Test Page",
        )
        assert created_page["id"] == created_page_id

        # Retrieve the created page
        retrieved_page = await notion_client.retrieve_page(created_page_id)
        assert retrieved_page["id"] == created_page_id
        assert retrieved_page == sample_create_page_response


@pytest.mark.asyncio
async def test_create_page_missing_parent_id(notion_client):
    """
    Test creating a page without parent ID.

    Failure conditions:
    - Empty parent ID raises NotionAPIError
    """
    with pytest.raises(NotionAPIError, match="Parent ID is required"):
        await notion_client.create_page(parent_id="", title="Test")

    with pytest.raises(NotionAPIError, match="Parent ID is required"):
        await notion_client.create_page(parent_id="   ", title="Test")


@pytest.mark.asyncio
async def test_create_page_missing_title(notion_client, test_parent_id):
    """
    Test creating a page without title.

    Failure conditions:
    - Empty title raises NotionAPIError
    """
    with pytest.raises(NotionAPIError, match="Title is required"):
        await notion_client.create_page(parent_id=test_parent_id, title="")

    with pytest.raises(NotionAPIError, match="Title is required"):
        await notion_client.create_page(parent_id=test_parent_id, title="   ")


@pytest.mark.asyncio
async def test_create_page_invalid_parent(notion_client, test_parent_id):
    """
    Test creating a page with invalid parent ID.

    Failure conditions:
    - 404 error for invalid parent raises NotionAPIError
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Parent not found"}
        mock_response.text = '{"message": "Parent not found"}'

        error = httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=mock_response,
        )
        mock_response.raise_for_status = MagicMock(side_effect=error)

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        with pytest.raises(NotionAPIError, match="Notion API error.*404"):
            await notion_client.create_page(
                parent_id=test_parent_id,
                title="Test Page",
            )


@pytest.mark.asyncio
async def test_create_page_rate_limit(notion_client, test_parent_id):
    """
    Test handling rate limit error when creating a page.

    Success conditions:
    - Rate limit error triggers retry logic
    - Request is retried after backoff
    """
    with patch("httpx.AsyncClient") as mock_client:
        # First response is 429, second is success
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "1"}
        rate_limit_response.json.return_value = {"message": "Rate limited"}

        success_response = MagicMock()
        success_response.json.return_value = {
            "object": "page",
            "id": "test-id",
            "properties": {"title": {"title": [{"text": {"content": "Test"}}]}},
        }
        success_response.status_code = 200
        success_response.raise_for_status = MagicMock()

        error = httpx.HTTPStatusError(
            "Too Many Requests",
            request=MagicMock(),
            response=rate_limit_response,
        )
        rate_limit_response.raise_for_status = MagicMock(side_effect=error)

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(
            side_effect=[rate_limit_response, success_response]
        )
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        # Mock the rate limiter to handle the 429
        notion_client.rate_limiter.handle_rate_limit_error = AsyncMock()

        result = await notion_client.create_page(
            parent_id=test_parent_id,
            title="Test Page",
        )

        assert result["id"] == "test-id"
        # Verify rate limiter was called
        notion_client.rate_limiter.handle_rate_limit_error.assert_called_once()


@pytest.mark.asyncio
async def test_create_page_timeout(notion_client, test_parent_id):
    """
    Test timeout when creating a page.

    Failure conditions:
    - Timeout exception raises NotionAPIError
    """
    with patch("httpx.AsyncClient") as mock_client:
        timeout_error = httpx.TimeoutException("Request timed out", request=MagicMock())
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(side_effect=timeout_error)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        with pytest.raises(NotionAPIError, match="timed out"):
            await notion_client.create_page(
                parent_id=test_parent_id,
                title="Test Page",
            )

