from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/KlamCowboy.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool|Critter\?)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class KlamCowboyAsyncContractTests(unittest.TestCase):
    def test_map_timers_lock_map_before_children_or_spawns(self) -> None:
        for name, guarded_use in (
            ("StartAtack", "map.GetCritters"),
            ("SpawnMobsLoop", "map.GetCritters"),
            ("SpawnMobs", "Entrance::MapCountEntry(map"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                self.assertLess(body.index("Sync::Lock(map)"), body.index(guarded_use))

    def test_entity_timers_lock_before_properties_or_destroy(self) -> None:
        for name, lock_call, guarded_use in (
            ("DogAlert", "Sync::LockCritterWithMap(dog)", "NpcPlanes::IsNoPlanes(dog)"),
            ("DeleteMobs", "Sync::LockCritterWithMap(mob)", "mob.NpcRole"),
            ("CowToAlive", "Sync::LockCritterWithMap(cow)", "cow.GetMap()"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                self.assertLess(body.index(lock_call), body.index(guarded_use))

    def test_finish_path_locks_current_quest_owner(self) -> None:
        attrs, body = function_contract("FinishQuest")

        self.assertIn("[[Async]]", attrs)
        owner_lock = body.index("LockQuestPlayer(Sync::SurvivingSnapshot(), player)")
        self.assertLess(owner_lock, body.index("player.KlamTorrCowboy"))
        self.assertLess(owner_lock, body.index("SetQuestGlobalState(ZERO_IDENT)"))

    def test_start_attack_keeps_map_and_owner_in_same_cover(self) -> None:
        _, body = function_contract("StartAtack")

        map_lock = body.index("Sync::Lock(map)")
        owner_lock = body.index("LockQuestPlayer(Sync::Snapshot(), questPlayer)")
        state_write = body.index("questPlayer.KlamTorrCowboy = 2")
        self.assertLess(map_lock, owner_lock)
        self.assertLess(owner_lock, state_write)

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
