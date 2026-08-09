"""Root URLconf for django-agentweb.

Only the URL modules of **enabled** domains are wired in, so a site exposes
exactly the agent-web surfaces it opts into via ``AGENTWEB``. Include this once
in your project's ``urls.py``::

    path("", include("agentweb.urls"))
"""

from __future__ import annotations

from django.urls import include, path

from . import conf

urlpatterns: list = []

if conf.is_enabled("LLMS"):
    urlpatterns.append(path("", include("agentweb.llms.urls")))

if conf.is_enabled("DISCOVERY"):
    urlpatterns.append(path("", include("agentweb.discovery.urls")))

if conf.is_enabled("WEBMCP"):
    urlpatterns.append(path("", include("agentweb.webmcp.urls")))

if conf.is_enabled("COMMERCE"):
    urlpatterns.append(path("", include("agentweb.commerce.urls")))

if conf.is_enabled("SDF"):
    urlpatterns.append(path("", include("agentweb.sdf.urls")))
