"""Tests for retrieving Notion pages."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from server.tools.notion import NotionClient, NotionAPIError


@pytest.mark.asyncio
async def test_retrieve_page_success(notion_client, sample_page_response, test_page_id):
    """
    Test successfully retrieving a page by ID.

    Success conditions:
    - Page is retrieved successfully
    - Response contains expected page data
    - Page ID is correctly formatted (dashes removed)
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_page_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await notion_client.retrieve_page(test_page_id)

        assert result == sample_page_response
        # Verify the request was made with the correct page ID (canonicalized dashed UUID)
        call_args = mock_client_instance.request.call_args
        assert call_args.kwargs["url"] == f"https://api.notion.com/v1/pages/{test_page_id}"


@pytest.mark.asyncio
async def test_retrieve_page_without_dashes(notion_client, sample_page_response):
    """
    Test retrieving a page with ID that doesn't have dashes.

    Success conditions:
    - Page ID without dashes works correctly
    - ID is canonicalized to dashed UUID
    """
    page_id_no_dashes = "12345678123412341234123456789abc"
    expected_dashed_id = "12345678-1234-1234-1234-123456789abc"
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_page_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await notion_client.retrieve_page(page_id_no_dashes)
        assert result == sample_page_response
        # Verify request used dashed ID
        call_args = mock_client_instance.request.call_args
        assert call_args.kwargs["url"] == f"https://api.notion.com/v1/pages/{expected_dashed_id}"


@pytest.mark.asyncio
async def test_retrieve_page_invalid_id(notion_client):
    """
    Test retrieving a page with invalid/empty ID.

    Failure conditions:
    - Empty page ID raises NotionAPIError
    - None page ID raises NotionAPIError
    """
    with pytest.raises(NotionAPIError, match="Page ID is required"):
        await notion_client.retrieve_page("")

    with pytest.raises(NotionAPIError, match="Page ID is required"):
        await notion_client.retrieve_page("   ")


@pytest.mark.asyncio
async def test_retrieve_page_not_found(notion_client, test_page_id):
    """
    Test retrieving a page that doesn't exist.

    Failure conditions:
    - 404 error raises NotionAPIError with appropriate message
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Page not found"}
        mock_response.text = '{"message": "Page not found"}'

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
            await notion_client.retrieve_page(test_page_id)


@pytest.mark.asyncio
async def test_retrieve_page_timeout(notion_client, test_page_id):
    """
    Test timeout when retrieving a page.

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
            await notion_client.retrieve_page(test_page_id)


@pytest.mark.asyncio
async def test_retrieve_page_network_error(notion_client, test_page_id):
    """
    Test network error when retrieving a page.

    Failure conditions:
    - Network error raises NotionAPIError
    """
    with patch("httpx.AsyncClient") as mock_client:
        network_error = httpx.RequestError("Connection failed", request=MagicMock())
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(side_effect=network_error)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        with pytest.raises(NotionAPIError, match="Network error"):
            await notion_client.retrieve_page(test_page_id)


@pytest.mark.asyncio
async def test_retrieve_page_empty_response(notion_client, test_page_id):
    """
    Test empty response from API.

    Failure conditions:
    - Empty response raises NotionAPIError
    """
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        with pytest.raises(NotionAPIError, match="empty response"):
            await notion_client.retrieve_page(test_page_id)

