"""WebMCP tool registry.

A minimal, framework-agnostic registry. Sites register tools at import time
(e.g. in ``AppConfig.ready``)::

    from agentweb.webmcp import tools

    @tools.register(
        name="check_availability",
        description="Check room availability for a date range.",
        read_only_hint=True,
        input_schema={...},
    )
    def check_availability(request, **params):
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Tool:
    """A WebMCP tool descriptor plus its handler.

    The safety hints mirror the WebMCP/MCP conventions: ``read_only_hint``
    marks side-effect-free tools, ``exposed_to`` constrains which agents may
    call it, ``untrusted_content_hint`` flags responses that may contain
    user-generated content.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    read_only_hint: bool = True
    exposed_to: str = "agents"
    untrusted_content_hint: bool = True
    requires_human_confirmation: bool = False
    input_schema: Dict[str, Any] = field(default_factory=dict)

    def to_descriptor(self) -> Dict[str, Any]:
        """Return the JSON-serialisable descriptor (no handler)."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "readOnlyHint": self.read_only_hint,
            "exposedTo": self.exposed_to,
            "untrustedContentHint": self.untrusted_content_hint,
            "requiresHumanConfirmation": self.requires_human_confirmation,
        }


_REGISTRY: Dict[str, Tool] = {}


def register(
    *,
    name: str,
    description: str,
    read_only_hint: bool = True,
    exposed_to: str = "agents",
    untrusted_content_hint: bool = True,
    requires_human_confirmation: bool = False,
    input_schema: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator registering ``handler`` as a WebMCP tool."""

    def decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
        _REGISTRY[name] = Tool(
            name=name,
            description=description,
            handler=handler,
            read_only_hint=read_only_hint,
            exposed_to=exposed_to,
            untrusted_content_hint=untrusted_content_hint,
            requires_human_confirmation=requires_human_confirmation,
            input_schema=input_schema or {},
        )
        return handler

    return decorator


def get(name: str) -> Optional[Tool]:
    """Return the registered :class:`Tool` for ``name`` (or ``None``)."""
    return _REGISTRY.get(name)


def all_tools() -> Dict[str, Tool]:
    """Return a copy of the tool registry."""
    return dict(_REGISTRY)


def clear() -> None:
    """Remove all registered tools (primarily for tests)."""
    _REGISTRY.clear()
