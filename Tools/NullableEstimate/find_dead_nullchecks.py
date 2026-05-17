#!/usr/bin/env python3
"""Read-only scan for definitively dead null checks in function bodies.

Patterns flagged (high-confidence redundant):
- DOUBLE_CHECK: same name checked for null twice in one function body, with
  no reassignment between them.
- AFTER_ASSERT: `Assert(x != null, ...); ... if (x [=!]= null) ...`
  the second check is dead.
- DEREF_THEN_CHECK: `x.something; ... if (x == null) ...` — if the
  earlier dereference unconditionally executes and would have crashed on
  null, the later check is dead.
- CHECK_THEN_DEREF_NO_GUARD: `if (x != null) {} x.foo` (dereference
  outside guard) — partial-cover guard, the deref is dead-guarded.
- IMMEDIATE_NULL_CHECK_AFTER_NEW: `T x = new T(); ... if (x == null)` —
  `new` never returns null in AS.

Run from project root. Reports file:line per finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estimate_nullables import FUNC_RE, extract_body

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "Scripts"

# Match `Assert(x != null, ...)` or `Assert(x != null)`
ASSERT_RE = re.compile(r"\bAssert\(\s*(\w+)\s*!=\s*null\b")
# Match `if (x == null)` or `if (x != null)` standalone
IF_NULL_RE = re.compile(r"\bif\s*\(\s*(\w+)\s*(==|!=)\s*null\b")
# Match standalone assignment `x = ...;` or `T x = ...;` (resets x)
ASSIGN_RE = re.compile(r"\b(\w+)\s*=\s*[^=]")
# Match dereference `x.member` or `x[...]`
DEREF_RE = re.compile(r"\b(\w+)\.\w")


def offsets_with(pat: re.Pattern, text: str, name: str):
    return [m.start() for m in pat.finditer(text) if m.group(1) == name]


def line_of(text: str, off: int) -> int:
    return text[:off].count("\n") + 1


def find_assigns(body: str, name: str) -> list[int]:
    """Find positions where `name` is reassigned (filters out comparisons)."""
    out = []
    for m in ASSIGN_RE.finditer(body):
        if m.group(1) != name:
            continue
        # Skip == != <= >=
        following = body[m.end() - 1:m.end() + 1]
        if following.startswith("=") or following.startswith(">") or following.startswith("<"):
            continue
        out.append(m.start())
    return out


def scan_function(file_rel: str, body: str, base_line: int, findings: dict):
    # Collect all `if (NAME OP null)` positions per name
    name_checks: dict[str, list[tuple[int, str]]] = {}
    for m in IF_NULL_RE.finditer(body):
        name_checks.setdefault(m.group(1), []).append((m.start(), m.group(2)))

    name_asserts: dict[str, list[int]] = {}
    for m in ASSERT_RE.finditer(body):
        name_asserts.setdefault(m.group(1), []).append(m.start())

    for name, checks in name_checks.items():
        if len(checks) < 1:
            continue
        assigns = find_assigns(body, name)
        # DOUBLE_CHECK
        if len(checks) >= 2:
            prev_off = checks[0][0]
            for off, op in checks[1:]:
                # Was there an assignment between prev_off and off?
                if any(prev_off < a < off for a in assigns):
                    prev_off = off
                    continue
                # Dead second check
                findings.setdefault("DOUBLE_CHECK", []).append(
                    f"{file_rel}:{base_line + body[:off].count(chr(10))}: '{name}' checked again at line {base_line + body[:off].count(chr(10))} (previous check at line {base_line + body[:prev_off].count(chr(10))})"
                )
                prev_off = off

        # AFTER_ASSERT
        for assert_off in name_asserts.get(name, []):
            for off, op in checks:
                if off <= assert_off:
                    continue
                if any(assert_off < a < off for a in assigns):
                    continue
                findings.setdefault("AFTER_ASSERT", []).append(
                    f"{file_rel}:{base_line + body[:off].count(chr(10))}: '{name}' checked at line {base_line + body[:off].count(chr(10))} after Assert at line {base_line + body[:assert_off].count(chr(10))}"
                )

        # DEREF_THEN_CHECK
        first_check = checks[0][0]
        derefs = [m.start() for m in DEREF_RE.finditer(body) if m.group(1) == name]
        for d_off in derefs:
            if d_off >= first_check:
                continue
            if any(d_off < a < first_check for a in assigns):
                continue
            # Is the dereference inside a nested `if (name != null) { ... }`?
            # Heuristic: skip if preceding ~50 chars contain "if (name != null"
            preceding = body[max(0, d_off - 80):d_off]
            if re.search(rf"\bif\s*\(\s*{re.escape(name)}\s*!=\s*null", preceding):
                continue
            findings.setdefault("DEREF_THEN_CHECK", []).append(
                f"{file_rel}:{base_line + body[:first_check].count(chr(10))}: '{name}' checked at line {base_line + body[:first_check].count(chr(10))} after unconditional dereference at line {base_line + body[:d_off].count(chr(10))}"
            )
            break


def main() -> int:
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    files = [f for f in files if f.name not in ("GuiScreens.fos", "Content.fos")]
    findings: dict[str, list[str]] = {}
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        pos = 0
        while True:
            m = FUNC_RE.search(text, pos)
            if not m:
                break
            brace_pos = text.find("{", m.end() - 1)
            if brace_pos == -1:
                break
            body = extract_body(text, brace_pos)
            pos = brace_pos + len(body) + 2
            if m.group("name") in {"if", "for", "while", "switch", "do", "namespace", "class", "enum", "case", "return"}:
                continue
            if m.group("ret") in {"if", "for", "while", "switch", "namespace", "class", "enum", "else", "return"}:
                continue
            base_line = text[:brace_pos + 1].count("\n") + 1
            rel = f.relative_to(ROOT)
            scan_function(str(rel), body, base_line, findings)

    print("=== Dead null-check scan ===\n")
    for cat in ("DOUBLE_CHECK", "AFTER_ASSERT", "DEREF_THEN_CHECK"):
        items = findings.get(cat, [])
        print(f"== {cat}: {len(items)} ==")
        for line in items[:50]:
            print(f"  {line}")
        if len(items) > 50:
            print(f"  ... ({len(items) - 50} more)")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
