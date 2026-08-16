# Structured data — Schema.org / JSON-LD

JSON-LD has **no URL module**. Enabling `JSONLD` does not add routes; you
embed graphs in HTML (or build them in views/APIs) using the Python helpers and
template tag.

## Checklist after `ENABLED`

1. Set `JSONLD.ENABLED = True` and optionally `PROFILES`.
2. Build a document in a view (builders, profiles, or `build_graph`).
3. Pass it to the template and render with `{% jsonld_script %}`.

```django
{% load agentweb_jsonld %}
{% jsonld_script jsonld_doc %}
```

The tag emits `<script type="application/ld+json">…</script>` with `<`, `>`,
`&` escaped so the payload cannot break out of the script element.

## Builders

Available helpers under `agentweb.jsonld` include:

`Organization`, `WebSite`, `WebPage`, `BreadcrumbList`, `Article`, `FAQPage`,
`Hotel`, `HotelRoom` (+ optional Product MTE), `Offer`, `UnitPriceSpecification`,
`AggregateOffer`, `Product`, plus additive `Person`, `Recipe`, `LocalBusiness`
(default subtype `HomeAndConstructionBusiness`), `Review`.

`Website` is normalized to `WebSite`.

## Graph policy

```python
from agentweb.jsonld import build_graph, build_organization

doc = build_graph(
    build_organization(name="Acme", url="https://example.com/", context=False),
)
# → {"@context": "https://schema.org", "@graph": [...]}  # deduped by @id
```

## Profiles

MVP: `sitewide`, `breadcrumb`, `article`, `faq`, `lodging`, `lodging_room`  
Additive: `recipe`, `person`, `local_business`, `review`

```python
APP_CONFIG = {
    "agentweb": {
        "JSONLD": {
            "ENABLED": True,
            "PROFILES": ["sitewide", "lodging"],
        },
    },
}
```

```python
from agentweb.jsonld import build_from_profiles

doc = build_from_profiles(
    ["sitewide", "lodging"],
    context={
        "site_url": "https://example.com/",
        "hotel_name": "Sea Hotel",
    },
)
```

If `names` is omitted, `build_from_profiles()` uses `JSONLD.PROFILES`. If that
list is empty but the domain is enabled, MVP profiles are used.

## Verify

1. Render a page that includes `{% jsonld_script doc %}`.
2. View source: one `application/ld+json` script with valid JSON.
3. Optionally paste into a Schema.org / Rich Results tester.

See [Configuration](../configuration.md#jsonld).
