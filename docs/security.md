# Security model

Agent-facing surfaces have a different threat model from ordinary site pages.

## Defaults

- Every domain is **off** until you set `ENABLED` in `APP_CONFIG["agentweb"]`.
- WebMCP **remote bridge** defaults to off (`REMOTE_BRIDGE: False`).
- Web Bot Auth defaults to off.

## Risks and mitigations

| Risk | Mitigation in this package |
|------|----------------------------|
| Prompt injection | Treat user/third-party content as untrusted; mark with hints; never embed secrets in tool output |
| Output injection | JSON-LD / WebMCP payloads escape script-breakout characters; do not mark untrusted strings safe |
| Data leakage | Opt-in domains; `EXCLUDE_PATTERNS` on llms sections; catalog only lists enabled domains |
| Unsafe tools | `readOnlyHint` / confirmation flags; transactional tools require human-in-the-loop |
| Headless bridge abuse | Keep `REMOTE_BRIDGE` off unless you accept CSRF-exempt POST invoke |
| Spoofed bots | Optional Web Bot Auth (`[webbotauth]` + `DISCOVERY.WEB_BOT_AUTH`) |

## Recommended production posture

1. Enable only domains you need (`LLMS` + `JSONLD` + `DISCOVERY` is a solid start).
2. Curate `LLMS.SECTIONS`; do not auto-publish admin or account URLs.
3. Use browser WebMCP with read-only tools; leave the remote bridge disabled.
4. Add Discovery middleware for honest `Link` advertisement without opening extra attack surface.
5. Review [SECURITY.md](https://github.com/DLRSP/django-agentweb/blob/main/.github/SECURITY.md) for reporting.

## Configuration pointers

- `WEBMCP.REMOTE_BRIDGE` — see [WebMCP](domains/webmcp.md)
- `DISCOVERY.WEB_BOT_AUTH` — see [Discovery](domains/discovery.md)
- Full keys — [Configuration](configuration.md)
