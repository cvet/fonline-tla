#!/usr/bin/env python3
"""Quality validators for TLA AngelScript (`Scripts/**/*.fos`).

This is a *validator*, not an auto-formatter: by default it only reports.
Autofixes for the unambiguous, safe checks are applied only on explicit
`--fix`. It complements `Tools/NullableEstimate/validate_nullable.py`
(which owns script `?`, native `ptr<T>`/`nptr<T>` ABI checks, and
Event/RemoteCall signature parity); this tool owns the broader hygiene rules
surfaced by the script refactoring audit.

Checks (severity):
  ERROR   trailing-blank-line        exactly one terminator at EOF, no extra blank
  ERROR   namespace-matches-filename first top-level namespace == file basename
  ERROR   preprocessor-guard-balance #if/#ifdef/#ifndef balance with #endif
  ERROR   component-null-probe       `.Comp == null` instead of `!HasComp`
  ERROR   item-static-signature      ItemStatic must match its engine callback ABI
  ERROR   legacy-item-kind           retired `ItemType`/`ItemProperty::Type` or a flat
                                     `<Comp>_<Field>` property of a declared component
  WARNING banner-tags               `// Author:` / `// ver x.y` header banners
  WARNING textpack-magic-id         `"" + (1234)` magic text-pack ids
  WARNING hand-rolled-utils         calls to helpers that duplicate engine APIs
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
# Component-accessor set: `///@ Property <Entity> <side> bool <Name> Component`
# declarations plus `.HasXxx` usage across all scripts (engine-provided
# Has-accessors such as HasChosen are known only from usage), so the
# component-null-probe check knows which `.Xxx == null` can be real probes.
# --------------------------------------------------------------------------

HAS_FLAG_RE = re.compile(r"\.Has([A-Z][A-Za-z0-9_]*)\b")
COMPONENT_DECLARATION_RE = re.compile(
    r"^[ \t]*///@[ \t]+Property[ \t]+\w+[ \t]+\w+[ \t]+bool[ \t]+([A-Za-z_]\w*)[ \t]+Component\b",
    re.MULTILINE,
)


def derive_component_names(code_text: str, source_text: str = "") -> set[str]:
    """Names from `.HasXxx` usage in code and from Component declarations in source."""
    return set(HAS_FLAG_RE.findall(code_text)) | set(COMPONENT_DECLARATION_RE.findall(source_text))


ENTITY_COMPONENT_DECLARATION_RE = re.compile(
    r"^[ \t]*///@[ \t]+Property[ \t]+(\w+)[ \t]+\w+[ \t]+bool[ \t]+([A-Za-z_]\w*)[ \t]+Component\b",
    re.MULTILINE,
)


def derive_entity_components(source_text: str) -> dict[str, set[str]]:
    """Declared component markers per entity: `///@ Property <Entity> <side> bool <Name> Component`."""
    out: dict[str, set[str]] = {}
    for entity, name in ENTITY_COMPONENT_DECLARATION_RE.findall(source_text):
        out.setdefault(entity, set()).add(name)
    return out


# A probe receiver that is a plain identifier declared in the same file with a
# type outside these entity handle types (e.g. `Gui::Object? obj`, whose `Grid`
# is the GUI cell grid) is not a component probe. Undeclared, `auto` and
# compound receivers (`a.b.Comp`, `f().Comp`) stay reported.
ENTITY_HANDLE_TYPES = frozenset({
    "Item", "AbstractItem", "ProtoItem", "StaticItem",
    "Critter", "AbstractCritter", "ProtoCritter",
    "Map", "AbstractMap", "ProtoMap",
    "Location", "AbstractLocation", "ProtoLocation",
    "Player", "AbstractPlayer",
})
UNKNOWN_DECLARATION_TYPES = frozenset({"auto"})
# Words that can precede an identifier without declaring it (`return obj`, `not obj`).
NON_TYPE_WORDS = frozenset({
    "abstract", "and", "break", "case", "cast", "catch", "class", "const", "continue", "default",
    "delete", "do", "else", "enum", "explicit", "external", "false", "final", "for", "funcdef",
    "if", "import", "in", "inout", "interface", "is", "mixin", "namespace", "new", "not", "null",
    "or", "out", "override", "private", "property", "protected", "return", "shared", "super",
    "switch", "this", "throw", "true", "try", "typedef", "while", "xor",
})


def plain_receiver(code: str, dot: int) -> str | None:
    """Identifier directly before `code[dot] == '.'`, or None for a compound receiver."""
    start = dot
    while start > 0 and (code[start - 1].isalnum() or code[start - 1] == "_"):
        start -= 1
    ident = code[start:dot]
    if not ident or ident[0].isdigit() or ident in NON_TYPE_WORDS:
        return None
    if start > 0 and code[start - 1] in ".:)]>":
        return None
    return ident


FOREACH_HEAD_RE = re.compile(r"\b(?:for|foreach)[ \t]*\($")


def declaration_head(code: str, start: int) -> str:
    """Same-line text before a declaration candidate, without a trailing `const`."""
    head = code[code.rfind("\n", 0, start) + 1:start].rstrip()
    if head.endswith("const") and (len(head) == 5 or not (head[-6].isalnum() or head[-6] == "_")):
        head = head[:-5].rstrip()
    return head


def declared_type(code: str, ident: str, before: int) -> str | None:
    """Type of the nearest declaration of `ident` before offset `before` (scope approximation).

    A candidate counts only at a declaration position (line start or after `( , ; { }`,
    optionally `const`) and before a declaration terminator (`=`, `;`, `,`, `)`, foreach `:`).
    That rejects operands such as `flag ? item : x`, `mask & item` and `x = flag ? item : y`.
    """
    declaration_re = re.compile(
        r"(?<![\w.:])((?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)"  # type, optionally namespace-qualified
        r"((?:[ \t]*<[^<>;{}()]*>)?"  # template arguments: array<Item@>
        r"(?:[ \t]*\[[ \t]*\])*"  # array suffix: Item[]
        r"(?:[ \t]*[?@])*"  # nullable / handle: Item?, Item ?, Item@
        # Reference: `Item& x`, `Item &in x`, `Item[] & x`; a spaced `a & b` is a bitwise operand.
        r"(?:&[ \t]*(?:in|out|inout)\b|&|[ \t]+&[ \t]*(?:in|out|inout)\b|(?<=[\]>])[ \t]*&)?)"
        r"[ \t]*(?<=[ \t?@&>\]])" + re.escape(ident) + r"\b"
        r"(?=[ \t]*(?:=(?!=)|;|,|\)|:(?!:)))"  # declaration terminator
    )
    found = None
    for match in declaration_re.finditer(code, 0, before):
        type_name, suffix = match.group(1), match.group(2)
        if type_name in NON_TYPE_WORDS:
            continue
        head = declaration_head(code, match.start())
        if head and head[-1] not in "(,;{}":
            continue
        # `(flag ? item : other)`: a `?` before `<ident> :` is a ternary unless this is a foreach head.
        if "?" in suffix and code[match.end():].lstrip(" \t").startswith(":") and not FOREACH_HEAD_RE.search(head):
            continue
        found = type_name
    return found


def is_non_entity_receiver(code: str, dot: int) -> bool:
    ident = plain_receiver(code, dot)
    if ident is None:
        return False
    type_name = declared_type(code, ident, dot)
    if type_name is None or type_name in UNKNOWN_DECLARATION_TYPES:
        return False
    return type_name not in ENTITY_HANDLE_TYPES


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

ANNOTATED_DECL_RE = re.compile(
    r"(?P<attrs>(?:[ \t]*\[\[[^\]\n]+\]\][ \t\r\n]*)+)"
    r"(?P<header>[^{};]+?)[ \t\r\n]*(?:\{|;)",
    re.MULTILINE,
)
ITEM_STATIC_ATTRIBUTE_RE = re.compile(r"\[\[[^\]\n]*\bItemStatic\b[^\]\n]*\]\]")
FUNCTION_HEADER_RE = re.compile(
    r"^[ \t\r\n]*(?P<return_type>.+?)[ \t\r\n]+(?P<name>[A-Za-z_]\w*)"
    r"[ \t\r\n]*\((?P<params>.*)\)[ \t\r\n]*$",
    re.DOTALL,
)
ITEM_STATIC_PARAM_RES = (
    re.compile(r"^[ \t\r\n]*Critter[ \t\r\n]+[A-Za-z_]\w*[ \t\r\n]*$"),
    re.compile(r"^[ \t\r\n]*StaticItem[ \t\r\n]+[A-Za-z_]\w*[ \t\r\n]*$"),
    re.compile(r"^[ \t\r\n]*Item[ \t\r\n]*\?[ \t\r\n]+[A-Za-z_]\w*[ \t\r\n]*$"),
    re.compile(r"^[ \t\r\n]*any[ \t\r\n]+[A-Za-z_]\w*[ \t\r\n]*$"),
)


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
        if is_non_entity_receiver(code, m.start()):
            continue
        comp = m.group(1)
        op = m.group(2)
        fix = f"!{'.'}Has{comp}" if op == "==" else f".Has{comp}"
        out.append(Violation("component-null-probe", rel, line_of(text, m.start()),
                             f".{comp} {op} null — use {'!x.Has' if op == '==' else 'x.Has'}{comp} (component accessors are guarded by Has{comp})",
                             SEVERITY_ERROR))
    return out


# Retired item-kind spellings: the kind enum and its property were replaced by
# property components (`Has<Comp>`, ItemKinds predicates). Code is matched
# outside comments and strings; `///@` metadata lines are matched as source.
LEGACY_ITEM_KIND_CODE_RE = re.compile(r"\bItemType\b|\bItemProperty[ \t]*::[ \t]*Type\b")
METADATA_LINE_RE = re.compile(r"^[ \t]*///@[^\n]*", re.MULTILINE)
LEGACY_ITEM_KIND_METADATA_RE = re.compile(r"\bItemType\b")
# `///@ Property <Entity> <side> <type> <name> ...`; the type may contain spaces (`dict<a, b>`).
PROPERTY_DECLARATION_RE = re.compile(r"^[ \t]*///@[ \t]+Property[ \t]+(\w+)[ \t]+\w+[ \t]+.+?[ \t]+([A-Za-z_][\w.]*)(?=[ \t]|$)")


def check_legacy_item_kind(rel: str, code: str, text: str, entity_components: dict[str, set[str]]) -> list[Violation]:
    out: list[Violation] = []
    for m in LEGACY_ITEM_KIND_CODE_RE.finditer(code):
        out.append(Violation("legacy-item-kind", rel, line_of(text, m.start()),
                             f"{m.group(0)} is retired — test kind components (`item.Has<Comp>`) or ItemKinds predicates",
                             SEVERITY_ERROR))
    for meta in METADATA_LINE_RE.finditer(text):
        line = meta.group(0)
        if LEGACY_ITEM_KIND_METADATA_RE.search(line):
            out.append(Violation("legacy-item-kind", rel, line_of(text, meta.start()),
                                 "ItemType is retired — model item kinds as property components",
                                 SEVERITY_ERROR))
            continue
        decl = PROPERTY_DECLARATION_RE.match(line)
        if decl is None:
            continue
        entity, name = decl.groups()
        for comp in sorted(entity_components.get(entity, ())):
            if name.startswith(comp + "_") and len(name) > len(comp) + 1:
                field = name[len(comp) + 1:]
                out.append(Violation("legacy-item-kind", rel, line_of(text, meta.start()),
                                     f"flat {entity} property {name} of component {comp} — declare {comp}.{field}",
                                     SEVERITY_ERROR))
                break
    return sorted(out, key=lambda v: v.line)


def check_item_static_signature(rel: str, code: str, text: str) -> list[Violation]:
    """Require the exact native callback contract for every ItemStatic function."""
    out: list[Violation] = []
    for match in ANNOTATED_DECL_RE.finditer(code):
        attrs = match.group("attrs")
        if not ITEM_STATIC_ATTRIBUTE_RE.search(attrs):
            continue

        header = match.group("header")
        signature = FUNCTION_HEADER_RE.fullmatch(header)
        valid = signature is not None
        if signature is not None:
            return_type = re.sub(r"[ \t\r\n]+", " ", signature.group("return_type").strip())
            params_text = signature.group("params").strip()
            params = [] if not params_text else params_text.split(",")
            valid = (
                return_type == "bool"
                and len(params) == len(ITEM_STATIC_PARAM_RES)
                and all(pattern.fullmatch(param) for pattern, param in zip(ITEM_STATIC_PARAM_RES, params))
            )

        if valid:
            continue

        actual = re.sub(r"[ \t\r\n]+", " ", header.strip())
        out.append(Violation(
            "item-static-signature",
            rel,
            line_of(text, match.start("attrs")),
            "ItemStatic callback must have signature "
            f"`bool NAME(Critter, StaticItem, Item?, any)`; got `{actual}`",
            SEVERITY_ERROR,
        ))
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
    # Test suites (Scripts/Test_*.fos) legitimately call the helpers under test;
    # the rule exists to steer gameplay code to native APIs, not to block coverage.
    if rel.replace("\\", "/").rsplit("/", 1)[-1].startswith("Test_"):
        return []

    out: list[Violation] = []
    for rx, hint in HAND_ROLLED:
        for m in rx.finditer(code):
            out.append(Violation("hand-rolled-utils", rel, line_of(text, m.start()),
                                 f"{m.group(0)} duplicates an engine API — {hint}", SEVERITY_WARNING))
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
    all_source = []
    cache: dict[Path, tuple[str, bytes, str]] = {}
    for f in files:
        raw = f.read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        kinds = classify(text)
        cache[f] = (text, raw, kinds)
        all_text.append(mask_to(text, kinds, "c"))
        all_source.append(text)
    components = derive_component_names("\n".join(all_text), "\n".join(all_source))
    entity_components = derive_entity_components("\n".join(all_source))

    violations: list[Violation] = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        text, raw, kinds = cache[f]
        code = mask_to(text, kinds, "c")
        violations += check_trailing_blank_line(rel, raw)
        violations += check_namespace(rel, f.name, text)
        violations += check_guard_balance(rel, code)
        violations += check_component_null_probe(rel, code, text, components)
        violations += check_item_static_signature(rel, code, text)
        violations += check_legacy_item_kind(rel, code, text, entity_components)
        violations += check_banner_tags(rel, text, kinds)
        violations += check_textpack_magic(rel, text, kinds)
        violations += check_hand_rolled(rel, code, text)
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
            # Same receiver rule as the check: a non-entity receiver stays as written.
            if is_non_entity_receiver(code, m.start(2) - 1):
                return text[m.start():m.end()]
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
    all_source = []
    for f in files:
        raw = f.read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        all_text.append(mask_to(text, classify(text), "c"))
        all_source.append(text)
    components = derive_component_names("\n".join(all_text), "\n".join(all_source))
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
