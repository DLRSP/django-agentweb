"""HTTP middleware for agent-discovery headers."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.urls import NoReverseMatch, reverse

from .. import conf


class AgentwebDiscoveryMiddleware:
    """Attach AI-oriented discovery headers when DISCOVERY is enabled.

    * ``Link`` — points at ``ai-catalog.json`` (ARD) when available
    * ``Permissions-Policy: tools=(self)`` — when WEBMCP is enabled
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if not conf.is_enabled("DISCOVERY"):
            return response

        links = []
        try:
            catalog = reverse("agentweb-ai-catalog")
            links.append(f'<{catalog}>; rel="ai-catalog"')
        except NoReverseMatch:
            pass
        try:
            agent = reverse("agentweb-agent-descriptor")
            links.append(f'<{agent}>; rel="agent-descriptor"')
        except NoReverseMatch:
            pass
        if links:
            existing = response.get("Link", "")
            combined = ", ".join([p for p in (existing, ", ".join(links)) if p])
            response["Link"] = combined

        if conf.is_enabled("WEBMCP"):
            # Allow same-origin WebMCP tool registration (Chrome Permissions-Policy).
            existing_pp = response.get("Permissions-Policy", "")
            tools_clause = "tools=(self)"
            if "tools=" not in existing_pp:
                response["Permissions-Policy"] = (
                    f"{existing_pp}, {tools_clause}".strip(", ")
                    if existing_pp
                    else tools_clause
                )

        response["X-Agentweb-Discovery"] = "1"
        return response
