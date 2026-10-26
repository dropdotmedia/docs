#!/usr/bin/env bash
# Upload a local file to drop.media through a one-time upload link (REST API).
# Needs: bash, curl, python3, and DROP_API_KEY set to a key with the files:write ability.
#
#   ./upload-with-link.sh <file> [--private] [--expires <duration>] [--name <slug>]
#
# Prints the hosted file's JSON (id, url, markdown, ...). Licensed under MIT; see LICENSES/MIT.txt.
set -euo pipefail

usage() { echo "usage: $0 <file> [--private] [--expires 7d] [--name slug]" >&2; exit 64; }

[[ $# -ge 1 ]] || usage
file=$1; shift
[[ -f $file ]] || { echo "not a file: $file" >&2; exit 66; }
: "${DROP_API_KEY:?set DROP_API_KEY to a drop.media API key with files:write}"

visibility=public expires= name=
while [[ $# -gt 0 ]]; do
  case $1 in
    --private) visibility=private; shift ;;
    --expires) expires=${2:?}; shift 2 ;;
    --name) name=${2:?}; shift 2 ;;
    *) usage ;;
  esac
done

body=$(python3 - "$(basename -- "$file")" "$visibility" "$expires" "$name" <<'PY'
import json, sys
filename, visibility, expires, name = sys.argv[1:]
body = {"filename": filename, "visibility": visibility}
if expires: body["expires_in"] = expires
if name: body["name"] = name
print(json.dumps(body))
PY
)

# 1. Ask for a one-time upload URL (valid for 15 minutes, one file).
slot=$(curl --silent --show-error --fail-with-body \
  -H "Authorization: Bearer ${DROP_API_KEY}" \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d "$body" https://drop.media/api/v1/uploads) || { echo "$slot" >&2; exit 1; }
upload_url=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["upload_url"])' <<<"$slot")

# 2. Send the bytes. The URL is the credential, so no Authorization header is sent here.
result=$(curl --silent --show-error --fail-with-body -T "$file" "$upload_url") || { echo "$result" >&2; exit 1; }

python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["data"], indent=2))' <<<"$result"
