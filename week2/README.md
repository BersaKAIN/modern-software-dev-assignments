# Action Item Extractor

A FastAPI-based web application that extracts actionable items from free-form meeting notes and text. The application supports both heuristic-based and LLM-powered extraction methods, allowing users to convert unstructured notes into organized, trackable action items.

## Overview

The Action Item Extractor is designed to help users process meeting notes, to-do lists, and other text inputs by automatically identifying and extracting actionable items. The application provides:

- **Dual Extraction Methods**: Both rule-based heuristics and LLM-powered extraction
- **Note Management**: Save and retrieve notes with full CRUD operations
- **Action Item Tracking**: Create, list, and mark action items as complete
- **Web Interface**: Simple HTML frontend for easy interaction
- **RESTful API**: Well-structured API endpoints for programmatic access

## Features

- Extract action items from various formats (bullet points, numbered lists, keyword prefixes)
- Save notes and associate action items with them
- Mark action items as done/undone
- Filter action items by note ID
- LLM-powered extraction using Ollama (llama3.1:8b model)
- Comprehensive error handling and validation
- SQLite database for persistent storage

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Conda environment (cs146s)
- Ollama installed and running locally
- llama3.1:8b model pulled in Ollama

### Installing Ollama and Model

1. Install Ollama from [https://ollama.com/download](https://ollama.com/download)
2. Pull the required model:
   ```bash
   ollama pull llama3.1:8b
   ```

## Setup

1. **Activate your conda environment**:
   ```bash
   conda activate cs146s
   ```

2. **Install dependencies** (from project root):
   ```bash
   poetry install
   ```

3. **Verify Ollama is running**:
   ```bash
   ollama list
   ```
   You should see `llama3.1:8b` in the list.

## Running the Application

From the project root directory:

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will start on `http://127.0.0.1:8000/`

### Access Points

- **Web Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative API Docs**: http://127.0.0.1:8000/redoc (ReDoc)

## API Endpoints

### Notes

#### Create a Note
- **POST** `/notes`
- **Request Body**:
  ```json
  {
    "content": "Meeting notes text here"
  }
  ```
- **Response**: Note object with `id`, `content`, and `created_at`

#### Get All Notes
- **GET** `/notes`
- **Response**: List of all notes ordered by ID (newest first)

#### Get Note by ID
- **GET** `/notes/{note_id}`
- **Response**: Single note object

### Action Items

#### Extract Action Items
- **POST** `/action-items/extract`
- **Request Body**:
  ```json
  {
    "text": "Meeting notes with action items:\n- [ ] Task 1\n- Task 2",
    "save_note": false
  }
  ```
- **Description**: Extracts action items from the provided text using LLM-powered extraction. Optionally saves the text as a note.
- **Response**: List of extracted action items with their IDs and metadata

#### List Action Items
- **GET** `/action-items`
- **Query Parameters**:
  - `note_id` (optional): Filter action items by note ID
- **Response**: List of action items (optionally filtered by note_id)

#### Mark Action Item as Done/Undone
- **POST** `/action-items/{action_item_id}/done`
- **Request Body**:
  ```json
  {
    "done": true
  }
  ```
- **Response**: Updated action item status

## Database Schema

The application uses SQLite with two main tables:

### Notes Table
- `id` (INTEGER PRIMARY KEY)
- `content` (TEXT NOT NULL)
- `created_at` (TEXT DEFAULT datetime('now'))

### Action Items Table
- `id` (INTEGER PRIMARY KEY)
- `note_id` (INTEGER, FOREIGN KEY to notes.id)
- `text` (TEXT NOT NULL)
- `done` (INTEGER DEFAULT 0)
- `created_at` (TEXT DEFAULT datetime('now'))

## Running Tests

The test suite uses `pytest` and includes both unit tests and integration tests.

### Run All Tests

```bash
poetry run pytest week2/tests/
```

### Run Specific Test Files

```bash
# Test extraction functionality
poetry run pytest week2/tests/test_extract.py

# Test notes endpoints
poetry run pytest week2/tests/test_notes.py

# Test action items endpoints
poetry run pytest week2/tests/test_action_items.py

# Test exception handlers
poetry run pytest week2/tests/test_exception_handlers.py
```

### Run LLM-Based Tests

Some tests require Ollama to be running and use the LLM for extraction. These tests are skipped by default and must be explicitly enabled:

```bash
RUN_LLM_TESTS=1 poetry run pytest week2/tests/test_extract.py
```

### Test Coverage

The test suite includes:
- Unit tests for extraction functions (heuristic and LLM-based)
- API endpoint tests for all routes
- Error handling and validation tests
- Database operation tests
- Edge case handling (empty inputs, missing fields, etc.)

## LLM Integration

### Model Used

The application uses **llama3.1:8b** via Ollama for LLM-powered action item extraction.

### Prompts

#### System Prompt
```
You are an assistant that extracts action items from meeting notes, 
regardless of how the action items are formatted. 
Action items can be delimited by '-', '*', numbers, or preceded by words like TODO, action, or next. 
If the input text does not contain any action items, return an empty list. 
If the input is empty or blank, return an empty list.
```

#### User Prompt
```
Extract action items from the content inside the <notes> tags.
Return a JSON object with a list of actions.

<notes>
{text}
</notes>
```

### Structured Output

The LLM extraction uses Pydantic models for structured output:

```python
class Action(BaseModel):
    action: str

class ActionItemsResponse(BaseModel):
    actions: list[Action]
```

The extraction function uses Ollama's `format` parameter to ensure JSON-structured responses, with temperature set to 0.0 to minimize hallucination.

### Extraction Function

The main LLM extraction function is `extract_action_items_llm()` in `week2/app/services/extract.py`. It:
1. Formats the input text with XML-style delimiters
2. Calls Ollama's chat API with structured output constraints
3. Parses the JSON response using Pydantic
4. Returns a list of action item strings

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── db.py                # Database operations
│   ├── data_models.py       # Data models (Note, ActionItem)
│   ├── schemas.py           # Pydantic schemas for API
│   ├── exceptions.py        # Custom exception classes
│   ├── exception_handlers.py # Exception handlers
│   ├── routers/
│   │   ├── notes.py         # Notes API endpoints
│   │   └── action_items.py  # Action items API endpoints
│   └── services/
│       └── extract.py       # Extraction logic (heuristic + LLM)
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_extract.py      # Extraction function tests
│   ├── test_notes.py         # Notes endpoint tests
│   ├── test_action_items.py # Action items endpoint tests
│   └── test_exception_handlers.py # Error handling tests
├── frontend/
│   └── index.html           # Web interface
├── data/
│   └── app.db               # SQLite database (created on first run)
├── assignment.md            # Assignment instructions
├── writeup.md               # Assignment writeup
└── README.md                # This file
```

## Configuration

Configuration is managed through `app/config.py` using Pydantic Settings. Environment variables can override defaults:

- `DB_PATH`: Path to SQLite database file (default: `week2/data/app.db`)
- `FRONTEND_DIR`: Directory containing frontend files (default: `week2/frontend`)
- `APP_TITLE`: Application title (default: "Action Item Extractor")
- `APP_DEBUG`: Debug mode (default: false)

## Error Handling

The application includes comprehensive error handling:

- `NoteNotFoundError`: Raised when a requested note doesn't exist
- `ActionItemNotFoundError`: Raised when a requested action item doesn't exist
- `DatabaseError`: Raised for database operation failures
- `AppException`: Base exception for application-specific errors

All exceptions are handled by dedicated exception handlers that return appropriate HTTP status codes and error messages.

## Development

### Code Style

The project uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting (selects E, F, I, UP, B rules)

### Adding New Features

1. Add new routes in `app/routers/`
2. Define schemas in `app/schemas.py`
3. Add database operations in `app/db.py`
4. Write tests in `tests/`
5. Update this README if adding new endpoints or features

## License

This project is part of a course assignment and is intended for educational purposes.

