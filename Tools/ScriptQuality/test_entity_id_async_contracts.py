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


class EntityIdAsyncContractTests(unittest.TestCase):
    def test_base_car_delete_locks_item_and_parent(self) -> None:
        attrs, body = function_contract("Scripts/Base.fos", "DeleteCar")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertLess(body.index("Sync::LockItemWithParent(car)"), body.index("Game.DestroyItem(car)"))

    def test_cave_player_signal_locks_critter_and_map(self) -> None:
        attrs, body = function_contract("Scripts/CaveMobs.fos", "PlayerHere")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::LockCritterWithMap(cr)")
        self.assertLess(lock_at, body.index("SendMessage::ToWhoSeesMe"))
        self.assertLess(lock_at, body.index("SendMessage::ToWhoISee"))

    def test_den_ghost_callbacks_lock_before_state_or_dialog(self) -> None:
        resurrect_attrs, resurrect_body = function_contract("Scripts/DenGhost.fos", "RessurectGhost")
        dialog_attrs, dialog_body = function_contract("Scripts/DenGhost.fos", "RunTreasureDialog")

        self.assertIn("[[TimeEvent]]", resurrect_attrs)
        self.assertIn("[[Async]]", resurrect_attrs)
        resurrect_lock_at = resurrect_body.index("Sync::LockCritterWithMap(ghost)")
        self.assertLess(resurrect_lock_at, resurrect_body.index("ghost.GetMap()"))
        self.assertLess(resurrect_lock_at, resurrect_body.index("CritterState::ToAlive"))

        self.assertIn("[[TimeEvent]]", dialog_attrs)
        self.assertIn("[[Async]]", dialog_attrs)
        self.assertLess(dialog_body.index("Sync::LockCritterWithMap(player)"), dialog_body.index("Dialogs::RunDialog"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        for path in ("Scripts/Base.fos", "Scripts/CaveMobs.fos", "Scripts/DenGhost.fos"):
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
