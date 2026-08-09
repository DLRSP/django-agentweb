"""Template tags for browser WebMCP registration."""

from __future__ import annotations

import json

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

from agentweb import conf
from agentweb.webmcp import tools

register = template.Library()


@register.simple_tag(takes_context=True)
def webmcp_register(context) -> str:
    """Embed tool descriptors + load ``webmcp.js`` for browser registration.

    Renders nothing when the WEBMCP domain is disabled. The script registers
    tools on ``navigator.modelContext`` when the browser supports WebMCP.
    """
    if not conf.is_enabled("WEBMCP"):
        return ""

    cfg = conf.get_domain("WEBMCP")
    bridge_url = ""
    if cfg.get("REMOTE_BRIDGE"):
        try:
            # Path prefix without tool name — JS appends /<name>.
            bridge_url = reverse(
                "agentweb-webmcp-tool", kwargs={"name": "_"}
            ).rsplit("/", 1)[0]
        except NoReverseMatch:
            bridge_url = ""

    payload = {
        "tools": [t.to_descriptor() for t in tools.all_tools().values()],
        "remoteBridgeUrl": bridge_url or None,
    }
    config_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    config_json = (
        config_json.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    html = (
        f'<script type="application/json" id="agentweb-webmcp-config">'
        f"{config_json}</script>\n"
        f'<script src="{_static_url(context, "agentweb/webmcp.js")}" '
        f"defer></script>"
    )
    return mark_safe(html)  # noqa: S308 - JSON escaped; script src is static


def _static_url(context, path: str) -> str:
    try:
        from django.templatetags.static import static

        return static(path)
    except Exception:
        return f"/static/{path}"
