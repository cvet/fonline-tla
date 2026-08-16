from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/MobWave.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool|Map\?)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class MobWaveAsyncContractTests(unittest.TestCase):
    def test_wave_lock_reloads_after_each_cover_expansion(self) -> None:
        attrs, body = function_contract("LockWaveForExecution")

        self.assertIn("[[Async]]", attrs)
        source_lock = body.index("Sync::Lock(map)")
        staged_load = body.index("staged.Load()")
        participants_lock = body.index("Sync::Lock(participantCover)")
        participants_reload = body.index("participantsLocked.Load()")
        full_lock = body.index("Sync::Lock(fullCover)")
        graph_reload = body.index("graphLocked.Load()")
        self.assertLess(source_lock, staged_load)
        self.assertLess(staged_load, participants_lock)
        self.assertLess(participants_lock, participants_reload)
        self.assertLess(participants_reload, full_lock)
        self.assertLess(full_lock, graph_reload)
        self.assertGreaterEqual(body.count("IsWaveGraphCurrent("), 2)

    def test_wave_graph_includes_mobs_targets_attackers_and_search_results(self) -> None:
        _, body = function_contract("CollectWaveParticipants")

        self.assertIn("mv.Mobs[i].MobId", body)
        self.assertIn("mv.Targets[i].TargetId", body)
        self.assertIn("mv.Targets[i].MobsAttack[j]", body)
        self.assertIn("searchTargets[i]", body)

        _, lock_body = function_contract("LockWaveForExecution")
        participant_maps = lock_body.index("participants[i].GetMap()")
        full_lock = lock_body.index("Sync::Lock(fullCover)")
        topology_check = lock_body.index("participants[i].MapId != participantMapIds[i]")
        self.assertLess(participant_maps, full_lock)
        self.assertLess(full_lock, topology_check)
        self.assertIn("destinationMap.GetLocation()", lock_body)

    def test_transit_preserves_wave_cover_before_engine_transfer(self) -> None:
        attrs, body = function_contract("DoActionTransferToMap")

        self.assertIn("[[Async]]", attrs)
        snapshot = body.index("Sync::Snapshot()")
        transfer_lock = body.index("Sync::LockForTransferToMap(mob, map, waveCover)")
        transfer = body.index("mob.TransferToMap(map")
        self.assertLess(snapshot, transfer_lock)
        self.assertLess(transfer_lock, transfer)

    def test_time_events_are_async_and_repeat_payload_is_bounded(self) -> None:
        for name in ("NextWaveStep", "DoRepeatStep", "DeleteSpawnedMob"):
            with self.subTest(name=name):
                attrs, _ = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)

        _, repeat_body = function_contract("DoRepeatStep")
        self.assertLess(repeat_body.index("values.length() < 2"), repeat_body.index("values[0]"))
        self.assertIn("repeatMinutes > 0", repeat_body)

        _, delete_body = function_contract("DeleteSpawnedMob")
        self.assertLess(delete_body.index("Sync::LockCritterWithMap(mob)"), delete_body.index("mob.IsDead()"))
        self.assertLess(delete_body.index("Sync::LockCritterWithMap(mob)"), delete_body.index("Game.DestroyCritter(mob)"))

    def test_callbacks_lock_then_reload_before_mutating_and_saving(self) -> None:
        _, next_body = function_contract("NextWaveStep")
        next_lock = next_body.index("LockWaveForExecution")
        next_reload = next_body.index("mv.Load()")
        next_execute = next_body.index("mv.DoStep()")
        next_save = next_body.index("mv.Save()")
        self.assertLess(next_lock, next_reload)
        self.assertLess(next_reload, next_execute)
        self.assertLess(next_execute, next_save)

        _, repeat_body = function_contract("DoRepeatStep")
        repeat_lock = repeat_body.index("LockWaveForExecution")
        repeat_reload = repeat_body.index("mv.Load()")
        repeat_execute = repeat_body.index("mv.RepeatStep()")
        repeat_save = repeat_body.index("mv.Save()")
        self.assertLess(repeat_lock, repeat_reload)
        self.assertLess(repeat_reload, repeat_execute)
        self.assertLess(repeat_execute, repeat_save)

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
