from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from .exceptions import ActionItemNotFoundError, AppException, DatabaseError, NoteNotFoundError
from .schemas import ErrorResponse

logger = logging.getLogger(__name__)


async def note_not_found_handler(request: Request, exc: NoteNotFoundError) -> JSONResponse:
    """Handle NoteNotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(detail=str(exc), status_code=404).model_dump(),
    )


async def action_item_not_found_handler(
    request: Request, exc: ActionItemNotFoundError
) -> JSONResponse:
    """Handle ActionItemNotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(detail=str(exc), status_code=404).model_dump(),
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle DatabaseError exceptions."""
    logger.error(f"Database error: {exc}", exc_info=exc.original_error)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="A database error occurred. Please try again later.",
            status_code=500,
        ).model_dump(),
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle general application exceptions."""
    logger.error(f"Application error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail=str(exc), status_code=500).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected error occurred. Please try again later.",
            status_code=500,
        ).model_dump(),
    )

