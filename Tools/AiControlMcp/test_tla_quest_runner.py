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
        self._events: list[dict] = []
        self._qa_request_id = 1

    def observe(self) -> dict:
        if self.observation is None:
            raise quests.BridgeError("connection closed")
        return self.observation

    def observe_safe(self) -> dict | None:
        return self.observation

    def act(self, command_type: str, **params) -> dict:
        self.commands.append((command_type, params))
        if command_type == "qa_get_prop" and self.observation is not None:
            value = quests.quest_value(self.observation, params["stringArg"])
            self._events.append({
                "seq": len(self._events) + 1,
                "event": {
                    "type": "qa_prop_value",
                    "prop": params["stringArg"],
                    "value": value,
                    "requestId": params.get("intArg", 0),
                },
            })
        if self.on_act is not None:
            self.on_act(self, command_type, params)
        return {}

    def events(self, after_seq=0, limit=500) -> list[dict]:
        return [event for event in self._events if event["seq"] > after_seq][:limit]

    def next_qa_request_id(self) -> int:
        request_id = self._qa_request_id
        self._qa_request_id += 1
        return request_id

    def close(self) -> None:
        pass


class TraceBridge(FakeBridge):
    def __init__(self, quest_value: int = 0, first_meeting: bool = False) -> None:
        observation = map_observation("arroyo")
        observation.update({
            "hasChosen": True,
            "chosen": {"hexX": 11, "hexY": 20},
            "quests": [{"name": "CritterProperty::TraceQuest", "value": quest_value}],
            "critters": [{
                "id": 77,
                "protoId": "TraceNpc",
                "dialogId": "trace_dialog",
                "hexX": 10,
                "hexY": 20,
            }],
        })
        super().__init__(observation)
        self.node = "closed"
        self.first_meeting = first_meeting
        self.dialog_opens = 0
        self.dropped_prop_reads = 0
        self.dropped_prop_writes = 0

    def _set_quest(self, value: int) -> None:
        self.observation["quests"][0]["value"] = value

    def _set_dialog(self, node: str) -> None:
        self.node = node
        if node == "closed":
            self.observation["dialog"] = {"active": False}
        elif node == "root":
            self.observation["dialog"] = {
                "active": True,
                "dialogId": "trace_dialog",
                "text": "Чем могу помочь?",
                "answers": ["Сразу всё сделано.", "Есть работа?", "[Уходите]"],
            }
        elif node == "intro":
            self.observation["dialog"] = {
                "active": True,
                "dialogId": "trace_dialog",
                "text": "Мы раньше не встречались.",
                "answers": ["Кто вы?", "[Уходите]"],
            }
        elif node == "offer":
            self.observation["dialog"] = {
                "active": True,
                "dialogId": "trace_dialog",
                "text": "Отнесёшь письмо?",
                "answers": ["Нет.", "Да, конечно."],
            }

    def act(self, command_type: str, **params) -> dict:
        self.commands.append((command_type, params))
        if command_type == "qa_get_prop":
            if self.dropped_prop_reads > 0:
                self.dropped_prop_reads -= 1
                return {}
            value = quests.quest_value(self.observation, params["stringArg"])
            self._events.append({
                "seq": len(self._events) + 1,
                "event": {
                    "type": "qa_prop_value",
                    "prop": params["stringArg"],
                    "value": value,
                    "requestId": params.get("intArg", 0),
                },
            })
        elif command_type == "qa_set_prop":
            if self.dropped_prop_writes > 0:
                self.dropped_prop_writes -= 1
            else:
                self._set_quest(int(params["intArg"]))
                self._events.append({
                    "seq": len(self._events) + 1,
                    "event": {
                        "type": "qa_prop_set",
                        "prop": params["stringArg"],
                        "value": int(params["intArg"]),
                        "requestId": params.get("x", 0),
                    },
                })
        elif command_type == "qa_teleport_hex":
            self.observation["chosen"] = {"hexX": params["x"], "hexY": params["y"]}
        elif command_type == "talk_to":
            self.dialog_opens += 1
            self._set_dialog("intro" if self.first_meeting else "root")
        elif command_type == "close_dialog":
            self._set_dialog("closed")
        elif command_type == "dialog_answer":
            index = int(params["intArg"])
            if self.node == "intro":
                self.first_meeting = False
                self._set_dialog("closed")
            elif self.node == "root" and index == 0:
                self._set_quest(self.observation["quests"][0]["value"] + 2)
                self._set_dialog("closed")
            elif self.node == "root" and index == 1:
                self._set_dialog("offer")
            elif self.node == "offer" and index == 1:
                self._set_quest(self.observation["quests"][0]["value"] + 1)
                self._set_dialog("closed")
            else:
                self._set_dialog("closed")
        return {}


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

    def test_qa_teleport_retries_when_the_first_async_lock_is_busy(self) -> None:
        attempts = 0

        def accept_second(bridge: FakeBridge, command_type: str, params: dict) -> None:
            nonlocal attempts
            if command_type != "qa_teleport_hex":
                return
            attempts += 1
            if attempts == 2:
                bridge.observation["chosen"] = {"hexX": params["x"], "hexY": params["y"]}

        bridge = FakeBridge(map_observation("arroyo"), accept_second)

        observation = quests.teleport_chosen_hex(
            bridge, (11, 20), timeout=1.0, retry_interval=0.0
        )

        self.assertIsNotNone(observation)
        self.assertEqual(attempts, 2)

    def test_dialog_open_retries_talk_from_the_confirmed_hex(self) -> None:
        npc = {"id": 77, "hexX": 10, "hexY": 20}
        observation = map_observation("arroyo")
        observation["chosen"] = {"hexX": 11, "hexY": 20}
        observation["critters"] = [dict(npc)]
        talk_attempts = 0

        def accept_second_talk(bridge: FakeBridge, command_type: str, _params: dict) -> None:
            nonlocal talk_attempts
            if command_type != "talk_to":
                return
            talk_attempts += 1
            if talk_attempts == 2:
                bridge.observation["dialog"] = {"active": True}

        bridge = FakeBridge(observation, accept_second_talk)

        reached_hex = quests.open_dialog_near_npc(
            bridge,
            npc,
            dialog_timeout=0.1,
            talk_retry_interval=0,
        )

        self.assertEqual(reached_hex, (11, 20))
        self.assertEqual(talk_attempts, 2)

    def test_dialog_failure_reports_server_talk_diagnostic(self) -> None:
        npc = {"id": 77, "hexX": 10, "hexY": 20}
        observation = map_observation("arroyo")
        observation["chosen"] = {"hexX": 11, "hexY": 20}
        observation["critters"] = [dict(npc)]

        def diagnose(bridge: FakeBridge, command_type: str, _params: dict) -> None:
            if command_type == "talk_to":
                bridge._events.append({
                    "seq": len(bridge._events) + 1,
                    "event": {
                        "type": "talk_diagnostic",
                        "npcId": 77,
                        "status": "npc_cannot_see_player",
                        "distance": 1,
                        "talkDistance": 3,
                        "playerSeesNpc": True,
                        "npcSeesPlayer": False,
                    },
                })

        bridge = FakeBridge(observation, diagnose)

        with self.assertRaisesRegex(
            quests.DialogOpenError,
            r"server=npc_cannot_see_player, distance=1/3, playerSeesNpc=true, npcSeesPlayer=false",
        ):
            quests.open_dialog_near_npc(
                bridge,
                npc,
                teleport_timeout=0,
                dialog_timeout=0,
            )


