"""Tests for the settings access layer (APP_CONFIG + defaults)."""

from django.test import SimpleTestCase, TestCase, override_settings

from agentweb import conf


class ConfDefaultsTestCase(SimpleTestCase):
    def test_unconfigured_domain_defaults_to_off(self):
        with override_settings(APP_CONFIG={}, AGENTWEB=None):
            for domain in conf.DEFAULTS:
                self.assertFalse(
                    conf.is_enabled(domain),
                    msg=f"{domain} should default to disabled",
                )

    def test_app_config_agentweb_merges_with_defaults(self):
        with override_settings(
            APP_CONFIG={"agentweb": {"LLMS": {"ENABLED": True}}},
            AGENTWEB=None,
        ):
            llms = conf.get_domain("LLMS")
            self.assertTrue(llms["ENABLED"])
            self.assertIn("CACHE_TIMEOUT", llms)

    def test_top_level_agentweb_overrides_app_config(self):
        with override_settings(
            APP_CONFIG={"agentweb": {"LLMS": {"ENABLED": False}}},
            AGENTWEB={"LLMS": {"ENABLED": True, "TITLE": "Top"}},
        ):
            llms = conf.get_domain("LLMS")
            self.assertTrue(llms["ENABLED"])
            self.assertEqual(llms["TITLE"], "Top")

    def test_is_enabled_is_case_insensitive(self):
        with override_settings(
            APP_CONFIG={"agentweb": {"DISCOVERY": {"ENABLED": True}}},
            AGENTWEB=None,
        ):
            self.assertTrue(conf.is_enabled("discovery"))


class ConfTestSuiteWiringTestCase(TestCase):
    """Smoke: test settings enable domains via APP_CONFIG."""

    def test_test_settings_enable_llms(self):
        self.assertTrue(conf.is_enabled("LLMS"))
