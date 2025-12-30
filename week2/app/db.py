from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from .config import settings
from .data_models import ActionItem, Note
from .exceptions import DatabaseError


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Get a database connection with proper error handling."""
    try:
        ensure_data_directory_exists()
        connection = sqlite3.connect(str(settings.db_path))
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to connect to database: {e}", original_error=e) from e


def init_db() -> None:
    """Initialize the database with required tables."""
    try:
        ensure_data_directory_exists()
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            connection.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}", original_error=e) from e


def insert_note(content: str) -> int:
    """Insert a new note and return its ID."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert note: {e}", original_error=e) from e


def list_notes() -> list[Note]:
    """List all notes, ordered by ID descending."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [Note.from_row(dict(row)) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list notes: {e}", original_error=e) from e


def get_note(note_id: int) -> Optional[Note]:
    """Get a note by ID, or None if not found."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Note.from_row(dict(row))
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get note: {e}", original_error=e) from e


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """Insert action items and return their IDs."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            connection.commit()
            return ids
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert action items: {e}", original_error=e) from e


def list_action_items(note_id: Optional[int] = None) -> list[ActionItem]:
    """List action items, optionally filtered by note_id, ordered by ID descending."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            rows = cursor.fetchall()
            return [ActionItem.from_row(dict(row)) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list action items: {e}", original_error=e) from e


def get_action_items_by_ids(action_item_ids: list[int]) -> list[ActionItem]:
    """Get action items by their IDs."""
    if not action_item_ids:
        return []
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            placeholders = ",".join("?" * len(action_item_ids))
            cursor.execute(
                f"SELECT id, note_id, text, done, created_at FROM action_items WHERE id IN ({placeholders})",
                action_item_ids,
            )
            rows = cursor.fetchall()
            return [ActionItem.from_row(dict(row)) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get action items: {e}", original_error=e) from e


def get_action_item(action_item_id: int) -> Optional[ActionItem]:
    """Get an action item by ID, or None if not found."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (action_item_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return ActionItem.from_row(dict(row))
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get action item: {e}", original_error=e) from e


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark an action item as done or not done."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            connection.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to update action item: {e}", original_error=e) from e


