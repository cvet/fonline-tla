from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def function_contract(path: str, name: str) -> tuple[str, str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8-sig")
    match = re.search(
        rf"(?P<attrs>(?:\s*\[\[[^\]\n]+\]\])+\s*)void\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
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


class DenSpeechTimeEventSyncTests(unittest.TestCase):
    def test_speech_time_events_lock_the_critter_and_map_before_messaging(self) -> None:
        callbacks = (
            ("Scripts/DenCooldude.fos", "Sing"),
            ("Scripts/DenKliff.fos", "Say"),
            ("Scripts/DenBarBekkyBoy.fos", "Announcement"),
            ("Scripts/DenBarBekkyBoy.fos", "AnnouncementMorning"),
        )

        for path, name in callbacks:
            with self.subTest(path=path, name=name):
                attrs, body = function_contract(path, name)
                self.assertIn("[[TimeEvent]]", attrs)
                self.assertIn("[[Async]]", attrs)
                lock_at = body.index("Sync::LockCritterWithMap")
                message_at = body.index("Messaging::")
                self.assertLess(lock_at, message_at)
                self.assertIn("Time::Seconds(1)", body)

    def test_virgin_return_time_event_locks_before_reading_or_moving_npc(self) -> None:
        attrs, body = function_contract("Scripts/DenVirgin.fos", "Check")

        self.assertIn("[[TimeEvent]]", attrs)
        self.assertIn("[[Async]]", attrs)
        lock_at = body.index("Sync::LockCritterWithMap")
        state_at = body.index("virgin.DenVirginCount")
        move_at = body.index("NpcPlanes::AddWalkPlane")
        self.assertLess(lock_at, state_at)
        self.assertLess(lock_at, move_at)
        self.assertIn("Time::Seconds(1)", body[:state_at])


if __name__ == "__main__":
    unittest.main()
