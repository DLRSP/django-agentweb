# Discovery — /.well-known

Publishes machine-readable descriptors so agents can discover which agent-web
features the site exposes.

## What you get after enabling

With `DISCOVERY.ENABLED = True` and `agentweb.urls` included:

| URL | Name | Role |
|-----|------|------|
| `/.well-known/agent.json` | `agentweb-agent-descriptor` | Compact capability map (legacy-friendly) |
| `/.well-known/ai-catalog.json` | `agentweb-ai-catalog` | [Agentic Resource Discovery](https://agenticresourcediscovery.org/) catalog (`specVersion` 1.0), CORS `*` |
| `/.well-known/mcp/server-card.json` | `agentweb-mcp-server-card` | MCP Server Card for the site WebMCP surface |

Catalog entries only reflect **other domains that are also enabled**. Enabling
discovery alone with every other domain off yields a minimal host catalog.

Optional host fields:

```python
APP_CONFIG = {
    "agentweb": {
        "DISCOVERY": {
            "ENABLED": True,
            "HOST_DISPLAY_NAME": "Example Hotel",
            "HOST_IDENTIFIER": "example.com",
            "WEB_BOT_AUTH": False,
        },
    },
}
```

## Middleware (recommended)

URLs work without middleware. Middleware advertises discovery on ordinary HTML
responses:

```python
MIDDLEWARE = [
    # ...
    "agentweb.discovery.middleware.AgentwebDiscoveryMiddleware",
]
```

When discovery is enabled, the middleware may set:

- `Link` — `rel="ai-catalog"` and `rel="agent-descriptor"`
- `X-Agentweb-Discovery: 1`
- `Permissions-Policy: tools=(self)` — only if `WEBMCP` is also enabled and
  `tools=` is not already present

## Web Bot Auth (optional)

Set `WEB_BOT_AUTH: True` and install the extra:

```bash
pip install "django-agentweb[webbotauth]"
```

This enforces HTTP Message Signatures (RFC 9421) on selected agent traffic.
Leave off unless you have a concrete agent-auth requirement.

## MCP server card and remote bridge

The server card describes browser WebMCP. Streamable HTTP remotes appear only
when `WEBMCP.REMOTE_BRIDGE` is enabled — keep that off for browser-only sites.

## Verify

1. `GET /.well-known/ai-catalog.json` → `200` JSON.
2. Enable `LLMS` and reload: catalog should mention readability resources.
3. With middleware: inspect response headers on a normal page for `Link`.

See [Configuration](../configuration.md#discovery).
