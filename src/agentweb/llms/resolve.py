"""Resolve LLMS editorial content from DB (preferred) or settings fallback."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from django.contrib.sites.models import Site

from agentweb import conf

from .models import LlmsDocument
from .sections import filter_sections


def _settings_editorial(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "TITLE": cfg.get("TITLE", "") or "",
        "DESCRIPTION": cfg.get("DESCRIPTION", "") or "",
        "BODY": cfg.get("BODY", "") or "",
        "SECTIONS": list(cfg.get("SECTIONS") or []),
        "source": "settings",
    }


def _document_editorial(document: LlmsDocument) -> Dict[str, Any]:
    sections = []
    for section in document.sections.all():
        links = []
        for link in section.links.all():
            item: Dict[str, Any] = {
                "title": link.title,
                "url": link.url,
            }
            if link.notes:
                item["notes"] = link.notes
            links.append(item)
        sections.append({"heading": section.heading, "links": links})
    return {
        "TITLE": document.title,
        "DESCRIPTION": document.description,
        "BODY": document.body,
        "SECTIONS": sections,
        "source": "database",
    }


def resolve_llms_content(
    site: Optional[Union[Site, int]] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Return editorial keys for llms rendering.

    Precedence:

    1. Infra always from ``conf.get_domain("LLMS")`` (caller applies separately).
    2. If a ``LlmsDocument`` exists for ``(site, language)``, whole-document
       editorial override (title, description, body, sections).
    3. Else settings editorial keys.
    4. Always apply settings ``EXCLUDE_PATTERNS`` to sections before return.
    """
    cfg = conf.get_domain("LLMS")
    patterns = list(cfg.get("EXCLUDE_PATTERNS") or [])

    site_obj: Optional[Site] = None
    if isinstance(site, Site):
        site_obj = site
    elif site is not None:
        try:
            site_obj = Site.objects.get(pk=site)
        except Site.DoesNotExist:
            site_obj = None

    editorial = _settings_editorial(cfg)
    if site_obj is not None and language:
        document = (
            LlmsDocument.objects.filter(site=site_obj, language=language)
            .prefetch_related("sections__links")
            .first()
        )
        if document is not None:
            editorial = _document_editorial(document)

    editorial["SECTIONS"] = filter_sections(
        list(editorial.get("SECTIONS") or []), patterns
    )
    if not editorial["SECTIONS"] and cfg.get("AUTO_SECTIONS"):
        # Same v1 behaviour as settings-only path (no crawl).
        editorial["SECTIONS"] = []
    return editorial
