"""Schema.org JSON-LD builders (native dicts, no third-party JSON-LD libs).

Keys with ``None`` values are dropped. Pass ``context=False`` when a node will
sit inside a ``build_graph`` ``@graph`` that already declares ``@context``.
The typo ``Website`` is normalized to ``WebSite`` via :func:`normalize_type`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

TYPE_ALIASES = {
    "Website": "WebSite",
    "website": "WebSite",
}


def normalize_type(type_name: str) -> str:
    """Normalize known Schema.org type misspellings (e.g. Website → WebSite)."""
    return TYPE_ALIASES.get(type_name, type_name)


def _clean(data: Dict[str, Any]) -> Dict[str, Any]:
    """Drop keys whose value is ``None`` (recursively for nested dicts)."""
    cleaned: Dict[str, Any] = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, dict):
            value = _clean(value)
        elif isinstance(value, list):
            value = [
                _clean(item) if isinstance(item, dict) else item
                for item in value
                if item is not None
            ]
        cleaned[key] = value
    return cleaned


def _with_id(node: Dict[str, Any], node_id: Optional[str]) -> Dict[str, Any]:
    if node_id:
        node = {"@id": node_id, **node}
    return node


def _maybe_context(node: Dict[str, Any], context: bool) -> Dict[str, Any]:
    if context:
        return {"@context": "https://schema.org", **node}
    return node


def build_organization(
    *,
    name: str,
    url: Optional[str] = None,
    logo: Optional[str] = None,
    same_as: Optional[Sequence[str]] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build an ``Organization`` node."""
    node = _with_id(
        {
            "@type": "Organization",
            "name": name,
            "url": url,
            "logo": logo,
            "sameAs": list(same_as) if same_as else None,
        },
        node_id or (f"{url.rstrip('#')}#organization" if url else None),
    )
    return _maybe_context(_clean(node), context)


