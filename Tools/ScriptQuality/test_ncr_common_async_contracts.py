from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/NcrCommon.fos"


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


class NcrCommonAsyncContractTests(unittest.TestCase):
    def assert_async_time_event(self, attrs: str) -> None:
        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

    def test_beggar_monologue_locks_npc_and_map(self) -> None:
        attrs, body = function_contract("BeggarTimeEvent")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::LockCritterWithMap(npc)")
        self.assertLess(lock_at, body.index("npc.IsAlive()"))
        self.assertLess(lock_at, body.index("Messaging::SayOnHead(npc"))

    def test_beggar_hide_money_locks_npc_and_map(self) -> None:
        attrs, body = function_contract("TimeToHideMoney")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::LockCritterWithMap(npc)")
        self.assertLess(lock_at, body.index("npc.IsAlive()"))
        self.assertLess(lock_at, body.index("NpcPlanes::AddWalkPlane(npc"))

    def test_brahmin_cycle_locks_map_before_child_access(self) -> None:
        attrs, body = function_contract("NextIllBrahmin")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::Lock(map)")
        self.assertLess(lock_at, body.index("map.GetCritters("))
        self.assertLess(lock_at, body.index("Ill2Healthy(ill[i])"))
        self.assertLess(lock_at, body.index("Healthy2Ill(brahmin)"))

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
