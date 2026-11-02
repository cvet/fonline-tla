#!/usr/bin/env python3
"""Validate the Item property-component contract of authored TLA content.

Item kinds move from the ``ItemType`` enum and flat ``<Kind>_<Field>``
properties to engine property components: an immutable bool marker
(``///@ Property Item Common bool Weapon Component``) plus qualified fields
(``Weapon.MaxAmmoCount``). Baking accepts every declared key, so it cannot see
a field authored without its marker, a marker on a map instance, two kind
markers on one prototype, or a persisted flat name retired without a
``MigrationRule``. This validator checks those contracts statically.

Components and properties come from ``///@ Property Item`` declarations in
``Scripts/**/*.fos`` (``Scripts/Generated/`` excluded). Item prototypes in
``Items/**/*.foitem`` resolve like ``ProtoBaker``: ancestors depth first, direct
parents left to right, the child last; an ancestor reached again through
another path contributes only at its first reach. Item instances are
``[.../Item]`` sections with ``$Proto`` in ``Maps/*.fomap``; their markers come
from the prototype. Static means effective ``Static = True`` or the legacy
``IsStatic = True`` that the Engine renames to ``Static``.

A rule involving an undeclared component is inactive, so a migration batch
activates its checks by declaring the kind marker:

- ``legacy-prefixed-key``: ``<C>_<F>`` key where ``<C>`` is a declared component.
- ``legacy-type-key``: a ``Type`` key once ``Type`` is no longer declared.
- ``transition-mismatch``: while ``Type`` is declared, effective ``Type = X``
  differs from marker ``X`` for a declared kind component.
- ``field-without-marker``: ``<C>.<F>`` authored where marker ``<C>`` is not true.
- ``marker-on-instance``: a component marker authored on a map instance.
- ``exclusive-kind``: more than one kind marker enabled.
- ``locker-mismatch``: ``Locker`` without ``Door``/``Container`` or the reverse
  (active once all three are declared).
- ``static-mismatch``: ``Grid`` on a non-static proto, another kind on a static one.
- ``missing-migration-rule``: a frozen legacy name that is no longer declared has
  no ``MigrationRule Property Item Rename|Remove`` in ``Scripts/Migration.fos``.
- ``dangling-migration-target``: a project ``Property Item Rename`` target is
  neither a script-declared nor an Engine ``ItemProperties`` property.

Every finding is an error; the exit code is 1 when any is reported.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]

KIND_COMPONENTS = ("Armor", "Drug", "Weapon", "Ammo", "Key", "Container", "Door", "Grid", "Car")
STATIC_KIND = "Grid"
LOCKER_COMPONENT = "Locker"
LOCKER_HOSTS = ("Door", "Container")
TYPE_PROPERTY = "Type"
STATIC_KEYS = ("Static", "IsStatic")

LEGACY_NAMES_PATH = "Tools/ContentQuality/item_component_legacy_names.txt"
MIGRATION_PATH = "Scripts/Migration.fos"
ENGINE_PROPERTIES_PATH = "Engine/Source/Common/EntityProperties.h"

CODES = (
    "legacy-prefixed-key",
    "legacy-type-key",
    "transition-mismatch",
    "field-without-marker",
    "marker-on-instance",
    "exclusive-kind",
    "locker-mismatch",
    "static-mismatch",
    "missing-migration-rule",
    "dangling-migration-target",
)

SECTION_RE = re.compile(r"^\s*\[([^]]+)]\s*$")
FIELD_RE = re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_.$]*)\s*=\s*(.*?)\s*$")
DECLARATION_RE = re.compile(r"^\s*///@\s+Property\s+Item\s+\w+\s+\S+\s+([A-Za-z_][A-Za-z0-9_.]*)(.*)$")
MIGRATION_RULE_RE = re.compile(r"^\s*///@\s+MigrationRule\s+Property\s+Item\s+(Rename|Remove)\s+(\S+)(?:\s+(\S+))?")
ENGINE_ITEM_BLOCK_RE = re.compile(r"^class\s+ItemProperties\b.*?^};", re.MULTILINE | re.DOTALL)
ENGINE_PROPERTY_RE = re.compile(r"FO_ENTITY_PROPERTY\([^()]*,\s*(\w+)\s*\)")
LEGACY_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)_(\w+)$")
INTEGER_RE = re.compile(r"[+-]?[0-9]+")


@dataclass(frozen=True)
class Violation:
    code: str
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class Declarations:
    properties: frozenset[str]
    components: frozenset[str]


@dataclass
class Section:
    path: str
    header: str
    line: int
    values: dict[str, tuple[str, int]] = field(default_factory=dict)

    def get(self, key: str) -> str | None:
        entry = self.values.get(key)
        return entry[0] if entry is not None else None

    def own_properties(self) -> list[tuple[str, str, int]]:
        """Property keys in source order; ``$`` control keys are not properties."""
        return [(key, value, line) for key, (value, line) in self.values.items() if not key.startswith("$")]


@dataclass
class ScanResult:
    item_files: int = 0
    proto_count: int = 0
    map_files: int = 0
    instance_count: int = 0
    components: tuple[str, ...] = ()
    kind_components: tuple[str, ...] = ()
    violations: list[Violation] = field(default_factory=list)


def is_true(value: str | None) -> bool:
    """Interpret an authored bool like the Engine: true/false ignoring case, else a nonzero integer."""
    if value is None:
        return False
    text = value.strip()
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    return INTEGER_RE.fullmatch(text) is not None and int(text) != 0


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def parse_sections(root: Path, path: Path) -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None
    path_text = relative(root, path)
    for line_number, line in enumerate(read_lines(path), start=1):
        section_match = SECTION_RE.match(line) if line.lstrip().startswith("[") else None
        if section_match is not None:
            current = Section(path_text, section_match.group(1).strip(), line_number)
            sections.append(current)
            continue
        if current is None:
            continue
        field_match = FIELD_RE.match(line)
        if field_match is not None:
            current.values[field_match.group(1)] = (field_match.group(2), line_number)
    return sections


def script_paths(root: Path) -> list[Path]:
    scripts_root = root / "Scripts"
    if not scripts_root.is_dir():
        return []
    return [
        path
        for path in sorted(scripts_root.rglob("*.fos"))
        if path.relative_to(scripts_root).parts[0] != "Generated"
    ]


def read_declarations(root: Path) -> Declarations:
    properties: set[str] = set()
    components: set[str] = set()
    for path in script_paths(root):
        for line in read_lines(path):
            match = DECLARATION_RE.match(line)
            if match is None:
                continue
            name = match.group(1)
            properties.add(name)
            if "Component" in match.group(2).split("//", 1)[0].split():
                components.add(name)
    return Declarations(frozenset(properties), frozenset(components))


def read_engine_item_properties(root: Path) -> set[str]:
    path = root / ENGINE_PROPERTIES_PATH
    if not path.is_file():
        return set()
    block = ENGINE_ITEM_BLOCK_RE.search(path.read_text(encoding="utf-8-sig", errors="replace"))
    return set(ENGINE_PROPERTY_RE.findall(block.group(0))) if block is not None else set()


class ProtoCatalog:
    """Item prototypes with baker-equivalent inherited values."""

    def __init__(self) -> None:
        self.sections: dict[str, Section] = {}
        self._effective: dict[str, dict[str, str]] = {}

    def add(self, section: Section, fallback_name: str) -> str:
        name = (section.get("$Name") or fallback_name).strip()
        # Baking rejects duplicate ids; keep the first so one error does not mask the other's checks.
        self.sections.setdefault(name, section)
        return name

    def __contains__(self, name: str) -> bool:
        return name in self.sections

    def effective(self, name: str) -> dict[str, str]:
        cached = self._effective.get(name)
        if cached is not None:
            return cached

        merged: dict[str, str] = {}
        reached: set[str] = set()
        active_path: list[str] = [name]

        def fill_parents(section: Section) -> None:
            for parent in (section.get("$Parent") or "").split():
                # Missing parents and cycles are baker errors; skip them instead of recursing forever.
                if parent not in self.sections or parent in active_path or parent in reached:
                    continue
                reached.add(parent)
                active_path.append(parent)
                fill_parents(self.sections[parent])
                active_path.pop()
                merged.update({key: value for key, value, _line in self.sections[parent].own_properties()})

        section = self.sections[name]
        fill_parents(section)
        merged.update({key: value for key, value, _line in section.own_properties()})
        self._effective[name] = merged
        return merged


class Checker:
    def __init__(self, declarations: Declarations, catalog: ProtoCatalog) -> None:
        self.catalog = catalog
        self.components = declarations.components
        self.kinds = tuple(kind for kind in KIND_COMPONENTS if kind in declarations.components)
        self.type_declared = TYPE_PROPERTY in declarations.properties
        self.locker_active = all(name in declarations.components for name in (LOCKER_COMPONENT, *LOCKER_HOSTS))
        self.violations: list[Violation] = []

    def add(self, code: str, path: str, line: int, message: str) -> None:
        self.violations.append(Violation(code, path, line, message))

    def check_key(self, path: str, line: int, key: str, markers: dict[str, str] | None, subject: str) -> None:
        legacy = LEGACY_KEY_RE.match(key)
        if legacy is not None and legacy.group(1) in self.components:
            component, field_name = legacy.groups()
            self.add(
                "legacy-prefixed-key",
                path,
                line,
                f"{subject}: {key} uses the retired flat name of component {component}; write {component}.{field_name}",
            )

        if key == TYPE_PROPERTY and not self.type_declared:
            self.add(
                "legacy-type-key",
                path,
                line,
                f"{subject}: Item.Type is no longer declared; author the kind component marker instead",
            )

        component = key.split(".", 1)[0] if "." in key else None
        if component is not None and component in self.components and markers is not None:
            if not is_true(markers.get(component)):
                self.add(
                    "field-without-marker",
                    path,
                    line,
                    f"{subject}: {key} is authored but the prototype does not enable {component} = True",
                )

    def check_exclusive(self, section: Section, values: dict[str, str], subject: str) -> None:
        enabled = [kind for kind in self.kinds if is_true(values.get(kind))]
        if len(enabled) > 1:
            self.add(
                "exclusive-kind",
                section.path,
                section.line,
                f"{subject}: enables {', '.join(enabled)}; at most one kind component is allowed",
            )

    def check_locker(self, section: Section, values: dict[str, str], subject: str) -> None:
        if not self.locker_active:
            return
        has_locker = is_true(values.get(LOCKER_COMPONENT))
        has_host = any(is_true(values.get(host)) for host in LOCKER_HOSTS)
        if has_locker and not has_host:
            self.add("locker-mismatch", section.path, section.line, f"{subject}: Locker requires Door or Container")
        elif has_host and not has_locker:
            self.add("locker-mismatch", section.path, section.line, f"{subject}: Door and Container require Locker")

    def check_static(self, section: Section, values: dict[str, str], subject: str) -> None:
        is_static = any(is_true(values.get(key)) for key in STATIC_KEYS)
        for kind in self.kinds:
            if not is_true(values.get(kind)):
                continue
            if kind == STATIC_KIND and not is_static:
                self.add("static-mismatch", section.path, section.line, f"{subject}: {kind} is allowed only on static items")
            elif kind != STATIC_KIND and is_static:
                self.add("static-mismatch", section.path, section.line, f"{subject}: {kind} is not allowed on static items")

    def check_transition(self, section: Section, values: dict[str, str], subject: str) -> None:
        if not self.type_declared or not self.kinds:
            return
        type_value = values.get(TYPE_PROPERTY, "None").strip()
        enabled = [kind for kind in self.kinds if is_true(values.get(kind))]
        expected = [type_value] if type_value in self.kinds else []
        if enabled != expected:
            markers = ", ".join(enabled) if enabled else "none"
            self.add(
                "transition-mismatch",
                section.path,
                section.line,
                f"{subject}: Type = {type_value} but enabled declared kind markers are {markers}",
            )

    def check_proto(self, name: str, section: Section) -> None:
        subject = f"proto {name}"
        values = self.catalog.effective(name)
        for key, _value, line in section.own_properties():
            self.check_key(section.path, line, key, values, subject)
        self.check_exclusive(section, values, subject)
        self.check_locker(section, values, subject)
        self.check_static(section, values, subject)
        self.check_transition(section, values, subject)

    def check_instance(self, section: Section) -> None:
        proto_name = (section.get("$Proto") or "").strip()
        subject = f"instance of {proto_name}"
        # Unknown prototypes are baker errors; marker-dependent checks need the prototype.
        proto_values = self.catalog.effective(proto_name) if proto_name in self.catalog else None
        overrides: dict[str, str] = {}
        for key, value, line in section.own_properties():
            if key in self.components:
                self.add(
                    "marker-on-instance",
                    section.path,
                    line,
                    f"{subject}: component marker {key} belongs on the item prototype, not on a map instance",
                )
                continue
            overrides[key] = value
            self.check_key(section.path, line, key, proto_values, subject)

        if proto_values is None:
            return
        merged = {**proto_values, **overrides}
        if any(key in overrides for key in STATIC_KEYS):
            self.check_static(section, merged, subject)
        if TYPE_PROPERTY in overrides:
            self.check_transition(section, merged, subject)


def check_migrations(root: Path, declarations: Declarations, violations: list[Violation]) -> None:
    rules: list[tuple[str, str, str | None, int]] = []
    migration_path = root / MIGRATION_PATH
    if migration_path.is_file():
        for line_number, line in enumerate(read_lines(migration_path), start=1):
            match = MIGRATION_RULE_RE.match(line)
            if match is not None:
                action, source, target = match.groups()
                rules.append((action, source.strip('"'), target.strip('"') if target else None, line_number))

    covered = {source for _action, source, _target, _line in rules}
    legacy_path = root / LEGACY_NAMES_PATH
    if legacy_path.is_file():
        for line_number, line in enumerate(read_lines(legacy_path), start=1):
            name = line.strip()
            if name and name not in declarations.properties and name not in covered:
                violations.append(
                    Violation(
                        "missing-migration-rule",
                        LEGACY_NAMES_PATH,
                        line_number,
                        f"legacy Item property {name} is no longer declared and has no "
                        f"'MigrationRule Property Item Rename|Remove {name}' in {MIGRATION_PATH}",
                    )
                )

    engine_properties = read_engine_item_properties(root)
    for action, source, target, line_number in rules:
        if action != "Rename" or target is None:
            continue
        if target not in declarations.properties and target not in engine_properties:
            violations.append(
                Violation(
                    "dangling-migration-target",
                    MIGRATION_PATH,
                    line_number,
                    f"Rename {source} -> {target}: {target} is not a declared script or Engine Item property",
                )
            )


def is_item_instance(section: Section) -> bool:
    return (section.header == "Item" or section.header.endswith("/Item")) and section.get("$Proto") is not None


def scan_project(root: Path) -> ScanResult:
    root = root.resolve()
    declarations = read_declarations(root)
    catalog = ProtoCatalog()
    result = ScanResult(
        components=tuple(sorted(declarations.components)),
        kind_components=tuple(kind for kind in KIND_COMPONENTS if kind in declarations.components),
    )

    items_root = root / "Items"
    proto_entries: list[tuple[str, Section]] = []
    item_paths = sorted(items_root.rglob("*.foitem")) if items_root.is_dir() else []
    result.item_files = len(item_paths)
    for path in item_paths:
        for section in parse_sections(root, path):
            if section.header == "ProtoItem":
                proto_entries.append((catalog.add(section, path.stem), section))
    result.proto_count = len(proto_entries)

    checker = Checker(declarations, catalog)
    for name, section in proto_entries:
        if catalog.sections[name] is section:
            checker.check_proto(name, section)

    maps_root = root / "Maps"
    map_paths = sorted(maps_root.glob("*.fomap")) if maps_root.is_dir() else []
    result.map_files = len(map_paths)
    for path in map_paths:
        for section in parse_sections(root, path):
            if is_item_instance(section):
                result.instance_count += 1
                checker.check_instance(section)

    check_migrations(root, declarations, checker.violations)
    result.violations = sorted(checker.violations, key=lambda item: (item.path, item.line, item.code))
    return result


def validate(root: Path) -> list[Violation]:
    return scan_project(root).violations


def format_violation(violation: Violation) -> str:
    return f"{violation.path}:{violation.line}: [{violation.code}] {violation.message}"


def print_summary(result: ScanResult) -> None:
    components = ", ".join(result.components) if result.components else "none"
    kinds = ", ".join(result.kind_components) if result.kind_components else "none"
    print(
        f"Scanned {result.proto_count} item proto(s) in {result.item_files} file(s) and "
        f"{result.instance_count} item instance(s) in {result.map_files} map(s)."
    )
    print(f"Declared Item components: {components}; kind components: {kinds}.")
    counts = Counter(violation.code for violation in result.violations)
    for code in CODES:
        if counts[code]:
            print(f"  {code}: {counts[code]}")
    print(f"Result: {len(result.violations)} violation(s).")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the TLA Item property-component content contract")
    parser.add_argument("--root", type=Path, default=ROOT, help="project root (defaults to the repository root)")
    parser.add_argument("--summary", action="store_true", help="print counts only, without individual violations")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not (root / "Scripts").is_dir():
        parser.error(f"Scripts directory not found under {root}")

    result = scan_project(root)
    if not args.summary:
        for violation in result.violations:
            print(format_violation(violation), file=sys.stderr)
    print_summary(result)
    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
