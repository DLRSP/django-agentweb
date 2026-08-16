# Configuration

All package options are read through `agentweb.conf`. Prefer configuring via
**`APP_CONFIG["agentweb"]`** so this package matches other reusable Django apps
that share a single nested settings dict.

## Precedence

1. Top-level `settings.AGENTWEB` — if set to a **non-empty dict**, it replaces
   the whole `APP_CONFIG["agentweb"]` block (useful for tests / one-shot
   overrides).
2. `settings.APP_CONFIG["agentweb"]` — **canonical** site configuration.
3. Package defaults in `agentweb.conf.DEFAULTS` (every domain `ENABLED: False`).

```python
from agentweb import conf

conf.is_enabled("LLMS")       # bool
conf.get_domain("LLMS")       # merged dict for one domain
conf.get_config()             # all domains, merged
```

Do not read raw `settings.APP_CONFIG` in your own code if you need defaults
applied — use `agentweb.conf`.

## Canonical shape

```python
APP_CONFIG = {
    "agentweb": {
        "LLMS": { ... },
        "JSONLD": { ... },
        "DISCOVERY": { ... },
        "WEBMCP": { ... },
        "COMMERCE": { ... },
        "SDF": { ... },
    },
}
```

Unknown domain keys are ignored. Within a domain, user keys **shallow-merge**
onto defaults (nested lists/dicts such as `SECTIONS` are replaced wholesale).

## Enablement checklist

Turning `ENABLED` on is necessary but not always sufficient.

| Domain | `ENABLED` | URLs auto? | Also configure / wire |
|--------|-----------|------------|------------------------|
| LLMS | yes | yes | Prefer **admin** LLMS documents (Site+language); settings `TITLE`/`SECTIONS` as fallback; optional `import_llms_from_settings` / `generate_llms_txt` |
| JSONLD | yes | no | `PROFILES` and/or Python builders; `{% load agentweb_jsonld %}` |
| DISCOVERY | yes | yes | optional middleware; optional `HOST_*` / `WEB_BOT_AUTH` |
| WEBMCP | yes | yes (manifest) | template tag; register tools; extras for proxy; optional `REMOTE_BRIDGE` |
| COMMERCE | yes | yes | optional `VENDOR` string |
| SDF | yes | yes | keep off unless you intentionally dogfood SDF |

### Middleware (Discovery)

```python
MIDDLEWARE = [
    # ...
    "agentweb.discovery.middleware.AgentwebDiscoveryMiddleware",
]
```

When `DISCOVERY` is enabled, responses gain `Link` headers pointing at the
catalog / agent descriptor, `X-Agentweb-Discovery: 1`, and (if `WEBMCP` is also
enabled) `Permissions-Policy: tools=(self)` when not already set.

### Template tags

| Library | Tags | Needed when |
|---------|------|-------------|
| `agentweb_jsonld` | `jsonld_script` | Embedding JSON-LD on HTML pages |
| `agentweb_webmcp` | `webmcp_register` | Browser WebMCP registration |
| `agentweb_webmcp_decl` | `webmcp_form_attrs`, `permissions_policy_tools` | Declarative form annotations |

### Management commands

```bash
python manage.py generate_llms_txt --output ./static/
python manage.py generate_llms_txt --output ./static/ --lang it
python manage.py import_llms_from_settings --site-id 1 --lang en
```

- `generate_llms_txt` — write static files (same resolve as the HTTP views).
- `import_llms_from_settings` — seed admin models from settings editorial keys
  (idempotent; never runs on migrate).

## Domain keys

### `LLMS`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Mount `/llms.txt` and `/llms-full.txt` |
| `TITLE` | str | `""` | Fallback H1 when no admin document |
| `DESCRIPTION` | str | `""` | Fallback blockquote summary |
| `BODY` | str | `""` | Fallback Markdown body |
| `SECTIONS` | list | `[]` | Fallback H2 blocks (see shape below) |
| `CACHE_TIMEOUT` | int | `3600` | Seconds; `0` disables caching |
| `I18N_VARIANTS` | bool | `True` | Advertise language variants in templates |
| `EXCLUDE_PATTERNS` | list | admin/accounts/… | Always applied after resolve (settings only) |
| `AUTO_SECTIONS` | bool | `False` | If no sections, emit minimal Docs placeholder |

