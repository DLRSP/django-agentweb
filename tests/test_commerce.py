"""Tests for the commerce / booking domain."""

from django.test import TestCase
from django.urls import reverse


class CommerceTestCase(TestCase):
    def test_commerce_descriptor(self):
        response = self.client.get(reverse("agentweb-commerce-descriptor"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["vendor"], "example-booking-vendor")
        self.assertIn("simulateBookingCost", data["operations"])
        self.assertTrue(data["requiresHumanConfirmation"])
