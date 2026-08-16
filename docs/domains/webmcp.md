# WebMCP — Web Model Context Protocol

**Browser-native** WebMCP registers tools on the page via `navigator.modelContext`
(or `document.modelContext`). Enabling the domain mounts discovery URLs; you
still must register tools and include a template tag for in-browser use.

## Checklist after `ENABLED`

1. `WEBMCP.ENABLED = True` in `APP_CONFIG["agentweb"]`.
2. Include `agentweb.urls` (already done in getting started).
3. Register tools in Python (`agentweb.webmcp.tools`).
4. Add `{% webmcp_register %}` to the base template (usually before `</body>`).
5. Optionally enable Discovery middleware for `Permissions-Policy: tools=(self)`.
6. Leave `REMOTE_BRIDGE` **False** unless you accept the headless HTTP trust model.

```python
APP_CONFIG = {
    "agentweb": {
        "WEBMCP": {
            "ENABLED": True,
            "DATA_SOURCE": "proxy",   # reserved (not enforced yet); keep proxy
            "REMOTE_BRIDGE": False, # HTTP invoke for headless agents
        },
    },
}
```

Install the proxy extra when you later wire server-side vendor calls (the
`DATA_SOURCE` key is reserved for that posture and is not enforced yet):

```bash
pip install "django-agentweb[webmcp]"
```

## URLs

| URL | Name | Role |
|-----|------|------|
| `/.well-known/webmcp.json` | `agentweb-webmcp-manifest` | JSON tool descriptors (not the browser API itself) |
| `/webmcp/tools/<name>` | `agentweb-webmcp-tool` | Optional remote bridge (`POST`); **404** unless `REMOTE_BRIDGE` |

## Template tags

### Browser registration

```django
{% load agentweb_webmcp %}
{% webmcp_register %}
```

Renders nothing when WebMCP is disabled. When enabled, embeds tool descriptors
and loads `agentweb/webmcp.js`, which registers tools when the browser API is
present (progressive enhancement).

### Declarative form attributes

```django
{% load agentweb_webmcp_decl %}
<form {% webmcp_form_attrs "search_rooms" "Search available rooms" %}>
  ...
</form>
```

Emits `data-mcp-tool-*` attributes for agents that understand declarative markup.

### Permissions-Policy without Discovery middleware

If you enable WebMCP but skip Discovery middleware, you can still advertise
same-origin tools permission:

```django
{% load agentweb_webmcp_decl %}
<meta http-equiv="Permissions-Policy" content="{% permissions_policy_tools %}">
```

Prefer Discovery middleware when that domain is on — it sets the response
header automatically when WebMCP is enabled.

## Register tools

```python
from agentweb.webmcp import tools

@tools.register(
    name="check_availability",
    description="Check room availability for dates.",
    read_only_hint=True,
    input_schema={"type": "object", "properties": {"check_in": {"type": "string"}}},
)
def check_availability(request, **params):
    return {"available": True, "check_in": params.get("check_in")}
```

Conventions:

- Prefer **read-only** tools (`read_only_hint=True`).
- State-changing tools should set `requires_human_confirmation=True`.
- Never expose secrets or privileged admin actions as tools.

## Remote bridge (optional)

`REMOTE_BRIDGE: True` allows CSRF-exempt `POST /webmcp/tools/<name>` for
headless agents. Read-only tools execute; confirmation-required tools return
`409`. This is **not** a substitute for in-browser WebMCP — see
[Security](../security.md).

## Verify

1. Open a page that includes `{% webmcp_register %}`.
2. `GET /.well-known/webmcp.json` lists your tools.
3. With bridge off, `POST /webmcp/tools/...` returns bridge-disabled.

See [Configuration](../configuration.md#webmcp).
