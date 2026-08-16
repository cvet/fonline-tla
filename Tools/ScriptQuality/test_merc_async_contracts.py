from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Merc.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?(?:void|bool|EventResult)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class MercAsyncContractTests(unittest.TestCase):
    def test_global_process_enters_async_idle_path(self) -> None:
        attrs, body = function_contract("MercGlobalProcess")

        self.assertIn("[[Event]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertIn("MercIdleImpl(cr)", body)

    def test_idle_locks_merc_master_and_maps_before_state_reads(self) -> None:
        attrs, body = function_contract("MercIdleImpl")

        self.assertIn("[[Async]]", attrs)
        merc_lock = body.index("Sync::LockCritterWithMap(merc)")
        master_id = body.index("ident masterId = merc.MercMasterId")
        master_lookup = body.index("Game.GetCritter(masterId)")
        pair_lock = body.index("Sync::LockCrittersWithMaps(pair)")
        master_state = body.index("master.IsDead()")
        self.assertLess(merc_lock, master_id)
        self.assertLess(master_id, master_lookup)
        self.assertLess(master_lookup, pair_lock)
        self.assertLess(pair_lock, master_state)

    def test_idle_prepares_map_and_global_group_covers_before_transfers(self) -> None:
        _, body = function_contract("MercIdleImpl")

        map_cover = body.index("Sync::LockForTransferToMap(merc, masterMap, pairCover)")
        map_transfer = body.index("merc.TransferToMap(masterMap")
        group_cover = body.index("GlobalmapGroup::LockGroupForMutation")
        charisma = body.index("leader.Charisma")
        global_transfer = body.index("merc.TransferToGlobalGroup(master)")
        self.assertLess(map_cover, map_transfer)
        self.assertLess(group_cover, charisma)
        self.assertLess(charisma, global_transfer)

    def test_release_locks_graph_and_rejects_stale_rehire(self) -> None:
        attrs, body = function_contract("ReleaseMerc")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        merc_lock = body.index("Sync::LockCritterWithMap(merc)")
        release_guard = body.index("CanReleaseMerc(merc.MercMasterId != ZERO_IDENT)")
        home_snapshot = body.index("ident homeMapId = merc.HomeMapId")
        destroy = body.index("Game.DestroyCritter(merc)")
        transfer_cover = body.index("Sync::LockForTransferToMap(merc, homeMap, releaseCover)")
        home_revalidation = body.index("merc.HomeMapId != homeMapId")
        transfer = body.index("merc.TransferToMap(homeMap")
        self.assertLess(merc_lock, release_guard)
        self.assertLess(release_guard, home_snapshot)
        self.assertLess(home_snapshot, destroy)
        self.assertLess(destroy, transfer_cover)
        self.assertLess(transfer_cover, home_revalidation)
        self.assertLess(home_revalidation, transfer)

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
