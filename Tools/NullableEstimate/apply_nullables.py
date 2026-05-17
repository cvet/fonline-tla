#!/usr/bin/env python3
"""Apply `T?` nullable suffix + aggressive cleanup of dead null checks.

Decision rule (with transitive propagation and two-branch handling check):
1. A parameter starts as "non-nullable" by default.
2. A parameter is marked nullable (KEEP, gets `?` suffix on its type) iff
   ALL of:
   a. The body genuinely two-branches on null vs non-null (else clause on
      `if (param == null)`, or `param != null ? ... :` ternary, or
      `param != null &&` short-circuit). Early-exit-only guards do NOT
      count — per the design principle "лучше не передаём null, чем
      внутри проверяем на null и выходим".
   b. AND one of:
      - At least one caller passes literal `null` at that argument position;
      - The function has an engine-invoked attribute (Event, TimeEvent,
        ModuleInit, PropertyGetter, PropertySetter, AnimCallback, *RemoteCall,
        DialogDemand, DialogResult);
      - The function name is the target of `@FuncName` (delegate) or is
        passed as a bare-identifier argument to another function;
      - The function has NO direct callers anywhere in scripts (conservative
        — could be called from dialog/proto/external data);
      - Some caller passes its own KEEP param at that position (transitive
        propagation, iterated until convergence).
3. A return type gets `?` suffix iff the body has `return null;` AND
   the return type is not primitive/void.

Cleanup for parameters that end up NON-nullable:
- Strip any existing `?` type suffix or legacy `[[Nullable]]` marker.
- Remove `Assert(param != null, ...)` lines from the body.
- Remove `if (param == null) { ... }` standalone guards (collapsing the
  paired `else` body to the main flow when present).
- Remove `param == null ||` and `|| param == null` clauses inside conditions.
- Remove `param != null &&` and `&& param != null` clauses.

Asserts on local variables (non-param names) are left intact.

The applier is idempotent: running it twice with no script changes between
runs is a no-op.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "Scripts"
ENGINE_SOURCE_DIR = ROOT / "Engine" / "Source"


def _discover_validated_script_types() -> frozenset[str]:
    """Mirror codegen's `is_validated_pointer_meta_type` for script-side meta
    names. Codegen emits `CheckArgNotNull` / `CheckReturnNotNull` at the
    script ↔ native boundary for: every `///@ ExportEntity` meta name and
    its declared relatives (Abstract/Proto/Static prefixes), the generic
    `Entity` base, and every `///@ ExportRefType` class. The script-facing
    meta name equals the entity name for entities/relatives and the class
    name for RefTypes."""
    types: set[str] = {"Entity"}

    export_entity_re = re.compile(r"///@\s*ExportEntity\s+(.+)")
    for path in ENGINE_SOURCE_DIR.rglob("*.h"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in export_entity_re.finditer(text):
            tokens = m.group(1).split()
            if len(tokens) < 3:
                continue
            entity_name = tokens[0]
            flags = tokens[3:]
            types.add(entity_name)
            if "HasAbstract" in flags:
                types.add("Abstract" + entity_name)
            if "HasProtos" in flags:
                types.add("Proto" + entity_name)
            if "HasStatics" in flags:
                types.add("Static" + entity_name)

    export_ref_re = re.compile(r"///@\s*ExportRefType\b[^\n]*\n(?:\s*//[^\n]*\n)*\s*class\s+(\w+)")
    for path in ENGINE_SOURCE_DIR.rglob("*.h"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in export_ref_re.finditer(text):
            types.add(m.group(1))

    return frozenset(types)


# Engine codegen emits `CheckArgNotNull` / `CheckReturnNotNull` for these
# meta-types at the script ↔ native boundary. Marking `?` on anything else
# (pure script class, primitive) is a no-op for runtime checks. The applier
# only manages `?` markers on this set; script-class markers (e.g. `Plan?`,
# `ItemBag?`) are documentary and out of scope.
SCRIPT_ENTITY_TYPES = _discover_validated_script_types()

PRIMITIVE_TYPES = {
    "void", "bool", "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64",
    "float", "float32", "float64", "double",
    "string", "hstring", "ident", "tick", "duration", "time",
    "mpos", "ipos", "mdir", "hdir", "any", "tpos",
}

ENGINE_INVOKED_ATTRS = {
    "Event", "TimeEvent", "ModuleInit", "PropertyGetter", "PropertySetter",
    "AnimCallback", "ServerRemoteCall", "ClientRemoteCall", "AdminRemoteCall",
    "DialogDemand", "DialogResult",
}

CONTROL_KEYWORDS = {
    "if", "for", "while", "switch", "do", "namespace", "class", "interface",
    "mixin", "enum", "case", "return", "else", "funcdef", "typedef",
}

FUNC_RE = re.compile(
    r"""^
        (?P<indent>[ \t]*)
        (?P<attrs>(?:\[\[[^\]\n]+\]\]\s*)*)
        (?P<ret>(?:\[\[\s*Nullable\s*\]\]\s+)?[A-Za-z_][\w:]*\??(?:\[\])?\??(?:\s*\&)?)\s+
        (?P<name>[A-Za-z_]\w*)\s*\(
        (?P<args>[^)]*)\)
        \s*\{
    """,
    re.VERBOSE | re.MULTILINE,
)


def split_args(args: str) -> List[Tuple[str, str, bool]]:
    args = args.strip()
    if not args:
        return []
    pieces = [p.strip() for p in args.split(",")]
    result = []
    for piece in pieces:
        if "=" in piece:
            piece = piece.split("=", 1)[0].strip()
        had_marker = False
        m = re.match(r"^\[\[\s*Nullable\s*\]\]\s*(.*)$", piece)
        if m:
            had_marker = True
            piece = m.group(1).strip()
        tokens = piece.split()
        if len(tokens) < 2:
            continue
        name = tokens[-1].lstrip("&")
        type_part = " ".join(tokens[:-1]).rstrip("&").strip()
        result.append((type_part, name, had_marker))
    return result


def extract_body(content: str, brace_pos: int) -> Tuple[str, int]:
    depth = 0
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
                    return content[brace_pos + 1:i], i
        i += 1
    return content[brace_pos + 1:i], i


def parse_attrs(attrs_text: str) -> List[str]:
    return [m.group(1) for m in re.finditer(r"\[\[\s*([A-Za-z_]\w*)", attrs_text)]


def find_namespace(content: str) -> str:
    m = re.search(r"^\s*namespace\s+([A-Za-z_]\w*)\s*\{", content, re.MULTILINE)
    return m.group(1) if m else ""


class FuncInfo:
    __slots__ = ("file", "line", "namespace", "name", "attrs",
                 "params", "body", "ret_type",
                 "body_start", "body_end", "head_start", "head_end")

    def __init__(self, file, line, namespace, name, attrs, params, body,
                 ret_type, body_start, body_end, head_start, head_end):
        self.file = file
        self.line = line
        self.namespace = namespace
        self.name = name
        self.attrs = attrs
        self.params = params
        self.body = body
        self.body_start = body_start
        self.body_end = body_end
        self.ret_type = ret_type
        self.head_start = head_start
        self.head_end = head_end

    def key(self):
        return (self.namespace, self.name)


def collect_functions(file_path: Path, text: str) -> List[FuncInfo]:
    ns = find_namespace(text)
    funcs = []
    pos = 0
    while True:
        m = FUNC_RE.search(text, pos)
        if not m:
            break
        head_start = m.start()
        brace_pos = m.end() - 1
        body, end_brace = extract_body(text, brace_pos)
        pos = end_brace + 1

        name = m.group("name")
        ret_type = m.group("ret").strip()
        if name in CONTROL_KEYWORDS:
            continue
        ret_type_clean = re.sub(r"^\[\[\s*Nullable\s*\]\]\s*", "", ret_type)
        if ret_type_clean.split()[0] in CONTROL_KEYWORDS:
            continue

        attrs = parse_attrs(m.group("attrs"))
        params = split_args(m.group("args"))
        line_no = text.count("\n", 0, head_start) + 1
        funcs.append(FuncInfo(
            file=file_path, line=line_no, namespace=ns, name=name,
            attrs=attrs, params=params, body=body, ret_type=ret_type_clean,
            body_start=brace_pos, body_end=end_brace,
            head_start=head_start, head_end=brace_pos,
        ))
    return funcs


def param_has_null_check(body: str, name: str) -> bool:
    """True if body checks param for null, NOT counting Assert(param != null, ...) lines."""
    eq = re.search(rf"\b{re.escape(name)}\s*==\s*null\b", body)
    ne = re.search(rf"\b{re.escape(name)}\s*!=\s*null\b", body)
    if not (eq or ne):
        return False
    body_no_assert = re.sub(
        rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;?",
        "",
        body,
    )
    eq2 = re.search(rf"\b{re.escape(name)}\s*==\s*null\b", body_no_assert)
    ne2 = re.search(rf"\b{re.escape(name)}\s*!=\s*null\b", body_no_assert)
    return bool(eq2 or ne2)


def has_two_branch_handling(body: str, name: str) -> bool:
    """A parameter is "meaningfully nullable" if the body branches on null vs
    non-null with substantive logic in both arms. Specifically (any of):
    - `param != null ? A : B` ternary (simple or composite condition),
    - `param != null &&` clause inside any return / assignment expression
      that has a fallback for the null case via `&&` short-circuit,
    - `if (... param ==/!= null ...) { ... } else { ... }`.
    Asserts are stripped first so that `Assert(param != null, ...)` doesn't
    trigger a false positive.
    """
    body_no_assert = re.sub(
        rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;?",
        "",
        body,
    )

    if re.search(rf"\b{re.escape(name)}\s*!=\s*null\s*\?", body_no_assert):
        return True
    if re.search(rf"\b{re.escape(name)}\s*==\s*null\s*\?", body_no_assert):
        return True
    # `param != null &&` clause — usually inside a return/condition where the
    # null case short-circuits to false, the non-null case proceeds.
    if re.search(rf"\b{re.escape(name)}\s*!=\s*null\s*&&", body_no_assert):
        return True

    # `if (... param == null ...) { ... } else ...` pattern.
    i = 0
    while i < len(body_no_assert):
        m = re.compile(rf"\bif\s*\(").search(body_no_assert, i)
        if not m:
            break
        op = m.end() - 1
        cp = find_matching_paren_simple(body_no_assert, op)
        if cp is None:
            break
        cond = body_no_assert[op + 1:cp]
        if re.search(rf"\b{re.escape(name)}\s*(==|!=)\s*null\b", cond):
            j = cp + 1
            while j < len(body_no_assert) and body_no_assert[j] in " \t\r\n":
                j += 1
            if j < len(body_no_assert) and body_no_assert[j] == "{":
                bc = find_matching_brace(body_no_assert, j)
                if bc is None:
                    break
                k = bc + 1
                while k < len(body_no_assert) and body_no_assert[k] in " \t\r\n":
                    k += 1
                if body_no_assert[k:k + 4] == "else" and (k + 4 == len(body_no_assert) or not (body_no_assert[k + 4].isalnum() or body_no_assert[k + 4] == "_")):
                    return True
                i = bc + 1
                continue
        i = cp + 1
    return False


def has_return_null(body: str) -> bool:
    return bool(re.search(r"\breturn\s+null\s*;", body))


def split_top_level_commas(s: str) -> List[Tuple[int, int]]:
    """Return list of (start_offset, end_offset) for top-level comma-separated pieces."""
    pieces = []
    depth_paren = 0
    depth_brk = 0
    depth_brace = 0
    angle = 0
    in_string = False
    in_char = False
    start = 0
    i = 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if in_string:
            if c == "\\":
                i += 2; continue
            if c == '"':
                in_string = False
        elif in_char:
            if c == "\\":
                i += 2; continue
            if c == "'":
                in_char = False
        elif c == '"':
            in_string = True
        elif c == "'":
            in_char = True
        elif c == "(": depth_paren += 1
        elif c == ")": depth_paren -= 1
        elif c == "[": depth_brk += 1
        elif c == "]": depth_brk -= 1
        elif c == "{": depth_brace += 1
        elif c == "}": depth_brace -= 1
        elif c == "<": angle += 1
        elif c == ">": angle -= 1
        elif c == "," and depth_paren == 0 and depth_brk == 0 and depth_brace == 0 and angle == 0:
            pieces.append((start, i))
            start = i + 1
        i += 1
    pieces.append((start, len(s)))
    return pieces


def find_matching_paren(text: str, open_pos: int) -> Optional[int]:
    depth = 0
    i = open_pos
    n = len(text)
    in_string = False
    in_char = False
    while i < n:
        c = text[i]
        if in_string:
            if c == "\\":
                i += 2; continue
            if c == '"':
                in_string = False
        elif in_char:
            if c == "\\":
                i += 2; continue
            if c == "'":
                in_char = False
        elif c == '"':
            in_string = True
        elif c == "'":
            in_char = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def find_callers(corpus: Dict[Path, str], target_ns: str, target_name: str, exclude: Tuple[Path, int]):
    """Return list of (caller_file, caller_line, arg_texts)."""
    pattern_qual = re.compile(rf"(?<![\w:]){re.escape(target_ns)}::{re.escape(target_name)}\s*\(") if target_ns else None
    pattern_unqual = re.compile(rf"(?<![\w:.@]){re.escape(target_name)}\s*\(")
    results = []
    for f, text in corpus.items():
        file_ns = find_namespace(text)
        if pattern_qual is not None:
            for m in pattern_qual.finditer(text):
                end_paren = find_matching_paren(text, m.end() - 1)
                if end_paren is None:
                    continue
                args_txt = text[m.end():end_paren]
                pieces = split_top_level_commas(args_txt)
                args = [args_txt[s:e].strip() for s, e in pieces if args_txt[s:e].strip()]
                line_no = text.count("\n", 0, m.start()) + 1
                results.append((f, line_no, args))
        if file_ns == target_ns or not target_ns:
            for m in pattern_unqual.finditer(text):
                if text[max(0, m.start()-2):m.start()].endswith("::"):
                    continue
                end_paren = find_matching_paren(text, m.end() - 1)
                if end_paren is None:
                    continue
                after = text[end_paren + 1:end_paren + 64].lstrip()
                # Skip function DEFINITIONS only (i.e. `<sig>) {`). A call
                # statement also ends with `;` after `)` — do NOT skip it.
                if after.startswith("{"):
                    continue
                args_txt = text[m.end():end_paren]
                pieces = split_top_level_commas(args_txt)
                args = [args_txt[s:e].strip() for s, e in pieces if args_txt[s:e].strip()]
                line_no = text.count("\n", 0, m.start()) + 1
                if (f, line_no) == exclude:
                    continue
                results.append((f, line_no, args))
    return results


def is_func_address_taken(corpus: Dict[Path, str], name: str) -> bool:
    """The function name is mentioned as a delegate target or passed as a bare-id arg."""
    if re.search(rf"@\s*(?:[A-Za-z_]\w*::)?{re.escape(name)}\b",
                 "\n".join(corpus.values())):
        return True
    pattern_in_args = re.compile(rf"[,(]\s*{re.escape(name)}\s*[,)]")
    if pattern_in_args.search("\n".join(corpus.values())):
        return True
    return False


def is_pure_ident(expr: str) -> Optional[str]:
    """If expr is a bare identifier, return it; else None."""
    s = expr.strip()
    if re.match(r"^[A-Za-z_]\w*$", s):
        return s
    return None


def compute_decisions_with_propagation(corpus: Dict[Path, str], funcs: List[FuncInfo]):
    """Returns: dict info_id -> ({param_name: 'keep'}, return_decision)."""

    # Index by (ns, name)
    by_key: Dict[Tuple[str, str], List[FuncInfo]] = {}
    for f in funcs:
        by_key.setdefault(f.key(), []).append(f)

    # For caller-finding, cache callers per (ns, name)
    callers_cache: Dict[Tuple[str, str], list] = {}
    def callers_of(info: FuncInfo):
        k = info.key()
        if k not in callers_cache:
            callers_cache[k] = find_callers(corpus, info.namespace, info.name, exclude=(info.file, info.line))
        return callers_cache[k]

    addr_taken_cache: Dict[str, bool] = {}
    def addr_taken(name: str) -> bool:
        if name not in addr_taken_cache:
            addr_taken_cache[name] = is_func_address_taken(corpus, name)
        return addr_taken_cache[name]

    # KEEP set: (info_id, param_name)
    keep_set: Set[Tuple[int, str]] = set()

    # Pre-compute which params have null checks
    param_check_map: Dict[int, Set[str]] = {}
    for info in funcs:
        check_set = set()
        for tp, pname, _ in info.params:
            tp_base = re.sub(r"\?+$", "", tp).strip()
            tp_base = re.sub(r"\[\]\??$", "", tp_base).strip()
            tp_base = re.sub(r"^(const|inout|in|out)\s+", "", tp_base).strip()
            tp_bare = tp_base.rsplit("::", 1)[-1]
            if tp_base in PRIMITIVE_TYPES:
                continue
            # `?` carries runtime semantics only for entity types. For other
            # ref-type/script-class handles the marker is documentation-only,
            # and validate_nullable.py forbids it. Don't even consider these.
            if tp_bare not in SCRIPT_ENTITY_TYPES:
                continue
            if param_has_null_check(info.body, pname):
                check_set.add(pname)
        param_check_map[id(info)] = check_set

    # Initial KEEP: direct evidence + body has two-branch handling.
    # Per the design rule: a parameter is Nullable ONLY when the body
    # meaningfully handles BOTH null and non-null cases (not just early-
    # exits on null). Early-exit-on-null patterns are guards that should
    # be removed; the contract is "caller must not pass null".
    for info in funcs:
        for pname in param_check_map[id(info)]:
            if not has_two_branch_handling(info.body, pname):
                # Early-exit / guard-only pattern. Per rule, never Nullable.
                continue
            engine_invoked = any(a in ENGINE_INVOKED_ATTRS for a in info.attrs)
            if engine_invoked:
                keep_set.add((id(info), pname))
                continue
            if addr_taken(info.name):
                keep_set.add((id(info), pname))
                continue
            calls = callers_of(info)
            param_idx = next((i for i, p in enumerate(info.params) if p[1] == pname), -1)
            if param_idx < 0:
                continue
            relevant = [c for c in calls if len(c[2]) > param_idx]
            if not relevant:
                keep_set.add((id(info), pname))
                continue
            if any(c[2][param_idx].strip() == "null" for c in relevant):
                keep_set.add((id(info), pname))

    # Map (caller file path, line) -> caller's FuncInfo by scanning funcs.
    # We need to know: for a call at file X line Y, which FuncInfo's body contains it?
    # Simpler: build a sorted list of (file, body_start, body_end, info) and binary
    # search by offset. But we need to know which function CONTAINS the call.
    by_file_funcs: Dict[Path, List[FuncInfo]] = {}
    for info in funcs:
        by_file_funcs.setdefault(info.file, []).append(info)
    for v in by_file_funcs.values():
        v.sort(key=lambda i: i.body_start)

    def find_containing_func(file: Path, line: int, text: str) -> Optional[FuncInfo]:
        """Given a caller's file and source line, find the FuncInfo whose body contains it."""
        # Convert line to offset
        offset = 0
        cur_line = 1
        for i, ch in enumerate(text):
            if cur_line == line:
                offset = i
                break
            if ch == "\n":
                cur_line += 1
        for info in by_file_funcs.get(file, []):
            if info.body_start <= offset <= info.body_end:
                return info
        return None

    # Propagation. Only upgrade to KEEP if the body genuinely two-branches
    # on null vs non-null (same rule as initial pass).
    changed = True
    iteration = 0
    while changed and iteration < 20:
        changed = False
        iteration += 1
        for info in funcs:
            for pname in param_check_map[id(info)]:
                if (id(info), pname) in keep_set:
                    continue
                if not has_two_branch_handling(info.body, pname):
                    continue
                param_idx = next((i for i, p in enumerate(info.params) if p[1] == pname), -1)
                if param_idx < 0:
                    continue
                calls = callers_of(info)
                relevant = [c for c in calls if len(c[2]) > param_idx]
                for cf, cline, cargs in relevant:
                    arg = cargs[param_idx].strip()
                    bare = is_pure_ident(arg)
                    if not bare:
                        continue
                    caller_info = find_containing_func(cf, cline, corpus[cf])
                    if caller_info is None:
                        continue
                    if (id(caller_info), bare) in keep_set:
                        keep_set.add((id(info), pname))
                        changed = True
                        break

    # Build final decisions.
    #
    # The script-side analyzer mirrors the engine-side rule: it does NOT add
    # or remove `?` markers — those are author decisions, and the heuristic
    # for "this param meaningfully two-branches on null" is reliable for the
    # author's first pass but causes churn when re-run against a curated
    # codebase. The analyzer's only remaining job is to strip dead null
    # guards on params whose declared type is NON-nullable (no `?` suffix
    # AND no legacy `[[Nullable]]` marker), since the engine boundary
    # (NativeDataProvider::CheckArgNotNull) will throw before the body runs
    # for entity-pointer args, and the convention itself enforces non-null
    # for everything else.
    decisions = {}
    for info in funcs:
        d = {"params": {}, "return": "none"}
        for tp, pname, had_marker in info.params:
            tp_trim = tp.rstrip()
            param_is_nullable = had_marker or tp_trim.endswith("?")
            if param_is_nullable:
                # Author marked nullable — preserve marker AND body. No edit.
                continue
            if pname not in param_check_map[id(info)]:
                # No null check in body for this param — nothing to strip.
                continue
            d["params"][pname] = "remove"
        decisions[id(info)] = (info, d)
    return decisions


def find_param_name_pos(text: str, args_start: int, args_end: int, pname: str) -> Optional[int]:
    """Return the offset where the parameter's name identifier begins."""
    pieces = []
    depth = 0
    angle = 0
    start = args_start
    i = args_start
    while i < args_end:
        c = text[i]
        if c == "(": depth += 1
        elif c == ")": depth -= 1
        elif c == "[": depth += 1
        elif c == "]": depth -= 1
        elif c == "<": angle += 1
        elif c == ">": angle -= 1
        elif c == "," and depth == 0 and angle == 0:
            pieces.append((start, i))
            start = i + 1
        i += 1
    pieces.append((start, args_end))

    for (s, e) in pieces:
        piece_text = text[s:e]
        no_default = piece_text.split("=", 1)[0]
        # Find LAST identifier match before `=`
        last_match = None
        for m in re.finditer(r"\b[A-Za-z_]\w*\b", no_default):
            last_match = m
        if last_match is None:
            continue
        if last_match.group() != pname:
            continue
        return s + last_match.start()
    return None


def compute_param_type_end_pos(text: str, args_start: int, args_end: int, pname: str) -> Optional[int]:
    """Position right after the parameter's type tokens, EXCLUDING any
    existing `?` suffix. Inserting `?` here turns `Type name` into
    `Type? name`; inserting at this position when text[pos] is already
    `?` is a no-op (idempotent)."""
    name_pos = find_param_name_pos(text, args_start, args_end, pname)
    if name_pos is None:
        return None
    pos = name_pos
    # Walk back over whitespace
    while pos > args_start and text[pos - 1] in " \t":
        pos -= 1
    # Walk back over any existing `?` suffix(es)
    while pos > args_start and text[pos - 1] == "?":
        pos -= 1
    return pos


def compute_return_name_pos(text: str, info: FuncInfo) -> Optional[int]:
    """Return the offset where the function name begins in the head."""
    open_paren = text.find("(", info.head_start)
    if open_paren == -1:
        return None
    # Walk back from `(` over whitespace, then collect the identifier
    i = open_paren
    while i > info.head_start and text[i - 1] in " \t":
        i -= 1
    end = i
    while i > info.head_start and (text[i - 1].isalnum() or text[i - 1] == "_"):
        i -= 1
    if i == end:
        return None
    return i


def compute_return_type_end_pos(text: str, info: FuncInfo) -> Optional[int]:
    """Position right after the return type, EXCLUDING any existing `?`."""
    name_pos = compute_return_name_pos(text, info)
    if name_pos is None:
        return None
    pos = name_pos
    while pos > info.head_start and text[pos - 1] in " \t\r\n":
        pos -= 1
    while pos > info.head_start and text[pos - 1] == "?":
        pos -= 1
    return pos


def find_all_nullable_attr_ranges_in_head(text: str, info: FuncInfo, args_start: int, args_end: int) -> List[Tuple[int, int]]:
    """Return list of (start, end) ranges in the function head that cover a
    `[[Nullable]]` attribute marker (legacy syntax) plus trailing whitespace.
    Both return-type-side (before function name) and parameter-list-side
    (between `(` and `)`) occurrences are detected."""
    ranges: List[Tuple[int, int]] = []
    # Scan head_start..head_end for `[[ Nullable ]]` patterns
    i = info.head_start
    while i < info.head_end - 3:
        if text[i] == "[" and i + 1 < info.head_end and text[i + 1] == "[":
            j = i + 2
            while j + 1 < info.head_end and not (text[j] == "]" and text[j + 1] == "]"):
                j += 1
            if j + 1 < info.head_end and text[j] == "]" and text[j + 1] == "]":
                inner = text[i + 2:j].strip()
                end_attr = j + 2
                if inner == "Nullable":
                    e = end_attr
                    while e < info.head_end and text[e] in " \t":
                        e += 1
                    # If the marker is on its own line (formatter style), also
                    # consume the trailing newline.
                    if e < info.head_end and text[e] == "\n":
                        e += 1
                    ranges.append((i, e))
                i = end_attr
                continue
        i += 1
    return ranges


# --- Body cleanup logic ---

def find_statement_range_around(body: str, anchor_pos: int) -> Tuple[int, int]:
    """Given an offset inside an `if (...)` block at the top level of a body,
    find the full statement extent: from the start of the indented `if` keyword
    to the end of the matching closing `}` (or `;` for single-stmt forms).
    Returns (start, end_exclusive).
    """
    # Walk back to start of line
    start = anchor_pos
    while start > 0 and body[start - 1] != "\n":
        start -= 1
    # Now find matching `}` for the if's block
    # Find the `(` of the if
    op = body.find("(", anchor_pos)
    if op == -1:
        return (start, anchor_pos)
    close_paren = find_matching_paren_simple(body, op)
    if close_paren is None:
        return (start, anchor_pos)
    # Skip whitespace after )
    k = close_paren + 1
    while k < len(body) and body[k] in " \t\r\n":
        k += 1
    if k < len(body) and body[k] == "{":
        end = find_matching_brace(body, k)
        if end is None:
            return (start, anchor_pos)
        # include trailing newline
        e = end + 1
        while e < len(body) and body[e] in " \t":
            e += 1
        if e < len(body) and body[e] == "\n":
            e += 1
        return (start, e)
    # Single-statement form: find next `;` at depth 0
    depth = 0
    j = k
    while j < len(body):
        c = body[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == ";" and depth == 0:
            e = j + 1
            while e < len(body) and body[e] in " \t":
                e += 1
            if e < len(body) and body[e] == "\n":
                e += 1
            return (start, e)
        j += 1
    return (start, anchor_pos)


def find_matching_paren_simple(text: str, open_pos: int) -> Optional[int]:
    depth = 0
    i = open_pos
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def find_matching_brace(text: str, open_pos: int) -> Optional[int]:
    depth = 0
    i = open_pos
    in_string = False
    in_char = False
    in_line_comment = False
    in_block_comment = False
    while i < len(text):
        c = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_line_comment:
            if c == "\n":
                in_line_comment = False
        elif in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            if c == "\\":
                i += 2; continue
            if c == '"':
                in_string = False
        elif in_char:
            if c == "\\":
                i += 2; continue
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
    return None


def clean_body_for_non_nullable_params(body: str, param_names: List[str]) -> str:
    """Apply aggressive cleanup of null-related defensive code for the given params."""
    text = body

    for name in param_names:
        # 1. Remove `Assert(name != null[, ...]);` lines including trailing newline
        text = re.sub(
            rf"^[ \t]*Assert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;[ \t]*\r?\n",
            "",
            text,
            flags=re.MULTILINE,
        )
        # Also handle inline asserts (no trailing newline, but keep going)
        text = re.sub(
            rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;[ \t]*",
            "",
            text,
        )

        # 2. Standalone `if (name == null) { ... }` — drop entire block.
        # If followed by `else { ... }` (or `else if`), strip the if-block
        # AND the `else` keyword, leaving the else-branch as the main path.
        pat = re.compile(rf"\bif\s*\(\s*{re.escape(name)}\s*==\s*null\s*\)\s*\{{")
        offset = 0
        while True:
            m = pat.search(text, offset)
            if not m:
                break
            brace_open = m.end() - 1
            brace_close = find_matching_brace(text, brace_open)
            if brace_close is None:
                break
            line_start = text.rfind("\n", 0, m.start()) + 1
            j = brace_close + 1
            while j < len(text) and text[j] in " \t\r\n":
                j += 1
            else_end = None
            if text[j:j + 4] == "else" and (j + 4 == len(text) or (not text[j + 4].isalnum() and text[j + 4] != "_")):
                else_end = j + 4
                # Skip whitespace after `else` so the next token starts cleanly
                while else_end < len(text) and text[else_end] in " \t":
                    else_end += 1
            if else_end is not None:
                # Remove from line_start through end of `else ` keyword.
                # The else-body (or `else if`) starts at else_end and remains.
                text = text[:line_start] + text[else_end:]
                offset = line_start
            else:
                e = brace_close + 1
                while e < len(text) and text[e] in " \t":
                    e += 1
                if e < len(text) and text[e] == "\n":
                    e += 1
                text = text[:line_start] + text[e:]
                offset = line_start

        # Same but for `name != null` form negated — rare but possible:
        # `if (name != null) { ... }` — we should NOT remove since this is
        # legitimate "do work if not null" pattern. Only remove if param is
        # non-nullable AND the body just does `return ...;` (defensive). For
        # safety, skip — the user said remove defensive checks; we focus on
        # `== null` guards.

        # 3. `name == null || ` clauses inside conditions:
        text = re.sub(rf"\b{re.escape(name)}\s*==\s*null\s*\|\|\s*", "", text)
        text = re.sub(rf"\s*\|\|\s*{re.escape(name)}\s*==\s*null\b", "", text)

        # 4. `name != null && ` clauses:
        text = re.sub(rf"\b{re.escape(name)}\s*!=\s*null\s*&&\s*", "", text)
        text = re.sub(rf"\s*&&\s*{re.escape(name)}\s*!=\s*null\b", "", text)

        # 5. `name != null ? A : B` ternary substitution is intentionally
        # NOT performed here. Balanced-paren parsing is required for safety
        # (regex easily eats the closing `)` of an enclosing expression),
        # and these are best handled manually if present.

    return text


def apply_to_file(file_text: str, infos: List[FuncInfo], decisions: Dict) -> str:
    """Apply all decisions producing minimal diffs that preserve formatting.

    The script-side applier only strips dead defensive null guards in
    function bodies. It never touches function heads (no marker add/remove).
    Decisions carry `params: {name: "remove"}` for params whose body has a
    null check but no `?` marker — codegen / convention guarantees those
    are non-null, so the guards are dead.
    """
    new_text = file_text
    funcs_sorted = sorted(infos, key=lambda i: -i.head_start)
    for info in funcs_sorted:
        if id(info) not in decisions:
            continue
        _, d = decisions[id(info)]

        remove_params = [p for p, v in d["params"].items() if v == "remove"]
        if not remove_params:
            continue

        body_start = info.body_start
        body_end = info.body_end

        body_inner = new_text[body_start + 1:body_end]
        new_body = body_inner
        for name in remove_params:
            new_body = re.sub(
                rf"^[ \t]*Assert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;[ \t]*\r?\n",
                "",
                new_body,
                flags=re.MULTILINE,
            )
            new_body = re.sub(
                rf"\bAssert\(\s*{re.escape(name)}\s*!=\s*null\b[^)]*\)\s*;[ \t]*",
                "",
                new_body,
            )
        new_body = clean_body_for_non_nullable_params(new_body, remove_params)
        new_text = new_text[:body_start + 1] + new_body + new_text[body_end:]

    return new_text


def main():
    dry_run = "--dry-run" in sys.argv
    report_only = "--report-only" in sys.argv
    check_mode = "--check" in sys.argv
    if check_mode:
        dry_run = True

    files = sorted(SCRIPTS_ROOT.rglob("*.fos"))
    files = [f for f in files if f.name not in ("GuiScreens.fos", "Content.fos")]
    corpus = {f: f.read_text(encoding="utf-8", errors="replace") for f in files}

    file_funcs: Dict[Path, List[FuncInfo]] = {}
    all_funcs: List[FuncInfo] = []
    for f, text in corpus.items():
        funcs = collect_functions(f, text)
        file_funcs[f] = funcs
        all_funcs.extend(funcs)

    decisions = compute_decisions_with_propagation(corpus, all_funcs)

    total_keep_param = 0
    total_remove_param = 0
    total_keep_ret = 0
    asserts_removable = 0
    for info_id, (info, d) in decisions.items():
        for pname, v in d["params"].items():
            if v == "keep":
                total_keep_param += 1
            else:
                total_remove_param += 1
        if d["return"] == "keep":
            total_keep_ret += 1
        # Count asserts on non-Nullable params
        keep = {p for p, v in d["params"].items() if v == "keep"}
        for tp, pname, _ in info.params:
            if pname in keep:
                continue
            tp_base = re.sub(r"\?+$", "", tp).strip()
            tp_base = re.sub(r"\[\]\??$", "", tp_base).strip()
            tp_base = re.sub(r"^(const|inout|in|out)\s+", "", tp_base).strip()
            if tp_base in PRIMITIVE_TYPES:
                continue
            if re.search(rf"\bAssert\(\s*{re.escape(pname)}\s*!=\s*null\b", info.body):
                asserts_removable += 1

    print("=== Summary ===")
    print(f"Files scanned: {len(files)}")
    print(f"Functions analyzed: {len(decisions)}")
    print(f"Parameters marked [[Nullable]] (KEEP): {total_keep_param}")
    print(f"Parameters with checks REMOVED: {total_remove_param}")
    print(f"Return values marked [[Nullable]]: {total_keep_ret}")
    print(f"Asserts(param != null) removable: {asserts_removable}")
    print()

    if report_only:
        print("=== KEEP (param [[Nullable]]) ===")
        c = 0
        for info_id, (info, d) in decisions.items():
            for pname, v in d["params"].items():
                if v == "keep":
                    rel = info.file.relative_to(ROOT)
                    print(f"  {rel}:{info.line} {info.namespace}::{info.name}({pname})")
                    c += 1
                    if c >= 50:
                        print(f"  ... ({total_keep_param - 50} more)"); break
            if c >= 50: break
        return

    changes = 0
    for f in files:
        infos = file_funcs[f]
        if not infos:
            continue
        text = corpus[f]
        new_text = apply_to_file(text, infos, decisions)
        if new_text != text:
            changes += 1
            if not dry_run:
                f.write_text(new_text, encoding="utf-8")
    print(f"Files changed: {changes}")
    if dry_run:
        print("(dry-run - no files written)")
    if check_mode and changes > 0:
        print("ERROR: nullable markers/cleanups out of date; run `python Tools/NullableEstimate/apply_nullables.py` and commit the result", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
