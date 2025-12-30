"""Integration tests against the real Notion API."""

import pytest
import os
from server.config import Config
from server.tools.notion import NotionClient

# Integration credentials provided by user
INTEGRATION_SECRET = "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"
# TEST_PAGE_ID = "963a77dafe2e4147a4bd87ed5a125ef1"
TEST_PAGE_ID = "2e2bcdf864bc80178863d9b29d01949a"


class IntegrationConfig(Config):
    """Configuration for integration tests."""
    NOTION_API_KEY = INTEGRATION_SECRET


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_retrieve_page():
    """
    Test retrieving a real page from Notion API.
    
    This test hits the actual Notion API using the provided credentials.
    """
    client = NotionClient(config=IntegrationConfig)
    
    print(f"\nAttempting to retrieve page: {TEST_PAGE_ID}")
    try:
        page = await client.retrieve_page(TEST_PAGE_ID)
        
        # Verify the response
        assert page["object"] == "page"
        # The API returns dashes in the ID
        canonical_id = f"{TEST_PAGE_ID[:8]}-{TEST_PAGE_ID[8:12]}-{TEST_PAGE_ID[12:16]}-{TEST_PAGE_ID[16:20]}-{TEST_PAGE_ID[20:]}"
        assert page["id"] == canonical_id
        
        print(f"Successfully retrieved page: {page['id']}")
        print(f"Page URL: {page.get('url')}")
        
    except Exception as e:
        pytest.fail(f"Integration test failed: {str(e)}")
