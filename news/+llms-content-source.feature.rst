LLMS editorial content can be managed in Django admin (``LlmsDocument`` per
site and language) while feature flags stay in ``APP_CONFIG["agentweb"]``.
Settings ``TITLE`` / ``DESCRIPTION`` / ``BODY`` / ``SECTIONS`` remain the
fallback when no database row exists.
