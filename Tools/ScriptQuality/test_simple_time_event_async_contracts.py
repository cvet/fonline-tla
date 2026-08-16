from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def function_contract(path: str, name: str) -> tuple[str, str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)?void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class SimpleTimeEventAsyncContractTests(unittest.TestCase):
    def assert_async_time_event(self, attrs: str) -> None:
        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

    def test_kess_model_timers_lock_critter_and_map(self) -> None:
        for name in ("KessRanger", "KessPoliceman"):
            with self.subTest(name=name):
                attrs, body = function_contract("Scripts/NcrKess.fos", name)
                self.assert_async_time_event(attrs)
                self.assertLess(body.index("Sync::LockCritterWithMap(kess)"), body.index("kess.ModelNameBase"))

    def test_elevator_reset_locks_map_before_property_update(self) -> None:
        attrs, body = function_contract("Scripts/Elevator.fos", "ResetData")

        self.assert_async_time_event(attrs)
        self.assertIn("values.length() < 2", body)
        self.assertLess(body.index("Sync::Lock(map)"), body.index("map.ElevatorData.clone()"))

    def test_jukebox_timer_locks_item_and_parent(self) -> None:
        attrs, body = function_contract("Scripts/Jukebox.fos", "OffJukeBox")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockItemWithParent(item)"), body.index("item.IsShowAnim = false"))

    def test_klam_quest_reset_locks_critter_and_map(self) -> None:
        attrs, body = function_contract("Scripts/KlamJura.fos", "ResetVar")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockCritterWithMap(cr)"), body.index("cr.KlamKuklachev = 0"))

    def test_scanner_destroy_locks_item_and_parent(self) -> None:
        attrs, body = function_contract("Scripts/Navarro.fos", "DeleteScaner")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockItemWithParent(item)"), body.index("Game.DestroyItem(item)"))

    def test_map_timers_validate_payload_and_lock_map(self) -> None:
        callbacks = (
            ("Scripts/Resources.fos", "AddResourcesCount", "values.length() < 4", "map.ResourcesData.clone()"),
            ("Scripts/V13Goris.fos", "DclawKidBorn", "values.length() < 2", "DclawKid(map"),
        )
        for path, name, payload_check, access in callbacks:
            with self.subTest(path=path, name=name):
                attrs, body = function_contract(path, name)
                self.assert_async_time_event(attrs)
                self.assertIn(payload_check, body)
                self.assertLess(body.index("Sync::Lock(map)"), body.index(access))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        paths = (
            "Scripts/NcrKess.fos",
            "Scripts/Elevator.fos",
            "Scripts/Jukebox.fos",
            "Scripts/KlamJura.fos",
            "Scripts/Navarro.fos",
            "Scripts/Resources.fos",
            "Scripts/V13Goris.fos",
        )
        for path in paths:
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
