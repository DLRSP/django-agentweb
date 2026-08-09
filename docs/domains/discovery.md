# Discovery — /.well-known

Publishes machine-readable descriptors so agents can discover which agent-web
features the site exposes:

- `/.well-known/agent.json` — compact capability map (soft-deprecated)
- `/.well-known/ai-catalog.json` — [Agentic Resource Discovery](https://agenticresourcediscovery.org/)
  catalog (`specVersion` 1.0) with CORS `Access-Control-Allow-Origin: *`
- `/.well-known/mcp/server-card.json` — MCP Server Card (v1 schema) for the
  site's WebMCP surface; Streamable HTTP remotes only when the optional remote
  bridge is enabled

Only **enabled** domains appear as catalog entries. Optional Web Bot Auth
(RFC 9421) remains behind the `webbotauth` extra and `DISCOVERY.WEB_BOT_AUTH`.
