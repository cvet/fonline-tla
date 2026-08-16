from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Sync.fos"


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


class SyncTransferContractTests(unittest.TestCase):
    def test_map_transfer_cover_includes_source_destination_and_location(self) -> None:
        attrs, body = function_contract("LockForTransferToMap")

        self.assertIn("[[Async]]", attrs)
        fixed_cover_at = body.index("fixedEntities.clone()")
        critter_at = body.index("AddUniqueEntity(initialCover, cr)")
        initial_lock_at = body.index("Lock(initialCover)")
        source_at = body.index("sourceMap = cr.GetMap()")
        location_at = body.index("destinationMap.GetLocation()")
        full_lock_at = body.index("Lock(transferCover)")
        source_check_at = body.index("cr.MapId != sourceMapId")
        location_check_at = body.index("destinationMap.GetLocation().Id != destinationLocationId")
        self.assertLess(fixed_cover_at, critter_at)
        self.assertLess(critter_at, initial_lock_at)
        self.assertLess(initial_lock_at, source_at)
        self.assertLess(initial_lock_at, location_at)
        self.assertLess(source_at, full_lock_at)
        self.assertLess(location_at, full_lock_at)
        self.assertLess(full_lock_at, source_check_at)
        self.assertLess(full_lock_at, location_check_at)

    def test_global_group_cover_collects_and_revalidates_every_source_map(self) -> None:
        attrs, body = function_contract("LockForTransferToGlobalWithGroup")

        self.assertIn("[[Async]]", attrs)
        participants_lock_at = body.index("Lock(participantsCover)")
        map_snapshot_at = body.index("sourceMapIds[i] = participants[i].MapId")
        source_map_at = body.index("participants[i].GetMap()")
        full_lock_at = body.index("Lock(transferCover)")
        topology_at = body.index("participants[i].MapId != sourceMapIds[i]")
        self.assertLess(participants_lock_at, map_snapshot_at)
        self.assertLess(participants_lock_at, source_map_at)
        self.assertLess(map_snapshot_at, full_lock_at)
        self.assertLess(source_map_at, full_lock_at)
        self.assertLess(full_lock_at, topology_at)

    def test_item_parent_cover_handles_every_ownership_kind(self) -> None:
        attrs, body = function_contract("LockItemWithParent")

        self.assertIn("[[Async]]", attrs)
        item_lock_at = body.index("Lock(item)")
        self.assertIn("ItemOwnership::MapHex", body)
        self.assertIn("ItemOwnership::CritterInventory", body)
        self.assertIn("ItemOwnership::ItemContainer", body)
        self.assertIn("ItemOwnership::Nowhere", body)
        self.assertLess(item_lock_at, body.index("Lock(item, map)"))
        self.assertLess(item_lock_at, body.index("Lock(item, cr)"))
        self.assertLess(item_lock_at, body.index("Lock(item, container)"))
        self.assertIn("item.MapId != mapId", body)
        self.assertIn("item.CritterId != critterId", body)
        self.assertIn("item.ContainerId != containerId", body)

    def test_map_parent_cover_locks_and_revalidates_location(self) -> None:
        attrs, body = function_contract("LockMapWithLocation")

        self.assertIn("[[Async]]", attrs)
        map_lock_at = body.index("Lock(map)")
        location_at = body.index("map.GetLocation()")
        full_lock_at = body.index("Lock(map, loc)")
        topology_at = body.index("map.GetLocation().Id != locationId")
        self.assertLess(map_lock_at, location_at)
        self.assertLess(location_at, full_lock_at)
        self.assertLess(full_lock_at, topology_at)

    def test_multi_critter_cover_collects_and_revalidates_current_maps(self) -> None:
        attrs, body = function_contract("LockCrittersWithMaps")

        self.assertIn("[[Async]]", attrs)
        fixed_cover_at = body.index("fixedEntities.clone()")
        critter_lock_at = body.index("Lock(critterCover)")
        map_snapshot_at = body.index("mapIds[i] = critters[i].MapId")
        map_at = body.index("critters[i].GetMap()")
        full_lock_at = body.index("Lock(fullCover)")
        topology_at = body.index("critters[i].MapId != mapIds[i]")
        self.assertLess(fixed_cover_at, critter_lock_at)
        self.assertLess(critter_lock_at, map_snapshot_at)
        self.assertLess(critter_lock_at, map_at)
        self.assertLess(map_snapshot_at, full_lock_at)
        self.assertLess(map_at, full_lock_at)
        self.assertLess(full_lock_at, topology_at)


if __name__ == "__main__":
    unittest.main()
