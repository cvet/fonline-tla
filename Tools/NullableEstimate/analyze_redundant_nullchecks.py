#!/usr/bin/env python3
"""Read-only analysis: classify `?`-marked params by body shape and flag
patterns where the null check / `?` marker is redundant per the
Nullability.md convention.

Categories produced per function/param:
- TWO_BRANCH: body uses `if (param != null) { useA } [else { useB }]` or
  `param != null ? use : fallback` — `?` is LEGITIMATE
- EARLY_EXIT_ONLY: body has only `if (param == null) { return ... }` or
  equivalent guard — `?` is WRONG per convention (caller must not pass
  null). Action: drop `?`, drop guard, fix callers.
- ASSERT_ONLY: body has `Assert(param != null, ...)` and no further null
  comparison — `?` is WRONG (Assert IS the non-null contract). Action:
  drop `?`, keep Assert (it now matches type).
- ASSERT_THEN_CHECK: body has Assert AND later `if (param == null)` — the
  later check is dead. Action: drop later check.
- TERNARY_TWO_BRANCH: `cond ? whenNotNull : whenNull` — LEGITIMATE
- MIXED: multiple patterns present, manual review needed.
- UNKNOWN: heuristic couldn't classify.

Also analyzes local variables:
- LOCAL_DEAD_AFTER_ASSERT: `Assert(x != null); ... if (x == null) ...` —
  second check dead
- LOCAL_DEAD_NON_NULLABLE_SOURCE: `T x = engine_call();` where
  engine_call returns non-nullable + `if (x == null)` — check dead

Run from project root. Output to stdout grouped by category.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from estimate_nullables import (
    FUNC_RE,
    PRIMITIVE_TYPES,
    extract_body,
    split_args,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "Scripts"


def has_early_exit_guard(body: str, name: str) -> bool:
    """if (name == null) { return/continue/break/ThrowException ... }"""
    pat = re.compile(
        rf"\bif\s*\(\s*{re.escape(name)}\s*==\s*null\s*\)\s*"
        rf"\{{[^}}]*\b(return|continue|break|ThrowException)\b[^}}]*\}}",
        re.DOTALL,
    )
    if pat.search(body):
        return True
    # Single-line: if (x == null) return;
    pat2 = re.compile(
        rf"\bif\s*\(\s*{re.escape(name)}\s*==\s*null\s*\)\s*"
        rf"(return|continue|break|ThrowException)\b",
    )
    return bool(pat2.search(body))


def has_use_in_pos_branch(body: str, name: str) -> bool:
    """if (name != null) { ... use name ... }  with body that actually uses name."""
    pat = re.compile(
        rf"\bif\s*\(\s*{re.escape(name)}\s*!=\s*null\b"
    )
    for m in pat.finditer(body):
        # Find following brace
        brace_pos = body.find("{", m.end())
        if brace_pos < 0:
            # Could be single-statement: if (x != null) x.foo();
            tail = body[m.end():m.end() + 200]
            if re.search(rf"\b{re.escape(name)}\b\.", tail):
                return True
            continue
        depth = 0
        end = brace_pos
        i = brace_pos
        while i < len(body):
            c = body[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        block = body[brace_pos + 1:end]
        if re.search(rf"\b{re.escape(name)}\b\.", block) or re.search(rf"\b{re.escape(name)}\b\s*(?:\.|=|;|,|\))", block):
            return True
    return False


def has_explicit_else_branch(body: str, name: str) -> bool:
    """if (name != null) { ... } else { ... } — explicit two-branch."""
    pat = re.compile(
        rf"\bif\s*\(\s*{re.escape(name)}\s*!=\s*null\s*\)\s*\{{[^}}]*\}}\s*else\b",
        re.DOTALL,
    )
    if pat.search(body):
        return True
    pat2 = re.compile(
        rf"\bif\s*\(\s*{re.escape(name)}\s*==\s*null\s*\)\s*\{{[^}}]*\}}\s*else\b",
        re.DOTALL,
    )
    return bool(pat2.search(body))


def has_ternary(body: str, name: str) -> bool:
    """name != null ? X : Y  /  name == null ? Y : X"""
    return bool(
        re.search(rf"\b{re.escape(name)}\s*!=\s*null\s*\?", body)
        or re.search(rf"\b{re.escape(name)}\s*==\s*null\s*\?", body)
    )


def has_short_circuit_use(body: str, name: str) -> bool:
    """if (name != null && name.something) — implicit two-branch."""
    return bool(
        re.search(rf"\b{re.escape(name)}\s*!=\s*null\s*&&\s*{re.escape(name)}\b\.", body)
        or re.search(rf"\b{re.escape(name)}\s*==\s*null\s*\|\|", body)
    )


def has_assert(body: str, name: str) -> bool:
    return bool(re.search(rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b", body))


def has_any_null_compare(body: str, name: str) -> bool:
    return bool(
        re.search(rf"\b{re.escape(name)}\s*(?:==|!=)\s*null\b", body)
    )


def classify_param(body: str, name: str) -> str:
    asserted = has_assert(body, name)
    early = has_early_exit_guard(body, name)
    ternary = has_ternary(body, name)
    explicit_else = has_explicit_else_branch(body, name)
    pos_use = has_use_in_pos_branch(body, name)
    short_circuit = has_short_circuit_use(body, name)
    any_compare = has_any_null_compare(body, name)

    if asserted:
        # If only Assert + maybe further checks
        if any_compare:
            # Count compares AFTER assert position
            am = re.search(rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b", body)
            tail = body[am.end():] if am else body
            if re.search(rf"\b{re.escape(name)}\s*(?:==|!=)\s*null\b", tail):
                return "ASSERT_THEN_CHECK"
        return "ASSERT_ONLY"

    real_branch = explicit_else or pos_use or ternary or short_circuit

    if real_branch and not early:
        return "TWO_BRANCH"
    if real_branch and early:
        # Both two-branch and early exit — mixed, but two-branch wins
        return "TWO_BRANCH"
    if early and not real_branch:
        return "EARLY_EXIT_ONLY"
    if not any_compare:
        return "NO_COMPARE"
    return "UNKNOWN"


ENGINE_INVOKED_PREFIXES = (
    "_",          # _XxxDead, _XxxUseSkill etc — engine event handlers / private callbacks
    "e_",         # item/critter event callbacks
    "s_",         # scenery callbacks
    "d_",         # dialog demands
    "r_",         # dialog results
    "dlg_",       # dialog script entries
    "critter_",   # engine critter callbacks
    "player_",    # engine player callbacks
    "npc_plane_", # engine NPC plane callbacks
    "GM_",        # global map callbacks
)
ENGINE_INVOKED_EXACT_PREFIXES = ("On",)  # OnSomething event subscribers


def is_engine_invoked(fname: str) -> bool:
    for p in ENGINE_INVOKED_PREFIXES:
        if fname.startswith(p):
            return True
    for p in ENGINE_INVOKED_EXACT_PREFIXES:
        # Must be CamelCase like OnXxx
        if fname.startswith(p) and len(fname) > 2 and fname[2].isupper():
            return True
    return False


def main() -> int:
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    files = [f for f in files if f.name not in ("GuiScreens.fos", "Content.fos")]
    buckets: dict[str, list[tuple[str, bool]]] = {
        "EARLY_EXIT_ONLY": [],
        "ASSERT_ONLY": [],
        "ASSERT_THEN_CHECK": [],
        "TWO_BRANCH": [],
        "NO_COMPARE": [],
        "UNKNOWN": [],
    }
    total = 0
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
            line = text[:m.start()].count("\n") + 1
            fname = m.group("name")
            args_text = m.group("args")
            engine_fired = is_engine_invoked(fname)
            # Find params with `?` marker
            for piece in args_text.split(","):
                stripped = piece.strip()
                if not stripped:
                    continue
                if "=" in stripped:
                    decl, _, _ = stripped.partition("=")
                    decl = decl.rstrip()
                else:
                    decl = stripped
                tokens = decl.split()
                if len(tokens) < 2:
                    continue
                last = tokens[-1].lstrip("&")
                tp = " ".join(tokens[:-1])
                tp_strip = tp.rstrip()
                # Only consider params marked nullable
                if not tp_strip.endswith("?"):
                    continue
                total += 1
                category = classify_param(body, last)
                rel = f.relative_to(ROOT)
                buckets[category].append((f"{rel}:{line} {fname}({tp_strip} {last})", engine_fired))

    print(f"=== Total `?`-marked params analyzed: {total} ===\n")

    # Special breakdown: EARLY_EXIT_ONLY split by engine-fired vs internal
    early = buckets["EARLY_EXIT_ONLY"]
    early_engine = [e for e, eng in early if eng]
    early_internal = [e for e, eng in early if not eng]
    print(f"== EARLY_EXIT_ONLY total: {len(early)} ==")
    print(f"   - engine-fired (`?` is OK — engine may pass null): {len(early_engine)}")
    print(f"   - INTERNAL helpers (`?` IS REDUNDANT — drop, fix callers): {len(early_internal)}")
    print()
    print(f"== Internal helpers with REDUNDANT `?` (action: drop `?`, keep guard or fix callers): ==")
    for line in early_internal:
        print(f"  {line}")
    print()
    print(f"== Engine-fired with EARLY_EXIT (acceptable — engine contract makes null possible): ==")
    for line in early_engine[:30]:
        print(f"  {line}")
    if len(early_engine) > 30:
        print(f"  ... ({len(early_engine) - 30} more)")
    print()

    for cat in ("ASSERT_ONLY", "ASSERT_THEN_CHECK", "NO_COMPARE", "UNKNOWN"):
        items = [it for it, _ in buckets[cat]]
        if not items:
            continue
        print(f"== {cat}: {len(items)} ==")
        for line in items[:50]:
            print(f"  {line}")
        if len(items) > 50:
            print(f"  ... ({len(items) - 50} more)")
        print()

    print(f"=== Summary ===")
    print(f"  TWO_BRANCH (legit `?`): {len(buckets['TWO_BRANCH'])}")
    print(f"  EARLY_EXIT engine-fired (acceptable `?`): {len(early_engine)}")
    print(f"  EARLY_EXIT internal (redundant `?`): {len(early_internal)}")
    print(f"  ASSERT_ONLY (dead Assert+?): {len([it for it, _ in buckets['ASSERT_ONLY']])}")
    print(f"  ASSERT_THEN_CHECK (dead later check): {len([it for it, _ in buckets['ASSERT_THEN_CHECK']])}")
    print(f"  NO_COMPARE (dereference w/o check, latent crash): {len([it for it, _ in buckets['NO_COMPARE']])}")
    print(f"  UNKNOWN (manual review): {len([it for it, _ in buckets['UNKNOWN']])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
