#!/usr/bin/env python3
"""MCP-level smoke runner for the The Life After AI control adapter."""

from __future__ import annotations

import argparse
import os
import sys

from ai_control_runner import (
    ADAPTER_PATH,
    MCP_VERSION,
    McpProcess,
    SmokeError,
    configure_stdio,
    require_result,
    tool_payload,
    unwrap_observation_payload,
    wait_observation_snapshot,
)

REQUIRED_TOOLS = {
    "tla_launch_options",
    "tla_launch_scene",
    "tla_launch_accounts",
    "tla_launch_two_players",
    "tla_launch",
    "tla_processes",
    "tla_logs",
    "tla_window_screenshot",
    "tla_save_screenshot",
    "tla_set_mouse_pos",
    "tla_show_screen",
    "tla_hide_screen",
    "tla_endpoints",
    "tla_status_all",
    "tla_team_status",
    "tla_team_memory",
    "tla_team_remember",
    "tla_team_forget",
    "tla_team_assign_roles",
    "tla_team_plan",
    "tla_team_tasks",
    "tla_group_rendezvous",
    "tla_follow_agent",
    "tla_wait_ready",
    "tla_wait_all_ready",
    "tla_select_endpoint",
    "tla_stop_process",
    "tla_observe",
    "tla_available_actions",
    "tla_explain_action",
    "tla_set_agent_profile",
    "tla_agent_profile",
    "tla_agent_memory",
    "tla_agent_remember",
    "tla_agent_forget",
    "tla_agent_known_people",
    "tla_agent_known_places",
    "tla_agent_tick",
    "tla_agent_run",
    "tla_agent_status",
    "tla_agent_decisions",
    "tla_agent_pause",
    "tla_agent_resume",
    "tla_world_summary",
    "tla_area_summary",
    "tla_recent_changes",
    "tla_visible_interactables",
    "tla_interest_points",
    "tla_nav_options",
    "tla_nav_plan",
    "tla_find_nearest_reachable",
    "tla_find_safe_step",
    "tla_find_cover",
    "tla_find_vantage",
    "tla_explore_options",
    "tla_route_memory",
    "tla_env_path",
    "tla_env_trace",
    "tla_env_obstacles",
    "tla_env_tactical_path",
    "tla_sync",
    "tla_social_context",
    "tla_conversation_state",
    "tla_reply_options",
    "tla_relation_note",
    "tla_agent_say_planned",
    "tla_step",
    "tla_next_events",
    "tla_wait_command",
    "tla_global_move_to",
    "tla_global_enter_interest",
    "tla_operate_container",
    "tla_accept_agreement",
    "tla_generate_critter",
    "tla_finish_generation",
    "tla_admin_prepare",
    "tla_admin_teleport_to_hex",
    "tla_admin_move_to_map",
    "tla_admin_to_faction_leader",
    "tla_admin_spawn_mob_at_target",
    "tla_admin_set_weather",
    "tla_request_roster",
    "tla_roster_switch",
    "tla_say",
    "tla_act_and_sync",
    "tla_clear_actions",
    "tla_schema",
    "tla_status",
    "tla_ping",
}


REQUIRED_RESOURCES = {
    "tla://guide/operator",
    "tla://launch/options",
    "tla://schema/commands",
    "tla://schema/observation",
    "tla://schema/events",
    "tla://schema/social",
    "tla://schema/agent",
    "tla://schema/world",
    "tla://schema/environment",
    "tla://schema/orchestration",
    "tla://schema/team",
    "tla://endpoints",
}
REQUIRED_PROMPTS = {"tla_operator_guide", "tla_conversation_guide"}


def assert_contains(actual: set[str], expected: set[str], label: str) -> None:
    missing = sorted(expected - actual)
    if missing:
        raise SmokeError(f"{label} is missing: {', '.join(missing)}")


