#!/usr/bin/env python3
"""Focused compatibility checks for MCP navigation over live TLA observations."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parent))

import ai_control_mcp as mcp  # noqa: E402


class NavigationObservationCompatibilityTests(unittest.TestCase):
    def test_nav_plan_accepts_flat_and_nested_visible_item_hexes(self) -> None:
        for flat_hexes in (True, False):
            with self.subTest(flat_hexes=flat_hexes):
                observation = self.observation(flat_hexes)
                bridge = self.bridge()
                payload = {"observationSeq": 7, "observation": observation}
                route = {
                    "reachable": True,
                    "toMovable": True,
                    "bestScore": 2,
                    "bestPathLength": 2,
                }

                with mock.patch.object(
                    mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
                ), mock.patch.object(
                    mcp, "environment_query", return_value={"jsonrpc": "2.0", "id": None, "result": {"result": route}}
                ) as query:
                    response = mcp.nav_plan_state(bridge, {})

                self.assertEqual(response["result"]["target"]["hex"], {"x": 12, "y": 20})
                self.assertEqual(response["result"]["plan"]["movement"]["arguments"], {"x": 12, "y": 20})
                self.assertEqual(query.call_args.args[2]["toX"], 12)
                self.assertEqual(query.call_args.args[2]["toY"], 20)

    def test_find_safe_step_accepts_flat_and_nested_chosen_hexes(self) -> None:
        for flat_hexes in (True, False):
            with self.subTest(flat_hexes=flat_hexes):
                observation = self.observation(flat_hexes)
                bridge = self.bridge()
                payload = {"observationSeq": 8, "observation": observation}
                route = {
                    "reachable": True,
                    "toMovable": True,
                    "bestScore": 1,
                    "bestPathLength": 1,
                }

                with mock.patch.object(
                    mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
                ), mock.patch.object(
                    mcp, "environment_query", return_value={"jsonrpc": "2.0", "id": None, "result": {"result": route}}
                ) as query:
                    response = mcp.find_safe_step_state(bridge, {"localRadius": 1, "maxCandidates": 1})

                result = response["result"]
                self.assertEqual(result["checked"], 1)
                self.assertEqual(result["totalCandidates"], 6)
                self.assertEqual(result["best"]["target"]["source"], "local_safe_step")
                self.assertIn(query.call_args.args[2]["toX"], range(9, 12))
                self.assertIn(query.call_args.args[2]["toY"], range(19, 22))

    def test_nav_plan_falls_back_to_path_for_unknown_tactical_query(self) -> None:
        observation = self.observation(True)
        bridge = self.bridge()
        payload = {"observationSeq": 8, "observation": observation}
        tactical_failure = self.environment_query_failure("tactical_path", "unknown_environment_query")
        path_route = {"reachable": True, "toMovable": True, "directDistance": 2, "pathLength": 2}
        path_success = {"jsonrpc": "2.0", "id": None, "result": {"result": path_route}}

        with mock.patch.object(
            mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
        ), mock.patch.object(mcp, "environment_query", side_effect=[tactical_failure, path_success]) as query:
            response = mcp.nav_plan_state(bridge, {})

        plan = response["result"]["plan"]
        self.assertEqual(plan["query"], "path")
        self.assertEqual(plan["route"]["query"], "path")
        self.assertEqual(
            plan["queryFallback"],
            {"from": "tactical_path", "to": "path", "reason": "unknown_environment_query"},
        )
        self.assertEqual([call.args[1] for call in query.call_args_list], ["tactical_path", "path"])

    def test_nav_plan_does_not_fall_back_for_other_query_failures(self) -> None:
        observation = self.observation(True)
        bridge = self.bridge()
        payload = {"observationSeq": 8, "observation": observation}
        failure = self.environment_query_failure("tactical_path", "map_missing")

        with mock.patch.object(
            mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
        ), mock.patch.object(mcp, "environment_query", return_value=failure) as query:
            response = mcp.nav_plan_state(bridge, {})

        self.assertEqual(response, failure)
        query.assert_called_once()
        self.assertEqual(query.call_args.args[1], "tactical_path")

    def test_find_safe_step_falls_back_to_path_for_unknown_tactical_query(self) -> None:
        observation = self.observation(True)
        bridge = self.bridge()
        payload = {"observationSeq": 9, "observation": observation}
        tactical_failure = self.environment_query_failure("tactical_path", "unknown_environment_query")
        path_route = {
            "reachable": True,
            "toMovable": True,
            "directDistance": 1,
            "pathLength": 1,
        }
        path_success = {"jsonrpc": "2.0", "id": None, "result": {"result": path_route}}

        with mock.patch.object(
            mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
        ), mock.patch.object(mcp, "environment_query", side_effect=[tactical_failure, path_success]) as query:
            response = mcp.find_safe_step_state(bridge, {"localRadius": 1, "maxCandidates": 1})

        best = response["result"]["best"]
        self.assertIsNotNone(best)
        self.assertEqual(best["route"]["query"], "path")
        self.assertEqual(
            best["queryFallback"],
            {"from": "tactical_path", "to": "path", "reason": "unknown_environment_query"},
        )
        self.assertEqual([call.args[1] for call in query.call_args_list], ["tactical_path", "path"])

    def test_find_safe_step_does_not_fall_back_for_other_query_failures(self) -> None:
        observation = self.observation(True)
        bridge = self.bridge()
        payload = {"observationSeq": 10, "observation": observation}
        failure = self.environment_query_failure("tactical_path", "map_missing")

        with mock.patch.object(
            mcp, "observe_target_payload", return_value=(bridge, None, payload, observation)
        ), mock.patch.object(mcp, "environment_query", return_value=failure) as query:
            response = mcp.find_safe_step_state(bridge, {"localRadius": 1, "maxCandidates": 1})

        self.assertEqual(response, failure)
        query.assert_called_once()
        self.assertEqual(query.call_args.args[1], "tactical_path")

    @staticmethod
    def observation(flat_hexes: bool) -> dict:
        chosen_hex = {"hexX": 10, "hexY": 20} if flat_hexes else {"hex": {"x": 10, "y": 20}}
        item_hex = {"hexX": 12, "hexY": 20} if flat_hexes else {"hex": {"x": 12, "y": 20}}
        critter_hex = {"hexX": 11, "hexY": 20} if flat_hexes else {"hex": {"x": 11, "y": 20}}
        return {
            "seq": 5,
            "connected": True,
            "hasMap": True,
            "hasChosen": True,
            "chosen": {"id": 1, **chosen_hex},
            "critters": [{"id": 2, "alive": True, **critter_hex}],
            "mapItems": [{"id": 3, "protoId": "test_item", "canPickUp": True, **item_hex}],
            "availableActions": ["move_to_hex"],
        }

    @staticmethod
    def bridge() -> SimpleNamespace:
        return SimpleNamespace(endpoint={"endpointId": "test"}, agent_profiles={}, agent_memories={})

    @staticmethod
    def environment_query_failure(query: str, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "result": {
                "completed": True,
                "timedOut": False,
                "event": {
                    "type": "environment_query_result",
                    "query": query,
                    "success": False,
                    "message": message,
                    "result": None,
                },
                "result": None,
            },
        }


if __name__ == "__main__":
    unittest.main()
