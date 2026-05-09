#!/usr/bin/env python3

"""Generate VERSION file by bumping the patch number relative to origin/master.

If VERSION is already modified in the current git diff (staged or unstaged),
the script leaves it untouched. Otherwise it reads the version from
origin/master, increments the patch component by one, and writes the result
unless that would lower the current repository version.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def parse_version(version: str, source: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Unexpected version format in {source}: {version}")

    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as ex:
        raise ValueError(f"Unexpected version format in {source}: {version}") from ex


def format_version(version: tuple[int, int, int]) -> str:
    return f"{version[0]}.{version[1]}.{version[2]}"


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    version_file = project_root / "VERSION"
    current_version = version_file.read_text().strip()

    # Check if VERSION is already in the diff (staged + unstaged)
    diff_files = run_git("diff", "--name-only", "HEAD", cwd=project_root)
    staged_files = run_git("diff", "--name-only", "--cached", cwd=project_root)
    changed = set(diff_files.splitlines()) | set(staged_files.splitlines())

    if "VERSION" in changed:
        print(f"VERSION already modified in diff: {current_version}")
        return 0

    # Read version from origin/master
    try:
        origin_version = run_git("show", "origin/master:VERSION", cwd=project_root).strip()
    except subprocess.CalledProcessError:
        print("Cannot read VERSION from origin/master, skipping", file=sys.stderr)
        return 0

    try:
        current = parse_version(current_version, "VERSION")
        origin = parse_version(origin_version, "origin/master:VERSION")
    except ValueError as ex:
        print(ex, file=sys.stderr)
        return 1

    origin_next = origin[0], origin[1], origin[2] + 1
    new_version = max(current, origin_next)
    new_version_text = format_version(new_version)

    version_file.write_text(new_version_text + "\n")
    print(f"VERSION: {current_version} -> {new_version_text} (origin/master: {origin_version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
