from __future__ import annotations

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUEST_DECL_RE = re.compile(
    r"///@ Property Critter \w+ \w+ (?P<name>\w+) Mutable.*?Group = Quests(?!\w)"
)
QUEST_ENTRY_RE = re.compile(
    r"^\{CritterProperty::(?P<prop>\w+)\}\{(?P<key>[^}]*)\}\{(?P<value>[^}]*)\}", re.MULTILINE
)
QUEST_LANGUAGES = ("russ", "engl")
QUEST_METADATA_KEYS = ("QName", "QDesc")

# Exact historical key gaps (2026-10-28 audit), not property-level allowances.
# Ratchet: fix the text and remove the tuple; never add a new one.
KNOWN_MISSING_METADATA = {
    ("russ", "DenJaneDolg", "QDesc"),
    ("russ", "KlamEidenBramin", "QDesc"),
    ("engl", "KlamEidenBramin", "QDesc"),
}
KNOWN_RUSSIAN_ONLY_KEYS = {
    ("DenJaneDolg", "Qdesc"),  # Historical lowercase typo; keys stay case-sensitive.
    ("NcrReddingCaravanEscort", "7"),
    ("NcrReddingCaravanEscort", "8"),
    ("NcrReddingCaravanEscort", "9"),
    ("NcrReddingCaravanEscort", "10"),
    ("NcrReddingCaravanEscort", "11"),
}


def quest_properties() -> set[str]:
    props: set[str] = set()
    for path in (PROJECT_ROOT / "Scripts").glob("*.fos"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if "Group = Quests" in line:
                match = QUEST_DECL_RE.search(line)
                if match:
                    props.add(match.group("name"))
    return props


def quest_keys(language: str) -> dict[str, set[str]]:
    text = (PROJECT_ROOT / "Texts" / f"Quest.{language}.fotxt").read_text(
        encoding="utf-8-sig"
    )
    keys: dict[str, set[str]] = {}
    for match in QUEST_ENTRY_RE.finditer(text):
        keys.setdefault(match.group("prop"), set()).add(match.group("key"))
    return keys


def language_packs() -> dict[str, dict[str, set[str]]]:
    return {language: quest_keys(language) for language in QUEST_LANGUAGES}


def has_nonzero_numeric_state(keys: set[str]) -> bool:
    return any(key.isdigit() and int(key) > 0 for key in keys)


class QuestTextCoverageContractTests(unittest.TestCase):
    def test_every_quest_property_has_nonzero_state_text_in_both_languages(self) -> None:
        props = quest_properties()
        packs = language_packs()
        missing = {
            (language, prop)
            for language, keys in packs.items()
            for prop in props
            if not has_nonzero_numeric_state(keys.get(prop, set()))
        }
        self.assertEqual(
            missing,
            set(),
            "every declared quest property needs at least one nonzero numeric state entry in both languages",
        )

    def test_quest_metadata_key_gaps_match_baseline(self) -> None:
        props = quest_properties()
        packs = language_packs()
        missing = {
            (language, prop, key)
            for language, keys in packs.items()
            for prop in props
            for key in QUEST_METADATA_KEYS
            if key not in keys.get(prop, set())
        }
        self.assertEqual(
            missing,
            KNOWN_MISSING_METADATA,
            "missing QName/QDesc keys must remain the exact historical tuples; a new key cannot hide behind a known property",
        )

    def test_quest_russian_only_keys_match_baseline(self) -> None:
        props = quest_properties()
        russian, english = quest_keys("russ"), quest_keys("engl")
        russian_only = {
            (prop, key)
            for prop in props
            for key in russian.get(prop, set()) - english.get(prop, set())
        }
        self.assertEqual(
            russian_only,
            KNOWN_RUSSIAN_ONLY_KEYS,
            "Russian-only quest keys must remain the exact historical tuples; add the English entry and shrink the baseline",
        )

    def test_quest_declared_and_texted_sets_match_in_both_languages(self) -> None:
        props = quest_properties()
        orphans = {
            (language, prop)
            for language, keys in language_packs().items()
            for prop in keys
            if prop not in props
        }
        self.assertEqual(
            orphans,
            set(),
            "quest pack entries must have a live Group = Quests property declaration in both language packs",
        )


if __name__ == "__main__":
    unittest.main()
