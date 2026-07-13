#!/usr/bin/env python3
"""Focused pure-Python resilience checks for the TLA quest runner."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tla_quest_runner as quests  # noqa: E402 - import the sibling runner under test.


class FakeBridge:
    def __init__(self, observation: dict | None, on_act=None) -> None:
        self.observation = observation
        self.on_act = on_act
        self.commands: list[tuple[str, dict]] = []

    def observe(self) -> dict:
        if self.observation is None:
            raise quests.BridgeError("connection closed")
        return self.observation

    def observe_safe(self) -> dict | None:
        return self.observation

    def act(self, command_type: str, **params) -> dict:
        self.commands.append((command_type, params))
        if self.on_act is not None:
            self.on_act(self, command_type, params)
        return {}

    def events(self, _after_seq=0, _limit=500) -> list[dict]:
        return []

    def close(self) -> None:
        pass


def map_observation(proto_id: str) -> dict:
    return {
        "hasMap": True,
        "map": {"protoId": proto_id, "width": 200, "height": 200},
        "chosen": {"hexX": 1, "hexY": 1},
        "critters": [],
        "dialog": {"active": False},
        "screen": {"modalActive": False},
    }


class QuestMapTransferTests(unittest.TestCase):
    def test_same_map_is_a_fast_path_without_qa_transfer(self) -> None:
        observation = map_observation("arroyo")
        bridge = FakeBridge(observation)

        result = quests.teleport_map(bridge, "arroyo", timeout=0)

        self.assertIs(result, observation)
        self.assertEqual(bridge.commands, [])

    def test_location_map_syntax_uses_the_map_proto(self) -> None:
        observation = map_observation("vcity_courtyard")
        bridge = FakeBridge(observation)

        result = quests.teleport_map(bridge, "vault_city/vcity_courtyard", timeout=0)

        self.assertIs(result, observation)
        self.assertEqual(
            quests.expected_map_proto("vault_city/vcity_courtyard"),
            "vcity_courtyard",
        )
        self.assertEqual(bridge.commands, [])

    def test_timeout_reports_the_expected_and_actual_map(self) -> None:
        bridge = FakeBridge(map_observation("den"))

        with self.assertRaisesRegex(
            quests.BridgeError,
            r"expected map arroyo, observed den",
        ):
            quests.teleport_map(bridge, "arroyo", timeout=0)

        self.assertEqual(bridge.commands, [("qa_teleport_map", {"stringArg": "arroyo"})])

    def test_timeout_reports_lost_observation_after_the_command(self) -> None:
        def disconnect(bridge: FakeBridge, command_type: str, _params: dict) -> None:
            if command_type == "qa_teleport_map":
                bridge.observation = None

        bridge = FakeBridge(map_observation("den"), disconnect)

        with self.assertRaisesRegex(quests.BridgeError, "observation unavailable after command"):
            quests.teleport_map(bridge, "arroyo", timeout=0)


class QuestDialogApproachTests(unittest.TestCase):
    def test_hex_neighbours_follow_engine_column_parity_and_map_bounds(self) -> None:
        self.assertEqual(
            quests.adjacent_hexes(10, 20),
            [(11, 20), (11, 21), (10, 21), (9, 21), (9, 20), (10, 19)],
        )
        self.assertEqual(
            quests.adjacent_hexes(11, 20),
            [(12, 20), (12, 19), (11, 19), (10, 19), (10, 20), (11, 21)],
        )
        self.assertEqual(
            quests.npc_approach_hexes({"hexX": 0, "hexY": 0}, {"width": 2, "height": 2}),
            [(1, 0), (1, 1), (0, 1)],
        )

    def test_dialog_open_checks_teleport_and_tries_the_next_neighbour(self) -> None:
        npc = {"id": 77, "hexX": 10, "hexY": 20}
        observation = map_observation("arroyo")
        observation["chosen"] = {"hexX": 5, "hexY": 5}
        observation["critters"] = [dict(npc)]

        def on_act(bridge: FakeBridge, command_type: str, params: dict) -> None:
            if command_type == "qa_teleport_hex" and (params["x"], params["y"]) == (11, 21):
                bridge.observation["chosen"] = {"hexX": 11, "hexY": 21}
            elif command_type == "talk_to":
                bridge.observation["dialog"] = {"active": True}

        bridge = FakeBridge(observation, on_act)

        reached_hex = quests.open_dialog_near_npc(
            bridge,
            npc,
            teleport_timeout=0,
            dialog_timeout=0,
        )

        self.assertEqual(reached_hex, (11, 21))
        self.assertEqual(
            bridge.commands,
            [
                ("qa_teleport_hex", {"x": 11, "y": 20}),
                ("qa_teleport_hex", {"x": 11, "y": 21}),
                ("clear_actions", {}),
                ("talk_to", {"targetId": 77}),
            ],
        )

    def test_missing_observation_is_an_explicit_dialog_error(self) -> None:
        bridge = FakeBridge(None)

        with self.assertRaisesRegex(quests.DialogOpenError, "client observation unavailable"):
            quests.open_dialog_near_npc(bridge, {"id": 77, "hexX": 10, "hexY": 20})


class QuestStageProgressTests(unittest.TestCase):
    def test_completed_monotonic_quest_skips_all_earlier_stages(self) -> None:
        observation = map_observation("vcity_courtyard")
        observation["hasChosen"] = True
        observation["quests"] = [{"name": "CritterProperty::ArroyoCassidyLetter", "value": 2}]
        bridge = FakeBridge(observation)
        args = SimpleNamespace(
            quest="cassidy_letter",
            host="127.0.0.1",
            port=43011,
            token="",
            timeout=1.0,
            register=False,
            name="CompletedQuest",
            login_timeout=1.0,
            require_exercised=False,
        )

        with mock.patch.object(quests, "Bridge", return_value=bridge):
            report = quests.run(args)

        self.assertTrue(report["ok"])
        self.assertEqual(report["final_quest_value"], 2)
        self.assertEqual([stage["already_satisfied"] for stage in report["stages"]], [True, True])
        self.assertEqual([stage["dialog_steps"] for stage in report["stages"]], [0, 0])
        self.assertFalse(report["exercised"])
        self.assertEqual(report["transitions_verified"], 0)
        self.assertEqual(bridge.commands, [])

        args.require_exercised = True
        with mock.patch.object(quests, "Bridge", return_value=bridge):
            strict_report = quests.run(args)

        self.assertFalse(strict_report["ok"])
        self.assertIn("no transition", strict_report["error"])

    def test_exact_mode_does_not_accept_a_later_value(self) -> None:
        self.assertFalse(quests.quest_target_reached(2, 1, "exact"))
        self.assertTrue(quests.quest_target_reached(1, 1, "exact"))


if __name__ == "__main__":
    unittest.main()
