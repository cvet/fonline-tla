#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_PROTO_EXTENSIONS = {'fopro', 'foloc', 'fomap', 'focr', 'foitem'}
UTF8_BOM = b'\xef\xbb\xbf'
SECTION_ENTITY_MAP = {
    'ProtoItem': 'Item',
    'ProtoCritter': 'Critter',
    'ProtoLocation': 'Location',
    'ProtoModifier': 'Modifier',
}


@dataclass(slots=True)
class PropertyOrderInfo:
    file_order: int
    group_order: int
    declaration_order: int
    component_root: str
    in_component: bool


@dataclass(slots=True)
class ComponentOrderInfo:
    file_order: int
    declaration_order: int


@dataclass(slots=True)
class EntityOrdering:
    properties: dict[str, PropertyOrderInfo]
    components: dict[str, ComponentOrderInfo]


@dataclass(slots=True)
class Entry:
    logical_lines: list[str]
    attached_comments: list[str]
    key: str | None
    original_index: int

    def emit_lines(self) -> list[str]:
        return [*self.attached_comments, *self.logical_lines]


class TerminalProgress:
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix
        self._last_len = 0

    def update(self, message: str) -> None:
        line = f'[{self._prefix}] {message}'
        padding = ' ' * max(0, self._last_len - len(line))
        sys.stdout.write('\r' + line + padding)
        sys.stdout.flush()
        self._last_len = len(line)

    def clear(self) -> None:
        if self._last_len == 0:
            return

        sys.stdout.write('\r' + ' ' * self._last_len + '\r')
        sys.stdout.flush()
        self._last_len = 0

    def finish(self, message: str) -> None:
        self.clear()
        print(f'[{self._prefix}] {message}', flush=True)


@dataclass(slots=True)
class Section:
    header: str
    entries: list[Entry]


def load_foconfig(engine_root: Path):
    sys.path.insert(0, str(engine_root / 'BuildTools'))
    import foconfig  # type: ignore
    return foconfig


def get_resource_pack_section(config_parser, pack_name: str):
    for section in config_parser.getSections('ResourcePack'):
        if section.getStr('Name', '') == pack_name:
            return section
    raise SystemExit(f"Resource pack '{pack_name}' not found in {config_parser}")


def split_words(text: str) -> list[str]:
    return [part for part in text.split() if part]


def meta_file_sort_key(project_root: Path, path: Path) -> tuple[str, str]:
    try:
        relative_path = path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        relative_path = path.resolve().as_posix()

    return (path.name.lower(), relative_path.lower())


def discover_codegen_args_file(project_root: Path) -> Path | None:
    candidates = sorted((project_root / 'Build').glob('*/codegen-args.txt'))
    return candidates[0] if candidates else None


def discover_meta_files_from_codegen_args(project_root: Path, args_file: Path) -> list[Path]:
    meta_files: list[Path] = []
    lines = args_file.read_text(encoding='utf-8-sig').splitlines()
    index = 0

    while index < len(lines):
        if lines[index] != '-meta' or index + 1 >= len(lines):
            index += 1
            continue

        meta_path = Path(lines[index + 1])
        if not meta_path.is_absolute():
            meta_path = (project_root / meta_path).resolve()

        if meta_path.is_file() and meta_path.suffix.lower() == '.fos':
            meta_files.append(meta_path)

        index += 2

    unique_meta_files = list(dict.fromkeys(meta_files))
    unique_meta_files.sort(key=lambda path: meta_file_sort_key(project_root, path))
    return unique_meta_files


def discover_meta_files(project_root: Path, main_config: Path) -> list[Path]:
    args_file = discover_codegen_args_file(project_root)
    if args_file is not None:
        meta_files = discover_meta_files_from_codegen_args(project_root, args_file)
        if meta_files:
            return meta_files

    foconfig = load_foconfig(project_root / 'Engine')
    parser = foconfig.ConfigParser()
    parser.loadFromFile(main_config)
    metadata_pack = get_resource_pack_section(parser, 'Metadata')

    meta_files: list[Path] = []
    seen: set[Path] = set()
    for input_dir in split_words(metadata_pack.getStr('InputDirs', '')):
        abs_dir = (project_root / input_dir).resolve()
        if not abs_dir.is_dir():
            continue
        for path in sorted(abs_dir.rglob('*.fos'), key=lambda file_path: meta_file_sort_key(project_root, file_path)):
            if path not in seen:
                meta_files.append(path)
                seen.add(path)
    return meta_files


