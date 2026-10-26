# Tools reference

drop.media's MCP server (`https://drop.media/mcp`, server name `drop.media`, version `1.0.0`) exposes seven tools.
`tools/list` returns only the tools your credential's scopes allow (see [authentication.md](authentication.md#2-scopes)).

| Tool | Scope | `readOnlyHint` | `destructiveHint` | `openWorldHint` |
|---|---|---|---|---|
| [`upload_file`](#upload_file) | `files:write` | false | false | true |
| [`create_upload_link`](#create_upload_link) | `files:write` | false | false | false |
| [`list_files`](#list_files) | `files:read` | true | false | false |
| [`get_file`](#get_file) | `files:read` | true | false | false |
| [`share_file`](#share_file) | `files:read` | true | false | false |
| [`delete_file`](#delete_file) | `files:delete` | false | **true** | false |
| [`generate_image`](#generate_image) | `images:generate` | false | false | true |

Each tool also declares `securitySchemes: [{"type": "oauth2", "scopes": ["<scope>"]}]`, which is mirrored in `_meta`.

## Response format

Successful calls return a short **text** summary for the model and, except for `delete_file`, **structured content**
(JSON). Tools that return a file use the [file object](#the-file-object) below.

Expected failures (bad input, unknown id, file too large, daily limit reached and so on) come back as a normal tool result
with `isError: true` and a message the agent can read and act on. They aren't protocol errors. Authentication problems
happen before any tool runs, as HTTP `401` (no or invalid credential) or `402` (email address not verified, or no active plan).

### The file object

```json
{
  "id": "4b0f6c1e-2d3a-4e5f-9a8b-7c6d5e4f3a2b",
  "url": "https://cdn.drop.media/your-prefix/4b0f6c1e-2d3a-4e5f-9a8b-7c6d5e4f3a2b.png",
  "url_expires_at": null,
  "thumbnail_url": "https://cdn.drop.media/your-prefix/thumbnail/4b0f6c1e-2d3a-4e5f-9a8b-7c6d5e4f3a2b.png",
  "markdown": "![settings-page](https://cdn.drop.media/your-prefix/4b0f6c1e-2d3a-4e5f-9a8b-7c6d5e4f3a2b.png)",
  "name": "settings-page.png",
  "mime_type": "image/png",
  "size": 183204,
  "width": 1440,
  "height": 900,
  "visibility": "public",
  "expires_at": null,
  "source": "mcp",
  "prompt": null,
  "model": null,
  "created_at": "2026-10-26T09:30:00+00:00"
}
```

| Field | Notes |
|---|---|
| `id` | The file id used by `get_file`, `share_file` and `delete_file`. A random UUID, or the custom `name` you chose. |
| `url` | Public files: the permanent CDN URL. Private files: a signed `https://drop.media/p/<id>?...&signature=...` link. |
| `url_expires_at` | `null` for public files; when the signed link stops working for private files (ISO 8601). |
| `thumbnail_url` | A thumbnail when one was made (signed for private files), otherwise `null`. |
| `markdown` | `![alt](url)` for images (alt is the prompt or file name), `[name](url)` for other files. |
| `name` | The original file name. |
| `width`, `height` | Pixel size for images, otherwise `null`. |
| `visibility` | `public` or `private`. |
| `expires_at` | When the file deletes itself, or `null`. |
| `source` | Where the file came from: `mcp`, `api`, `web` or `generated`. |
| `prompt`, `model` | AI prompt and model, if they were supplied or the image was generated. |

## Shared storage arguments

`upload_file`, `create_upload_link` and `generate_image` accept these:

| Argument | Type | Default | Constraints |
|---|---|---|---|
| `visibility` | `"public"` \| `"private"` | `"public"` | Public files get a permanent CDN URL. Private files are only reachable through signed, expiring links. |
| `expires_in` | string | none (kept until deleted) | A duration such as `"90s"`, `"30m"`, `"1h"`, `"7d"` or `"2w"`, a number of seconds, or an ISO 8601 date/time. Must be at least one minute and at most 365 days in the future. `"never"` means no expiry. |
| `name` | string | random UUID | `^[A-Za-z0-9_-]{1,100}$`. Used in the URL instead of a random id. Must not already be in use by anyone on drop.media. |

---

## `upload_file`

> Host a file on drop.media and get a URL you can put in a PR, issue, chat message, email or web page.
> Send one of: `file` (a file from the conversation, such as an image the user attached or you generated),
> `url` (drop.media downloads it), or `content_base64` plus `filename`.
> If you can run shell commands and the file is on disk, prefer `create_upload_link` + curl: it avoids base64-encoding large files.
> Supported: images (PNG, JPG, GIF, WebP, SVG, AVIF, HEIC), PDF, video (MP4, MOV, WebM), audio (MP3, WAV, M4A),
> text (TXT, MD, CSV, JSON, LOG) and Office files (DOCX, XLSX, PPTX).

**Scope:** `files:write`

Send exactly one source. If you send more than one, `file` is used first, then `url`, then `content_base64`.

| Argument | Type | Required | Notes |
|---|---|---|---|
| `file` | object | one source | A conversation file, for clients that provide one (ChatGPT fills this in through `openai/fileParams`). Properties: `download_url` (string, required), `file_id` (string, required), `mime_type` (string), `file_name` (string). |
| `url` | string (URI) | one source | A public `http`/`https` URL that drop.media downloads. |
| `content_base64` | string | one source | Base64 file contents. A `data:` URI is also accepted. |
| `filename` | string | with `content_base64` | Name including extension, for example `"chart.png"`. The extension decides the file type. |
| `visibility`, `expires_in`, `name` | | no | See [shared storage arguments](#shared-storage-arguments). |
| `prompt` | string | no | If the image was AI-generated, the prompt (up to 4000 characters). Stored with the file. |
| `model` | string | no | If the image was AI-generated, the model (up to 100 characters). |

**Limits:**

- Files can be up to 100 MB.
- The type must be one of the supported types. It's matched by extension and then checked against the file's actual
  bytes, so a renamed file is rejected.
- URLs are downloaded only from public internet addresses. Private, loopback, link-local and reserved addresses are
  refused, including after redirects. drop.media follows up to 3 redirects and waits up to 20 seconds.

**Example input** (host a public image):

```json
{
  "url": "https://drop.media/images/brand/icon-512.png",
  "expires_in": "7d"
}
```

**Example result:**

- text: `Uploaded.` followed by `URL: <url>`. For private files, a note says when the link stops working and suggests
  `share_file` for a longer-lived link.
- structured content: a [file object](#the-file-object).

**Common errors:**

| Message | Cause |
|---|---|
| `Provide file, url, or content_base64 with a filename.` | No source was given. |
| `A filename (e.g. "chart.png") is required with content_base64.` | `filename` is missing. |
| `content_base64 is not valid base64.` | The content couldn't be decoded. |
| `Files can be at most 100MB.` / `The file at that URL is too large.` | The size limit was exceeded. |
| `Unsupported file type. Allowed: ...` | The extension isn't supported, or the content doesn't match it. |
| `That URL points to a private or reserved address.` | The URL resolves to a non-public address. |
| `Could not resolve <host>.` / `Could not download the file at that URL.` / `Downloading that URL failed with HTTP <status>.` / `That URL redirected too many times.` | The URL couldn't be fetched. |
| `The name "<name>" is already taken.` | Choose another `name`, or leave it out. |

---

## `create_upload_link`

> Get a one-time upload URL for a file that is on disk, then send it with curl (the response includes the exact command):
> `curl --fail-with-body -T ./screenshot.png '<upload_url>'`
> curl prints JSON with the hosted file's `url`. The link takes one file and expires after 15 minutes.
> Retrying is safe: sending the same file again returns the file already stored, and a GET on the URL says whether the upload finished.
> Best choice when you can run shell commands; use upload_file otherwise.

**Scope:** `files:write`

| Argument | Type | Required | Notes |
|---|---|---|---|
| `filename` | string | **yes** | The name the file will be stored under, including extension, for example `"screenshot.png"`. The extension decides the file type. |
| `visibility`, `expires_in`, `name` | | no | See [shared storage arguments](#shared-storage-arguments). These are checked now, so mistakes show up before the upload. |
| `prompt`, `model` | string | no | As for `upload_file`. |

**Example input:**

```json
{
  "filename": "settings-page.png",
  "expires_in": "30d"
}
```

**Example structured content:**

```json
{
  "upload_url": "https://drop.media/api/v1/uploads/<one-time-token>",
  "method": "PUT",
  "status_url": "https://drop.media/api/v1/uploads/<one-time-token>",
  "max_bytes": 104857600,
  "expires_at": "2026-10-26T09:45:00+00:00",
  "curl": "curl --fail-with-body -T 'settings-page.png' 'https://drop.media/api/v1/uploads/<one-time-token>'"
}
```

The text content asks the agent to run the `curl` command from the directory containing the file, adjusting the path
if needed.

**Errors:** `A filename is required, e.g. "screenshot.png".` and the storage-argument errors under
[`upload_file`](#upload_file). Upload errors happen later, at the `PUT` (see below).

### The upload-link workflow

The MCP tool call doesn't transfer the file. It only returns a URL. **Something with access to the file must then
send the bytes over HTTP.** That's usually the agent running `curl` in a shell. Clients that can't read local files or
make HTTP requests (many chat apps, for example) can't complete this step. They should use `upload_file` with a `url` or
base64 content instead.

1. Call `create_upload_link` with the file's name and options.
2. Send the raw file with a `PUT` to `upload_url`. No `Authorization` header is needed, because the link itself is the
   credential:

   ```bash
   curl --fail-with-body -T ./settings-page.png '<upload_url>'
   ```

   The local path can be anything. The file is stored under the `filename` you passed in step 1.
3. Read the JSON response. `data` is a [file object](#the-file-object) whose `url` and `markdown` you can use.

| `PUT` status | Meaning |
|---|---|
| `201` | Stored. Body: `{"data": <file object>}`. |
| `200` | The same bytes were already uploaded with this link (for example after a dropped connection). Returns the existing file. |
| `409` | The link is busy receiving another upload, or it was already used for a different file. Request a new link. |
| `404` | The link is invalid or expired, the API key that created it was revoked, or the subscription is no longer active. |
| `422` | The file was rejected: too large, unsupported type, or the `name` was taken in the meantime. The body contains `message`. |
| `429` | Too many requests. The upload endpoint allows 30 `PUT`s per minute. |

To check on an upload that may have finished (for example after a timeout), send a `GET` to `status_url`. It returns
`{"data": {"status": "pending" | "completed", "expires_at": "...", "file": <file object or null>}}`.

Each link accepts **one** file and expires **15 minutes** after it's created. Treat it like a password until then.

---

## `list_files`

> List files in the drop.media library, newest first. It is shared by all the user's AI tools, so look here for files they or another agent added before. Search matches every word in names and AI prompts.

**Scope:** `files:read`

| Argument | Type | Default | Notes |
|---|---|---|---|
| `search` | string | none | Words to look for in the file id, original name or AI prompt. Every word must appear; spaces, dashes, underscores and dots all separate words, so `q3 revenue` finds `q3-revenue.png`. |
| `type` | `"all"` \| `"images"` \| `"video"` \| `"audio"` \| `"pdfs"` \| `"docs"` \| `"generated"` | `"all"` | `docs` means text, JSON and Office files. `generated` means images made with `generate_image` or on the website. |
| `page` | integer ≥ 1 | `1` | |
| `per_page` | integer 1–100 | `20` | |

Expired files aren't listed. You only see your own files.

**Example input:**

```json
{ "search": "settings", "type": "images", "per_page": 5 }
```

**Example structured content:**

```json
{
  "files": [
    { "id": "settings-page", "url": "https://cdn.drop.media/your-prefix/settings-page.png", "visibility": "public", "...": "other file object fields" }
  ],
  "page": 1,
  "total": 1,
  "has_more": false
}
```

The text content is `Showing <n> of <total> file(s), page <p>:` followed by one line per file (id, type, date and URL).
Private files appear as `[private: use share_file for a link]` in the text, but their structured entries contain a
signed link that expires after 1 hour. If nothing matches, the text is `No files found.`

---

## `get_file`

> Get the details and URL of one file by its id.

**Scope:** `files:read`

| Argument | Type | Required | Notes |
|---|---|---|---|
| `id` | string | **yes** | The file id, as returned by `upload_file` or `list_files`. |

**Example input:** `{ "id": "settings-page" }`

**Result:** text `URL: <url>` and a [file object](#the-file-object). For a private file, the `url` is a signed link valid for
1 hour (or until the file expires, if that's sooner).

**Errors:** `No file with id "<id>". Use list_files to find ids.` (This also covers expired files and files in other accounts.)

---

## `share_file`

> Get a shareable link to a file. For private files this is a signed link that expires after `ttl` (default 1h, max 7d). Public files always return their permanent URL.

**Scope:** `files:read`

| Argument | Type | Default | Notes |
|---|---|---|---|
| `id` | string | required | The file id. |
| `ttl` | string | `"1h"` | How long a private link should work, for example `"15m"`, `"1h"`, `"3d"`. Same formats as `expires_in`. Minimum one minute, maximum 7 days. For public files the value is still checked but has no effect. |

A private link never outlives its file. If the file expires sooner, the link expires with it. Links are signed against
the specific file, so they stop working if the file is deleted, even if a new file later reuses the same name.

**Example input:**

```json
{ "id": "q3-report", "ttl": "1d" }
```

**Example result:**

- text: `Link (works until 2026-10-27T09:30:00+00:00): https://drop.media/p/q3-report?expires=...&ref=...&signature=...`
  for a private file, or `Permanent URL: <url>` for a public one.
- structured content: a [file object](#the-file-object) whose `url` and `url_expires_at` describe the new link.

**Errors:** unknown id (as for `get_file`), `Expiry can be at most 7 days away.`,
`Expiry must be at least a minute in the future.` and
`Use a duration like "30m", "1h", "7d" or "2w", or an ISO 8601 date.`

Anyone who has a signed link can open the file until the link expires. Links can't be revoked individually; deleting
the file is the way to cut off access early.

---

## `delete_file`

> Permanently delete a file. Its URL stops working (CDN caches may take a few minutes to clear).

**Scope:** `files:delete` · **Destructive**

| Argument | Type | Required | Notes |
|---|---|---|---|
| `id` | string | **yes** | The file id to delete. |

**Example input:** `{ "id": "old-screenshot" }`

**Result:** text `Deleted <id>.` (no structured content). The file and its thumbnail are removed from storage. This
can't be undone.

**Errors:** `No file with id "<id>". Use list_files to find ids.`

Look up the id with `list_files` or `get_file` and confirm it with the user before you delete. A close match isn't
enough.

---

## `generate_image`

> Generate an image from a text prompt and host it on drop.media. Returns the URL; the prompt and model are saved with the file. Takes 10-60 seconds.

**Scope:** `images:generate`

| Argument | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string | required | 1–4000 characters. Describe the subject, style and composition. |
| `size` | `"1024x1024"` \| `"1536x1024"` \| `"1024x1536"` | `"1024x1024"` | Square, landscape or portrait. |
| `visibility`, `expires_in`, `name` | | | See [shared storage arguments](#shared-storage-arguments). |

Each account has a daily generation limit. The result says how many generations are left, and the limit resets at
midnight UTC. Each call creates and stores a new image.

**Example input:**

```json
{
  "prompt": "Isometric illustration of a data pipeline, soft pastel palette, white background",
  "size": "1536x1024",
  "expires_in": "30d"
}
```

**Example result:**

- text: `Generated with <model>. <n> generation(s) left today.` followed by `URL: <url>`.
- structured content: a [file object](#the-file-object) with `source: "generated"` and the `prompt` and `model` filled in.

**Errors:**

| Message | Cause |
|---|---|
| `The prompt must be between 1 and 4000 characters.` | The prompt is empty or too long. |
| `Size must be one of: 1024x1024, 1536x1024, 1024x1536.` | The size is invalid. |
| `You have reached today's image generation limit. It resets at midnight UTC.` | The daily limit was reached. |
| `The image generator rejected that prompt: ...` | The upstream model refused the prompt. |
| `The image generator is busy. Please try again shortly.` / `Image generation failed. Please try again.` / `The image generator could not be reached. Please try again.` | A temporary upstream failure. Retry later. |

---

## Rate limits

Requests to `/mcp` are limited to 120 per minute per account. Upload links accept 30 `PUT`s and 60 status `GET`s per
minute.
