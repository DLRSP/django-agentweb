Initial package scaffold: core ``agentweb`` app with per-site activation
(``APP_CONFIG["agentweb"]`` + feature flags) and sub-apps for the five agent-web
domains — readability (``llms.txt``), structured data (Schema.org/JSON-LD),
agent discovery (``/.well-known``), WebMCP tools, agentic commerce/booking and
SDF. Domains are opt-in per site and default to off.
