# Script Quality Validators

`validate_scripts.py` checks `Scripts/**/*.fos` (TLA AngelScript) for the
hygiene issues surfaced by the script refactoring audit. It is a **validator,
not a formatter**: by default it only reports. Autofixes for the few safe,
unambiguous checks are applied only on explicit `--fix`.

It complements `Tools/NullableEstimate/validate_nullable.py`, which owns
`?`/`FO_NULLABLE` placement and Event/RemoteCall signature parity. The two do
not overlap.

Generated files (`Content.fos`, `GuiScreens.fos`) are always excluded.

## Checks

| Check | Severity | Autofix | What it flags |
| ----- | -------- | ------- | ------------- |
| `trailing-blank-line` | error | yes | File must end with exactly one EOL terminator (no extra blank line, no missing newline). |
| `namespace-matches-filename` | error | no | First top-level `namespace X` must equal the file basename (allowlist: `ColorExt.fos` → `Color`). |
| `preprocessor-guard-balance` | error | no | `#if`/`#ifdef`/`#ifndef` must balance with `#endif`. |
| `component-null-probe` | error | yes | `x.Comp == null` / `!= null` on a component accessor → use `!x.HasComp` / `x.HasComp`. Component names are derived from `.HasXxx` usage across the tree. |
| `banner-tags` | warning | yes | `// Author:` / `// ver x.y` header banners (git carries authorship). |
| `textpack-magic-id` | warning | no | `"" + (1234)` magic text-pack ids → use a named `MsgStr`/`Enum` key. |
| `hand-rolled-utils` | warning | no | Calls to `UtilsForArray::Find/Present/Merge`, `Tla::Min/Max/Clamp/Abs/Distance/Pow2`, `Stdlib::*Arr*` that duplicate engine APIs. |
| `redundant-bool-return` | warning | no | `if (c) return true; else return false;` → `return c;` / `return !c;`. |
| `commented-out-code` | warning | no | Disabled code left as `//` comments. |
| `file-too-large` | warning | no | Non-generated file over 1500 lines — candidate for splitting. |

The `error` checks are currently clean across the tree (zero-tolerance gates).
The `warning` checks have a large existing backlog and are meant to be driven
down with the ratchet (see below), not gated absolutely.

## Usage

```bash
# Full report (exit 1 if any error-level violation)
py -3 Tools/ScriptQuality/validate_scripts.py

# Per-check counts only
py -3 Tools/ScriptQuality/validate_scripts.py --summary

# Snapshot current counts -> baseline.json
py -3 Tools/ScriptQuality/validate_scripts.py --baseline

# Fail only on NEW violations above the baseline (use in CI / pre-handoff)
py -3 Tools/ScriptQuality/validate_scripts.py --ratchet

# Apply the safe autofixes in place (trailing-blank-line, banner-tags,
# component-null-probe), then review the diff
py -3 Tools/ScriptQuality/validate_scripts.py --fix
```

VS Code tasks: **Analyze :: Script Quality** (summary) and
**Analyze :: Script Quality (Ratchet)**.

## Ratchet workflow

`baseline.json` records per-`(check, file)` violation counts. `--ratchet`
fails only when a file's count for a check rises above its baseline, so the
backlog can be burned down gradually while preventing regressions. After
deliberately reducing violations in a refactor pass, re-run `--baseline` to
lock in the lower numbers.
