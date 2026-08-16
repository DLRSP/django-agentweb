# Commerce & booking

Discovery and hooks for agentic commerce/booking (CAP / UCP for Lodging / AP2).

Typical independent-hotel goals: **check availability**, **simulate a price**,
and **start a direct reservation**. Full transactional flows stay with your
booking-engine vendor; this package exposes a discovery descriptor and
integration hooks.

## Checklist after `ENABLED`

1. `COMMERCE.ENABLED = True`.
2. Include `agentweb.urls`.
3. Optionally set `VENDOR` to an opaque booking-engine identifier.
4. Wire real booking APIs in your project (or via WebMCP tools) — this domain
   does not replace the booking engine.

```python
APP_CONFIG = {
    "agentweb": {
        "COMMERCE": {
            "ENABLED": True,
            "VENDOR": "example-booking-engine",
        },
    },
}
```

Optional extra for HTTP helpers:

```bash
pip install "django-agentweb[commerce]"
```

## URL

| URL | Name |
|-----|------|
| `/.well-known/commerce.json` | `agentweb-commerce-descriptor` |

When Discovery is also enabled, the ai-catalog can advertise this surface.

## CAP Lite helpers

For product/catalog payloads you can embed in JSON-LD or return from WebMCP
tools (read-only probes), use the CAP Lite builders:

```python
from agentweb.commerce import build_cap_lite_product, build_cap_lite_catalog

room = build_cap_lite_product(
    name="Deluxe Room",
    description="Sea view, king bed",
    url="https://example.com/rooms/deluxe/",
    price="120.00",
    currency="EUR",
    sku="room-deluxe",
)

catalog = build_cap_lite_catalog(
    [
        {
            "name": "Deluxe Room",
            "price": "120.00",
            "currency": "EUR",
            "description": "Sea view, king bed",
            "url": "https://example.com/rooms/deluxe/",
            "sku": "room-deluxe",
        },
    ],
)
```

Combine with [JSON-LD](jsonld.md) (`{% jsonld_script %}`) or a read-only WebMCP
tool when agents need structured offers. Checkout and payment stay with the
booking vendor and should remain human-confirmed.

## Status

Descriptor, CAP Lite builders, and hooks are available; deep booking adapters
continue to evolve. Prefer WebMCP read-only tools for availability/price probes
while keeping checkout human-confirmed.

See [Configuration](../configuration.md#commerce).
