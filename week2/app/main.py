from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import init_db
from .exception_handlers import (
    action_item_not_found_handler,
    app_exception_handler,
    database_error_handler,
    general_exception_handler,
    note_not_found_handler,
)
from .exceptions import ActionItemNotFoundError, AppException, DatabaseError, NoteNotFoundError
from .routers import action_items, notes

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_title,
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the frontend HTML page."""
    html_path = settings.frontend_dir / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"Frontend file not found: {html_path}")
    return html_path.read_text(encoding="utf-8")


# Register exception handlers
app.add_exception_handler(NoteNotFoundError, note_not_found_handler)
app.add_exception_handler(ActionItemNotFoundError, action_item_not_found_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Include routers
app.include_router(notes.router)
app.include_router(action_items.router)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.frontend_dir)), name="static")