class QuestDialogTraceTests(unittest.TestCase):
    def test_property_name_and_keyword_normalization(self) -> None:
        self.assertEqual(quests.normalize_property_name("CritterProperty::ArroyoCassidyLetter"), "ArroyoCassidyLetter")
        self.assertEqual(quests.normalize_property_name("Critter.ArroyoCassidyLetter"), "ArroyoCassidyLetter")
        self.assertEqual(
            quests.answer_keyword_set("[Да, конечно, я отнесу письмо!]"),
            ["да, конечно, я отнесу письмо", "конечно", "отнесу", "письмо"],
        )

    def test_trace_prioritizes_authored_armour_grease_leads(self) -> None:
        answers = [
            "Да. Я хотел бы спросить тебя кое о чём.",
            "Я заметил... Твоя броня совсем поржавела.",
        ]

        selectors = quests.trace_answer_selectors(answers)

        self.assertEqual(selectors[0]["text"], answers[1])

    def test_trace_prioritizes_repair_leads_over_refusal(self) -> None:
        answers = [
            "Нет, мне нужно кое-что другое.",
            "Да могу посмотреть, руки у меня вроде не из задницы растут.",
        ]

        selectors = quests.trace_answer_selectors(answers)

        self.assertEqual(selectors[0]["text"], answers[1])

    def test_trace_prioritizes_virginia_quest_lead(self) -> None:
        answers = [
            "Что у тебя можно поесть?",
            "Что произошло в городе за последнее время?",
            "Пока.",
        ]

        selectors = quests.trace_answer_selectors(answers)

        self.assertEqual(selectors[0]["text"], answers[1])

    def test_trace_replays_randomized_text_by_stable_slot(self) -> None:
        selector = {
            "index": 1,
            "text": "А ты чего тут стоишь?",
            "answer_count": 3,
        }

        self.assertEqual(
            quests.resolve_trace_answer(
                ["Первый ответ", "Чего сторожишь тут?", "Последний ответ"],
                selector,
            ),
            1,
        )
        self.assertIsNone(
            quests.resolve_trace_answer(
                ["Чего сторожишь тут?", "Последний ответ"],
                selector,
            )
        )

    def test_trace_prefers_unique_exact_text_after_answer_reordering(self) -> None:
        selector = {
            "index": 1,
            "text": "А ты чего тут стоишь?",
            "answer_count": 3,
        }

        self.assertEqual(
            quests.resolve_trace_answer(
                ["Первый ответ", "Второй ответ", "А ты чего тут стоишь?", "Выход"],
                selector,
            ),
            2,
        )

    def test_replay_signature_ignores_random_greeting_and_exit_variant(self) -> None:
        first = {
            "dialog": {
                "active": True,
                "dialogId": "trace_dialog",
                "text": "Снова ты?",
                "answers": ["Есть работа?", "Ничего."],
            }
        }
        second = {
            "dialog": {
                "active": True,
                "dialogId": "trace_dialog",
                "text": "Что тебе налить?",
                "answers": ["Есть работа?", "Ладно, неважно. Пока."],
            }
        }

        self.assertEqual(
            quests.dialog_replay_signature(first),
            quests.dialog_replay_signature(second),
        )

    def test_authoritative_read_retries_a_dropped_async_response(self) -> None:
        bridge = TraceBridge(quest_value=3)
        bridge.dropped_prop_reads = 1

        value = quests.read_quest_authoritative(
            bridge, "TraceQuest", timeout=1.0, attempts=3
        )

        self.assertEqual(value, 3)
        self.assertEqual(
            [command for command, _params in bridge.commands].count("qa_get_prop"),
            2,
        )

    def test_authoritative_read_ignores_a_stale_correlated_response(self) -> None:
        class StaleThenCurrentBridge(TraceBridge):
            def act(self, command_type: str, **params) -> dict:
                if command_type == "qa_get_prop":
                    self._events.append({
                        "seq": len(self._events) + 1,
                        "event": {
                            "type": "qa_prop_value",
                            "prop": params["stringArg"],
                            "value": 0,
                            "requestId": params["intArg"] - 1,
                        },
                    })
                return super().act(command_type, **params)

        bridge = StaleThenCurrentBridge(quest_value=3)

        value = quests.quest_value_server(bridge, "TraceQuest", timeout=0.03)

        self.assertEqual(value, 3)

    def test_property_setup_retries_a_dropped_async_write(self) -> None:
        bridge = TraceBridge(quest_value=0)
        bridge.dropped_prop_writes = 1

        value = quests.set_quest_value(
            bridge, "TraceQuest", 6, timeout=0.1, retry_interval=0
        )

        self.assertEqual(value, 6)
        self.assertEqual(quests.quest_value(bridge.observation, "TraceQuest"), 6)
        self.assertEqual(
            [command for command, _params in bridge.commands].count("qa_set_prop"),
            2,
        )
        request_ids = {
            params["x"]
            for command, params in bridge.commands
            if command == "qa_set_prop"
        }
        self.assertEqual(len(request_ids), 1)
        self.assertNotEqual(request_ids, {0})

    def test_trace_ranks_stage_advance_and_keeps_node_paths(self) -> None:
        bridge = TraceBridge()
        npc = bridge.observation["critters"][0]

        trace = quests.trace_dialog_paths(
            bridge,
            npc,
            "trace_dialog",
            "TraceQuest",
            0,
            max_depth=3,
            max_paths=12,
            answer_timeout=0,
            reset_timeout=0,
        )

        self.assertFalse(trace["truncated"])
        self.assertEqual(trace["branch_errors"], [])
        self.assertEqual(
            [(candidate["rank"], candidate["answer"], candidate["stage_advance"])
             for candidate in trace["candidates"]],
            [(1, "Сразу всё сделано.", 2), (2, "Да, конечно.", 1)],
        )
        self.assertEqual(
            [step["answer"] for step in trace["candidates"][1]["node_path"]],
            ["Есть работа?", "Да, конечно."],
        )

    def test_trace_stabilizes_a_one_shot_first_meeting_root(self) -> None:
        bridge = TraceBridge(first_meeting=True)

        trace = quests.trace_dialog_paths(
            bridge,
            bridge.observation["critters"][0],
            "trace_dialog",
            "TraceQuest",
            0,
            max_depth=3,
            max_paths=12,
            answer_timeout=0,
            reset_timeout=0,
        )

        self.assertEqual(trace["root_stabilization_opens"], 2)
        self.assertEqual(trace["root_rebases"], 1)
        self.assertEqual(
            [candidate["answer"] for candidate in trace["candidates"]],
            ["Сразу всё сделано.", "Да, конечно."],
        )

    def test_trace_reports_an_internal_wall_clock_limit(self) -> None:
        bridge = TraceBridge()

        trace = quests.trace_dialog_paths(
            bridge,
            bridge.observation["critters"][0],
            "trace_dialog",
            "TraceQuest",
            0,
            max_depth=3,
            max_paths=12,
            answer_timeout=0,
            reset_timeout=0,
            max_seconds=0,
        )

        self.assertTrue(trace["time_limit_reached"])
        self.assertTrue(trace["truncated"])
        self.assertEqual(trace["explored_paths"], 0)

    def test_run_trace_restores_the_original_flag(self) -> None:
        bridge = TraceBridge(quest_value=4)
        args = SimpleNamespace(
            flag="CritterProperty::TraceQuest",
            trace_map="arroyo",
            npc="TraceNpc",
            dialog="trace_dialog",
            npc_hex=None,
            setup_json="",
            trace_max_depth=3,
            trace_max_paths=12,
            trace_max_candidates=8,
            trace_max_seconds=30,
            trace_answer_timeout=0,
            trace_reset_timeout=0,
            host="127.0.0.1",
            port=43011,
            token="",
            timeout=1.0,
            register=False,
            name="TraceRunner",
            login_timeout=1.0,
            map_timeout=93.0,
        )

        with (
            mock.patch.object(quests, "Bridge", return_value=bridge),
            mock.patch.object(quests, "teleport_map", wraps=quests.teleport_map) as teleport,
        ):
            report = quests.run_trace(args)

        self.assertTrue(report["ok"])
        teleport.assert_called_once_with(bridge, "arroyo", timeout=93.0)
        self.assertTrue(report["flag_restored"])
        self.assertEqual(report["original_value"], 4)
        self.assertEqual(bridge.observation["quests"][0]["value"], 4)


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
            map_timeout=90.0,
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
