"""Module E2E smoke: content manager admin → public llms.txt."""

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse

from agentweb.llms.models import LlmsDocument, LlmsLink, LlmsSection

User = get_user_model()


class LlmsAdminToPublicSmokeTests(TestCase):
    def setUp(self):
        self.site, _ = Site.objects.get_or_create(
            id=1, defaults={"domain": "example.com", "name": "example"}
        )
        self.user = User.objects.create_superuser(
            username="cm-e2e", password="x", email="cm@example.com"
        )

    def test_admin_create_appears_on_public_llms(self):
        self.client.force_login(self.user)
        add_url = reverse("admin:agentweb_llmsdocument_add")
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("LLMS document", html)
        for forbidden in ("CMS page", "Flatpage", "Constance", "Remote bridge"):
            self.assertNotIn(forbidden, html)

        doc = LlmsDocument.objects.create(
            site=self.site,
            language="en",
            title="E2E Hotel",
            description="Managed in admin",
        )
        section = LlmsSection.objects.create(
            document=doc, heading="Book", position=0
        )
        LlmsLink.objects.create(
            section=section,
            title="Rooms",
            url="https://example.com/rooms/",
            position=0,
        )
        public = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(public.status_code, 200)
        body = public.content.decode()
        self.assertIn("E2E Hotel", body)
        self.assertIn("Rooms", body)
