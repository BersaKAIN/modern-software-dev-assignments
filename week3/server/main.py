"""MCP Notion Server - Main entrypoint."""

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from server.config import Config
from server.tools.notion import NotionClient, NotionAPIError
from server.tools.rate_limiter import RateLimiter

# Configure logging to stderr (required for STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Validate configuration on startup
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_second=Config.RATE_LIMIT_REQUESTS_PER_SECOND,
    warning_threshold=Config.RATE_LIMIT_WARNING_THRESHOLD,
)

# Initialize Notion client
notion_client = NotionClient(
    config=Config,
    rate_limiter=rate_limiter,
)

# Create MCP server
app = Server("notion-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="notion_retrieve_page",
            description="Retrieve a Notion page by its ID. Returns the page object with properties, content, and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "The ID of the Notion page to retrieve",
                    }
                },
                "required": ["page_id"],
            },
        ),
        Tool(
            name="notion_create_page",
            description="Create a new page in Notion under a parent page or database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "parent_id": {
                        "type": "string",
                        "description": "The ID of the parent page or database",
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the new page",
                    },
                    "properties": {
                        "type": "object",
                        "description": "Optional additional page properties",
                        "additionalProperties": True,
                    },
                },
                "required": ["parent_id", "title"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls.

    Args:
        name: Name of the tool to call
        arguments: Tool arguments

    Returns:
        List of text content with tool results
    """
    try:
        if name == "notion_retrieve_page":
            page_id = arguments.get("page_id")
            if not page_id:
                return [
                    TextContent(
                        type="text",
                        text="Error: page_id is required",
                    )
                ]

            logger.info(f"Retrieving page: {page_id}")
            page = await notion_client.retrieve_page(page_id)

            # Format response
            response_text = json.dumps(page, indent=2)
            return [
                TextContent(
                    type="text",
                    text=f"Successfully retrieved page:\n\n{response_text}",
                )
            ]

        elif name == "notion_create_page":
            parent_id = arguments.get("parent_id")
            title = arguments.get("title")
            properties = arguments.get("properties")

            if not parent_id:
                return [
                    TextContent(
                        type="text",
                        text="Error: parent_id is required",
                    )
                ]
            if not title:
                return [
                    TextContent(
                        type="text",
                        text="Error: title is required",
                    )
                ]

            logger.info(f"Creating page with title '{title}' under parent {parent_id}")
            page = await notion_client.create_page(
                parent_id=parent_id,
                title=title,
                properties=properties,
            )

            # Format response
            response_text = json.dumps(page, indent=2)
            return [
                TextContent(
                    type="text",
                    text=f"Successfully created page:\n\n{response_text}",
                )
            ]

        else:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'",
                )
            ]

    except NotionAPIError as e:
        logger.error(f"Notion API error: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}",
            )
        ]
    except Exception as e:
        logger.exception(f"Unexpected error in tool '{name}': {e}")
        return [
            TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}",
            )
        ]


async def main():
    """Run the MCP server with STDIO transport."""
    logger.info("Starting MCP Notion Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

