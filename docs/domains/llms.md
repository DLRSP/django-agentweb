# Readability — llms.txt

Serves a curated Markdown summary so agents can understand your site without
scraping HTML ([llmstxt.org](https://llmstxt.org/)).

## What you get after enabling

With `LLMS.ENABLED = True` and `path("", include("agentweb.urls"))`:

| URL | Name | Content |
|-----|------|---------|
| `/llms.txt` | `agentweb-llms-txt` | Concise curated summary |
| `/llms-full.txt` | `agentweb-llms-full-txt` | Longer variant (`full` flag in template) |

- **Content-Type:** `text/plain; charset=utf-8`
- **Shape:** H1 title, blockquote summary, optional body, H2 link sections
- **Caching:** keyed by **site + language** (`CACHE_TIMEOUT`; `0` disables)

No middleware or template tags are required for the HTTP views.

## Two ways to supply content (hybrid)

| Layer | What it stores | Who edits it |
|-------|----------------|--------------|
| **Admin (recommended)** | Title, description, body, sections/links per **Site + language** | Content managers |
| **`APP_CONFIG` (fallback)** | Same editorial keys + infra flags | Developers / deploy |

**Precedence:** if an **LLMS document** exists for the current site and language,
that whole document wins. Otherwise settings `TITLE` / `DESCRIPTION` / `BODY` /
`SECTIONS` are used. **`EXCLUDE_PATTERNS`**, **`ENABLED`**, and **`CACHE_TIMEOUT`**
always come from `APP_CONFIG` (never from admin).

### Recommended: Django admin

1. Enable `LLMS` and run migrations (`python manage.py migrate`).
2. Create a staff group **Agentweb content managers** with only:
   `agentweb.view_llmsdocument`, `add_llmsdocument`, `change_llmsdocument`,
   `delete_llmsdocument` (plus `sites.view_site` if the Site dropdown is used).
3. In admin → **LLMS documents**: set Site, Language, Title, Description, Body.
4. Add **Sections** on the document; open each section to add **Links**.
5. Open `/llms.txt` — you should see the admin title.

Content managers must **not** receive permission to edit security flags
(`REMOTE_BRIDGE`, `WEB_BOT_AUTH`, domain `ENABLED`) — those stay in settings.

### Fallback / bootstrap via settings

```python
APP_CONFIG = {
    "agentweb": {
        "LLMS": {
            "ENABLED": True,
            "TITLE": "Example Hotel",
            "DESCRIPTION": "Independent hotel on the Italian coast.",
            "BODY": "Optional Markdown paragraphs.",
            "CACHE_TIMEOUT": 3600,
            "I18N_VARIANTS": True,
            "EXCLUDE_PATTERNS": ["/admin/", "/accounts/", "/private/", "/api/", "secret"],
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
    },
}
```

### Import settings → admin (optional)

One-shot (or re-runnable) seed from settings into the database:

```bash
python manage.py import_llms_from_settings
python manage.py import_llms_from_settings --site-id 1 --lang en
```

Idempotent: updates the document and replaces sections/links. Does **not** run
on `migrate`.

## Management command (static files)

Dynamic views are enough for most sites. To pre-render static files:

```bash
python manage.py generate_llms_txt --output ./static/
python manage.py generate_llms_txt --output ./static/ --lang it --site-id 1
```

Uses the same resolve path as the HTTP views (DB override or settings fallback).

## i18n

Language-prefixed paths such as `/it/llms.txt` resolve the document for that
language code. Create one LLMS document per language you need.

## Verify

1. `ENABLED: True`, migrate, restart.
2. Either fill admin **or** settings editorial keys.
3. `GET /llms.txt` → `200`, starts with `# Your Title`.
4. Confirm private URLs do not appear when matching `EXCLUDE_PATTERNS`.

See [Configuration](../configuration.md#llms).
