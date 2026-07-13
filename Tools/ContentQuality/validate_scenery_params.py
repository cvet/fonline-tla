#!/usr/bin/env python3
"""Validate known-safe ``SceneryParams`` contracts in authored TLA maps.

The engine stores ``SceneryParams`` as ``hstring[]``. Resource baking therefore
accepts arbitrary tokens and cannot catch an integer slot containing a symbolic
value, a malformed legacy ``@N`` entry, or a wrong number of parameters. This
validator parses each ``[Item]`` section in ``Maps/*.fomap`` and applies schemas
only to contracts whose meaning is known.

Unknown scripts are ignored. ``Scenery::TransferToMap`` is deliberately
reported as a warning because its first parameter is historically ambiguous
(map id versus location id); warnings never affect the exit code.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"

INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1

SECTION_RE = re.compile(r"^\s*\[([^]]+)]\s*$")
FIELD_RE = re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_.$]*)\s*=\s*(.*?)\s*$")
CANONICAL_INT_RE = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
CONTENT_ID_PART_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")

EXPECTED_ELEVATOR_MAP_COUNT = {
    0: 4,
    1: 2,
    2: 3,
    3: 2,
    4: 3,
    5: 2,
    6: 3,
    7: 3,
    8: 3,
}


@dataclass(frozen=True)
class MapField:
    value: str
    line: int


@dataclass
class MapItem:
    path: Path
    section_line: int
    fields: dict[str, MapField] = field(default_factory=dict)

    def get(self, name: str) -> MapField | None:
        return self.fields.get(name)

    @property
    def context(self) -> str:
        parts: list[str] = []
        proto = self.get("$Proto")
        hex_field = self.get("Hex")
        if proto is not None:
            parts.append(f"proto {proto.value}")
        if hex_field is not None:
            parts.append(f"hex {hex_field.value}")
        return ", ".join(parts) if parts else "item"


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: Path
    line: int
    script: str
    context: str
    message: str


@dataclass
class ValidationResult:
    project_root: Path
    map_files: int = 0
    item_sections: int = 0
    contract_items: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == SEVERITY_WARNING]


def parse_map_items(path: Path) -> list[MapItem]:
    """Parse item sections without interpreting unrelated map properties."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    items: list[MapItem] = []
    current: MapItem | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(line)
        if section_match is not None:
            if current is not None:
                items.append(current)
            current = MapItem(path=path, section_line=line_number) if section_match.group(1) == "Item" else None
            continue

        if current is None:
            continue

        field_match = FIELD_RE.match(line)
        if field_match is None:
            continue

        current.fields[field_match.group(1)] = MapField(field_match.group(2), line_number)

    if current is not None:
        items.append(current)

    return items


def tokenize_params(value: str) -> list[str] | None:
    try:
        return shlex.split(value, comments=False, posix=True)
    except ValueError:
        return None


def parse_canonical_int(token: str, *, allow_legacy_at: bool = False) -> int | None:
    """Parse a canonical signed int32, optionally accepting legacy ``@N``."""
    text = token
    if allow_legacy_at and text.startswith("@"):
        text = text[1:]

    if CANONICAL_INT_RE.fullmatch(text) is None:
        return None

    value = int(text, 10)
    if value < INT32_MIN or value > INT32_MAX or text != str(value):
        return None
    return value


def is_content_id(token: str, namespace: str, *, allow_zero: bool = False) -> bool:
    if allow_zero and token == "0":
        return True
    prefix = f"Content::{namespace}::"
    value = token[len(prefix):] if token.startswith(prefix) else token
    return CONTENT_ID_PART_RE.fullmatch(value) is not None


