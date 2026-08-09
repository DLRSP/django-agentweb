"""URLs for the SDF domain."""

from __future__ import annotations

from django.urls import path

from .views import SdfDescriptorView

urlpatterns = [
    path(
        ".well-known/sdf.json",
        SdfDescriptorView.as_view(),
        name="agentweb-sdf-descriptor",
    ),
]
