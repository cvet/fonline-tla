from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_contract_module(module_name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(module_name, HERE / file_name)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {file_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


english_surface = load_contract_module(
    "content_quality_english_text_surface", "test_english_text_surface.py"
)
quest_coverage = load_contract_module(
    "content_quality_quest_text_coverage", "test_quest_text_coverage.py"
)


class ContentQualityRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="content-quality-regressions-"
        )
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        for directory in ("Texts", "Dialogs", "Scripts"):
            (self.root / directory).mkdir()
        self.english_root = english_surface.PROJECT_ROOT
        self.english_baseline = english_surface.BASELINE_PATH
        self.quest_root = quest_coverage.PROJECT_ROOT
        self.quest_missing_metadata = quest_coverage.KNOWN_MISSING_METADATA
        self.quest_russian_only = quest_coverage.KNOWN_RUSSIAN_ONLY_KEYS
        self.write_english_baseline()
        english_surface.PROJECT_ROOT = self.root
        english_surface.BASELINE_PATH = self.root / "english_text_baseline.json"
        quest_coverage.PROJECT_ROOT = self.root
        quest_coverage.KNOWN_MISSING_METADATA = set()
        quest_coverage.KNOWN_RUSSIAN_ONLY_KEYS = set()

    def tearDown(self) -> None:
        english_surface.PROJECT_ROOT = self.english_root
        english_surface.BASELINE_PATH = self.english_baseline
        quest_coverage.PROJECT_ROOT = self.quest_root
        quest_coverage.KNOWN_MISSING_METADATA = self.quest_missing_metadata
        quest_coverage.KNOWN_RUSSIAN_ONLY_KEYS = self.quest_russian_only

    def write_file(self, relative_path: str, text: str) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def write_english_baseline(
        self,
        cyrillic_entries: dict[str, list[str]] | None = None,
        dialogs_without_english_block: list[str] | None = None,
    ) -> None:
        baseline = {
            "cyrillic_entries": cyrillic_entries or {},
            "dialogs_without_english_block": dialogs_without_english_block or [],
        }
        self.write_file("english_text_baseline.json", json.dumps(baseline, indent=2) + "\n")

    def run_english_contract(self, method_name: str) -> None:
        getattr(english_surface.EnglishTextSurfaceContractTests(method_name), method_name)()

    def run_quest_contract(self, method_name: str) -> None:
        getattr(quest_coverage.QuestTextCoverageContractTests(method_name), method_name)()

    def write_quest_fixture(
        self, property_name: str, russian_entries: str, english_entries: str
    ) -> None:
        self.write_file(
            "Scripts/Quest.fos",
            f"///@ Property Critter Common uint8 {property_name} Mutable Group = Quests Quest = 1\n",
        )
        self.write_file("Texts/Quest.russ.fotxt", russian_entries)
        self.write_file("Texts/Quest.engl.fotxt", english_entries)

    def test_same_count_swapped_cyrillic_identity_is_rejected(self) -> None:
        # One corrected identity and one new offender keep the aggregate count equal.
        self.write_file(
            "Dialogs/swap.fodlg",
            "[Text engl]\n"
            "{Speech 1}{}{English}\n"
            "{Speech 2}{}{Текст}\n",
        )
        self.write_english_baseline({"Dialogs/swap.fodlg": ["{Speech 1}{}"]})
        with self.assertRaises(AssertionError):
            self.run_english_contract("test_cyrillic_entries_match_identity_baseline")

    def test_new_cyrillic_entry_in_known_dialog_is_rejected(self) -> None:
        self.write_file(
            "Dialogs/existing.fodlg",
            "[Text engl]\n"
            "{Speech 1}{}{Текст}\n"
            "{Speech 2}{}{Текст}\n",
        )
        self.write_english_baseline({"Dialogs/existing.fodlg": ["{Speech 1}{}"]})
        with self.assertRaises(AssertionError):
            self.run_english_contract("test_cyrillic_entries_match_identity_baseline")

    def test_literal_bracket_before_cyrillic_text_is_scanned(self) -> None:
        self.write_file(
            "Dialogs/bracket.fodlg",
            "[Text engl]\n"
            "{Speech 1}{}{[Wait]}\n"
            "{Speech 2}{}{Текст}\n"
            "{Speech 3}{}{[Wait] Текст}\n"
            "[Text russ]\n"
            "{Speech 4}{}{Текст}\n",
        )
        self.write_english_baseline(
            {"Dialogs/bracket.fodlg": ["{Speech 2}{}", "{Speech 3}{}"]}
        )
        self.run_english_contract("test_cyrillic_entries_match_identity_baseline")

    def test_dialog_without_english_section_is_detected(self) -> None:
        self.write_file("Dialogs/no_english.fodlg", "[Text russ]\n{Speech 1}{}{Текст}\n")
        self.write_english_baseline(dialogs_without_english_block=[])
        with self.assertRaises(AssertionError):
            self.run_english_contract("test_dialogs_without_english_block_match_baseline")

    def test_clean_new_english_pack_is_allowed(self) -> None:
        self.write_file("Texts/Clean.engl.fotxt", "{100}{}{English only}\n")
        self.write_english_baseline()
        self.run_english_contract("test_cyrillic_entries_match_identity_baseline")
        self.run_english_contract("test_dialogs_without_english_block_match_baseline")

    def test_plain_english_pack_entries_are_scanned(self) -> None:
        self.write_file("Texts/Plain.engl.fotxt", "{100}{}{Текст} \t\n{200}{}{English}\n")
        self.write_english_baseline({"Texts/Plain.engl.fotxt": ["{100}{}"]})
        self.run_english_contract("test_cyrillic_entries_match_identity_baseline")
        self.write_file("Texts/Plain.engl.fotxt", "{100}{}{English}\n{200}{}{Текст}\n")
        with self.assertRaises(AssertionError):
            self.run_english_contract("test_cyrillic_entries_match_identity_baseline")

    def test_qname_only_quest_property_is_rejected_in_russian(self) -> None:
        self.write_quest_fixture(
            "QNameOnly",
            russian_entries="{CritterProperty::QNameOnly}{QName}{Город}\n",
            english_entries="{CritterProperty::QNameOnly}{1}{Started}\n",
        )
        with self.assertRaises(AssertionError):
            self.run_quest_contract(
                "test_every_quest_property_has_nonzero_state_text_in_both_languages"
            )

    def test_qname_only_quest_property_is_rejected_in_english(self) -> None:
        self.write_quest_fixture(
            "QNameOnly",
            russian_entries="{CritterProperty::QNameOnly}{1}{Начато}\n",
            english_entries="{CritterProperty::QNameOnly}{QName}{City}\n",
        )
        with self.assertRaises(AssertionError):
            self.run_quest_contract(
                "test_every_quest_property_has_nonzero_state_text_in_both_languages"
            )

    def test_additional_missing_english_state_for_known_gap_is_rejected(self) -> None:
        russian_entries = (
            "{CritterProperty::Gapped}{QName}{Имя}\n"
            "{CritterProperty::Gapped}{QDesc}{Описание}\n"
            "{CritterProperty::Gapped}{1}{Начато}\n"
            "{CritterProperty::Gapped}{2}{Завершено}\n"
        )
        self.write_quest_fixture(
            "Gapped",
            russian_entries=russian_entries,
            english_entries=(
                "{CritterProperty::Gapped}{QName}{Name}\n"
                "{CritterProperty::Gapped}{QDesc}{Description}\n"
                "{CritterProperty::Gapped}{1}{Started}\n"
            ),
        )
        quest_coverage.KNOWN_RUSSIAN_ONLY_KEYS = {("Gapped", "2")}
        self.run_quest_contract("test_quest_russian_only_keys_match_baseline")
        self.write_file(
            "Texts/Quest.russ.fotxt",
            russian_entries + "{CritterProperty::Gapped}{3}{Новое}\n",
        )
        with self.assertRaises(AssertionError):
            self.run_quest_contract("test_quest_russian_only_keys_match_baseline")

    def test_complete_both_language_quest_fixture_is_accepted(self) -> None:
        self.write_quest_fixture(
            "Complete",
            russian_entries=(
                "{CritterProperty::Complete}{QName}{Имя}\n"
                "{CritterProperty::Complete}{QDesc}{Описание}\n"
                "{CritterProperty::Complete}{1}{Начато}\n"
                "{CritterProperty::Complete}{2}{Завершено}\n"
            ),
            english_entries=(
                "{CritterProperty::Complete}{QName}{Name}\n"
                "{CritterProperty::Complete}{QDesc}{Description}\n"
                "{CritterProperty::Complete}{1}{Started}\n"
                "{CritterProperty::Complete}{2}{Finished}\n"
            ),
        )
        for method_name in (
            "test_every_quest_property_has_nonzero_state_text_in_both_languages",
            "test_quest_metadata_key_gaps_match_baseline",
            "test_quest_russian_only_keys_match_baseline",
            "test_quest_declared_and_texted_sets_match_in_both_languages",
        ):
            self.run_quest_contract(method_name)

    def test_invalid_utf8_in_russian_quest_pack_is_not_replaced(self) -> None:
        self.write_quest_fixture(
            "Complete", "{CritterProperty::Complete}{1}{Начато}\n",
            "{CritterProperty::Complete}{1}{Started}\n",
        )
        (self.root / "Texts/Quest.russ.fotxt").write_bytes(b"{CritterProperty::Complete}{1}{\xff}\n")
        with self.assertRaises(UnicodeDecodeError):
            self.run_quest_contract("test_every_quest_property_has_nonzero_state_text_in_both_languages")


if __name__ == "__main__":
    unittest.main()
