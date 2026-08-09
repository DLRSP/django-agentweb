"""Validate llms.txt body against the llmstxt.org minimal grammar."""

from __future__ import annotations

from typing import List


def validate_llms_txt(body: str) -> List[str]:
    """Return a list of validation errors (empty if the document is OK).

    Checks the hard requirements used by community validators / Agentic
    Browsing audits: non-empty body, exactly one leading H1, no HTML tags.
    """
    errors: List[str] = []
    text = (body or "").lstrip("\ufeff")  # allow BOM
    if not text.strip():
        return ["empty document"]

    lines = text.splitlines()
    # Skip leading blank lines.
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return ["empty document"]

    first = lines[idx].rstrip()
    if not first.startswith("# ") or first.startswith("##"):
        errors.append("missing H1 as first non-empty line")
    elif len(first) <= 2:
        errors.append("empty H1 title")

    h1_count = sum(
        1
        for line in lines
        if line.startswith("# ") and not line.startswith("##")
    )
    if h1_count > 1:
        errors.append(f"expected one H1, found {h1_count}")

    lowered = text.lower()
    for tag in ("<html", "<script", "<div", "<p>"):
        if tag in lowered:
            errors.append(f"HTML tag not allowed in llms.txt ({tag})")
            break

    return errors
