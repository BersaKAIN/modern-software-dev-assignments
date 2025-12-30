# Project Roadmap & Context

## 🧠 Technical Context (DO NOT IGNORE)
- **Rule:** Prefer clean and concise code.

Design and implement a Model Context Protocol (MCP) server that wraps a real external API.

## API Documentation (You need to fetch contents from the URL)
1. Retrieve a page: https://developers.notion.com/reference/retrieve-a-page

2. Create a page: https://developers.notion.com/reference/post-page

## Requirement
For each of the MCP tools
1. Implement basic resilience:
   - Graceful errors for HTTP failures, timeouts, and empty results.
   - Respect API rate limits (e.g., simple backoff or user-facing warning).
2. Packaging and docs:
   - Provide clear setup instructions, environment variables, and run commands.
   - Include an example invocation flow (what to type/click in the client to trigger the tools).
3. Choose one deployment mode:
   - Local: STDIO server, runnable from your machine and discoverable by Claude Desktop or an AI IDE like Cursor.
   - Remote: HTTP server accessible over the network, callable by an MCP-aware client or an agent runtime. Extra credit if deployed and reachable.
4. (Optional) Bonus: Authentication
   - API key support via environment variable and client configuration; or
   - OAuth2-style bearer tokens for HTTP transport, validating token audience and never passing tokens through to upstream APIs.

## Testing
### Page Retrieval
- [] Write a test that can get a page that's identified by it's page id.

### Page Creation
- [] Write a test that can create a dummy page.
- [] Write a test that can retrieve the dummy page just created.
