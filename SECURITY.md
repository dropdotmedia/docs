# Security

## Reporting a vulnerability

Report security issues with the drop.media service, including the MCP server at `https://drop.media/mcp`, OAuth,
API keys, upload links or private file links, **privately** through the contact form at
<https://drop.media/contact>. Start your message with "Security".

**Don't** open a public GitHub issue, discussion or pull request about a vulnerability.

Include:

- what's affected (endpoint, tool name, client)
- steps to reproduce and the impact you saw
- your contact details for follow-up

Don't include real API keys, OAuth tokens, upload links or signed file links. If one was exposed while you were
testing, revoke it under **Agents & API** at <https://drop.media/developers> and tell us that you did.

Only test against your own account and data. Don't access other people's files, degrade the service, or run automated
scanning that generates large volumes of traffic.

## Leaked credentials

If you find a drop.media API key or token in this repository or in an issue, report it privately as above. Don't repeat
it in public. If it's your own, revoke it straight away.

## Scope of this repository

This repository contains documentation and example configuration only. It doesn't contain drop.media's server code.
Issues with the example scripts (for example, unsafe handling of credentials) can be reported the same way, or as a
normal issue if they don't expose anyone's data.
