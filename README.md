[![dropmedia](https://cdn.drop.media/dropmedia/drop-github-readme-banner-paper.png)](https://cdn.drop.media/dropmedia/drop-github-readme-banner-paper.png)


# drop.media MCP

**Upload once. Find, use and share across your AI workflows.**

drop.media is one media library for you and all your AI agents. Files added in Claude, ChatGPT, Cursor, the terminal or
the website land in the same library, where every other agent you connect can find them, use them and share a link.

[drop.media](https://drop.media) runs a remote [Model Context Protocol](https://modelcontextprotocol.io) server at
`https://drop.media/mcp`. Once it's connected, your agent can host a screenshot, chart, PDF, recording or generated
image and get back a URL and a ready-made Markdown snippet to paste into a pull request, issue, document or chat message.

> [!NOTE]
> drop.media is a hosted commercial service, hosted by drop.media. You need a drop.media account with a verified email
> address to connect: the free plan includes the media library, the MCP server, the REST API and the CLI, and a
> subscription adds bigger files, permanent links, more storage and image generation. This repository holds documentation and example configuration only. It does
> **not** contain a server you can run yourself. See [current pricing](https://drop.media/pricing).

## Quick start

**Claude Code**: add the server, then sign in from inside Claude Code:

```bash
claude mcp add --transport http drop https://drop.media/mcp
```

Then run `/mcp` in Claude Code, choose `drop` and complete the sign-in in your browser.

**Any other client that supports remote MCP servers with OAuth**: add `https://drop.media/mcp` as a remote
(Streamable HTTP) server and sign in when prompted. If your client can't use OAuth, use an API key instead
(see [Authentication](docs/authentication.md)).

Setup for Cursor, VS Code, Claude (web and desktop) and ChatGPT is in [docs/clients.md](docs/clients.md).

## What agents use it for

- **Screenshots in pull requests.** An agent with shell access asks for an upload link, sends the PNG with `curl`, and
  puts the returned Markdown image into the PR description.
- **Hosting a file that's already online.** Pass a public URL and drop.media downloads and hosts its own copy.
- **Sharing a sensitive report.** Upload it as `private` and hand out a signed link that stops working after a set time
  (up to 7 days).
- **Short-lived files.** Set `expires_in` (for example `7d`) and the file deletes itself.
- **Generated images.** Create an image from a text prompt and host it in one step. The prompt and model are saved
  with the file.
- **Finding files from anywhere.** Everything you or any connected agent uploads lands in one library. Ask for "the Q3
  revenue chart" and `list_files` finds `q3-revenue.png`, whichever client or person uploaded it.
- **Library housekeeping.** Look up and delete files you uploaded earlier.

## Endpoint and transport

| | |
|---|---|
| URL | `https://drop.media/mcp` |
| Transport | Streamable HTTP (JSON-RPC over `POST`). `GET` returns `405`, and there's no separate SSE endpoint. |
| Authentication | OAuth 2.1 (with discovery and dynamic client registration) **or** `Authorization: Bearer <API key>` |
| Server name / version | `drop.media` / `1.0.0` (as reported in `initialize`) |

An unauthenticated request gets `401` with a `WWW-Authenticate` header that points to
`https://drop.media/.well-known/oauth-protected-resource/mcp`. OAuth-capable clients use this to start sign-in
automatically.

## Authentication in brief

- **OAuth (recommended for apps and IDEs).** The client registers itself, opens a drop.media consent page and receives
  short-lived tokens that refresh automatically. There are no keys to copy.
- **API keys.** Create a key under **Agents & API** at <https://drop.media/developers>, choose its abilities and send it as
  `Authorization: Bearer <API key>`.

Both use the same four scopes (also called abilities): `files:read`, `files:write`, `files:delete` and `images:generate`.
**The server only lists the tools your credential allows.** Details: [docs/authentication.md](docs/authentication.md).

## Tools

| Tool | What it does | Scope | Changes data |
|---|---|---|---|
| [`upload_file`](docs/tools.md#upload_file) | Host a file sent as a URL, as base64 or (in ChatGPT) as a conversation file | `files:write` | Creates a file |
| [`create_upload_link`](docs/tools.md#create_upload_link) | Get a one-time URL that a shell client sends a file to with `curl -T` | `files:write` | Creates an upload link |
| [`list_files`](docs/tools.md#list_files) | List or search your files, newest first | `files:read` | No |
| [`get_file`](docs/tools.md#get_file) | Get one file's details and URL | `files:read` | No |
| [`share_file`](docs/tools.md#share_file) | Get a link: a signed, expiring link for private files, or the permanent URL for public ones | `files:read` | No |
| [`delete_file`](docs/tools.md#delete_file) | Delete a file permanently | `files:delete` | **Deletes** |
| [`generate_image`](docs/tools.md#generate_image) | Generate an image from a prompt and host it | `images:generate` | Creates a file |

Full arguments, responses and errors: [docs/tools.md](docs/tools.md). Worked examples: [docs/examples.md](docs/examples.md).

> [!IMPORTANT]
> Connecting the MCP server doesn't give the server access to your computer. drop.media can't read files on your disk.
> To upload a local file, the *client* must be able to read it and make an HTTP request, for example an agent that can run
> `curl`. Agents without file or shell access can only host files from public URLs, base64 content they already have,
> or (in ChatGPT) files attached to the conversation. See
> [the upload-link workflow](docs/tools.md#the-upload-link-workflow).

## Files, links and expiry

| | Public (default) | Private |
|---|---|---|
| URL | Permanent CDN URL: `https://cdn.drop.media/<prefix>/<name>.<ext>` | Signed `https://drop.media/p/...` link |
| Who can open it | Anyone with the URL | Anyone with an unexpired signed link |
| Link lifetime | Until the file is deleted or expires | 1 hour by default, up to 7 days (`share_file` `ttl`), and never longer than the file itself |

- **Expiry.** Any file can be given `expires_in` (for example `30m`, `1h`, `7d` or `2w`; at least one minute and at most
  365 days). Once a file expires, the tools stop returning it and signed links return `410`. Expired files are then removed
  automatically.
- **Deletion.** `delete_file` removes the file and its thumbnail. Signed links stop working straight away. Public CDN
  URLs can take a few minutes to stop working while caches clear.
- **Custom names.** `name` sets the URL slug (letters, numbers, `-` and `_`, up to 100 characters). Names are unique
  across drop.media, so a common name may already be taken.
- **Supported types (up to 100 MB).** Images (PNG, JPG, GIF, WebP, SVG, AVIF, HEIC), PDF, video (MP4, MOV, WebM), audio
  (MP3, WAV, M4A), text (TXT, MD, CSV, JSON, LOG) and Office files (DOCX, XLSX, PPTX).

By default a public URL contains a random UUID, so it's hard to guess but works for anyone who has it. A custom `name` makes it
easier to guess. Use `private` for anything you wouldn't post publicly.

## Documentation

- [Authentication](docs/authentication.md): accounts, OAuth, API keys, scopes and revocation
- [Client setup](docs/clients.md): Claude Code, Cursor, VS Code, Claude, ChatGPT and generic configuration
- [Tools reference](docs/tools.md): every argument, response and error
- [Examples](docs/examples.md): end-to-end workflows
- [Troubleshooting](docs/troubleshooting.md)
- [Directory metadata](docs/directory.md): descriptions, topics and MCP Registry notes

## Other ways in

drop.media also has a REST API (`https://drop.media/api/v1`) and a CLI
([`drop-media` on npm](https://www.npmjs.com/package/drop-media)). Both use the same API keys. A summary for LLMs
is at <https://drop.media/llms.txt>.

## Support, security and contributing

- Problems with an integration or these docs: [open an issue](https://github.com/dropdotmedia/docs/issues/new/choose).
  Don't include API keys, tokens or private file links.
- Account and billing questions: <https://drop.media/contact>.
- Security reports: see [SECURITY.md](SECURITY.md). Don't open a public issue.
- Contributions: see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The documentation is licensed under [CC BY 4.0](LICENSES/CC-BY-4.0.txt), and the standalone example code in
[`examples/`](examples) and [`scripts/`](scripts) is licensed under [MIT](LICENSES/MIT.txt). See [LICENSE.md](LICENSE.md)
for details. Neither licence grants any rights to drop.media's application, hosted service, name or logo.
