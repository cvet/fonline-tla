from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def function_contract(path: str, name: str) -> tuple[str, str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if match is None:
        raise AssertionError(f"function {name} not found in {path}")

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
        raise AssertionError(f"function {name} has an unbalanced body in {path}")
    return match.group("attrs") or "", source[opening + 1:cursor - 1]


class VaultCityQuestAsyncContractTests(unittest.TestCase):
    def test_single_queue_timer_locks_critter_and_map(self) -> None:
        attrs, body = function_contract("Scripts/VcGuardsman.fos", "DoNextOrder")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::LockCritterWithMap(cr)")
        self.assertLess(lock_at, body.index("cr.ControlledByPlayer"))
        self.assertLess(lock_at, body.index("march.CheckOrderCompleted()"))

    def test_commander_helper_locks_saved_squad_and_maps(self) -> None:
        attrs, body = function_contract("Scripts/VcGuardsman.fos", "LockCommanderSquad")

        self.assertIn("[[Async]]", attrs)
        commander_lock = body.index("Sync::LockCritterWithMap(commander)")
        squad_read = body.index("commander.SquadMarchSquads.clone()")
        group_lock = body.index("Sync::LockCrittersWithMaps(participants)")
        self.assertLess(commander_lock, squad_read)
        self.assertLess(squad_read, group_lock)

    def test_commander_timers_lock_full_participant_cover(self) -> None:
        for name, guarded_use in (
            ("ResetCommander", "cmdr.Load()"),
            ("NextGuardOrder", "cmdr.Load()"),
        ):
            with self.subTest(name=name):
                attrs, body = function_contract("Scripts/VcGuardsman.fos", name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                self.assertLess(body.index("LockCommanderSquad("), body.index(guarded_use))

    def test_drill_start_locks_npc_player_and_maps_and_checks_same_map(self) -> None:
        attrs, body = function_contract("Scripts/VcGuardsman.fos", "TimeToStart")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::LockCrittersWithMaps(participants)")
        self.assertLess(lock_at, body.index("player.MapId != npc.MapId"))
        self.assertLess(lock_at, body.index("map.GetCritters"))

    def test_lynnet_delayed_speech_and_witnesses_are_covered(self) -> None:
        prisoner_attrs, prisoner_body = function_contract("Scripts/VcLynnet.fos", "PrisonerTalk")
        answer_attrs, answer_body = function_contract("Scripts/VcLynnet.fos", "Answer")

        self.assertIn("[[TimeEvent]]", prisoner_attrs)
        self.assertIn("[[Async]]", prisoner_attrs)
        self.assertLess(prisoner_body.index("Sync::LockCritterWithMap(cr)"), prisoner_body.index("Messaging::Say(cr"))

        self.assertIn("[[TimeEvent]]", answer_attrs)
        self.assertIn("[[Async]]", answer_attrs)
        group_lock = answer_body.index("Sync::LockCrittersWithMaps(participants)")
        self.assertLess(group_lock, answer_body.index("Messaging::Say(guards[i]"))
        self.assertLess(group_lock, answer_body.index("player.VCLynettForgery"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        for path in ("Scripts/VcGuardsman.fos", "Scripts/VcLynnet.fos"):
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