def run_static_checks(client: McpProcess) -> None:
    init = require_result(
        client.request(
            "initialize",
            {
                "protocolVersion": MCP_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "last-frontier-ai-control-smoke", "version": "0.1.0"},
            },
        ),
        "initialize",
    )
    if "prompts" not in init.get("capabilities", {}):
        raise SmokeError("initialize did not advertise prompts capability")
    client.notify("notifications/initialized")
    print("ok initialize")

    tools = require_result(client.request("tools/list"), "tools/list").get("tools", [])
    assert_contains({tool["name"] for tool in tools}, REQUIRED_TOOLS, "tools/list")
    print("ok tools/list")

    resources = require_result(client.request("resources/list"), "resources/list").get("resources", [])
    assert_contains({resource["uri"] for resource in resources}, REQUIRED_RESOURCES, "resources/list")
    print("ok resources/list")

    guide = require_result(client.request("resources/read", {"uri": "tla://guide/operator"}), "resources/read")
    guide_text = guide["contents"][0]["text"]
    if "tla_next_events" not in guide_text or "tla_clear_actions" not in guide_text:
        raise SmokeError("operator guide does not mention expected control-loop tools")
    print("ok operator guide resource")

    prompts = require_result(client.request("prompts/list"), "prompts/list").get("prompts", [])
    assert_contains({prompt["name"] for prompt in prompts}, REQUIRED_PROMPTS, "prompts/list")
    require_result(client.request("prompts/get", {"name": "tla_operator_guide"}), "prompts/get")
    print("ok prompt guide")

    schema = tool_payload(client, "tla_schema", {"section": "commands"})
    if "typedTools" not in schema:
        raise SmokeError("command schema does not include typedTools")
    print("ok command schema")

    launch_options = tool_payload(client, "tla_launch_options")
    # TLA не использует сцен-систему lf; локальный тестовый профиль — субконфиг LocalTest из TLA.fomain.
    if "LocalTest" not in {entry.get("name") for entry in launch_options.get("subConfigs", [])}:
        raise SmokeError("launch options do not include LocalTest subconfig")
    print("ok launch options")


def run_live_checks(client: McpProcess, event_limit: int, wait_command: float, skip_command: bool, observe_timeout: float) -> None:
    tool_payload(client, "tla_ping")
    print("ok tla_ping")

    status = tool_payload(client, "tla_status")
    if "running" not in status:
        raise SmokeError("tla_status did not return bridge running state")
    print("ok tla_status")

    wait_observation_snapshot(client, observe_timeout)
    print("ok tla_observe")

    tool_payload(client, "tla_next_events", {"seekLatest": True, "limit": 1})
    print("ok event cursor seekLatest")

    if skip_command:
        return

    accepted = tool_payload(client, "tla_clear_actions")
    command_seq = accepted.get("commandSeq")
    if not isinstance(command_seq, int):
        raise SmokeError("tla_clear_actions did not return commandSeq")
    print(f"ok tla_clear_actions accepted commandSeq={command_seq}")

    completion = tool_payload(
        client,
        "tla_wait_command",
        {"commandSeq": command_seq, "timeoutMs": int(wait_command * 1000), "pollIntervalMs": 100, "limit": event_limit},
    )
    if not completion.get("completed"):
        raise SmokeError(f"Timed out waiting for command_completed seq={command_seq}")

    event = completion.get("event", {})
    if not event.get("success"):
        raise SmokeError(f"clear_actions completed with failure: {event.get('message')}")
    print("ok command_completed")


def build_adapter_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(ADAPTER_PATH),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--timeout",
        str(args.timeout),
    ]
    if args.token:
        command.extend(["--token", args.token])
    return command


def main() -> int:
    configure_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("TLA_AI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TLA_AI_PORT", "43011")))
    parser.add_argument("--token", default=os.environ.get("TLA_AI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TLA_AI_TIMEOUT", "3")))
    parser.add_argument("--event-limit", type=int, default=100)
    parser.add_argument("--wait-command", type=float, default=3.0)
    parser.add_argument("--skip-command", action="store_true", help="Do not queue the harmless tla_clear_actions command.")
    parser.add_argument("--static-only", action="store_true", help="Only check static MCP tools/resources/prompts; no game client required.")
    args = parser.parse_args()

    client = McpProcess(build_adapter_command(args))
    try:
        run_static_checks(client)
        if not args.static_only:
            run_live_checks(client, args.event_limit, args.wait_command, args.skip_command, args.timeout)
    except SmokeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
