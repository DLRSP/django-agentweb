"""CAP Lite helpers — Product/Offer JSON-LD for agentic commerce discovery."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from agentweb.jsonld import builders


def build_cap_lite_product(
    *,
    name: str,
    price: Any,
    currency: str = "EUR",
    description: Optional[str] = None,
    url: Optional[str] = None,
    sku: Optional[str] = None,
    availability: str = "https://schema.org/InStock",
) -> Dict[str, Any]:
    """Build a Product+Offer graph suitable for CAP Lite surfaces."""
    offer = builders.build_offer(
        price=price,
        currency=currency,
        availability=availability,
        url=url,
    )
    return builders.build_product(
        name=name,
        description=description,
        sku=sku,
        offers=offer,
        context=True,
    )


def build_cap_lite_catalog(
    products: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Wrap product nodes in a single ``@graph`` document."""
    from agentweb.jsonld.graph import build_graph

    nodes: List[Dict[str, Any]] = []
    for item in products:
        nodes.append(
            build_cap_lite_product(
                name=item["name"],
                price=item["price"],
                currency=item.get("currency", "EUR"),
                description=item.get("description"),
                url=item.get("url"),
                sku=item.get("sku"),
                availability=item.get(
                    "availability", "https://schema.org/InStock"
                ),
            )
        )
    # Strip per-node @context before graphing.
    stripped = [{k: v for k, v in n.items() if k != "@context"} for n in nodes]
    return build_graph(*stripped)
