from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# Shared field definition for note content/text
NOTE_CONTENT_FIELD = Field(..., min_length=1, description="The content/text of the note")


# Base Note Schema
class NoteBase(BaseModel):
    """Base schema for note content with shared field constraints."""

    content: str = NOTE_CONTENT_FIELD


# Note Schemas
class NoteCreate(NoteBase):
    """Schema for creating a new note."""

    pass


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: int
    created_at: str

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for list of notes response."""

    notes: List[NoteResponse]


# Action Item Schemas
class ActionItemExtractRequest(BaseModel):
    """Schema for action item extraction request."""

    text: str = NOTE_CONTENT_FIELD
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ActionItemResponse(BaseModel):
    """Schema for a single action item response."""

    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str

    class Config:
        from_attributes = True


class ActionItemExtractResponse(BaseModel):
    """Schema for action item extraction response."""

    note_id: Optional[int] = None
    items: List[ActionItemResponse]


class ActionItemListResponse(BaseModel):
    """Schema for list of action items response."""

    items: List[ActionItemResponse]


class ActionItemDoneRequest(BaseModel):
    """Schema for marking an action item as done."""

    done: bool = Field(default=True, description="Whether the action item is done")


class ActionItemDoneResponse(BaseModel):
    """Schema for action item done response."""

    id: int
    done: bool


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
    status_code: int

