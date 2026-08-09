"""JSON-LD profile combination contracts for common site shapes.

Uses generic context only (no real site names in assertions). Covers lodging,
editorial, trades, and personal profile stacks.
"""

from django.test import SimpleTestCase

from agentweb.jsonld import profiles


class ProfileCombinationsTestCase(SimpleTestCase):
    def test_lodging_site_sitewide_faq_lodging_room(self):
        doc = profiles.build_from_profiles(
            ["sitewide", "faq", "lodging", "lodging_room"],
            context={
                "site_url": "https://hotel.example/",
                "organization_name": "Coast Hotel",
                "faq_questions": [{"question": "Pets?", "answer": "Yes."}],
                "hotel_name": "Coast Hotel",
                "hotel_url": "https://hotel.example/",
                "room_name": "Sea View",
                "price": 150,
                "currency": "EUR",
            },
        )
        types = {
            tuple(n["@type"]) if isinstance(n["@type"], list) else n["@type"]
            for n in doc["@graph"]
        }
        self.assertTrue(
            {"Organization", "WebSite", "FAQPage", "Hotel"}.issubset(types)
        )
        self.assertIn(("HotelRoom", "Product"), types)

    def test_content_site_sitewide_recipe_article_faq(self):
        doc = profiles.build_from_profiles(
            ["sitewide", "recipe", "article", "faq"],
            context={
                "site_url": "https://food.example/",
                "organization_name": "Food Mag",
                "recipe_name": "Soup",
                "ingredients": ["water"],
                "headline": "Seasonal soup",
                "url": "https://food.example/soup",
                "faq_questions": [{"question": "Vegan?", "answer": "Yes."}],
            },
        )
        types = {n["@type"] for n in doc["@graph"]}
        self.assertTrue(
            {
                "Organization",
                "WebSite",
                "Recipe",
                "Article",
                "FAQPage",
            }.issubset(types)
        )

    def test_editorial_site_sitewide_article(self):
        doc = profiles.build_from_profiles(
            ["sitewide", "article"],
            context={
                "site_url": "https://news.example/",
                "organization_name": "News Co",
                "headline": "Daily",
                "url": "https://news.example/daily",
            },
        )
        types = {n["@type"] for n in doc["@graph"]}
        self.assertTrue({"Organization", "WebSite", "Article"}.issubset(types))

    def test_trades_site_breadcrumb_local_business(self):
        doc = profiles.build_from_profiles(
            ["breadcrumb", "local_business"],
            context={
                "breadcrumb_items": [
                    {"name": "Home", "url": "https://build.example/"},
                    {"name": "Services", "url": "https://build.example/s"},
                ],
                "business_name": "Build Co",
                "url": "https://build.example/",
                "business_type": "HomeAndConstructionBusiness",
            },
        )
        types = {n["@type"] for n in doc["@graph"]}
        self.assertEqual(
            types, {"BreadcrumbList", "HomeAndConstructionBusiness"}
        )

    def test_personal_site_person_sitewide(self):
        doc = profiles.build_from_profiles(
            ["sitewide", "person"],
            context={
                "site_url": "https://person.example/",
                "organization_name": "Studio",
                "person_name": "Alex",
                "url": "https://person.example/about",
            },
        )
        types = {n["@type"] for n in doc["@graph"]}
        self.assertTrue({"Organization", "WebSite", "Person"}.issubset(types))
