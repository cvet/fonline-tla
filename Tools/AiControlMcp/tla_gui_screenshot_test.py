#!/usr/bin/env python3
"""Capture and verify a repeatable screenshot matrix for parameterless TLA GUI screens.

Run this against an already connected in-game client with AiControl.Enabled=True. Contextual screens
such as Dialog, Barter, PickUp, Split, Aim, Radio, and elevators must be tested through their live flows.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

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


DEFAULT_SCREENS = ("Options", "Inventory", "Character", "PipBoy", "FixBoy", "Menu", "Credits")
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CENTERED_SCREEN_SIZES = {
    "Options": (640, 480),
    "Inventory": (499, 377),
    "Character": (640, 480),
    "PipBoy": (640, 480),
    "Menu": (164, 144),
}
CREDITS_CONTENT_ROI = (0.20, 0.45, 0.80, 1.00)
CREDITS_MIN_VISIBLE_PIXELS = 24
CREDITS_MIN_VISIBLE_WIDTH = 6
CREDITS_MIN_VISIBLE_HEIGHT = 3
FIXBOY_SCREEN_SIZE = (640, 480)
FIXBOY_CONTENT_RECT = (85, 70, 425, 420)
FIXBOY_MIN_SETTLE_MS = 1500
CHOSEN_REQUIRED_SCREENS = frozenset({"Inventory", "Character", "PipBoy", "FixBoy"})

# These rectangles target text which must be present inside the centered, fixed-size legacy screens.
# Multiple independent regions make a coincidentally colorful map much less likely to pass.
CENTERED_SCREEN_CONTENT_REGIONS = {
    "Options": (
        ((35, 20, 225, 330), 200, 60, 40),
        ((225, 20, 600, 330), 200, 100, 40),
        ((470, 430, 580, 475), 80, 35, 8),
    ),
    "Inventory": (
        ((285, 45, 465, 245), 200, 70, 60),
    ),
    "Character": (
        ((15, 30, 170, 300), 150, 60, 50),
        ((175, 30, 335, 315), 150, 60, 40),
        ((350, 15, 625, 235), 200, 100, 60),
    ),
    "PipBoy": (
        ((300, 80, 620, 340), 500, 120, 80),
    ),
    "Menu": (
        ((20, 20, 145, 48), 100, 35, 8),
        ((20, 56, 145, 84), 100, 35, 8),
        ((20, 92, 145, 120), 100, 50, 8),
    ),
}

BARTER_SCREEN_SIZE = (640, 311)
BARTER_HEADER_RECT = (140, 10, 520, 110)
BARTER_ITEM_RECTS = (
    (105, 151, 175, 191),
    (241, 130, 311, 171),
    (329, 130, 399, 171),
    (464, 151, 534, 191),
)
BARTER_COST_RECTS = ((241, 289, 311, 306), (329, 289, 399, 306))


def command_completed_successfully(payload: dict[str, Any]) -> tuple[bool, str]:
    completion = payload.get("completion")
    if not isinstance(completion, dict):
        return False, "completion object is missing"
    if not completion.get("completed"):
        return False, "command completion timed out" if completion.get("timedOut") else "command did not complete"
    event = completion.get("event")
    if not isinstance(event, dict):
        return False, "command_completed event is missing"
    if event.get("success") is not True:
        return False, str(event.get("message") or "command failed")
    return True, str(event.get("message") or "ok")


def path_in_workspace(workspace_root: Path, value: str, default: Path) -> Path:
    path = Path(value).expanduser() if value.strip() else default
    if not path.is_absolute():
        path = workspace_root / path
    path = path.resolve()
    try:
        path.relative_to(workspace_root.resolve())
    except ValueError as exc:
        raise ValueError(f"Path must stay inside the workspace: {path}") from exc
    return path


def screen_file_name(screen: str) -> str:
    safe = "".join(character if character.isalnum() or character in "-_" else "_" for character in screen)
    return (safe or "screen") + ".tga"


def observed_screen_names(observation: dict[str, Any]) -> list[str]:
    screen = observation.get("screen")
    if not isinstance(screen, dict):
        return []
    names = screen.get("screens")
    return [str(name) for name in names] if isinstance(names, list) else []


def capture_tga_path(capture: dict[str, Any]) -> Path | None:
    candidates: list[Path] = []
    for field in ("absolutePath", "path", "relativePath"):
        value = capture.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = WORKSPACE_ROOT / candidate
        candidate = candidate.resolve()
        candidates.append(candidate)
        if candidate.is_file():
            return candidate
    return candidates[0] if candidates else None


def read_uncompressed_true_color_tga(path: Path) -> tuple[bytes, int, int, int, int, bool, bool]:
    data = path.read_bytes()
    if len(data) < 18:
        raise ValueError("TGA header is truncated")

    id_length = data[0]
    color_map_type = data[1]
    image_type = data[2]
    width = int.from_bytes(data[12:14], "little")
    height = int.from_bytes(data[14:16], "little")
    pixel_depth = data[16]
    image_descriptor = data[17]
    if color_map_type != 0 or image_type != 2 or pixel_depth not in (24, 32) or width <= 0 or height <= 0:
        raise ValueError("Content check requires an uncompressed true-color TGA")

    bytes_per_pixel = pixel_depth // 8
    payload_offset = 18 + id_length
    payload_size = width * height * bytes_per_pixel
    if payload_offset + payload_size > len(data):
        raise ValueError("TGA pixel payload is truncated")

    return data, width, height, bytes_per_pixel, payload_offset, bool(image_descriptor & 0x20), bool(image_descriptor & 0x10)


def tga_roi_has_visible_content(
    image: tuple[bytes, int, int, int, int, bool, bool],
    bounds: tuple[int, int, int, int],
    is_visible: Callable[[int, int, int], bool],
    minimum_pixels: int,
    minimum_width: int,
    minimum_height: int,
) -> bool:
    data, width, height, bytes_per_pixel, payload_offset, origin_top, origin_right = image
    left = max(0, min(width - 1, bounds[0]))
    top = max(0, min(height - 1, bounds[1]))
    right = max(left + 1, min(width, bounds[2]))
    bottom = max(top + 1, min(height, bounds[3]))

    visible_pixels = 0
    min_visible_x = right
    max_visible_x = left
    min_visible_y = bottom
    max_visible_y = top
    for y in range(top, bottom):
        storage_y = y if origin_top else height - 1 - y
        row_offset = payload_offset + storage_y * width * bytes_per_pixel
        for x in range(left, right):
            storage_x = width - 1 - x if origin_right else x
            pixel_offset = row_offset + storage_x * bytes_per_pixel
            blue, green, red = data[pixel_offset:pixel_offset + 3]
            if not is_visible(red, green, blue):
                continue

            visible_pixels += 1
            min_visible_x = min(min_visible_x, x)
            max_visible_x = max(max_visible_x, x)
            min_visible_y = min(min_visible_y, y)
            max_visible_y = max(max_visible_y, y)
            if (visible_pixels >= minimum_pixels and
                    max_visible_x - min_visible_x + 1 >= minimum_width and
                    max_visible_y - min_visible_y + 1 >= minimum_height):
                return True

    return False


def tga_roi_statistics(
    image: tuple[bytes, int, int, int, int, bool, bool],
    bounds: tuple[int, int, int, int],
    is_visible: Callable[[int, int, int], bool],
) -> dict[str, int | float]:
    data, width, height, bytes_per_pixel, payload_offset, origin_top, origin_right = image
    left = max(0, min(width - 1, bounds[0]))
    top = max(0, min(height - 1, bounds[1]))
    right = max(left + 1, min(width, bounds[2]))
    bottom = max(top + 1, min(height, bounds[3]))

    visible_pixels = 0
    dark_pixels = 0
    min_visible_x = right
    max_visible_x = left
    min_visible_y = bottom
    max_visible_y = top
    color_buckets: set[tuple[int, int, int]] = set()
    for y in range(top, bottom):
        storage_y = y if origin_top else height - 1 - y
        row_offset = payload_offset + storage_y * width * bytes_per_pixel
        for x in range(left, right):
            storage_x = width - 1 - x if origin_right else x
            pixel_offset = row_offset + storage_x * bytes_per_pixel
            blue, green, red = data[pixel_offset:pixel_offset + 3]
            color_buckets.add((red // 16, green // 16, blue // 16))
            if max(red, green, blue) < 80:
                dark_pixels += 1
            if not is_visible(red, green, blue):
                continue
            visible_pixels += 1
            min_visible_x = min(min_visible_x, x)
            max_visible_x = max(max_visible_x, x)
            min_visible_y = min(min_visible_y, y)
            max_visible_y = max(max_visible_y, y)

    pixel_count = (right - left) * (bottom - top)
    return {
        "pixels": pixel_count,
        "visiblePixels": visible_pixels,
        "visibleWidth": max_visible_x - min_visible_x + 1 if visible_pixels else 0,
        "visibleHeight": max_visible_y - min_visible_y + 1 if visible_pixels else 0,
        "visibleRatio": visible_pixels / pixel_count,
        "darkRatio": dark_pixels / pixel_count,
        "colorBuckets": len(color_buckets),
    }


def centered_screen_bounds(
    image: tuple[bytes, int, int, int, int, bool, bool],
    screen_size: tuple[int, int],
    relative_bounds: tuple[int, int, int, int],
) -> tuple[int, int, int, int] | None:
    _, width, height, _, _, _, _ = image
    screen_width, screen_height = screen_size
    if width < screen_width or height < screen_height:
        return None
    screen_left = (width - screen_width) // 2
    screen_top = (height - screen_height) // 2
    return (
        screen_left + relative_bounds[0],
        screen_top + relative_bounds[1],
        screen_left + relative_bounds[2],
        screen_top + relative_bounds[3],
    )


def is_interface_green(red: int, green: int, blue: int) -> bool:
    return green >= 180 and 35 <= red <= 110 and blue <= 40 and green - red >= 100


def is_interface_gold(red: int, green: int, blue: int) -> bool:
    return 120 <= red <= 210 and 80 <= green <= 170 and blue <= 55 and red >= green + 15 and green >= blue + 45


def is_neutral_bright_text(red: int, green: int, blue: int) -> bool:
    return min(red, green, blue) >= 100 and max(red, green, blue) - min(red, green, blue) <= 50


def tga_centered_screen_content_is_visible(path: Path, screen_name: str) -> bool:
    image = read_uncompressed_true_color_tga(path)
    screen_size = CENTERED_SCREEN_SIZES[screen_name]
    predicate = is_interface_gold if screen_name == "Menu" else is_interface_green
    for relative_bounds, minimum_pixels, minimum_width, minimum_height in CENTERED_SCREEN_CONTENT_REGIONS[screen_name]:
        bounds = centered_screen_bounds(image, screen_size, relative_bounds)
        if bounds is None:
            return False
        statistics = tga_roi_statistics(image, bounds, predicate)
        if (statistics["visiblePixels"] < minimum_pixels or
                statistics["visibleWidth"] < minimum_width or
                statistics["visibleHeight"] < minimum_height or
                statistics["visibleRatio"] > 0.45 or
                statistics["darkRatio"] < 0.35):
            return False
    return True


def tga_barter_panels_are_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    header_bounds = centered_screen_bounds(image, BARTER_SCREEN_SIZE, BARTER_HEADER_RECT)
    if header_bounds is None:
        return False
    header = tga_roi_statistics(image, header_bounds, lambda _red, _green, _blue: False)
    if header["darkRatio"] < 0.80:
        return False

    for relative_bounds in BARTER_ITEM_RECTS:
        bounds = centered_screen_bounds(image, BARTER_SCREEN_SIZE, relative_bounds)
        if bounds is None:
            return False
        if tga_roi_statistics(image, bounds, lambda _red, _green, _blue: False)["colorBuckets"] < 60:
            return False

    for relative_bounds in BARTER_COST_RECTS:
        bounds = centered_screen_bounds(image, BARTER_SCREEN_SIZE, relative_bounds)
        if bounds is None:
            return False
        statistics = tga_roi_statistics(image, bounds, is_neutral_bright_text)
        if (statistics["visiblePixels"] < 20 or
                statistics["visibleWidth"] < 10 or
                statistics["visibleHeight"] < 5 or
                statistics["visibleRatio"] > 0.45):
            return False
    return True


def tga_relative_roi_has_visible_content(path: Path,
                                         roi: tuple[float, float, float, float] = CREDITS_CONTENT_ROI) -> bool:
    image = read_uncompressed_true_color_tga(path)
    _, width, height, _, _, _, _ = image
    bounds = (int(width * roi[0]), int(height * roi[1]), int(width * roi[2]), int(height * roi[3]))
    return tga_roi_has_visible_content(
        image,
        bounds,
        lambda red, green, blue: red > 24 or green > 24 or blue > 24,
        CREDITS_MIN_VISIBLE_PIXELS,
        CREDITS_MIN_VISIBLE_WIDTH,
        CREDITS_MIN_VISIBLE_HEIGHT,
    )


def tga_fixboy_recipe_list_is_visible(path: Path) -> bool:
    image = read_uncompressed_true_color_tga(path)
    _, width, height, _, _, _, _ = image
    screen_left = (width - FIXBOY_SCREEN_SIZE[0]) // 2
    screen_top = (height - FIXBOY_SCREEN_SIZE[1]) // 2
    bounds = (
        screen_left + FIXBOY_CONTENT_RECT[0],
        screen_top + FIXBOY_CONTENT_RECT[1],
        screen_left + FIXBOY_CONTENT_RECT[2],
        screen_top + FIXBOY_CONTENT_RECT[3],
    )
    return tga_roi_has_visible_content(
        image,
        bounds,
        lambda red, green, blue: max(red, green, blue) >= 64 and max(red, green, blue) - min(red, green, blue) >= 32,
        24,
        6,
        3,
    )


def capture_settle_ms(screen: str, requested_ms: int) -> int:
    return max(requested_ms, FIXBOY_MIN_SETTLE_MS) if screen.rsplit("::", 1)[-1] == "FixBoy" else requested_ms


def capture_content_check(screen: str, capture: dict[str, Any], allow_generic: bool = False) -> tuple[bool, str]:
    if capture.get("verified") is not True:
        return False, "capture_not_verified"
    screen_name = screen.rsplit("::", 1)[-1]
    if screen_name not in {*CENTERED_SCREEN_SIZES, "Credits", "FixBoy"}:
        return ((True, "generic_capture_verified") if allow_generic else
                (False, "content_oracle_unsupported"))

    path = capture_tga_path(capture)
    prefix = screen_name.lower()
    if path is None or not path.is_file():
        return False, f"{prefix}_tga_missing"
    try:
        if screen_name == "Credits":
            has_visible_content = tga_relative_roi_has_visible_content(path)
        elif screen_name == "FixBoy":
            has_visible_content = tga_fixboy_recipe_list_is_visible(path)
        else:
            has_visible_content = tga_centered_screen_content_is_visible(path, screen_name)
    except (OSError, ValueError):
        return False, f"{prefix}_tga_invalid"
    if not has_visible_content:
        failure_messages = {
            "Credits": "credits_text_not_visible",
            "FixBoy": "fixboy_recipe_list_not_visible",
            "Options": "options_controls_not_visible",
            "Inventory": "inventory_stats_not_visible",
            "Character": "character_stats_not_visible",
            "PipBoy": "pipboy_content_not_visible",
            "Menu": "menu_buttons_not_visible",
        }
        return False, failure_messages[screen_name]
    success_messages = {
        "Credits": "credits_text_visible",
        "FixBoy": "fixboy_recipe_list_visible",
        "Options": "options_controls_visible",
        "Inventory": "inventory_stats_visible",
        "Character": "character_stats_visible",
        "PipBoy": "pipboy_content_visible",
        "Menu": "menu_buttons_visible",
    }
    return True, success_messages[screen_name]


def wait_for_screen_state(client: McpProcess, screen: str, active: bool, timeout_ms: int) -> tuple[bool, list[str]]:
    deadline = time.monotonic() + max(0, timeout_ms) / 1000.0
    active_names: list[str] = []
    while True:
        observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
        active_names = observed_screen_names(observation)
        is_active = any(name == screen or name.endswith("::" + screen) for name in active_names)
        if is_active == active:
            return True, active_names
        if time.monotonic() >= deadline:
            return False, active_names
        time.sleep(0.1)


def run_audit(client: McpProcess, screens: list[str], output_relative: str, settle_ms: int,
              timeout_ms: int, allow_generic: bool = False) -> dict[str, Any]:
    started_ms = int(time.time() * 1000)
    entries: list[dict[str, Any]] = []
    wait_args = {"waitForCompletion": True, "timeoutMs": timeout_ms, "pollIntervalMs": 100}

    initial_observation = unwrap_observation_payload(call_tool(client, "tla_observe"))
    required_screens = sorted({screen.rsplit("::", 1)[-1] for screen in screens} & CHOSEN_REQUIRED_SCREENS)
    if required_screens and (initial_observation.get("hasChosen") is not True or initial_observation.get("hasMap") is not True):
        raise SmokeError(f"Screens {', '.join(required_screens)} require an in-game chosen critter on a map")

    for screen in screens:
        entry: dict[str, Any] = {"screen": screen, "verified": False}
        try:
            show = call_tool(client, "tla_show_screen", {"screen": screen, **wait_args})
            show_ok, show_message = command_completed_successfully(show)
            entry["show"] = {"ok": show_ok, "message": show_message, "commandSeq": show.get("commandSeq")}
            if not show_ok:
                entries.append(entry)
                continue

            active_matched, active_names = wait_for_screen_state(client, screen, True, timeout_ms)
            entry["activeScreens"] = active_names
            entry["activeMatched"] = active_matched

            prefix = output_relative.rstrip("/")
            relative_path = f"{prefix}/{screen_file_name(screen)}" if prefix else screen_file_name(screen)
            capture = call_tool(
                client,
                "tla_save_screenshot",
                {"path": relative_path, "settleMs": capture_settle_ms(screen, settle_ms), "timeoutMs": timeout_ms, "pollIntervalMs": 100},
            )
            entry["capture"] = capture
            content_ok, content_message = capture_content_check(screen, capture, allow_generic)
            entry["contentCheck"] = {"ok": content_ok, "message": content_message}
            entry["verified"] = bool(entry["activeMatched"] and content_ok)
        except (SmokeError, OSError, ValueError) as exc:
            entry["error"] = str(exc)
        finally:
            try:
                hide = call_tool(client, "tla_hide_screen", {"screen": screen, **wait_args})
                hide_ok, hide_message = command_completed_successfully(hide)
                hidden_matched, remaining_screens = wait_for_screen_state(client, screen, False, timeout_ms) if hide_ok else (False, [])
                entry["hide"] = {"ok": hide_ok and hidden_matched,
                                 "message": hide_message if hidden_matched else "screen remained active",
                                 "commandSeq": hide.get("commandSeq"),
                                 "remainingScreens": remaining_screens}
                entry["verified"] = bool(entry.get("verified") and hide_ok and hidden_matched)
            except (SmokeError, OSError, ValueError) as exc:
                entry["hide"] = {"ok": False, "message": str(exc)}
                entry["verified"] = False

        entries.append(entry)

    return {
        "schemaVersion": 1,
        "kind": "tla_gui_screenshot_audit",
        "startedAtUnixMs": started_ms,
        "finishedAtUnixMs": int(time.time() * 1000),
        "screens": entries,
        "verified": bool(entries) and all(bool(entry.get("verified")) for entry in entries),
    }


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("TLA_AI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TLA_AI_PORT", "43011")))
    parser.add_argument("--token", default=os.environ.get("TLA_AI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TLA_AI_TIMEOUT", "3")))
    parser.add_argument("--workspace-root", default=os.environ.get("TLA_WORKSPACE_ROOT", str(WORKSPACE_ROOT)))
    parser.add_argument("--screens", default=",".join(DEFAULT_SCREENS), help="Comma-separated parameterless GuiScreen names.")
    parser.add_argument("--output-dir", default="", help="Directory inside the workspace; a timestamped directory is used by default.")
    parser.add_argument("--manifest", default="", help="JSON manifest path inside the workspace; defaults to <output-dir>/manifest.json.")
    parser.add_argument("--settle-ms", type=int, default=250)
    parser.add_argument("--command-timeout-ms", type=int, default=10000)
    parser.add_argument("--allow-generic", action="store_true",
                        help="allow unknown screens to pass using only the generic nonblank-frame check")
    args = parser.parse_args()

    if args.settle_ms < 0 or args.settle_ms > 10000:
        parser.error("--settle-ms must be in the 0..10000 range")
    if args.command_timeout_ms < 0 or args.command_timeout_ms > 60000:
        parser.error("--command-timeout-ms must be in the 0..60000 range")
    screens = [screen.strip() for screen in args.screens.split(",") if screen.strip()]
    if not screens:
        parser.error("--screens must contain at least one GuiScreen name")

    workspace_root = Path(args.workspace_root).resolve()
    default_output = workspace_root / "Workspace" / "AiControlScreenshots" / time.strftime("gui-audit-%Y%m%d-%H%M%S")
    try:
        output_dir = path_in_workspace(workspace_root, args.output_dir, default_output)
        manifest_path = path_in_workspace(workspace_root, args.manifest, output_dir / "manifest.json")
    except ValueError as exc:
        parser.error(str(exc))
    output_relative = output_dir.relative_to(workspace_root).as_posix()

    command = build_adapter_command(ADAPTER_PATH, args.host, args.port, args.timeout, args.token)
    command.extend(["--workspace-root", str(workspace_root)])
    client = McpProcess(command, request_timeout=max(args.timeout, args.command_timeout_ms / 1000.0 + 5.0))
    try:
        initialize_client(client, "tla-gui-screenshot-test")
        manifest = run_audit(client, screens, output_relative, args.settle_ms,
                             args.command_timeout_ms, args.allow_generic)
    except (SmokeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    manifest["workspaceRoot"] = str(workspace_root)
    manifest["outputDirectory"] = str(output_dir)
    manifest["manifestPath"] = str(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