class ItemValidator:
    def __init__(self, project_root: Path, item: MapItem, script: str, params_field: MapField | None):
        self.project_root = project_root
        self.item = item
        self.script = script
        self.params_field = params_field
        self.findings: list[Finding] = []

    def add(self, severity: str, code: str, message: str, *, line: int | None = None) -> None:
        self.findings.append(
            Finding(
                severity=severity,
                code=code,
                path=self.item.path.relative_to(self.project_root),
                line=line or (self.params_field.line if self.params_field is not None else self.item.section_line),
                script=self.script,
                context=self.item.context,
                message=message,
            )
        )

    def error(self, code: str, message: str) -> None:
        self.add(SEVERITY_ERROR, code, message)

    def warning(self, code: str, message: str) -> None:
        self.add(SEVERITY_WARNING, code, message)

    def params(self) -> list[str] | None:
        if self.params_field is None:
            self.error("missing-params", "required SceneryParams field is missing")
            return None
        params = tokenize_params(self.params_field.value)
        if params is None:
            self.error("invalid-tokenization", "SceneryParams contains an unterminated quote or escape")
        return params

    def exact_arity(self, expected: int) -> list[str] | None:
        params = self.params()
        if params is None:
            return None
        if len(params) != expected:
            self.error("arity", f"expected {expected} parameter(s), found {len(params)}")
            return None
        return params

    def integer(
        self,
        token: str,
        name: str,
        *,
        allow_legacy_at: bool = False,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int | None:
        value = parse_canonical_int(token, allow_legacy_at=allow_legacy_at)
        form = "canonical integer or legacy @N" if allow_legacy_at else "canonical integer"
        if value is None:
            self.error("integer", f"{name} must be a {form}, got {token!r}")
            return None
        if minimum is not None and value < minimum:
            self.error("range", f"{name} must be >= {minimum}, got {value}")
        if maximum is not None and value > maximum:
            self.error("range", f"{name} must be <= {maximum}, got {value}")
        return value


def validate_elevator(check: ItemValidator) -> None:
    params = check.exact_arity(5)
    if params is None:
        return

    check.integer(params[0], "entry", minimum=0)
    elevator_type = check.integer(params[1], "elevator type", minimum=0, maximum=8)

    map_count = 0
    seen_zero = False
    for index, token in enumerate(params[2:], start=1):
        if token == "0":
            seen_zero = True
            continue
        if seen_zero:
            check.error("sentinel-order", f"map slot {index} follows a 0 sentinel")
        if not is_content_id(token, "Map"):
            check.error(
                "map-id",
                f"map slot {index} must be a bare map id, Content::Map id, or 0 sentinel, got {token!r}",
            )
            continue
        map_count += 1

    if elevator_type in EXPECTED_ELEVATOR_MAP_COUNT:
        expected = EXPECTED_ELEVATOR_MAP_COUNT[elevator_type]
        if map_count != expected:
            check.error("map-count", f"elevator type {elevator_type} requires {expected} map(s), found {map_count}")


def validate_elevator4(check: ItemValidator) -> None:
    params = check.exact_arity(5)
    if params is None:
        return

    check.integer(params[0], "entry", minimum=0)
    for index, token in enumerate(params[1:], start=1):
        if token == "0" or not is_content_id(token, "Map"):
            check.error(
                "map-id",
                f"four-floor elevator map slot {index} must be a bare or Content::Map id, got {token!r}",
            )


def validate_numeric_role(check: ItemValidator) -> None:
    params = check.exact_arity(1)
    if params is not None:
        check.integer(params[0], "NPC role", minimum=1)


def validate_legacy_entry(check: ItemValidator) -> None:
    params = check.exact_arity(1)
    if params is not None:
        check.integer(params[0], "entry", allow_legacy_at=True, minimum=0)


def validate_energy_barrier_terminal(check: ItemValidator) -> None:
    params = check.exact_arity(3)
    if params is None:
        return
    check.integer(params[0], "barrier network number", minimum=1)
    check.integer(params[1], "hack bonus", minimum=-100, maximum=100)
    check.integer(params[2], "hit bonus", minimum=-100, maximum=100)


def validate_android_box(check: ItemValidator) -> None:
    params = check.exact_arity(1)
    if params is not None:
        check.integer(params[0], "find chance", minimum=0, maximum=100)


def validate_npc_dialog(check: ItemValidator) -> None:
    params = check.exact_arity(5)
    if params is None:
        return

    check.integer(params[0], "NPC role", minimum=1)
    first_text = check.integer(params[1], "first text id", minimum=1)
    last_text = check.integer(params[2], "last text id", minimum=1)
    check.integer(params[3], "wait seconds", minimum=1, maximum=60)
    check.integer(params[4], "radius", minimum=1, maximum=100)
    if first_text is not None and last_text is not None and first_text > last_text:
        check.error("text-order", f"first text id {first_text} must not exceed last text id {last_text}")


def validate_scenery_door(check: ItemValidator) -> None:
    params = check.exact_arity(2)
    if params is None:
        return
    check.integer(params[0], "door entry", allow_legacy_at=True, minimum=0)
    check.integer(params[1], "open flag", minimum=0, maximum=1)


def validate_scenery_dialog(check: ItemValidator) -> None:
    params = check.exact_arity(1)
    if params is None:
        return
    if not is_content_id(params[0], "Dialog", allow_zero=True):
        check.error(
            "dialog-id",
            f"dialog must be a bare dialog id, Content::Dialog id, or 0 sentinel, got {params[0]!r}",
        )


def warn_ambiguous_transfer(check: ItemValidator) -> None:
    check.warning(
        "ambiguous-transfer",
        "Scenery::TransferToMap has a known ambiguous map/location id contract; "
        "parameters are reported but not schema-validated",
    )


Validator = Callable[[ItemValidator], None]

CONTRACTS: dict[str, Validator] = {
    "Trigger::Elevator": validate_elevator,
    "Trigger::Elevator4": validate_elevator4,
    "Trigger::Warn": validate_numeric_role,
    "Trigger::Attack": validate_numeric_role,
    "Trigger::AttackStop": validate_numeric_role,
    "Trigger::DialogNpc": validate_numeric_role,
    "Trigger::DoorOpen": validate_legacy_entry,
    "Trigger::DoorClose": validate_legacy_entry,
    "Silo::Transit": validate_legacy_entry,
    "EnergyBarier::Terminal": validate_energy_barrier_terminal,
    "SeAndroid::Boxes": validate_android_box,
    "NpcDialog::NpcDialog": validate_npc_dialog,
    "Scenery::DoorControl": validate_scenery_door,
    "Scenery::Dialog": validate_scenery_dialog,
    "Scenery::TransferToMap": warn_ambiguous_transfer,
}


def item_scripts(item: MapItem) -> Iterable[tuple[str, MapField]]:
    for field_name in ("TriggerScript", "StaticScript"):
        script_field = item.get(field_name)
        if script_field is not None:
            yield script_field.value, script_field


def validate_project(project_root: Path) -> ValidationResult:
    project_root = project_root.resolve()
    maps_root = project_root / "Maps"
    result = ValidationResult(project_root=project_root)

    map_paths = sorted(maps_root.glob("*.fomap")) if maps_root.is_dir() else []
    result.map_files = len(map_paths)

    for map_path in map_paths:
        items = parse_map_items(map_path)
        result.item_sections += len(items)
        for item in items:
            for script, _script_field in item_scripts(item):
                validator = CONTRACTS.get(script)
                if validator is None:
                    continue
                result.contract_items += 1
                check = ItemValidator(project_root, item, script, item.get("SceneryParams"))
                validator(check)
                result.findings.extend(check.findings)

    return result


def format_finding(finding: Finding) -> str:
    return (
        f"{finding.path.as_posix()}:{finding.line}: "
        f"{finding.severity.upper()} [{finding.code}] {finding.script} "
        f"({finding.context}): {finding.message}"
    )


def finding_sort_key(finding: Finding) -> tuple[str, int, str, str]:
    return finding.path.as_posix(), finding.line, finding.severity, finding.code


def print_summary(result: ValidationResult) -> None:
    print(
        f"Scanned {result.map_files} map file(s), {result.item_sections} item section(s), "
        f"{result.contract_items} known contract item(s)."
    )
    print(f"Result: {len(result.errors)} error(s), {len(result.warnings)} warning(s).")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate known TLA SceneryParams map contracts")
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=ROOT,
        help="project root (defaults to the repository root)",
    )
    parser.add_argument("--summary", action="store_true", help="print counts only")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    if not (project_root / "Maps").is_dir():
        parser.error(f"Maps directory not found under {project_root}")

    result = validate_project(project_root)
    if not args.summary:
        for finding in sorted(result.findings, key=finding_sort_key):
            stream = sys.stderr if finding.severity == SEVERITY_ERROR else sys.stdout
            print(format_finding(finding), file=stream)
    print_summary(result)
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
