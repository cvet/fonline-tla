from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Caravan.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool|Critter\[\]|Critter\?)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class CaravanAsyncContractTests(unittest.TestCase):
    def test_entity_time_events_are_async(self) -> None:
        for name in (
            "StartPrepareCaravan",
            "BeginCaravan",
            "PrepareCaravanDeferred",
            "StartCaravan",
            "DeleteLeader",
            "TransferToStartPos",
        ):
            with self.subTest(name=name):
                attrs, _ = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)

    def test_prepare_path_locks_search_results_and_final_leader(self) -> None:
        search_attrs, search_body = function_contract("GetCrittersByDialogId")
        prepare_attrs, prepare_body = function_contract("PrepareCaravan")
        transfer_attrs, transfer_body = function_contract("TransferToPos")

        self.assertIn("[[Async]]", search_attrs)
        self.assertLess(search_body.index("Sync::Lock(map)"), search_body.index("map.GetCritters"))
        self.assertLess(search_body.index("Sync::Lock(map, foundCrits)"), search_body.index("foundCrits[i].DialogId"))

        self.assertIn("[[Async]]", prepare_attrs)
        self.assertIn("PlaceLeaderCritterToPos", prepare_body)
        self.assertIn("CheckLeaderInPos", prepare_body)
        self.assertLess(prepare_body.rindex("Sync::LockCritterWithMap(leader)"), prepare_body.index("SetEvents(leader"))

        self.assertIn("[[Async]]", transfer_attrs)
        self.assertLess(transfer_body.index("Sync::LockForTransferToMap"), transfer_body.index("leader.TransferToMap"))

    def test_start_filters_same_map_members_and_transfers_the_group(self) -> None:
        attrs, body = function_contract("StartCaravanImpl")

        self.assertIn("[[Async]]", attrs)
        initial_cover_at = body.index("Sync::LockCritterWithMap(leader)")
        member_cover_at = body.index("Sync::Lock(leader, map, player)")
        policy_at = body.index("CanJoinPreparedCaravan")
        group_cover_at = body.index("Sync::LockForTransferToGlobalWithGroup")
        topology_at = body.index("caravanGroup[i].MapId != map.Id")
        setup_at = body.index("leader.SetupScript")
        transfer_at = body.index("leader.TransferToGlobalWithGroup")
        self.assertLess(initial_cover_at, member_cover_at)
        self.assertLess(member_cover_at, policy_at)
        self.assertIn("player.MapId == map.Id", body)
        self.assertLess(group_cover_at, topology_at)
        self.assertLess(topology_at, setup_at)
        self.assertLess(setup_at, transfer_at)
        self.assertNotIn("leader.TransferToGlobal()", body)

    def test_guard_creation_reacquires_new_critter_before_setup(self) -> None:
        attrs, body = function_contract("GetCritterGuard")

        self.assertIn("[[Async]]", attrs)
        create_at = body.index("map.AddCritter")
        full_cover_at = body.index("Sync::Lock(map, leader, guard)")
        setup_at = body.index("guard.SetupScript")
        self.assertLess(create_at, full_cover_at)
        self.assertLess(full_cover_at, setup_at)

    def test_stale_cleanup_events_validate_leader_identity(self) -> None:
        delete_attrs, delete_body = function_contract("DeleteLeader")
        transfer_attrs, transfer_body = function_contract("TransferToStartPos")

        self.assertIn("[[Async]]", delete_attrs)
        delete_lock_at = delete_body.index("Sync::LockCritterWithMap(leader)")
        identity_at = delete_body.index("li.CritterId != leader.Id")
        reset_at = delete_body.index("ci.CaravanReset()")
        destroy_at = delete_body.index("Game.DestroyCritter(leader)")
        self.assertLess(delete_lock_at, identity_at)
        self.assertLess(identity_at, reset_at)
        self.assertLess(reset_at, destroy_at)
        self.assertIn("li.CritterId = ZERO_IDENT", delete_body)

        self.assertIn("[[Async]]", transfer_attrs)
        self.assertLess(transfer_body.index("Sync::LockCritterWithMap(leader)"), transfer_body.index("ci.Leader.CritterId == leader.Id"))
        self.assertLess(transfer_body.index("ci.Leader.CritterId == leader.Id"), transfer_body.index("ci.Leader.TransferToPos(true)"))

    def test_dialog_entry_defers_start_and_modules_do_not_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
        redding_source = (PROJECT_ROOT / "Scripts/MapReddingMiners.fos").read_text(encoding="utf-8-sig")

        self.assertIn("Game.StartTimeEvent(Time::Asap(), StartCaravan, any(npc.CaravanCrvId))", source)
        self.assertNotIn("StartCaravanImpl(npc.CaravanCrvId)", source)
        self.assertIn("Game.StartTimeEvent(Time::Asap(), Caravan::PrepareCaravanDeferred, 3)", redding_source)
        self.assertNotIn("Caravan::PrepareCaravan(3)", redding_source)
        self.assertNotIn("Game.Sync(", source)
        self.assertNotIn("Game.Sync(", redding_source)


if __name__ == "__main__":
    unittest.main()
