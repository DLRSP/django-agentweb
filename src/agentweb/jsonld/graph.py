"""Assemble a single Schema.org ``@graph`` with stable ``@id`` deduplication."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .builders import build_organization, build_website, normalize_type


def _strip_context(node: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in node.items() if k != "@context"}


def _normalize_types(node: Dict[str, Any]) -> Dict[str, Any]:
    raw = node.get("@type")
    if isinstance(raw, str):
        node = {**node, "@type": normalize_type(raw)}
    elif isinstance(raw, list):
        node = {**node, "@type": [normalize_type(t) for t in raw]}
    return node


def build_graph(
    *nodes: Dict[str, Any],
    site_url: Optional[str] = None,
    include_sitewide: bool = False,
    organization: Optional[Dict[str, Any]] = None,
    website: Optional[Dict[str, Any]] = None,
    organization_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Build ``{"@context": schema.org, "@graph": [...]}`` with ``@id`` dedupe.

    Nodes that share the same ``@id`` collapse to the first occurrence
    (reference-don't-clone). Nested ``@context`` keys are stripped so the
    document has a single top-level context.
    """
    graph: List[Dict[str, Any]] = []
    seen: Dict[str, int] = {}

    def _add(node: Optional[Dict[str, Any]]) -> None:
        if not node:
            return
        cleaned = _normalize_types(_strip_context(dict(node)))
        node_id = cleaned.get("@id")
        if node_id and node_id in seen:
            return
        if node_id:
            seen[node_id] = len(graph)
        graph.append(cleaned)

    if include_sitewide and site_url:
        org = organization or build_organization(
            name=organization_name or site_url,
            url=site_url,
            context=False,
        )
        web = website or build_website(
            name=organization_name or site_url,
            url=site_url,
            publisher=org.get("@id"),
            context=False,
        )
        _add(org)
        _add(web)

    for node in nodes:
        _add(node)

    return {"@context": "https://schema.org", "@graph": graph}


def merge_graphs(*graphs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple graph documents, deduping by ``@id``."""
    nodes: List[Dict[str, Any]] = []
    for doc in graphs:
        nodes.extend(doc.get("@graph") or [])
        # Also accept a lone typed node.
        if "@type" in doc and "@graph" not in doc:
            nodes.append(doc)
    return build_graph(*nodes)
