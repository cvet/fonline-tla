from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Purgatory.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if match is None:
        raise AssertionError(f"function {name} not found")

    opening = match.end() - 1
    depth = 1
    cursor = opening + 1
    while cursor < len(source) and depth:
        if source[cursor] == "{":
            depth += 1
        elif source[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth != 0:
        raise AssertionError(f"function {name} has an unbalanced body")
    return match.group("attrs") or "", source[opening + 1:cursor - 1]


class PurgatoryAsyncContractTests(unittest.TestCase):
    def test_location_cleanup_locks_before_children_messages_and_destroy(self) -> None:
        attrs, body = function_contract("DeletePurgatory")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::Lock(loc)")
        self.assertLess(lock_at, body.index("loc.GetMapByIndex(i)"))
        self.assertLess(lock_at, body.index("map.GetCritters(CritterFindType::Players)"))
        self.assertLess(lock_at, body.index("Messaging::Info(critters[i]"))
        self.assertLess(lock_at, body.index("Game.DestroyLocation(loc)"))

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
