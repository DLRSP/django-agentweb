"""Views for the discovery domain."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views import View

from .descriptors import (
    build_ai_catalog,
    build_descriptor,
    build_mcp_server_card,
)


class AgentDescriptorView(View):
    """Serve ``/.well-known/agent.json`` describing enabled capabilities."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse(build_descriptor(request))


class AiCatalogView(View):
    """Serve ``/.well-known/ai-catalog.json`` (ARD / ai-catalog 1.0)."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = JsonResponse(build_ai_catalog(request))
        # Required for cross-origin registry crawlers.
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response

    def options(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response


class McpServerCardView(View):
    """Serve ``/.well-known/mcp/server-card.json`` (MCP Server Card v1)."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = JsonResponse(
            build_mcp_server_card(request),
            content_type="application/mcp-server-card+json",
        )
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response

    def options(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response