**Editorial preferred path:** Django admin **LLMS documents** (per Site + language).
Settings keys above remain a supported fallback forever. See
[Readability](domains/llms.md).

Section shape:

```python
{
    "heading": "Book",
    "links": [
        {"title": "Rooms", "url": "https://example.com/rooms/", "notes": "optional"},
    ],
}
```

### `JSONLD`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Allow default profile resolution when names omitted |
| `PROFILES` | list[str] | `[]` | Default profile names for `build_from_profiles()` |

Profiles do not register URLs. See [Structured data](domains/jsonld.md).

### `DISCOVERY`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Mount `/.well-known/` discovery JSON |
| `WEB_BOT_AUTH` | bool | `False` | Enforce Web Bot Auth (needs `[webbotauth]` extra) |
| `HOST_DISPLAY_NAME` | str | `""` | Optional ARD host display name |
| `HOST_IDENTIFIER` | str | `""` | Optional ARD host identifier |

Catalog entries only list **other domains that are also enabled**.

### `WEBMCP`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Manifest URL + allow template registration |
| `DATA_SOURCE` | str | `"proxy"` | Reserved for future vendor-call posture (`proxy` vs `client`). Not read by runtime code yet — keep `"proxy"`; do not rely on it for security. |
| `REMOTE_BRIDGE` | bool | `False` | Allow HTTP `POST /webmcp/tools/<name>` for headless agents |

Browser WebMCP works with the template tag alone; the remote bridge is a
separate trust boundary — see [Security](security.md).

### `COMMERCE`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Mount `/.well-known/commerce.json` |
| `VENDOR` | str \| None | `None` | Optional booking-engine identifier for discovery |

### `SDF`

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ENABLED` | bool | `False` | Mount `/.well-known/sdf.json` (experimental) |

## Optional top-level override

```python
# Replaces APP_CONFIG["agentweb"] entirely when non-empty
AGENTWEB = {
    "LLMS": {"ENABLED": True, "TITLE": "Override"},
}
```

Prefer `APP_CONFIG` in project settings. Keep `AGENTWEB` for tests
(`override_settings`) or temporary migrations.

## Restart / reload notes

- Changing `ENABLED` for URL domains requires a **process restart** so
  `agentweb.urls` is re-imported.
- Changing content keys (`TITLE`, `SECTIONS`, profiles, …) is picked up on the
  next request (and after cache expiry for LLMS when `CACHE_TIMEOUT` > 0).

## Worked example (hotel-oriented site)

```python
APP_CONFIG = {
    "agentweb": {
        "LLMS": {
            "ENABLED": True,
            "TITLE": "Sea View Hotel",
            "DESCRIPTION": "Boutique hotel with direct booking.",
            "CACHE_TIMEOUT": 3600,
            "SECTIONS": [
                {
                    "heading": "Stay",
                    "links": [
                        {
                            "title": "Rooms",
                            "url": "https://example.com/rooms/",
                            "notes": "Types, amenities, photos",
                        },
                        {
                            "title": "Book",
                            "url": "https://example.com/book/",
                            "notes": "Direct reservation",
                        },
                    ],
                },
            ],
        },
        "JSONLD": {
            "ENABLED": True,
            "PROFILES": ["sitewide", "lodging", "lodging_room"],
        },
        "DISCOVERY": {
            "ENABLED": True,
            "HOST_DISPLAY_NAME": "Sea View Hotel",
        },
        "WEBMCP": {
            "ENABLED": True,
            "DATA_SOURCE": "proxy",
            "REMOTE_BRIDGE": False,
        },
        "COMMERCE": {
            "ENABLED": True,
            "VENDOR": "example-booking-engine",
        },
        "SDF": {"ENABLED": False},
    },
}

MIDDLEWARE = [
    # ...
    "agentweb.discovery.middleware.AgentwebDiscoveryMiddleware",
]
```

Then in the base HTML template:

```django
{% load agentweb_jsonld agentweb_webmcp %}
{# ... build `jsonld_doc` in the view context ... #}
{% jsonld_script jsonld_doc %}
{% webmcp_register %}
```
