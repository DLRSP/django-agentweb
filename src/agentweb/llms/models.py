"""Editorial LLMS documents (admin-editable; settings remain fallback)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def _language_codes() -> list[str]:
    return [code for code, _name in settings.LANGUAGES]


def validate_llms_link_url(value: str) -> None:
    """Allow http(s) absolute URLs or site-relative paths; reject dangerous schemes."""
    url = (value or "").strip()
    if not url:
        raise ValidationError(_("URL is required."))
    lower = url.lower()
    if lower.startswith(("javascript:", "data:", "vbscript:")):
        raise ValidationError(_("This URL scheme is not allowed."))
    if url.startswith("/"):
        return
    if lower.startswith(("http://", "https://")):
        return
    raise ValidationError(
        _("Use an absolute http(s) URL or a site-relative path starting with /.")
    )


class LlmsDocument(models.Model):
    """Curated llms.txt content for one site and language."""

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="agentweb_llms_documents",
        verbose_name=_("Site"),
    )
    language = models.CharField(
        _("Language"),
        max_length=16,
        help_text=_("Language code from Django LANGUAGES (e.g. en, it)."),
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    body = models.TextField(_("Body"), blank=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("LLMS document")
        verbose_name_plural = _("LLMS documents")
        constraints = [
            models.UniqueConstraint(
                fields=("site", "language"),
                name="agentweb_llmsdocument_site_language_uniq",
            ),
        ]
        ordering = ("site_id", "language")

    def __str__(self) -> str:
        return f"{self.title} ({self.language})"

    def clean(self) -> None:
        allowed = _language_codes()
        if self.language and self.language not in allowed:
            raise ValidationError(
                {
                    "language": _(
                        "Language %(code)s is not in settings.LANGUAGES."
                    )
                    % {"code": self.language}
                }
            )


class LlmsSection(models.Model):
    """H2 section within an LLMS document."""

    document = models.ForeignKey(
        LlmsDocument,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("LLMS document"),
    )
    heading = models.CharField(_("Heading"), max_length=255)
    position = models.PositiveIntegerField(_("Position"), default=0)

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        ordering = ("position", "id")

    def __str__(self) -> str:
        return self.heading


class LlmsLink(models.Model):
    """Link row inside an LLMS section."""

    section = models.ForeignKey(
        LlmsSection,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name=_("Section"),
    )
    title = models.CharField(_("Title"), max_length=255)
    url = models.CharField(
        _("URL"),
        max_length=2048,
        validators=[validate_llms_link_url],
        help_text=_("Absolute http(s) URL or site-relative path (e.g. /rooms/)."),
    )
    notes = models.CharField(_("Notes"), max_length=512, blank=True)
    position = models.PositiveIntegerField(_("Position"), default=0)

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
        ordering = ("position", "id")

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        validate_llms_link_url(self.url)
