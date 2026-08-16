from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def function_contract(path: str, name: str) -> tuple[str, str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool|Map\?)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class ReplicationAsyncContractTests(unittest.TestCase):
    def test_nearest_replicator_locks_maps_then_locations_before_distance_reads(self) -> None:
        attrs, body = function_contract("Scripts/Replication.fos", "GetNearReplicatorMap")

        self.assertIn("[[Async]]", attrs)
        first_lock = body.index("Sync::Lock(cover)")
        location_lookup = body.index("maps[i].GetLocation()")
        second_lock = body.index("Sync::Lock(cover)", first_lock + 1)
        distance_read = body.index("loc.WorldPos.x")
        self.assertLess(first_lock, location_lookup)
        self.assertLess(location_lookup, second_lock)
        self.assertLess(second_lock, distance_read)

    def test_replication_stabilizes_group_and_both_transfer_paths(self) -> None:
        attrs, body = function_contract("Scripts/Replication.fos", "ReplicateCritter")

        self.assertIn("[[Async]]", attrs)
        initial_lock = body.index("Sync::LockCritterWithMap(cr)")
        self.assertLess(initial_lock, body.index("cr.GetMap()"))
        self.assertLess(initial_lock, body.index("cr.GetItems(ItemProperty::Type, ItemType::Car)"))

        group_lock = body.index("GlobalmapGroup::LockGroupForMutation")
        find_encounter = body.index("Worldmap::FindEncounter")
        invite_lock = body.index("LockEncounterForInvite(encounterDescriptor)")
        invite = body.index("Worldmap::InviteToEncounter")
        car_transfer_lock = body.index("Sync::LockForTransferToMap(cr, mapTo)")
        car_transfer = body.index("cr.TransferToMap(mapTo")
        self.assertLess(group_lock, find_encounter)
        self.assertLess(find_encounter, invite_lock)
        self.assertLess(invite_lock, invite)
        self.assertLess(invite, car_transfer_lock)
        self.assertLess(car_transfer_lock, car_transfer)

        final_transfer_lock = body.rindex("Sync::LockForTransferToMap(cr, map)")
        final_transfer = body.rindex("cr.TransferToMap(map")
        post_transfer_lock = body.rindex("Sync::LockCritterWithMap(cr)")
        self.assertLess(final_transfer_lock, final_transfer)
        self.assertLess(final_transfer, post_transfer_lock)

    def test_enemy_stack_registry_handles_are_locked_before_type_read(self) -> None:
        attrs, body = function_contract("Scripts/EnemyStack.fos", "ClearEnemyStackNpc")

        self.assertIn("[[Async]]", attrs)
        full_lock = body.index("Sync::Lock(cover)")
        self.assertLess(full_lock, body.index("!enemy.ControlledByPlayer"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        for path in ("Scripts/Replication.fos", "Scripts/EnemyStack.fos"):
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
