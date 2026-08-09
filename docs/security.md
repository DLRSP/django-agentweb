# Security model

Agent-facing surfaces require an explicit threat model:

- **Prompt injection** — user/third-party content surfaced to agents is
  untrusted; mark it with `untrustedContentHint`, never embed secrets.
- **Output injection** — never reflect unsanitised input into structured
  responses.
- **Data leakage** — nothing is exposed without explicit per-site activation;
  defaults are off.
- **Tool safety** — `readOnlyHint` / `exposedTo` on every WebMCP tool;
  transactional tools require human-in-the-loop. The optional HTTP remote
  bridge (`WEBMCP.REMOTE_BRIDGE`, default off) is CSRF-exempt by design for
  headless callers; do not mark session-sensitive reads as read-only, and keep
  the bridge disabled unless you accept that trust boundary.
- **Agent authentication** — optional Web Bot Auth (RFC 9421) via the
  `webbotauth` extra.

See [`SECURITY.md`](https://github.com/DLRSP/django-agentweb/blob/main/.github/SECURITY.md).
