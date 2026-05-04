#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


UTF8_BOM = b'\xef\xbb\xbf'
SETTING_LINE_RE = re.compile(r'^\s*([A-Za-z0-9_.]+)\s*=\s*(.*?)\s*$')
SECTION_HEADER_RE = re.compile(r'^\s*\[[^\]]+\]\s*$')
ENGINE_SETTING_RE = re.compile(r'^(?:FIXED_SETTING|VARIABLE_SETTING)\([^,]+,\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\b')
SCRIPT_SETTING_RE = re.compile(r'^\s*///@\s*Setting\s+\S+\s+\S+\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*$')


@dataclass(slots=True)
class ConfigEntry:
    key: str
    value: str
    comments: list[str]
    original_index: int


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

    return meta_files


def discover_meta_files(project_root: Path, main_config: Path) -> list[Path]:
    args_file = discover_codegen_args_file(project_root)
    if args_file is not None:
        meta_files = discover_meta_files_from_codegen_args(project_root, args_file)
        if meta_files:
            return sorted(dict.fromkeys(meta_files))

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
        for path in sorted(abs_dir.rglob('*.fos')):
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


def register_setting(setting_name: str, setting_order: dict[str, int]) -> None:
    if setting_name in setting_order:
        return

    setting_order[setting_name] = len(setting_order)


def build_setting_order(project_root: Path, main_config: Path) -> dict[str, int]:
    setting_order: dict[str, int] = {}

    settings_include = project_root / 'Engine' / 'Source' / 'Common' / 'Settings-Include.h'
    for raw_line in settings_include.read_text(encoding='utf-8-sig').splitlines():
        line = raw_line.strip()
        match = ENGINE_SETTING_RE.match(line)
        if match is None:
            continue
        register_setting(f'{match.group(1)}.{match.group(2)}', setting_order)

    for meta_path in discover_meta_files(project_root, main_config):
        for raw_line in meta_path.read_text(encoding='utf-8-sig').splitlines():
            match = SCRIPT_SETTING_RE.match(raw_line)
            if match is None:
                continue
            register_setting(f'{match.group(1)}.{match.group(2)}', setting_order)

    return setting_order


def split_lines(content: str) -> list[str]:
    return content.replace('\r\n', '\n').replace('\r', '\n').split('\n')


def normalize_comment_block(lines: list[str]) -> list[str]:
    block = [line.rstrip() for line in lines]
    while block and not block[0].strip():
        block.pop(0)
    while block and not block[-1].strip():
        block.pop()
    return block


def parse_entries(lines: list[str]) -> tuple[list[str], list[ConfigEntry], list[str]]:
    entries: list[ConfigEntry] = []
    pending_comments: list[str] = []
    leading_comments: list[str] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#'):
            pending_comments.append(raw_line.rstrip())
            continue

        match = SETTING_LINE_RE.match(raw_line)
        if match is None:
            pending_comments.append(raw_line.rstrip())
            continue

        if not entries and pending_comments:
            leading_comments = normalize_comment_block(pending_comments)
            pending_comments = []

        entries.append(
            ConfigEntry(
                key=match.group(1),
                value=match.group(2),
                comments=normalize_comment_block(pending_comments),
                original_index=len(entries),
            )
        )
        pending_comments = []

    return leading_comments, entries, pending_comments


def is_grouped_setting(entry: ConfigEntry) -> bool:
    return '.' in entry.key


def sort_settings(entries: list[ConfigEntry], setting_order: dict[str, int]) -> list[ConfigEntry]:
    unknown_settings: dict[str, int] = {}

    def setting_rank(setting_name: str) -> int:
        if setting_name in setting_order:
            return setting_order[setting_name]
        if setting_name not in unknown_settings:
            unknown_settings[setting_name] = len(setting_order) + len(unknown_settings)
        return unknown_settings[setting_name]

    return sorted(
        entries,
        key=lambda entry: (
            entry.key.split('.', 1)[0].lower(),
            entry.key.split('.', 1)[0],
            setting_rank(entry.key),
            entry.original_index,
        ),
    )


