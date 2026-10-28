from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Read-only identity baseline; tests compare exact sets and never regenerate it.
BASELINE_PATH = Path(__file__).resolve().with_name("english_text_baseline.json")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
ENTRY_RE = re.compile(r"^\{([^}]*)\}\{([^}]*)\}\{(.*)\}$")
SECTION_HEADER_RE = re.compile(r"^\[[^\[\]]+\]$")
ENGLISH_SECTION_HEADER = "[Text engl]"
BASELINE_MEMBERS = {"cyrillic_entries", "dialogs_without_english_block"}


def cyrillic_entry_identity(line: str) -> str | None:
    match = ENTRY_RE.fullmatch(line.rstrip(" \t"))
    if match is not None and CYRILLIC_RE.search(match.group(3)):
        return f"{{{match.group(1)}}}{{{match.group(2)}}}"
    return None


# Headers are whole lines; a literal '[' inside an entry value must not truncate.
def scan_english_block(text: str) -> tuple[bool, set[str]]:
    """Return whether [Text engl] exists and the Cyrillic entry identities in it."""
    has_english_section = False
    in_english_section = False
    identities: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if SECTION_HEADER_RE.fullmatch(stripped):
            in_english_section = stripped == ENGLISH_SECTION_HEADER
            has_english_section = has_english_section or in_english_section
            continue
        if not in_english_section:
            continue
        identity = cyrillic_entry_identity(line)
        if identity is not None:
            identities.add(identity)
    return has_english_section, identities


def english_surface_files() -> list[Path]:
    return [
        *sorted((PROJECT_ROOT / "Texts").glob("*.engl.fotxt")),
        *sorted((PROJECT_ROOT / "Dialogs").glob("*.fodlg")),
    ]


def collect_english_surface() -> tuple[dict[str, set[str]], set[str]]:
    cyrillic_entries: dict[str, set[str]] = {}
    dialogs_without_english_block: set[str] = set()
    for path in english_surface_files():
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        if path.parent == PROJECT_ROOT / "Texts":
            # A .fotxt pack contains bare entries; only dialogs use language sections.
            has_english_section = True
            identities = {identity for line in text.splitlines()
                          if (identity := cyrillic_entry_identity(line)) is not None}
        else:
            has_english_section, identities = scan_english_block(text)
        relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        if identities:
            cyrillic_entries[relative_path] = identities
        if path.parent.name == "Dialogs" and not has_english_section:
            dialogs_without_english_block.add(relative_path)
    return cyrillic_entries, dialogs_without_english_block


def load_baseline() -> tuple[dict[str, set[str]], set[str]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8-sig"))
    if set(baseline) != BASELINE_MEMBERS:
        raise ValueError(
            f"{BASELINE_PATH}: expected exactly {sorted(BASELINE_MEMBERS)}, got {sorted(baseline)}"
        )
    return (
        {path: set(identities) for path, identities in baseline["cyrillic_entries"].items()},
        set(baseline["dialogs_without_english_block"]),
    )


class EnglishTextSurfaceContractTests(unittest.TestCase):
    def test_cyrillic_entries_match_identity_baseline(self) -> None:
        actual_entries, _ = collect_english_surface()
        baseline_entries, _ = load_baseline()
        new = {path: entries - baseline_entries.get(path, set())
               for path, entries in actual_entries.items() if entries - baseline_entries.get(path, set())}
        fixed = {path: entries - actual_entries.get(path, set())
                 for path, entries in baseline_entries.items() if entries - actual_entries.get(path, set())}
        self.assertFalse(new, "New Cyrillic identities: translate these entries; do not expand the baseline")
        self.assertFalse(fixed, "Corrected identities: remove only these entries from the baseline")

    def test_dialogs_without_english_block_match_baseline(self) -> None:
        _, actual_dialogs = collect_english_surface()
        _, baseline_dialogs = load_baseline()
        self.assertEqual(
            actual_dialogs,
            baseline_dialogs,
            "dialogs without [Text engl] differ from the shrink-only baseline: "
            "add the English section and remove only completed paths from the baseline",
        )


if __name__ == "__main__":
    unittest.main()
