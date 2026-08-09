"""Tests for the structured-data (JSON-LD) domain."""

import json

from django.template import Context, Template
from django.test import TestCase

from agentweb.jsonld import builders


class BuildersTestCase(TestCase):
    def test_build_hotel_drops_none_and_adds_context(self):
        hotel = builders.build_hotel(name="Hotel X", telephone=None)
        self.assertEqual(hotel["@context"], "https://schema.org")
        self.assertEqual(hotel["@type"], "Hotel")
        self.assertNotIn("telephone", hotel)

    def test_build_offer_with_price_specification(self):
        spec = builders.build_price_specification(120, "EUR", unit_code="DAY")
        offer = builders.build_offer(
            price=120, currency="EUR", price_specification=spec
        )
        self.assertEqual(offer["priceSpecification"]["unitCode"], "DAY")


class JsonLdTagTestCase(TestCase):
    def test_jsonld_script_renders_safe_block(self):
        hotel = builders.build_hotel(name="Hotel X")
        template = Template(
            "{% load agentweb_jsonld %}{% jsonld_script hotel %}"
        )
        rendered = template.render(Context({"hotel": hotel}))
        self.assertIn('type="application/ld+json"', rendered)
        self.assertNotIn(
            "<script>",
            rendered.replace('<script type="application/ld+json">', ""),
        )
        # Payload must remain valid JSON after escaping is reversed.
        payload = rendered.split(">", 1)[1].rsplit("<", 1)[0]
        payload = (
            payload.replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026", "&")
        )
        self.assertEqual(json.loads(payload)["name"], "Hotel X")

    def test_jsonld_script_escapes_hostile_payload(self):
        hostile = builders.build_hotel(
            name="</script><script>alert(1)</script> & co"
        )
        template = Template(
            "{% load agentweb_jsonld %}{% jsonld_script hotel %}"
        )
        rendered = template.render(Context({"hotel": hostile}))
        # The only markup is the wrapping <script> ... </script> pair; the
        # serialised payload between them must not contain raw < > &.
        self.assertEqual(rendered.count("</script>"), 1)
        body = rendered[len('<script type="application/ld+json">') :]
        body = body[: -len("</script>")]
        self.assertNotIn("<", body)
        self.assertNotIn(">", body)
        self.assertNotIn("&", body)

    def test_jsonld_script_empty_is_blank(self):
        template = Template(
            "{% load agentweb_jsonld %}{% jsonld_script data %}"
        )
        self.assertEqual(template.render(Context({"data": None})), "")
