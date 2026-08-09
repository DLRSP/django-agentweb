"""URLs for the readability (llms.txt) domain."""

from __future__ import annotations

from functools import wraps

from django.core.cache import cache
from django.urls import path
from django.utils.cache import get_cache_key
from django.utils.translation import get_language

from .. import conf
from .views import LlmsTxtView


def _cache_timeout() -> int:
    """Read LLMS cache timeout at call time (settings may change in tests)."""
    return int(conf.get_domain("LLMS").get("CACHE_TIMEOUT", 0) or 0)


def _language_cache(view):
    """Cache the view response keyed by path + active language.

    Standard ``cache_page`` alone is unsafe when the body varies by
    ``get_language()`` / ``/{lang}/`` without a language-aware cache key.
    Timeout is resolved per request so settings overrides take effect.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        timeout = _cache_timeout()
        if timeout <= 0:
            return view(request, *args, **kwargs)

        lang = (
            kwargs.get("lang")
            or getattr(request, "LANGUAGE_CODE", None)
            or get_language()
            or "en"
        )
        # Prefer Django's cache-key helper, then namespace by language.
        base_key = get_cache_key(request, key_prefix=f"agentweb.llms.{lang}")
        if base_key is None:
            base_key = f"agentweb.llms.{lang}:{request.path}"

        cached = cache.get(base_key)
        if cached is not None:
            return cached

        response = view(request, *args, **kwargs)
        if getattr(response, "status_code", 500) == 200:
            # Materialize content before storing (TemplateResponse safety).
            if hasattr(response, "render") and callable(response.render):
                response.render()
            cache.set(base_key, response, timeout)
        return response

    return wrapper


urlpatterns = [
    path(
        "llms.txt",
        _language_cache(LlmsTxtView.as_view(full=False)),
        name="agentweb-llms-txt",
    ),
    path(
        "llms-full.txt",
        _language_cache(LlmsTxtView.as_view(full=True)),
        name="agentweb-llms-full-txt",
    ),
]
