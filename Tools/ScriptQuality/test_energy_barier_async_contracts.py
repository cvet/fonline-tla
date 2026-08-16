from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts/EnergyBarier.fos"
SYNC_SCRIPT_PATH = PROJECT_ROOT / "Scripts/EnergyBarierSync.fos"


def function_contract(name: str, path: Path = SCRIPT_PATH) -> tuple[str, str]:
    source = path.read_text(encoding="utf-8-sig")
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


class EnergyBarierAsyncContractTests(unittest.TestCase):
    def test_every_barrier_time_event_is_async(self) -> None:
        for name in (
            "InitBarier",
            "TurnOnBariers",
            "TurnOnBarier",
            "DisableForceField",
            "EnableForceField",
        ):
            with self.subTest(name=name):
                attrs, _ = function_contract(name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)

    def test_deferred_initialization_locks_item_and_stable_parent_map(self) -> None:
        _, body = function_contract("InitBarier")

        item_lock_at = body.index("Sync::Lock(barier)")
        map_id_at = body.index("ident mapId = barier.MapId")
        full_cover_at = body.index("Sync::Lock(barier, map)")
        topology_at = body.index("barier.MapId != mapId")
        initialize_at = body.rindex("InitBariers(barier)")
        self.assertLess(item_lock_at, map_id_at)
        self.assertLess(map_id_at, full_cover_at)
        self.assertLess(full_cover_at, topology_at)
        self.assertLess(topology_at, initialize_at)

    def test_mode_callbacks_lock_full_script_owned_cover(self) -> None:
        for name in ("TurnOnBariers", "DisableForceField", "EnableForceField"):
            with self.subTest(name=name):
                _, body = function_contract(name)
                self.assertLess(body.index("LockBariersNet(net)"), body.index("net.ChangeNetMode"))

        _, one_body = function_contract("TurnOnBarier")
        self.assertLess(one_body.index("LockBarierModes"), one_body.index("barier.ChangeMode"))

        helper_attrs, helper_body = function_contract("LockBarierModes", SYNC_SCRIPT_PATH)
        net_attrs, net_body = function_contract("LockBariersNet", SYNC_SCRIPT_PATH)
        self.assertIn("[[Async]]", helper_attrs)
        self.assertIn("[[Async]]", net_attrs)
        self.assertGreaterEqual(helper_body.count("Sync::Lock(entities)"), 2)
        self.assertIn("Sync::AddUniqueEntity(entities, map)", helper_body)
        self.assertIn("BarierModeEntitiesAreCovered", helper_body)
        self.assertIn("bariers[i].Barier.MapId != mapIds[i]", helper_body)
        self.assertIn("SameBariers(net, snapshot)", net_body)

    def test_network_schedules_only_one_auto_enable(self) -> None:
        _, body = function_contract("ChangeNetMode")

        self.assertIn("scheduleAutoEnable = scheduleAutoEnable || ShouldAutoEnable", body)
        self.assertEqual(body.count("Game.StartTimeEvent(BarrierOpenTime(), TurnOnBariers"), 1)
        self.assertLess(body.index("for (int i = 0;"), body.index("if (scheduleAutoEnable)"))
        self.assertLess(body.index("if (scheduleAutoEnable)"), body.index("NetState = mode"))

    def test_barrier_callbacks_do_not_call_game_sync_directly(self) -> None:
        for path in (SCRIPT_PATH, SYNC_SCRIPT_PATH):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
