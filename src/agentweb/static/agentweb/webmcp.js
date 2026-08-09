/**
 * Browser WebMCP registration helper for django-agentweb.
 *
 * Real WebMCP (Chrome origin trial / W3C WebML CG) registers tools on the page
 * via navigator.modelContext (or document.modelContext). This script reads tool
 * descriptors from a JSON script tag and registers them when the API exists.
 *
 * Usage (template tag renders the config + this script):
 *   {% load agentweb_webmcp %}
 *   {% webmcp_register %}
 */
(function () {
  "use strict";

  function getModelContext() {
    if (typeof navigator !== "undefined" && navigator.modelContext) {
      return navigator.modelContext;
    }
    if (typeof document !== "undefined" && document.modelContext) {
      return document.modelContext;
    }
    return null;
  }

  function parseConfig() {
    var el = document.getElementById("agentweb-webmcp-config");
    if (!el) {
      return null;
    }
    try {
      return JSON.parse(el.textContent || "{}");
    } catch (err) {
      console.warn("[agentweb] invalid WebMCP config JSON", err);
      return null;
    }
  }

  function buildHandler(tool, bridgeBase) {
    return async function (input) {
      if (tool.requiresHumanConfirmation || tool.readOnlyHint === false) {
        return {
          error: "human confirmation required",
          requiresHumanConfirmation: true,
        };
      }
      if (!bridgeBase) {
        return {
          error: "no remote bridge; provide a page-local handler",
          name: tool.name,
          input: input || {},
        };
      }
      var url = bridgeBase.replace(/\/$/, "") + "/" + encodeURIComponent(tool.name);
      var response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(input || {}),
      });
      var data = await response.json().catch(function () {
        return {};
      });
      if (!response.ok) {
        return { error: data.error || "tool failed", status: response.status, data: data };
      }
      return data.result !== undefined ? data.result : data;
    };
  }

  function register() {
    var ctx = getModelContext();
    var config = parseConfig();
    if (!config || !Array.isArray(config.tools)) {
      return;
    }
    if (!ctx || typeof ctx.registerTool !== "function") {
      // Progressive enhancement: no browser WebMCP — descriptors stay in DOM.
      return;
    }
    var bridge = config.remoteBridgeUrl || null;
    config.tools.forEach(function (tool) {
      if (!tool || !tool.name) {
        return;
      }
      try {
        ctx.registerTool(
          {
            name: tool.name,
            description: tool.description || "",
            inputSchema: tool.inputSchema || { type: "object" },
            readOnlyHint: tool.readOnlyHint !== false,
            exposedTo: tool.exposedTo || "agents",
            untrustedContentHint: tool.untrustedContentHint !== false,
            requiresHumanConfirmation: !!tool.requiresHumanConfirmation,
          },
          buildHandler(tool, bridge)
        );
      } catch (err) {
        console.warn("[agentweb] WebMCP registerTool failed", tool.name, err);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", register);
  } else {
    register();
  }
})();
