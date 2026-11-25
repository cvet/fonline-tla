#!/usr/bin/env python3
"""Runs the Engine script checks with this project's scopes, configuration and baselines.

`check_script_bindings.py` compares AngelScript handlers with their event and remote-call
declarations and keeps native script-facing signatures on `ptr<T>`/`nptr<T>`;
`check_angelscript_hygiene.py` checks module conventions of the backend. Both are
Engine-owned (`Engine/BuildTools`); TLA keeps only their arguments here so the local task
and CI call the same command. The rows of `script_bindings_baseline.tsv` only go down.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE_TOOLS = ROOT / "Engine" / "BuildTools"
QUALITY = ROOT / "Tools" / "ScriptQuality"

CHECKS = [
    [ENGINE_TOOLS / "check_script_bindings.py", "--root", ROOT,
     "--scope", "Engine/Source", "--scope", "SourceExt", "--scripts", "Scripts",
     "--exclude", "SourceExt/SHA/*", "--baseline", QUALITY / "script_bindings_baseline.tsv"],
    [ENGINE_TOOLS / "check_angelscript_hygiene.py", "--root", ROOT, "--scripts", "Scripts",
     "--config", QUALITY / "angelscript_hygiene.json"],
]


def main() -> int:
    failed = False

    for command in CHECKS:
        result = subprocess.run([sys.executable, *(str(part) for part in command)], check=False)
        failed = failed or result.returncode != 0

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
