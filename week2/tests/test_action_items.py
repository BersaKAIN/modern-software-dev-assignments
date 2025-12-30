from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_extract_action_items_without_saving_note(client: TestClient):
    """Test extracting action items without saving as a note."""
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
    """Test extracting action items and saving the text as a note."""
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
    """Test extracting action items with empty text (should fail validation)."""
    response = client.post(
        "/action-items/extract",
        json={"text": "", "save_note": False},
    )
    
    assert response.status_code == 422  # Validation error


def test_extract_action_items_missing_text(client: TestClient):
    """Test extracting action items with missing text field (should fail validation)."""
    response = client.post(
        "/action-items/extract",
        json={"save_note": False},
    )
    
    assert response.status_code == 422  # Validation error


def test_extract_action_items_default_save_note(client: TestClient):
    """Test that save_note defaults to False when not provided."""
    text = "Some notes with - action item"
    
    response = client.post(
        "/action-items/extract",
        json={"text": text},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["note_id"] is None


def test_list_action_items_empty(client: TestClient):
    """Test listing action items when none exist."""
    response = client.get("/action-items")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_list_action_items_with_data(client: TestClient):
    """Test listing all action items."""
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
    """Test listing action items filtered by note_id."""
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
    """Test listing action items filtered by a note_id that doesn't exist."""
    response = client.get("/action-items?note_id=99999")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_mark_action_item_done(client: TestClient):
    """Test marking an action item as done."""
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
    """Test marking an action item as not done."""
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
    """Test that done defaults to True when not provided."""
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
    """Test marking a non-existent action item as done (should return 404)."""
    response = client.post(
        "/action-items/99999/done",
        json={"done": True},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "99999" in data["detail"]

