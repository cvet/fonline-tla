#!/usr/bin/env python3
"""Static MCP guide text builders for The Life After AI control."""

from __future__ import annotations


def operator_guide_text(typed_tool_names: list[str]) -> str:
    typed_tools = ", ".join(typed_tool_names)
    return f"""# The Life After AI Control Operator Guide

You control a normal The Life After client through the AI control bridge. Stay inside the available tools and prefer semantic actions over raw input.

Recommended loop:

1. If no client is running, call `tla_launch_options` to discover project subconfigs and selectable scenes, then call a launch recipe (`tla_launch_scene`, `tla_launch_accounts`, `tla_launch_two_players`) or raw `tla_launch` with `enableAiControl = true`.
2. Use `tla_processes`, `tla_endpoints`, `tla_status_all`, and `tla_team_status` to inspect launched processes and controlled clients. Use `tla_team_assign_roles`, `tla_team_plan`, and `tla_group_rendezvous` when coordinating multiple accounts. Use `tla_select_endpoint` to choose the default client, or pass `endpointId` to a tool to target one client for just that call.
3. Call `tla_wait_ready` or `tla_wait_all_ready` after launch when you need to wait for connected/map/chosen readiness before acting.
4. Call `tla_schema` with `section = "commands"` and `section = "observation"` when you need exact field meanings.
5. Call `tla_step` for the normal perception loop: it reads new events, a fresh client snapshot, and current action suggestions together. Use `tla_sync` / `tla_observe` / `tla_next_events` separately when you need explicit control.
6. Read event payloads before deciding what changed, then use the observation snapshot as current state. Check `social.heardSpeech` / `social.pendingResponses` on `tla_step` or `tla_sync`, or call `tla_conversation_state` / `tla_reply_options`, so visible speech is not ignored.
7. Call `tla_world_summary` when you want compact perception: area, recent changes, interactables, interest points, nav options, and social counts in one response. Use `tla_area_summary`, `tla_recent_changes`, `tla_visible_interactables`, `tla_interest_points`, and `tla_nav_options` for narrower reads.
8. Call `tla_nav_plan`, `tla_find_nearest_reachable`, `tla_find_safe_step`, `tla_find_cover`, `tla_find_vantage`, or `tla_explore_options` when you need path-checked planning, cover/vantage anchors, or exploration leads before issuing movement.
9. Call `tla_inventory_summary`, `tla_loot_options`, `tla_healing_options`, `tla_reload_options`, or `tla_combat_options` when you need item/combat priorities before using normal item or attack tools.
10. Call `tla_dialog_options`, `tla_task_options`, `tla_xp_source_plan`, `tla_dialog_memory`, `tla_task_memory`, `tla_global_options`, `tla_travel_plan`, `tla_enter_options`, or `tla_route_memory` when deciding how to answer dialogs, remember visible task hints, plan XP sources, pass account/generation gates, or travel on the global map.
11. Call `tla_available_actions` or `tla_explain_action` when you need current candidate ids, answer indexes, item ids, or roster indexes.
12. Call `tla_env_path`, `tla_env_trace`, `tla_env_obstacles`, or `tla_env_tactical_path` before movement/combat positioning when distance, line of fire, blockers, or visible threat avoidance matters.
13. For QA setup only, inspect `observation.admin` / `tla_available_actions`; if admin access is visible, use `tla_admin_prepare`, `tla_admin_move_to_map`, `tla_admin_teleport_to_hex`, `tla_admin_spawn_mob_at_target`, or related `tla_admin_*` tools with `allowAdmin = true`, then record that setup before starting player-like validation.
14. Call `tla_agent_tick` when you want the adapter to update endpoint-local memory and return an advisory decision trace before choosing the actual command. Call `tla_agent_run` for a bounded observe/decide loop; pass `execute = true` only when you want it to issue the selected normal typed tool under its safety gates. Use `tla_agent_memory`, `tla_agent_status`, `tla_agent_decisions`, and `tla_relation_note` to inspect or update what the runtime remembered and why it suggested something; use `tla_agent_memory_save` / `tla_agent_memory_load` only when a long QA run needs explicit Workspace/AiMemory persistence.
15. When a command fails, a process exits, or the world looks inconsistent, call `tla_logs` to inspect recent server/client logs.
16. When visual state itself is the evidence, such as particles, shaders, or GUI layout, call `tla_window_screenshot` for a diagnostic PNG of a visible local process window.
17. Pick one semantic typed tool when you want to act. Available typed tools: {typed_tools}.
18. After acting, prefer `tla_act_and_sync` or pass `syncAfterCompletion = true` to a typed command tool when you need `command_completed` events and a fresh observation in one call.

Important rules:

- Use visible ids from `tla_observe` or recent events. Do not invent entity or item ids.
- Treat `tla_step` and `tla_available_actions` action suggestions as advisory: they map visible state to likely arguments but server validation still decides the result.
- Prefer typed tools such as `tla_move_to_hex`, `tla_talk_to`, `tla_dialog_answer`, `tla_ui_answer`, `tla_say`, `tla_request_roster`, `tla_roster_switch`, and `tla_use_item` over raw `tla_act`.
- Use `syncAfterCompletion = true` on command tools when the next decision needs an immediate post-command observation.
- Use `tla_set_agent_profile` once per controlled endpoint when the host wants a specific role/persona. The profile is echoed in `social.profile` and helps classify whether speech is addressed to the agent.
- `tla_agent_tick` is advisory: it observes, remembers, and suggests a next intent, but it does not execute commands by itself. `tla_agent_run` can execute only when `execute = true`, its deployment/readiness policy allows execution, and the selected normal typed tool passes server validation. It must not use launch/admin/log/schema/generated-file surfaces as world knowledge or autonomous actions.
- `tla_admin_*` tools are not player-like actions. They require `allowAdmin = true`, current admin/moderator access, and are for setup before a QA pass; `tla_agent_run` blocks them even when allowlisted.
- When `social.pendingResponses` is non-empty, decide whether your role should answer and reply with `tla_agent_say_planned` or `tla_say`; avoid answering your own `say_received` events.
- Environment query tools are read-only client-side helpers. They use the current replicated map view and visible critters/items, so treat their tactical-risk output as advisory rather than omniscient.
- `tla_window_screenshot` is adapter-side visual QA. It writes a PNG under `Workspace/AiControlScreenshots` by default and should not be used as normal in-world perception.
- Inventory, loot, and combat option tools are heuristic summaries over visible item/critter fields. They help choose normal tools; they do not prove item compatibility, hostility, or server acceptance.
- Dialog, task, and global-map option/memory tools are advisory summaries over visible dialog/global-map/action fields. They do not expose hidden quest state and do not execute commands.
- Use `tla_act` only as a compatibility escape hatch for commands that do not yet have a typed tool.
- Use `tla_mouse_click` and `tla_key_press` only for UI surfaces without semantic commands.
- Commands are normal client actions and still pass through server validation.
- `tla_next_events` stores a cursor per endpoint inside this MCP adapter process. Use `reset = true` only when you intentionally want to reread from the beginning of the retained event buffer. Use `seekLatest = true` when you want to skip retained events and start tailing new ones.
- Launch recipes are thin helpers over `tla_launch`: they fill `subConfig`, `clientCount`, and `settings.Scene.Startup`, then use the same process launcher.
- `tla_launch` passes normal engine command-line settings. For embedded clients, `AiControl.Port` is the first client port and `AiControl.PortStride` spaces subsequent clients.
"""


