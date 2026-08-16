# django-agentweb

Make your Django site a first-class citizen of the agentic web.

`django-agentweb` helps AI agents discover, understand and act on your site
across five opt-in domains: readability (`llms.txt`), structured data
(Schema.org/JSON-LD), agent discovery (`/.well-known`), WebMCP tools, and
agentic commerce/booking (plus SDF behind a flag).

Every domain is **off by default** and activated **per site** through
`APP_CONFIG["agentweb"]`.

| Guide | When to read it |
|-------|-----------------|
| [Getting started](getting-started.md) | Install, apps, URLs, and “what else do I need?” |
| [Configuration](configuration.md) | Full `APP_CONFIG` reference and enablement checklist |
| [Domains](domains/llms.md) | How each feature is used day to day |
| [Security](security.md) | Threat model for agent-facing surfaces |

!!! note "Status"
    Alpha. Core domains (llms.txt, JSON-LD profiles, discovery / ai-catalog /
    MCP server-card, browser WebMCP, CAP Lite) are implemented and opt-in.
    Booking adapters and extras (Web Bot Auth, full SDF) follow.
