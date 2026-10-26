# Examples

Each workflow shows what you might ask, the tool calls the agent makes, and what comes back. Tool arguments follow the
[tools reference](tools.md). Responses are shortened.

Before you host anything, check what's in it. Public files are visible to anyone who has the URL. Screenshots, logs and
exports often contain tokens, email addresses or customer data. Use `"visibility": "private"` when in doubt.

- [1. Upload a local file with an upload link](#1-upload-a-local-file-with-an-upload-link)
- [2. Host a file that's already online](#2-host-a-file-thats-already-online)
- [3. Generate and host an image](#3-generate-and-host-an-image)
- [4. Share a private report with an expiring link](#4-share-a-private-report-with-an-expiring-link)
- [5. Find a file, then delete it](#5-find-a-file-then-delete-it)
- [6. Without MCP: upload from a script or CI job](#6-without-mcp-upload-from-a-script-or-ci-job)

---

## 1. Upload a local file with an upload link

**Needs:** an agent that can read the file and run `curl` (for example Claude Code, or Cursor or VS Code in agent
mode with terminal access) · scope `files:write`

> "Add the screenshot at `./artifacts/settings-page.png` to the PR description."

**Step 1: the agent asks for a link.**

```json
{
  "tool": "create_upload_link",
  "arguments": { "filename": "settings-page.png", "expires_in": "90d" }
}
```

Response (structured content):

```json
{
  "upload_url": "https://drop.media/api/v1/uploads/<one-time-token>",
  "method": "PUT",
  "max_bytes": 104857600,
  "expires_at": "2026-10-26T09:45:00+00:00",
  "curl": "curl --fail-with-body -T 'settings-page.png' 'https://drop.media/api/v1/uploads/<one-time-token>'"
}
```

**Step 2: the agent sends the bytes.** This step runs in the agent's shell, not in drop.media. It uses the real path:

```bash
curl --fail-with-body -T ./artifacts/settings-page.png 'https://drop.media/api/v1/uploads/<one-time-token>'
```

```json
{
  "data": {
    "id": "0c7e5b1d-...",
    "url": "https://cdn.drop.media/your-prefix/0c7e5b1d-....png",
    "markdown": "![settings-page](https://cdn.drop.media/your-prefix/0c7e5b1d-....png)",
    "visibility": "public",
    "expires_at": "2027-01-24T09:30:00+00:00"
  }
}
```

**Step 3:** the agent pastes `data.markdown` into the PR description.

If the connection drops, run the same `curl` again: the same bytes return the file already stored. Or send a `GET` to the
link to see whether the upload finished. After 15 minutes the link expires; ask for a new one.

---

## 2. Host a file that's already online

**Needs:** any MCP client · scope `files:write`

> "Make a stable copy of https://drop.media/images/brand/icon-512.png that deletes itself in a week."

```json
{
  "tool": "upload_file",
  "arguments": {
    "url": "https://drop.media/images/brand/icon-512.png",
    "expires_in": "7d"
  }
}
```

Text result:

```text
Uploaded.
URL: https://cdn.drop.media/your-prefix/<id>.png
```

drop.media downloads the file from the public internet, so the URL must be publicly reachable. It can't fetch
intranet, `localhost` or private-network URLs, or pages behind a login.

---

## 3. Generate and host an image

**Needs:** scope `images:generate` · counts towards the daily generation limit

> "Generate a landscape hero image for the docs homepage: an isometric data pipeline in soft pastels."

```json
{
  "tool": "generate_image",
  "arguments": {
    "prompt": "Isometric illustration of a data pipeline, soft pastel palette, white background, no text",
    "size": "1536x1024"
  }
}
```

Text result:

```text
Generated with <model>. <n> generation(s) left today.
URL: https://cdn.drop.media/your-prefix/<id>.png
```

The structured content includes `markdown`, the `prompt` and the `model`. Generation takes 10–60 seconds, and every call
creates a new file, so don't retry a call that's still running.

---

## 4. Share a private report with an expiring link

**Needs:** scopes `files:write` and `files:read` · an agent with shell access (for a local file)

> "Upload `q3-report.pdf` privately, keep it for 30 days, and give me a link for the finance team that works for 2 days."

**Upload it as private:**

```json
{
  "tool": "create_upload_link",
  "arguments": {
    "filename": "q3-report.pdf",
    "visibility": "private",
    "expires_in": "30d"
  }
}
```

```bash
curl --fail-with-body -T ./q3-report.pdf '<upload_url>'
```

The response's `data.id` is a random UUID. Use a random id for sensitive files rather than a guessable `name`.

**Create the link to share:**

```json
{
  "tool": "share_file",
  "arguments": { "id": "<id from the upload>", "ttl": "2d" }
}
```

```text
Link (works until 2026-10-28T09:30:00+00:00): https://drop.media/p/<id>?expires=...&ref=...&signature=...
```

- Anyone who has this link can open the file until it expires, so send it only to the people who need it.
- A link lasts at most 7 days, and never longer than the file. Call `share_file` again for a new one.
- To cut off access early, delete the file (example 5).

---

## 5. Find a file, then delete it

**Needs:** scope `files:read` to find, `files:delete` to delete

> "Delete the old onboarding screenshots I uploaded last month."

**Find candidates:**

```json
{ "tool": "list_files", "arguments": { "search": "onboarding", "type": "images", "per_page": 20 } }
```

```text
Showing 2 of 2 file(s), page 1:
- onboarding-step-1 (image/png, 2026-09-14) https://cdn.drop.media/your-prefix/onboarding-step-1.png
- onboarding-step-2 (image/png, 2026-09-14) https://cdn.drop.media/your-prefix/onboarding-step-2.png
```

**Confirm with the user, then delete each one by its exact id:**

```json
{ "tool": "delete_file", "arguments": { "id": "onboarding-step-1" } }
```

```text
Deleted onboarding-step-1.
```

Deletion is permanent. Public CDN URLs can keep working for a few minutes while caches clear. Search matches every word
anywhere in names and prompts, so check every result before deleting it.

---

## 6. Without MCP: upload from a script or CI job

The same upload-link flow is available over the REST API, which is useful when no agent is involved.
[`examples/upload-with-link.sh`](../examples/upload-with-link.sh) does it in one command:

```bash
export DROP_API_KEY='<API key with files:write>'
./examples/upload-with-link.sh ./artifacts/settings-page.png --private --expires 7d
```

It calls `POST https://drop.media/api/v1/uploads`, sends the file with `curl -T`, and prints the response's
`data` JSON (the file object). In CI, store the key as a masked secret. Note that public uploads from a public repository's
CI are visible to everyone.
