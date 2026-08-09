# django-agentweb

[![CI/CD](https://github.com/DLRSP/django-agentweb/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-agentweb/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/django-agentweb.svg)](https://pypi.org/project/django-agentweb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue)](https://dlrsp.github.io/django-agentweb/)

Make your Django site a **first-class citizen of the agentic web**.

`django-agentweb` is a reusable Django app that helps AI agents (and the LLMs
behind them) **discover, understand, and act on** your site — across five
complementary domains. Every domain is **opt-in per site** and **off by
default**, so you expose only what you choose.

> Status: **alpha**. Core domains (llms.txt, JSON-LD profiles, discovery /
> ai-catalog + MCP server-card, browser WebMCP, CAP Lite) are implemented and
> opt-in per site. Booking adapters and extras (Web Bot Auth, full SDF) follow.
> See the [roadmap](#roadmap).

## The five agent-web domains

| # | Domain | What it provides | Standard(s) |
|---|--------|------------------|-------------|
| 1 | **Readability** | `llms.txt` / `llms-full.txt`, per-language variants | `llms.txt` |
| 2 | **Structured data** | Schema.org JSON-LD (`Hotel`, `HotelRoom`, `Offer`, …) | Schema.org / JSON-LD |
| 3 | **Discovery** | `/.well-known/` agent descriptors & capability manifest | Agent-Ready Web |
| 4 | **WebMCP** | In-page tools agents can call (read-only by default) | Web Model Context Protocol |
| 5 | **Commerce / SDF** | Agentic booking/commerce discovery + hooks; SDF (flag, off) | CAP / UCP / AP2, SDF |

## Why

Search and assistants increasingly mediate discovery through agents. For an
independent hotel, that means letting an agent **check availability, simulate a
booking price, and start a direct reservation** — and reducing dependence on
OTAs (Booking.com / Expedia). The same building blocks benefit any content or
commerce site.

This package is intentionally **generic and externally adoptable**: it
implements all five domains even where a given deployment won't use them, to
maximise reuse and external visibility.

## Install

```bash
pip install django-agentweb            # core (pure Django)
pip install "django-agentweb[webmcp]"  # + server-side tool proxy
pip install "django-agentweb[all]"     # everything
```

Requires `django.contrib.sites`. Editable checkout for contributors:

```bash
pip install -e ".[testing]"
```

## Quickstart

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "agentweb",
]

AGENTWEB = {
    "LLMS": {"ENABLED": True},
    "JSONLD": {"ENABLED": True},
    "DISCOVERY": {"ENABLED": True},
    "WEBMCP": {"ENABLED": False},
    "COMMERCE": {"ENABLED": False},
    "SDF": {"ENABLED": False},
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

Only the domains you enable register any URLs or expose any data.

## Security

Agent-facing surfaces have a distinct threat model (prompt/output injection,
data leakage, unsafe tool calls). Transactional tools always require
human-in-the-loop. See [`SECURITY.md`](.github/SECURITY.md).

## Roadmap

Readability → structured data → discovery → WebMCP → commerce/booking → SDF,
followed by per-site rollout. See the package docs for the current domain status.

## License

MIT — see [`LICENSE`](LICENSE).
