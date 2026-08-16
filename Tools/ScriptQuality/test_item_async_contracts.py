from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ITEM_SOURCE = PROJECT_ROOT / "Scripts/Item.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = ITEM_SOURCE.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if match is None:
        raise AssertionError(f"function {name} not found in Scripts/Item.fos")

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
    return match.group("attrs"), source[opening + 1:cursor - 1]


class ItemAsyncContractTests(unittest.TestCase):
    def test_auto_close_door_keeps_the_full_script_owned_cover(self) -> None:
        attrs, body = function_contract("AutoCloseDoor")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

        door_lock_at = body.index("Sync::Lock(door)")
        opened_at = body.index("door.Opened")
        map_lock_at = body.index("Sync::Lock(door, map)")
        occupant_lookup_at = body.index("map.GetCritterOnHex")
        occupant_lock_at = body.index("Sync::Lock(door, map, cr)")
        occupant_read_at = body.index("cr.IsAlive")
        transfer_at = body.index("cr.TransferToMap")
        restored_cover_at = body.index("Sync::Lock(door, map)", transfer_at)
        switch_at = body.index("Lockers::SwitchLocker")

        self.assertLess(door_lock_at, opened_at)
        self.assertLess(map_lock_at, occupant_lookup_at)
        self.assertLess(occupant_lock_at, occupant_read_at)
        self.assertLess(occupant_lock_at, transfer_at)
        self.assertLess(transfer_at, restored_cover_at)
        self.assertLess(restored_cover_at, switch_at)
        self.assertNotIn("if (!Lockers::SwitchLocker", body)

    def test_deferred_destroy_locks_item_before_destroy(self) -> None:
        attrs, body = function_contract("DeferredDestroyItem")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertLess(body.index("Sync::LockItemWithParent(item)"), body.index("Game.DestroyItem(item)"))

    def test_item_callbacks_do_not_hide_engine_sync(self) -> None:
        source = ITEM_SOURCE.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)
        self.assertIn("Game.StartTimeEvent(delay, AutoCloseDoor, value)", source)


if __name__ == "__main__":
    unittest.main()
