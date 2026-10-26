# Client setup

drop.media's MCP server is a remote server: `https://drop.media/mcp` (Streamable HTTP). Every client below connects to it
directly, with no local proxy and nothing to install. Use OAuth where the client supports it; otherwise send an API key
(see [authentication.md](authentication.md)).

Replace `<API key>` / `DROP_API_KEY` with your own key. Never commit a real one.

## How each configuration was checked

| Client | Configuration | How it was checked |
|---|---|---|
| Claude Code | `claude mcp add --transport http` / `.mcp.json` | Official Claude Code docs. Live tool calls (`list_files`, `create_upload_link`) were made from a Claude Code session connected to `https://drop.media/mcp`. |
| Cursor | `mcp.json` with `url` | Official Cursor docs only (not tested end to end) |
| VS Code | `mcp.json` with `servers` / `"type": "http"` | Official VS Code docs only (not tested end to end) |
| Claude (web, desktop) | Custom connector | Official Claude docs only (not tested end to end) |
| ChatGPT | Custom MCP server | Official OpenAI docs only (not tested end to end) |
| All | OAuth discovery, `401` challenge, `405` on `GET` | Checked against the live server |

Client menus and file formats change often. If something here doesn't match your client, follow its current docs (linked
in each section) and [open an issue](https://github.com/dropdotmedia/docs/issues/new/choose).

---

## Claude Code

Docs: <https://code.claude.com/docs/en/mcp>

### OAuth (recommended)

```bash
claude mcp add --transport http drop https://drop.media/mcp
```

Then, inside Claude Code, run `/mcp`, select `drop` and finish signing in to drop.media in your browser. Tokens are stored
and refreshed by Claude Code. Outside an interactive session, `claude mcp login drop` runs the same sign-in.

Add `--scope user` to make the server available in all your projects, or `--scope project` to write it to the project's
`.mcp.json`.

### API key

```bash
claude mcp add --transport http drop https://drop.media/mcp \
  --header "Authorization: Bearer <API key>"
```

To share the setup with a team without sharing a key, commit a `.mcp.json` at the project root that reads the key
from each developer's environment ([`examples/config/claude-code.mcp.json`](../examples/config/claude-code.mcp.json)):

```json
{
  "mcpServers": {
    "drop": {
      "type": "http",
      "url": "https://drop.media/mcp",
      "headers": {
        "Authorization": "Bearer ${DROP_API_KEY}"
      }
    }
  }
}
```

Claude Code asks for approval before using servers from a project's `.mcp.json`. If you configure an `Authorization`
header and drop.media rejects it, Claude Code reports a failed connection rather than falling back to OAuth. Remove the
header to use OAuth.

Claude Code can run shell commands, so it can use [`create_upload_link`](tools.md#create_upload_link) to upload local
files.

---

## Cursor

Docs: <https://cursor.com/docs/context/mcp>

Add the server to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (this project).

### OAuth (recommended)

```json
{
  "mcpServers": {
    "drop": {
      "url": "https://drop.media/mcp"
    }
  }
}
```

Cursor detects that the server needs sign-in and handles discovery, registration and tokens. Use the server's
login prompt in Cursor's MCP settings to sign in.

### API key

([`examples/config/cursor.mcp.json`](../examples/config/cursor.mcp.json))

```json
{
  "mcpServers": {
    "drop": {
      "url": "https://drop.media/mcp",
      "headers": {
        "Authorization": "Bearer ${env:DROP_API_KEY}"
      }
    }
  }
}
```

Set `DROP_API_KEY` in the environment Cursor is launched from. Avoid writing the literal key into a project
`.cursor/mcp.json` that might be committed.

---

## VS Code (GitHub Copilot agent mode)

Docs: <https://code.visualstudio.com/docs/copilot/customization/mcp-servers> and the
[MCP configuration reference](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration)

Put the configuration in `.vscode/mcp.json` (this workspace) or in your user profile's `mcp.json` (run **MCP: Open User
Configuration** from the Command Palette). You can also run **MCP: Add Server**, choose **HTTP** and enter
`https://drop.media/mcp`. VS Code uses a top-level `servers` key, not `mcpServers`.

### OAuth (recommended)

```json
{
  "servers": {
    "drop": {
      "type": "http",
      "url": "https://drop.media/mcp"
    }
  }
}
```

When the server starts, VS Code asks you to sign in and opens drop.media in your browser.

### API key

VS Code prompts for the key once and stores it securely. Nothing secret goes in the file
([`examples/config/vscode.mcp.json`](../examples/config/vscode.mcp.json)):

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "drop-api-key",
      "description": "drop.media API key",
      "password": true
    }
  ],
  "servers": {
    "drop": {
      "type": "http",
      "url": "https://drop.media/mcp",
      "headers": {
        "Authorization": "Bearer ${input:drop-api-key}"
      }
    }
  }
}
```

---

## Claude (claude.ai and Claude Desktop): custom connector

Docs: <https://claude.com/docs/connectors/custom/remote-mcp>

drop.media isn't listed in Claude's Connectors Directory, so you add it as a **custom connector**. That's different
from installing a reviewed directory listing, and Claude labels it as a connection to an unverified service.

**Free, Pro and Max plans** (Free plans allow one custom connector):

1. Go to **Customize > Connectors** and select **Add custom connector**.
2. For the URL, enter `https://drop.media/mcp`.
3. Authentication: use OAuth (**Sign in now** or **Sign in when needed**). If you're asked how Claude should identify
   itself, choose **Register automatically** (dynamic client registration). drop.media doesn't support Claude's
   "published identity" (Client ID Metadata Document) option. Leave client ID and secret blank.
