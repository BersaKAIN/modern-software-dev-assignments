# MCP Notion Server

A Model Context Protocol (MCP) server that wraps the Notion API, providing tools for retrieving and creating Notion pages. The server runs locally via STDIO transport and integrates with MCP clients like Claude Desktop or Cursor.

## Overview

This MCP server exposes two tools for interacting with the Notion API:

1. **`notion_retrieve_page`** - Retrieve a Notion page by its ID
2. **`notion_create_page`** - Create a new page in Notion under a parent page or database

The server includes robust error handling, rate limiting, and comprehensive logging.

## Prerequisites

- Python 3.10 or higher
- A Notion API key (integration token)
- Poetry (for dependency management)

### Getting a Notion API Key

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "MCP Notion Server")
4. Select the workspace where you want to use it
5. Copy the "Internal Integration Token" (this is your API key)
6. Share the integration with the pages/databases you want to access:
   - Open the page/database in Notion
   - Click the "..." menu → "Connections" → "Add connections"
   - Select your integration

## Installation

1. **Install dependencies** (from project root):

```bash
poetry install
```

2. **Set up environment variables**:

Create a `.env` file in the `week3/` directory (or set environment variables):

```bash
NOTION_API_KEY=your_notion_api_key_here
```

Alternatively, export it in your shell:

```bash
export NOTION_API_KEY=your_notion_api_key_here
```

## Running the Server

### Local STDIO Server

Run the server using Python:

```bash
cd week3
poetry run python -m server.main
```

The server will communicate via STDIO, which is required for MCP clients like Claude Desktop.

## MCP Client Configuration

### Claude Desktop

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notion": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "-m",
        "server.main"
      ],
      "cwd": "/path/to/modern-software-dev-assignments/week3",
      "env": {
        "NOTION_API_KEY": "your_notion_api_key_here"
      }
    }
  }
}
```

**Note**: Replace `/path/to/modern-software-dev-assignments/week3` with the actual path to your `week3` directory.

### Cursor IDE

For Cursor IDE, configure the MCP server in your Cursor settings. The configuration is similar to Claude Desktop.

## Tool Reference

### `notion_retrieve_page`

Retrieve a Notion page by its ID.

**Parameters:**
- `page_id` (string, required): The ID of the Notion page to retrieve

**Returns:**
- Page object with properties, content, and metadata

**Example:**
```json
{
  "page_id": "12345678-1234-1234-1234-123456789abc"
}
```

**Example Response:**
```json
{
  "object": "page",
  "id": "12345678-1234-1234-1234-123456789abc",
  "created_time": "2023-01-01T00:00:00.000Z",
  "last_edited_time": "2023-01-01T00:00:00.000Z",
  "properties": {
    "title": {
      "title": [
        {
          "text": {
            "content": "My Page Title"
          }
        }
      ]
    }
  }
}
```

**Error Handling:**
- Invalid page ID: Returns error message
- Page not found (404): Returns error message
- Network errors: Returns error message with details
- Timeouts: Returns timeout error message

### `notion_create_page`

Create a new page in Notion under a parent page or database.

**Parameters:**
- `parent_id` (string, required): The ID of the parent page or database
- `title` (string, required): The title of the new page
- `properties` (object, optional): Additional page properties

**Returns:**
- Created page object with ID

**Example:**
```json
{
  "parent_id": "parent-1234-1234-1234-123456789abc",
  "title": "My New Page",
  "properties": {
    "Status": {
      "select": {
        "name": "In Progress"
      }
    }
  }
}
```

**Example Response:**
```json
{
  "object": "page",
  "id": "87654321-4321-4321-4321-cba987654321",
  "created_time": "2023-01-01T00:00:00.000Z",
  "last_edited_time": "2023-01-01T00:00:00.000Z",
  "properties": {
    "title": {
      "title": [
        {
          "text": {
            "content": "My New Page"
          }
        }
      ]
    }
  }
}
```

**Error Handling:**
- Missing parent_id or title: Returns validation error
- Invalid parent (404): Returns error message
- Network errors: Returns error message with details
- Timeouts: Returns timeout error message

## Example Invocation Flow

### Using Claude Desktop

1. **Start Claude Desktop** with the MCP server configured
2. **Ask Claude to retrieve a page**:
   ```
   Can you retrieve the Notion page with ID 12345678-1234-1234-1234-123456789abc?
   ```
   Claude will use the `notion_retrieve_page` tool automatically.

3. **Ask Claude to create a page**:
   ```
   Create a new Notion page titled "Meeting Notes" under parent page parent-1234-1234-1234-123456789abc
   ```
   Claude will use the `notion_create_page` tool automatically.

### Using Cursor IDE

Similar to Claude Desktop, you can invoke the tools through natural language prompts in Cursor's AI chat interface.

## Testing

Run the test suite:

```bash
cd week3
poetry run pytest tests/
```

Run specific test files:

```bash
# Test page retrieval
poetry run pytest tests/test_retrieve_page.py

# Test page creation
poetry run pytest tests/test_create_page.py
```

### Test Coverage

The test suite includes:
- Successful page retrieval
- Successful page creation
- Retrieving a newly created page
- Error cases (invalid IDs, network failures, timeouts)
- Rate limiting behavior
- Input validation

## Features

### Error Handling

The server gracefully handles:
- HTTP failures (4xx, 5xx errors)
- Network timeouts
- Empty API responses
- Invalid input parameters

All errors are returned as structured messages to the MCP client without crashing the server.

### Rate Limiting

The server implements rate limiting to respect Notion's API limits:
- Default limit: 3 requests per second
- Automatic backoff on 429 (Too Many Requests) responses
- User-facing warnings when approaching rate limits

### Logging

All logging goes to stderr (required for STDIO servers):
- INFO level: Tool invocations and successful operations
- ERROR level: API errors and failures
- WARNING level: Rate limit warnings

## Troubleshooting

### Server won't start

**Error**: `NOTION_API_KEY environment variable is required`

**Solution**: Make sure you've set the `NOTION_API_KEY` environment variable or added it to your `.env` file.

### "Page not found" errors

**Cause**: The integration doesn't have access to the page, or the page ID is incorrect.

**Solution**:
1. Verify the page ID is correct (you can find it in the page URL)
2. Make sure you've shared the page with your Notion integration
3. Check that the integration has the correct permissions

### Rate limit errors

**Cause**: Too many requests in a short time period.

**Solution**: The server automatically handles rate limits with backoff. If you see frequent rate limit errors, consider reducing the frequency of requests.

### Connection errors

**Cause**: Network issues or Notion API is unavailable.

**Solution**:
1. Check your internet connection
2. Verify the Notion API is operational
3. Check firewall settings if running in a restricted environment

## Project Structure

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP server entrypoint
│   ├── config.py            # Configuration management
│   └── tools/
│       ├── __init__.py
│       ├── notion.py        # Notion API client wrapper
│       └── rate_limiter.py  # Rate limiting logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_retrieve_page.py
│   └── test_create_page.py
└── README.md                # This file
```

## Configuration

Configuration is managed through environment variables and `server/config.py`:

- `NOTION_API_KEY`: Your Notion API integration token (required)
- `HTTP_TIMEOUT`: HTTP request timeout in seconds (default: 30.0)
- `RATE_LIMIT_REQUESTS_PER_SECOND`: Rate limit threshold (default: 3.0)

## License

This project is part of a course assignment.

## References

- [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [Notion API Documentation](https://developers.notion.com/reference)
- [Notion API - Retrieve a Page](https://developers.notion.com/reference/retrieve-a-page)
- [Notion API - Create a Page](https://developers.notion.com/reference/post-page)

