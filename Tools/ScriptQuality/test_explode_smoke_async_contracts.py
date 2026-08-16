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


class ExplodeSmokeAsyncContractTests(unittest.TestCase):
    def assert_async_time_event(self, attrs: str) -> None:
        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)

    def test_deferred_explosion_locks_charge_and_current_parent(self) -> None:
        attrs, body = function_contract("Scripts/Explode.fos", "DeferredExplode")

        self.assert_async_time_event(attrs)
        lock_at = body.index("Sync::LockItemWithParent(item)")
        self.assertLess(lock_at, body.index("item.ProtoId"))
        self.assertLess(lock_at, body.index("Game.DestroyItem(item)"))

    def test_mine_respawn_validates_payload_and_locks_map(self) -> None:
        attrs, body = function_contract("Scripts/Explode.fos", "RespawnTimerMine")

        self.assert_async_time_event(attrs)
        payload_at = body.index("values.length() < 9")
        lock_at = body.index("Sync::Lock(map)")
        add_at = body.index("map.AddItem")
        self.assertLess(payload_at, lock_at)
        self.assertLess(lock_at, add_at)

    def test_smoke_step_locks_map_and_optional_owner(self) -> None:
        attrs, body = function_contract("Scripts/SmokeGrenade.fos", "DoSmokeBlast")

        self.assert_async_time_event(attrs)
        self.assertIn("values.length() < 6", body)
        owner_at = body.index("Game.GetCritter(ownerId)")
        map_cover_at = body.index("Entity[] cover = {map}")
        owner_cover_at = body.index("Sync::AddUniqueEntity(cover, owner)")
        lock_at = body.index("Sync::Lock(cover)")
        skill_at = body.index("owner.SkillThrowing")
        map_access_at = body.index("Effects::PlaySound(map")
        self.assertLess(owner_at, lock_at)
        self.assertLess(map_cover_at, lock_at)
        self.assertLess(owner_cover_at, lock_at)
        self.assertLess(lock_at, skill_at)
        self.assertLess(lock_at, map_access_at)

    def test_smoke_cleanup_locks_each_item_and_parent(self) -> None:
        attrs, body = function_contract("Scripts/SmokeGrenade.fos", "DeleteSmokes")

        self.assert_async_time_event(attrs)
        self.assertLess(body.index("Sync::LockItemWithParent(item)"), body.index("Game.DestroyItem(item)"))

    def test_modules_do_not_call_game_sync_directly(self) -> None:
        for path in ("Scripts/Explode.fos", "Scripts/SmokeGrenade.fos"):
            with self.subTest(path=path):
                source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
                self.assertNotIn("Game.Sync(", source)


if __name__ == "__main__":
    unittest.main()
