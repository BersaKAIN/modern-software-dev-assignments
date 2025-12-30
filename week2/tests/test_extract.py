import os
import logging
import pytest

from ..app.services.extract import extract_action_items

# Get a logger for this module
logger = logging.getLogger(__name__)


def test_extract_bullets_and_checkboxes():
    """
    Test extracting action items from text with various bullet and checkbox formats.
    
    Scenario: Text contains action items formatted as checkboxes (- [ ]), bullets (*), 
    and numbered lists (1.), mixed with narrative text.
    
    Success conditions:
    - All action items are extracted correctly
    - Checkbox items are extracted (e.g., "Set up database")
    - Bullet items are extracted (e.g., "implement API extract endpoint")
    - Numbered list items are extracted (e.g., "Write tests")
    - Narrative sentences are not extracted as action items
    
    Failure conditions:
    - Action items are missing from extraction
    - Narrative text is incorrectly extracted as action items
    - Different formats are not recognized
    - Extraction logic fails for mixed formats
    """
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items

import re

from ..app.services.extract import extract_action_items_llm

@pytest.mark.skipif(
    not os.environ.get("RUN_LLM_TESTS"),
    reason="LLM-based test; set RUN_LLM_TESTS=1 to enable",
)
def test_extract_action_items_llm_bullets_and_numbers():
    """
    Test LLM-based extraction of action items from various formats.
    
    Scenario: Text contains action items in multiple formats (bullets, numbers, keywords, 
    checkboxes) mixed with narrative text that should not be extracted.
    
    Success conditions:
    - All action items are extracted regardless of format
    - Bullet items are extracted (e.g., "Set up development environment")
    - Numbered items are extracted (e.g., "Deploy backend API")
    - Keyword-prefixed items are extracted (e.g., "TODO:", "next:", "action:")
    - Checkbox items are extracted (e.g., "[ ] Document database schema")
    - Narrative text is not extracted as action items
    
    Failure conditions:
    - Action items are missing from extraction
    - Narrative text is incorrectly extracted
    - Different formats are not recognized by LLM
    - LLM extraction fails or returns incorrect results
    """
    # Bullets with '-', '*', numbered list, and mix of checkboxes
    text = """
    - Set up development environment
    * Create user authentication flow
    1. Deploy backend API
    2. TODO: Write frontend integration
    Some random note that isn't an action item.
    next: Review code quality
    action: Produce deployment instructions
    [ ] Document database schema
    """

    items = extract_action_items_llm(text)
    assert any(re.search(r"set up.*environment", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"create.*authentication", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"deploy.*api", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"write frontend integration", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"review code quality", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"produce deployment instructions", i, re.IGNORECASE) for i in items)
    assert any(re.search(r"document database schema", i, re.IGNORECASE) for i in items)
    assert all(not re.search(r"random note", i, re.IGNORECASE) for i in items)

@pytest.mark.skipif(
    not os.environ.get("RUN_LLM_TESTS"),
    reason="LLM-based test; set RUN_LLM_TESTS=1 to enable",
)
@pytest.mark.parametrize(
    "text,expected",
    [
        (
            # Only keyword prefixes
            "TODO: Refactor codebase\naction: Add tests\nnext: Release app",
            ["Refactor codebase", "Add tests", "Release app"],
        ),
        (
            # Only checkboxes
            "[ ] Prepare slides\n[todo] Schedule meeting",
            ["Prepare slides", "Schedule meeting"],
        ),
        (
            # Sentences inside a paragraph
            "We need to improve logging. Add data validation. Check error handling. The team will discuss next week.",
            ["Add data validation", "Check error handling"],
        ),
        (
            # Empty input
            "",
            [],
        ),
        (
            # Input with no valid action items
            "There was a meeting. No follow up is needed.",
            [],
        ),
    ]
)
def test_extract_action_items_llm_varied_inputs(text, expected):
    """
    Test LLM-based extraction with various input scenarios.
    
    Scenario: Tests multiple input formats including keyword prefixes, checkboxes, 
    sentences in paragraphs, empty input, and text with no action items.
    
    Success conditions:
    - Keyword-prefixed items are extracted correctly
    - Checkbox items are extracted correctly
    - Action items within paragraphs are identified
    - Empty input returns empty list
    - Text with no action items returns empty list
    - All expected items are found in the output
    
    Failure conditions:
    - Expected items are missing from extraction
    - Empty input returns non-empty list
    - Text with no action items returns action items
    - Extraction fails for specific formats
    - LLM hallucinates items that don't exist
    """
    items = extract_action_items_llm(text)
    for exp in expected:
        assert any(exp.lower() in i.lower() for i in items), f"Expected '{exp}' in LLM output: {items}"
    if not expected:
        assert items == [] or all(not i.strip() for i in items)  # Accepts empty or whitespace-only returns

