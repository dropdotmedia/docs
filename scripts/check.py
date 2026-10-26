#!/usr/bin/env python3
"""Lightweight checks for this docs repository (standard library only).

- every *.json file parses
- every ```json code block in Markdown parses
- relative links and #anchors in Markdown point at files and headings that exist
- with --external, http(s) links respond (HEAD, falling back to GET)
- no obvious credentials (bearer tokens, upload links, signed URLs) are committed

Licensed under MIT; see LICENSES/MIT.txt.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "LICENSES"}

FENCE = re.compile(r"^```(\w*)\s*$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)|<(https?://[^>\s]+)>")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
SECRETS = [
    (re.compile(r"Bearer\s+(?![<$])[A-Za-z0-9|_-]{20,}"), "looks like a real bearer token"),
    (re.compile(r"/api/v1/uploads/[A-Za-z0-9]{48}"), "looks like a real upload link"),
    (re.compile(r"signature=[0-9a-f]{32,}"), "looks like a real signed URL"),
]


def files(pattern):
    return [p for p in ROOT.rglob(pattern) if not SKIP_DIRS & set(p.relative_to(ROOT).parts)]


def slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path, cache={}):
    if path not in cache:
        found, seen, in_code = set(), {}, False
        for line in path.read_text(encoding="utf-8").splitlines():
            if FENCE.match(line):
                in_code = not in_code
            match = None if in_code else HEADING.match(line)
            if match:
                base = slug(match.group(2))
                n = seen.get(base, 0)
                seen[base] = n + 1
                found.add(base if n == 0 else f"{base}-{n}")
        cache[path] = found
    return cache[path]


def markdown_blocks(text):
    lang, start, buf = None, 0, []
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match and lang is None:
            lang, start, buf = match.group(1) or "text", number, []
        elif line.strip() == "```" and lang is not None:
            yield lang, start, "\n".join(buf)
            lang = None
        elif lang is not None:
            buf.append(line)


def strip_code(text):
    return re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", text, flags=re.S))


def check_url(url):
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "drop-docs-link-check"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status < 400 or response.status in (401, 405)
        except urllib.error.HTTPError as e:
            # Endpoints that need auth or POST still prove the URL exists.
            if e.code in (401, 402, 405):
                return True
            if method == "GET":
                return False
        except Exception:
            if method == "GET":
                return False
    return False


def main():
    external = "--external" in sys.argv
    errors, urls = [], set()

    for path in files("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {e}")

    for path in files("*.md"):
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")

        for lang, line, block in markdown_blocks(text):
            if lang == "json":
                try:
                    json.loads(block)
                except json.JSONDecodeError as e:
                    errors.append(f"{rel}:{line}: invalid JSON block: {e}")

        for match in LINK.finditer(strip_code(text)):
            target = match.group(1) or match.group(2)
            if target.startswith(("http://", "https://")):
                urls.add(target)
                continue
            if target.startswith("mailto:"):
                continue
            file_part, _, anchor = target.partition("#")
            dest = (path.parent / file_part).resolve() if file_part else path
            if not dest.exists():
                errors.append(f"{rel}: broken link {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                errors.append(f"{rel}: missing anchor {target}")

    for path in files("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".yml", ".sh", ".py"}:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for pattern, message in SECRETS:
                    if pattern.search(line):
                        errors.append(f"{path.relative_to(ROOT)}:{number}: {message}")

    if external:
        for url in sorted(urls):
            if not check_url(url):
                errors.append(f"unreachable: {url}")

    for error in errors:
        print(error)
    print(f"{'FAIL' if errors else 'OK'}: {len(errors)} problem(s)" + ("" if external else " (external links not checked)"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
