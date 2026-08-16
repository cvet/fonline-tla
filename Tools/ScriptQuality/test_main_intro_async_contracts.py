from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/MainIntro.fos"


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


class MainIntroAsyncContractTests(unittest.TestCase):
    def test_map_effect_callbacks_validate_payload_and_lock_expected_map(self) -> None:
        for name, guarded_use in (
            ("SmallEffect", "map.IntroDoorsOpen"),
            ("MainEffect", "Effects::RunEffect(map"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                payload_guard = body.index("values.length() < 2")
                lock_at = body.index("Sync::LockCritterWithMapAndLocation(cr, fixedCover)")
                map_check = body.index("cr.MapId != map.Id")
                self.assertLess(payload_guard, lock_at)
                self.assertLess(lock_at, map_check)
                self.assertLess(map_check, body.index(guarded_use))

    def test_critter_callbacks_lock_before_state_effects_or_replication(self) -> None:
        for name, guarded_use in (
            ("KillPlayer", "Effects::PlaySound"),
            ("OnPlayerDead", "player.Gender"),
            ("ReplicateCritter", "player.ModelNameBase"),
            ("ShowMessage", "player.ReplicationCount"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                self.assertLess(body.index("Sync::LockCritterWithMap(player)"), body.index(guarded_use))

    def test_replication_callback_locks_before_shared_async_path(self) -> None:
        _, body = function_contract("ReplicateCritter")

        self.assertLess(body.index("Sync::LockCritterWithMap(player)"), body.index("Replication::ReplicateCritter(player)"))

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
