"""Views serving ``llms.txt`` and ``llms-full.txt``."""

from __future__ import annotations

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.cache import patch_cache_control
from django.utils.translation import override
from django.views import View

from .. import conf
from .resolve import resolve_llms_content
from .validate import validate_llms_txt

# Spec convention: plain text Markdown (llmstxt.org / community validators).
CONTENT_TYPE = "text/plain; charset=utf-8"


class LlmsTxtView(View):
    """Render the ``llms.txt`` (or ``llms-full.txt``) document as text.

    Editorial content comes from ``resolve_llms_content`` (database override or
    settings fallback). Caching is applied at the URL layer and keyed by site
    and language.
    """

    full: bool = False

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        cfg = conf.get_domain("LLMS")
        language = (
            kwargs.get("lang")
            or getattr(request, "LANGUAGE_CODE", None)
            or settings.LANGUAGE_CODE
        )
        site = get_current_site(request)
        editorial = resolve_llms_content(site=site, language=language)
        template = (
            "agentweb/llms-full.txt" if self.full else "agentweb/llms.txt"
        )
        with override(language):
            context = {
                "title": editorial.get("TITLE", "") or "Untitled site",
                "description": editorial.get("DESCRIPTION", ""),
                "body": editorial.get("BODY", ""),
                "sections": editorial.get("SECTIONS") or [],
                "language": language,
                "languages": [code for code, _name in settings.LANGUAGES],
                "i18n_variants": bool(cfg.get("I18N_VARIANTS")),
                "full": self.full,
                "request": request,
            }
            body = render_to_string(template, context, request=request)

        validation_errors = validate_llms_txt(body)
        response = HttpResponse(body, content_type=CONTENT_TYPE)
        if validation_errors:
            response["X-Agentweb-Llms-Valid"] = "0"
        else:
            response["X-Agentweb-Llms-Valid"] = "1"
        response["Content-Language"] = language
        response["Vary"] = "Accept-Language"
        patch_cache_control(response, public=True)
        return response
