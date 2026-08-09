# Security Policy

## Reporting a Vulnerability

Please report security issues privately to **dlrsp.dev@gmail.com** or via GitHub
Security Advisories. Do not open public issues for vulnerabilities.

## Agentic-web threat model (project-specific)

`django-agentweb` exposes content and tools intended for autonomous AI agents.
Treat the following as first-class security concerns:

- **Prompt injection** — any user-generated or third-party content surfaced in
  `llms.txt`, JSON-LD, discovery documents or WebMCP tool descriptions must be
  treated as untrusted. Mark such content with `untrustedContentHint` and never
  embed secrets or internal instructions.
- **Output injection** — agent-facing endpoints must not reflect unsanitised
  input back into structured responses.
- **Data leakage** — discovery and tool endpoints expose only what each site
  explicitly opts into. Defaults are off; nothing is exposed without
  per-site activation.
- **Tool safety** — WebMCP tools declare `readOnlyHint` / `exposedTo`; any
  state-changing or transactional tool (booking, payment) requires
  human-in-the-loop confirmation and never executes silently. The optional
  HTTP remote bridge (`WEBMCP.REMOTE_BRIDGE`) defaults to off and is
  CSRF-exempt for headless agents; keep it disabled unless you accept that
  trust boundary, and never classify session-sensitive reads as read-only.
- **Agent authentication** — optional Web Bot Auth (RFC 9421, `webbotauth`
  extra) verifies signed agent requests where enforcement is required.

See `docs/security.md` for the full per-domain model.
