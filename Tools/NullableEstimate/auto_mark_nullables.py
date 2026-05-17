#!/usr/bin/env python3
"""Apply `?` suffix to .fos params/returns flagged by estimate_nullables.py.

Inclusive auto-marker: for every parameter where the body has a `!= null` /
`== null` check (and is NOT covered by an early Assert(param != null)), and
for every return where the body has `return null;`, add a trailing `?` to
the type token in the function head.

Idempotent: skips spots that already have `?` or legacy `[[Nullable]]`.

This is an opinionated first pass. Per Nullability.md the curated final
state may remove markers where the convention says "caller must not pass
null" — those edits are the author's, run after this pass.

Skips: Scripts/GuiScreens.fos (generated), Scripts/Content.fos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from estimate_nullables import (
    FUNC_RE,
    PRIMITIVE_TYPES,
    extract_body,
    is_nullable_param,
    is_nullable_return,
    split_args,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "Scripts"


def add_marker_to_param(args_text: str, pname: str) -> tuple[str, bool]:
    """Add `?` suffix to the type token of parameter `pname` in args_text."""
    pieces = args_text.split(",")
    out = []
    changed = False
    for piece in pieces:
        raw = piece
        stripped = piece.strip()
        if not stripped:
            out.append(raw)
            continue
        # Strip default value for parsing
        if "=" in stripped:
            decl, _, default = stripped.partition("=")
            decl = decl.rstrip()
            suffix = "=" + default
        else:
            decl = stripped
            suffix = ""
        tokens = decl.split()
        if len(tokens) < 2:
            out.append(raw)
            continue
        # Extract trailing name (may have & prefix)
        last = tokens[-1].lstrip("&")
        if last != pname:
            out.append(raw)
            continue
        # Combine all type tokens
        type_part = " ".join(tokens[:-1])
        # Skip primitives
        tp_base = re.sub(r"\[\]\??$", "", type_part).strip()
        tp_base = re.sub(r"^(const|inout|in|out)\s+", "", tp_base).strip()
        tp_base = re.sub(r"\?+$", "", tp_base).strip()
        if tp_base in PRIMITIVE_TYPES:
            out.append(raw)
            continue
        # Skip if already nullable
        if type_part.rstrip().endswith("?"):
            out.append(raw)
            continue
        # Skip arrays — `Type[]?` is valid but estimator doesn't separate
        # array element vs handle nullability; leave to author.
        if type_part.rstrip().endswith("[]"):
            out.append(raw)
            continue
        # Skip generic/template types — engine preprocessor's StripNullableTypeSuffix
        # only strips `?` after IDENTIFIER or `]`, not after `>`.
        if type_part.rstrip().endswith(">"):
            out.append(raw)
            continue
        # Skip [[Nullable]] legacy
        if "[[Nullable]]" in type_part or "[[ Nullable ]]" in type_part:
            out.append(raw)
            continue
        # Rebuild with `?`
        new_decl = type_part + "? " + tokens[-1] + (" " + suffix if suffix else "")
        # Preserve leading whitespace of original piece
        leading_ws = raw[:len(raw) - len(raw.lstrip())]
        trailing_ws = raw[len(raw.rstrip()):]
        new_piece = leading_ws + new_decl.strip() + trailing_ws
        out.append(new_piece)
        changed = True
    return ",".join(out), changed


def add_return_marker(head: str, ret_type: str) -> tuple[str, bool]:
    """Add `?` to the return type in a function head string."""
    # Skip if already nullable or primitive
    if ret_type in PRIMITIVE_TYPES or ret_type == "void":
        return head, False
    if "?" in ret_type:
        return head, False
    # Replace first standalone occurrence of ret_type token (before func name)
    # Function head looks like: [[Attr]] ReturnType[]? FuncName(...
    # We want to replace ReturnType -> ReturnType?
    # Use a regex matching the ret_type as a whole word
    pattern = re.compile(r"\b" + re.escape(ret_type) + r"\b(\[\])?")
    m = pattern.search(head)
    if not m:
        return head, False
    array_suffix = m.group(1) or ""
    replacement = ret_type + array_suffix + "?"
    new_head = head[:m.start()] + replacement + head[m.end():]
    return new_head, True


def process_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    original = text
    marks_param = 0
    marks_ret = 0
    # Collect all matches first (positions will shift as we edit)
    matches = []
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
        matches.append((m.start(), m.end(), m.group(), m.group("args"), m.group("ret"), body))
    # Apply edits from end to start so offsets stay valid
    new_text = text
    for start, end, head, args_text, ret_type, body in reversed(matches):
        ret_clean = ret_type.rstrip("[]").rstrip("&").strip()
        ret_clean = re.sub(r"^(const)\s+", "", ret_clean)
        # Edit params
        args_split = split_args(args_text)
        needs_params = []
        for tp, pname in args_split:
            tp_c = re.sub(r"\[\]$", "", tp).strip()
            tp_c = re.sub(r"^(const|inout|in|out)\s+", "", tp_c).strip()
            if tp_c in PRIMITIVE_TYPES:
                continue
            if is_nullable_param(body, pname):
                needs_params.append(pname)
        needs_return = is_nullable_return(body, ret_clean)
        if not needs_params and not needs_return:
            continue
        new_args = args_text
        param_changed = False
        for pname in needs_params:
            new_args, ch = add_marker_to_param(new_args, pname)
            if ch:
                param_changed = True
                marks_param += 1
        new_head = head.replace(args_text, new_args, 1) if param_changed else head
        if needs_return:
            new_head, ch = add_return_marker(new_head, ret_clean)
            if ch:
                marks_ret += 1
        if new_head != head:
            new_text = new_text[:start] + new_head + new_text[end:]
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return marks_param, marks_ret


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    files = [f for f in files if f.name not in ("GuiScreens.fos", "Content.fos")]
    total_p = 0
    total_r = 0
    files_changed = 0
    for f in files:
        if dry_run:
            # Re-implement dry-run by copying logic but not writing
            saved = f.read_text(encoding="utf-8")
            p, r = process_file(f)
            if p or r:
                files_changed += 1
                print(f"{f.relative_to(ROOT)}: +{p} param, +{r} return")
                # Restore
                f.write_text(saved, encoding="utf-8")
            total_p += p
            total_r += r
        else:
            p, r = process_file(f)
            if p or r:
                files_changed += 1
                print(f"{f.relative_to(ROOT)}: +{p} param, +{r} return")
            total_p += p
            total_r += r
    print()
    print(f"Files changed: {files_changed}")
    print(f"Parameters marked: {total_p}")
    print(f"Returns marked: {total_r}")
    if dry_run:
        print("(dry-run - changes were rolled back)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