def conversation_guide_text(agent_name: str = "", agent_role: str = "", goals: str = "", conversation_style: str = "") -> str:
    name_line = f"- Agent name: {agent_name.strip()}\n" if agent_name.strip() else ""
    role_line = f"- Role: {agent_role.strip()}\n" if agent_role.strip() else ""
    goals_line = f"- Goals: {goals.strip()}\n" if goals.strip() else ""
    style_line = f"- Conversation style: {conversation_style.strip()}\n" if conversation_style.strip() else ""
    profile_lines = name_line + role_line + goals_line + style_line
    if not profile_lines:
        profile_lines = "- Configure a role with `tla_set_agent_profile` before long-running playtests.\n"

    return f"""# The Life After Conversation Awareness

Use this guide with the MCP social context returned by `tla_step`, `tla_sync`, or `tla_social_context`.

Configured role:
{profile_lines}
Conversation loop:

1. Always inspect `social.heardSpeech` after reading events. These are player-visible `say_received` events, not privileged server chat.
2. Treat `addressedToAgent = likely` plus `needsResponse = true` as a prompt to consider replying.
3. Use `reasons` to understand why the adapter thinks the message is or is not addressed to you: name/alias mention, second-person wording, question/request/greeting markers, or self-speech.
4. Decide the actual answer with your role, current objective, local observation, and recent dialog context. The adapter gives hints, not final social judgment.
5. Reply only through `tla_say` unless a dialog answer or gameplay action is more appropriate.
6. Keep replies short, in character, and in the configured language unless another player clearly switches language.
7. Do not answer your own `selfSpeech` events unless you are deliberately narrating or correcting yourself.
"""


def agent_examples_text() -> str:
    return """# The Life After Agent Authoring Examples

Use these examples as starting profiles. Apply them with `tla_set_agent_profile`, then run `tla_agent_tick` for advisory decisions or bounded `tla_agent_run` with the matching mode.

## QA Tester

Profile:
```json
{"preset":"qa_tester","name":"QA","role":"QA tester","goals":["exercise visible features","report loops and blocked actions"],"skillLevel":"expert","activityLevel":"busy"}
```
Run hint: `tla_agent_run` with `mode=soak` in the live runner, typed tools only, `execute=true` only in private QA.

## Wanderer

Profile:
```json
{"preset":"cautious_explorer","name":"Wanderer","role":"wanderer","goals":["walk through reachable areas","avoid fights","notice changed places"],"riskTolerance":"low","lootStyle":"minimal","skillLevel":"average"}
```
Run hint: use `--autonomous-mode explore`, keep combat tools blocked, and let route memory penalize recent failed paths.

## Social Helper

Profile:
```json
{"preset":"social_player","name":"Helper","aliases":["help","guide"],"role":"social helper","goals":["hear nearby players","answer direct questions briefly"],"conversationStyle":"short, friendly, in character","socialPolicy":"answer direct speech, stay quiet otherwise","skillLevel":"average"}
```
Run hint: use `--autonomous-mode social` or `tla_reply_options` plus `tla_agent_say_planned`; keep auto-reply deterministic only for tests.

## Combat Scout

Profile:
```json
{"preset":"guard","name":"Scout","role":"combat scout","goals":["survive hostile encounters","keep distance","warn the team"],"combatStyle":"defensive","riskTolerance":"medium","lootStyle":"combat","skillLevel":"expert"}
```
Run hint: use combat mode only in private QA, enable `allowCombat`, and check `tla_combat_options`, `tla_find_cover`, `tla_reload_options`, and `tla_retreat_options` before attacks.

## Trader

Profile:
```json
{"preset":"helper","name":"Trader","role":"trader","goals":["talk to players","prefer barter and safe travel","avoid stealing"],"conversationStyle":"practical and concise","lootStyle":"valuable","combatStyle":"avoidant","skillLevel":"average"}
```
Run hint: prefer `tla_dialog_options`, `tla_global_options`, and social replies; block combat unless the host explicitly switches to a defensive test.
"""
