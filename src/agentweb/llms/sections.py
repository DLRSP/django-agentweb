"""Curate llms.txt sections from settings, applying exclude filters."""

from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlparse


def _is_excluded(url: str, patterns: List[str]) -> bool:
    """Return True if ``url`` matches any exclude pattern (case-insensitive)."""
    if not url or not patterns:
        return False
    haystack = url.lower()
    path = (urlparse(url).path or "").lower()
    for pattern in patterns:
        p = (pattern or "").lower()
        if not p:
            continue
        if p in haystack or p in path:
            return True
    return False


def filter_sections(
    sections: List[Dict[str, Any]],
    exclude_patterns: List[str],
) -> List[Dict[str, Any]]:
    """Return sections with excluded links removed; drop empty sections."""
    cleaned: List[Dict[str, Any]] = []
    for section in sections or []:
        heading = (section.get("heading") or "").strip()
        links_in = section.get("links") or []
        links_out = []
        for link in links_in:
            url = (link.get("url") or "").strip()
            title = (link.get("title") or "").strip()
            if not url or not title:
                continue
            if _is_excluded(url, exclude_patterns):
                continue
            item = {"title": title, "url": url}
            notes = (link.get("notes") or "").strip()
            if notes:
                item["notes"] = notes
            links_out.append(item)
        if heading and links_out:
            cleaned.append({"heading": heading, "links": links_out})
    return cleaned


def build_sections(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build curated sections from LLMS config."""
    patterns = list(cfg.get("EXCLUDE_PATTERNS") or [])
    sections = filter_sections(list(cfg.get("SECTIONS") or []), patterns)
    if sections:
        return sections
    if cfg.get("AUTO_SECTIONS"):
        # v1: no site crawl — emit a placeholder Docs section only when the
        # site provided no SECTIONS. Sites should supply curated links.
        return []
    return []
