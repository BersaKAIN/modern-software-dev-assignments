from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_create_note(client: TestClient):
    """Test creating a new note."""
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
    """Test creating a note with empty content (should fail validation)."""
    response = client.post(
        "/notes",
        json={"content": ""},
    )
    
    assert response.status_code == 422  # Validation error


def test_create_note_missing_content(client: TestClient):
    """Test creating a note with missing content field (should fail validation)."""
    response = client.post(
        "/notes",
        json={},
    )
    
    assert response.status_code == 422  # Validation error


def test_get_note_by_id(client: TestClient):
    """Test getting an existing note by ID."""
    # Create a note first
    content = "Test note content"
    create_response = client.post(
        "/notes",
        json={"content": content},
    )
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]
    
    # Get the note
    response = client.get(f"/notes/{note_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["content"] == content
    assert "created_at" in data


def test_get_note_not_found(client: TestClient):
    """Test getting a non-existent note (should return 404)."""
    response = client.get("/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "99999" in data["detail"]


def test_list_notes_empty(client: TestClient):
    """Test listing notes when none exist."""
    response = client.get("/notes")
    
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == []


def test_list_notes_with_data(client: TestClient):
    """Test listing all notes."""
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
    """Test that notes are ordered by ID descending (newest first)."""
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

