from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEXT_ID_RE = re.compile(r"^\{([^}]+)\}", re.MULTILINE)

# Existing untranslated entries in Text.engl.fotxt. Keep this as a ratchet: remove ids when their English
# surface is authored; never expand the baseline to admit a new omission.
KNOWN_MISSING_ENGLISH_IDS = (
    {str(value) for value in range(3861, 3890)}
    | {str(value) for value in range(3891, 3899)}
    | {str(value) for value in range(70070, 70097)}
    | {str(value) for value in range(7215, 7230)}
    | {str(value) for value in range(8040, 8064)}
)
KIDNAP_TEXT_IDS = {str(value) for value in range(3350, 3355)}
DEATHCLAW_EGG_TEXT_IDS = {str(value) for value in range(3490, 3496)}
DEN_BEKKY_TEXT_IDS = {str(value) for value in range(1100, 1103)}
VC_LYNNET_TEXT_IDS = {str(value) for value in range(5920, 5925)}
HUB_LAB_TEXT_IDS = {"8030", "8031"}
RACING_START_TEXT_IDS = {"3857", "3858"}


def read_text_ids(language: str) -> set[str]:
    path = PROJECT_ROOT / "Texts" / f"Text.{language}.fotxt"
    return set(TEXT_ID_RE.findall(path.read_text(encoding="utf-8-sig")))


class TextPackParityContractTests(unittest.TestCase):
    def test_text_pack_language_gaps_do_not_grow(self) -> None:
        russian_ids = read_text_ids("russ")
        english_ids = read_text_ids("engl")

        self.assertEqual(russian_ids - english_ids, KNOWN_MISSING_ENGLISH_IDS)
        self.assertEqual(english_ids - russian_ids, set())

    def test_wright_kidnap_runtime_texts_exist_in_both_languages(self) -> None:
        self.assertTrue(KIDNAP_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(KIDNAP_TEXT_IDS <= read_text_ids("engl"))

    def test_deathclaw_egg_runtime_texts_exist_in_both_languages(self) -> None:
        self.assertTrue(DEATHCLAW_EGG_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(DEATHCLAW_EGG_TEXT_IDS <= read_text_ids("engl"))

    def test_den_bekky_text_ids_are_not_shifted(self) -> None:
        self.assertTrue(DEN_BEKKY_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(DEN_BEKKY_TEXT_IDS <= read_text_ids("engl"))

        english_ids = TEXT_ID_RE.findall((PROJECT_ROOT / "Texts/Text.engl.fotxt").read_text(encoding="utf-8-sig"))
        self.assertEqual([english_ids.count(text_id) for text_id in sorted(DEN_BEKKY_TEXT_IDS)], [1, 1, 1])

    def test_vault_city_lynnet_runtime_texts_exist_in_both_languages(self) -> None:
        self.assertTrue(VC_LYNNET_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(VC_LYNNET_TEXT_IDS <= read_text_ids("engl"))

    def test_hub_lab_runtime_texts_exist_in_both_languages(self) -> None:
        self.assertTrue(HUB_LAB_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(HUB_LAB_TEXT_IDS <= read_text_ids("engl"))

    def test_racing_start_runtime_texts_exist_in_both_languages(self) -> None:
        self.assertTrue(RACING_START_TEXT_IDS <= read_text_ids("russ"))
        self.assertTrue(RACING_START_TEXT_IDS <= read_text_ids("engl"))


if __name__ == "__main__":
    unittest.main()
