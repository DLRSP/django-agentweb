"""Structured-data domain — Schema.org / JSON-LD.

Builders, ``build_graph`` assembler, and a consumer-agnostic profile registry
(``sitewide``, ``breadcrumb``, ``article``, ``faq``, ``lodging``,
``lodging_room``, plus additive ``recipe`` / ``person`` / ``local_business`` /
``review``). Render with ``{% jsonld_script %}``.
"""

from .builders import (  # noqa: F401
    build_aggregate_offer,
    build_article,
    build_breadcrumb,
    build_faq,
    build_hotel,
    build_hotel_room,
    build_local_business,
    build_offer,
    build_organization,
    build_person,
    build_price_specification,
    build_product,
    build_recipe,
    build_review,
    build_webpage,
    build_website,
    normalize_type,
    prices_match,
)
from .graph import build_graph, merge_graphs  # noqa: F401
from .profiles import (  # noqa: F401
    MVP_PROFILES,
    PROFILES,
    build_from_profiles,
    resolve_profiles,
)
