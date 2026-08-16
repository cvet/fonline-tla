"""Regression contracts for the Arroyo Mynoc defence quest."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "ArroyoMynocDefence.fos"


class ArroyoMynocDefenceContractTests(unittest.TestCase):
    def test_initial_stage_allows_the_authored_solo_dialog_branch(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        helper = re.search(
            r"void StartQuest\(Critter player, int stage\)\s*\{(?P<body>.*?)\n\}",
            source,
            flags=re.DOTALL,
        )

        self.assertIsNotNone(helper)
        body = helper.group("body")
        self.assertIn("if (stage == 2 && group.length() < MIN_PLAYERS)", body)
        self.assertNotRegex(
            body,
            r"(?m)^\s*if \(group\.length\(\) < MIN_PLAYERS\)",
        )

    def test_second_stage_still_rejects_an_undersized_group(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        result = re.search(
            r"int StartStage2\(Critter player, Critter npc\)\s*\{(?P<body>.*?)\n\}",
            source,
            flags=re.DOTALL,
        )

        self.assertIsNotNone(result)
        self.assertIn("if (group.length() < MIN_PLAYERS)", result.group("body"))
        self.assertIn("return DIALOG_NUM_COUNT;", result.group("body"))


if __name__ == "__main__":
    unittest.main()
