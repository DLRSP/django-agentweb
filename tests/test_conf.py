"""Tests for the settings access layer (defaults + per-site activation)."""

from django.test import TestCase, override_settings

from agentweb import conf


class ConfTestCase(TestCase):
    def test_unconfigured_domain_defaults_to_off(self):
        with override_settings(AGENTWEB={}):
            for domain in conf.DEFAULTS:
                self.assertFalse(
                    conf.is_enabled(domain),
                    msg=f"{domain} should default to disabled",
                )

    def test_user_override_merges_with_defaults(self):
        with override_settings(AGENTWEB={"LLMS": {"ENABLED": True}}):
            llms = conf.get_domain("LLMS")
            self.assertTrue(llms["ENABLED"])
            # Default keys still present.
            self.assertIn("CACHE_TIMEOUT", llms)

    def test_is_enabled_is_case_insensitive(self):
        with override_settings(AGENTWEB={"DISCOVERY": {"ENABLED": True}}):
            self.assertTrue(conf.is_enabled("discovery"))
