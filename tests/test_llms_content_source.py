"""LLMS content source: database override with settings fallback."""

from __future__ import annotations

import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import translation

from agentweb.llms.models import LlmsDocument, LlmsLink, LlmsSection
from agentweb.llms.resolve import resolve_llms_content


User = get_user_model()


class LlmsContentSourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site, _ = Site.objects.get_or_create(
            id=1, defaults={"domain": "example.com", "name": "example"}
        )
        Site.objects.filter(pk=1).update(domain="example.com", name="example")
        cls.site.refresh_from_db()

    def setUp(self):
        cache.clear()
        translation.activate("en")

    def tearDown(self):
        cache.clear()
        translation.deactivate()

    def test_llms_falls_back_to_settings_when_no_document(self):
        response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertTrue(body.startswith("# Test Site"))
        self.assertIn("About", body)

    def test_database_document_overrides_settings_title(self):
        doc = LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="Admin Title",
            description="From admin",
            body="",
        )
        section = LlmsSection.objects.create(
            document=doc, heading="Stay", position=0
        )
        LlmsLink.objects.create(
            section=section,
            title="Rooms",
            url="https://example.com/rooms/",
            position=0,
        )
        response = self.client.get(reverse("agentweb-llms-txt"))
        body = response.content.decode()
        self.assertTrue(body.startswith("# Admin Title"))
        self.assertIn("From admin", body)
        self.assertIn("Rooms", body)
        self.assertNotIn("# Test Site", body)

    def test_exclude_patterns_still_apply_to_database_links(self):
        doc = LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="Admin Title",
            description="desc",
        )
        section = LlmsSection.objects.create(
            document=doc, heading="Docs", position=0
        )
        LlmsLink.objects.create(
            section=section,
            title="Secret",
            url="https://example.com/admin/secret/",
            position=0,
        )
        LlmsLink.objects.create(
            section=section,
            title="Public",
            url="https://example.com/about/",
            position=1,
        )
        response = self.client.get(reverse("agentweb-llms-txt"))
        body = response.content.decode()
        self.assertIn("Public", body)
        self.assertNotIn("Secret", body)
        self.assertNotIn("/admin/", body)

    def test_cached_response_invalidates_after_document_save(self):
        with override_settings(
            APP_CONFIG={
                "agentweb": {
                    "LLMS": {
                        "ENABLED": True,
                        "TITLE": "Settings Title",
                        "DESCRIPTION": "desc",
                        "CACHE_TIMEOUT": 3600,
                        "SECTIONS": [],
                        "EXCLUDE_PATTERNS": ["/admin/"],
                    },
                    "JSONLD": {"ENABLED": True},
                    "DISCOVERY": {"ENABLED": True},
                    "WEBMCP": {"ENABLED": True},
                    "COMMERCE": {"ENABLED": True},
                    "SDF": {"ENABLED": True},
                }
            },
            AGENTWEB=None,
            LANGUAGE_CODE="en",
        ):
            first = self.client.get(reverse("agentweb-llms-txt"))
            self.assertIn("Settings Title", first.content.decode())
            LlmsDocument.objects.create(
                site=self.site,
                language="en",
                title="Fresh Title",
                description="desc",
            )
            second = self.client.get(reverse("agentweb-llms-txt"))
            self.assertIn("Fresh Title", second.content.decode())
            self.assertNotIn("Settings Title", second.content.decode())

    def test_language_isolation_between_documents(self):
        LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="English Doc",
            description="en",
        )
        LlmsDocument.objects.create(
            site=self.site,
            language="it",
            title="Documento IT",
            description="it",
        )
        en_body = self.client.get(reverse("agentweb-llms-txt")).content.decode()
        it_body = self.client.get("/it/llms.txt").content.decode()
        self.assertIn("English Doc", en_body)
        self.assertIn("Documento IT", it_body)
        self.assertNotIn("Documento IT", en_body)
        self.assertNotIn("English Doc", it_body)

    def test_resolve_uses_at_most_three_queries(self):
        doc = LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="Q",
            description="d",
        )
        section = LlmsSection.objects.create(
            document=doc, heading="H", position=0
        )
        LlmsLink.objects.create(
            section=section, title="L", url="https://example.com/", position=0
        )
        with CaptureQueriesContext(connection) as ctx:
            resolve_llms_content(site=self.site, language="en")
        self.assertLessEqual(len(ctx), 3)

    def test_generate_llms_txt_matches_resolved_content(self):
        LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="Static Title",
            description="static desc",
        )
        with tempfile.TemporaryDirectory() as tmp:
            call_command("generate_llms_txt", output=tmp, site_id=self.site.id)
            text = (Path(tmp) / "llms.txt").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Static Title"))

    def test_import_llms_from_settings_is_idempotent(self):
        call_command("import_llms_from_settings", site_id=self.site.id, lang="en")
        self.assertEqual(LlmsDocument.objects.count(), 1)
        doc = LlmsDocument.objects.get()
        self.assertEqual(doc.title, "Test Site")
        self.assertEqual(doc.sections.count(), 1)
        call_command("import_llms_from_settings", site_id=self.site.id, lang="en")
        self.assertEqual(LlmsDocument.objects.count(), 1)
        self.assertEqual(LlmsDocument.objects.get().sections.count(), 1)

    def test_migrations_create_editorial_tables(self):
        table_names = connection.introspection.table_names()
        self.assertIn("agentweb_llmsdocument", table_names)
        self.assertIn("agentweb_llmssection", table_names)
        self.assertIn("agentweb_llmslink", table_names)


