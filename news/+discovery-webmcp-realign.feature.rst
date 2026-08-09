Discovery adds ARD ``/.well-known/ai-catalog.json`` (specVersion 1.0, CORS ``*``)
alongside the existing agent descriptor. WebMCP realigned to browser-native
registration (``{% webmcp_register %}`` + ``webmcp.js`` for
``navigator.modelContext``); HTTP tool invoke is an opt-in remote bridge
(``REMOTE_BRIDGE``, default off).
