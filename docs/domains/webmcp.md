# WebMCP — Web Model Context Protocol

**Browser-native** WebMCP (Chrome origin trial / W3C WebML CG) registers tools
on the page via `navigator.modelContext` (or `document.modelContext`).

Use the template tag:

```django
{% load agentweb_webmcp %}
{% webmcp_register %}
```

This embeds tool descriptors and loads `agentweb/webmcp.js`, which registers
tools when the browser API is present (progressive enhancement).

Tools are **read-only by default** and declare `readOnlyHint` / `exposedTo`.
State-changing tools require human-in-the-loop confirmation.

An optional HTTP **remote bridge** (`/webmcp/tools/<name>`) exists for headless
agents when `WEBMCP.REMOTE_BRIDGE` is True — it is **not** a substitute for
in-browser WebMCP.
