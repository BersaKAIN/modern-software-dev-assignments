from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_extract_action_items_without_saving_note(client: TestClient):
    """
    Test extracting action items from text without saving the text as a note.
    
    Scenario: User provides text with action items (bullets, checkboxes, numbered lists)
    and sets save_note=False.
    
    Success conditions:
    - Returns 200 status code
    - note_id is None (no note was created)
    - Action items are extracted and returned with proper structure
    - All action items have note_id=None and done=False
    
    Failure conditions:
    - Non-200 status code
    - note_id is not None
    - Action items are missing or incorrectly extracted
    - Action item structure is invalid
    """
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """
    
    response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": False},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["note_id"] is None
    assert len(data["items"]) > 0
    
    # Verify action items were extracted
    item_texts = [item["text"] for item in data["items"]]
    assert "Set up database" in item_texts
    assert "implement API extract endpoint" in item_texts
    assert "Write tests" in item_texts
    
    # Verify action item structure
    for item in data["items"]:
        assert "id" in item
        assert "text" in item
        assert "done" in item
        assert "created_at" in item
        assert item["note_id"] is None
        assert item["done"] is False


def test_extract_action_items_with_saving_note(client: TestClient):
    """
    Test extracting action items from text and saving the text as a note.
    
    Scenario: User provides text with action items and sets save_note=True.
    
    Success conditions:
    - Returns 200 status code
    - note_id is not None (a note was created)
    - Action items are extracted and linked to the created note
    - The note can be retrieved and contains the original text
    - All action items have the correct note_id
    
    Failure conditions:
    - Non-200 status code
    - note_id is None
    - Action items are not linked to the note
    - Note cannot be retrieved or has incorrect content
    """
    text = """
    Meeting notes:
    - Review code
    - Deploy application
    """
    
    response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": True},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["note_id"] is not None
    assert isinstance(data["note_id"], int)
    assert len(data["items"]) > 0
    
    # Verify action items are linked to the note
    for item in data["items"]:
        assert item["note_id"] == data["note_id"]
    
    # Verify the note was created
    note_response = client.get(f"/notes/{data['note_id']}")
    assert note_response.status_code == 200
    note_data = note_response.json()
    assert note_data["content"] == text


def test_extract_action_items_empty_text(client: TestClient):
    """
    Test extracting action items with empty text string.
    
    Scenario: User provides an empty string for the text field.
    
    Success conditions:
    - Returns 422 status code (validation error)
    - Request is rejected before processing
    
    Failure conditions:
    - Returns 200 status code (should not process empty text)
    - Action items are extracted from empty text
    """
    response = client.post(
        "/action-items/extract",
        json={"text": "", "save_note": False},
    )
    
    assert response.status_code == 422  # Validation error


def test_extract_action_items_missing_text(client: TestClient):
    """
    Test extracting action items with missing required text field.
    
    Scenario: User sends request without the required 'text' field in the JSON payload.
    
    Success conditions:
    - Returns 422 status code (validation error)
    - Request is rejected due to missing required field
    
    Failure conditions:
    - Returns 200 status code (should not process without text)
    - Request is processed without the text field
    """
    response = client.post(
        "/action-items/extract",
        json={"save_note": False},
    )
    
    assert response.status_code == 422  # Validation error


def test_extract_action_items_default_save_note(client: TestClient):
    """
    Test that save_note parameter defaults to False when not provided.
    
    Scenario: User sends request without specifying the save_note field.
    
    Success conditions:
    - Returns 200 status code
    - note_id is None (defaults to not saving note)
    - Action items are extracted successfully
    
    Failure conditions:
    - Returns non-200 status code
    - note_id is not None (should default to False)
    - Request fails due to missing save_note field
    """
    text = "Some notes with - action item"
    
    response = client.post(
        "/action-items/extract",
        json={"text": text},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["note_id"] is None


def test_list_action_items_empty(client: TestClient):
    """
    Test listing action items when no action items exist in the database.
    
    Scenario: Database is empty, user requests list of all action items.
    
    Success conditions:
    - Returns 200 status code
    - Returns empty list in items array
    - Response structure is valid
    
    Failure conditions:
    - Non-200 status code
    - Returns non-empty list when database is empty
    - Invalid response structure
    """
    response = client.get("/action-items")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_list_action_items_with_data(client: TestClient):
    """
    Test listing all action items when multiple action items exist.
    
    Scenario: Multiple action items exist in database, user requests list without filters.
    
    Success conditions:
    - Returns 200 status code
    - Returns all action items
    - Items are ordered by ID descending (newest first)
    - Response structure is valid
    
    Failure conditions:
    - Non-200 status code
    - Missing action items in response
    - Incorrect ordering (not descending by ID)
    - Invalid response structure
    """
    # Create some action items
    text1 = "- First action item"
    text2 = "- Second action item"
    
    client.post("/action-items/extract", json={"text": text1, "save_note": False})
    client.post("/action-items/extract", json={"text": text2, "save_note": False})
    
    response = client.get("/action-items")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2
    
    # Verify items are ordered by ID descending (newest first)
    item_ids = [item["id"] for item in data["items"]]
    assert item_ids == sorted(item_ids, reverse=True)


def test_list_action_items_filtered_by_note_id(client: TestClient):
    """
    Test listing action items filtered by a specific note_id.
    
    Scenario: Action items exist both linked and unlinked to notes, user filters by note_id.
    
    Success conditions:
    - Returns 200 status code
    - Returns only action items linked to the specified note_id
    - Does not return action items linked to other notes or unlinked items
    - All returned items have the correct note_id
    
    Failure conditions:
    - Non-200 status code
    - Returns action items not linked to the specified note_id
    - Missing action items that should be included
    - Filtering logic is incorrect
    """
    # Create a note with action items
    text = """
    Meeting notes:
    - Action 1
    - Action 2
    """
    
    extract_response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": True},
    )
    assert extract_response.status_code == 200
    note_id = extract_response.json()["note_id"]
    
    # Create action items without a note
    client.post(
        "/action-items/extract",
        json={"text": "- Unlinked action", "save_note": False},
    )
    
    # Filter by note_id
    response = client.get(f"/action-items?note_id={note_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2
    
    # Verify all items belong to the specified note
    for item in data["items"]:
        assert item["note_id"] == note_id


def test_list_action_items_filtered_by_nonexistent_note_id(client: TestClient):
    """
    Test listing action items filtered by a note_id that doesn't exist.
    
    Scenario: User filters action items by a note_id that has no associated action items.
    
    Success conditions:
    - Returns 200 status code
    - Returns empty list (no action items match the filter)
    - Does not raise an error for non-existent note_id
    
    Failure conditions:
    - Non-200 status code (should handle gracefully)
    - Returns action items when none should match
    - Raises exception for non-existent note_id
    """
    response = client.get("/action-items?note_id=99999")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_mark_action_item_done(client: TestClient):
    """
    Test marking an existing action item as done.
    
    Scenario: User marks an action item as completed by setting done=True.
    
    Success conditions:
    - Returns 200 status code
    - Response contains correct action item id and done=True
    - Action item is updated in database (verified by listing)
    - Status persists when retrieved again
    
    Failure conditions:
    - Non-200 status code
    - Action item is not updated in database
    - Response contains incorrect id or done status
    - Status does not persist
    """
    # Create an action item
    text = "- Complete this task"
    extract_response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": False},
    )
    assert extract_response.status_code == 200
    action_item_id = extract_response.json()["items"][0]["id"]
    
    # Mark as done
    response = client.post(
        f"/action-items/{action_item_id}/done",
        json={"done": True},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == action_item_id
    assert data["done"] is True
    
    # Verify it's marked as done in the list
    list_response = client.get("/action-items")
    list_data = list_response.json()
    item = next(item for item in list_data["items"] if item["id"] == action_item_id)
    assert item["done"] is True


def test_mark_action_item_not_done(client: TestClient):
    """
    Test marking an action item as not done (unmarking a completed item).
    
    Scenario: User marks a previously completed action item as incomplete by setting done=False.
    
    Success conditions:
    - Returns 200 status code
    - Response contains correct action item id and done=False
    - Action item status is updated from done to not done
    - Status persists when retrieved again
    
    Failure conditions:
    - Non-200 status code
    - Action item status is not updated
    - Response contains incorrect status
    - Cannot change status from done to not done
    """
    # Create an action item
    text = "- Complete this task"
    extract_response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": False},
    )
    assert extract_response.status_code == 200
    action_item_id = extract_response.json()["items"][0]["id"]
    
    # First mark as done
    client.post(
        f"/action-items/{action_item_id}/done",
        json={"done": True},
    )
    
    # Then mark as not done
    response = client.post(
        f"/action-items/{action_item_id}/done",
        json={"done": False},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == action_item_id
    assert data["done"] is False
    
    # Verify it's marked as not done in the list
    list_response = client.get("/action-items")
    list_data = list_response.json()
    item = next(item for item in list_data["items"] if item["id"] == action_item_id)
    assert item["done"] is False


def test_mark_action_item_done_default_value(client: TestClient):
    """
    Test that the done parameter defaults to True when not provided in the request.
    
    Scenario: User marks action item as done without specifying the done field.
    
    Success conditions:
    - Returns 200 status code
    - done defaults to True (action item is marked as done)
    - Response reflects the default value
    
    Failure conditions:
    - Non-200 status code
    - done does not default to True
    - Request fails due to missing done field
    """
    # Create an action item
    text = "- Complete this task"
    extract_response = client.post(
        "/action-items/extract",
        json={"text": text, "save_note": False},
    )
    assert extract_response.status_code == 200
    action_item_id = extract_response.json()["items"][0]["id"]
    
    # Mark as done without specifying done field
    response = client.post(
        f"/action-items/{action_item_id}/done",
        json={},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True


def test_mark_action_item_done_not_found(client: TestClient):
    """
    Test marking a non-existent action item as done.
    
    Scenario: User attempts to mark an action item that doesn't exist in the database.
    
    Success conditions:
    - Returns 404 status code (not found)
    - Error response contains detail message with the action item id
    - No action item is created or modified
    
    Failure conditions:
    - Returns 200 status code (should not succeed)
    - Returns different error code
    - Creates or modifies an action item
    - Error message is missing or incorrect
    """
    response = client.post(
        "/action-items/99999/done",
        json={"done": True},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "99999" in data["detail"]

