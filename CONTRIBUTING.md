# Contributing

Thanks for helping improve the drop.media MCP docs. This repository holds documentation and integration examples for
the **hosted** drop.media MCP server. It doesn't contain the server, and pull requests can't change the service's behaviour.
To request a feature or report a service problem, use <https://drop.media/contact> or an issue.

## What's welcome

- Corrections where the docs don't match what the server actually does
- Setup instructions for another MCP client, or updates when a client's config format changes
- Clearer explanations, examples and troubleshooting entries

## Rules for content

- **Describe only what exists.** Tool names, arguments, limits and errors must match the live server. When in doubt,
  check `tools/list` with your own credential. Don't add features, prices, limits or client support you haven't
  confirmed.
- **Say how you checked client instructions.** In [docs/clients.md](docs/clients.md), mark a configuration as *tested*
  only if you connected with it and called a tool. Otherwise mark it as checked against the client's official docs, and
  link to them. Include the client version you used.
- **Prefer native remote connections.** Don't add local proxies or bridges when the client supports remote servers.
- **Never commit secrets.** Use placeholders such as `<API key>` or `DROP_API_KEY`. Don't include real upload links,
  signed file links, account prefixes, email addresses or screenshots of private data.
- **Keep it short.** Link to official client documentation rather than copying it.
- Don't add badges, star counts, testimonials or claims of directory approval.

## Making a change

1. Fork the repository and create a branch.
2. Edit the Markdown or examples.
3. Run the checks (Python 3.9+, standard library only):

   ```bash
   python3 scripts/check.py             # JSON files, JSON code blocks, internal links and anchors
   python3 scripts/check.py --external  # also checks that external links respond
   ```

4. Open a pull request saying what changed and how you checked it.

## Licensing of contributions

By contributing, you agree that documentation changes are licensed under CC BY 4.0 and code or configuration changes
under MIT, as described in [LICENSE.md](LICENSE.md).
