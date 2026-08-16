from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Hunter.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class HunterAsyncContractTests(unittest.TestCase):
    def test_barter_cleanup_locks_owner_and_items_before_batch_destroy(self) -> None:
        attrs, body = function_contract("DestroyItemsHough")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        payload_guard = body.index("values.length() < 2")
        item_lookup = body.index("Game.GetItem(values[i])")
        full_lock = body.index("Sync::Lock(cover)")
        ownership_read = body.index("items[i].CritterId")
        destroy = body.index("Game.DestroyItems(ownedItems)")
        self.assertLess(payload_guard, item_lookup)
        self.assertLess(item_lookup, full_lock)
        self.assertLess(full_lock, ownership_read)
        self.assertLess(ownership_read, destroy)

    def test_lure_locks_selected_registry_speaker_before_access(self) -> None:
        attrs, body = function_contract("Lure")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        snapshot = body.index("Sync::Snapshot()")
        speaker_lock = body.index("Sync::Lock(cover)")
        topology = body.index("speaker.MapId == map.Id")
        speech = body.index("Messaging::Say(speaker")
        self.assertLess(snapshot, speaker_lock)
        self.assertLess(speaker_lock, topology)
        self.assertLess(topology, speech)

    def test_rat_graph_filters_authored_roles_and_preserves_location_maps(self) -> None:
        attrs, body = function_contract("LockRatMoveGraph")

        self.assertIn("[[Async]]", attrs)
        location_lock = body.index("Sync::Lock(loc)")
        maps_lock = body.index("Sync::Lock(loc, map, mapTo)")
        hostile_query = body.index("HostileLocationQuest::NPC_ROLE_HOSTILE")
        player_query = body.index("CritterFindType::NonDeadPlayers")
        ally_query = body.index("HostileLocationQuest::NPC_ROLE_ALLY")
        graph_lock = body.index("Sync::LockCrittersWithMaps(participants, fixedCover)")
        topology = body.index("currentRats[i].MapId != mapId")
        self.assertLess(location_lock, maps_lock)
        self.assertLess(maps_lock, hostile_query)
        self.assertLess(hostile_query, graph_lock)
        self.assertLess(player_query, graph_lock)
        self.assertLess(ally_query, graph_lock)
        self.assertLess(graph_lock, topology)
        self.assertIn("currentRats.resize(5)", body)

    def test_rat_transfer_preserves_graph_cover_and_revalidates_destination(self) -> None:
        attrs, body = function_contract("MoveRat")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        graph_lock = body.index("LockRatMoveGraph")
        snapshot = body.index("Sync::Snapshot()")
        transfer_lock = body.index("Sync::LockForTransferToMap(cr, mapTo, graphCover)")
        transfer = body.index("cr.TransferToMap(mapTo")
        destination_check = body.index("cr.MapId != mapTo.Id")
        reschedule = body.index("Game.StartTimeEvent(Time::Seconds(Game.Random(1, 3)), MoveRat")
        self.assertLess(graph_lock, snapshot)
        self.assertLess(snapshot, transfer_lock)
        self.assertLess(transfer_lock, transfer)
        self.assertLess(transfer, destination_check)
        self.assertLess(destination_check, reschedule)

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
