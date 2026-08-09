"""WebMCP domain — browser-native tools + optional remote bridge.

Primary surface: in-page registration via ``navigator.modelContext``
(Chrome WebMCP origin trial / W3C WebML CG), driven by ``{% webmcp_register %}``
and ``static/agentweb/webmcp.js``.

Secondary (opt-in): HTTP tool-invoke bridge at ``/webmcp/tools/<name>`` when
``WEBMCP.REMOTE_BRIDGE`` is True — for headless agents, **not** a substitute
for browser WebMCP.

Tools are **read-only by default** and declare ``readOnlyHint`` / ``exposedTo``;
state-changing tools require human-in-the-loop confirmation.
"""
