from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_note_not_found_error_handler(client: TestClient):
    """Test that NoteNotFoundError returns 404 with proper error response."""
    response = client.get("/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "status_code" in data
    assert data["status_code"] == 404
    assert "99999" in data["detail"]
    assert "not found" in data["detail"].lower()


def test_action_item_not_found_error_handler(client: TestClient):
    """Test that ActionItemNotFoundError returns 404 with proper error response."""
    response = client.post(
        "/action-items/99999/done",
        json={"done": True},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "status_code" in data
    assert data["status_code"] == 404
    assert "99999" in data["detail"]
    assert "not found" in data["detail"].lower()


def test_validation_error_format(client: TestClient):
    """Test that validation errors return proper 422 format."""
    # Missing required field
    response = client.post(
        "/notes",
        json={},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_empty_text_validation_error(client: TestClient):
    """Test that empty text validation returns 422."""
    response = client.post(
        "/action-items/extract",
        json={"text": "", "save_note": False},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