class LlmsContentManagerPermissionTests(TestCase):
    def setUp(self):
        self.site, _ = Site.objects.get_or_create(
            id=1, defaults={"domain": "example.com", "name": "example"}
        )
        perms = list(
            Permission.objects.filter(
                content_type__app_label="agentweb",
                codename__in=[
                    "view_llmsdocument",
                    "add_llmsdocument",
                    "change_llmsdocument",
                    "delete_llmsdocument",
                ],
            )
        )
        self.assertEqual(len(perms), 4, "expected migrated LLMS document perms")
        group, _ = Group.objects.get_or_create(name="Agentweb content managers")
        group.permissions.set(perms)
        self.cm_user = User.objects.create_user(
            username="cm", password="x", is_staff=True
        )
        self.cm_user.groups.add(group)

    def test_content_manager_can_open_llms_document_admin(self):
        self.client.force_login(self.cm_user)
        url = reverse("admin:agentweb_llmsdocument_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("LLMS document", html)
        for forbidden in (
            "CMS page",
            "Flatpage",
            "Constance",
            "Remote bridge",
            "Web Bot Auth",
        ):
            self.assertNotIn(forbidden, html)

    def test_content_manager_cannot_edit_flags_via_document_admin(self):
        self.client.force_login(self.cm_user)
        url = reverse("admin:agentweb_llmsdocument_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode().lower()
        self.assertNotIn("remote_bridge", html)
        self.assertNotIn("web_bot_auth", html)
        self.assertNotIn('name="enabled"', html)

    def test_content_manager_add_form_shows_allowed_vocabulary(self):
        self.client.force_login(self.cm_user)
        response = self.client.get(reverse("admin:agentweb_llmsdocument_add"))
        html = response.content.decode()
        for allowed in ("Site", "Language", "Title", "Description", "Sections"):
            self.assertIn(allowed, html)

    def test_staff_without_model_perms_is_denied(self):
        staff = User.objects.create_user(
            username="staff-noperm", password="x", is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:agentweb_llmsdocument_changelist"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_admin_redirects_to_login(self):
        response = self.client.get(reverse("admin:agentweb_llmsdocument_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response["Location"])

    def test_content_manager_can_save_document_with_section_inline(self):
        self.client.force_login(self.cm_user)
        response = self.client.post(
            reverse("admin:agentweb_llmsdocument_add"),
            {
                "site": self.site.id,
                "language": "en",
                "title": "CM Created",
                "description": "via admin",
                "body": "",
                "sections-TOTAL_FORMS": "1",
                "sections-INITIAL_FORMS": "0",
                "sections-MIN_NUM_FORMS": "0",
                "sections-MAX_NUM_FORMS": "1000",
                "sections-0-heading": "Stay",
                "sections-0-position": "0",
                "sections-0-id": "",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        doc = LlmsDocument.objects.get(title="CM Created")
        self.assertEqual(doc.sections.count(), 1)


class LlmsContentSourceIsolationTests(TestCase):
    def setUp(self):
        cache.clear()
        translation.activate("en")
        self.site_a = Site.objects.create(domain="a.example.com", name="A")
        self.site_b = Site.objects.create(domain="b.example.com", name="B")

    def tearDown(self):
        cache.clear()
        translation.deactivate()

    def test_documents_do_not_leak_across_sites(self):
        LlmsDocument.objects.create(
            site=self.site_a, language="en", title="Site A Title", description="a"
        )
        LlmsDocument.objects.create(
            site=self.site_b, language="en", title="Site B Title", description="b"
        )
        with override_settings(SITE_ID=self.site_a.id):
            body = self.client.get(reverse("agentweb-llms-txt")).content.decode()
        self.assertIn("Site A Title", body)
        self.assertNotIn("Site B Title", body)

    def test_javascript_url_rejected_on_link_clean(self):
        doc = LlmsDocument.objects.create(
            site=self.site_a, language="en", title="T", description=""
        )
        section = LlmsSection.objects.create(document=doc, heading="H", position=0)
        link = LlmsLink(
            section=section,
            title="Bad",
            url="javascript:alert(1)",
            position=0,
        )
        with self.assertRaises(Exception):
            link.full_clean()

    def test_generate_matches_settings_when_tables_empty(self):
        self.assertEqual(LlmsDocument.objects.count(), 0)
        with tempfile.TemporaryDirectory() as tmp:
            call_command("generate_llms_txt", output=tmp, site_id=1, lang="en")
            text = (Path(tmp) / "llms.txt").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Test Site"))

    def test_migrate_does_not_import_settings_content(self):
        # Tables exist from test DB setup; editorial rows must stay empty
        # unless import_llms_from_settings is invoked explicitly.
        self.assertEqual(LlmsDocument.objects.count(), 0)
