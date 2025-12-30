from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from .. import db
from ..exceptions import ActionItemNotFoundError
from ..schemas import (
    ActionItemDoneRequest,
    ActionItemDoneResponse,
    ActionItemExtractRequest,
    ActionItemExtractResponse,
    ActionItemListResponse,
    ActionItemResponse,
)
from ..services.extract import extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ActionItemExtractResponse)
def extract(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    """Extract action items from text."""
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items_llm(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    
    # Get the inserted action items by their IDs
    inserted_items = db.get_action_items_by_ids(ids)
    
    return ActionItemExtractResponse(
        note_id=note_id,
        items=[
            ActionItemResponse(
                id=ai.id,
                note_id=ai.note_id,
                text=ai.text,
                done=ai.done,
                created_at=ai.created_at,
            )
            for ai in inserted_items
        ],
    )


@router.get("", response_model=ActionItemListResponse)
def list_all(note_id: Optional[int] = Query(None, description="Filter by note ID")) -> ActionItemListResponse:
    """List all action items, optionally filtered by note_id."""
    action_items = db.list_action_items(note_id=note_id)
    return ActionItemListResponse(
        items=[
            ActionItemResponse(
                id=ai.id,
                note_id=ai.note_id,
                text=ai.text,
                done=ai.done,
                created_at=ai.created_at,
            )
            for ai in action_items
        ]
    )


@router.post("/{action_item_id}/done", response_model=ActionItemDoneResponse)
def mark_done(action_item_id: int, payload: ActionItemDoneRequest) -> ActionItemDoneResponse:
    """Mark an action item as done or not done."""
    # Verify action item exists
    action_item = db.get_action_item(action_item_id)
    if action_item is None:
        raise ActionItemNotFoundError(action_item_id)
    
    db.mark_action_item_done(action_item_id, payload.done)
    return ActionItemDoneResponse(id=action_item_id, done=payload.done)


