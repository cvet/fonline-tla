#!/usr/bin/env python3
"""Strip dead defensive null guards in ///@ ExportMethod declarations.

Author intent is the source of truth for FO_NULLABLE placement — the
analyzer does NOT add or remove FO_NULLABLE markers (the heuristic for
inferring "this param can be null" from body shape is too unreliable and
causes churn against curated code). Its only job is to delete `if (param
== nullptr) throw ...;` guards on entity-pointer params that are NOT
marked FO_NULLABLE, since codegen now emits
`NativeDataProvider::CheckArgNotNull` for those before the body runs and
the guard is dead.

Idempotent: re-applies on a file with existing guards correctly cleaned
as a no-op.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = ROOT / "Engine" / "Source" / "Scripting"
ENGINE_SOURCE_DIR = ROOT / "Engine" / "Source"
SOURCE_EXT_DIR = ROOT / "SourceExt"


def _discover_validated_pointer_types() -> frozenset[str]:
    """Build the set of C++ type names that codegen emits runtime null checks for.

    Mirrors `is_validated_pointer_meta_type` in `Engine/BuildTools/codegen.py`:
    every game entity (server + client class names plus the relatives
    Abstract/Proto/Static when the entity declares them), the generic Entity
    bases, and every `///@ ExportRefType` class.
    """
    types: set[str] = {"Entity", "ServerEntity", "ClientEntity", "ScriptSelfEntity"}

    export_entity_re = re.compile(r"///@\s*ExportEntity\s+(.+)")
    for path in ENGINE_SOURCE_DIR.rglob("*.h"):
        try:
            for m in export_entity_re.finditer(path.read_text(encoding="utf-8")):
                tokens = m.group(1).split()
                if len(tokens) < 3:
                    continue
                entity_name = tokens[0]
                server_class = tokens[1]
                client_class = tokens[2]
                flags = tokens[3:]
                types.add(server_class)
                types.add(client_class)
                if "HasAbstract" in flags:
                    types.add("Abstract" + entity_name)
                if "HasProtos" in flags:
                    types.add("Proto" + entity_name)
                if "HasStatics" in flags:
                    types.add("Static" + entity_name)
        except UnicodeDecodeError:
            continue

    export_ref_re = re.compile(r"///@\s*ExportRefType\b[^\n]*\n(?:\s*//[^\n]*\n)*\s*class\s+(\w+)")
    for path in ENGINE_SOURCE_DIR.rglob("*.h"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in export_ref_re.finditer(text):
            types.add(m.group(1))

    return frozenset(types)


ENGINE_ENTITY_TYPES = _discover_validated_pointer_types()

# Match `///@ ExportMethod\n[optional flags line]\nFO_SCRIPT_API <ret> <Name>(<args>)\s*{`
# We must capture the full body to inspect it. Use a stateful parser instead
# of a single regex.

EXPORT_RE = re.compile(
    r"///@\s*ExportMethod[^\n]*\n"
    r"FO_SCRIPT_API\s+"
    r"(?P<ret>(?:FO_NULLABLE\s+)?[A-Za-z_][\w:]*\s*\*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*\("
    r"(?P<args>[^)]*)"
    r"\)\s*\n\{"
)


def find_matching_brace(text: str, open_pos: int) -> int:
    depth = 0
    i = open_pos
    n = len(text)
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line_comment:
            if c == "\n":
                in_line_comment = False
        elif in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
        elif in_char:
            if c == "\\":
                i += 2
                continue
            if c == "'":
                in_char = False
        elif c == "/" and nxt == "/":
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
                return i
        i += 1
    return -1


def split_top_level_commas(text: str) -> list[str]:
    pieces: list[str] = []
    depth_paren = 0
    depth_angle = 0
    cur = []
    for c in text:
        if c == "(":
            depth_paren += 1
            cur.append(c)
        elif c == ")":
            depth_paren -= 1
            cur.append(c)
        elif c == "<":
            depth_angle += 1
            cur.append(c)
        elif c == ">":
            depth_angle -= 1
            cur.append(c)
        elif c == "," and depth_paren == 0 and depth_angle == 0:
            pieces.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    if cur:
        pieces.append("".join(cur).strip())
    return pieces


def parse_arg(arg_text: str) -> tuple[bool, str, str, str]:
    """Return (is_pointer, type_part, name, current_marker)."""
    has_marker = False
    a = arg_text.strip()
    if a.startswith("FO_NULLABLE"):
        has_marker = True
        a = a[len("FO_NULLABLE"):].lstrip()
    # type is everything up to the last identifier
    sep = a.rfind(" ")
    if sep < 0:
        return False, a, "", ""
    type_part = a[:sep].rstrip()
    name = a[sep + 1:].strip()
    is_pointer = type_part.rstrip().endswith("*")
    return is_pointer, type_part, name, "FO_NULLABLE" if has_marker else ""


def body_has_return_nullptr(body: str) -> bool:
    return bool(re.search(r"\breturn\s+nullptr\s*;", body))


# Heuristics for "this expression can return null". Names that, by engine
# convention, denote nullable lookup/find operations.
NULLABLE_CALL_NAMES = {
    "GetMap", "GetCritter", "GetItem", "GetPlayer", "GetLocation", "GetEntity",
    "FindMap", "FindCritter", "FindItem", "FindPlayer", "FindLocation",
    "GetItemFromCritter", "GetItemFromAllSlots", "GetHand1Item", "GetHand2Item",
    "GetPlayerByUserId", "GetPlayerByUserName", "GetCritterByPid",
    "GetMovingContext", "GetCachedCritterContext", "GetActiveItem",
    "GetWeapon", "GetAmmo", "GetCurrentControl", "GetCurChosenScroll",
    "GetActiveScreen", "GetActiveItem", "GetTopWindow",
}

RETURN_ANYTHING_RE = re.compile(r"\breturn\s+([^;]+);")
NULLABLE_CALL_PATTERNS = [
    re.compile(r"\b(?:Get|Find)[A-Z]\w*\s*\("),  # Get*/Find* family
]


def body_returns_nullable_value(body: str) -> bool:
    """Detect bodies that return values that are likely nullable, beyond the
    obvious `return nullptr;` literal."""
    if body_has_return_nullptr(body):
        return True
    for m in RETURN_ANYTHING_RE.finditer(body):
        expr = m.group(1).strip()
        # Strip enclosing parens
        while expr.startswith("(") and expr.endswith(")"):
            expr = expr[1:-1].strip()
        # Check if the returned expression contains a known nullable-returning call
        for pat in NULLABLE_CALL_PATTERNS:
            if pat.search(expr):
                # Exclude calls that obviously can't be null:
                # `static_cast<X>(...)`, `new X(...)`, address-of `&...`
                if expr.startswith("new ") or expr.startswith("&"):
                    continue
                return True
        # Direct call to a known nullable name like `GetPlayer()`
        for name in NULLABLE_CALL_NAMES:
            if re.search(rf"\b{re.escape(name)}\s*\(", expr):
                if expr.startswith("new ") or expr.startswith("&"):
                    continue
                return True
    return False


def body_has_defensive_throw_for_param(body: str, pname: str) -> bool:
    """True if body has `if (pname == nullptr) throw ...;` (non-null contract
    documented via a defensive guard)."""
    if re.search(
        rf"\bif\s*\(\s*{re.escape(pname)}\s*==\s*nullptr\s*\)\s*\{{[^}}]*\bthrow\b[^}}]*\}}",
        body,
    ):
        return True
    if re.search(
        rf"\bif\s*\(\s*!\s*{re.escape(pname)}\s*\)\s*\{{[^}}]*\bthrow\b[^}}]*\}}",
        body,
    ):
        return True
    return False


def find_matching_brace_in_str(text: str, open_pos: int) -> int:
    return find_matching_brace(text, open_pos)


def strip_param_null_guards(body: str, non_nullable_params: list[str]) -> str:
    """Remove defensive `if (param == nullptr) { ... }` blocks for parameters
    that are non-nullable (codegen-emitted CheckArgNotNull already throws
    before the body runs)."""
    text = body
    for pname in non_nullable_params:
        # Match `if (pname == nullptr) {`
        pat = re.compile(rf"^([ \t]*)if\s*\(\s*{re.escape(pname)}\s*==\s*nullptr\s*\)\s*\{{", re.MULTILINE)
        while True:
            m = pat.search(text)
            if not m:
                break
            brace_open = m.end() - 1
            brace_close = find_matching_brace(text, brace_open)
            if brace_close < 0:
                break
            line_start = m.start()
            e = brace_close + 1
            # Consume trailing whitespace and one newline
            while e < len(text) and text[e] in " \t":
                e += 1
            if e < len(text) and text[e] == "\n":
                e += 1
            # Also consume one trailing blank line if present
            blank_start = e
            while e < len(text) and text[e] in " \t":
                e += 1
            if e < len(text) and text[e] == "\n":
                e += 1
            else:
                e = blank_start
            text = text[:line_start] + text[e:]
        # Match `!pname` form too: `if (!pname) { throw ... }`
        pat2 = re.compile(rf"^([ \t]*)if\s*\(\s*!\s*{re.escape(pname)}\s*\)\s*\{{", re.MULTILINE)
        while True:
            m = pat2.search(text)
            if not m:
                break
            brace_open = m.end() - 1
            brace_close = find_matching_brace(text, brace_open)
            if brace_close < 0:
                break
            block = text[brace_open + 1:brace_close]
            if "throw" not in block:
                # Not a defensive guard — leave alone
                break
            line_start = m.start()
            e = brace_close + 1
            while e < len(text) and text[e] in " \t":
                e += 1
            if e < len(text) and text[e] == "\n":
                e += 1
            blank_start = e
            while e < len(text) and text[e] in " \t":
                e += 1
            if e < len(text) and text[e] == "\n":
                e += 1
            else:
                e = blank_start
            text = text[:line_start] + text[e:]
    return text


def body_dereferences_param(body: str, pname: str) -> bool:
    """True if the body directly dereferences pname via `pname->` access
    without checking for null first. If any dereference exists, the function
    implicitly assumes non-null."""
    return bool(re.search(rf"\b{re.escape(pname)}\s*->", body))


def param_should_be_nullable(body: str, pname: str) -> bool:
    """Decide if pname should be marked FO_NULLABLE.

    Rule: mark FO_NULLABLE if the body genuinely allows null:
      - Body has no defensive `if (pname == nullptr) throw ...;` guard
        (otherwise the contract is non-null and the throw documents it).
      - Body doesn't directly dereference pname via `pname->` (which would
        crash on null).

    Examples this catches:
      - `dynamic_cast<X*>(contextItem)` — passes to a null-tolerant cast
      - `someFunc(param)` — passes through without dereferencing
      - `param != nullptr ? ... : ...` — explicit two-branch
      - `if (param != nullptr) { ... }` — explicit null-tolerant branch
    """
    if body_has_defensive_throw_for_param(body, pname):
        return False
    if body_dereferences_param(body, pname):
        return False
    return True


def remove_marker_in_args(args_text: str, want_marker: dict[str, bool]) -> str:
    """Rewrite args text, applying FO_NULLABLE per decisions.

    Preserves original formatting/order: we only mutate the leading marker
    of each piece. Parameters whose name is NOT in `want_marker` are left
    completely as-is — that includes any existing FO_NULLABLE marker.
    Only callers' explicit decisions (entity-pointer args) take effect.
    """
    pieces = split_top_level_commas(args_text)
    if not pieces:
        return args_text
    new_pieces = []
    for piece in pieces:
        stripped = piece.strip()
        leading_ws = piece[:len(piece) - len(piece.lstrip())]
        had = stripped.startswith("FO_NULLABLE")
        body_part = stripped[len("FO_NULLABLE"):].lstrip() if had else stripped
        tokens = body_part.split()
        if len(tokens) < 2:
            new_pieces.append(piece)
            continue
        name = tokens[-1]
        # Drop any default value annotation from the name
        if "=" in body_part:
            name = body_part.split("=", 1)[0].rstrip().split()[-1]
        if name not in want_marker:
            # No decision for this param — leave whatever the author wrote.
            new_pieces.append(piece)
            continue
        target = want_marker[name]
        if target:
            new_pieces.append(leading_ws + "FO_NULLABLE " + body_part)
        else:
            new_pieces.append(leading_ws + body_part)
    # Join with ", " — this collapses multi-line slightly. We try harder:
    # if the original args_text contained newlines, preserve them.
    return ", ".join(new_pieces)


def apply_file(text: str) -> tuple[str, dict[str, int]]:
    counters = {"ret_marked": 0, "param_marked": 0, "ret_unmarked": 0, "param_unmarked": 0, "guards_stripped": 0}
    edits: list[tuple[int, int, str]] = []
    pos = 0
    while True:
        m = EXPORT_RE.search(text, pos)
        if not m:
            break
        # Find body bounds
        brace_open = text.find("{", m.end() - 1)
        if brace_open < 0:
            break
        body_end = find_matching_brace(text, brace_open)
        if body_end < 0:
            break
        body = text[brace_open + 1:body_end]
        # The analyzer ONLY strips dead defensive guards. It does NOT add or
        # remove FO_NULLABLE markers — those are the author's call, and the
        # heuristic for inferring "this param can be null" is unreliable
        # enough that auto-suggestions cause churn (see TransferToMap, Move,
        # ...: the body just forwards `map`, which says nothing about the
        # contract). Existing markers always pass through unchanged.
        ret_raw = m.group("ret").strip()
        new_ret = ret_raw

        args_text = m.group("args")
        new_args = args_text

        # For every ENTITY-pointer arg that is NOT marked FO_NULLABLE, the
        # codegen now emits NativeDataProvider::CheckArgNotNull before the
        # native call. Any defensive `if (param == nullptr) throw ...;`
        # inside the body is therefore dead code — strip it.
        non_nullable_entity_params: list[str] = []
        for arg_index, arg in enumerate(split_top_level_commas(args_text)):
            if arg_index == 0:
                continue  # `self` / engine receiver
            is_ptr, type_part, name, had = parse_arg(arg)
            if not is_ptr or not name:
                continue
            type_clean = type_part.rstrip("*&").strip()
            if type_clean not in ENGINE_ENTITY_TYPES:
                continue
            if had:
                continue  # FO_NULLABLE present — author asked for null tolerance, leave guards alone
            non_nullable_entity_params.append(name)

        new_body = strip_param_null_guards(body, non_nullable_entity_params)
        if new_body != body:
            # Count stripped guards (heuristic: count `if (.* == nullptr)` removed)
            counters["guards_stripped"] += body.count(" == nullptr") - new_body.count(" == nullptr")
            edits.append((brace_open + 1, body_end, new_body))

        # Locate offsets to splice
        # Replace ret span and args span individually.
        ret_start, ret_end = m.start("ret"), m.end("ret")
        args_start, args_end = m.start("args"), m.end("args")
        edits.append((ret_start, ret_end, new_ret))
        edits.append((args_start, args_end, new_args))

        pos = body_end + 1

    # Apply edits in reverse order
    new_text = text
    for start, end, replacement in sorted(edits, key=lambda e: -e[0]):
        if new_text[start:end] != replacement:
            new_text = new_text[:start] + replacement + new_text[end:]
    return new_text, counters


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    check_mode = "--check" in sys.argv
    if check_mode:
        dry_run = True
    files = sorted(ENGINE_DIR.glob("*ScriptMethods.cpp"))
    if SOURCE_EXT_DIR.is_dir():
        files += sorted(p for p in SOURCE_EXT_DIR.glob("*.cpp") if "ExportMethod" in p.read_text(encoding="utf-8", errors="ignore"))
    grand_total = {"ret_marked": 0, "param_marked": 0, "ret_unmarked": 0, "param_unmarked": 0, "guards_stripped": 0}
    changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        new_text, counters = apply_file(text)
        for k, v in counters.items():
            grand_total[k] += v
        if new_text != text:
            changed += 1
            if not dry_run:
                f.write_text(new_text, encoding="utf-8")
            print(f"{f.relative_to(ROOT)}: ret_marked={counters['ret_marked']} param_marked={counters['param_marked']}")
    print()
    print(f"Files changed: {changed}")
    print(f"Returns marked FO_NULLABLE: {grand_total['ret_marked']}")
    print(f"Params marked FO_NULLABLE: {grand_total['param_marked']}")
    print(f"Dead null-guards stripped: {grand_total['guards_stripped']}")
    if dry_run:
        print("(dry-run - no files written)")
    if check_mode and changed > 0:
        print("ERROR: native FO_NULLABLE markers out of date; run `python Tools/NullableEstimate/apply_native_nullable.py` and commit the result", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
