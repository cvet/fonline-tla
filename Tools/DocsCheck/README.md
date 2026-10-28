# DocsCheck

Dependency-free Markdown corpus auditor for project documentation. It checks
every Markdown file known to git here — tracked plus new untracked, non-ignored
files, so freshly authored pages are audited before committing (the Engine
submodule is a separate corpus). A tracked path deleted from the working tree
is skipped.

## What it checks

- strict UTF-8 and absence of the U+FFFD replacement character;
- exactly one H1 per page (one-line import wrappers are exempt) and no
  heading-level jumps;
- local inline links resolving to existing files, with GitHub-style anchors
  from ATX headings; percent-encoded local paths and fragments are decoded;
- repeated ATX headings receive `-1`, `-2`, ... anchor suffixes, and inline
  code markup inside a heading is ignored when computing its anchor;
- content inside backtick or tilde fences (three or more markers) is ignored
  for headings and links; a closing fence must use the opening marker kind and
  be at least as long. An unclosed fence is reported;
- destinations beginning with `http://`, `https://` or `mailto:` are skipped.

## Limits

This is an inline-link/ATX-heading subset, not a Markdown renderer, and it is
not a documentation schema validator. Reference-style links, HTML, nested
block structure and viewer-specific rendering are not audited. Inline image
destinations are treated like ordinary local links. External URLs are not
fetched or validated; external-link auditing is separate. Size, readability,
prose quality, link-rot and reference-link coverage are separate audits; use
[DocumentationMaintenance](../../Docs/DocumentationMaintenance.md) as the
project procedure.

Run it with the `Check :: Docs Links` VS Code task or directly:

```sh
py -3 Tools/DocsCheck/check_docs.py           # audit; exit 1 on findings
py -3 Tools/DocsCheck/check_docs.py --selftest  # isolated detector fixtures
```

`--selftest` creates its own small `Docs/` and `README.md` fixtures in a fresh
temporary directory and never writes into the repository.

Use it for documentation-only changes instead of a native build, per
[DocumentationMaintenance](../../Docs/DocumentationMaintenance.md). The
checker is deliberately independent of any site generator: it validates
references and basic structure, not rendering.
