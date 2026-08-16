"""Django admin for editorial LLMS documents."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.sites.models import Site

from .models import LlmsDocument, LlmsLink, LlmsSection


class _DocumentPermInlineMixin:
    """Allow document-level perms to manage nested section/link inlines."""

    def _user_can_change_document(self, request) -> bool:
        return request.user.has_perm("agentweb.change_llmsdocument")

    def has_view_permission(self, request, obj=None) -> bool:
        return request.user.has_perm("agentweb.view_llmsdocument")

    def has_add_permission(self, request, obj=None) -> bool:
        return request.user.has_perm("agentweb.add_llmsdocument")

    def has_change_permission(self, request, obj=None) -> bool:
        return self._user_can_change_document(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.has_perm("agentweb.delete_llmsdocument")


class LlmsLinkInline(_DocumentPermInlineMixin, admin.TabularInline):
    model = LlmsLink
    extra = 1
    fields = ("title", "url", "notes", "position")
    ordering = ("position", "id")


class LlmsSectionInline(_DocumentPermInlineMixin, admin.TabularInline):
    model = LlmsSection
    extra = 1
    fields = ("heading", "position")
    show_change_link = True
    ordering = ("position", "id")


class _SiteScopedAdminMixin:
    """Limit changelists/forms to Sites the user may access."""

    site_field_path = "site"

    def _allowed_sites(self, request):
        if request.user.is_superuser:
            return Site.objects.all()
        # Staff content managers: all sites (no per-site ACL model in v1).
        # Still scopes queryset for consistency and future hooks.
        return Site.objects.all()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        sites = self._allowed_sites(request)
        lookup = self.site_field_path
        return qs.filter(**{f"{lookup}__in": sites})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "site" or (
            db_field.name == "document" and self.site_field_path.startswith("document")
        ):
            if db_field.name == "site":
                kwargs["queryset"] = self._allowed_sites(request)
        if db_field.name == "document":
            kwargs["queryset"] = LlmsDocument.objects.filter(
                site__in=self._allowed_sites(request)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LlmsSection)
class LlmsSectionAdmin(_SiteScopedAdminMixin, admin.ModelAdmin):
    site_field_path = "document__site"
    list_display = ("heading", "document", "position")
    list_filter = ("document__site", "document__language")
    search_fields = ("heading", "document__title")
    ordering = ("document", "position", "id")
    inlines = [LlmsLinkInline]


@admin.register(LlmsDocument)
class LlmsDocumentAdmin(_SiteScopedAdminMixin, admin.ModelAdmin):
    site_field_path = "site"
    list_display = ("title", "site", "language", "updated_at")
    list_filter = ("site", "language")
    search_fields = ("title", "description")
    ordering = ("site", "language")
    inlines = [LlmsSectionInline]
    fieldsets = (
        (
            None,
            {"fields": ("site", "language", "title", "description", "body")},
        ),
    )
