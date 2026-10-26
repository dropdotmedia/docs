# Examples

Standalone example code and configuration for connecting to drop.media's hosted MCP server. Licensed under
[MIT](../LICENSES/MIT.txt).

| File | |
|---|---|
| [`config/claude-code.mcp.json`](config/claude-code.mcp.json) | Claude Code project `.mcp.json`, with the API key read from `DROP_API_KEY` |
| [`config/cursor.mcp.json`](config/cursor.mcp.json) | Cursor `mcp.json`, with the API key read from `DROP_API_KEY` |
| [`config/vscode.mcp.json`](config/vscode.mcp.json) | VS Code `mcp.json`, which prompts for the key once and stores it securely |
| [`config/generic.mcp.json`](config/generic.mcp.json) | The common `mcpServers` shape for other clients; replace the placeholder |
| [`upload-with-link.sh`](upload-with-link.sh) | Upload a local file through a one-time upload link with the REST API (bash, curl, python3) |

These API-key configurations are for clients that can't use OAuth. With OAuth, configure just the URL; see
[docs/clients.md](../docs/clients.md).
