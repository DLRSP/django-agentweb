"""Application configuration for django-agentweb."""

from django.apps import AppConfig


class AgentwebConfig(AppConfig):
    """Single Django app exposing the five agent-web domains.

    Domains are sub-packages (``llms``, ``jsonld``, ``discovery``, ``webmcp``,
    ``commerce``, ``sdf``) activated per site via the ``AGENTWEB`` setting.
    """

    name = "agentweb"
    verbose_name = "Agentic Web"
    default_auto_field = "django.db.models.BigAutoField"
