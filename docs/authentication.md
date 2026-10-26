# Authentication

drop.media's MCP server at `https://drop.media/mcp` accepts two kinds of credential:

| | OAuth 2.1 | API key |
|---|---|---|
| Best for | Apps and IDEs that support MCP OAuth: Claude, ChatGPT, Claude Code, Cursor, VS Code | Clients without OAuth, scripts, CI, headless agents |
| Setup | Add the URL, then sign in and approve in the browser | Create a key, then put it in a header |
| Lifetime | 1-hour access token, refreshed automatically (refresh token valid for 90 days, rotated on each use) | Until revoked |
| Sent as | `Authorization: Bearer <access token>` (handled by the client) | `Authorization: Bearer <API key>` |

Both are checked the same way, and both are subject to the same scopes and subscription requirement.

## 1. Account and subscription

1. Create an account at <https://drop.media/register>.
2. Subscribe. The MCP server, API keys, REST API and CLI need an active subscription; see
   [pricing](https://drop.media/pricing).

Without an active subscription, `/mcp` responds with HTTP `402` and the message *"This drop.media account does not have an
active subscription, which the MCP server requires."* The OAuth consent page also won't let you approve a connection.

## 2. Scopes

drop.media's scopes are also called API key "abilities". The names are the same for OAuth and API keys.

| Scope | Allows | Tools |
|---|---|---|
| `files:read` | List and read files | `list_files`, `get_file`, `share_file` |
| `files:write` | Upload files and create share links | `upload_file`, `create_upload_link` |
| `files:delete` | Delete files | `delete_file` |
| `images:generate` | Generate images with AI | `generate_image` |

**Tools you don't have the scope for are hidden.** `tools/list` returns only the tools your credential allows. A
read-only key sees just `list_files`, `get_file`, `share_file` and `send_feedback`, which every credential gets. Each tool also declares its required scope in
`securitySchemes`, so OAuth clients can request the right one.

Grant the least you need. For example, an agent that only posts screenshots needs `files:write`. Add `files:read`
if it should also find earlier uploads, and leave `files:delete` off unless the agent should be able to remove files.

## 3. OAuth

OAuth-capable clients discover everything themselves. You add the URL and sign in.

What happens:

1. The client calls `/mcp` without a token and gets `401` with
   `WWW-Authenticate: Bearer realm="mcp", resource_metadata="https://drop.media/.well-known/oauth-protected-resource/mcp"`.
2. It reads the [protected resource metadata](https://drop.media/.well-known/oauth-protected-resource/mcp) (RFC 9728) and
   the [authorization server metadata](https://drop.media/.well-known/oauth-authorization-server) (RFC 8414).
3. It registers itself at `POST https://drop.media/oauth/register` (dynamic client registration, RFC 7591). Redirect URIs
   must use `https`, except `http` on `localhost`, `127.0.0.1` or `[::1]`.
4. Your browser opens `https://drop.media/oauth/authorize`. Sign in to drop.media, review the app name and requested
   scopes, then choose **Allow** or deny.
5. The client exchanges the code at `POST https://drop.media/oauth/token` (authorization code with PKCE `S256`) and refreshes
   tokens with the `refresh_token` grant.

Details that affect client setup:

- **Supported:** authorization code with PKCE (`S256` only), refresh tokens, dynamic client registration, the `iss`
  authorization response parameter (RFC 9207) and the `resource` parameter (RFC 8707; it must be `https://drop.media/mcp`).
- **Not supported:** OAuth Client ID Metadata Documents, pre-registered client IDs issued by drop.media, client
  credentials and device code grants. In clients that ask how to identify themselves (for example Claude's **OAuth client**
  setting), choose dynamic registration ("Register automatically").
- **Scopes requested:** if a client doesn't request a scope, it's granted all four. The consent page shows exactly what
  will be granted. You can approve or deny the request, but you can't pick individual scopes on that page. To limit an
  integration, use an API key with fewer abilities.
- **Where connections appear:** each OAuth access token is an API key named after the app. It appears under **Agents &
  API** with the scopes you granted.

## 4. API keys

1. Sign in and open **Agents & API** at <https://drop.media/developers>.
2. Enter a key name that describes where it will be used (for example "Claude Code on my laptop"; up to 60 characters).
3. Select the abilities this key needs.
4. Select **Create API key** and copy the key. It's shown **once**, so store it in a password manager or secret store
   straight away.

Send it on every request:

```http
Authorization: Bearer <API key>
```

The same key works for the [REST API](https://drop.media/llms.txt) and the
[`drop` CLI](https://www.npmjs.com/package/drop-media).

## 5. Revoking access

- **API key:** under **Agents & API**, select **Revoke** next to the key. Anything using it stops working, including
  upload links that were created with it and haven't been used yet.
- **OAuth connection:** revoke the app's entry under **Agents & API**. This also invalidates its refresh token, so the
  app must ask you to approve it again. You can also disconnect in the client (for example, **Clear authentication** in
  Claude Code's `/mcp` menu, or `claude mcp logout <name>`). That clears the client's stored tokens. To be sure the
  credentials are invalidated, also revoke them on drop.media.

Revoke immediately if a key may have leaked (for example in a commit, a log, a screenshot or a shared transcript), then
create a new one.

## 6. Storing credentials safely

- Use OAuth where your client supports it, so there's no long-lived secret to store.
- Never commit an API key. Use your client's secret mechanism instead of pasting the key into a shared config file:
  - Claude Code `.mcp.json`: `"Authorization": "Bearer ${DROP_API_KEY}"` (environment variable expansion)
  - Cursor `mcp.json`: `"Authorization": "Bearer ${env:DROP_API_KEY}"`
  - VS Code `mcp.json`: an `inputs` entry with `"password": true`, referenced as `${input:drop-api-key}`

  The exact syntax for each client is in [clients.md](clients.md).
- If a project config with a key reference is committed, the variable *name* is shared but the key isn't. Each developer
  sets their own `DROP_API_KEY`.
- Note that `claude mcp add ... --header "Authorization: Bearer $DROP_API_KEY"` expands the variable in your shell, so the
  key itself ends up in Claude Code's local config file (`~/.claude.json`). That's fine on your own machine. For shared
  projects, use `.mcp.json` with `${DROP_API_KEY}`.
- Give each agent or machine its own key, so you can revoke one without breaking the others.
- Upload links (`upload_url`) are credentials too. Anyone who has the link can upload one file to your account until it
  expires (15 minutes). Don't post them.
- Signed private-file links give anyone who has them access to the file until they expire. Keep their `ttl` short.

All examples in this repository use placeholders such as `<API key>` and `DROP_API_KEY`. They never contain real values.
