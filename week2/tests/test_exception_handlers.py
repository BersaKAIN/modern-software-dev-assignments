from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_note_not_found_error_handler(client: TestClient):
    """
    Test that NoteNotFoundError exception is handled correctly.
    
    Scenario: User requests a note by ID that doesn't exist, triggering NoteNotFoundError.
    
    Success conditions:
    - Returns 404 status code (not found)
    - Error response contains 'detail' and 'status_code' fields
    - status_code field is 404
    - detail message includes the note id and indicates not found
    
    Failure conditions:
    - Returns non-404 status code
    - Missing required error response fields
    - Error message is missing or incorrect
    - Exception is not caught and handled properly
    """
    response = client.get("/notes/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "status_code" in data
    assert data["status_code"] == 404
    assert "99999" in data["detail"]
    assert "not found" in data["detail"].lower()


def test_action_item_not_found_error_handler(client: TestClient):
    """
    Test that ActionItemNotFoundError exception is handled correctly.
    
    Scenario: User attempts to mark a non-existent action item as done, triggering ActionItemNotFoundError.
    
    Success conditions:
    - Returns 404 status code (not found)
    - Error response contains 'detail' and 'status_code' fields
    - status_code field is 404
    - detail message includes the action item id and indicates not found
    
    Failure conditions:
    - Returns non-404 status code
    - Missing required error response fields
    - Error message is missing or incorrect
    - Exception is not caught and handled properly
    """
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
    """
    Test that validation errors return proper 422 format.
    
    Scenario: User sends request with missing required field, triggering Pydantic validation error.
    
    Success conditions:
    - Returns 422 status code (unprocessable entity)
    - Error response contains 'detail' field with validation information
    - Request is rejected before processing
    
    Failure conditions:
    - Returns non-422 status code
    - Missing detail field in error response
    - Request is processed despite validation error
    - Error format is incorrect
    """
    # Missing required field
    response = client.post(
        "/notes",
        json={},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_empty_text_validation_error(client: TestClient):
    """
    Test that empty text validation returns 422 error.
    
    Scenario: User sends request with empty text field, triggering field validation error.
    
    Success conditions:
    - Returns 422 status code (validation error)
    - Error response contains 'detail' field
    - Request is rejected due to empty text validation
    - No action items are extracted
    
    Failure conditions:
    - Returns non-422 status code
    - Empty text is accepted and processed
    - Missing detail field in error response
    - Validation does not catch empty text
    """
    response = client.post(
        "/action-items/extract",
        json={"text": "", "save_note": False},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

