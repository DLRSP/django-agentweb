# Getting started

This page gets you from a blank Django project to working agent-web surfaces.
After apps + URLs, **each domain may need one or two extra steps** (middleware,
template tags, content, commands). The checklist below answers “is that all?”.

## 1. Install from PyPI

```bash
pip install django-agentweb
```

Optional extras (only if you need them):

```bash
pip install "django-agentweb[webmcp]"      # server-side vendor proxy helpers
pip install "django-agentweb[webbotauth]"  # Web Bot Auth (RFC 9421)
pip install "django-agentweb[commerce]"   # commerce HTTP helpers
pip install "django-agentweb[all]"        # all of the above
```

Requires Python 3.10+, Django 3.2+, and `django.contrib.sites` in
`INSTALLED_APPS`.

## 2. Register the app

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "agentweb",
]
```

Set `SITE_ID` as usual for `django.contrib.sites`.

## 3. Configure domains (`APP_CONFIG`)

Canonical configuration lives under **`APP_CONFIG["agentweb"]`**. Domains you
omit (or leave with `ENABLED: False`) stay inactive.

```python
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
        # Keep others off until you need them:
        # "WEBMCP": {"ENABLED": False},
        # "COMMERCE": {"ENABLED": False},
        # "SDF": {"ENABLED": False},
    },
}
```

Full key reference: [Configuration](configuration.md).

## 4. Include URLs once

```python
# project urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("", include("agentweb.urls")),
]
```

`agentweb.urls` only mounts routes for **enabled** domains (evaluated when the
URLconf is imported). After changing `ENABLED` flags, restart the process so
URL patterns reload.

| Domain enabled | Routes you get |
|----------------|----------------|
| `LLMS` | `/llms.txt`, `/llms-full.txt` |
| `DISCOVERY` | `/.well-known/agent.json`, `ai-catalog.json`, `mcp/server-card.json` |
| `WEBMCP` | `/.well-known/webmcp.json`, optional `/webmcp/tools/<name>` |
| `COMMERCE` | `/.well-known/commerce.json` |
| `SDF` | `/.well-known/sdf.json` |
| `JSONLD` | *(no URL module — template tags / Python API only)* |

## 5. After apps + URLs — what else?

| Domain | Extra steps required? | What to do |
|--------|----------------------|------------|
| **LLMS** | Content yes; command optional | Prefer admin **LLMS documents** (Site + language). Settings `TITLE`/`SECTIONS` work as fallback. Optional: `import_llms_from_settings`, `generate_llms_txt`. |
| **JSONLD** | Yes (templates or views) | Build a graph in Python or enable profiles, then `{% jsonld_script %}` in the page. |
| **DISCOVERY** | Middleware recommended | Add `agentweb.discovery.middleware.AgentwebDiscoveryMiddleware` so responses advertise the catalog via `Link`. |
| **WEBMCP** | Yes (templates + tools) | `{% webmcp_register %}` in base template; register tools in Python; optional remote bridge. |
| **COMMERCE** | Minimal | Descriptor URL is enough for discovery; wire a vendor when you need booking. |
| **SDF** | Minimal | Descriptor URL only while the format is experimental. |

Detailed per-domain guides are under **Domains** in the nav.

## Minimal verification

With `LLMS` and `DISCOVERY` enabled:

```bash
python manage.py runserver
# open http://127.0.0.1:8000/llms.txt
# open http://127.0.0.1:8000/.well-known/ai-catalog.json
```

## Next

- [Configuration reference](configuration.md) — every key and the enablement matrix
- [Security](security.md) — before enabling WebMCP remote bridge or bot auth
