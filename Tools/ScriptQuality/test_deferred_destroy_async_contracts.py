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


class DeferredDestroyAsyncContractTests(unittest.TestCase):
    def assert_async_time_event(self, attrs: str) -> None:
        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

    def test_item_destroy_callbacks_lock_the_current_parent(self) -> None:
        callbacks = (
            ("Scripts/GameEventCaches.fos", "DeferredDestroyItem"),
            ("Scripts/SeAndroid.fos", "DefferedDestroyItem"),
        )
        for path, name in callbacks:
            with self.subTest(path=path, name=name):
                attrs, body = function_contract(path, name)
                self.assert_async_time_event(attrs)
                self.assertLess(body.index("Sync::LockItemWithParent(item)"), body.index("Game.DestroyItem(item)"))

    def test_location_destroy_locks_location(self) -> None:
        attrs, body = function_contract("Scripts/GameEventStorehouse.fos", "DeferredDestroyLocation")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::Lock(loc)"), body.index("Game.DestroyLocation(loc)"))

    def test_critter_destroy_locks_critter_and_source_map(self) -> None:
        attrs, body = function_contract("Scripts/SfInvasion.fos", "DeferredDestroyCritter")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockCritterWithMap(cr)"), body.index("Game.DestroyCritter(cr)"))

    def test_android_map_cleanup_locks_map_and_location(self) -> None:
        attrs, body = function_contract("Scripts/SeAndroid.fos", "DeferredDestroyMap")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockMapWithLocation(map)"), body.index("Game.DestroyLocation(map.GetLocation())"))

    def test_android_explosion_locks_map_before_map_access(self) -> None:
        attrs, body = function_contract("Scripts/SeAndroid.fos", "DeferredExplode")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::Lock(map)")
        self.assertLess(lock_at, body.index("Entrance::ParseEntries(map"))
        self.assertLess(lock_at, body.index("Explode::ExplodeEx(map"))

    def test_auto_garbage_callbacks_lock_the_target_topology(self) -> None:
        location_callbacks = (
            ("Scripts/Location.fos", "DeferredDestroyLocation", "Sync::Lock(loc)"),
            ("Scripts/VcGuardsman.fos", "DeleteQuestLocation", "Sync::Lock(loc)"),
            ("Scripts/NrWriKidnap.fos", "DeleteQuestLocation", "Sync::LockMapWithLocation(map)"),
        )
        for path, name, lock in location_callbacks:
            with self.subTest(path=path, name=name):
                attrs, body = function_contract(path, name)
                self.assert_async_time_event(attrs)
                self.assertLess(body.index(lock), body.index("AutoGarbage"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        paths = (
            "Scripts/GameEventCaches.fos",
            "Scripts/GameEventStorehouse.fos",
            "Scripts/Location.fos",
            "Scripts/SfInvasion.fos",
            "Scripts/SeAndroid.fos",
            "Scripts/VcGuardsman.fos",
            "Scripts/NrWriKidnap.fos",
        )
        for path in paths:
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
