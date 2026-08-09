# Structured data — Schema.org / JSON-LD

Native builders + a single `@graph` assembler + consumer-agnostic **profiles**.

## Builders

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
from agentweb.jsonld import build_from_profiles

doc = build_from_profiles(
    ["sitewide", "lodging"],
    context={"site_url": "https://example.com/", "hotel_name": "Sea Hotel"},
)
```

```django
{% load agentweb_jsonld %}
{% jsonld_script doc %}
```

Configure defaults via `AGENTWEB["JSONLD"]["PROFILES"]`.
