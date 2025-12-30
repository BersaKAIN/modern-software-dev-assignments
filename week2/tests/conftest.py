from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ..app.config import settings
from ..app.db import init_db
from ..app.main import app


@pytest.fixture(scope="function")
def temp_db() -> Generator[Path, None, None]:
    """Create a temporary database file for testing."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    db_path_obj = Path(db_path)
    
    # Override the settings.db_path temporarily
    original_db_path = settings.db_path
    settings.db_path = db_path_obj
    
    # Initialize the database
    init_db()
    
    yield db_path_obj
    
    # Restore original db_path
    settings.db_path = original_db_path
    
    # Clean up temporary database
    if db_path_obj.exists():
        db_path_obj.unlink()


@pytest.fixture(scope="function")
def client(temp_db: Path) -> Generator[TestClient, None, None]:
    """Create a test client with a temporary database."""
    with TestClient(app) as test_client:
        yield test_client

