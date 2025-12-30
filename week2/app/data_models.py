from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Note:
    """Data model representing a note in the database."""

    id: int
    content: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> Note:
        """Create a Note instance from a database row."""
        return cls(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )


@dataclass
class ActionItem:
    """Data model representing an action item in the database."""

    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str

    @classmethod
    def from_row(cls, row: dict) -> ActionItem:
        """Create an ActionItem instance from a database row."""
        return cls(
            id=row["id"],
            note_id=row["note_id"],
            text=row["text"],
            done=bool(row["done"]),
            created_at=row["created_at"],
        )

