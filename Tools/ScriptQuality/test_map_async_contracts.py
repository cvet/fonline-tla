from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def function_contract(path: str, name: str) -> tuple[str, str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)(?:void|bool)\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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
    return match.group("attrs"), source[opening + 1:cursor - 1]


class MapAsyncContractTests(unittest.TestCase):
    def test_coast_weather_locks_map_before_property_access(self) -> None:
        attrs, body = function_contract("Scripts/MapCoast.fos", "CoastLoop0")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertLess(body.index("Sync::Lock(map)"), body.index("map.RainCapacity"))

    def test_radiation_loop_uses_async_script_side_cover(self) -> None:
        attrs, body = function_contract("Scripts/MapRadiation.fos", "MapLoop")
        helper_attrs, helper_body = function_contract("Scripts/MapRadiation.fos", "AffectRadiationToAllCritters")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertIn("[[Async]]", helper_attrs)
        self.assertLess(helper_body.index("Sync::Lock(map)"), helper_body.index("map.MapRadiationMinDose"))
        self.assertLess(helper_body.index("Sync::Lock(map)"), helper_body.index("map.GetCritters"))

        receiver_lock_at = helper_body.index("Sync::Lock(map, cr)")
        topology_check_at = helper_body.index("cr.MapId != map.Id")
        dose_at = helper_body.index("Radiation::AffectRadiation(cr, value)")
        self.assertLess(receiver_lock_at, topology_check_at)
        self.assertLess(topology_check_at, dose_at)

    def test_modoc_wasp_timeout_locks_each_independent_entity(self) -> None:
        attrs, body = function_contract("Scripts/MapModoc.fos", "ResetWaspLoc")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertLess(body.index("Sync::Lock(loc)"), body.index("loc.AutoGarbage"))
        self.assertLess(body.index("Sync::Lock(cr)"), body.index("cr.ModJoeGiantWasp"))

    def test_primal_tribe_simple_time_events_lock_before_entity_use(self) -> None:
        natur_attrs, natur_body = function_contract("Scripts/MapPrimalTribe.fos", "NaturResp")
        delete_attrs, delete_body = function_contract("Scripts/MapPrimalTribe.fos", "DeleteRaider")

        self.assertIn("[[TimeEvent]]", natur_attrs)
        self.assertIn("[[Async]]", natur_attrs)
        self.assertLess(natur_body.index("Sync::Lock(map)"), natur_body.index("map.Id"))

        self.assertIn("[[TimeEvent]]", delete_attrs)
        self.assertIn("[[Async]]", delete_attrs)
        self.assertLess(delete_body.index("Sync::Lock(raider)"), delete_body.index("Game.DestroyCritter(raider)"))

    def test_primal_tribe_target_loops_lock_actor_map_and_target(self) -> None:
        citizen_attrs, citizen_body = function_contract("Scripts/MapPrimalTribe.fos", "CChangeTarget")
        raider_attrs, raider_body = function_contract("Scripts/MapPrimalTribe.fos", "RaiderChangeTarget")

        self.assertIn("[[TimeEvent]]", citizen_attrs)
        self.assertIn("[[Async]]", citizen_attrs)
        self.assertLess(citizen_body.index("Sync::LockCritterWithMap(crit)"), citizen_body.index("map.GetCritters"))
        self.assertLess(citizen_body.index("Sync::Lock(crit, map, target)"), citizen_body.index("NpcPlanes::AddAttackPlane"))

        self.assertIn("[[TimeEvent]]", raider_attrs)
        self.assertIn("[[Async]]", raider_attrs)
        self.assertLess(raider_body.index("Sync::LockCritterWithMap(raider)"), raider_body.index("map.GetCritters"))
        target_lock_at = raider_body.index("Sync::Lock(raider, map, target)")
        self.assertLess(target_lock_at, raider_body.index("NpcPlanes::AddAttackPlane"))

        walk_at = raider_body.index("NpcPlanes::AddWalkPlane")
        restored_cover_at = raider_body.index("Sync::Lock(raider, map)", walk_at)
        misc_at = raider_body.index("NpcPlanes::AddMiscPlane")
        self.assertLess(walk_at, restored_cover_at)
        self.assertLess(restored_cover_at, misc_at)

    def test_primal_tribe_quest_results_are_deferred_and_lock_each_player(self) -> None:
        attrs, body = function_contract("Scripts/MapPrimalTribe.fos", "DeferredSendQuestStat")
        run_attrs, run_body = function_contract("Scripts/MapPrimalTribe.fos", "RunRandom")
        source = (PROJECT_ROOT / "Scripts/MapPrimalTribe.fos").read_text(encoding="utf-8-sig")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        self.assertLess(body.index("ident[] players = QuestPlayers.clone()"), body.index("QuestPlayers.clear()"))
        self.assertLess(body.index("Sync::Lock(cr)"), body.index("cr.TribRaiderKillCount"))
        self.assertNotIn("cr.GetMap()", body)

        self.assertIn("[[TimeEvent]]", run_attrs)
        self.assertIn("[[Async]]", run_attrs)
        self.assertLess(run_body.index("Sync::LockCritterWithMap(crit)"), run_body.index("map.GetCritters"))
        self.assertNotRegex(source, r"(?<!Deferred)SendQuestStat\s*\(")

    def test_primal_tribe_raid_start_runs_only_in_async_job_with_full_covers(self) -> None:
        start_attrs, start_body = function_contract("Scripts/MapPrimalTribe.fos", "StartAttack")
        impl_attrs, impl_body = function_contract("Scripts/MapPrimalTribe.fos", "StartAttackImpl")
        spawn_attrs, spawn_body = function_contract("Scripts/MapPrimalTribe.fos", "SpawnRaiders")
        one_attrs, one_body = function_contract("Scripts/MapPrimalTribe.fos", "SpawnRaider")
        _, enter_body = function_contract("Scripts/MapPrimalTribe.fos", "PlayerInMap")

        self.assertIn("[[TimeEvent]]", start_attrs)
        self.assertIn("[[Async]]", start_attrs)
        self.assertIn("[[Async]]", impl_attrs)
        self.assertIn("[[Async]]", spawn_attrs)
        self.assertIn("[[Async]]", one_attrs)
        self.assertIn("StartAttackImpl()", start_body)
        self.assertIn("SpawnRaiders", impl_body)

        map_lock_at = spawn_body.index("Sync::Lock(map)")
        raiders_at = spawn_body.index("map.GetCritters")
        cover_at = spawn_body.index("Sync::Lock(map, raiders)")
        destroy_at = spawn_body.index("Game.DestroyCritters")
        restored_at = spawn_body.index("Sync::Lock(map)", destroy_at)
        self.assertLess(map_lock_at, raiders_at)
        self.assertLess(cover_at, destroy_at)
        self.assertLess(destroy_at, restored_at)
        self.assertLess(spawn_body.index("Sync::Lock(crit)"), spawn_body.index("crit.TribSulikRaid"))
        self.assertLess(spawn_body.index("Sync::Lock(map, citizen)"), spawn_body.index("citizen.IsNoHome"))

        add_at = one_body.index("map.AddCritter")
        new_cover_at = one_body.index("Sync::Lock(map, raider)")
        subscribe_at = one_body.index("raider.OnDead.Subscribe")
        self.assertLess(add_at, new_cover_at)
        self.assertLess(new_cover_at, subscribe_at)

        self.assertNotIn("StartAttackImpl()", enter_body)
        self.assertIn("Game.StartTimeEvent(Time::Asap(), StartAttack)", enter_body)

    def test_map_callbacks_do_not_call_game_sync_directly(self) -> None:
        for path in (
            "Scripts/MapCoast.fos",
            "Scripts/MapModoc.fos",
            "Scripts/MapPrimalTribe.fos",
            "Scripts/MapRadiation.fos",
        ):
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
