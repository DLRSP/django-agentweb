"""Readability domain — ``llms.txt`` / ``llms-full.txt``.

Serves a curated, Markdown-style summary of the site for LLM agents. Supports
per-language variants (root ``/llms.txt`` index + ``/{lang}/llms.txt``) and can
be served dynamically (cached) or pre-rendered via the
``generate_llms_txt`` management command.
"""
