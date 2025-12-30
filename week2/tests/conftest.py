from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ..app import config
from ..app.db import init_db
from ..app.main import app


@pytest.fixture(scope="function")
def temp_db() -> Generator[Path, None, None]:
    """
    Create a temporary database file for testing.
    
    This fixture provides test isolation by creating a fresh SQLite database
    for each test function. The database is initialized with the required tables
    and cleaned up after the test completes.
    
    Success conditions:
    - Temporary database file is created
    - Database is initialized with proper schema
    - Settings are correctly overridden
    - Database is cleaned up after test
    
    Failure conditions:
    - Database file cannot be created
    - Database initialization fails
    - Settings override does not work
    - Cleanup fails (file remains)
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    db_path_obj = Path(db_path)
    
    # Override the settings.db_path temporarily
    # This works because db module imports settings at module level
    original_db_path = config.settings.db_path
    config.settings.db_path = db_path_obj
    
    # Initialize the database
    init_db()
    
    yield db_path_obj
    
    # Restore original db_path
    config.settings.db_path = original_db_path
    
    # Clean up temporary database
    if db_path_obj.exists():
        db_path_obj.unlink()


@pytest.fixture(scope="function")
def client(temp_db: Path) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client with a temporary database.
    
    This fixture provides a TestClient instance that uses the temporary database
    created by the temp_db fixture. This ensures each test has an isolated database
    and can make HTTP requests to the FastAPI application.
    
    Success conditions:
    - TestClient is created successfully
    - TestClient uses the temporary database
    - HTTP requests can be made to all endpoints
    - Client is properly closed after test
    
    Failure conditions:
    - TestClient cannot be created
    - TestClient uses wrong database
    - HTTP requests fail
    - Client is not properly cleaned up
    """
    with TestClient(app) as test_client:
        yield test_client

