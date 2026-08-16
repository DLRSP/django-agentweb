"""Import LLMS editorial content from settings into the database.

Idempotent: re-running updates the document and replaces sections/links for
the target site + language. Never runs automatically on migrate.

Usage::

    python manage.py import_llms_from_settings
    python manage.py import_llms_from_settings --site-id 1 --lang en
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from agentweb import conf
from agentweb.llms.cache import invalidate_llms_cache
from agentweb.llms.models import LlmsDocument, LlmsLink, LlmsSection


class Command(BaseCommand):
    help = "Import LLMS TITLE/DESCRIPTION/BODY/SECTIONS from settings into DB."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--site-id",
            type=int,
            default=None,
            help="Site primary key (default: settings.SITE_ID).",
        )
        parser.add_argument(
            "--lang",
            default=None,
            help="Language code (default: settings.LANGUAGE_CODE).",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        site_id = options["site_id"] or getattr(settings, "SITE_ID", None)
        if site_id is None:
            raise CommandError("SITE_ID is not configured; pass --site-id.")
        try:
            site = Site.objects.get(pk=site_id)
        except Site.DoesNotExist as exc:
            raise CommandError(f"Site id={site_id} does not exist.") from exc

        language = options["lang"] or settings.LANGUAGE_CODE
        cfg = conf.get_domain("LLMS")
        title = (cfg.get("TITLE") or "").strip() or "Untitled site"
        description = cfg.get("DESCRIPTION") or ""
        body = cfg.get("BODY") or ""
        sections = list(cfg.get("SECTIONS") or [])

        document, created = LlmsDocument.objects.update_or_create(
            site=site,
            language=language,
            defaults={
                "title": title,
                "description": description,
                "body": body,
            },
        )
        document.sections.all().delete()
        for index, section_data in enumerate(sections):
            heading = (section_data.get("heading") or "").strip()
            if not heading:
                continue
            section = LlmsSection.objects.create(
                document=document,
                heading=heading,
                position=index,
            )
            for link_index, link_data in enumerate(
                section_data.get("links") or []
            ):
                link_title = (link_data.get("title") or "").strip()
                url = (link_data.get("url") or "").strip()
                if not link_title or not url:
                    continue
                LlmsLink.objects.create(
                    section=section,
                    title=link_title,
                    url=url,
                    notes=(link_data.get("notes") or "").strip(),
                    position=link_index,
                )

        invalidate_llms_cache(site.id, language)
        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} LLMS document site={site.id} language={language}"
            )
        )
