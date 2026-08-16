# SDF — Structured Data Format

Single-promoter emerging format. Implemented behind a feature flag, **off by
default**, for dogfooding and demos only.

## Checklist after `ENABLED`

1. Understand that SDF support is experimental.
2. `SDF.ENABLED = True` only if you intentionally want the descriptor public.
3. Include `agentweb.urls`.

```python
APP_CONFIG = {
    "agentweb": {
        "SDF": {"ENABLED": False},  # keep off in production unless intentional
    },
}
```

## URL

| URL | Name |
|-----|------|
| `/.well-known/sdf.json` | `agentweb-sdf-descriptor` |

No middleware or template tags. Prefer mature domains (llms, JSON-LD, discovery,
WebMCP) for production agent readiness.

See [Configuration](../configuration.md#sdf).
