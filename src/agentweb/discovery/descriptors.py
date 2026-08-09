"""Build discovery documents: legacy agent.json + ARD ai-catalog.json."""

from __future__ import annotations

from typing import Any, Dict, List

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse

from .. import __version__, conf

SERVER_CARD_SCHEMA = (
    "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json"
)


def _safe_reverse(name: str) -> str | None:
    try:
        return reverse(name)
    except NoReverseMatch:
        return None


def _absolute(request, path: str | None) -> str | None:
    if not path:
        return None
    return request.build_absolute_uri(path)


def _host_meta() -> Dict[str, str]:
    cfg = conf.get_domain("DISCOVERY")
    display = (cfg.get("HOST_DISPLAY_NAME") or "").strip()
    identifier = (cfg.get("HOST_IDENTIFIER") or "").strip()
    try:
        site = Site.objects.get_current()
        if not display:
            display = site.name or site.domain
        if not identifier:
            identifier = f"https://{site.domain}"
    except Exception:
        if not display:
            display = "site"
        if not identifier:
            identifier = getattr(settings, "SITE_ID", "site")
    return {"displayName": display, "identifier": str(identifier)}


def build_descriptor(request) -> Dict[str, Any]:
    """Return the ``/.well-known/agent.json`` payload for the current site.

    Soft-deprecated in favour of :func:`build_ai_catalog` /
    ``/.well-known/ai-catalog.json`` (ARD). Kept for one minor as a compact
    capability map for early integrators; new consumers should prefer
    ``ai-catalog.json``.
    """
    capabilities: Dict[str, Any] = {}

    if conf.is_enabled("LLMS"):
        url = _safe_reverse("agentweb-llms-txt")
        capabilities["llmsTxt"] = {"url": _absolute(request, url)}

    if conf.is_enabled("WEBMCP"):
        url = _safe_reverse("agentweb-webmcp-manifest")
        capabilities["webmcp"] = {
            "manifest": _absolute(request, url),
            "note": (
                "Browser WebMCP uses navigator.modelContext; the manifest "
                "lists tool descriptors for page registration."
            ),
        }

    if conf.is_enabled("COMMERCE"):
        url = _safe_reverse("agentweb-commerce-descriptor")
        capabilities["commerce"] = {
            "descriptor": _absolute(request, url),
            "vendor": conf.get_domain("COMMERCE").get("VENDOR"),
        }

    descriptor: Dict[str, Any] = {
        "schemaVersion": "0.1",
        "name": "agentweb",
        "deprecated": True,
        "successor": "/.well-known/ai-catalog.json",
        "capabilities": capabilities,
        "untrustedContentHint": True,
    }

    if conf.get_domain("DISCOVERY").get("WEB_BOT_AUTH"):
        descriptor["webBotAuth"] = {"required": True, "spec": "RFC9421"}

    return descriptor


