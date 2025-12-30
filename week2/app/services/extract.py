from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Action(BaseModel):
    action: str


class ActionItemsResponse(BaseModel):
    actions: list[Action]


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique

def extract_action_items_llm(text: str) -> list[str]:
    """
    Use an LLM (via ollama) to extract action items from the input text.
    Returns a list of action item strings.
    """
    # Early return for empty input
    if not text or not text.strip():
        return []
    
    # Define the system and user prompt
    system_prompt = (
        "You are an assistant that extracts action items from meeting notes, "
        "regardless of how the action items are formatted. "
        "Action items can be delimited by '-', '*', numbers, or preceded by words like TODO, action, or next. "
        "If the input text does not contain any action items, return an empty list. "
        "If the input is empty or blank, return an empty list."
    )
    user_prompt = (
        f"Extract all action items from the following notes:\n\n{text}\n\n"
        "Return the action items as a list of Action objects, each with an 'action' field."
    )

    # Call ollama API with format parameter
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        format=ActionItemsResponse.model_json_schema(),
        options={"temperature": 0.3},
    )
    
    # Parse the response using Pydantic
    action_items_response = ActionItemsResponse.model_validate_json(response.message.content)
    
    # Extract action strings from Action objects
    return [action.action for action in action_items_response.actions]


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
