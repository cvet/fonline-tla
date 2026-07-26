#!/usr/bin/env python3
"""Exercise deterministic contextual TLA GUI screens through their real client flows.

The runner currently covers:

* Aim, Split, Timer, Use, and SkillBox through the parameterized context-screen bridge command;
* PickUp, opened by interacting with a safe visible container/locker (or an explicit item id);
* Radio, opened by normally using an owned radio on the chosen critter;
* Elevator, captured when already open or reached through an explicitly supplied real trigger hex;
* DialogBox, opened through the server-backed two-answer QA fixture and closed with its safe answer.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from collections.abc import Callable
from typing import Any

from ai_control_runner import (
    ADAPTER_PATH,
    McpProcess,
    SmokeError,
    build_adapter_command,
    call_tool,
    configure_stdio,
    initialize_client,
    unwrap_observation_payload,
)
from tla_gui_screenshot_test import (
    capture_tga_path,
    centered_screen_bounds,
    command_completed_successfully,
    is_interface_gold,
    is_interface_green,
    is_neutral_bright_text,
    path_in_workspace,
    read_uncompressed_true_color_tga,
    tga_roi_statistics,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCREENS = ("SkillBox", "Aim", "Split", "Timer", "Use", "PickUp", "Radio", "Elevator", "DialogBox")
BRIDGE_CONTEXT_SCREENS = frozenset({"SkillBox", "Aim", "Split", "Timer", "Use"})
SUPPORTED_SCREENS = BRIDGE_CONTEXT_SCREENS | {"PickUp", "Radio", "Elevator", "DialogBox"}
# How many nearest safe containers to path-probe before giving up on the PickUp context (one bridge
# round-trip each). Nearest-first ordering does NOT correlate with reachability — on arroyo the first
# reachable container sits at rank 12 of 20, behind eleven nearer ones walled off inside buildings — so
# this has to cover a whole map's worth of visible containers, not just the closest handful.
PICKUP_REACHABILITY_PROBE_LIMIT = 32
CONTEXT_REQUIREMENTS = {
    "Aim": "visible living non-chosen critter",
    "Split": "inventory stack with count greater than one",
    "Timer": "owned dynamite (the authored timer-capable item)",
    "Use": "inventory item with canUseOnSmth=true and a visible critter or item target",
    "SkillBox": "chosen critter on a map",
    "PickUp": "safe unopened container or locker the chosen critter can path adjacent to",
    "Radio": "owned inventory item with protoId=radio or hasRadio=true",
    "Elevator": "already-open elevator or explicit --elevator-trigger-hex X Y",
    "DialogBox": "AiControl.AllowQaCommands and a chosen critter",
}
TIMED_USE_PROTO_IDS = frozenset({"dynamite"})

SKILLBOX_SCREEN_SIZE = (185, 368)
SKILLBOX_TITLE_RECT = (20, 5, 165, 42)
SKILLBOX_ROWS_RECT = (8, 42, 178, 325)
PICKUP_SCREEN_SIZE = (417, 376)
PICKUP_PREVIEW_RECT = (303, 35, 373, 135)
PICKUP_INVENTORY_RECT = (54, 33, 124, 333)
PICKUP_CONTAINER_RECT = (175, 36, 245, 336)
RADIO_SCREEN_SIZE = (331, 202)
RADIO_LABELS_RECT = (12, 8, 150, 192)
RADIO_CHANNEL_DIAL_RECT = (145, 5, 285, 130)
RADIO_CONTROLS_RECT = (12, 75, 315, 195)
ELEVATOR_SCREEN_SIZES = ((230, 284), (231, 285))
ELEVATOR_BUTTONS_RECT = (8, 35, 64, 276)
ELEVATOR_PANEL_RECT = (108, 18, 225, 276)
DIALOGBOX_SCREEN_SIZE = (302, 151)
DIALOGBOX_PROMPT_RECT = (20, 15, 285, 90)
DIALOGBOX_ANSWERS_RECT = (40, 99, 290, 149)
CONTEXT_SCREEN_SIZES = {
    "Aim": (504, 309),
    "Split": (259, 162),
    "Timer": (259, 162),
    "Use": (292, 376),
}
CONTEXT_SCREEN_REGIONS = {
    "Aim": (
        ((170, 31, 340, 256), "texture", 40, 30, 50),
        ((20, 25, 150, 260), "green", 100, 40, 120),
        ((350, 25, 485, 260), "green", 100, 40, 120),
    ),
    "Split": (
        ((17, 46, 107, 111), "texture", 20, 10, 10),
        ((120, 38, 220, 116), "text", 30, 20, 12),
    ),
    "Timer": (
        ((16, 43, 106, 108), "texture", 20, 10, 10),
        ((116, 36, 221, 117), "texture", 20, 20, 20),
        ((132, 58, 202, 98), "text", 20, 15, 8),
    ),
    "Use": (
        ((39, 34, 139, 334), "texture", 30, 15, 20),
        ((174, 35, 235, 133), "texture", 20, 10, 10),
    ),
}


def screen_names(observation: dict[str, Any]) -> list[str]:
    screen = observation.get("screen")
    if not isinstance(screen, dict):
        return []
    names = screen.get("screens")
    if not isinstance(names, list):
        names = screen.get("activeScreens")
    return [str(name) for name in names] if isinstance(names, list) else []


def screen_is_active(observation: dict[str, Any], screen: str) -> bool:
    return any(name == screen or name.endswith("::" + screen) for name in screen_names(observation))


def active_modal_name(observation: dict[str, Any]) -> str:
    screen = observation.get("screen")
    if not isinstance(screen, dict) or screen.get("modalActive") is not True:
        return ""
    return str(screen.get("activeModal") or screen.get("active") or "")


def active_dialog_box_prompt(observation: dict[str, Any]) -> dict[str, Any] | None:
    prompt = observation.get("uiPrompt")
    if not isinstance(prompt, dict) or prompt.get("active") is not True or prompt.get("kind") != "dialog_box":
        return None
    session = prompt.get("dialogBoxSession")
    if isinstance(session, bool) or not isinstance(session, int) or session < 1 or session > 0xFFFFFFFF:
        return None
    return prompt


def dialog_box_has_safe_fixture_answer(prompt: dict[str, Any]) -> bool:
    buttons = prompt.get("buttons")
    if not isinstance(buttons, list) or len(buttons) != 2:
        return False
    return any(
        isinstance(button, dict)
        and button.get("index") == 1
        and button.get("id") == "answer_1"
        and button.get("enabled") is not False
        and button.get("dangerous") is not True
        for button in buttons
    )


def wait_for_observation(client: McpProcess, predicate: Any, timeout_ms: int) -> dict[str, Any] | None:
    deadline = time.monotonic() + max(timeout_ms, 0) / 1000.0
    last: dict[str, Any] = {}
    while True:
        last = unwrap_observation_payload(call_tool(client, "tla_observe"))
        if predicate(last):
            return last
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.1)


def item_id_matches(item: dict[str, Any], requested_id: str) -> bool:
    return str(item.get("id") or "") == requested_id


def container_is_reachable(client: McpProcess, item: dict[str, Any], timeout_ms: int) -> bool:
    """Can the chosen critter path adjacent to this container? `cut=1` mirrors the client's own pick
    distance (`useDist` in ChosenActions::ChosenPickItem), so this answers exactly the question the game
    asks before it queues the approach walk."""
    target = item_hex(item)
    if target is None:
        return False

    payload = call_tool(client, "tla_env_path", {
        "toX": target[0],
        "toY": target[1],
        "cut": 1,
        "waitForCompletion": True,
        "timeoutMs": timeout_ms,
    })
    result = payload.get("result") if isinstance(payload, dict) else None
    return bool(result.get("reachable")) if isinstance(result, dict) else False


def describe_pickup_approach(client: McpProcess, item: dict[str, Any], timeout_ms: int) -> dict[str, Any] | None:
    """Measure where the chosen critter ended up relative to the container it was sent to open.

    `blocked` is True when the critter is out of pick range (`directDistance > 1`) and no path closes the
    remaining gap — i.e. the approach is over and it did not arrive, so no screen can ever appear.
    """
    target = item_hex(item)
    if target is None:
        return None

    payload = call_tool(client, "tla_env_path", {
        "toX": target[0],
        "toY": target[1],
        "cut": 1,
        "waitForCompletion": True,
        "timeoutMs": timeout_ms,
    })
    result = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(result, dict):
        return None

    distance = result.get("directDistance")
    reachable = bool(result.get("reachable"))
    out_of_range = isinstance(distance, int) and distance > 1
    return {
        "from": result.get("from"),
        "to": result.get("to"),
        "directDistance": distance,
        "pathLength": result.get("pathLength"),
        "reachable": reachable,
        "blocked": bool(out_of_range and not reachable),
    }


def pickup_candidate_is_safe(item: dict[str, Any]) -> bool:
    """Only choose a real unopened container; never pick up an ordinary ground item or a door."""
    required_fields = {
        "hasContainer",
        "hasLocker",
        "hasDoor",
        "canOpen",
        "opened",
        "lockerLocked",
        "lockerJammed",
        "lockerBroken",
        "lockerNoOpen",
        "isGag",
    }
    if item.get("id") is None or not required_fields.issubset(item):
        return False
    return bool(
        item.get("hasContainer") is True
        and item.get("hasLocker") is True
        and item.get("hasDoor") is False
        and item.get("canOpen") is True
        and item.get("opened") is False
        and item.get("lockerLocked") is False
        and item.get("lockerJammed") is False
        and isinstance(item.get("lockerBroken"), bool)
        and item.get("lockerNoOpen") is False
        and item.get("isGag") is False
    )


def item_hex(item: dict[str, Any]) -> tuple[int, int] | None:
    value = item.get("hex")
    try:
        if isinstance(value, dict):
            return int(value["x"]), int(value["y"])
        return int(item["hexX"]), int(item["hexY"])
    except (KeyError, TypeError, ValueError):
        return None


def chosen_hex(observation: dict[str, Any]) -> tuple[int, int] | None:
    chosen = observation.get("chosen")
    return item_hex(chosen) if isinstance(chosen, dict) else None


def select_pickup_candidate(observation: dict[str, Any], requested_id: str = "",
                            is_reachable: Callable[[dict[str, Any]], bool] | None = None,
                            probe_limit: int = PICKUP_REACHABILITY_PROBE_LIMIT) -> dict[str, Any] | None:
    items = [item for item in observation.get("mapItems", []) if isinstance(item, dict)]
    if requested_id:
        selected = next((item for item in items if item_id_matches(item, requested_id)), None)
        if selected is None:
            raise ValueError(f"PickUp item {requested_id} is not visible")
        if not pickup_candidate_is_safe(selected):
            raise ValueError(f"PickUp item {requested_id} is not a safe unopened container")
        return selected

    candidates = [item for item in items if pickup_candidate_is_safe(item)]
    origin = chosen_hex(observation)

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        target = item_hex(item)
        distance = (abs(target[0] - origin[0]) + abs(target[1] - origin[1])
                    if target is not None and origin is not None else 1_000_000)
        return distance, str(item.get("id") or "")

    candidates.sort(key=sort_key)
    if is_reachable is None:
        return candidates[0] if candidates else None

    # Visibility is not reachability: a container can be fully observable through a window or across a
    # wall while no path reaches it. Interacting with such a target is a legitimate no-op in game (the
    # chosen critter never starts walking), so probe nearest-first and take the first target the client
    # can actually path adjacent to. Probing costs a round-trip each, hence the bounded scan.
    for item in candidates[:probe_limit]:
        if is_reachable(item):
            return item

    return None


def select_radio_candidate(observation: dict[str, Any]) -> dict[str, Any] | None:
    inventory = [item for item in observation.get("inventory", []) if isinstance(item, dict)]
    candidates = [
        item
        for item in inventory
        if item.get("id") is not None
        and (item.get("hasRadio") is True or str(item.get("protoId") or "").casefold() == "radio")
    ]
    candidates.sort(key=lambda item: (item.get("hasRadio") is not True, str(item.get("id"))))
    return candidates[0] if candidates else None


def interface_text(red: int, green: int, blue: int) -> bool:
    return is_interface_gold(red, green, blue) or is_neutral_bright_text(red, green, blue)


def aim_interface_green(red: int, green: int, blue: int) -> bool:
    return green >= 80 and green >= red * 1.35 and green >= blue * 1.2


def skillbox_candidate_bounds(width: int, height: int) -> list[tuple[int, int, int, int]]:
    screen_width, screen_height = SKILLBOX_SCREEN_SIZE
    if width < screen_width or height < screen_height:
        return []
    positions = (
        ((width - screen_width) // 2, (height - screen_height) // 2),
        (width - screen_width, (height - screen_height) // 2),
        (width - screen_width, 0),
        (width - screen_width, height - screen_height),
    )
    unique: list[tuple[int, int, int, int]] = []
    for left, top in positions:
        bounds = (left, top, left + screen_width, top + screen_height)
        if bounds not in unique:
            unique.append(bounds)
    return unique


def relative_bounds(parent: tuple[int, int, int, int], child: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return parent[0] + child[0], parent[1] + child[1], parent[0] + child[2], parent[1] + child[3]


def tga_skillbox_content_is_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    _, width, height, _, _, _, _ = image
    for screen_bounds in skillbox_candidate_bounds(width, height):
        whole = tga_roi_statistics(image, screen_bounds, interface_text)
        title = tga_roi_statistics(image, relative_bounds(screen_bounds, SKILLBOX_TITLE_RECT), interface_text)
        rows = tga_roi_statistics(image, relative_bounds(screen_bounds, SKILLBOX_ROWS_RECT), interface_text)
        if (whole["darkRatio"] >= 0.25 and whole["colorBuckets"] >= 3
                and 20 <= title["visiblePixels"] <= 1500
                and title["visibleWidth"] >= 20 and title["visibleHeight"] >= 4
                and rows["visiblePixels"] >= 180 and rows["visibleWidth"] >= 70
                and rows["visibleHeight"] >= 150 and rows["visibleRatio"] <= 0.35):
            return True
    return False


def tga_pickup_content_is_visible(path: Path, require_container_items: bool) -> bool:
    image = read_uncompressed_true_color_tga(path)
    screen_bounds = centered_screen_bounds(image, PICKUP_SCREEN_SIZE, (0, 0, *PICKUP_SCREEN_SIZE))
    if screen_bounds is None:
        return False

    whole = tga_roi_statistics(image, screen_bounds, lambda _red, _green, _blue: False)
    preview = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, PICKUP_PREVIEW_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    inventory = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, PICKUP_INVENTORY_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    container = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, PICKUP_CONTAINER_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    frame_visible = whole["colorBuckets"] >= 16 and 0.20 <= whole["darkRatio"] <= 0.98
    preview_visible = (preview["colorBuckets"] >= 8 and preview["visiblePixels"] >= 30
                       and preview["visibleWidth"] >= 8 and preview["visibleHeight"] >= 8)
    lists_visible = max(inventory["colorBuckets"], container["colorBuckets"]) >= 8
    container_item_visible = (container["visiblePixels"] >= 20 and container["visibleWidth"] >= 5
                              and container["visibleHeight"] >= 5)
    return bool(frame_visible and preview_visible and lists_visible
                and (not require_container_items or container_item_visible))


def radio_label(red: int, green: int, blue: int) -> bool:
    return red >= 100 and green >= 90 and blue <= 90 and red + green >= blue * 3


def tga_radio_content_is_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    screen_bounds = centered_screen_bounds(image, RADIO_SCREEN_SIZE, (0, 0, *RADIO_SCREEN_SIZE))
    if screen_bounds is None:
        return False

    whole = tga_roi_statistics(image, screen_bounds, lambda _red, _green, _blue: False)
    labels = tga_roi_statistics(image, relative_bounds(screen_bounds, RADIO_LABELS_RECT), radio_label)
    channel_dial = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, RADIO_CHANNEL_DIAL_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    controls = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, RADIO_CONTROLS_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    return bool(
        whole["colorBuckets"] >= 16
        and 0.15 <= whole["darkRatio"] <= 0.98
        and labels["visiblePixels"] >= 80
        and labels["visibleWidth"] >= 70
        and labels["visibleHeight"] >= 80
        and channel_dial["colorBuckets"] >= 8
        and channel_dial["visiblePixels"] >= 120
        and channel_dial["visibleWidth"] >= 80
        and channel_dial["visibleHeight"] >= 50
        and controls["colorBuckets"] >= 10
        and controls["visiblePixels"] >= 250
        and controls["visibleWidth"] >= 220
        and controls["visibleHeight"] >= 80
    )


def tga_elevator_content_is_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    for size in ELEVATOR_SCREEN_SIZES:
        screen_bounds = centered_screen_bounds(image, size, (0, 0, *size))
        if screen_bounds is None:
            continue
        whole = tga_roi_statistics(image, screen_bounds, lambda _red, _green, _blue: False)
        buttons = tga_roi_statistics(
            image,
            relative_bounds(screen_bounds, ELEVATOR_BUTTONS_RECT),
            lambda red, green, blue: max(red, green, blue) >= 40,
        )
        panel = tga_roi_statistics(
            image,
            relative_bounds(screen_bounds, ELEVATOR_PANEL_RECT),
            lambda red, green, blue: max(red, green, blue) >= 40,
        )
        if (
            whole["colorBuckets"] >= 12
            and 0.15 <= whole["darkRatio"] <= 0.98
            and buttons["colorBuckets"] >= 8
            and buttons["visiblePixels"] >= 120
            and buttons["visibleWidth"] >= 35
            and buttons["visibleHeight"] >= 100
            and panel["colorBuckets"] >= 10
            and panel["visiblePixels"] >= 300
            and panel["visibleWidth"] >= 80
            and panel["visibleHeight"] >= 180
        ):
            return True
    return False


def dialog_box_text(red: int, green: int, blue: int) -> bool:
    return interface_text(red, green, blue) or is_interface_green(red, green, blue)


def tga_dialog_box_content_is_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    screen_bounds = centered_screen_bounds(image, DIALOGBOX_SCREEN_SIZE, (0, 0, *DIALOGBOX_SCREEN_SIZE))
    if screen_bounds is None:
        return False

    whole = tga_roi_statistics(image, screen_bounds, lambda _red, _green, _blue: False)
    prompt = tga_roi_statistics(image, relative_bounds(screen_bounds, DIALOGBOX_PROMPT_RECT), dialog_box_text)
    answers = tga_roi_statistics(image, relative_bounds(screen_bounds, DIALOGBOX_ANSWERS_RECT), dialog_box_text)
    answer_panel = tga_roi_statistics(
        image,
        relative_bounds(screen_bounds, DIALOGBOX_ANSWERS_RECT),
        lambda red, green, blue: max(red, green, blue) >= 40,
    )
    return bool(
        whole["colorBuckets"] >= 12
        and 0.20 <= whole["darkRatio"] <= 0.99
        and prompt["visiblePixels"] >= 25
        and prompt["visibleWidth"] >= 50
        and prompt["visibleHeight"] >= 7
        and answers["visiblePixels"] >= 20
        and answers["visibleWidth"] >= 12
        and answers["visibleHeight"] >= 22
        and answers["visibleRatio"] <= 0.45
        and answer_panel["colorBuckets"] >= 8
        and answer_panel["visiblePixels"] >= 150
        and answer_panel["visibleWidth"] >= 180
        and answer_panel["visibleHeight"] >= 35
    )


def contextual_content_check(screen: str, capture: dict[str, Any], require_container_items: bool = False) -> tuple[bool, str]:
    if capture.get("verified") is not True:
        return False, "capture_not_verified"
    path = capture_tga_path(capture)
    prefix = screen.lower()
    if path is None or not path.is_file():
        return False, f"{prefix}_tga_missing"
    try:
        if screen == "SkillBox":
            visible = tga_skillbox_content_is_visible(path)
            return (True, "skillbox_skills_visible") if visible else (False, "skillbox_skills_not_visible")
        if screen == "PickUp":
            visible = tga_pickup_content_is_visible(path, require_container_items)
            return (True, "pickup_panels_visible") if visible else (False, "pickup_panels_not_visible")
        if screen == "Radio":
            visible = tga_radio_content_is_visible(path)
            return (True, "radio_controls_visible") if visible else (False, "radio_controls_not_visible")
        if screen == "Elevator":
            visible = tga_elevator_content_is_visible(path)
            return (True, "elevator_controls_visible") if visible else (False, "elevator_controls_not_visible")
        if screen == "DialogBox":
            visible = tga_dialog_box_content_is_visible(path)
            return (True, "dialog_box_prompt_visible") if visible else (False, "dialog_box_prompt_not_visible")
        if screen in CONTEXT_SCREEN_SIZES:
            visible = tga_centered_context_screen_is_visible(path, screen)
            success = f"{screen.lower()}_context_visible"
            failure = f"{screen.lower()}_context_not_visible"
            return (True, success) if visible else (False, failure)
    except (OSError, ValueError):
        return False, f"{prefix}_tga_invalid"
    return False, "content_oracle_unsupported"


def tga_centered_context_screen_is_visible(path: Path, screen: str) -> bool:
    image = read_uncompressed_true_color_tga(path)
    size = CONTEXT_SCREEN_SIZES[screen]
    screen_bounds = centered_screen_bounds(image, size, (0, 0, *size))
    if screen_bounds is None:
        return False
    whole = tga_roi_statistics(image, screen_bounds, lambda _red, _green, _blue: False)
    if whole["colorBuckets"] < 12 or not 0.15 <= whole["darkRatio"] <= 0.98:
        return False

    for relative, kind, minimum_pixels, minimum_width, minimum_height in CONTEXT_SCREEN_REGIONS[screen]:
        if kind == "text":
            predicate = interface_text
        elif kind == "green":
            predicate = aim_interface_green
        else:
            predicate = lambda red, green, blue: max(red, green, blue) >= 40
        stats = tga_roi_statistics(image, relative_bounds(screen_bounds, relative), predicate)
        if (stats["visiblePixels"] < minimum_pixels or stats["visibleWidth"] < minimum_width
                or stats["visibleHeight"] < minimum_height):
            return False
        if kind == "texture" and stats["colorBuckets"] < 6:
            return False
        if kind in {"text", "green"} and stats["visibleRatio"] > 0.45:
            return False
    return True


def capture_screen(client: McpProcess, screen: str, output_relative: str, settle_ms: int,
                   timeout_ms: int, require_container_items: bool = False) -> dict[str, Any]:
    path = f"{output_relative.rstrip('/')}/{screen}.tga"
    capture = call_tool(
        client,
        "tla_save_screenshot",
        {"path": path, "settleMs": settle_ms, "timeoutMs": timeout_ms, "pollIntervalMs": 100},
    )
    content_ok, content_message = contextual_content_check(screen, capture, require_container_items)
    return {"capture": capture, "contentCheck": {"ok": content_ok, "message": content_message}, "verified": content_ok}


def hide_screen(client: McpProcess, screen: str, timeout_ms: int) -> dict[str, Any]:
    payload = call_tool(
        client,
        "tla_hide_screen",
        {"screen": screen, "waitForCompletion": True, "timeoutMs": timeout_ms, "pollIntervalMs": 100},
    )
    command_ok, message = command_completed_successfully(payload)
    hidden = wait_for_observation(client, lambda obs: not screen_is_active(obs, screen), timeout_ms) if command_ok else None
    return {"ok": bool(command_ok and hidden is not None), "message": message, "commandSeq": payload.get("commandSeq")}


def visible_living_critter(observation: dict[str, Any]) -> dict[str, Any] | None:
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict) or critter.get("id") is None or critter.get("isChosen") is True:
            continue
        if critter.get("alive") is False or critter.get("isAlive") is False or critter.get("dead") is True:
            continue
        return critter
    return None


def context_screen_arguments(screen: str, observation: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    inventory = [item for item in observation.get("inventory", []) if isinstance(item, dict)]
    if screen == "SkillBox":
        return {"screen": screen}, ""
    if screen == "Aim":
        target = visible_living_critter(observation)
        return ({"screen": screen, "targetId": target["id"]}, "") if target else (None, "no_visible_living_target")
    if screen == "Split":
        item = next((entry for entry in inventory
                     if entry.get("id") is not None and int(entry.get("count") or 0) > 1
                     and entry.get("stackable") is not False), None)
        return ({"screen": screen, "itemId": item["id"]}, "") if item else (None, "no_inventory_stack")
    if screen == "Timer":
        item = next((entry for entry in inventory
                     if entry.get("id") is not None
                     and ((entry.get("canUse") is True and isinstance(entry.get("visualFeedback"), dict)
                           and entry["visualFeedback"].get("timerCapable") is True)
                          or str(entry.get("protoId") or "") in TIMED_USE_PROTO_IDS)), None)
        return ({"screen": screen, "itemId": item["id"]}, "") if item else (None, "no_timer_capable_item")
    if screen == "Use":
        inventory_with_ids = [entry for entry in inventory if entry.get("id") is not None]
        if not inventory_with_ids:
            return None, "empty_inventory"
        if not any(entry.get("canUseOnSmth") is True for entry in inventory_with_ids):
            return None, "no_inventory_item_usable_on_target"
        target = visible_living_critter(observation)
        if target is not None:
            return {"screen": screen, "targetId": target["id"]}, ""
        map_item = next((entry for entry in observation.get("mapItems", [])
                         if isinstance(entry, dict) and entry.get("id") is not None), None)
        if map_item is not None:
            return {"screen": screen, "itemId": map_item["id"], "isInventory": False}, ""
        return None, "no_visible_use_target"
    return None, "contextual_flow_not_supported"


def run_bridge_context(client: McpProcess, screen: str, output_relative: str,
                       settle_ms: int, timeout_ms: int) -> dict[str, Any]:
    entry: dict[str, Any] = {"screen": screen, "status": "failed", "verified": False}
    observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    if observation.get("hasChosen") is not True or observation.get("hasMap") is not True:
        entry.update(status="skipped", reason="chosen_on_map_required")
        return entry
    modal = active_modal_name(observation)
    if modal and not modal.endswith("::" + screen) and modal != screen:
        entry.update(status="skipped", reason=f"blocking_modal:{modal}")
        return entry

    context_args, reason = context_screen_arguments(screen, observation)
    if context_args is None:
        entry.update(status="skipped", reason=reason)
        return entry
    entry["context"] = context_args

    try:
        show = call_tool(
            client,
            "tla_show_context_screen",
            {**context_args, "waitForCompletion": True, "timeoutMs": timeout_ms, "pollIntervalMs": 100},
        )
        show_ok, show_message = command_completed_successfully(show)
        entry["show"] = {"ok": show_ok, "message": show_message, "commandSeq": show.get("commandSeq")}
        active = wait_for_observation(client, lambda obs: screen_is_active(obs, screen), timeout_ms) if show_ok else None
        if active is None:
            entry["reason"] = f"{screen.lower()}_did_not_open"
            return entry
        entry.update(capture_screen(client, screen, output_relative, settle_ms, timeout_ms))
        entry["status"] = "passed" if entry["verified"] else "failed"
        return entry
    except (SmokeError, OSError, ValueError) as exc:
        entry["reason"] = str(exc)
        return entry
    finally:
        try:
            entry["hide"] = hide_screen(client, screen, timeout_ms)
            entry["verified"] = bool(entry.get("verified") and entry["hide"]["ok"])
            if entry.get("status") == "passed" and not entry["verified"]:
                entry["status"] = "failed"
        except (SmokeError, OSError, ValueError) as exc:
            entry["hide"] = {"ok": False, "message": str(exc)}
            entry["verified"] = False
            if entry.get("status") == "passed":
                entry["status"] = "failed"


def run_skillbox(client: McpProcess, output_relative: str, settle_ms: int, timeout_ms: int) -> dict[str, Any]:
    return run_bridge_context(client, "SkillBox", output_relative, settle_ms, timeout_ms)


def run_pickup(client: McpProcess, output_relative: str, settle_ms: int, timeout_ms: int,
               requested_item_id: str) -> dict[str, Any]:
    entry: dict[str, Any] = {"screen": "PickUp", "status": "failed", "verified": False}
    observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    if observation.get("hasChosen") is not True or observation.get("hasMap") is not True:
        entry.update(status="skipped", reason="chosen_on_map_required")
        return entry

    already_active = screen_is_active(observation, "PickUp")
    try:
        candidate: dict[str, Any] | None = None
        if not already_active:
            modal = active_modal_name(observation)
            if modal:
                entry.update(status="skipped", reason=f"blocking_modal:{modal}")
                return entry
            safe_visible = sum(1 for item in observation.get("mapItems", [])
                               if isinstance(item, dict) and pickup_candidate_is_safe(item))
            candidate = select_pickup_candidate(
                observation,
                requested_item_id,
                is_reachable=lambda item: container_is_reachable(client, item, timeout_ms),
            )
            if candidate is None:
                # Separate the two prerequisite misses: nothing usable in sight vs. everything in sight
                # walled off. Both are missing context, not a client defect.
                entry["safeVisibleContainers"] = safe_visible
                entry["reachabilityProbeLimit"] = PICKUP_REACHABILITY_PROBE_LIMIT
                reason = "no_reachable_container" if safe_visible else "no_safe_visible_container"
                entry.update(status="skipped", reason=reason)
                return entry
            entry["target"] = {
                key: candidate.get(key)
                for key in (
                    "id",
                    "protoId",
                    "hex",
                    "hasContainer",
                    "hasLocker",
                    "hasDoor",
                    "canOpen",
                    "opened",
                    "lockerLocked",
                    "lockerJammed",
                    "lockerBroken",
                    "lockerNoOpen",
                    "isGag",
                    "isStatic",
                )
                if key in candidate
            }
            interaction = call_tool(
                client,
                "tla_pick_item",
                {
                    "itemId": candidate["id"],
                    "isStatic": bool(candidate.get("isStatic") or candidate.get("static")),
                    "waitForCompletion": True,
                    "timeoutMs": timeout_ms,
                    "pollIntervalMs": 100,
                },
            )
            interaction_ok, interaction_message = command_completed_successfully(interaction)
            entry["interaction"] = {
                "ok": interaction_ok,
                "message": interaction_message,
                "commandSeq": interaction.get("commandSeq"),
            }
            if not interaction_ok:
                entry["reason"] = "container_interaction_rejected"
                return entry

        active = wait_for_observation(
            client,
            lambda obs: screen_is_active(obs, "PickUp")
            and (not isinstance(obs.get("activeCollection"), dict)
                 or obs["activeCollection"].get("active") is True),
            timeout_ms,
        )
        if active is None:
            # The client walks the chosen critter to the container before opening it. If the approach
            # stalls out of pick range — a nearer hex freed up during the probe, a critter parked on the
            # only approach hex, a target reachable from afar but boxed in up close — the client silently
            # stops and no screen ever appears. That is the map's fault, not the GUI's, so report it as a
            # missing prerequisite with the measured geometry instead of an indistinguishable failure.
            approach = describe_pickup_approach(client, candidate, timeout_ms) if candidate else None
            if approach is not None:
                entry["approach"] = approach
                if approach["blocked"]:
                    entry.update(status="skipped", reason="approach_blocked")
                    return entry

            entry["reason"] = "pickup_collection_did_not_open"
            return entry

        collection = active.get("activeCollection") if isinstance(active.get("activeCollection"), dict) else {}
        received_count = collection.get("receivedCount")
        items = collection.get("items") if isinstance(collection.get("items"), list) else []
        require_items = bool((isinstance(received_count, int) and received_count > 0) or items)
        entry["collection"] = {
            "kind": collection.get("kind"),
            "transferType": collection.get("transferType"),
            "containerId": collection.get("containerId"),
            "receivedCount": received_count,
            "itemCount": len(items),
        }
        entry.update(capture_screen(client, "PickUp", output_relative, settle_ms, timeout_ms, require_items))
        entry["status"] = "passed" if entry["verified"] else "failed"
        return entry
    except (SmokeError, OSError, ValueError) as exc:
        entry["reason"] = str(exc)
        return entry
    finally:
        if already_active or entry.get("interaction", {}).get("ok"):
            try:
                entry["hide"] = hide_screen(client, "PickUp", timeout_ms)
                entry["verified"] = bool(entry.get("verified") and entry["hide"]["ok"])
                if entry.get("status") == "passed" and not entry["verified"]:
                    entry["status"] = "failed"
            except (SmokeError, OSError, ValueError) as exc:
                entry["hide"] = {"ok": False, "message": str(exc)}
                entry["verified"] = False
                if entry.get("status") == "passed":
                    entry["status"] = "failed"


def run_radio(client: McpProcess, output_relative: str, settle_ms: int, timeout_ms: int) -> dict[str, Any]:
    entry: dict[str, Any] = {"screen": "Radio", "status": "failed", "verified": False}
    observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    already_active = screen_is_active(observation, "Radio")
    should_hide = already_active
    try:
        if not already_active:
            if observation.get("hasChosen") is not True:
                entry.update(status="skipped", reason="chosen_required")
                return entry
            modal = active_modal_name(observation)
            if modal:
                entry.update(status="skipped", reason=f"blocking_modal:{modal}")
                return entry
            radio = select_radio_candidate(observation)
            if radio is None:
                entry.update(status="skipped", reason="no_owned_radio")
                return entry
            entry["target"] = {
                key: radio.get(key)
                for key in ("id", "protoId", "hasRadio", "canUse")
                if key in radio
            }
            interaction = call_tool(
                client,
                "tla_use_item",
                {
                    "itemId": radio["id"],
                    "waitForCompletion": True,
                    "timeoutMs": timeout_ms,
                    "pollIntervalMs": 100,
                },
            )
            interaction_ok, interaction_message = command_completed_successfully(interaction)
            entry["interaction"] = {
                "ok": interaction_ok,
                "message": interaction_message,
                "commandSeq": interaction.get("commandSeq"),
            }
            should_hide = interaction_ok
            if not interaction_ok:
                entry["reason"] = "radio_self_use_rejected"
                return entry

        active = wait_for_observation(client, lambda obs: screen_is_active(obs, "Radio"), timeout_ms)
        if active is None:
            entry["reason"] = "radio_did_not_open"
            return entry

        should_hide = True
        entry.update(capture_screen(client, "Radio", output_relative, settle_ms, timeout_ms))
        entry["status"] = "passed" if entry["verified"] else "failed"
        return entry
    except (SmokeError, OSError, ValueError) as exc:
        entry["reason"] = str(exc)
        return entry
    finally:
        if should_hide:
            try:
                entry["hide"] = hide_screen(client, "Radio", timeout_ms)
                entry["verified"] = bool(entry.get("verified") and entry["hide"]["ok"])
                if entry.get("status") == "passed" and not entry["verified"]:
                    entry["status"] = "failed"
            except (SmokeError, OSError, ValueError) as exc:
                entry["hide"] = {"ok": False, "message": str(exc)}
                entry["verified"] = False
                if entry.get("status") == "passed":
                    entry["status"] = "failed"


def run_elevator(client: McpProcess, output_relative: str, settle_ms: int, timeout_ms: int,
                 trigger_hex: tuple[int, int] | None) -> dict[str, Any]:
    entry: dict[str, Any] = {"screen": "Elevator", "status": "failed", "verified": False}
    observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    already_active = screen_is_active(observation, "Elevator")
    should_hide = already_active
    try:
        if already_active:
            entry["source"] = "already_active"
        else:
            if observation.get("hasChosen") is not True or observation.get("hasMap") is not True:
                entry.update(status="skipped", reason="chosen_on_map_required")
                return entry
            modal = active_modal_name(observation)
            if modal:
                entry.update(status="skipped", reason=f"blocking_modal:{modal}")
                return entry
            if trigger_hex is None:
                entry.update(status="skipped", reason="elevator_trigger_hex_required")
                return entry

            trigger_x, trigger_y = trigger_hex
            entry["source"] = "trigger_hex"
            entry["triggerHex"] = {"x": trigger_x, "y": trigger_y}
            movement = call_tool(
                client,
                "tla_move_to_hex",
                {
                    "x": trigger_x,
                    "y": trigger_y,
                    "waitForCompletion": True,
                    "timeoutMs": timeout_ms,
                    "pollIntervalMs": 100,
                },
            )
            movement_ok, movement_message = command_completed_successfully(movement)
            entry["movement"] = {
                "ok": movement_ok,
                "message": movement_message,
                "commandSeq": movement.get("commandSeq"),
            }
            should_hide = movement_ok
            if not movement_ok:
                entry["reason"] = "elevator_trigger_move_rejected"
                return entry

        active = wait_for_observation(client, lambda obs: screen_is_active(obs, "Elevator"), timeout_ms)
        if active is None:
            entry["reason"] = "elevator_did_not_open"
            return entry

        should_hide = True
        entry.update(capture_screen(client, "Elevator", output_relative, settle_ms, timeout_ms))
        entry["status"] = "passed" if entry["verified"] else "failed"
        return entry
    except (SmokeError, OSError, ValueError) as exc:
        entry["reason"] = str(exc)
        return entry
    finally:
        if should_hide:
            # Closing the modal is deliberate; choosing a floor is never part of this visual test.
            try:
                entry["hide"] = hide_screen(client, "Elevator", timeout_ms)
                entry["verified"] = bool(entry.get("verified") and entry["hide"]["ok"])
                if entry.get("status") == "passed" and not entry["verified"]:
                    entry["status"] = "failed"
            except (SmokeError, OSError, ValueError) as exc:
                entry["hide"] = {"ok": False, "message": str(exc)}
                entry["verified"] = False
                if entry.get("status") == "passed":
                    entry["status"] = "failed"


def run_dialog_box(client: McpProcess, output_relative: str, settle_ms: int, timeout_ms: int) -> dict[str, Any]:
    entry: dict[str, Any] = {"screen": "DialogBox", "status": "failed", "verified": False}
    observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    if screen_is_active(observation, "DialogBox") or active_dialog_box_prompt(observation) is not None:
        entry.update(status="skipped", reason="dialog_box_already_active")
        return entry
    if observation.get("hasChosen") is not True:
        entry.update(status="skipped", reason="chosen_required")
        return entry
    modal = active_modal_name(observation)
    if modal:
        entry.update(status="skipped", reason=f"blocking_modal:{modal}")
        return entry

    cleanup_needed = False
    try:
        fixture = call_tool(
            client,
            "tla_qa_show_dialog_box",
            {"waitForCompletion": True, "timeoutMs": timeout_ms, "pollIntervalMs": 100},
        )
        fixture_ok, fixture_message = command_completed_successfully(fixture)
        entry["fixture"] = {
            "ok": fixture_ok,
            "message": fixture_message,
            "commandSeq": fixture.get("commandSeq"),
        }
        if not fixture_ok:
            if "qa_commands_disabled" in fixture_message:
                entry.update(status="skipped", reason="qa_commands_disabled")
            else:
                entry["reason"] = f"dialog_box_fixture_rejected:{fixture_message}"
            return entry

        cleanup_needed = True
        prompt_observation = wait_for_observation(
            client,
            lambda obs: screen_is_active(obs, "DialogBox") and active_dialog_box_prompt(obs) is not None,
            timeout_ms,
        )
        if prompt_observation is None:
            entry["reason"] = "dialog_box_prompt_did_not_open"
            return entry

        prompt = active_dialog_box_prompt(prompt_observation)
        if prompt is None:
            entry["reason"] = "dialog_box_prompt_contract_missing"
            return entry
        session = prompt["dialogBoxSession"]
        buttons = prompt.get("buttons") if isinstance(prompt.get("buttons"), list) else []
        entry["uiPrompt"] = {
            "kind": prompt.get("kind"),
            "dialogBoxSession": session,
            "buttons": buttons,
        }
        if not dialog_box_has_safe_fixture_answer(prompt):
            entry["reason"] = "dialog_box_safe_answer_missing"
            return entry

        capture_ok = False
        try:
            entry.update(capture_screen(client, "DialogBox", output_relative, settle_ms, timeout_ms))
            capture_ok = entry.get("verified") is True
            if not capture_ok:
                entry["reason"] = "dialog_box_content_not_visible"
        except (SmokeError, OSError, ValueError) as exc:
            entry["reason"] = f"dialog_box_capture_failed:{exc}"
        entry["captureVerified"] = capture_ok
        entry["verified"] = False

        answer = call_tool(
            client,
            "tla_ui_answer",
            {
                "answerIndex": 1,
                "answerId": "answer_1",
                "expectedSession": session,
                "waitForCompletion": True,
                "timeoutMs": timeout_ms,
                "pollIntervalMs": 100,
            },
        )
        answer_ok, answer_message = command_completed_successfully(answer)
        entry["answer"] = {
            "ok": answer_ok,
            "message": answer_message,
            "commandSeq": answer.get("commandSeq"),
            "answerIndex": 1,
            "answerId": "answer_1",
            "expectedSession": session,
        }
        if not answer_ok:
            entry["reason"] = f"dialog_box_safe_answer_rejected:{answer_message}"
            return entry

        closed = wait_for_observation(
            client,
            lambda obs: not screen_is_active(obs, "DialogBox") and active_dialog_box_prompt(obs) is None,
            timeout_ms,
        )
        if closed is None:
            entry["reason"] = "dialog_box_did_not_close"
            return entry

        cleanup_needed = False
        entry["verified"] = capture_ok
        entry["status"] = "passed" if capture_ok else "failed"
        return entry
    except (SmokeError, OSError, ValueError) as exc:
        entry["reason"] = str(exc)
        return entry
    finally:
        if cleanup_needed:
            try:
                entry["fallbackHide"] = hide_screen(client, "DialogBox", timeout_ms)
            except (SmokeError, OSError, ValueError) as exc:
                entry["fallbackHide"] = {"ok": False, "message": str(exc)}


def run_playtest(client: McpProcess, screens: list[str], output_relative: str, settle_ms: int,
                 timeout_ms: int, pickup_item_id: str, require_all: bool,
                 elevator_trigger_hex: tuple[int, int] | None = None) -> dict[str, Any]:
    started_ms = int(time.time() * 1000)
    entries: list[dict[str, Any]] = []
    for requested_screen in screens:
        screen = requested_screen.rsplit("::", 1)[-1]
        if screen in BRIDGE_CONTEXT_SCREENS:
            entries.append(run_bridge_context(client, screen, output_relative, settle_ms, timeout_ms))
        elif screen == "PickUp":
            entries.append(run_pickup(client, output_relative, settle_ms, timeout_ms, pickup_item_id))
        elif screen == "Radio":
            entries.append(run_radio(client, output_relative, settle_ms, timeout_ms))
        elif screen == "Elevator":
            entries.append(run_elevator(client, output_relative, settle_ms, timeout_ms, elevator_trigger_hex))
        elif screen == "DialogBox":
            entries.append(run_dialog_box(client, output_relative, settle_ms, timeout_ms))
        else:
            entries.append({
                "screen": screen,
                "status": "skipped",
                "verified": False,
                "reason": "contextual_flow_not_supported",
            })

    passed = [entry for entry in entries if entry.get("status") == "passed"]
    failed = [entry for entry in entries if entry.get("status") == "failed"]
    skipped = [entry for entry in entries if entry.get("status") == "skipped"]
    ok = bool(passed) and not failed and (not require_all or not skipped)
    return {
        "schemaVersion": 1,
        "kind": "tla_context_gui_playtest",
        "startedAtUnixMs": started_ms,
        "finishedAtUnixMs": int(time.time() * 1000),
        "screens": entries,
        "summary": {"passed": len(passed), "failed": len(failed), "skipped": len(skipped)},
        "contextRequirements": CONTEXT_REQUIREMENTS,
        "verified": ok,
    }


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("TLA_AI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TLA_AI_PORT", "43011")))
    parser.add_argument("--token", default=os.environ.get("TLA_AI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TLA_AI_TIMEOUT", "3")))
    parser.add_argument("--workspace-root", default=os.environ.get("TLA_WORKSPACE_ROOT", str(WORKSPACE_ROOT)))
    parser.add_argument("--screens", default=",".join(DEFAULT_SCREENS),
                        help="Comma-separated screen names; implemented: SkillBox, Aim, Split, Timer, Use, PickUp, Radio, Elevator, DialogBox.")
    parser.add_argument("--pickup-item-id", default="",
                        help="Optional visible container item id; otherwise the nearest safe container is used.")
    parser.add_argument(
        "--elevator-trigger-hex",
        type=int,
        nargs=2,
        metavar=("X", "Y"),
        help="Real authored elevator trigger hex. Without it Elevator is captured only when already open.",
    )
    parser.add_argument("--output-dir", default="",
                        help="Directory inside the workspace; a timestamped directory is used by default.")
    parser.add_argument("--report", default="", help="JSON report path; defaults to <output-dir>/report.json.")
    parser.add_argument("--settle-ms", type=int, default=500)
    parser.add_argument("--command-timeout-ms", type=int, default=60000)
    parser.add_argument("--require-all", action="store_true", help="Treat unavailable/skipped contexts as failure.")
    args = parser.parse_args()

    if args.settle_ms < 0 or args.settle_ms > 10000:
        parser.error("--settle-ms must be in the 0..10000 range")
    if args.command_timeout_ms < 1000 or args.command_timeout_ms > 180000:
        parser.error("--command-timeout-ms must be in the 1000..180000 range")
    if args.elevator_trigger_hex is not None and any(value < 0 or value > 65535 for value in args.elevator_trigger_hex):
        parser.error("--elevator-trigger-hex coordinates must be in the 0..65535 range")
    screens = [screen.strip() for screen in args.screens.split(",") if screen.strip()]
    if not screens:
        parser.error("--screens must contain at least one screen name")

    workspace_root = Path(args.workspace_root).resolve()
    default_output = workspace_root / "Workspace" / "AiControlScreenshots" / time.strftime("context-gui-%Y%m%d-%H%M%S")
    try:
        output_dir = path_in_workspace(workspace_root, args.output_dir, default_output)
        report_path = path_in_workspace(workspace_root, args.report, output_dir / "report.json")
    except ValueError as exc:
        parser.error(str(exc))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_relative = output_dir.relative_to(workspace_root).as_posix()

    command = build_adapter_command(ADAPTER_PATH, args.host, args.port, args.timeout, args.token)
    command.extend(["--workspace-root", str(workspace_root)])
    client = McpProcess(command, request_timeout=max(args.timeout, args.command_timeout_ms / 1000.0 + 5.0))
    try:
        initialize_client(client, "tla-context-gui-playtest")
        report = run_playtest(
            client,
            screens,
            output_relative,
            args.settle_ms,
            args.command_timeout_ms,
            args.pickup_item_id.strip(),
            args.require_all,
            tuple(args.elevator_trigger_hex) if args.elevator_trigger_hex is not None else None,
        )
    except (SmokeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    report.update({
        "workspaceRoot": str(workspace_root),
        "outputDirectory": str(output_dir),
        "reportPath": str(report_path),
    })
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
