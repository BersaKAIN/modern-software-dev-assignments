from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_create_note(client: TestClient):
    """
    Test creating a new note with valid content.
    
    Scenario: User provides valid note content and creates a new note.
    
    Success conditions:
    - Returns 200 status code
    - Note is created with a unique id
    - Response contains id, content, and created_at fields
    - Content matches the input
    
    Failure conditions:
    - Non-200 status code
    - Note is not created
    - Missing required fields in response
    - Content does not match input
    """
    content = "This is a test note with some content."
    
    response = client.post(
        "/notes",
        json={"content": content},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert isinstance(data["id"], int)
    assert data["content"] == content
    assert "created_at" in data


def test_create_note_empty_content(client: TestClient):
    """
    Test creating a note with empty content string.
    
    Scenario: User attempts to create a note with an empty string for content.
    
    Success conditions:
    - Returns 422 status code (validation error)
    - Request is rejected before processing
    - Note is not created
    
    Failure conditions:
    - Returns 200 status code (should not accept empty content)
    - Note is created with empty content
    - Validation does not catch empty string
    """
    response = client.post(
        "/notes",
        json={"content": ""},
    )
    
    assert response.status_code == 422  # Validation error


def test_create_note_missing_content(client: TestClient):
    """
    Test creating a note with missing required content field.
    
    Scenario: User sends request without the required 'content' field in the JSON payload.
    
    Success conditions:
    - Returns 422 status code (validation error)
    - Request is rejected due to missing required field
    - Note is not created
    
    Failure conditions:
    - Returns 200 status code (should not process without content)
    - Request is processed without the content field
    - Note is created without content
    """
    response = client.post(
        "/notes",
        json={},
    )
    
    assert response.status_code == 422  # Validation error


def test_get_note_by_id(client: TestClient):
    """
    Test retrieving an existing note by its ID.
    
    Scenario: A note exists in the database, user requests it by ID.
    
    Success conditions:
    - Returns 200 status code
    - Response contains the correct note with matching id
    - Content matches the original note
    - All required fields (id, content, created_at) are present
    
    Failure conditions:
    - Non-200 status code
    - Note id does not match requested id
    - Content is incorrect or missing
    - Required fields are missing
    """
    # Create a note first
    content = "Test note content"
    create_response = client.post(
        "/notes",
        json={"content": content},
    )
    assert create_response.status_code == 200
    note_id = create_response.json()["id"]
    
    # Get the note
    response = client.get(f"/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["content"] == content
    assert "created_at" in data


def test_get_note_not_found(client: TestClient):
    """
    Test retrieving a note that doesn't exist.
    
    Scenario: User requests a note by ID that doesn't exist in the database.
    
    Success conditions:
    - Returns 404 status code (not found)
    - Error response contains detail message with the note id
    - No note is returned
    
    Failure conditions:
    - Returns 200 status code (should not succeed)
    - Returns different error code
    - Returns a note when none exists
    - Error message is missing or incorrect
    """
    response = client.get("/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "99999" in data["detail"]


def test_list_notes_empty(client: TestClient):
    """
    Test listing notes when no notes exist in the database.
    
    Scenario: Database is empty, user requests list of all notes.
    
    Success conditions:
    - Returns 200 status code
    - Returns empty list in notes array
    - Response structure is valid
    
    Failure conditions:
    - Non-200 status code
    - Returns non-empty list when database is empty
    - Invalid response structure
    """
    response = client.get("/notes")
    
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == []


def test_list_notes_with_data(client: TestClient):
    """
    Test listing all notes when multiple notes exist.
    
    Scenario: Multiple notes exist in database, user requests list without filters.
    
    Success conditions:
    - Returns 200 status code
    - Returns all created notes
    - All notes are present in the response
    - Response structure is valid
    
    Failure conditions:
    - Non-200 status code
    - Missing notes in response
    - Incorrect number of notes returned
    - Invalid response structure
    """
    # Create multiple notes
    content1 = "First note"
    content2 = "Second note"
    content3 = "Third note"
    
    create_response1 = client.post("/notes", json={"content": content1})
    create_response2 = client.post("/notes", json={"content": content2})
    create_response3 = client.post("/notes", json={"content": content3})
    
    assert all(r.status_code == 200 for r in [create_response1, create_response2, create_response3])
    
    # List all notes
    response = client.get("/notes")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) >= 3
    
    # Verify all created notes are in the list
    note_contents = [note["content"] for note in data["notes"]]
    assert content1 in note_contents
    assert content2 in note_contents
    assert content3 in note_contents


def test_list_notes_ordering(client: TestClient):
    """
    Test that notes are returned in descending order by ID (newest first).
    
    Scenario: Multiple notes exist with different IDs, user requests list.
    
    Success conditions:
    - Returns 200 status code
    - Notes are ordered by ID descending (highest ID first)
    - Newest note (highest ID) appears first in the list
    - Ordering is consistent
    
    Failure conditions:
    - Non-200 status code
    - Notes are not in descending order
    - Oldest note appears first (incorrect ordering)
    - Ordering is inconsistent
    """
    # Create multiple notes
    content1 = "First note"
    content2 = "Second note"
    content3 = "Third note"
    
    create_response1 = client.post("/notes", json={"content": content1})
    create_response2 = client.post("/notes", json={"content": content2})
    create_response3 = client.post("/notes", json={"content": content3})
    
    note_id1 = create_response1.json()["id"]
    note_id2 = create_response2.json()["id"]
    note_id3 = create_response3.json()["id"]
    
    # List all notes
    response = client.get("/notes")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify ordering (descending by ID)
    note_ids = [note["id"] for note in data["notes"]]
    assert note_ids == sorted(note_ids, reverse=True)
    
    # Verify the newest note (highest ID) is first
    assert data["notes"][0]["id"] == max(note_id1, note_id2, note_id3)

