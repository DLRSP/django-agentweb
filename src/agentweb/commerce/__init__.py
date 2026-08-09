"""Commerce / booking domain — agentic commerce discovery + hooks.

Provides the discovery surface for agentic commerce/booking (CAP / UCP for
Lodging / AP2) and integration hooks. Transactional flows (real reservations,
payments) are delegated to a booking-engine vendor configured via
``COMMERCE.VENDOR``; this module does not process payments itself.

Priority use cases (e.g. an independent hotel): expose enough for an agent to
check availability, simulate a booking price and start a **direct** reservation,
reducing OTA dependence. Off by default.
"""

from .cap_lite import build_cap_lite_catalog, build_cap_lite_product

__all__ = ["build_cap_lite_catalog", "build_cap_lite_product"]
