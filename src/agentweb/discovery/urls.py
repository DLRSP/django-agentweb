"""URLs for the discovery domain."""

from __future__ import annotations

from django.urls import path

from .views import AgentDescriptorView, AiCatalogView, McpServerCardView

urlpatterns = [
    path(
        ".well-known/agent.json",
        AgentDescriptorView.as_view(),
        name="agentweb-agent-descriptor",
    ),
    path(
        ".well-known/ai-catalog.json",
        AiCatalogView.as_view(),
        name="agentweb-ai-catalog",
    ),
    path(
        ".well-known/mcp/server-card.json",
        McpServerCardView.as_view(),
        name="agentweb-mcp-server-card",
    ),
]
