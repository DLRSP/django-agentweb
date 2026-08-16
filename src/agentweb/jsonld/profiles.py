"""JSON-LD profile registry — consumer-agnostic page contracts.

MVP profiles: ``sitewide``, ``breadcrumb``, ``article``, ``faq``, ``lodging``,
``lodging_room``. Additive: ``recipe``, ``person``, ``local_business``,
``review``.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence

from .. import conf
from . import builders
from .graph import build_graph

ProfileFn = Callable[[Dict[str, Any]], List[Dict[str, Any]]]


def _sitewide(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    site_url = ctx.get("site_url") or ""
    name = ctx.get("organization_name") or ctx.get("site_name") or site_url
    org = builders.build_organization(
        name=name,
        url=site_url or None,
        logo=ctx.get("logo"),
        same_as=ctx.get("same_as"),
        context=False,
    )
    web = builders.build_website(
        name=ctx.get("site_name") or name,
        url=site_url,
        publisher=org.get("@id"),
        in_language=ctx.get("in_language"),
        context=False,
    )
    nodes = [org, web]
    if ctx.get("page_name") and ctx.get("page_url"):
        nodes.append(
            builders.build_webpage(
                name=ctx["page_name"],
                url=ctx["page_url"],
                description=ctx.get("page_description"),
                is_part_of=web.get("@id"),
                context=False,
            )
        )
    return nodes


def _breadcrumb(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = ctx.get("breadcrumb_items") or []
    if not items:
        return []
    return [
        builders.build_breadcrumb(
            items,
            node_id=ctx.get("breadcrumb_id"),
            context=False,
        )
    ]


def _article(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("headline"):
        return []
    return [
        builders.build_article(
            headline=ctx["headline"],
            url=ctx.get("url"),
            description=ctx.get("description"),
            date_published=ctx.get("date_published"),
            date_modified=ctx.get("date_modified"),
            author=ctx.get("author"),
            image=ctx.get("image"),
            context=False,
        )
    ]


def _faq(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    questions = ctx.get("faq_questions") or []
    if not questions:
        return []
    return [
        builders.build_faq(questions, node_id=ctx.get("faq_id"), context=False)
    ]


def _lodging(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("hotel_name"):
        return []
    return [
        builders.build_hotel(
            name=ctx["hotel_name"],
            url=ctx.get("hotel_url"),
            description=ctx.get("hotel_description"),
            address=ctx.get("address"),
            telephone=ctx.get("telephone"),
            star_rating=ctx.get("star_rating"),
            rooms=ctx.get("rooms"),
            context=False,
        )
    ]


def _lodging_room(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("room_name"):
        return []
    offers = ctx.get("offers")
    if offers is None and ctx.get("price") is not None:
        offers = [
            builders.build_offer(
                price=ctx["price"],
                currency=ctx.get("currency") or "EUR",
                availability=ctx.get("availability"),
                url=ctx.get("offer_url"),
                price_specification=builders.build_price_specification(
                    ctx["price"],
                    ctx.get("currency") or "EUR",
                    unit_code=ctx.get("unit_code") or "DAY",
                ),
            )
        ]
    return [
        builders.build_hotel_room(
            name=ctx["room_name"],
            description=ctx.get("room_description"),
            occupancy=ctx.get("occupancy"),
            bed_type=ctx.get("bed_type"),
            offers=offers,
            amenities=ctx.get("amenities"),
            as_product=bool(ctx.get("as_product", True)),
            node_id=ctx.get("room_id"),
            context=False,
        )
    ]


def _recipe(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("recipe_name"):
        return []
    return [
        builders.build_recipe(
            name=ctx["recipe_name"],
            description=ctx.get("description"),
            recipe_ingredient=ctx.get("ingredients"),
            recipe_instructions=ctx.get("instructions"),
            image=ctx.get("image"),
            context=False,
        )
    ]


def _person(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("person_name"):
        return []
    return [
        builders.build_person(
            name=ctx["person_name"],
            url=ctx.get("url"),
            job_title=ctx.get("job_title"),
            image=ctx.get("image"),
            same_as=ctx.get("same_as"),
            context=False,
        )
    ]


def _local_business(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("business_name"):
        return []
    return [
        builders.build_local_business(
            name=ctx["business_name"],
            url=ctx.get("url"),
            telephone=ctx.get("telephone"),
            address=ctx.get("address"),
            business_type=ctx.get("business_type")
            or "HomeAndConstructionBusiness",
            context=False,
        )
    ]


def _review(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not ctx.get("item_name"):
        return []
    return [
        builders.build_review(
            item_name=ctx["item_name"],
            review_body=ctx.get("review_body"),
            rating_value=ctx.get("rating_value"),
            author=ctx.get("author"),
            context=False,
        )
    ]


PROFILES: Dict[str, ProfileFn] = {
    "sitewide": _sitewide,
    "breadcrumb": _breadcrumb,
    "article": _article,
    "faq": _faq,
    "lodging": _lodging,
    "lodging_room": _lodging_room,
    # Additive (post-MVP, same API)
    "recipe": _recipe,
    "person": _person,
    "local_business": _local_business,
    "review": _review,
}

MVP_PROFILES = (
    "sitewide",
    "breadcrumb",
    "article",
    "faq",
    "lodging",
    "lodging_room",
)


def resolve_profiles(
    names: Sequence[str],
    context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Resolve profile names to a flat list of Schema.org nodes (no @context)."""
    nodes: List[Dict[str, Any]] = []
    for name in names:
        fn = PROFILES.get(name)
        if fn is None:
            raise KeyError(f"unknown JSON-LD profile: {name}")
        nodes.extend(fn(context))
    return nodes


def build_from_profiles(
    names: Optional[Sequence[str]] = None,
    *,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a full ``@graph`` document from profile names + context.

    If ``names`` is omitted, uses ``JSONLD.PROFILES`` from
    ``APP_CONFIG["agentweb"]`` (or MVP defaults when the list is empty and
    JSONLD is enabled).
    """
    cfg = conf.get_domain("JSONLD")
    selected = (
        list(names) if names is not None else list(cfg.get("PROFILES") or [])
    )
    if not selected and conf.is_enabled("JSONLD"):
        selected = list(MVP_PROFILES)
    ctx = context or {}
    nodes = resolve_profiles(selected, ctx)
    return build_graph(
        *nodes,
        site_url=ctx.get("site_url"),
        include_sitewide=False,
        organization_name=ctx.get("organization_name"),
    )
