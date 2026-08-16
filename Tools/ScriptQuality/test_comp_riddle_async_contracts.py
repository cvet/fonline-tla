from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/CompRiddle.fos"


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


class CompRiddleAsyncContractTests(unittest.TestCase):
    def test_reset_locks_map_before_loading_or_saving_riddle(self) -> None:
        attrs, body = function_contract("ResetRiddle")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertIn("values.length() < 3", body)
        lock_at = body.index("Sync::Lock(map)")
        load_at = body.index("GetRiddleInfo(mapId")
        save_at = body.index("riddle.Save()")
        repeat_at = body.index("Game.StartTimeEvent")
        self.assertLess(lock_at, load_at)
        self.assertLess(load_at, save_at)
        self.assertLess(save_at, repeat_at)

    def test_camera_locks_player_each_location_and_selected_map_graph(self) -> None:
        attrs, body = function_contract("ShowCamera")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        player_lock_at = body.index("Sync::Lock(cr)")
        world_pos_at = body.index("playerWorldPos = cr.WorldPos")
        location_lock_at = body.index("Sync::Lock(cr, loc)")
        location_read_at = body.index("loc.WorldPos")
        map_at = body.index("Map map = loc.GetMapByIndex(0)")
        graph_lock_at = body.index("Sync::Lock(cr, loc, map)")
        topology_at = body.index("map.GetLocation().Id != loc.Id")
        view_at = body.index("cr.ViewMap")
        self.assertLess(player_lock_at, world_pos_at)
        self.assertLess(location_lock_at, location_read_at)
        self.assertLess(map_at, graph_lock_at)
        self.assertLess(graph_lock_at, topology_at)
        self.assertLess(topology_at, view_at)

    def test_comp_riddle_does_not_call_game_sync_directly(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")
        self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
