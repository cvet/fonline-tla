#!/usr/bin/env python3
"""Validate native ptr/nptr script ABI and AngelScript `?` contracts.

Engine-side script handles use explicit borrowed-pointer wrappers:
`ptr<T>` is non-null and `nptr<T>` is nullable. Bare `T*` is rejected on
script-facing surfaces, while ordinary internal C++ pointers and engine
hooks remain outside this check. The native gate covers:

  - `FO_SCRIPT_API` declarations owned by `///@ ExportMethod`;
  - members named by a `///@ ExportRefType ... Export = ...` list;
  - `FindFunc<...>` / `CheckFunc<...>` script-signature template args.

The removed `FO_NULLABLE` macro is rejected if it reappears in native code.

Script side (`Scripts/**/*.fos`):
  - The `T?` suffix must be on a handle-able ref type. `int?`, `bool?`,
    `mpos?`, etc. are forbidden — AngelScript has no `null` value for
    these.

Exits non-zero with a list of violations. Used by CI and `Analyze ::
Nullable Placement` task.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_SOURCE_DIR = ROOT / "Engine" / "Source"
SOURCE_EXT_DIR = ROOT / "SourceExt"
SCRIPTS_ROOT = ROOT / "Scripts"
NATIVE_SOURCE_SUFFIXES = frozenset({".cc", ".cpp", ".h", ".hpp"})

# Types the `?` suffix is never meaningful for: AngelScript has no `null`
# value of these types.
SCRIPT_PRIMITIVE_TYPES = frozenset({
    "void", "bool",
    "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64",
    "float", "float32", "float64", "double",
    "string", "hstring", "ident", "tick", "duration", "time",
    "mpos", "ipos", "mdir", "hdir", "any", "tpos", "ucolor",
})

EXPORT_METHOD_RE = re.compile(
    r"^[ \t]*///@\s*ExportMethod\b[^\r\n]*\r?\n(?P<signature>[^\r\n]*)",
    re.MULTILINE,
)
EXPORT_REF_TYPE_RE = re.compile(
    r"^[ \t]*///@\s*ExportRefType\b(?P<flags>[^\r\n]*)",
    re.MULTILINE,
)
FO_SCRIPT_API_RE = re.compile(r"\bFO_SCRIPT_API\b")
FO_NULLABLE_RE = re.compile(r"\bFO_NULLABLE\b")
TEMPLATE_CALL_RE = re.compile(r"\b(?P<name>FindFunc|CheckFunc)\s*<")
CPP_RAW_STRING_START_RE = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')

# A script handle may be namespaced and cv-qualified. The lookahead avoids
# treating multiplication (`count * 2`) as a pointer declarator.
RAW_POINTER_RE = re.compile(
    r"(?<![\w:])(?:(?:const|volatile)\s+)*"
    r"(?P<type>[A-Za-z_]\w*(?:::\w+)*)\s*\*"
    r"(?=\s*(?:const\b|volatile\b|[A-Za-z_]\w*|[,>&)\[\];={}]|$))"
)


def find_line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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


def mask_cpp_non_code(text: str, *, preserve_codegen_tags: bool = False) -> str:
    """Blank C++ comments and literals while preserving offsets/newlines."""
    chars = list(text)
    n = len(text)
    i = 0

    def blank(start: int, end: int) -> None:
        for pos in range(start, end):
            if chars[pos] not in "\r\n":
                chars[pos] = " "

    while i < n:
        if text.startswith("//", i):
            end = text.find("\n", i + 2)
            end = n if end == -1 else end
            line_start = text.rfind("\n", 0, i) + 1
            is_codegen_tag = text.startswith("///@", i) and not text[line_start:i].strip()
            if not (preserve_codegen_tags and is_codegen_tag):
                blank(i, end)
            i = end
            continue
        if text.startswith("/*", i):
            close = text.find("*/", i + 2)
            end = n if close == -1 else close + 2
            blank(i, end)
            i = end
            continue

        raw_match = CPP_RAW_STRING_START_RE.match(text, i)
        if raw_match is not None:
            delimiter = raw_match.group(1)
            close_token = ")" + delimiter + '"'
            content_start = raw_match.end()
            close = text.find(close_token, content_start)
            end = n if close == -1 else close + len(close_token)
            blank(i, end)
            i = end
            continue

        prefix_len = 0
        for prefix in ('u8"', 'u"', 'U"', 'L"', '"', "u8'", "u'", "U'", "L'", "'"):
            if text.startswith(prefix, i):
                prefix_len = len(prefix)
                quote = prefix[-1]
                break
        if prefix_len:
            j = i + prefix_len
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == quote:
                    j += 1
                    break
                j += 1
            blank(i, min(j, n))
            i = min(j, n)
            continue
        i += 1
    return "".join(chars)


def find_matching_delimiter(text: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return -1


def previous_line(text: str, offset: int) -> str:
    line_start = text.rfind("\n", 0, offset) + 1
    previous_end = max(0, line_start - 1)
    previous_start = text.rfind("\n", 0, previous_end) + 1
    return text[previous_start:previous_end].strip()


def validate_native_text(path: Path, text: str) -> list[str]:
    """Validate one native source file. Kept pure for focused unit tests."""
    if not any(token in text for token in ("ExportMethod", "ExportRefType", "FO_SCRIPT_API", "FindFunc", "CheckFunc", "FO_NULLABLE")):
        return []

    errors: list[str] = []
    shown_path = display_path(path)
    masked = mask_cpp_non_code(text)
    tags_visible = mask_cpp_non_code(text, preserve_codegen_tags=True)
    reported_raw_offsets: set[int] = set()

    def report_raw(fragment: str, base_offset: int, surface: str) -> None:
        for pointer in RAW_POINTER_RE.finditer(fragment):
            offset = base_offset + pointer.start()
            if offset in reported_raw_offsets:
                continue
            reported_raw_offsets.add(offset)
            line = find_line_number(text, offset)
            type_name = pointer.group("type")
            errors.append(
                f"{shown_path}:{line}: raw pointer '{type_name}*' in {surface} — "
                "use ptr<T> for non-null or nptr<T> for nullable script handles"
            )

    # ExportMethod context is one line by codegen contract.
    for match in EXPORT_METHOD_RE.finditer(tags_visible):
        signature = match.group("signature")
        signature_offset = match.start("signature")
        report_raw(mask_cpp_non_code(signature), signature_offset, "`///@ ExportMethod` signature")

    # Catch unannotated FO_SCRIPT_API declarations too, while intentionally
    # excluding EngineHook: hooks use a separate native ABI and SetupBakersHook
    # is not a script-callable binding.
    for match in FO_SCRIPT_API_RE.finditer(masked):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line_end = len(text) if line_end == -1 else line_end
        owner_tag = previous_line(text, match.start())
        if owner_tag.startswith("///@ EngineHook"):
            continue
        surface = "`///@ ExportMethod` signature" if owner_tag.startswith("///@ ExportMethod") else "FO_SCRIPT_API signature"
        report_raw(masked[line_start:line_end], line_start, surface)

    # Only members explicitly named after `Export =` are script ABI. Internal
    # raw helpers and storage in the same class remain outside this gate.
    for tag in EXPORT_REF_TYPE_RE.finditer(tags_visible):
        export_match = re.search(r"\bExport\s*=\s*(?P<names>.*)$", tag.group("flags"))
        if export_match is None:
            continue
        export_names = set(re.findall(r"[A-Za-z_]\w*", export_match.group("names")))
        if not export_names:
            continue

        class_match = re.search(r"\b(?:class|struct)\s+[A-Za-z_]\w*[^;{]*\{", masked[tag.end():])
        if class_match is None:
            continue
        class_open = tag.end() + class_match.end() - 1
        class_close = find_matching_delimiter(masked, class_open, "{", "}")
        if class_close == -1:
            continue

        block_offset = class_open + 1
        for line in masked[block_offset:class_close].splitlines(keepends=True):
            member_name = ""
            for method_match in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", line):
                if method_match.group(1) in export_names:
                    member_name = method_match.group(1)
                    break
            if not member_name:
                for field_name in sorted(export_names):
                    if re.search(rf"\b{re.escape(field_name)}\b\s*(?:\{{|=|;)", line):
                        member_name = field_name
                        break
            if member_name:
                report_raw(line, block_offset, f"exported `///@ ExportRefType` member '{member_name}'")
            block_offset += len(line)

    # FindFunc/CheckFunc template arguments describe AngelScript signatures.
    # Balance nested templates so containers such as vector<Item*> are caught.
    for call in TEMPLATE_CALL_RE.finditer(masked):
        angle_open = call.end() - 1
        angle_close = find_matching_delimiter(masked, angle_open, "<", ">")
        if angle_close == -1:
            continue
        args_offset = angle_open + 1
        report_raw(masked[args_offset:angle_close], args_offset, f"{call.group('name')} template arguments")

    for marker in FO_NULLABLE_RE.finditer(masked):
        line = find_line_number(text, marker.start())
        errors.append(
            f"{shown_path}:{line}: obsolete FO_NULLABLE marker — "
            "use ptr<T> for non-null or nptr<T> for nullable script handles"
        )

    return errors


def iter_native_files() -> list[Path]:
    files: list[Path] = []
    for root in (ENGINE_SOURCE_DIR, SOURCE_EXT_DIR):
        if not root.is_dir():
            continue
        files.extend(path for path in root.rglob("*") if path.suffix in NATIVE_SOURCE_SUFFIXES)
    return sorted(files)


def validate_engine() -> list[str]:
    errors: list[str] = []
    for path in iter_native_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(validate_native_text(path, text))
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
# Capture all leading attributes, function name, and args span. The handler may
# carry extra attributes before the return type, e.g. `[[ServerRemoteCall]] [[Async]]`.
HANDLER_DECL_RE = re.compile(
    r"^((?:\[\[\w+\]\]\s*)+)"
    r"\w[\w?:\s\[\]]*?\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)
HANDLER_ATTR_RE = re.compile(r"\[\[(Event|ServerRemoteCall|ClientRemoteCall|AdminRemoteCall)\]\]")


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
            attrs = HANDLER_ATTR_RE.findall(m.group(1))
            if not attrs:
                continue
            func_name = m.group(2)
            args = parse_decl_args(m.group(3))
            line = find_line_number(text, m.start())
            for attr in attrs:
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
    errors_native = validate_engine()
    errors_scripts = validate_scripts()
    errors_signatures = validate_event_and_remotecall_signatures()
    if errors_native:
        print("=== Native ptr/nptr script ABI errors ===", file=sys.stderr)
        for e in errors_native:
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
    total = len(errors_native) + len(errors_scripts) + len(errors_signatures)
    if total > 0:
        print(
            f"FAILED: {total} violation(s) "
            f"({len(errors_native)} native ABI, {len(errors_scripts)} script, {len(errors_signatures)} handler-mismatch)",
            file=sys.stderr,
        )
        return 1
    print("OK: nullability and native ptr/nptr script ABI contracts are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
