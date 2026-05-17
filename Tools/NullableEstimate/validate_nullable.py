#!/usr/bin/env python3
"""Validate placement of FO_NULLABLE and `?` nullability markers.

The marker is a contract annotation. It documents "this handle may be null"
to readers and, for the subset of types where codegen knows how to validate
it (entity meta-types), is enforced by `NativeDataProvider::CheckArgNotNull`
/ `CheckReturnNotNull` at the script ↔ native boundary. The validator
catches the two placement mistakes that are always wrong:

Engine side (`Engine/Source/Scripting/*ScriptMethods.cpp`):
  - FO_NULLABLE may only appear inside a function declaration that is
    immediately preceded by `///@ ExportMethod`. Anywhere else the macro
    is silently a no-op (it never reaches codegen).
  - FO_NULLABLE must be adjacent to a pointer type — never a primitive
    or a non-pointer value type. Stick a `?`/FO_NULLABLE on `int`, `bool`,
    `mpos`, etc. and you've made a meaningless declaration.

Script side (`Scripts/**/*.fos`):
  - The `T?` suffix must be on a handle-able ref type. `int?`, `bool?`,
    `mpos?`, etc. are forbidden — AngelScript has no `null` value for
    these.

Whether the marker triggers a runtime check or is purely declarative
documentation depends on the underlying type (codegen plumbs the check
for entity meta-types only). Both uses are valid — the validator does
not require entity-typed targets.

Exits non-zero with a list of violations. Used by CI and `Analyze ::
Nullable Placement` task.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_METHODS_DIR = ROOT / "Engine" / "Source" / "Scripting"
SOURCE_EXT_DIR = ROOT / "SourceExt"
SCRIPTS_ROOT = ROOT / "Scripts"

# Types the `?` suffix / FO_NULLABLE marker is *never* meaningful for —
# AngelScript has no `null` value of these types, and the engine's
# preprocessor doesn't recognize them as handle types either. Marker on
# any of these is a typo / leftover.
SCRIPT_PRIMITIVE_TYPES = frozenset({
    "void", "bool",
    "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64",
    "float", "float32", "float64", "double",
    "string", "hstring", "ident", "tick", "duration", "time",
    "mpos", "ipos", "mdir", "hdir", "any", "tpos", "ucolor",
})

# C++ engine primitives / value types where FO_NULLABLE would be a typo —
# the marker is only meaningful on a pointer to a class.
ENGINE_PRIMITIVE_TYPES = frozenset({
    "void", "bool",
    "int8_t", "int16_t", "int32_t", "int64_t",
    "uint8_t", "uint16_t", "uint32_t", "uint64_t", "size_t",
    "float32_t", "float64_t", "float", "double",
    "string", "string_view", "hstring", "ident_t", "any_t",
    "mpos", "ipos", "ipos32", "mdir", "hdir", "tpos", "ucolor",
})

EXPORT_METHOD_RE = re.compile(
    r"^///@\s*ExportMethod[^\n]*\n"
    r"FO_SCRIPT_API\s+"
    r"(?:(FO_NULLABLE)\s+)?"             # group 1 = return-type marker
    r"([A-Za-z_][\w:]*)\s*(\*?)\s+"      # group 2 = return type name, group 3 = `*` if pointer
    r"([A-Za-z_]\w*)\s*\("                # group 4 = function name
    r"([^)]*)\)",                          # group 5 = args text
    re.MULTILINE,
)

FO_NULLABLE_OCCURRENCE_RE = re.compile(r"\bFO_NULLABLE\b")


def find_line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def split_args(args_text: str) -> list[str]:
    pieces: list[str] = []
    depth = 0
    angle = 0
    cur: list[str] = []
    for c in args_text:
        if c == "(" or c == "[":
            depth += 1
            cur.append(c)
        elif c == ")" or c == "]":
            depth -= 1
            cur.append(c)
        elif c == "<":
            angle += 1
            cur.append(c)
        elif c == ">":
            angle -= 1
            cur.append(c)
        elif c == "," and depth == 0 and angle == 0:
            pieces.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    if cur:
        pieces.append("".join(cur).strip())
    return pieces


def parse_arg(arg_text: str) -> tuple[bool, str, bool, str]:
    """Return (has_marker, type_name_without_modifiers, is_pointer, param_name)."""
    a = arg_text.strip()
    has_marker = a.startswith("FO_NULLABLE")
    if has_marker:
        a = a[len("FO_NULLABLE"):].lstrip()
    # Drop default value if present
    if "=" in a:
        a = a.split("=", 1)[0].rstrip()
    sep = a.rfind(" ")
    if sep < 0:
        return has_marker, a, False, ""
    type_part = a[:sep].rstrip()
    name = a[sep + 1:].strip()
    is_pointer = type_part.rstrip().endswith("*")
    type_name = type_part.rstrip("*&").strip()
    return has_marker, type_name, is_pointer, name


def validate_engine() -> list[str]:
    errors: list[str] = []
    files = sorted(ENGINE_METHODS_DIR.glob("*ScriptMethods.cpp"))
    if SOURCE_EXT_DIR.is_dir():
        files += sorted(p for p in SOURCE_EXT_DIR.glob("*.cpp") if "ExportMethod" in p.read_text(encoding="utf-8", errors="ignore"))
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        # Track FO_NULLABLE offsets that fall inside a recognized ExportMethod
        # signature; anything not seen there is an out-of-band misuse.
        seen_marker_offsets: set[int] = set()

        for m in EXPORT_METHOD_RE.finditer(text):
            ret_marker = m.group(1)
            ret_type = m.group(2)
            ret_star = m.group(3)
            func_name = m.group(4)
            args_text = m.group(5)

            if ret_marker is not None:
                marker_offset = m.start(1)
                seen_marker_offsets.add(marker_offset)
                if not ret_star:
                    line = find_line_number(text, marker_offset)
                    errors.append(f"{f.relative_to(ROOT)}:{line}: FO_NULLABLE on non-pointer return type '{ret_type}' of '{func_name}' — the marker is only meaningful on pointer types")
                elif ret_type in ENGINE_PRIMITIVE_TYPES:
                    line = find_line_number(text, marker_offset)
                    errors.append(f"{f.relative_to(ROOT)}:{line}: FO_NULLABLE on primitive return type '{ret_type}*' of '{func_name}' — only class-pointer returns can be null")

            # Walk args and find their FO_NULLABLE markers
            args_offset_base = m.start(5)
            piece_offset = 0
            for piece in split_args(args_text):
                # Find the absolute offset of this piece's FO_NULLABLE if any
                idx = args_text.find(piece, piece_offset)
                if idx < 0:
                    continue
                piece_abs_start = args_offset_base + idx
                piece_offset = idx + len(piece)

                has_marker, type_name, is_pointer, param_name = parse_arg(piece)
                if not has_marker:
                    continue
                marker_offset = piece_abs_start + piece.find("FO_NULLABLE")
                seen_marker_offsets.add(marker_offset)
                if not is_pointer:
                    line = find_line_number(text, marker_offset)
                    errors.append(f"{f.relative_to(ROOT)}:{line}: FO_NULLABLE on non-pointer parameter '{type_name} {param_name}' of '{func_name}' — the marker is only meaningful on pointer types")
                elif type_name in ENGINE_PRIMITIVE_TYPES:
                    line = find_line_number(text, marker_offset)
                    errors.append(f"{f.relative_to(ROOT)}:{line}: FO_NULLABLE on primitive parameter '{type_name}* {param_name}' of '{func_name}' — only class-pointer args can be null")

        # Any remaining FO_NULLABLE occurrence (not seen inside a recognized
        # ExportMethod signature) is misuse.
        for m in FO_NULLABLE_OCCURRENCE_RE.finditer(text):
            if m.start() in seen_marker_offsets:
                continue
            line = find_line_number(text, m.start())
            errors.append(f"{f.relative_to(ROOT)}:{line}: FO_NULLABLE outside an `///@ ExportMethod` signature — the macro is a no-op here")

    return errors


# Script-side validator. Match `T?` where T is followed by `?` followed by
# whitespace and either an identifier (param/var name) or `[` (array suffix)
# or another sigil. We only validate inside the SAME contexts the engine
# preprocessor recognizes — at brace_depth 0 (outside function bodies). This
# matches the preprocessor's `StripNullableTypeSuffix` behavior.
SCRIPT_T_QUESTION_RE = re.compile(
    r"(?<![.\w])([A-Za-z_][\w:]*)\?(?=\s*(?:[A-Za-z_]|\[|\)|,|=))"
)


def split_outside_function_bodies_for_validation(text: str) -> list[tuple[int, int]]:
    """Return regions of `text` that are NOT inside function bodies — same
    detection rule as the engine preprocessor (`{` after `)`/`else`/`do`/
    `try`/`catch` opens a body)."""
    n = len(text)
    regions: list[tuple[int, int]] = []
    body_depth = 0
    region_start = 0
    i = 0
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
            i += 1
            continue
        if in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if in_char:
            if c == "\\":
                i += 2
                continue
            if c == "'":
                in_char = False
            i += 1
            continue
        if c == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if c == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "'":
            in_char = True
            i += 1
            continue
        if c == "{":
            j = i - 1
            while j >= 0 and text[j] in " \t\r\n":
                j -= 1
            is_body = False
            if j >= 0 and text[j] == ")":
                is_body = True
            elif j >= 0:
                wstart = j
                while wstart > 0 and (text[wstart - 1].isalnum() or text[wstart - 1] == "_"):
                    wstart -= 1
                if text[wstart:j + 1] in ("else", "do", "try", "catch"):
                    is_body = True
            if is_body:
                if body_depth == 0:
                    regions.append((region_start, i + 1))
                body_depth += 1
            i += 1
            continue
        if c == "}":
            if body_depth > 0:
                body_depth -= 1
                if body_depth == 0:
                    region_start = i
            i += 1
            continue
        i += 1
    regions.append((region_start, n))
    return regions


def validate_scripts() -> list[str]:
    errors: list[str] = []
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    for f in files:
        if f.name in ("GuiScreens.fos", "Content.fos"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for region_start, region_end in split_outside_function_bodies_for_validation(text):
            chunk = text[region_start:region_end]
            for m in SCRIPT_T_QUESTION_RE.finditer(chunk):
                type_name = m.group(1)
                # Strip namespace prefix for the test, e.g. `Gui::Object` -> `Object`
                bare = type_name.rsplit("::", 1)[-1]
                if bare not in SCRIPT_PRIMITIVE_TYPES:
                    continue
                abs_offset = region_start + m.start()
                line = find_line_number(text, abs_offset)
                errors.append(f"{f.relative_to(ROOT)}:{line}: `?` on primitive type '{type_name}' — primitives cannot be null in AngelScript")
    return errors


# Match `///@ Event <Target> <Entity> EventName(arg1, arg2, ...)` and
# `///@ RemoteCall <Target> CallName(arg1, arg2, ...)`. Captures the part
# inside the parentheses for per-arg analysis.
SCRIPT_EVENT_DECL_RE = re.compile(
    r"^///@\s*Event\s+\S+\s+\S+\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)
SCRIPT_REMOTECALL_DECL_RE = re.compile(
    r"^///@\s*RemoteCall\s+(Server|Client)\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)

# `[[Event]] void OnXxx(args)` / `[[ServerRemoteCall]] void XxxName(args)` etc.
# Capture the attribute, function name, and args span. The handler may carry
# extra attributes between `[[ ]]` and the return type.
HANDLER_DECL_RE = re.compile(
    r"^\[\[(Event|ServerRemoteCall|ClientRemoteCall|AdminRemoteCall)\]\]\s*\n"
    r"\w[\w?:\s\[\]]*?\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)


def parse_decl_args(args_text: str) -> list[tuple[str, bool, str]]:
    """Return [(type, nullable, name)] for each parsed argument."""
    result: list[tuple[str, bool, str]] = []
    for piece in split_args(args_text):
        piece = piece.strip()
        if not piece:
            continue
        # Drop default value
        if "=" in piece:
            piece = piece.split("=", 1)[0].rstrip()
        # Split into tokens; last token is name, rest is type
        tokens = piece.split()
        if len(tokens) < 2:
            continue
        name = tokens[-1]
        type_part = " ".join(tokens[:-1])
        nullable = type_part.endswith("?")
        if nullable:
            type_part = type_part[:-1].rstrip()
        result.append((type_part, nullable, name))
    return result


def validate_event_and_remotecall_signatures() -> list[str]:
    """For every `///@ Event` / `///@ RemoteCall` declaration in scripts,
    find the matching handler/subscriber function and verify per-arg `?`
    markers agree. Mismatches are real bugs: the declared contract and the
    implementation disagree about whether `null` is allowed.

    The handler lookup is by attribute and function name:
      `///@ Event ... OnXxx(...)` → `[[Event]] void OnXxx(...)`
      `///@ RemoteCall Server Xxx(...)` → `[[ServerRemoteCall]] void Xxx(...)`
    Multiple files may define the same handler name (e.g. several
    subscribers to the same event). Each definition is validated separately.
    """
    errors: list[str] = []
    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))

    declarations: list[tuple[Path, int, str, str, list[tuple[str, bool, str]]]] = []
    # Per (attribute, function_name) → list of (file, line, args)
    handlers: dict[tuple[str, str], list[tuple[Path, int, list[tuple[str, bool, str]]]]] = {}

    for f in files:
        if f.name in ("GuiScreens.fos", "Content.fos"):
            continue
        text = f.read_text(encoding="utf-8", errors="replace")

        for m in SCRIPT_EVENT_DECL_RE.finditer(text):
            event_name = m.group(1)
            args = parse_decl_args(m.group(2))
            line = find_line_number(text, m.start())
            declarations.append((f, line, "Event", event_name, args))

        for m in SCRIPT_REMOTECALL_DECL_RE.finditer(text):
            target = m.group(1)
            call_name = m.group(2)
            args = parse_decl_args(m.group(3))
            line = find_line_number(text, m.start())
            declarations.append((f, line, target + "RemoteCall", call_name, args))

        for m in HANDLER_DECL_RE.finditer(text):
            attr = m.group(1)
            func_name = m.group(2)
            args = parse_decl_args(m.group(3))
            line = find_line_number(text, m.start())
            handlers.setdefault((attr, func_name), []).append((f, line, args))

    for decl_file, decl_line, decl_attr, decl_name, decl_args in declarations:
        # Event handlers use the [[Event]] attribute; remote calls use
        # [[<Target>RemoteCall]] matching the declaration target.
        if decl_attr == "Event":
            handler_attr = "Event"
        else:
            handler_attr = decl_attr  # ServerRemoteCall / ClientRemoteCall
        impls = handlers.get((handler_attr, decl_name), [])

        if not impls and decl_attr.endswith("RemoteCall"):
            # An inbound RemoteCall declaration must have a matching impl on
            # the corresponding side. If absent, the engine already errors
            # at module load — but flag it here too for early feedback.
            errors.append(
                f"{decl_file.relative_to(ROOT)}:{decl_line}: `///@ RemoteCall` '{decl_name}' "
                f"has no matching `[[{handler_attr}]]` function"
            )
            continue

        for impl_file, impl_line, impl_args in impls:
            if len(impl_args) != len(decl_args):
                # AS engine catches arg-count mismatch at module load — skip
                # here to avoid duplicate noise.
                continue
            mismatched: list[str] = []
            for index, (decl_arg, impl_arg) in enumerate(zip(decl_args, impl_args)):
                if decl_arg[1] != impl_arg[1]:
                    mismatched.append(
                        f"arg #{index + 1} '{impl_arg[2]}': "
                        f"declared {'nullable' if decl_arg[1] else 'non-null'}, "
                        f"handler is {'nullable' if impl_arg[1] else 'non-null'}"
                    )
            if mismatched:
                errors.append(
                    f"{impl_file.relative_to(ROOT)}:{impl_line}: [[{handler_attr}]] '{decl_name}' "
                    f"nullable mismatch vs declaration at "
                    f"{decl_file.relative_to(ROOT)}:{decl_line} — " + "; ".join(mismatched)
                )

    return errors


def main() -> int:
    errors_engine = validate_engine()
    errors_scripts = validate_scripts()
    errors_signatures = validate_event_and_remotecall_signatures()
    if errors_engine:
        print("=== Engine FO_NULLABLE placement errors ===", file=sys.stderr)
        for e in errors_engine:
            print(e, file=sys.stderr)
        print(file=sys.stderr)
    if errors_scripts:
        print("=== Script `?` placement errors ===", file=sys.stderr)
        for e in errors_scripts:
            print(e, file=sys.stderr)
        print(file=sys.stderr)
    if errors_signatures:
        print("=== Event/RemoteCall handler signature mismatches ===", file=sys.stderr)
        for e in errors_signatures:
            print(e, file=sys.stderr)
        print(file=sys.stderr)
    total = len(errors_engine) + len(errors_scripts) + len(errors_signatures)
    if total > 0:
        print(
            f"FAILED: {total} violation(s) "
            f"({len(errors_engine)} engine, {len(errors_scripts)} script, {len(errors_signatures)} handler-mismatch)",
            file=sys.stderr,
        )
        return 1
    print("OK: nullability marker placement is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
