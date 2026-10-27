# Troubleshooting

When you report a problem, include the client name and version, which authentication you used (OAuth or API key),
the tool name and the error text. **Remove** API keys, tokens, upload links and signed private-file links first.

## Connection and authentication

### `401 Unauthenticated`

Either no credential was sent or it isn't valid.

- **OAuth clients:** start sign-in again (Claude Code: `/mcp`, then select `drop`; other clients: their reconnect or
  sign-in action). If you revoked the connection under **Agents & API**, the client must ask you to approve it again.
- **API key:** check the header is exactly `Authorization: Bearer <API key>` (one space, no quotes around the key) and
  that the key hasn't been revoked. If the key comes from an environment variable, make sure that variable is set in the
  environment the *client* starts in, not just in your shell.
- Claude Code: if a configured `Authorization` header is rejected, Claude Code doesn't fall back to OAuth. Remove the
  header, or fix the key.

### `402` / "Verify the email address" or "does not have an active subscription"

The MCP server needs a verified email address (for the free plan) or an active subscription. Follow the link in the
message to verify, or check your plan at <https://drop.media/billing>. The OAuth consent page also refuses to connect
accounts without either.

### The sign-in page won't complete

- Sign in to drop.media in the browser window the client opened, then approve.
- *"This app is not registered with drop.media"*: the client's registration is stale. Remove the server and add it again.
- *"The redirect URI does not match..."* or `invalid_redirect_uri`: the client is using a redirect URI it didn't
  register. drop.media only accepts `https` redirect URIs, or `http` on `localhost`, `127.0.0.1` or `[::1]`.
- Claude's custom connector: choose **Register automatically** (dynamic client registration). drop.media doesn't support
  the Client ID Metadata Document ("published identity") option, or pre-issued client IDs.
- `invalid_target`: the client sent a `resource` other than `https://drop.media/mcp`. Check the URL has no extra path
  or trailing characters.

### "Unsupported transport", or the connection fails immediately

- drop.media uses **Streamable HTTP** at `https://drop.media/mcp`. There's no SSE endpoint, and `GET /mcp` returns `405`.
  If your client asks for a transport, choose HTTP / Streamable HTTP, not SSE.
- Clients that only support local (stdio) servers can't connect natively. See
  [clients.md](clients.md#generic-remote-mcp-configuration).
- Make sure you're using `https://drop.media/mcp`, not `https://drop.media` or a `/sse` path.

### Too many requests (`429`)

`/mcp` allows 120 requests per minute per account. Upload links allow 30 `PUT`s and 60 status `GET`s per minute. Wait
and retry.

## Missing tools or scopes

### A tool doesn't appear

`tools/list` only includes the tools your credential's scopes allow:

| Missing tool | Scope needed |
|---|---|
| `upload_file`, `create_upload_link` | `files:write` |
| `list_files`, `get_file`, `share_file` | `files:read` |
| `delete_file` | `files:delete` |
| `generate_image` | `images:generate` |
| `send_feedback` | none; every credential sees it |

API key abilities can't be changed after the key is created. Create a new key with the right abilities, update your
client and revoke the old one. For OAuth, revoke the connection and connect again. Some clients also cache the tool list
until you reconnect or restart them.

### `This API key doesn't have the "<scope>" ability.`

A tool was called without its scope (for example, from a client that cached an old tool list). Fix as above.

## Uploading files

### The agent says it can't upload a local file

An MCP connection lets the agent call drop.media's tools. It **doesn't** give drop.media or the agent access to your
files. A local upload needs a client that can read the file and make an HTTP request:

- **Agent with a shell** (Claude Code, IDE agents with terminal access): `create_upload_link`, then `curl -T`.
- **Chat apps without file system access:** use `upload_file` with a public `url`. In ChatGPT, attach the file to the
  conversation, and `upload_file` can take it through its `file` argument. Small files can also be sent as
  `content_base64`, but large base64 payloads use up the model's context and are slow.
- Or upload it yourself in the browser at <https://drop.media>, or with the [`drop` CLI](https://www.npmjs.com/package/drop-media).

### Upload link errors

| Symptom | Fix |
|---|---|
| `404` "This upload link is invalid or has expired." | Links last 15 minutes and stop working if the API key that created them is revoked or the subscription lapses. Ask for a new link. |
| `409` "already receiving a file" | Another upload is in progress on this link. Wait, then `GET` the link to check. |
| `409` "already used for a different file" | Each link takes one file. Ask for a new link for each file. |
| `422` "Files can be at most 100MB." | Make the file smaller (compress it, trim it or lower the resolution). |
| `422` "Unsupported file type..." | Check the `filename` extension you passed to `create_upload_link` is supported **and** matches the real content. A `.png` that's actually a JPEG is rejected. |
| `422` "The name ... is already taken." | Names are unique across drop.media. Choose another, or leave it out. |
| `curl` uploads an empty file or the wrong file | `-T` takes the path to the file on the machine running `curl`. Run it from the right directory, or use an absolute path. |

### `upload_file` with a `url` fails

- *"That URL points to a private or reserved address."*: drop.media only fetches public internet addresses. It can't
  fetch `localhost`, private networks or internal hostnames.
- *"Downloading that URL failed with HTTP 403/404"*: the URL needs a login or doesn't exist. Download the file another
  way and upload it with an upload link.
- *"Could not download the file at that URL."*: a timeout (20 seconds) or connection error. *"That URL redirected too
  many times."*: there were more than 3 redirects.
- *"Unsupported file type..."*: the URL may return an HTML page rather than the file itself. Use the direct file URL.

## Links and expiry

### A private link stopped working

Signed links expire (1 hour by default, `ttl` up to 7 days) and never last longer than the file. An expired link
returns an error. Use `share_file` to get a new one. A link to a file that has expired or been deleted can't be renewed.

### A file disappeared

Files uploaded with `expires_in` are deleted automatically once they expire; signed links to them return `410`, and the
tools report `No file with id ...`. Check `expires_at` in the file object. To keep a file, upload it without `expires_in`.

### A deleted public file still loads

CDN caches can keep serving a deleted public file for a few minutes.

## Image generation

- *"You have reached today's image generation limit."*: the limit resets at midnight UTC.
- *"The image generator rejected that prompt: ..."*: rephrase the prompt.
- *"busy"*, *"could not be reached"* or *"failed"*: a temporary upstream problem. Try again later.
- Calls take 10–60 seconds. If your client times out sooner, raise its tool timeout. Each completed call stores a new
  image, so check `list_files` with `type: "generated"` before you retry.

## Still stuck?

- Integration or documentation problems: [open an issue](https://github.com/dropdotmedia/docs/issues/new/choose).
- Account or billing: <https://drop.media/contact>.
- Security issues: [SECURITY.md](../SECURITY.md).
