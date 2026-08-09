"""Views for the WebMCP domain.

Browser WebMCP registers tools via ``navigator.modelContext`` (see
``static/agentweb/webmcp.js``). This module still serves:

* a JSON **manifest** of tool descriptors (for discovery / page embedding), and
* an optional **remote bridge** HTTP invoke endpoint (off by default via
  ``WEBMCP.REMOTE_BRIDGE``) for headless agents — not a substitute for
  in-browser WebMCP.
"""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .. import conf
from . import tools


class WebMCPManifestView(View):
    """Serve tool descriptors for page registration and discovery."""

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse(
            {
                "schemaVersion": "0.1",
                "protocol": "webmcp-descriptors",
                "note": (
                    "Register these tools with navigator.modelContext on the "
                    "page (see agentweb/webmcp.js). This JSON is not the "
                    "browser WebMCP API itself."
                ),
                "tools": [
                    tool.to_descriptor() for tool in tools.all_tools().values()
                ],
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class WebMCPToolView(View):
    """Optional HTTP bridge for remote/headless tool invocation.

    Disabled unless ``AGENTWEB['WEBMCP']['REMOTE_BRIDGE']`` is True. Read-only
    tools execute; state-changing / human-confirmation tools return 409.
    """

    def post(
        self, request: HttpRequest, name: str, *args, **kwargs
    ) -> JsonResponse:
        if not conf.get_domain("WEBMCP").get("REMOTE_BRIDGE"):
            return JsonResponse({"error": "remote bridge disabled"}, status=404)

        tool = tools.get(name)
        if tool is None:
            return JsonResponse({"error": "unknown tool"}, status=404)

        if tool.requires_human_confirmation or not tool.read_only_hint:
            return JsonResponse(
                {
                    "error": "human confirmation required",
                    "requiresHumanConfirmation": True,
                },
                status=409,
            )

        try:
            params = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON body"}, status=400)

        if tool.input_schema:
            # Minimal shape check: reject non-object payloads when schema says
            # type=object. Full JSON Schema validation is deferred.
            expected = tool.input_schema.get("type")
            if expected == "object" and not isinstance(params, dict):
                return JsonResponse(
                    {"error": "params must be a JSON object"}, status=400
                )

        result = tool.handler(request, **params)
        return JsonResponse({"result": result})
