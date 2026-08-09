"""Template tags for rendering Schema.org JSON-LD.

Usage::

    {% load agentweb_jsonld %}
    {% jsonld_script hotel_dict %}

Renders a ``<script type="application/ld+json">`` block. The payload is
JSON-encoded (not HTML-escaped into entities) but ``<`` is escaped to ``\\u003c``
to prevent breaking out of the script element.
"""

from __future__ import annotations

import json
from typing import Any

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def jsonld_script(data: Any) -> str:
    """Render ``data`` as a safe JSON-LD ``<script>`` block."""
    if not data:
        return ""
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Prevent premature </script> termination / breakout.
    payload = (
        payload.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return mark_safe(  # noqa: S308 - payload is JSON-serialised and escaped
        f'<script type="application/ld+json">{payload}</script>'
    )
