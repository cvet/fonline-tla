from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/GameEventReplicator.fos"


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


class GameEventReplicatorAsyncContractTests(unittest.TestCase):
    def test_cleanup_holds_map_cover_for_children_and_transfers(self) -> None:
        attrs, body = function_contract("DeleteSandbags")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::Lock(map)")
        self.assertLess(lock_at, body.index("map.GetCritters(CritterFindType::NonDeadPlayers)"))
        self.assertLess(lock_at, body.index("cr.TransferToGlobal()"))
        self.assertLess(lock_at, body.index("Game.DestroyItems(items)"))
        self.assertLess(lock_at, body.index("Game.DestroyCritter(npc)"))

    def test_tank_explosion_keeps_item_parent_critter_and_map_covered(self) -> None:
        attrs, body = function_contract("ExplodeReplTank")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        parent_lock_at = body.index("Sync::LockItemWithParent(item)")
        snapshot_at = body.index("Sync::Snapshot()")
        critter_at = body.index("Sync::AddUniqueEntity(cover, cr)")
        map_at = body.index("Sync::AddUniqueEntity(cover, map)")
        full_lock_at = body.index("Sync::Lock(cover)")
        quest_at = body.index("cr.GEReplExplodeTank")
        destroy_at = body.index("Game.DestroyItem(item)")
        self.assertLess(parent_lock_at, snapshot_at)
        self.assertLess(snapshot_at, critter_at)
        self.assertLess(snapshot_at, map_at)
        self.assertLess(critter_at, full_lock_at)
        self.assertLess(map_at, full_lock_at)
        self.assertLess(full_lock_at, quest_at)
        self.assertLess(full_lock_at, destroy_at)

    def test_tank_hex_is_not_read_after_item_destruction(self) -> None:
        _, body = function_contract("ExplodeReplTank")

        snapshot_at = body.index("mpos tankHex = item.Hex")
        destroy_at = body.index("Game.DestroyItem(item)")
        smoke_at = body.index("SmokeGrenade::SmokeBlast(map, tankHex")
        self.assertLess(snapshot_at, destroy_at)
        self.assertLess(destroy_at, smoke_at)
        self.assertNotIn("item.Hex", body[destroy_at:])

    def test_module_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
