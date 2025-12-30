from __future__ import annotations


class AppException(Exception):
    """Base exception for application-specific errors."""

    pass


class NoteNotFoundError(AppException):
    """Raised when a note is not found."""

    def __init__(self, note_id: int):
        self.note_id = note_id
        super().__init__(f"Note with id {note_id} not found")


class ActionItemNotFoundError(AppException):
    """Raised when an action item is not found."""

    def __init__(self, action_item_id: int):
        self.action_item_id = action_item_id
        super().__init__(f"Action item with id {action_item_id} not found")


class DatabaseError(AppException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.original_error = original_error
        super().__init__(message)

