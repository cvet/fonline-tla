from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = PROJECT_ROOT / "Scripts/ReddGates.fos"


def function_contract(name: str) -> tuple[str, str]:
    source = SOURCE_PATH.read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if match is None:
        raise AssertionError(f"function {name} not found in Scripts/ReddGates.fos")

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


class ReddGatesAsyncContractTests(unittest.TestCase):
    def test_close_gates_locks_every_entity_before_use(self) -> None:
        attrs, body = function_contract("CloseGates")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

        gates_lock_at = body.index("Sync::Lock(gates)")
        map_position_at = body.index("gates.GetMapPosition")
        map_lock_at = body.index("Sync::Lock(gates, map)")
        occupant_lookup_at = body.index("map.GetCritterOnHex")
        occupant_lock_at = body.index("Sync::Lock(gates, map, cr)")
        transfer_at = body.index("cr.TransferToMap")
        restored_cover_at = body.index("Sync::Lock(gates, map)", transfer_at)
        switch_at = body.index("Lockers::SwitchLocker")

        self.assertLess(gates_lock_at, map_position_at)
        self.assertLess(map_lock_at, occupant_lookup_at)
        self.assertLess(occupant_lock_at, transfer_at)
        self.assertLess(transfer_at, restored_cover_at)
        self.assertLess(restored_cover_at, switch_at)

    def test_close_gates_retries_if_topology_changes(self) -> None:
        _, body = function_contract("CloseGates")

        self.assertIn("lockedMap !is map || lockedHex != gatesHex", body)
        self.assertIn("RetryCloseGates(gates, Time::Seconds(1))", body)
        self.assertIn("postMoveCr != null && postMoveCr !is cr", body)

    def test_redd_gates_does_not_call_game_sync_directly(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
