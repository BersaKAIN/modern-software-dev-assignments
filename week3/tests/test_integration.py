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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_create_and_retrieve_page():
    """
    Test creating a page titled 'NEW_TEST_PAGE' and then retrieving it.
    
    This verifies the end-to-end flow of creating a resource and then accessing it.
    """
    client = NotionClient(config=IntegrationConfig)
    
    title = "NEW_TEST_PAGE"
    print(f"\nAttempting to create page under parent: {TEST_PAGE_ID}")
    
    try:
        # 1. Create page
        created_page = await client.create_page(
            parent_id=TEST_PAGE_ID,
            title=title
        )
        
        assert created_page["object"] == "page"
        page_id = created_page["id"]
        print(f"Successfully created page: {page_id} with title '{title}'")
        
        # 2. Retrieve page
        print(f"Attempting to retrieve created page: {page_id}")
        retrieved_page = await client.retrieve_page(page_id)
        
        assert retrieved_page["id"] == page_id
        
        # Verify title matches
        retrieved_title_obj = retrieved_page["properties"].get("title") or retrieved_page["properties"].get("Title")
        
        if retrieved_title_obj and "title" in retrieved_title_obj:
             if retrieved_title_obj["title"]:
                 content = retrieved_title_obj["title"][0]["text"]["content"]
                 assert content == title
                 print("Title verification successful")
             else:
                 print("Warning: Title is empty")
        else:
            print(f"Warning: Could not verify title structure. Keys: {retrieved_page['properties'].keys()}")

    except Exception as e:
        pytest.fail(f"Integration create/retrieve test failed: {str(e)}")