def render_entry_block(entries: list[ConfigEntry]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        if entry.comments:
            if lines and lines[-1] != '':
                lines.append('')
            lines.extend(entry.comments)
        lines.append(f'{entry.key} = {entry.value}')
    return lines


def append_block(target: list[str], block: list[str]) -> None:
    if not block:
        return
    if target and target[-1] != '':
        target.append('')
    target.extend(block)


def format_settings_section(lines: list[str], setting_order: dict[str, int], metadata_keys: tuple[str, ...] = (), *, separate_groups: bool = True) -> list[str]:
    leading_comments, entries, tail_lines = parse_entries(lines)
    metadata_rank = {key: index for index, key in enumerate(metadata_keys)}

    metadata_entries = sorted(
        [entry for entry in entries if entry.key in metadata_rank],
        key=lambda entry: (metadata_rank[entry.key], entry.original_index),
    )
    grouped_entries = sort_settings([entry for entry in entries if is_grouped_setting(entry) and entry.key not in metadata_rank], setting_order)
    other_entries = [entry for entry in entries if entry.key not in metadata_rank and not is_grouped_setting(entry)]

    result: list[str] = list(leading_comments)
    append_block(result, render_entry_block(metadata_entries))
    append_block(result, render_entry_block(other_entries))

    current_group = None
    group_block: list[ConfigEntry] = []
    for entry in grouped_entries:
        group_name = entry.key.split('.', 1)[0]
        if current_group is None:
            current_group = group_name
        if group_name != current_group:
            if separate_groups:
                append_block(result, render_entry_block(group_block))
            else:
                result.extend(render_entry_block(group_block))
            group_block = []
            current_group = group_name
        group_block.append(entry)

    if separate_groups:
        append_block(result, render_entry_block(group_block))
    else:
        result.extend(render_entry_block(group_block))

    trailing = normalize_comment_block(tail_lines)
    if result and trailing:
        result.append('')
    result.extend(trailing)
    return result


def split_sections(lines: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    first_section_index = next((index for index, line in enumerate(lines) if SECTION_HEADER_RE.match(line.strip())), len(lines))
    main_lines = lines[:first_section_index]
    sections: list[tuple[str, list[str]]] = []

    index = first_section_index
    while index < len(lines):
        header = lines[index].rstrip()
        index += 1
        body_start = index
        while index < len(lines) and not SECTION_HEADER_RE.match(lines[index].strip()):
            index += 1
        sections.append((header, lines[body_start:index]))

    return main_lines, sections


def format_fomain_content(content: str, project_root: Path, main_config: Path) -> str:
    setting_order = build_setting_order(project_root, main_config)
    lines = split_lines(content)
    main_lines, sections = split_sections(lines)

    formatted_lines = format_settings_section(main_lines, setting_order)

    for header, body_lines in sections:
        if formatted_lines and formatted_lines[-1] != '':
            formatted_lines.append('')
        formatted_lines.append(header)

        stripped_header = header.strip()
        if stripped_header == '[SubConfig]':
            formatted_lines.extend(format_settings_section(body_lines, setting_order, metadata_keys=('Name', 'Parent'), separate_groups=False))
        else:
            formatted_lines.extend(line.rstrip() for line in body_lines)

    return '\n'.join(formatted_lines)


def format_fomain(project_root: Path, target_path: Path, check_only: bool = False) -> int:
    original, has_bom = read_text_strip_bom(target_path)
    line_ending = detect_line_ending(original)
    formatted = format_fomain_content(original, project_root, target_path)
    formatted = ensure_trailing_newline(normalize_line_endings(formatted, line_ending), line_ending)

    if not differs_beyond_line_endings(original, formatted) and not has_bom:
        print('[FomainFormatter] Completed, changed 0 file(s)', flush=True)
        return 0

    if check_only:
        print('[FomainFormatter] 1 file(s) require formatting', flush=True)
        return 1

    write_text_utf8(target_path, formatted)
    print(f'[FomainFormatter] Formatted: {target_path.relative_to(project_root).as_posix()}', flush=True)
    print('[FomainFormatter] Completed, changed 1 file(s)', flush=True)
    return 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Format project fomain file')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('path', nargs='?', default='TLA.fomain')
    return parser


def main() -> None:
    args = create_parser().parse_args()
    project_root = Path(__file__).resolve().parents[2]
    target_path = (project_root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    exit_code = format_fomain(project_root, target_path, args.check)
    raise SystemExit(exit_code)


if __name__ == '__main__':
    main()