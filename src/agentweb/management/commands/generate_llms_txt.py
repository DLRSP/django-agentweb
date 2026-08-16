"""Pre-render static ``llms.txt`` / ``llms-full.txt`` files.

Useful when serving the readability documents as static assets instead of (or
in addition to) the dynamic cached view.

Usage::

    python manage.py generate_llms_txt --output ./static/
"""

from __future__ import annotations

import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import override

from agentweb import conf
from agentweb.llms.resolve import resolve_llms_content


class Command(BaseCommand):
    help = "Render llms.txt and llms-full.txt to static files."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--output",
            default=".",
            help="Directory to write llms.txt / llms-full.txt into.",
        )
        parser.add_argument(
            "--lang",
            default=None,
            help="Language code to render (default: settings.LANGUAGE_CODE).",
        )
        parser.add_argument(
            "--site-id",
            type=int,
            default=None,
            help="Site primary key (default: settings.SITE_ID).",
        )

    def handle(self, *args, **options) -> None:
        cfg = conf.get_domain("LLMS")
        output_dir = options["output"]
        language = options["lang"] or settings.LANGUAGE_CODE
        site_id = options["site_id"] or getattr(settings, "SITE_ID", 1)
        try:
            site = Site.objects.get(pk=site_id)
        except Site.DoesNotExist:
            site = None

        editorial = resolve_llms_content(site=site, language=language)
        os.makedirs(output_dir, exist_ok=True)

        context = {
            "title": editorial.get("TITLE", "") or "Untitled site",
            "description": editorial.get("DESCRIPTION", ""),
            "body": editorial.get("BODY", ""),
            "sections": editorial.get("SECTIONS") or [],
            "language": language,
            "languages": [code for code, _name in settings.LANGUAGES],
            "i18n_variants": bool(cfg.get("I18N_VARIANTS")),
        }
        with override(language):
            for filename, template, full in (
                ("llms.txt", "agentweb/llms.txt", False),
                ("llms-full.txt", "agentweb/llms-full.txt", True),
            ):
                body = render_to_string(
                    template, {**context, "full": full, "request": None}
                )
                path = os.path.join(output_dir, filename)
                with open(path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(body)
                self.stdout.write(self.style.SUCCESS(f"Wrote {path}"))
