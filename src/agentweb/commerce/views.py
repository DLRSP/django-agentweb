"""Views for the commerce / booking domain."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views import View

from .. import conf


class CommerceDescriptorView(View):
    """Serve a discovery document for agentic commerce/booking.

    Describes how an agent can interact (availability, price simulation, direct
    booking) and which vendor backs the transactional flow. Actual transactions
    are delegated to the vendor — see ``COMMERCE.VENDOR``.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        cfg = conf.get_domain("COMMERCE")
        return JsonResponse(
            {
                "schemaVersion": "0.1",
                "vendor": cfg.get("VENDOR"),
                "operations": [
                    "checkAvailability",
                    "simulateBookingCost",
                    "startDirectBooking",
                ],
                # Booking is a state-changing action: agents must route through
                # a human-in-the-loop confirmation, never auto-commit.
                "requiresHumanConfirmation": True,
                "untrustedContentHint": True,
            }
        )
