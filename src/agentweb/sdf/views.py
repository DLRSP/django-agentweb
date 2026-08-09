"""Views for the SDF domain."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views import View


class SdfDescriptorView(View):
    """Serve a minimal ``/.well-known/sdf.json`` placeholder.

    Scaffold only: emits a stub document so the surface is discoverable when the
    domain is explicitly enabled. Full SDF support is deferred.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse(
            {
                "schemaVersion": "0.1",
                "status": "experimental",
                "note": "SDF support is a placeholder behind a feature flag.",
            }
        )
