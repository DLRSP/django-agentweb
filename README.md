# django-agentweb

[![CI/CD](https://github.com/DLRSP/django-agentweb/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-agentweb/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/django-agentweb.svg)](https://pypi.org/project/django-agentweb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue)](https://dlrsp.github.io/django-agentweb/)

Make your Django site a **first-class citizen of the agentic web**.

`django-agentweb` helps AI agents discover, understand, and act on your site
across five complementary domains. Every domain is **opt-in** and **off by
default**.

> Status: **alpha**. Core domains are implemented and opt-in. Booking adapters
> and some extras follow — see the [docs](https://dlrsp.github.io/django-agentweb/).

## Domains

| Domain | What it provides |
|--------|------------------|
| **Readability** | `llms.txt` / `llms-full.txt` |
| **Structured data** | Schema.org JSON-LD profiles |
| **Discovery** | `/.well-known/` agent descriptors |
| **WebMCP** | In-page tools agents can call |
| **Commerce / SDF** | Booking discovery hooks; SDF (flag, off) |

## Install

```bash
pip install django-agentweb
pip install "django-agentweb[webmcp]"   # optional: server-side tool proxy
pip install "django-agentweb[all]"      # optional: all extras
```

Requires `django.contrib.sites`.

## Quickstart

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "agentweb",
]

APP_CONFIG = {
    "agentweb": {
        "LLMS": {"ENABLED": True},  # content: admin LLMS documents (or settings fallback)
        "JSONLD": {"ENABLED": True},
        "DISCOVERY": {"ENABLED": True},
    },
}
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("", include("agentweb.urls")),
]
```

Enabling a domain alone is not always enough: some features need middleware,
template tags, or a management command. See the
[Getting started](https://dlrsp.github.io/django-agentweb/getting-started/)
and [Configuration](https://dlrsp.github.io/django-agentweb/configuration/)
guides.

## License

MIT — see [`LICENSE`](LICENSE).