4. Select **Add**, then **Connect**, and approve access on drop.media.

**Team and Enterprise plans:** an Owner adds the connector under **Organization settings > Connectors** (**Add >
Custom**, type **Web**) with the same URL and settings. Each member then connects it with their own drop.media account
under **Customize > Connectors**.

Without shell access, Claude in the browser can't read files from your computer. It can host files from public URLs,
or content it has as base64, and it can generate images.

---

## ChatGPT: custom MCP server

Docs: <https://developers.openai.com/apps-sdk/deploy/connect-chatgpt>

You can add drop.media to ChatGPT yourself as a custom MCP server. Availability depends on your ChatGPT plan and workspace
policy, and the menu names have changed over time. Follow OpenAI's current page. The steps it describes are:

1. Open the Plugins page (<https://chatgpt.com/plugins>), select **+** and choose **Add custom MCP server**.
2. Give it a name and description, choose a public endpoint and enter `https://drop.media/mcp`.
3. Choose OAuth authentication, review the risk warning and accept it. ChatGPT registers itself with drop.media
   automatically.
4. Create it, then review the tools drop.media reports and sign in to drop.media when prompted.

In ChatGPT, `upload_file` can also take a **file from the conversation** (an image you attached, or one ChatGPT
generated) through its `file` argument, so it doesn't need a URL or base64 content.

A custom server you add yourself is separate from an app published in ChatGPT's directory. This repository doesn't
claim that drop.media has a published ChatGPT directory listing.

---

## Generic remote MCP configuration

For any client that supports remote Streamable HTTP servers, these are the values to use:

| Setting | Value |
|---|---|
| Transport / type | Streamable HTTP (often `"http"` or `"streamable-http"`) |
| URL | `https://drop.media/mcp` |
| Auth (preferred) | OAuth 2.1 with discovery from the `401` response, dynamic client registration and PKCE `S256` |
| Auth (alternative) | Header `Authorization: Bearer <API key>` |

Many clients accept this shape ([`examples/config/generic.mcp.json`](../examples/config/generic.mcp.json)). Check
your client's documentation for its exact key names:

```json
{
  "mcpServers": {
    "drop": {
      "url": "https://drop.media/mcp",
      "headers": {
        "Authorization": "Bearer <API key>"
      }
    }
  }
}
```

**Clients that only support local (stdio) servers** can't connect natively. This repository doesn't recommend a
particular bridge. If you use one, its OAuth and secret handling is your responsibility.

### Checking the connection without a client

These requests don't change anything. The first needs no credentials; the second lists the tools your key can see:

```bash
# Should print a 401 status and a WWW-Authenticate header pointing to the OAuth metadata
curl -si -X POST https://drop.media/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | head -n 12

# With an API key: lists the tools this key's abilities allow
curl -s https://drop.media/mcp \
  -H "Authorization: Bearer $DROP_API_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Normal MCP clients send `initialize` first; these `curl` requests are only for a quick check.
