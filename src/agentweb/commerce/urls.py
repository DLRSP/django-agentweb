"""URLs for the commerce / booking domain."""

from __future__ import annotations

from django.urls import path

from .views import CommerceDescriptorView

urlpatterns = [
    path(
        ".well-known/commerce.json",
        CommerceDescriptorView.as_view(),
        name="agentweb-commerce-descriptor",
    ),
]
