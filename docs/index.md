# django-agentweb

Make your Django site a first-class citizen of the agentic web.

`django-agentweb` helps AI agents discover, understand and act on your site
across five opt-in domains: readability (`llms.txt`), structured data
(Schema.org/JSON-LD), agent discovery (`/.well-known`), WebMCP tools, and
agentic commerce/booking (plus SDF behind a flag).

Every domain is **off by default** and activated **per site** through the
`AGENTWEB` setting.

See [Getting started](getting-started.md).

!!! note "Status"
    Alpha. Core domains (llms.txt, JSON-LD profiles, discovery / ai-catalog /
    MCP server-card, browser WebMCP, CAP Lite) are implemented and opt-in per
    site. Booking adapters and extras (Web Bot Auth, full SDF) follow.
