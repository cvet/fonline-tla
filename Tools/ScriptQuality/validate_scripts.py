#!/usr/bin/env python3
"""Quality validators for TLA AngelScript (`Scripts/**/*.fos`).

This is a *validator*, not an auto-formatter: by default it only reports.
Autofixes for the unambiguous, safe checks are applied only on explicit
`--fix`. It complements `Tools/NullableEstimate/validate_nullable.py`
(which owns `?`/FO_NULLABLE placement and Event/RemoteCall signature
parity); this tool owns the broader hygiene rules surfaced by the script
refactoring audit.

Checks (severity):
  ERROR   trailing-blank-line        exactly one terminator at EOF, no extra blank
  ERROR   namespace-matches-filename first top-level namespace == file basename
  ERROR   preprocessor-guard-balance #if/#ifdef/#ifndef balance with #endif
  ERROR   component-null-probe       `.Comp == null` instead of `!HasComp`
  WARNING banner-tags               `// Author:` / `// ver x.y` header banners
  WARNING textpack-magic-id         `"" + (1234)` magic text-pack ids
  WARNING hand-rolled-utils         calls to helpers that duplicate engine APIs
  WARNING cyrillic-comment          Cyrillic text inside comments (policy: English)
  WARNING redundant-bool-return     `if (c) return true; else return false;`
  WARNING commented-out-code        disabled code left as `//` comments
  WARNING file-too-large            non-generated file over the size threshold

Modes:
  (default)     report all; exit 1 if any ERROR-level violation exists
  --summary     print per-check counts only
  --baseline    snapshot current per-(check,file) counts to baseline.json
  --ratchet     exit 1 only on violations ABOVE the baseline (no-new-violations)
  --fix         apply safe autofixes (trailing-blank-line, banner-tags,
                component-null-probe), then re-report

Usage:
  python Tools/ScriptQuality/validate_scripts.py
  python Tools/ScriptQuality/validate_scripts.py --summary
  python Tools/ScriptQuality/validate_scripts.py --baseline
  python Tools/ScriptQuality/validate_scripts.py --ratchet
  python Tools/ScriptQuality/validate_scripts.py --fix
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "Scripts"
BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"

# Generated files — never hand-edited, excluded from every check.
GENERATED = frozenset({"GuiScreens.fos", "Content.fos"})

# The single intentional namespace != filename case.
NAMESPACE_ALLOW = {"ColorExt.fos": "Color"}

FILE_SIZE_WARN = 1500  # non-generated .fos lines

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass
class Violation:
    check: str
    path: str  # relative to ROOT, forward slashes
    line: int
    message: str
    severity: str


# --------------------------------------------------------------------------
# Shared lexer: classify every character as code / comment / string so each
# validator can run regexes against "code only" or "comments only" without
# being fooled by the other. Newlines are preserved in the masked text so
# line numbers stay accurate.
# --------------------------------------------------------------------------

def classify(text: str) -> str:
    """Return a per-char class string: 'c' code, 'L' line-comment,
    'B' block-comment, 's' string, 'h' char-literal. Same length as text."""
    n = len(text)
    out = bytearray(b"c" * n)
    i = 0
    state = "c"  # c, L, B, s, h
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state == "c":
            if c == "/" and nxt == "/":
                state = "L"
                out[i] = ord("L")
                out[i + 1] = ord("L")
                i += 2
                continue
            if c == "/" and nxt == "*":
                state = "B"
                out[i] = ord("B")
                out[i + 1] = ord("B")
                i += 2
                continue
            if c == '"':
                state = "s"
                out[i] = ord("s")
                i += 1
                continue
            if c == "'":
                state = "h"
                out[i] = ord("h")
                i += 1
                continue
            i += 1
            continue
        if state == "L":
            if c == "\n":
                state = "c"
                # leave newline as code so line breaks read as code
            else:
                out[i] = ord("L")
            i += 1
            continue
        if state == "B":
            out[i] = ord("B")
            if c == "*" and nxt == "/":
                out[i + 1] = ord("B")
                i += 2
                state = "c"
                continue
            i += 1
            continue
        if state == "s":
            if c == "\\":
                if i + 1 < n:
                    out[i] = ord("s")
                    out[i + 1] = ord("s")
                i += 2
                continue
            out[i] = ord("s")
            if c == '"':
                state = "c"
            i += 1
            continue
        if state == "h":
            if c == "\\":
                if i + 1 < n:
                    out[i] = ord("h")
                    out[i + 1] = ord("h")
                i += 2
                continue
            out[i] = ord("h")
            if c == "'":
                state = "c"
            i += 1
            continue
    return out.decode("ascii")


def mask_to(text: str, kinds: str, keep: str) -> str:
    """Return text with every char whose class is NOT in `keep` replaced by a
    space, except newlines which are preserved (keeps line numbers stable)."""
    keep_set = set(keep)
    chars = []
    for ch, k in zip(text, kinds):
        if k in keep_set:
            chars.append(ch)
        elif ch == "\n":
            chars.append("\n")
        else:
            chars.append(" ")
    return "".join(chars)


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# --------------------------------------------------------------------------
# Component-accessor set: derive from `.HasXxx` usage across all scripts so
# the component-null-probe check knows which `.Xxx == null` are real probes.
# --------------------------------------------------------------------------

HAS_FLAG_RE = re.compile(r"\.Has([A-Z][A-Za-z0-9_]*)\b")


def derive_component_names(all_text: str) -> set[str]:
    return set(HAS_FLAG_RE.findall(all_text))


# --------------------------------------------------------------------------
# Individual checks. Each returns a list[Violation] for one file.
# --------------------------------------------------------------------------

NAMESPACE_RE = re.compile(r"^[ \t]*namespace[ \t]+([A-Za-z_]\w*)", re.MULTILINE)
PRE_OPEN_RE = re.compile(r"^[ \t]*#[ \t]*(if|ifdef|ifndef)\b")
PRE_CLOSE_RE = re.compile(r"^[ \t]*#[ \t]*endif\b")
BANNER_AUTHOR_RE = re.compile(r"^[ \t]*//[ \t]*Author[ \t]*:", re.IGNORECASE)
BANNER_VER_RE = re.compile(r"^[ \t]*//[ \t]*ver\b[ \t]*[\d.]", re.IGNORECASE)
TEXTPACK_MAGIC_RE = re.compile(r'""[ \t]*\+[ \t]*\(?[ \t]*(\d+)')
CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")
REDUNDANT_BOOL_RE = re.compile(
    r"if[ \t]*\([^\n]*\)[ \t]*\{?[ \t]*\n?[ \t]*return[ \t]+(true|false)[ \t]*;"
    r"[ \t\r\n]*\}?[ \t\r\n]*(?:else[ \t]*\{?[ \t\r\n]*)?return[ \t]+(true|false)[ \t]*;"
)
COMMENTED_CODE_RE = re.compile(
    r"^[ \t]*//[ \t]*(?:if|for|while|return|switch|else|do)\b[^\n]*[;{)]"
    r"|^[ \t]*//[ \t]*[A-Za-z_][\w:]*[ \t]*\([^\n]*\)[ \t]*;"
)
HAND_ROLLED = [
    (re.compile(r"\bUtilsForArray::(FindInArray|Present|MergeArrays)\b"),
     "use native array members (.find(x) != -1 / .insertLast)"),
    (re.compile(r"\bTla::(Min|Max|Clamp|Abs|Distance|Pow2)\b"),
     "use the engine Math:: namespace (Math::Min/Max/Clamp/Abs) or Game.GetDistance"),
    (re.compile(r"\bStdlib::(StrToIntArr|IntArrToStr|StrToStrArr|StrArrToStr|StrToHStrArr|HStrArrToStr)\b"),
     "use native string.split / a short join loop"),
]


def check_trailing_blank_line(rel: str, raw: bytes) -> list[Violation]:
    if not raw:
        return [Violation("trailing-blank-line", rel, 1, "file is empty", SEVERITY_ERROR)]
    stripped = raw.rstrip(b"\r\n")
    trailer = raw[len(stripped):]
    if trailer not in (b"\r\n", b"\n"):
        nlines = raw.count(b"\n") + 1
        if not trailer:
            msg = "file does not end with a newline"
        else:
            msg = "file has trailing blank line(s); keep exactly one terminator at EOF"
        return [Violation("trailing-blank-line", rel, nlines, msg, SEVERITY_ERROR)]
    return []


def check_namespace(rel: str, name: str, text: str) -> list[Violation]:
    m = NAMESPACE_RE.search(text)
    if not m:
        return []
    declared = m.group(1)
    base = name[:-4]  # strip .fos
    expected = NAMESPACE_ALLOW.get(name, base)
    if declared != expected:
        return [Violation("namespace-matches-filename", rel, line_of(text, m.start()),
                          f"namespace '{declared}' != expected '{expected}' (filename)", SEVERITY_ERROR)]
    return []


def check_guard_balance(rel: str, code: str) -> list[Violation]:
    out: list[Violation] = []
    stack: list[int] = []
    for idx, ln in enumerate(code.splitlines(), start=1):
        if PRE_OPEN_RE.match(ln):
            stack.append(idx)
        elif PRE_CLOSE_RE.match(ln):
            if not stack:
                out.append(Violation("preprocessor-guard-balance", rel, idx,
                                     "#endif without matching #if/#ifdef/#ifndef", SEVERITY_ERROR))
            else:
                stack.pop()
    for open_line in stack:
        out.append(Violation("preprocessor-guard-balance", rel, open_line,
                             "#if/#ifdef/#ifndef without matching #endif", SEVERITY_ERROR))
    return out


def check_component_null_probe(rel: str, code: str, text: str, components: set[str]) -> list[Violation]:
    if not components:
        return []
    out: list[Violation] = []
    alt = "|".join(sorted(re.escape(c) for c in components))
    rx = re.compile(r"\.(" + alt + r")[ \t]*(==|!=)[ \t]*null\b")
    for m in rx.finditer(code):
        comp = m.group(1)
        op = m.group(2)
        fix = f"!{'.'}Has{comp}" if op == "==" else f".Has{comp}"
        out.append(Violation("component-null-probe", rel, line_of(text, m.start()),
                             f".{comp} {op} null — use {'!x.Has' if op == '==' else 'x.Has'}{comp} (component accessors are guarded by Has{comp})",
                             SEVERITY_ERROR))
    return out


def check_banner_tags(rel: str, text: str, kinds: str) -> list[Violation]:
    out: list[Violation] = []
    comment = mask_to(text, kinds, "LB")
    for idx, ln in enumerate(comment.splitlines(), start=1):
        if BANNER_AUTHOR_RE.match(ln) or BANNER_VER_RE.match(ln):
            out.append(Violation("banner-tags", rel, idx,
                                 "remove author/version banner comment (git carries authorship)",
                                 SEVERITY_WARNING))
    return out


def check_textpack_magic(rel: str, text: str, kinds: str) -> list[Violation]:
    # The `""` empty-string literal is part of the pattern, so keep string
    # literals in the mask (blank only comments) to avoid losing it.
    src = mask_to(text, kinds, "csh")
    out: list[Violation] = []
    for m in TEXTPACK_MAGIC_RE.finditer(src):
        out.append(Violation("textpack-magic-id", rel, line_of(text, m.start()),
                             f'"" + ({m.group(1)}) magic text id — use a named MsgStr/Enum key', SEVERITY_WARNING))
    return out


def check_hand_rolled(rel: str, code: str, text: str) -> list[Violation]:
    out: list[Violation] = []
    for rx, hint in HAND_ROLLED:
        for m in rx.finditer(code):
            out.append(Violation("hand-rolled-utils", rel, line_of(text, m.start()),
                                 f"{m.group(0)} duplicates an engine API — {hint}", SEVERITY_WARNING))
    return out


def check_cyrillic_comment_lines(rel: str, text: str, kinds: str) -> list[Violation]:
    comment = mask_to(text, kinds, "LB")
    out: list[Violation] = []
    for idx, ln in enumerate(comment.splitlines(), start=1):
        if CYRILLIC_RE.search(ln):
            out.append(Violation("cyrillic-comment", rel, idx,
                                 "Cyrillic text in comment — committed comments should be English", SEVERITY_WARNING))
    return out


def check_redundant_bool(rel: str, code: str, text: str) -> list[Violation]:
    out: list[Violation] = []
    for m in REDUNDANT_BOOL_RE.finditer(code):
        if m.group(1) != m.group(2):  # opposite booleans
            out.append(Violation("redundant-bool-return", rel, line_of(text, m.start()),
                                 "if/else returning opposite bools — collapse to `return COND;` / `return !COND;`",
                                 SEVERITY_WARNING))
    return out


def check_commented_code(rel: str, text: str, kinds: str) -> list[Violation]:
    comment = mask_to(text, kinds, "LB")
    out: list[Violation] = []
    for idx, ln in enumerate(comment.splitlines(), start=1):
        if CYRILLIC_RE.search(ln):
            continue
        if "///@" in ln or "////" in ln:
            continue
        if COMMENTED_CODE_RE.match(ln):
            out.append(Violation("commented-out-code", rel, idx,
                                 "commented-out code — delete dead code (git carries history)", SEVERITY_WARNING))
    return out


def check_file_size(rel: str, text: str) -> list[Violation]:
    nlines = text.count("\n") + 1
    if nlines > FILE_SIZE_WARN:
        return [Violation("file-too-large", rel, 1,
                          f"{nlines} lines (> {FILE_SIZE_WARN}) — consider splitting into focused modules",
                          SEVERITY_WARNING)]
    return []


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def collect_files() -> list[Path]:
    return sorted(p for p in SCRIPTS_ROOT.rglob("*.fos") if p.name not in GENERATED)


def analyze() -> list[Violation]:
    files = collect_files()
    # Build component set from the whole tree first.
    all_text = []
    cache: dict[Path, tuple[str, bytes, str]] = {}
    for f in files:
        raw = f.read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        kinds = classify(text)
        cache[f] = (text, raw, kinds)
        all_text.append(mask_to(text, kinds, "c"))
    components = derive_component_names("\n".join(all_text))

    violations: list[Violation] = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        text, raw, kinds = cache[f]
        code = mask_to(text, kinds, "c")
        violations += check_trailing_blank_line(rel, raw)
        violations += check_namespace(rel, f.name, text)
        violations += check_guard_balance(rel, code)
        violations += check_component_null_probe(rel, code, text, components)
        violations += check_banner_tags(rel, text, kinds)
        violations += check_textpack_magic(rel, text, kinds)
        violations += check_hand_rolled(rel, code, text)
        violations += check_cyrillic_comment_lines(rel, text, kinds)
        violations += check_redundant_bool(rel, code, text)
        violations += check_commented_code(rel, text, kinds)
        violations += check_file_size(rel, text)
    return violations


def counts_by_check(violations: list[Violation]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for v in violations:
        d = out.setdefault(v.check, {"error": 0, "warning": 0})
        d[v.severity] += 1
    return out


def baseline_key_counts(violations: list[Violation]) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in violations:
        key = f"{v.check}\t{v.path}"
        out[key] = out.get(key, 0) + 1
    return out


def cmd_baseline(violations: list[Violation]) -> int:
    data = baseline_key_counts(violations)
    BASELINE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote baseline with {len(data)} (check,file) entries / {len(violations)} violations to {BASELINE_PATH.relative_to(ROOT)}")
    return 0


def cmd_ratchet(violations: list[Violation]) -> int:
    if not BASELINE_PATH.exists():
        print("No baseline.json — run with --baseline first", file=sys.stderr)
        return 2
    base = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    cur = baseline_key_counts(violations)
    regressions = []
    for key, count in sorted(cur.items()):
        if count > base.get(key, 0):
            check, path = key.split("\t", 1)
            regressions.append(f"{path}: {check} +{count - base.get(key, 0)} (now {count}, baseline {base.get(key, 0)})")
    if regressions:
        print("=== New quality regressions above baseline ===", file=sys.stderr)
        for r in regressions:
            print(r, file=sys.stderr)
        print(f"\nFAILED: {len(regressions)} (check,file) regression(s)", file=sys.stderr)
        return 1
    print("OK: no new violations above baseline")
    return 0


def cmd_summary(violations: list[Violation]) -> int:
    counts = counts_by_check(violations)
    files = len(collect_files())
    print(f"Scanned {files} .fos files (excluding {', '.join(sorted(GENERATED))})\n")
    print(f"{'check':28s} {'error':>7s} {'warning':>8s}")
    print("-" * 46)
    terr = twarn = 0
    for check in sorted(counts):
        e = counts[check]["error"]
        w = counts[check]["warning"]
        terr += e
        twarn += w
        print(f"{check:28s} {e:7d} {w:8d}")
    print("-" * 46)
    print(f"{'TOTAL':28s} {terr:7d} {twarn:8d}")
    return 1 if terr > 0 else 0


def report(violations: list[Violation]) -> int:
    errors = [v for v in violations if v.severity == SEVERITY_ERROR]
    warnings = [v for v in violations if v.severity == SEVERITY_WARNING]
    if errors:
        print("=== ERRORS ===", file=sys.stderr)
        for v in sorted(errors, key=lambda x: (x.path, x.line)):
            print(f"{v.path}:{v.line}: [{v.check}] {v.message}", file=sys.stderr)
        print(file=sys.stderr)
    if warnings:
        print("=== WARNINGS ===", file=sys.stderr)
        for v in sorted(warnings, key=lambda x: (x.check, x.path, x.line)):
            print(f"{v.path}:{v.line}: [{v.check}] {v.message}", file=sys.stderr)
        print(file=sys.stderr)
    print(f"{'FAILED' if errors else 'OK'}: {len(errors)} error(s), {len(warnings)} warning(s)",
          file=sys.stderr)
    return 1 if errors else 0


# --------------------------------------------------------------------------
# Autofix (safe checks only): trailing-blank-line, banner-tags,
# component-null-probe.
# --------------------------------------------------------------------------

def fix_file(path: Path, components: set[str]) -> int:
    """Apply safe autofixes in place. Returns number of fixes applied."""
    raw = path.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    fixes = 0

    # banner-tags: drop matching header comment lines (first 40 lines).
    # Only drop banner lines outside comments? They are comments by definition;
    # rebuild the comment mask to avoid deleting a line that merely contains the
    # text inside a string literal.
    kinds_banner = classify(text)
    comment_mask = mask_to(text, kinds_banner, "LB").split("\n")
    lines = text.split("\n")
    new_lines = []
    for idx, ln in enumerate(lines):
        masked = comment_mask[idx] if idx < len(comment_mask) else ""
        if BANNER_AUTHOR_RE.match(masked) or BANNER_VER_RE.match(masked):
            fixes += 1
            continue
        new_lines.append(ln)
    text = "\n".join(new_lines)

    # component-null-probe: `.Comp == null` -> `!x`?  Not a pure textual swap
    # (needs the receiver), so we only rewrite the canonical `recv.Comp == null`
    # / `recv.Comp != null` forms into `!recv.HasComp` / `recv.HasComp`.
    if components:
        alt = "|".join(sorted(re.escape(c) for c in components))
        probe_re = re.compile(r"([A-Za-z_][\w.]*)\.(" + alt + r")[ \t]*(==|!=)[ \t]*null\b")

        def repl(m: re.Match) -> str:
            nonlocal fixes
            fixes += 1
            recv, comp, op = m.group(1), m.group(2), m.group(3)
            return (f"!{recv}.Has{comp}" if op == "==" else f"{recv}.Has{comp}")

        # Only rewrite in code regions: rebuild kinds and apply per-match guarded by mask.
        kinds = classify(text)
        code = mask_to(text, kinds, "c")
        # Find matches in code mask, then splice into original text by offset.
        result = []
        last = 0
        for m in probe_re.finditer(code):
            result.append(text[last:m.start()])
            result.append(repl(m))
            last = m.end()
        result.append(text[last:])
        text = "".join(result)

    # trailing-blank-line: normalize EOF to exactly one terminator.
    body = text.rstrip("\n")
    text = body + "\n"

    new_raw = text.replace("\n", eol.decode("ascii")).encode("utf-8")
    if new_raw != raw:
        path.write_bytes(new_raw)
    return fixes


def cmd_fix() -> int:
    files = collect_files()
    all_text = []
    for f in files:
        raw = f.read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        all_text.append(mask_to(text, classify(text), "c"))
    components = derive_component_names("\n".join(all_text))
    total = 0
    touched = 0
    for f in files:
        before = f.read_bytes()
        fixes = fix_file(f, components)
        after = f.read_bytes()
        if after != before:
            touched += 1
            total += fixes
    print(f"Applied autofixes to {touched} file(s) ({total} edit(s))")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="TLA AngelScript quality validators")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--summary", action="store_true", help="print per-check counts only")
    g.add_argument("--baseline", action="store_true", help="snapshot current violations to baseline.json")
    g.add_argument("--ratchet", action="store_true", help="fail only on violations above baseline")
    g.add_argument("--fix", action="store_true", help="apply safe autofixes in place")
    args = ap.parse_args()

    if args.fix:
        return cmd_fix()

    violations = analyze()
    if args.summary:
        return cmd_summary(violations)
    if args.baseline:
        return cmd_baseline(violations)
    if args.ratchet:
        return cmd_ratchet(violations)
    return report(violations)


if __name__ == "__main__":
    sys.exit(main())
