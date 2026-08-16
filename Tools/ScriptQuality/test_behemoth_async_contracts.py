from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/Behemoth.fos"


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


class BehemothAsyncContractTests(unittest.TestCase):
    def test_route_idle_revalidates_current_map_location_and_target(self) -> None:
        attrs, body = function_contract("BehemothIdle")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        initial_cover_at = body.index("Sync::LockCritterWithMapAndLocation(cr)")
        target_at = body.index("locTo = GetLocationTo(cr)")
        target_cover_at = body.index("Sync::LockCritterWithMapAndLocation(cr, fixedEntities)")
        target_check_at = body.index("currentLocTo !is locTo")
        route_at = body.index("RunOrderRoute(cr)")
        self.assertLess(initial_cover_at, target_at)
        self.assertLess(target_at, target_cover_at)
        self.assertLess(target_cover_at, target_check_at)
        self.assertLess(target_check_at, route_at)

    def test_camera_time_event_locks_player_map_and_location(self) -> None:
        attrs, body = function_contract("ShowCamera")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        player_lock_at = body.index("Sync::Lock(player)")
        map_cover_at = body.index("Sync::Lock(player, map)")
        location_at = body.index("Location loc = map.GetLocation()")
        full_cover_at = body.index("Sync::Lock(player, map, loc)")
        topology_at = body.index("map.GetLocation().Id != loc.Id")
        view_at = body.index("player.ViewMap")
        self.assertLess(player_lock_at, map_cover_at)
        self.assertLess(map_cover_at, location_at)
        self.assertLess(location_at, full_cover_at)
        self.assertLess(full_cover_at, topology_at)
        self.assertLess(topology_at, view_at)

    def test_behemoth_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
