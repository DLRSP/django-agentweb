"""Cache helpers and invalidation for LLMS responses."""

from __future__ import annotations

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save

from .models import LlmsDocument, LlmsLink, LlmsSection


def llms_cache_key(site_id: int, language: str, *, full: bool) -> str:
    """Stable cache key for a site + language + variant."""
    variant = "full" if full else "short"
    return f"agentweb.llms.{site_id}.{language}.{variant}"


def invalidate_llms_cache(
    site_id: int | None = None, language: str | None = None
) -> None:
    """Drop cached llms responses for a site/language (or all documents)."""
    if site_id is not None and language is not None:
        cache.delete(llms_cache_key(site_id, language, full=False))
        cache.delete(llms_cache_key(site_id, language, full=True))
        return

    for doc in LlmsDocument.objects.all().only("site_id", "language"):
        cache.delete(llms_cache_key(doc.site_id, doc.language, full=False))
        cache.delete(llms_cache_key(doc.site_id, doc.language, full=True))


def _site_language_from_instance(instance) -> tuple[int, str] | None:
    if isinstance(instance, LlmsDocument):
        return instance.site_id, instance.language
    if isinstance(instance, LlmsSection):
        return instance.document.site_id, instance.document.language
    if isinstance(instance, LlmsLink):
        document = instance.section.document
        return document.site_id, document.language
    return None


def _invalidate_instance(sender, instance, **kwargs) -> None:
    pair = _site_language_from_instance(instance)
    if pair is None:
        return
    site_id, language = pair
    invalidate_llms_cache(site_id, language)


def connect_llms_cache_signals() -> None:
    """Wire post_save/post_delete handlers (idempotent)."""
    for model, uid in (
        (LlmsDocument, "doc"),
        (LlmsSection, "section"),
        (LlmsLink, "link"),
    ):
        post_save.connect(
            _invalidate_instance,
            sender=model,
            dispatch_uid=f"agentweb.llms.{uid}.save",
        )
        post_delete.connect(
            _invalidate_instance,
            sender=model,
            dispatch_uid=f"agentweb.llms.{uid}.delete",
        )
