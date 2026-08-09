"""Discovery domain — ``/.well-known`` agent descriptors.

Publishes a machine-readable capability descriptor so agents can discover which
agent-web features the site exposes (llms.txt, WebMCP manifest, commerce
endpoints, …). Optional Web Bot Auth (RFC 9421) enforcement lives behind the
``webbotauth`` extra and the ``DISCOVERY.WEB_BOT_AUTH`` flag.
"""
