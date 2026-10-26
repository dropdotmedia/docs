# Directory metadata

Text and metadata for GitHub and MCP directories. Keep it in sync with the [README](../README.md) and
[`server.json`](../server.json). drop.media is published in the
[official MCP Registry](https://registry.modelcontextprotocol.io) as `media.drop/mcp`. That doesn't mean it's listed
in, approved by or verified by any other directory.

## GitHub repository

**Description** (no more than 350 characters):

> Docs and example configs for drop.media's hosted MCP server: let AI agents upload files and get back links (public CDN URLs or expiring private links). OAuth or API key. Not a self-hostable server.

**Website:** `https://drop.media`

**Topics:**
`mcp`, `model-context-protocol`, `mcp-server`, `remote-mcp`, `ai-agents`, `file-hosting`, `file-upload`, `image-hosting`,
`claude`, `cursor`, `vscode`, `chatgpt`, `oauth2`, `documentation`

## Directory submission text

**Name:** drop.media

**Short description** (95 characters, the same as `server.json`):

> One media library for all your AI agents: upload once, then find, use and share files anywhere.

**Longer description:**

> Upload once. Find, use and share across your AI workflows. drop.media is one media library shared by all your AI
> agents: files added in one client (or on the website, the CLI or the API) can be found with list_files and reused in
> every other. Agents upload screenshots, charts, PDFs, recordings and other
> files, or generate images from a prompt, and get back a URL and a ready-made Markdown snippet for pull requests,
> issues, documents and chat. Public files get a permanent CDN URL. Private files are only reachable through signed links
> that expire within 7 days, and any file can be set to delete itself. Seven tools: upload_file, create_upload_link,
> list_files, get_file, share_file, delete_file and generate_image. A remote Streamable HTTP server hosted by drop.media
> at https://drop.media/mcp, with OAuth 2.1 (dynamic client registration) or API-key authentication. Requires a
> drop.media subscription.

**Facts directories usually ask for:**

| | |
|---|---|
| Endpoint | `https://drop.media/mcp` |
| Transport | Streamable HTTP |
| Authentication | OAuth 2.1 (PKCE S256, dynamic client registration) or `Authorization: Bearer <API key>` |
| Hosting | Hosted by drop.media; there's no local package and no self-hosted option |
| Pricing | Paid subscription required: <https://drop.media/pricing> |
| Docs | <https://github.com/dropdotmedia/docs> |
| Support | <https://drop.media/contact> |
| Privacy / terms | <https://drop.media/privacy> / <https://drop.media/terms> |
| Icon | <https://drop.media/images/brand/icon-512.png> (512×512 PNG), <https://drop.media/images/brand/mark.svg> |

## Official MCP Registry (`server.json`)

[`server.json`](../server.json) describes the hosted server for the
[official MCP Registry](https://registry.modelcontextprotocol.io). It follows the `2025-12-11` schema and only uses
`remotes`, the registry's form for hosted servers. There are no `packages`, because there's nothing to install.
It passes validation against that schema.

Choices worth knowing about:

- **`name: media.drop/mcp`** is the reverse-DNS form of `drop.media`. The registry accepted it after HTTP domain
  verification: drop.media serves the public key at `https://drop.media/.well-known/mcp-registry-auth`.
- **No `repository`.** That field is for the server's source code, which is private. This docs repository isn't the
  server's source.
- **No `headers`.** OAuth-capable clients discover authentication from the server's `401` response. API keys are documented
  in [authentication.md](authentication.md) rather than declared as a required header.
- **`version: 1.0.0`** matches the version the server reports in `initialize`. Bump both together when tools change in
  a way directory users should know about.

### Publishing

`media.drop/mcp` version `1.0.0` was published on 2026-10-26 and is listed at
`https://registry.modelcontextprotocol.io/v0.1/servers?search=media.drop/mcp`.

To publish a new version:

1. Bump `version` here and in the server's `initialize` response.
2. Install `mcp-publisher` (`brew install mcp-publisher` or a release binary; see the registry's
   [publishing guide](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx)).
3. Run `mcp-publisher login http --domain drop.media --private-key <private key>`. The key is the ed25519 private
   key for the public key drop.media serves at `/.well-known/mcp-registry-auth` (set as `MCP_REGISTRY_AUTH` in the
   app, with a default in `config/drop.php`). Keep the private key out of this repository. If it's lost, generate a
   new pair and serve the new public key; see the registry's
   [authentication guide](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/authentication.mdx).
4. Run `mcp-publisher publish` from this directory.

The registry doesn't check that the remote URL belongs to the namespace owner, and each remote URL can only be
registered under one name.

The registry is in preview and its schema changes. Check the current schema version before publishing. Registry
acceptance doesn't mean listing in any downstream directory (for example Claude's Connectors Directory or ChatGPT's
plugin directory). Each of those has its own submission and review.
