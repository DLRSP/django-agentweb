"""JSON-LD builders, graph assembler, and profile registry tests."""

import json

from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from agentweb.jsonld import builders, graph, profiles


class BuildersGenericTestCase(SimpleTestCase):
    def test_organization_website_webpage(self):
        org = builders.build_organization(
            name="Acme", url="https://ex.com/", context=False
        )
        web = builders.build_website(
            name="Acme",
            url="https://ex.com/",
            publisher=org["@id"],
            context=False,
        )
        page = builders.build_webpage(
            name="Home",
            url="https://ex.com/",
            is_part_of=web["@id"],
            context=False,
        )
        self.assertEqual(org["@type"], "Organization")
        self.assertEqual(web["@type"], "WebSite")
        self.assertEqual(page["@type"], "WebPage")
        self.assertEqual(web["publisher"]["@id"], org["@id"])

    def test_website_typo_normalized(self):
        self.assertEqual(builders.normalize_type("Website"), "WebSite")

    def test_article_breadcrumb_faq(self):
        article = builders.build_article(
            headline="Hello", url="https://ex.com/a"
        )
        crumb = builders.build_breadcrumb(
            [
                {"name": "Home", "url": "https://ex.com/"},
                {"name": "A", "url": "https://ex.com/a"},
            ]
        )
        faq = builders.build_faq(
            [{"question": "Q?", "answer": "A."}], context=False
        )
        self.assertEqual(article["@type"], "Article")
        self.assertEqual(crumb["@type"], "BreadcrumbList")
        self.assertEqual(faq["mainEntity"][0]["@type"], "Question")


class LodgingBuildersTestCase(SimpleTestCase):
    def test_hotel_room_as_product_mte(self):
        offer = builders.build_offer(price=120, currency="EUR")
        room = builders.build_hotel_room(
            name="Suite",
            offers=[offer],
            amenities=["wifi"],
            as_product=True,
            context=False,
        )
        self.assertEqual(room["@type"], ["HotelRoom", "Product"])
        self.assertEqual(room["amenityFeature"][0]["name"], "wifi")

    def test_price_accuracy_helper(self):
        self.assertTrue(builders.prices_match(120, "120.0"))
        self.assertFalse(builders.prices_match(120, 99))


class GraphTestCase(SimpleTestCase):
    def test_dedupe_organization_by_id(self):
        org1 = builders.build_organization(
            name="Acme", url="https://ex.com/", context=False
        )
        org2 = builders.build_organization(
            name="Acme Dup", url="https://ex.com/", context=False
        )
        doc = graph.build_graph(org1, org2)
        orgs = [n for n in doc["@graph"] if n.get("@type") == "Organization"]
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0]["name"], "Acme")

    def test_single_context_no_nested(self):
        hotel = builders.build_hotel(name="H", url="https://ex.com/h")
        doc = graph.build_graph(hotel)
        self.assertEqual(doc["@context"], "https://schema.org")
        self.assertTrue(all("@context" not in n for n in doc["@graph"]))
        # Website typo normalized inside graph
        bad = {"@type": "Website", "@id": "https://ex.com/#w", "name": "X"}
        doc2 = graph.build_graph(bad)
        self.assertEqual(doc2["@graph"][0]["@type"], "WebSite")


class ProfilesTestCase(SimpleTestCase):
    def test_resolve_sitewide_breadcrumb(self):
        nodes = profiles.resolve_profiles(
            ["sitewide", "breadcrumb"],
            {
                "site_url": "https://ex.com/",
                "organization_name": "Acme",
                "site_name": "Acme Site",
                "page_name": "Home",
                "page_url": "https://ex.com/",
                "breadcrumb_items": [
                    {"name": "Home", "url": "https://ex.com/"},
                ],
            },
        )
        types = {n["@type"] for n in nodes}
        self.assertIn("Organization", types)
        self.assertIn("WebSite", types)
        self.assertIn("WebPage", types)
        self.assertIn("BreadcrumbList", types)

    def test_lodging_and_room_profiles(self):
        nodes = profiles.resolve_profiles(
            ["lodging", "lodging_room"],
            {
                "hotel_name": "Sea Hotel",
                "hotel_url": "https://ex.com/",
                "room_name": "Double",
                "price": 90,
                "currency": "EUR",
            },
        )
        types = {
            tuple(n["@type"]) if isinstance(n["@type"], list) else n["@type"]
            for n in nodes
        }
        self.assertIn("Hotel", types)
        self.assertIn(("HotelRoom", "Product"), types)

    def test_additive_profiles_person_recipe_business_review(self):
        nodes = profiles.resolve_profiles(
            ["person", "recipe", "local_business", "review"],
            {
                "person_name": "Ada",
                "recipe_name": "Pasta",
                "ingredients": ["flour"],
                "business_name": "Build Co",
                "business_type": "HomeAndConstructionBusiness",
                "item_name": "Stay",
                "rating_value": 5,
            },
        )
        types = {n["@type"] for n in nodes}
        self.assertEqual(
            types,
            {
                "Person",
                "Recipe",
                "HomeAndConstructionBusiness",
                "Review",
            },
        )

    def test_unknown_profile_raises(self):
        with self.assertRaises(KeyError):
            profiles.resolve_profiles(["nope"], {})

    def test_build_from_profiles_graph(self):
        doc = profiles.build_from_profiles(
            ["sitewide", "article"],
            context={
                "site_url": "https://ex.com/",
                "organization_name": "Acme",
                "headline": "News",
                "url": "https://ex.com/news",
            },
        )
        self.assertIn("@graph", doc)
        self.assertEqual(doc["@context"], "https://schema.org")


class JsonLdRenderTestCase(TestCase):
    def test_graph_renders_single_script(self):
        doc = graph.build_graph(
            builders.build_organization(
                name="Acme", url="https://ex.com/", context=False
            )
        )
        template = Template(
            "{% load agentweb_jsonld %}{% jsonld_script graph %}"
        )
        rendered = template.render(Context({"graph": doc}))
        self.assertEqual(rendered.count('type="application/ld+json"'), 1)
        body = rendered[
            len('<script type="application/ld+json">') : -len("</script>")
        ]
        payload = json.loads(
            body.replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026", "&")
        )
        self.assertIn("@graph", payload)
