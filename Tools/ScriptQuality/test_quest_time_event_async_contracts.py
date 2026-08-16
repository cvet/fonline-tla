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


class QuestTimeEventAsyncContractTests(unittest.TestCase):
    def assert_async_time_event(self, attrs: str) -> None:
        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

    def test_android_radio_locks_item_and_current_owner(self) -> None:
        attrs, body = function_contract("Scripts/SeAndroid.fos", "AndroidRadio")

        self.assert_async_time_event(attrs)
        self.assertIn("values.length() < 4", body)
        lock_at = body.index("Sync::LockItemWithParent(item)")
        self.assertLess(lock_at, body.index("item.SeAndroidRadioListened"))
        self.assertLess(lock_at, body.index("item.GetCritter()"))
        self.assertLess(lock_at, body.index("item.Radio.Channel"))

    def test_android_awake_locks_both_critters_and_expected_map(self) -> None:
        attrs, body = function_contract("Scripts/SeAndroid.fos", "AwakePlayer")

        self.assert_async_time_event(attrs)
        pair_lock_at = body.index("Sync::LockCrittersWithMaps(critters)")
        map_cover_at = body.index("Sync::AddUniqueEntity(cover, map)")
        full_lock_at = body.index("Sync::Lock(cover)")
        topology_at = body.index("player.MapId != map.Id")
        reward_at = body.index("player.Experience += 4000")
        dialog_at = body.index("Dialogs::RunDialog(player, doctor, true)")
        self.assertLess(pair_lock_at, map_cover_at)
        self.assertLess(map_cover_at, full_lock_at)
        self.assertLess(full_lock_at, topology_at)
        self.assertLess(topology_at, reward_at)
        self.assertLess(topology_at, dialog_at)

    def test_bank_warning_locks_guard_player_and_maps(self) -> None:
        attrs, body = function_contract("Scripts/ReplicationBank.fos", "WarnGagPlayer")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::LockCrittersWithMaps(critters)")
        self.assertLess(lock_at, body.index("guard.IsSee(player)"))
        self.assertLess(lock_at, body.index("Messaging::SayShout(guard"))

    def test_bank_attack_clears_state_and_locks_pair_before_attack(self) -> None:
        attrs, body = function_contract("Scripts/ReplicationBank.fos", "AttackGagPlayer")

        self.assert_async_time_event(attrs)
        guard_lock_at = body.index("Sync::LockCritterWithMap(guard)")
        clear_at = body.index("guard.ReplBankeIsAttackGagPlayer = false")
        pair_lock_at = body.index("Sync::LockCrittersWithMaps(critters)")
        attack_at = body.index("NpcPlanes::AddAttackPlane(guard, 0, player)")
        self.assertLess(guard_lock_at, clear_at)
        self.assertLess(clear_at, pair_lock_at)
        self.assertLess(pair_lock_at, attack_at)

    def test_town_supply_locks_hostile_and_map_before_spawn(self) -> None:
        attrs, body = function_contract("Scripts/TownSupply.fos", "CallTownSupplyNext")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::LockCritterWithMap(hostile)")
        self.assertLess(lock_at, body.index("hostile.Level"))
        self.assertLess(lock_at, body.index("CallSupply(victimId, hostile, count)"))

    def test_smit_radio_locks_smit_and_map(self) -> None:
        attrs, body = function_contract("Scripts/NcrSmit.fos", "BeginRadioComm")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockCritterWithMap(smit)"), body.index("BeginRadioCom(smit)"))

    def test_signal_location_locks_before_hiding(self) -> None:
        attrs, body = function_contract("Scripts/SignalRocket.fos", "HideLocation")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::Lock(loc)"), body.index("loc.Hidden = true"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        paths = (
            "Scripts/SeAndroid.fos",
            "Scripts/ReplicationBank.fos",
            "Scripts/TownSupply.fos",
            "Scripts/NcrSmit.fos",
            "Scripts/SignalRocket.fos",
        )
        for path in paths:
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