def build_ai_catalog(request) -> Dict[str, Any]:
    """Return ``/.well-known/ai-catalog.json`` (Agentic Resource Discovery).

    Spec: https://agenticresourcediscovery.org/ai_catalog_spec/
    Publishes only enabled agent-web surfaces. CORS is set on the view.
    """
    host = _host_meta()
    domain = ""
    try:
        domain = Site.objects.get_current().domain
    except Exception:
        domain = "example.com"

    entries: List[Dict[str, Any]] = []

    if conf.is_enabled("LLMS"):
        llms_url = _absolute(request, _safe_reverse("agentweb-llms-txt"))
        if llms_url:
            entries.append(
                {
                    "identifier": f"urn:air:{domain}:llms:root",
                    "displayName": "llms.txt",
                    "type": "text/plain",
                    "url": llms_url,
                    "description": "Curated Markdown index for AI agents.",
                    "representativeQueries": [
                        "what does this site offer",
                        "summarize this website for an agent",
                    ],
                }
            )

    if conf.is_enabled("WEBMCP"):
        manifest = _absolute(request, _safe_reverse("agentweb-webmcp-manifest"))
        if manifest:
            entries.append(
                {
                    "identifier": f"urn:air:{domain}:webmcp:tools",
                    "displayName": "WebMCP tool descriptors",
                    "type": "application/json",
                    "url": manifest,
                    "description": (
                        "Tool descriptors for in-page WebMCP registration "
                        "(navigator.modelContext)."
                    ),
                    "representativeQueries": [
                        "what tools can an agent call on this page",
                        "check availability or simulate a booking cost",
                    ],
                }
            )

    if conf.is_enabled("COMMERCE"):
        commerce = _absolute(
            request, _safe_reverse("agentweb-commerce-descriptor")
        )
        if commerce:
            entries.append(
                {
                    "identifier": f"urn:air:{domain}:commerce:descriptor",
                    "displayName": "Agentic commerce descriptor",
                    "type": "application/json",
                    "url": commerce,
                    "description": (
                        "Discovery for availability, price simulation, and "
                        "direct booking hooks."
                    ),
                    "representativeQueries": [
                        "simulate booking cost",
                        "start a direct reservation",
                    ],
                }
            )

    if conf.is_enabled("WEBMCP"):
        card = _absolute(request, _safe_reverse("agentweb-mcp-server-card"))
        if card:
            entries.append(
                {
                    "identifier": f"urn:air:{domain}:mcp:server-card",
                    "displayName": "MCP server card",
                    "type": "application/mcp-server-card+json",
                    "url": card,
                    "description": (
                        "MCP Server Card for agentweb WebMCP discovery."
                    ),
                    "representativeQueries": [
                        "how do agents connect to this site's tools",
                    ],
                }
            )

    return {
        "specVersion": "1.0",
        "host": host,
        "entries": entries,
    }


def build_mcp_server_card(request) -> Dict[str, Any]:
    """Return ``/.well-known/mcp/server-card.json`` (MCP Server Card v1).

    Describes the site's agentweb WebMCP surface. A Streamable HTTP remote is
    included only when ``WEBMCP.REMOTE_BRIDGE`` is enabled; otherwise the card
    advertises browser WebMCP via the tool-descriptor manifest in ``_meta``.
    """
    host = _host_meta()
    manifest = _absolute(request, _safe_reverse("agentweb-webmcp-manifest"))
    card: Dict[str, Any] = {
        "$schema": SERVER_CARD_SCHEMA,
        "name": "io.github.dlrsp/agentweb",
        "version": __version__,
        "title": "django-agentweb WebMCP",
        "description": (
            "In-page WebMCP tools for this Django site (opt-in per domain)."
        ),
        "websiteUrl": host.get("identifier") or None,
    }
    # Drop empty optional URI fields (schema wants format:uri when present).
    if not card.get("websiteUrl"):
        card.pop("websiteUrl", None)

    remotes: List[Dict[str, Any]] = []
    if conf.is_enabled("WEBMCP") and conf.get_domain("WEBMCP").get(
        "REMOTE_BRIDGE"
    ):
        # Bridge invoke base (clients append /<tool>); not a full MCP session.
        try:
            bridge_path = reverse(
                "agentweb-webmcp-tool", kwargs={"name": "_"}
            ).rsplit("/", 1)[0]
        except NoReverseMatch:
            bridge_path = None
        bridge = _absolute(request, bridge_path)
        if bridge:
            remotes.append(
                {
                    "type": "streamable-http",
                    "url": bridge,
                }
            )
    if remotes:
        card["remotes"] = remotes

    card["_meta"] = {
        "io.github.dlrsp/agentweb": {
            "protocol": "webmcp-browser",
            "manifestUrl": manifest,
            "remoteBridge": bool(
                conf.is_enabled("WEBMCP")
                and conf.get_domain("WEBMCP").get("REMOTE_BRIDGE")
            ),
        }
    }
    return card
