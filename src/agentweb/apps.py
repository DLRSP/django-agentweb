"""Application configuration for django-agentweb."""

from django.apps import AppConfig


class AgentwebConfig(AppConfig):
    """Single Django app exposing the five agent-web domains.

    Domains are sub-packages (``llms``, ``jsonld``, ``discovery``, ``webmcp``,
    ``commerce``, ``sdf``) activated per site via
    ``APP_CONFIG["agentweb"]`` (optional top-level ``AGENTWEB`` override).

    Editorial LLMS copy may live in models (admin); feature flags stay in
    ``APP_CONFIG``.
    """

    name = "agentweb"
    verbose_name = "Agentic Web"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from agentweb.llms.cache import connect_llms_cache_signals

        connect_llms_cache_signals()
