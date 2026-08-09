"""Smoke tests: package imports and SDF placeholder."""

from django.test import TestCase
from django.urls import reverse

import agentweb


class SmokeTestCase(TestCase):
    def test_version_present(self):
        self.assertTrue(agentweb.__version__)

    def test_sdf_placeholder(self):
        response = self.client.get(reverse("agentweb-sdf-descriptor"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "experimental")
