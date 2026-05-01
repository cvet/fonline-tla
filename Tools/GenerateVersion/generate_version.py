#!/usr/bin/env python3

"""Generate VERSION file by bumping the patch number relative to origin/master.

If VERSION is already modified in the current git diff (staged or unstaged),
the script leaves it untouched. Otherwise it reads the version from
origin/master, increments the patch component by one, and writes the result.
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


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    version_file = project_root / "VERSION"

    # Check if VERSION is already in the diff (staged + unstaged)
    diff_files = run_git("diff", "--name-only", "HEAD", cwd=project_root)
    staged_files = run_git("diff", "--name-only", "--cached", cwd=project_root)
    changed = set(diff_files.splitlines()) | set(staged_files.splitlines())

    if "VERSION" in changed:
        current = version_file.read_text().strip()
        print(f"VERSION already modified in diff: {current}")
        return 0

    # Read version from origin/master
    try:
        origin_version = run_git("show", "origin/master:VERSION", cwd=project_root).strip()
    except subprocess.CalledProcessError:
        print("Cannot read VERSION from origin/master, skipping", file=sys.stderr)
        return 0

    # Parse and bump patch
    parts = origin_version.split(".")
    if len(parts) != 3:
        print(f"Unexpected version format on origin/master: {origin_version}", file=sys.stderr)
        return 1

    major, minor, patch = parts[0], parts[1], parts[2]
    new_version = f"{major}.{minor}.{int(patch) + 1}"

    version_file.write_text(new_version + "\n")
    print(f"VERSION: {origin_version} -> {new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
