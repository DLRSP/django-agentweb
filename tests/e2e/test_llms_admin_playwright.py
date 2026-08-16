"""Playwright browser E2E: admin LLMS document → public /llms.txt."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

pytest.importorskip("playwright")

from playwright.sync_api import sync_playwright  # noqa: E402

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_admin_llms_document_visible_on_public_page(live_server):
    site, _ = Site.objects.get_or_create(
        id=1, defaults={"domain": "example.com", "name": "example"}
    )
    Site.objects.filter(pk=site.pk).update(domain="example.com", name="example")
    User.objects.create_superuser(
        username="e2e-admin", password="e2e-pass", email="e2e@example.com"
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{live_server.url}/admin/login/")
        page.fill('input[name="username"]', "e2e-admin")
        page.fill('input[name="password"]', "e2e-pass")
        page.click('input[type="submit"]')
        page.goto(f"{live_server.url}/admin/agentweb/llmsdocument/add/")
        page.wait_for_selector("text=LLMS document")
        content = page.content()
        assert "CMS page" not in content
        assert "Flatpage" not in content
        assert "Remote bridge" not in content

        page.select_option('select[name="site"]', label=site.name)
        page.fill('input[name="language"]', "en")
        page.fill('input[name="title"]', "Playwright Hotel")
        page.fill('textarea[name="description"]', "From browser E2E")
        page.fill('input[name="sections-0-heading"]', "Book")
        page.click('input[name="_save"]')
        page.wait_for_url("**/admin/agentweb/llmsdocument/**")

        page.goto(f"{live_server.url}/llms.txt")
        body = page.inner_text("body")
        assert "Playwright Hotel" in body
        assert "From browser E2E" in body
        browser.close()
