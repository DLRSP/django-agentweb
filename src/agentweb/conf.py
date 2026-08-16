"""Settings access layer for django-agentweb.

Configuration follows the shared ``APP_CONFIG`` pattern used by other reusable
Django packages. Every domain is **off by default**; a site opts in explicitly.

Precedence (highest first):

1. Top-level ``settings.AGENTWEB`` (full dict override, if defined and non-empty)
2. ``settings.APP_CONFIG["agentweb"]``
3. Package :data:`DEFAULTS`

Example (canonical)::

    APP_CONFIG = {
        "agentweb": {
            "LLMS": {
                "ENABLED": True,
                "TITLE": "Example Hotel",
                "DESCRIPTION": "Independent hotel on the Italian coast.",
                "SECTIONS": [
                    {
                        "heading": "Book",
                        "links": [
                            {
                                "title": "Rooms",
                                "url": "https://example.com/rooms/",
                                "notes": "Room types and amenities",
                            },
                        ],
                    },
                ],
            },
            "JSONLD": {"ENABLED": True, "PROFILES": ["sitewide", "lodging"]},
            "DISCOVERY": {"ENABLED": True},
            "WEBMCP": {"ENABLED": False},
            "COMMERCE": {"ENABLED": False},
            "SDF": {"ENABLED": False},
        },
    }

Reading config through this module (rather than settings dicts directly)
guarantees defaults are always applied.
"""

from __future__ import annotations

from typing import Any, Dict

from django.conf import settings

#: Canonical key inside ``settings.APP_CONFIG``.
APP_CONFIG_KEY = "agentweb"

#: Optional top-level Django setting (full-dict override; migration / tests).
SETTING_NAME = "AGENTWEB"

#: Default configuration for every domain. Merged shallowly with user config.
#: Editorial LLMS keys (TITLE, DESCRIPTION, BODY, SECTIONS) are **fallback**
#: when no admin ``LlmsDocument`` exists for the current site + language.
DEFAULTS: Dict[str, Dict[str, Any]] = {
    # Domain 1 — Readability (llms.txt / llms-full.txt).
    "LLMS": {
        "ENABLED": False,
        "TITLE": "",
        "DESCRIPTION": "",
        # Cache timeout (seconds) for the dynamic view; 0 disables caching.
        "CACHE_TIMEOUT": 3600,
        # Per-language variants at /{lang}/llms.txt plus root /llms.txt index.
        "I18N_VARIANTS": True,
        # Curated H2 sections: [{heading, links: [{title, url, notes?}]}]
        "SECTIONS": [],
        # Optional body paragraphs (Markdown) between summary and sections.
        "BODY": "",
        # URL substrings / path prefixes never emitted into llms.txt.
        "EXCLUDE_PATTERNS": [
            "/admin/",
            "/accounts/",
            "/private/",
            "/api/",
            "secret",
        ],
        # When True and SECTIONS empty, emit a minimal Docs section from
        # TITLE/DESCRIPTION only (no auto-crawl of the site in v1).
        "AUTO_SECTIONS": False,
    },
    # Domain 2 — Structured data (Schema.org / JSON-LD).
    "JSONLD": {
        "ENABLED": False,
        # Profile names resolved by agentweb.jsonld.profiles.
        "PROFILES": [],
    },
    # Domain 3 — Discovery (/.well-known agent descriptors + ai-catalog).
    "DISCOVERY": {
        "ENABLED": False,
        # Optional Web Bot Auth (RFC 9421) enforcement — requires the
        # ``webbotauth`` extra. Off by default.
        "WEB_BOT_AUTH": False,
        # Host display name / identifier for ai-catalog.json (ARD).
        "HOST_DISPLAY_NAME": "",
        "HOST_IDENTIFIER": "",
    },
    # Domain 4 — WebMCP (browser-native) + optional remote tool bridge.
    "WEBMCP": {
        "ENABLED": False,
        # "proxy" -> reach vendors server-side (recommended; needs ``webmcp``
        # extra). "client" -> agent calls vendor directly (not recommended).
        "DATA_SOURCE": "proxy",
        # When True, also expose the optional HTTP tool-invoke bridge for
        # headless/remote agents. Browser WebMCP does not need this.
        "REMOTE_BRIDGE": False,
    },
    # Domain 5a — Agentic commerce / booking.
    "COMMERCE": {
        "ENABLED": False,
        # Transactional flows delegated to a booking-engine vendor; this module
        # provides discovery + hooks only.
        "VENDOR": None,
    },
    # Domain 5b — SDF (single-promoter; behind flag, off by default).
    "SDF": {
        "ENABLED": False,
    },
}

#: Domains that expose URL modules (``jsonld`` is template-only).
URL_DOMAINS = ("LLMS", "DISCOVERY", "WEBMCP", "COMMERCE", "SDF")


def _user_config() -> Dict[str, Any]:
    """Return the user-supplied domain dict (not yet merged with defaults)."""
    top = getattr(settings, SETTING_NAME, None)
    if isinstance(top, dict) and top:
        return top
    app_config = getattr(settings, "APP_CONFIG", None) or {}
    block = app_config.get(APP_CONFIG_KEY)
    return dict(block) if isinstance(block, dict) else {}


def get_config() -> Dict[str, Dict[str, Any]]:
    """Return the full merged configuration (defaults + user overrides)."""
    user_config = _user_config()
    merged: Dict[str, Dict[str, Any]] = {}
    for domain, defaults in DEFAULTS.items():
        overrides = user_config.get(domain, {}) or {}
        merged[domain] = {**defaults, **overrides}
    return merged


def get_domain(domain: str) -> Dict[str, Any]:
    """Return the merged config dict for a single domain."""
    return get_config().get(domain.upper(), {})


def is_enabled(domain: str) -> bool:
    """Return ``True`` if ``domain`` is opted in for the current site."""
    return bool(get_domain(domain).get("ENABLED", False))
