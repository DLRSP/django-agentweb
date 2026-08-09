"""URLs for the WebMCP domain."""

from __future__ import annotations

from django.urls import path

from .views import WebMCPManifestView, WebMCPToolView

urlpatterns = [
    path(
        ".well-known/webmcp.json",
        WebMCPManifestView.as_view(),
        name="agentweb-webmcp-manifest",
    ),
    path(
        "webmcp/tools/<str:name>",
        WebMCPToolView.as_view(),
        name="agentweb-webmcp-tool",
    ),
]
