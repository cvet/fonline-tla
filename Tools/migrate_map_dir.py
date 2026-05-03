"""Migrate per-critter `Dir = N` (hex direction 0..5) in *.fomap to angle degrees.

Engine change: the `Dir` property is now `mdir`, parsed as int angle in degrees.
The hexagonal `mdir(hdir)` constructor maps `dir -> dir*60 + 30`, so existing
hex-direction values must be rewritten as canonical angles to round-trip.

Mapping (hex -> angle):
    0 -> 30, 1 -> 90, 2 -> 150, 3 -> 210, 4 -> 270, 5 -> 330

Idempotent: any `Dir` value already > 5 is treated as already migrated and left
alone. The script only touches lines that match `^Dir = [0-5]$` exactly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


DIR_LINE = re.compile(r"^Dir = ([0-5])\s*$")


def convert_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    out_lines: list[str] = []
    changed = 0

    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        match = DIR_LINE.match(stripped)
        if match is None:
            out_lines.append(line)
            continue

        hex_dir = int(match.group(1))
        angle = hex_dir * 60 + 30
        newline = line[len(stripped):]
        out_lines.append(f"Dir = {angle}{newline}")
        changed += 1

    if changed != 0:
        path.write_text("".join(out_lines), encoding="utf-8")

    return changed


def main(maps_dir: Path) -> int:
    if not maps_dir.is_dir():
        print(f"Not a directory: {maps_dir}", file=sys.stderr)
        return 2

    total_files = 0
    total_lines = 0

    for path in sorted(maps_dir.glob("*.fomap")):
        n = convert_file(path)
        if n != 0:
            total_files += 1
            total_lines += n
            print(f"  {path.name}: {n} dir(s)")

    print(f"Migrated {total_lines} Dir line(s) across {total_files} file(s).")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "Maps"
    sys.exit(main(target))
