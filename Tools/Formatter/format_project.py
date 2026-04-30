#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


PROJECT_FORMAT_PATTERNS = [
    'Scripts/*.fos',
    'Scripts/Json/*.fos',
    'Scripts/Extension/*.cpp',
    'Scripts/Extension/*.h',
    'Gui/*.fogui',
]
UTF8_BOM = b'\xef\xbb\xbf'
CLANG_FORMAT_VERSION_RE = re.compile(r'clang-format version (\d+)(?:\.|\b)')


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


def discover_clang_format(project_root: Path) -> str:
    bundled = project_root / 'Tools' / 'clang-format-20.exe'
    candidates: list[str] = []

    if sys.platform == 'win32' and bundled.is_file():
        candidates.append(str(bundled))

    for executable in ('clang-format-20', 'clang-format'):
        path = shutil.which(executable)
        if path and path not in candidates:
            candidates.append(path)

    for candidate in candidates:
        try:
            version_output = subprocess.check_output([candidate, '--version'], text=True, encoding='utf-8', errors='replace')
        except (OSError, subprocess.CalledProcessError):
            continue

        match = CLANG_FORMAT_VERSION_RE.search(version_output)
        if match is not None and int(match.group(1)) == 20:
            return candidate

    raise SystemExit('clang-format version 20 not found')


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


def strip_text_bom(content: str) -> str:
    return content[1:] if content.startswith('\ufeff') else content


def format_files(clang_format: str, root: Path, patterns: Sequence[str]) -> int:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(root.glob(pattern)))

    if not files:
        return 0

    changed = 0
    seen: set[Path] = set()
    unique_files: list[Path] = []

    for path in files:
        if path in seen:
            continue
        seen.add(path)
        unique_files.append(path)

    progress = TerminalProgress('ProjectFormatter')
    total = len(unique_files)

    for index, path in enumerate(unique_files, start=1):
        rel_path = path.relative_to(root).as_posix()
        progress.update(f'Formatting {index}/{total}: {rel_path}')

        original, has_bom = read_text_strip_bom(path)
        formatted = strip_text_bom(subprocess.check_output([clang_format, str(path)], text=True, encoding='utf-8'))
        formatted = ensure_trailing_newline(normalize_line_endings(formatted, detect_line_ending(original)), detect_line_ending(original))
        if not differs_beyond_line_endings(original, formatted) and not has_bom:
            continue

        changed += 1
        write_text_utf8(path, formatted)

    progress.finish(f'Completed, changed {changed} file(s)')
    return changed


def run_proto_formatter(project_root: Path, paths: Sequence[str], check_only: bool) -> None:
    command = [sys.executable, str(project_root / 'Tools' / 'Formatter' / 'format_prototypes.py')]
    if check_only:
        command.append('--check')
    command.extend(paths)
    subprocess.check_call(command)


def run_fomain_formatter(project_root: Path, target_path: str | None, check_only: bool) -> None:
    command = [sys.executable, str(project_root / 'Tools' / 'Formatter' / 'format_fomain.py')]
    if check_only:
        command.append('--check')
    if target_path:
        command.append(target_path)
    subprocess.check_call(command)


def format_scripts(project_root: Path) -> None:
    clang_format = discover_clang_format(project_root)
    format_files(clang_format, project_root, PROJECT_FORMAT_PATTERNS)


def format_prototypes(project_root: Path, paths: Sequence[str], check_only: bool) -> None:
    run_proto_formatter(project_root, paths, check_only)


def format_fomain(project_root: Path, target_path: str | None, check_only: bool) -> None:
    run_fomain_formatter(project_root, target_path, check_only)


def format_all(project_root: Path) -> None:
    format_scripts(project_root)
    format_fomain(project_root, None, False)
    format_prototypes(project_root, [], False)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Project formatting helpers')
    subparsers = parser.add_subparsers(dest='command', required=True)

    scripts_parser = subparsers.add_parser('scripts', help='format project script, extension and gui files')
    scripts_parser.set_defaults(no_args=True)

    protos_parser = subparsers.add_parser('prototypes', help='format project prototype files')
    protos_parser.add_argument('--check', action='store_true')
    protos_parser.add_argument('paths', nargs='*')

    fomain_parser = subparsers.add_parser('fomain', help='format project fomain file')
    fomain_parser.add_argument('--check', action='store_true')
    fomain_parser.add_argument('path', nargs='?')

    all_parser = subparsers.add_parser('all', help='format scripts, fomain, and prototypes')
    all_parser.set_defaults(no_args=True)

    return parser


def main() -> None:
    args = create_parser().parse_args()
    project_root = Path(__file__).resolve().parents[2]

    if args.command == 'scripts':
        format_scripts(project_root)
        return
    if args.command == 'prototypes':
        format_prototypes(project_root, args.paths, args.check)
        return
    if args.command == 'fomain':
        format_fomain(project_root, args.path, args.check)
        return
    if args.command == 'all':
        format_all(project_root)
        return

    raise SystemExit(f'Unsupported command: {args.command}')


if __name__ == '__main__':
    main()
