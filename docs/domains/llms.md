# Readability — llms.txt

Serves `llms.txt` and `llms-full.txt` so agents can read a curated Markdown
summary of your site ([llmstxt.org](https://llmstxt.org/)).

- **Content-Type:** `text/plain; charset=utf-8`
- **Shape:** H1 title, blockquote summary, optional body, H2 link sections
- **i18n:** root `/llms.txt` plus `/{lang}/llms.txt` when included under
  Django `i18n_patterns` (`I18N_VARIANTS`)
- **Generation:** dynamic language-keyed cached view; `generate_llms_txt`
  management command for static files
- **Safety:** `EXCLUDE_PATTERNS` strips private/admin URLs from curated sections

Configure via `AGENTWEB["LLMS"]` (`TITLE`, `DESCRIPTION`, `SECTIONS`, …).
