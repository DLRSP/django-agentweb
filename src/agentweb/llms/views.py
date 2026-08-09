"""Views serving ``llms.txt`` and ``llms-full.txt``."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.cache import patch_cache_control
from django.utils.translation import get_language, override
from django.views import View

from .. import conf
from .sections import build_sections
from .validate import validate_llms_txt

# Spec convention: plain text Markdown (llmstxt.org / community validators).
CONTENT_TYPE = "text/plain; charset=utf-8"


class LlmsTxtView(View):
    """Render the ``llms.txt`` (or ``llms-full.txt``) document as text.

    The ``full`` flag selects the verbose variant. Content is rendered from the
    ``agentweb/llms.txt`` / ``agentweb/llms-full.txt`` templates so projects can
    override them. Caching is applied at the URL layer (see ``urls``) and is
    keyed by language to avoid cross-locale contamination.
    """

    full: bool = False

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        cfg = conf.get_domain("LLMS")
        language = (
            kwargs.get("lang") or get_language() or settings.LANGUAGE_CODE
        )
        template = (
            "agentweb/llms-full.txt" if self.full else "agentweb/llms.txt"
        )
        with override(language):
            context = {
                "title": cfg.get("TITLE", "") or "Untitled site",
                "description": cfg.get("DESCRIPTION", ""),
                "body": cfg.get("BODY", ""),
                "sections": build_sections(cfg),
                "language": language,
                "languages": [code for code, _name in settings.LANGUAGES],
                "i18n_variants": bool(cfg.get("I18N_VARIANTS")),
                "full": self.full,
                "request": request,
            }
            body = render_to_string(template, context, request=request)

        # Soft validation: log-friendly marker header when the curated body
        # violates the minimal llms.txt grammar (does not fail the response).
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
