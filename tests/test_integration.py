"""Cross-domain integration tests for agent-web surfaces.

Covers language-isolated LLMS caching, JSON-LD script breakout, REMOTE_BRIDGE
gates, discovery Link headers, and the proxy DATA_SOURCE network posture.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from agentweb.jsonld import builders
from agentweb.webmcp import tools


def _agentweb(**domain_overrides):
    base = {name: dict(cfg) for name, cfg in settings.AGENTWEB.items()}
    for name, overrides in domain_overrides.items():
        base[name] = {**base.get(name, {}), **overrides}
    return base


class LlmsLanguageCacheIsolationTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()
        translation.deactivate()

    def test_llms_cache_does_not_leak_across_languages(self):
        """Cache keys must include language so EN hits do not serve IT."""
        langs = [("en", "English"), ("it", "Italian")]
        v1 = _agentweb(
            LLMS={
                "ENABLED": True,
                "TITLE": "Title-V1",
                "DESCRIPTION": "desc",
                "CACHE_TIMEOUT": 3600,
                "SECTIONS": [],
            }
        )
        with override_settings(
            AGENTWEB=v1, LANGUAGE_CODE="en", LANGUAGES=langs
        ):
            en_resp = self.client.get(reverse("agentweb-llms-txt"))
            self.assertEqual(en_resp.status_code, 200)
            self.assertEqual(en_resp["Content-Language"], "en")
            self.assertIn("Title-V1", en_resp.content.decode())

        # Mutate curated title; English cache must keep V1 while Italian misses.
        v2 = _agentweb(
            LLMS={
                "ENABLED": True,
                "TITLE": "Title-V2",
                "DESCRIPTION": "desc",
                "CACHE_TIMEOUT": 3600,
                "SECTIONS": [],
            }
        )
        with override_settings(
            AGENTWEB=v2, LANGUAGE_CODE="en", LANGUAGES=langs
        ):
            en_cached = self.client.get(reverse("agentweb-llms-txt"))
            self.assertEqual(en_cached["Content-Language"], "en")
            self.assertIn("Title-V1", en_cached.content.decode())
            self.assertNotIn("Title-V2", en_cached.content.decode())

            # Fresh client + i18n prefix so LocaleMiddleware activates Italian
            # (session language cookie from the English client must not apply).
            it_client = self.client_class()
            it_resp = it_client.get("/it/llms.txt")
            self.assertEqual(it_resp.status_code, 200)
            self.assertEqual(it_resp["Content-Language"], "it")
            self.assertIn("Title-V2", it_resp.content.decode())
            self.assertNotIn("Title-V1", it_resp.content.decode())

    def test_llms_cache_hit_serves_same_body_on_second_get(self):
        """With CACHE_TIMEOUT > 0, a second GET returns the cached body."""
        cfg = _agentweb(
            LLMS={
                "ENABLED": True,
                "TITLE": "Cache-Hit-Title",
                "DESCRIPTION": "desc",
                "CACHE_TIMEOUT": 3600,
                "SECTIONS": [],
            }
        )
        with override_settings(AGENTWEB=cfg, LANGUAGE_CODE="en"):
            first = self.client.get(reverse("agentweb-llms-txt"))
            second = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.content, second.content)
        self.assertIn("Cache-Hit-Title", second.content.decode())


class GenerateLlmsTxtCommandTests(TestCase):
    def test_generate_llms_txt_command_smoke(self):
        """Management command writes llms.txt when present."""
        with tempfile.TemporaryDirectory() as tmp:
            call_command("generate_llms_txt", output=tmp)
            path = Path(tmp) / "llms.txt"
            self.assertTrue(path.is_file())
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("#"))
            self.assertGreater(len(text), 10)


class JsonLdScriptEscapeTests(TestCase):
    def test_jsonld_script_escapes_script_terminator(self):
        hostile = builders.build_hotel(
            name='</script><script>alert("xss")</script>'
        )
        rendered = Template(
            "{% load agentweb_jsonld %}{% jsonld_script hotel %}"
        ).render(Context({"hotel": hostile}))
        self.assertEqual(rendered.count("</script>"), 1)
        inner = rendered[
            len('<script type="application/ld+json">') : -len("</script>")
        ]
        self.assertNotIn("</script>", inner)
        self.assertIn("\\u003c/script\\u003e", inner)
        payload = (
            inner.replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026", "&")
        )
        self.assertEqual(
            json.loads(payload)["name"],
            '</script><script>alert("xss")</script>',
        )


class RemoteBridgeGateTests(TestCase):
    def setUp(self):
        tools.clear()

    def tearDown(self):
        tools.clear()

    def test_remote_bridge_off_returns_404(self):
        @tools.register(name="ping", description="Ping.", read_only_hint=True)
        def _ping(request, **params):
            return {"ok": True}

        url = reverse("agentweb-webmcp-tool", args=["ping"])
        response = self.client.post(
            url, data="{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("remote bridge disabled", response.json()["error"])

    def test_state_changing_tool_returns_409_when_bridge_on(self):
        @tools.register(
            name="mutate",
            description="Mutate.",
            read_only_hint=False,
            requires_human_confirmation=True,
        )
        def _mutate(request, **params):  # pragma: no cover - blocked
            return {"done": True}

        with override_settings(
            AGENTWEB=_agentweb(WEBMCP={"ENABLED": True, "REMOTE_BRIDGE": True})
        ):
            url = reverse("agentweb-webmcp-tool", args=["mutate"])
            response = self.client.post(
                url, data="{}", content_type="application/json"
            )
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.json()["requiresHumanConfirmation"])


class DiscoveryLinkHeaderTests(TestCase):
    def test_link_headers_present_when_discovery_enabled(self):
        response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        link = response["Link"]
        self.assertIn('rel="ai-catalog"', link)
        self.assertIn('rel="agent-descriptor"', link)
        self.assertEqual(response["X-Agentweb-Discovery"], "1")

    def test_no_discovery_headers_when_disabled(self):
        with override_settings(
            AGENTWEB=_agentweb(DISCOVERY={"ENABLED": False})
        ):
            response = self.client.get(reverse("agentweb-llms-txt"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Link", response)
        self.assertNotIn("X-Agentweb-Discovery", response)


class ProxyDataSourceSsrfGapTests(TestCase):
    """DATA_SOURCE=proxy must not open unguarded outbound URL fetches yet.

    When a server-side proxy fetch is added, link-local and loopback targets
    must be blocked before enabling that path.
    """

    def test_proxy_data_source_has_no_url_fetch_helper(self):
        import agentweb.commerce as commerce_pkg
        import agentweb.webmcp as webmcp_pkg

        for mod in (webmcp_pkg, commerce_pkg):
            self.assertFalse(
                hasattr(mod, "fetch_vendor")
                or hasattr(mod, "proxy_get")
                or hasattr(mod, "safe_proxy_url"),
                msg=(
                    f"{mod.__name__} must not expose an unguarded proxy fetch; "
                    "add link-local blocking before shipping DATA_SOURCE=proxy IO"
                ),
            )

    def test_proxy_mode_does_not_open_network_on_tool_invoke(self):
        """Read-only bridge invoke must not perform outbound HTTP today."""

        @tools.register(
            name="echo",
            description="Echo.",
            read_only_hint=True,
            input_schema={"type": "object"},
        )
        def _echo(request, **params):
            return params

        with override_settings(
            AGENTWEB=_agentweb(
                WEBMCP={
                    "ENABLED": True,
                    "DATA_SOURCE": "proxy",
                    "REMOTE_BRIDGE": True,
                }
            )
        ):
            with patch("urllib.request.urlopen") as urlopen:
                with patch("socket.create_connection") as create_conn:
                    url = reverse("agentweb-webmcp-tool", args=["echo"])
                    response = self.client.post(
                        url,
                        data=json.dumps({"x": 1}),
                        content_type="application/json",
                    )
        self.assertEqual(response.status_code, 200)
        urlopen.assert_not_called()
        create_conn.assert_not_called()
