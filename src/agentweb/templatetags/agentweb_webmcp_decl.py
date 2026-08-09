"""Declarative WebMCP helpers — HTML form annotations for browser agents."""

from __future__ import annotations

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def webmcp_form_attrs(
    name: str,
    description: str = "",
    *,
    read_only: bool = True,
) -> str:
    """Emit ``data-mcp-*`` attributes for declarative WebMCP form annotation.

    Usage::

        <form {% webmcp_form_attrs "search_rooms" "Search available rooms" %}>
    """
    return format_html(
        'data-mcp-tool-name="{}" data-mcp-tool-description="{}" '
        'data-mcp-tool-readonly="{}"',
        name,
        description,
        "true" if read_only else "false",
    )


@register.simple_tag
def permissions_policy_tools() -> str:
    """Emit a ``Permissions-Policy`` meta-compatible tools clause."""
    return "tools=(self)"
