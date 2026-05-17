#!/usr/bin/env python3
"""Estimate how many [[Nullable]] markers would be added across all .fos scripts.

Rule (conservative, body-driven):
- Parameter is nullable if function body contains "paramName == null" or "paramName != null".
- Return is nullable if function body contains "return null;".
- Skips parameters whose first body line is an Assert(paramName != null) without later null checks.

This is a heuristic estimate, not a precise compiler analysis. AngelScript's
.fos files have a single-namespace-per-file convention with no #include,
#if SERVER/CLIENT/MAPPER blocks, and conventional function declarations.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

SCRIPTS_ROOT = Path(__file__).resolve().parents[2] / "Scripts"

# Engine entity-like types we care about (others can also be nullable but
# these are the dominant ones in practice).
NULLABLE_TYPES = {
    "Critter", "Player", "Item", "StaticItem", "Map", "Location",
    "Entity", "GenericEntity", "MapSprite", "InvocationContext",
    "DialogContext", "MapPart", "ScreenItem", "Animation", "AnyMap",
    "GuiPart", "UiPart", "GroupEntity", "AccountInfo",
    # Any pascal-case Type starting with capital that is not a primitive
}

PRIMITIVE_TYPES = {
    "void", "bool", "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64",
    "float", "float32", "float64", "double",
    "string", "hstring", "ident", "tick", "duration", "time",
    "mpos", "ipos", "mdir", "any",
}

# Match a function declaration like:
#   ReturnType Name(...) {       (definition with body)
#   namespace::ReturnType Name(...) {
#   [[Attr]] ReturnType Name(...) {
# We grab definitions only (with body), per-file.
FUNC_RE = re.compile(
    r"""^                                       # start of line
        (?P<indent>[ \t]*)                      # leading whitespace
        (?P<head>(?:\[\[[^\]]+\]\]\s*)*         # optional [[Attr]]
                  (?P<ret>[A-Za-z_][\w:]*(?:\[\])?(?:\s*&)?)\s+  # return type
                  (?P<name>[A-Za-z_]\w*)\s*    # function name
                  \(                             # open paren
                  (?P<args>[^)]*)\s*\)           # args, no nested parens
                  [^{\n;]*\s*\{                  # any post-modifier then {
        )
    """,
    re.VERBOSE | re.MULTILINE,
)

ASSERT_RE = re.compile(r"^\s*Assert\(\s*(\w+)\s*!=\s*null\s*\)\s*;", re.MULTILINE)


def split_args(args: str) -> List[Tuple[str, str]]:
    """Split a parameter list into [(type, name), ...] tuples.

    Returns empty list for empty args. Skips primitive types.
    """
    args = args.strip()
    if not args:
        return []
    pieces = [p.strip() for p in args.split(",")]
    result = []
    for piece in pieces:
        # remove default value if present (e.g. `Critter cr = null`)
        if "=" in piece:
            piece = piece.split("=", 1)[0].strip()
        # remove [[Nullable]] prefix if already present
        piece = re.sub(r"^\[\[\s*Nullable\s*\]\]\s*", "", piece)
        # piece is now like: "Critter cr" or "const Map& m" or "Critter[] crs"
        # Extract trailing identifier as name, rest as type.
        tokens = piece.split()
        if len(tokens) < 2:
            continue
        name = tokens[-1].lstrip("&")
        type_part = " ".join(tokens[:-1]).rstrip("&").strip()
        result.append((type_part, name))
    return result


def extract_body(content: str, brace_pos: int) -> str:
    """Extract balanced { ... } body starting from brace_pos (which points at the '{')."""
    depth = 0
    end = brace_pos
    i = brace_pos
    n = len(content)
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    while i < n:
        c = content[i]
        nxt = content[i + 1] if i + 1 < n else ""
        if in_line_comment:
            if c == "\n":
                in_line_comment = False
        elif in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            if c == "\\":
                i += 1
            elif c == '"':
                in_string = False
        elif in_char:
            if c == "\\":
                i += 1
            elif c == "'":
                in_char = False
        else:
            if c == "/" and nxt == "/":
                in_line_comment = True
                i += 1
            elif c == "/" and nxt == "*":
                in_block_comment = True
                i += 1
            elif c == '"':
                in_string = True
            elif c == "'":
                in_char = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        i += 1
    return content[brace_pos + 1:end]


def is_nullable_param(body: str, name: str) -> bool:
    eq_pat = re.compile(rf"\b{re.escape(name)}\s*==\s*null\b")
    ne_pat = re.compile(rf"\b{re.escape(name)}\s*!=\s*null\b")
    has_check = bool(eq_pat.search(body) or ne_pat.search(body))
    if not has_check:
        return False
    # If the function asserts non-null first, treat as contract non-null
    # unless subsequent checks still occur.
    for am in ASSERT_RE.finditer(body):
        if am.group(1) == name:
            # Find checks after the assert
            tail = body[am.end():]
            if eq_pat.search(tail) or ne_pat.search(tail):
                return True
            return False
    return True


def is_nullable_return(body: str, ret_type: str) -> bool:
    if ret_type in PRIMITIVE_TYPES:
        return False
    if ret_type == "void":
        return False
    # "return null;" or "return null;" with whitespace
    return bool(re.search(r"\breturn\s+null\s*;", body))


def analyze_file(path: Path) -> Tuple[int, int, int]:
    """Return (param_markers, return_markers, function_count) for the file."""
    text = path.read_text(encoding="utf-8", errors="replace")
    param_marks = 0
    return_marks = 0
    func_count = 0
    pos = 0
    while True:
        m = FUNC_RE.search(text, pos)
        if not m:
            break
        # Find the actual '{' position
        brace_pos = text.find("{", m.end() - 1)
        if brace_pos == -1:
            break
        body = extract_body(text, brace_pos)
        # Move past this body
        pos = brace_pos + len(body) + 2

        # Skip control-flow keywords masquerading as functions
        if m.group("name") in {"if", "for", "while", "switch", "do", "namespace", "class", "enum", "case", "return"}:
            continue
        # Skip likely-noise where return type is also a keyword
        if m.group("ret") in {"if", "for", "while", "switch", "namespace", "class", "enum", "else", "return"}:
            continue

        func_count += 1
        args = split_args(m.group("args"))
        for type_part, name in args:
            # Strip [] suffix and const/inout for type test
            tp = re.sub(r"\[\]$", "", type_part).strip()
            tp = re.sub(r"^(const|inout|in|out)\s+", "", tp).strip()
            if tp in PRIMITIVE_TYPES:
                continue
            if is_nullable_param(body, name):
                param_marks += 1
        ret_type = m.group("ret").rstrip("[]").rstrip("&").strip()
        ret_type = re.sub(r"^(const)\s+", "", ret_type)
        if is_nullable_return(body, ret_type):
            return_marks += 1
    return param_marks, return_marks, func_count


def main() -> int:
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    total_param = 0
    total_ret = 0
    total_funcs = 0
    per_file = []
    for f in files:
        try:
            p, r, fc = analyze_file(f)
        except Exception as e:
            print(f"# error analyzing {f}: {e}", file=sys.stderr)
            continue
        total_param += p
        total_ret += r
        total_funcs += fc
        if p + r > 0:
            per_file.append((f, p, r, fc))

    per_file.sort(key=lambda t: -(t[1] + t[2]))
    print(f"Total .fos files analyzed: {len(files)}")
    print(f"Total functions found: {total_funcs}")
    print(f"Total nullable PARAMETER markers needed: {total_param}")
    print(f"Total nullable RETURN markers needed: {total_ret}")
    print(f"Total [[Nullable]] markers: {total_param + total_ret}")
    print()
    print("Top 30 files by marker count:")
    for f, p, r, fc in per_file[:30]:
        rel = f.relative_to(SCRIPTS_ROOT.parent)
        print(f"  {p+r:4d}  ({p} param + {r} ret) of {fc} funcs  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
