"""URLs for the readability (llms.txt) domain."""

from __future__ import annotations

from functools import wraps

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.urls import path

from .. import conf
from .cache import llms_cache_key
from .views import LlmsTxtView


def _cache_timeout() -> int:
    """Read LLMS cache timeout at call time (settings may change in tests)."""
    return int(conf.get_domain("LLMS").get("CACHE_TIMEOUT", 0) or 0)


def _site_language_cache(view, *, full: bool):
    """Cache the view response keyed by site + language + variant."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        timeout = _cache_timeout()
        if timeout <= 0:
            return view(request, *args, **kwargs)

        lang = (
            kwargs.get("lang")
            or getattr(request, "LANGUAGE_CODE", None)
            or settings.LANGUAGE_CODE
            or "en"
        )
        site = get_current_site(request)
        key = llms_cache_key(site.id, lang, full=full)

        cached = cache.get(key)
        if cached is not None:
            return cached

        response = view(request, *args, **kwargs)
        if getattr(response, "status_code", 500) == 200:
            if hasattr(response, "render") and callable(response.render):
                response.render()
            cache.set(key, response, timeout)
        return response

    return wrapper


urlpatterns = [
    path(
        "llms.txt",
        _site_language_cache(LlmsTxtView.as_view(full=False), full=False),
        name="agentweb-llms-txt",
    ),
    path(
        "llms-full.txt",
        _site_language_cache(LlmsTxtView.as_view(full=True), full=True),
        name="agentweb-llms-full-txt",
    ),
]