def read_text_strip_bom(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    has_bom = data.startswith(UTF8_BOM)
    return data.decode('utf-8-sig'), has_bom


def detect_line_ending(content: str) -> str:
    return '\r\n' if '\r\n' in content else '\n'


def normalize_line_endings(content: str, line_ending: str) -> str:
    return content.replace('\r\n', '\n').replace('\r', '\n').replace('\n', line_ending)


def normalize_for_comparison(content: str) -> str:
    return content.replace('\r\n', '\n').replace('\r', '\n')


def differs_beyond_line_endings(original: str, formatted: str) -> bool:
    return normalize_for_comparison(original) != normalize_for_comparison(formatted)


def ensure_trailing_newline(content: str, line_ending: str) -> str:
    return content.rstrip('\r\n') + line_ending


def write_text_utf8(path: Path, content: str) -> None:
    path.write_bytes(content.encode('utf-8'))


def discover_proto_files(project_root: Path, main_config: Path, explicit_paths: list[str]) -> list[Path]:
    if explicit_paths:
        proto_files: list[Path] = []
        seen: set[Path] = set()
        for raw_path in explicit_paths:
            path = (project_root / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
            if path.is_dir():
                for file_path in sorted(path.rglob('*')):
                    if file_path.is_file() and file_path.suffix.lstrip('.').lower() in SUPPORTED_PROTO_EXTENSIONS and file_path not in seen:
                        proto_files.append(file_path)
                        seen.add(file_path)
            elif path.is_file() and path.suffix.lstrip('.').lower() in SUPPORTED_PROTO_EXTENSIONS and path not in seen:
                proto_files.append(path)
                seen.add(path)
        return proto_files

    foconfig = load_foconfig(project_root / 'Engine')
    parser = foconfig.ConfigParser()
    parser.loadFromFile(main_config)

    extensions = [ext for ext in split_words(parser.mainSection().getStr('Baking.ProtoFileExtensions', '')) if ext in SUPPORTED_PROTO_EXTENSIONS]
    extensions_set = set(extensions)
    protos_pack = get_resource_pack_section(parser, 'Protos')
    recursive = protos_pack.getBool('RecursiveInput', False)

    proto_files: list[Path] = []
    seen: set[Path] = set()
    for input_dir in split_words(protos_pack.getStr('InputDirs', '')):
        abs_dir = (project_root / input_dir).resolve()
        if not abs_dir.is_dir():
            continue
        iterator = abs_dir.rglob('*') if recursive else abs_dir.glob('*')
        for file_path in sorted(iterator):
            if file_path.is_file() and file_path.suffix.lstrip('.').lower() in extensions_set and file_path not in seen:
                proto_files.append(file_path)
                seen.add(file_path)
    return proto_files


def parse_property_flags(flags_text: str) -> tuple[list[str], list[str]]:
    tokens = split_words(flags_text)
    flags: list[str] = []
    groups: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == 'Group' and index + 2 < len(tokens) and tokens[index + 1] == '=':
            groups.append(tokens[index + 2])
            index += 3
            continue
        flags.append(token)
        index += 1
    return flags, groups


def parse_meta_order(meta_files: list[Path]) -> dict[str, EntityOrdering]:
    ordering: dict[str, EntityOrdering] = {}
    file_group_order: dict[tuple[str, int], dict[str, int]] = {}

    for file_order, meta_path in enumerate(meta_files):
        declaration_order = 0
        for raw_line in meta_path.read_text(encoding='utf-8-sig').splitlines():
            line = raw_line.strip()
            if not line.startswith('///@ Property '):
                continue

            property_text = line[len('///@ Property '):]
            comment_pos = property_text.find('//')
            if comment_pos != -1:
                property_text = property_text[:comment_pos].rstrip()

            tokens = property_text.split(' ', 4)
            if len(tokens) < 4:
                continue

            entity = tokens[0]
            property_name = tokens[3]
            flags_text = tokens[4] if len(tokens) > 4 else ''
            flags, groups = parse_property_flags(flags_text)

            entity_ordering = ordering.setdefault(entity, EntityOrdering(properties={}, components={}))
            if property_name in entity_ordering.properties:
                continue

            primary_group = groups[0] if groups else ''
            group_key = (entity, file_order)
            groups_in_file = file_group_order.setdefault(group_key, {})
            if primary_group and primary_group not in groups_in_file:
                groups_in_file[primary_group] = len(groups_in_file)
            group_order = groups_in_file.get(primary_group, len(groups_in_file))

            is_component_marker = 'Component' in flags and '.' not in property_name
            component_root = property_name.split('.', 1)[0] if ('.' in property_name or is_component_marker) else ''
            in_component = bool(component_root)

            entity_ordering.properties[property_name] = PropertyOrderInfo(
                file_order=file_order,
                group_order=group_order,
                declaration_order=declaration_order,
                component_root=component_root,
                in_component=in_component,
            )

            if component_root and component_root not in entity_ordering.components:
                entity_ordering.components[component_root] = ComponentOrderInfo(file_order=file_order, declaration_order=declaration_order)

            declaration_order += 1

    return ordering


def split_sections(lines: list[str]) -> tuple[list[str], list[Section]]:
    preamble: list[str] = []
    sections: list[Section] = []
    current_header: str | None = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            if current_header is None:
                current_header = stripped
            else:
                sections.append(Section(current_header, parse_entries(current_lines)))
                current_header = stripped
            current_lines = []
        elif current_header is None:
            preamble.append(line)
        else:
            current_lines.append(line)

    if current_header is not None:
        sections.append(Section(current_header, parse_entries(current_lines)))

    return preamble, sections


def parse_entries(lines: list[str]) -> list[Entry]:
    entries: list[Entry] = []
    pending_comments: list[str] = []
    index = 0
    entry_index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith('#'):
            pending_comments.append(stripped)
            index += 1
            continue

        logical_lines = [stripped]
        while logical_lines[-1].endswith('\\') and index + 1 < len(lines):
            index += 1
            logical_lines.append(lines[index].rstrip())

        key = None
        first_line = logical_lines[0]
        if '=' in first_line:
            key = first_line.split('=', 1)[0].strip()

        entries.append(Entry(logical_lines=logical_lines, attached_comments=pending_comments, key=key, original_index=entry_index))
        pending_comments = []
        entry_index += 1
        index += 1

    if pending_comments:
        entries.append(Entry(logical_lines=[], attached_comments=pending_comments, key=None, original_index=entry_index))

    return entries


def section_entity(header: str) -> str | None:
    return SECTION_ENTITY_MAP.get(header.strip()[1:-1])


def header_sort_key(entry: Entry) -> tuple[int, int]:
    if entry.key == '$Name':
        return (0, entry.original_index)
    if entry.key == '$Parent':
        return (1, entry.original_index)
    return (2, entry.original_index)


def make_name_entry(name: str) -> Entry:
    return Entry(logical_lines=[f'$Name = {name}'], attached_comments=[], key='$Name', original_index=-1)


def resolve_component_root(entity_ordering: EntityOrdering | None, key: str, known_component_roots: set[str] | None = None) -> str:
    if '.' in key:
        return key.split('.', 1)[0]
    if entity_ordering and key in entity_ordering.components:
        return key
    if known_component_roots and key in known_component_roots:
        return key
    return ''


def detect_component_roots(entries: list[Entry], entity_ordering: EntityOrdering | None) -> set[str]:
    roots: set[str] = set(entity_ordering.components.keys()) if entity_ordering else set()

    for entry in entries:
        if entry.key and '.' in entry.key:
            roots.add(entry.key.split('.', 1)[0])

    return roots


def non_component_sort_key(entity_ordering: EntityOrdering | None, entry: Entry) -> tuple[int, int, int, int]:
    if entry.key is None or entity_ordering is None:
        return (1, 10**9, 10**9, entry.original_index)

    info = entity_ordering.properties.get(entry.key)
    if info is None or info.in_component:
        return (1, 10**9, 10**9, entry.original_index)

    return (0, info.file_order, info.declaration_order, entry.original_index)


def component_sort_key(entity_ordering: EntityOrdering | None, entry: Entry, known_component_roots: set[str] | None = None) -> tuple[int, int, int, int, int]:
    if entry.key is None:
        return (1, 10**9, 10**9, 10**9, entry.original_index)

    component_root = resolve_component_root(entity_ordering, entry.key, known_component_roots)
    if not component_root:
        return (1, 10**9, 10**9, 10**9, entry.original_index)

    root_info = entity_ordering.components.get(component_root) if entity_ordering else None
    property_info = entity_ordering.properties.get(entry.key) if entity_ordering else None

    if root_info is None:
        root_file_order = 10**9
        root_declaration_order = 10**9
    else:
        root_file_order = root_info.file_order
        root_declaration_order = root_info.declaration_order

    if entry.key == component_root:
        return (0, root_file_order, root_declaration_order, -1, entry.original_index)

    if property_info is None:
        return (1, root_file_order, root_declaration_order, 10**9, entry.original_index)

    return (0, root_file_order, root_declaration_order, property_info.declaration_order, entry.original_index)


def emit_component_entries(
    lines: list[str],
    component_entries: list[Entry],
    entity_ordering: EntityOrdering | None,
    component_roots: set[str],
) -> None:
    previous_root = ''

    for entry in component_entries:
        component_root = resolve_component_root(entity_ordering, entry.key or '', component_roots)
        if previous_root and component_root and component_root != previous_root:
            lines.append('')

        lines.extend(entry.emit_lines())
        if component_root:
            previous_root = component_root


def format_section(section: Section, ordering: dict[str, EntityOrdering], default_name: str | None = None) -> list[str]:
    entity = section_entity(section.header)
    if entity is None:
        lines = [section.header]
        for entry in section.entries:
            lines.extend(entry.emit_lines())
        return lines

    entity_ordering = ordering.get(entity)
    component_roots = detect_component_roots(section.entries, entity_ordering)

    header_entries: list[Entry] = []
    non_component_entries: list[Entry] = []
    component_entries: list[Entry] = []
    text_entries: list[Entry] = []

    for entry in section.entries:
        if entry.key is None:
            non_component_entries.append(entry)
            continue

        if entry.key in ('$Name', '$Parent'):
            header_entries.append(entry)
            continue

        if entry.key.startswith('$Text'):
            text_entries.append(entry)
            continue

        component_root = resolve_component_root(entity_ordering, entry.key, component_roots)
        if component_root:
            component_entries.append(entry)
        else:
            non_component_entries.append(entry)

    if default_name and not any(entry.key == '$Name' for entry in header_entries):
        header_entries.append(make_name_entry(default_name))

    header_entries.sort(key=header_sort_key)
    non_component_entries.sort(key=lambda entry: non_component_sort_key(entity_ordering, entry))
    component_entries.sort(key=lambda entry: component_sort_key(entity_ordering, entry, component_roots))

    lines = [section.header]
    groups = [header_entries, non_component_entries, component_entries, text_entries]
    emitted_group = False

    for group in groups:
        if not group:
            continue
        if emitted_group:
            lines.append('')
        if group is component_entries:
            emit_component_entries(lines, component_entries, entity_ordering, component_roots)
        else:
            for entry in group:
                lines.extend(entry.emit_lines())
        emitted_group = True

    return lines


def format_file(path: Path, ordering: dict[str, EntityOrdering]) -> str:
    content, _ = read_text_strip_bom(path)
    preamble, sections = split_sections(content.splitlines())

    output_lines: list[str] = [line.rstrip() for line in preamble if line.strip()]
    for section in sections:
        formatted_lines = format_section(section, ordering, path.stem)
        if output_lines:
            output_lines.append('')
        output_lines.extend(formatted_lines)

    return '\n'.join(output_lines).rstrip() + '\n'


def format_prototypes(project_root: Path, main_config: Path, explicit_paths: list[str], check_only: bool = False) -> int:
    meta_files = discover_meta_files(project_root, main_config)
    ordering = parse_meta_order(meta_files)
    proto_files = discover_proto_files(project_root, main_config, explicit_paths)

    if not proto_files:
        print('[ProtoFormatter] No prototype files found', flush=True)
        return 0

    changed = 0
    progress = TerminalProgress('ProtoFormatter')
    total = len(proto_files)

    for index, path in enumerate(proto_files, start=1):
        rel_path = path.relative_to(project_root).as_posix()
        progress.update(f'Formatting {index}/{total}: {rel_path}')

        original, has_bom = read_text_strip_bom(path)
        formatted = ensure_trailing_newline(normalize_line_endings(format_file(path, ordering), detect_line_ending(original)), detect_line_ending(original))
        if differs_beyond_line_endings(original, formatted) or has_bom:
            changed += 1
            if not check_only:
                write_text_utf8(path, formatted)

    if check_only and changed != 0:
        progress.finish(f'{changed} file(s) require formatting')
        return 1

    progress.finish(f'Completed, changed {changed} file(s)')
    return 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Format project prototype files')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('paths', nargs='*')
    return parser


def main() -> None:
    args = create_parser().parse_args()
    project_root = Path(__file__).resolve().parents[2]
    exit_code = format_prototypes(
        project_root=project_root,
        main_config=project_root / 'TLA.fomain',
        explicit_paths=list(args.paths),
        check_only=args.check,
    )
    raise SystemExit(exit_code)


if __name__ == '__main__':
    main()