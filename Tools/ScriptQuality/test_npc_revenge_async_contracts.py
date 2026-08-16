from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/NpcRevenge.fos"


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


class NpcRevengeAsyncContractTests(unittest.TestCase):
    def test_map_loops_lock_map_before_saved_state_or_children(self) -> None:
        for name, guarded_use in (
            ("MapLoopCheckGag", "RevengeFromMap(map)"),
            ("MapLoopMeeting", "RevengeFromMap(map)"),
            ("MapLoopLeaderCalls", "RevengeFromMap(map)"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                self.assertLess(body.index("Sync::Lock(map)"), body.index(guarded_use))

    def test_delayed_answer_validates_payload_and_locks_registry_map(self) -> None:
        attrs, body = function_contract("MeetingAnswer")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        payload_guard = body.index("values.length() < 3")
        map_lock = body.index("Sync::Lock(map)")
        self.assertLess(payload_guard, map_lock)
        self.assertLess(map_lock, body.index("RevengeFromMap(map)"))
        self.assertLess(map_lock, body.index("map.GetCrittersInRadius"))

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