def build_website(
    *,
    name: str,
    url: str,
    publisher: Optional[Union[str, Dict[str, Any]]] = None,
    in_language: Optional[str] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``WebSite`` node (never ``Website``)."""
    pub = publisher
    if isinstance(publisher, str):
        pub = {"@id": publisher}
    node = _with_id(
        {
            "@type": "WebSite",
            "name": name,
            "url": url,
            "publisher": pub,
            "inLanguage": in_language,
        },
        node_id or f"{url.rstrip('#')}#website",
    )
    return _maybe_context(_clean(node), context)


def build_webpage(
    *,
    name: str,
    url: str,
    description: Optional[str] = None,
    is_part_of: Optional[Union[str, Dict[str, Any]]] = None,
    breadcrumb: Optional[Union[str, Dict[str, Any]]] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``WebPage`` node."""
    part = is_part_of
    if isinstance(is_part_of, str):
        part = {"@id": is_part_of}
    crumb = breadcrumb
    if isinstance(breadcrumb, str):
        crumb = {"@id": breadcrumb}
    node = _with_id(
        {
            "@type": "WebPage",
            "name": name,
            "url": url,
            "description": description,
            "isPartOf": part,
            "breadcrumb": crumb,
        },
        node_id or url,
    )
    return _maybe_context(_clean(node), context)


def build_breadcrumb(
    items: Sequence[Dict[str, str]],
    *,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``BreadcrumbList`` from ``[{name, url}, ...]``."""
    elements = []
    for position, item in enumerate(items, start=1):
        elements.append(
            _clean(
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": item.get("name"),
                    "item": item.get("url"),
                }
            )
        )
    node = _with_id(
        {"@type": "BreadcrumbList", "itemListElement": elements},
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_article(
    *,
    headline: str,
    url: Optional[str] = None,
    description: Optional[str] = None,
    date_published: Optional[str] = None,
    date_modified: Optional[str] = None,
    author: Optional[Union[str, Dict[str, Any]]] = None,
    image: Optional[str] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build an ``Article`` node."""
    auth = author
    if isinstance(author, str):
        auth = {"@type": "Person", "name": author}
    node = _with_id(
        {
            "@type": "Article",
            "headline": headline,
            "url": url,
            "description": description,
            "datePublished": date_published,
            "dateModified": date_modified,
            "author": auth,
            "image": image,
        },
        node_id or url,
    )
    return _maybe_context(_clean(node), context)


def build_faq(
    questions: Sequence[Dict[str, str]],
    *,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build an ``FAQPage`` from ``[{question, answer}, ...]``."""
    entities = []
    for qa in questions:
        entities.append(
            _clean(
                {
                    "@type": "Question",
                    "name": qa.get("question"),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": qa.get("answer"),
                    },
                }
            )
        )
    node = _with_id(
        {"@type": "FAQPage", "mainEntity": entities},
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_person(
    *,
    name: str,
    url: Optional[str] = None,
    job_title: Optional[str] = None,
    image: Optional[str] = None,
    same_as: Optional[Sequence[str]] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``Person`` node (author / personal-site profiles)."""
    node = _with_id(
        {
            "@type": "Person",
            "name": name,
            "url": url,
            "jobTitle": job_title,
            "image": image,
            "sameAs": list(same_as) if same_as else None,
        },
        node_id or url,
    )
    return _maybe_context(_clean(node), context)


def build_local_business(
    *,
    name: str,
    url: Optional[str] = None,
    telephone: Optional[str] = None,
    address: Optional[Dict[str, Any]] = None,
    business_type: str = "LocalBusiness",
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``LocalBusiness`` (or subtype e.g. HomeAndConstructionBusiness)."""
    type_name = normalize_type(business_type)
    node = _with_id(
        {
            "@type": type_name,
            "name": name,
            "url": url,
            "telephone": telephone,
            "address": address,
        },
        node_id or (f"{url.rstrip('#')}#business" if url else None),
    )
    return _maybe_context(_clean(node), context)


def build_recipe(
    *,
    name: str,
    description: Optional[str] = None,
    recipe_ingredient: Optional[Sequence[str]] = None,
    recipe_instructions: Optional[Sequence[str]] = None,
    image: Optional[str] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``Recipe`` node (additive profile for content sites)."""
    instructions = None
    if recipe_instructions:
        instructions = [
            {"@type": "HowToStep", "text": step} for step in recipe_instructions
        ]
    node = _with_id(
        {
            "@type": "Recipe",
            "name": name,
            "description": description,
            "recipeIngredient": (
                list(recipe_ingredient) if recipe_ingredient else None
            ),
            "recipeInstructions": instructions,
            "image": image,
        },
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_review(
    *,
    item_name: str,
    review_body: Optional[str] = None,
    rating_value: Optional[Any] = None,
    best_rating: Optional[Any] = 5,
    author: Optional[str] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``Review`` node."""
    rating = None
    if rating_value is not None:
        rating = _clean(
            {
                "@type": "Rating",
                "ratingValue": rating_value,
                "bestRating": best_rating,
            }
        )
    node = _with_id(
        {
            "@type": "Review",
            "itemReviewed": {"@type": "Thing", "name": item_name},
            "reviewBody": review_body,
            "reviewRating": rating,
            "author": {"@type": "Person", "name": author} if author else None,
        },
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_product(
    *,
    name: str,
    description: Optional[str] = None,
    sku: Optional[str] = None,
    offers: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    image: Optional[str] = None,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``Product`` node (CAP Lite / lodging room MTE)."""
    node = _with_id(
        {
            "@type": "Product",
            "name": name,
            "description": description,
            "sku": sku,
            "offers": offers,
            "image": image,
        },
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_aggregate_offer(
    *,
    low_price: Any,
    high_price: Any,
    currency: str,
    offer_count: Optional[int] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build an ``AggregateOffer`` node."""
    node = {
        "@type": "AggregateOffer",
        "lowPrice": low_price,
        "highPrice": high_price,
        "priceCurrency": currency,
        "offerCount": offer_count,
    }
    return _maybe_context(_clean(node), context)


def build_price_specification(
    price: Any,
    currency: str,
    *,
    unit_code: Optional[str] = None,
    valid_from: Optional[str] = None,
    valid_through: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a ``UnitPriceSpecification`` node."""
    return _clean(
        {
            "@type": "UnitPriceSpecification",
            "price": price,
            "priceCurrency": currency,
            "unitCode": unit_code,
            "validFrom": valid_from,
            "validThrough": valid_through,
        }
    )


def build_offer(
    *,
    price: Any,
    currency: str,
    availability: Optional[str] = None,
    url: Optional[str] = None,
    valid_from: Optional[str] = None,
    valid_through: Optional[str] = None,
    price_specification: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build an ``Offer`` node."""
    return _clean(
        {
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "availability": availability,
            "url": url,
            "validFrom": valid_from,
            "validThrough": valid_through,
            "priceSpecification": price_specification,
        }
    )


def build_hotel_room(
    *,
    name: str,
    description: Optional[str] = None,
    occupancy: Optional[int] = None,
    bed_type: Optional[str] = None,
    offers: Optional[List[Dict[str, Any]]] = None,
    amenities: Optional[Sequence[str]] = None,
    as_product: bool = False,
    node_id: Optional[str] = None,
    context: bool = False,
) -> Dict[str, Any]:
    """Build a ``HotelRoom`` node; optionally multi-type ``[HotelRoom, Product]``."""
    types: Union[str, List[str]] = (
        ["HotelRoom", "Product"] if as_product else "HotelRoom"
    )
    amenity_features = None
    if amenities:
        amenity_features = [
            {"@type": "LocationFeatureSpecification", "name": a}
            for a in amenities
        ]
    node = _with_id(
        {
            "@type": types,
            "name": name,
            "description": description,
            "occupancy": occupancy,
            "bed": bed_type,
            "offers": offers,
            "amenityFeature": amenity_features,
        },
        node_id,
    )
    return _maybe_context(_clean(node), context)


def build_hotel(
    *,
    name: str,
    url: Optional[str] = None,
    description: Optional[str] = None,
    address: Optional[Dict[str, Any]] = None,
    telephone: Optional[str] = None,
    star_rating: Optional[Any] = None,
    rooms: Optional[List[Dict[str, Any]]] = None,
    node_id: Optional[str] = None,
    context: bool = True,
) -> Dict[str, Any]:
    """Build a ``Hotel`` / ``LodgingBusiness``-compatible node."""
    rating = None
    if star_rating is not None:
        rating = {"@type": "Rating", "ratingValue": star_rating}
    node = _with_id(
        {
            "@type": "Hotel",
            "name": name,
            "url": url,
            "description": description,
            "address": address,
            "telephone": telephone,
            "starRating": rating,
            "containsPlace": rooms,
        },
        node_id or (f"{url.rstrip('#')}#hotel" if url else None),
    )
    return _maybe_context(_clean(node), context)


def prices_match(jsonld_price: Any, visible_price: Any) -> bool:
    """Return True when JSON-LD offer price matches the visible UI price."""
    try:
        return float(jsonld_price) == float(visible_price)
    except (TypeError, ValueError):
        return str(jsonld_price).strip() == str(visible_price).strip()
