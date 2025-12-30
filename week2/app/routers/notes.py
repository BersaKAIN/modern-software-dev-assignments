from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..exceptions import NoteNotFoundError
from ..schemas import NoteCreate, NoteListResponse, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreate) -> NoteResponse:
    """Create a new note."""
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise NoteNotFoundError(note_id)
    return NoteResponse(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
    )


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Get a note by ID."""
    note = db.get_note(note_id)
    if note is None:
        raise NoteNotFoundError(note_id)
    return NoteResponse(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
    )


@router.get("", response_model=NoteListResponse)
def list_notes() -> NoteListResponse:
    """List all notes."""
    notes = db.list_notes()
    return NoteListResponse(
        notes=[
            NoteResponse(id=note.id, content=note.content, created_at=note.created_at)
            for note in notes
        ]
    )


