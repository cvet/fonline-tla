#!/usr/bin/env python3
"""Pure-Python tests for contextual GUI target selection and screenshot oracles."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, patch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tla_context_gui_playtest as context_gui  # noqa: E402


def successful_command(message: str = "ok") -> dict[str, object]:
    return {
        "commandSeq": 17,
        "completion": {
            "completed": True,
            "event": {"success": True, "message": message},
        },
    }


def failed_command(message: str) -> dict[str, object]:
    return {
        "commandSeq": 18,
        "completion": {
            "completed": True,
            "event": {"success": False, "message": message},
        },
    }


def safe_container_item(item_id: object = 1, **overrides: object) -> dict[str, object]:
    item: dict[str, object] = {
        "id": item_id,
        "hasContainer": True,
        "hasLocker": True,
        "hasDoor": False,
        "canOpen": True,
        "opened": False,
        "lockerLocked": False,
        "lockerJammed": False,
        "lockerBroken": False,
        "lockerNoOpen": False,
        "isGag": False,
    }
    item.update(overrides)
    return item


def write_tga(path: Path, width: int, height: int,
              rectangles: list[tuple[int, int, int, int, tuple[int, int, int]]],
              patterns: list[tuple[int, int, int, int]] | None = None) -> None:
    pixels = bytearray([0, 0, 0, 255] * (width * height))

    def put_pixel(x: int, y: int, color: tuple[int, int, int]) -> None:
        offset = (y * width + x) * 4
        red, green, blue = color
        pixels[offset:offset + 4] = bytes((blue, green, red, 255))

    for left, top, rect_width, rect_height in patterns or []:
        for y in range(top, min(height, top + rect_height)):
            for x in range(left, min(width, left + rect_width)):
                value = (x * 19 + y * 31) & 0xFF
                put_pixel(x, y, (40 + value // 2, 25 + value // 3, 15 + value // 4))

    for left, top, rect_width, rect_height, color in rectangles:
        for y in range(top, min(height, top + rect_height)):
            for x in range(left, min(width, left + rect_width)):
                put_pixel(x, y, color)

    header = bytearray(18)
    header[2] = 2
    header[12:14] = width.to_bytes(2, "little")
    header[14:16] = height.to_bytes(2, "little")
    header[16] = 32
    header[17] = 0x28
    path.write_bytes(bytes(header) + bytes(pixels))


class PickUpCandidateTests(unittest.TestCase):
    def test_selects_nearest_safe_container(self) -> None:
        observation = {
            "chosen": {"hex": {"x": 10, "y": 10}},
            "mapItems": [
                safe_container_item(1, hex={"x": 11, "y": 10}, hasDoor=True),
                safe_container_item(2, hex={"x": 12, "y": 10}, lockerLocked=True),
                safe_container_item(3, hex={"x": 20, "y": 20}),
                safe_container_item(4, hex={"x": 13, "y": 10}),
            ],
        }

        self.assertEqual(context_gui.select_pickup_candidate(observation)["id"], 4)

    def test_explicit_candidate_must_be_safe_and_visible(self) -> None:
        observation = {
            "mapItems": [
                safe_container_item("safe"),
                {"id": "ground-item", "canOpen": True, "canPickUp": True},
            ],
        }

        self.assertEqual(context_gui.select_pickup_candidate(observation, "safe")["id"], "safe")
        with self.assertRaisesRegex(ValueError, "not a safe unopened container"):
            context_gui.select_pickup_candidate(observation, "ground-item")
        with self.assertRaisesRegex(ValueError, "is not visible"):
            context_gui.select_pickup_candidate(observation, "missing")

    def test_explicit_candidate_rejects_the_minimal_bridge_item_shape(self) -> None:
        observation = {"mapItems": [{"id": 91, "protoId": "known_fixture", "hexX": 10, "hexY": 12}]}

        with self.assertRaisesRegex(ValueError, "not a safe unopened container"):
            context_gui.select_pickup_candidate(observation, "91")

    def test_rejects_open_locked_gagged_and_no_open_containers(self) -> None:
        variants = (
            {"opened": True},
            {"lockerLocked": True},
            {"lockerJammed": True},
            {"lockerBroken": "false"},
            {"lockerNoOpen": True},
            {"isGag": True},
            {"canOpen": False},
            {"hasContainer": False},
            {"hasLocker": False},
            {"hasDoor": True},
        )
        for variant in variants:
            with self.subTest(variant=variant):
                item = safe_container_item(**variant)
                self.assertFalse(context_gui.pickup_candidate_is_safe(item))

    def test_rejects_missing_capability_metadata(self) -> None:
        required_fields = (
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
        )
        for field in required_fields:
            with self.subTest(field=field):
                item = safe_container_item()
                del item[field]
                self.assertFalse(context_gui.pickup_candidate_is_safe(item))


class RadioCandidateTests(unittest.TestCase):
    def test_prefers_explicit_radio_component_and_accepts_radio_proto(self) -> None:
        observation = {
            "inventory": [
                {"id": 1, "protoId": "radio"},
                {"id": 2, "protoId": "custom_transceiver", "hasRadio": True},
            ],
        }

        self.assertEqual(context_gui.select_radio_candidate(observation)["id"], 2)
        self.assertEqual(
            context_gui.select_radio_candidate({"inventory": [{"id": 3, "protoId": "RADIO"}]})["id"],
            3,
        )

    def test_rejects_nonfunctional_radio_like_items_and_missing_ids(self) -> None:
        observation = {
            "inventory": [
                {"id": 4, "protoId": "vic_radio"},
                {"protoId": "radio"},
                {"id": 5, "hasRadio": False},
            ],
        }

        self.assertIsNone(context_gui.select_radio_candidate(observation))


class DialogBoxPromptTests(unittest.TestCase):
    def test_accepts_active_prompt_with_session_and_safe_second_answer(self) -> None:
        prompt = {
            "active": True,
            "kind": "dialog_box",
            "dialogBoxSession": 123,
            "buttons": [
                {"index": 0, "id": "answer_0", "enabled": True, "dangerous": True},
                {"index": 1, "id": "answer_1", "enabled": True, "dangerous": False},
            ],
        }

        self.assertIs(context_gui.active_dialog_box_prompt({"uiPrompt": prompt}), prompt)
        self.assertTrue(context_gui.dialog_box_has_safe_fixture_answer(prompt))

    def test_rejects_wrong_kind_invalid_session_and_unsafe_answer(self) -> None:
        for prompt in (
            {"active": True, "kind": "elevator", "dialogBoxSession": 1},
            {"active": True, "kind": "dialog_box"},
            {"active": True, "kind": "dialog_box", "dialogBoxSession": 0},
            {"active": True, "kind": "dialog_box", "dialogBoxSession": True},
        ):
            with self.subTest(prompt=prompt):
                self.assertIsNone(context_gui.active_dialog_box_prompt({"uiPrompt": prompt}))

        self.assertFalse(context_gui.dialog_box_has_safe_fixture_answer({
            "buttons": [{"index": 1, "id": "answer_1", "dangerous": True}],
        }))


class ContextArgumentTests(unittest.TestCase):
    def test_builds_parameters_from_live_observation(self) -> None:
        observation = {
            "critters": [{"id": 77, "alive": True}],
            "mapItems": [{"id": 88}],
            "inventory": [
                {"id": 11, "count": 9, "stackable": True},
                {"id": 12, "count": 1, "protoId": "dynamite"},
                {"id": 13, "count": 1, "canUseOnSmth": True},
            ],
        }

        self.assertEqual(context_gui.context_screen_arguments("SkillBox", observation)[0], {"screen": "SkillBox"})
        self.assertEqual(context_gui.context_screen_arguments("Aim", observation)[0], {"screen": "Aim", "targetId": 77})
        self.assertEqual(context_gui.context_screen_arguments("Split", observation)[0], {"screen": "Split", "itemId": 11})
        self.assertEqual(context_gui.context_screen_arguments("Timer", observation)[0], {"screen": "Timer", "itemId": 12})
        self.assertEqual(context_gui.context_screen_arguments("Use", observation)[0], {"screen": "Use", "targetId": 77})

    def test_missing_context_is_reported_without_fabricated_ids(self) -> None:
        for screen, reason in (
            ("Aim", "no_visible_living_target"),
            ("Split", "no_inventory_stack"),
            ("Timer", "no_timer_capable_item"),
            ("Use", "empty_inventory"),
        ):
            with self.subTest(screen=screen):
                arguments, actual_reason = context_gui.context_screen_arguments(screen, {"inventory": []})
                self.assertIsNone(arguments)
                self.assertEqual(actual_reason, reason)

    def test_use_requires_an_inventory_item_usable_on_a_target(self) -> None:
        observation = {
            "inventory": [{"id": 13, "canUse": True, "canUseOnSmth": False}],
            "critters": [{"id": 77, "alive": True}],
        }

        arguments, reason = context_gui.context_screen_arguments("Use", observation)

        self.assertIsNone(arguments)
        self.assertEqual(reason, "no_inventory_item_usable_on_target")


class ContextScreenshotOracleTests(unittest.TestCase):
    def test_skillbox_accepts_title_and_eight_spread_skill_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "skillbox.tga"
            width, height = 1024, 768
            left = (width - context_gui.SKILLBOX_SCREEN_SIZE[0]) // 2
            top = (height - context_gui.SKILLBOX_SCREEN_SIZE[1]) // 2
            rectangles = [(left + 45, top + 12, 90, 8, (164, 131, 20))]
            for index in range(8):
                y = top + 52 + index * 32
                rectangles.extend([
                    (left + 12, y, 82, 7, (164, 131, 20)),
                    (left + 108, y, 35, 7, (180, 180, 180)),
                ])
            write_tga(path, width, height, rectangles, [(left, top, 185, 368)])

            self.assertTrue(context_gui.tga_skillbox_content_is_visible(path))
            self.assertEqual(
                context_gui.contextual_content_check("SkillBox", {"verified": True, "absolutePath": str(path)}),
                (True, "skillbox_skills_visible"),
            )

    def test_skillbox_accepts_right_anchored_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "skillbox-right.tga"
            width, height = 1280, 720
            left = width - context_gui.SKILLBOX_SCREEN_SIZE[0]
            top = 0
            rectangles = [(left + 45, top + 12, 90, 8, (164, 131, 20))]
            for index in range(8):
                rectangles.append((left + 12, top + 52 + index * 32, 132, 7, (164, 131, 20)))
            write_tga(path, width, height, rectangles, [(left, top, 185, 368)])

            self.assertTrue(context_gui.tga_skillbox_content_is_visible(path))

    def test_skillbox_rejects_blank_and_solid_map_like_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            for name, rectangles in (
                ("blank", []),
                ("solid", [(0, 0, 1024, 768, (164, 131, 20))]),
            ):
                with self.subTest(name=name):
                    path = Path(temp_dir) / f"{name}.tga"
                    write_tga(path, 1024, 768, rectangles)
                    self.assertFalse(context_gui.tga_skillbox_content_is_visible(path))

    def test_pickup_accepts_frame_preview_and_container_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pickup.tga"
            width, height = 1024, 768
            left = (width - context_gui.PICKUP_SCREEN_SIZE[0]) // 2
            top = (height - context_gui.PICKUP_SCREEN_SIZE[1]) // 2
            patterns = [
                (left, top, 417, 30),
                (left, top + 346, 417, 30),
                (left, top, 35, 376),
                (left + 382, top, 35, 376),
                (left + 303, top + 35, 70, 100),
                (left + 54, top + 33, 70, 300),
                (left + 175, top + 36, 70, 300),
            ]
            write_tga(path, width, height, [], patterns)

            self.assertTrue(context_gui.tga_pickup_content_is_visible(path, True))
            self.assertEqual(
                context_gui.contextual_content_check("PickUp", {"verified": True, "absolutePath": str(path)}, True),
                (True, "pickup_panels_visible"),
            )

    def test_pickup_rejects_missing_preview_and_uniform_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            left = (1024 - context_gui.PICKUP_SCREEN_SIZE[0]) // 2
            top = (768 - context_gui.PICKUP_SCREEN_SIZE[1]) // 2
            missing_preview = root / "missing-preview.tga"
            write_tga(missing_preview, 1024, 768, [], [
                (left, top, 417, 30),
                (left, top + 346, 417, 30),
                (left, top, 35, 376),
                (left + 382, top, 35, 376),
                (left + 175, top + 36, 70, 300),
            ])
            solid = root / "solid.tga"
            write_tga(solid, 1024, 768, [(0, 0, 1024, 768, (80, 120, 60))])

            self.assertFalse(context_gui.tga_pickup_content_is_visible(missing_preview, True))
            self.assertFalse(context_gui.tga_pickup_content_is_visible(solid, False))

    def test_unverified_and_unsupported_captures_are_rejected(self) -> None:
        self.assertEqual(
            context_gui.contextual_content_check("SkillBox", {"verified": False}),
            (False, "capture_not_verified"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "any.tga"
            write_tga(path, 2, 2, [])
            self.assertEqual(
                context_gui.contextual_content_check("Unknown", {"verified": True, "absolutePath": str(path)}),
                (False, "content_oracle_unsupported"),
            )

    def test_radio_accepts_channel_labels_dial_and_switches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "radio.tga"
            width, height = 1024, 768
            left = (width - context_gui.RADIO_SCREEN_SIZE[0]) // 2
            top = (height - context_gui.RADIO_SCREEN_SIZE[1]) // 2
            patterns = [
                (left, top, *context_gui.RADIO_SCREEN_SIZE),
                (left + 145, top + 5, 140, 125),
                (left + 12, top + 75, 303, 120),
            ]
            rectangles = [
                (left + 20, top + 18, 105, 9, (180, 140, 30)),
                (left + 20, top + 70, 105, 9, (180, 140, 30)),
                (left + 20, top + 150, 105, 9, (180, 140, 30)),
            ]
            write_tga(path, width, height, rectangles, patterns)

            self.assertTrue(context_gui.tga_radio_content_is_visible(path))
            self.assertEqual(
                context_gui.contextual_content_check("Radio", {"verified": True, "absolutePath": str(path)}),
                (True, "radio_controls_visible"),
            )

    def test_elevator_accepts_button_column_and_instrument_panel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "elevator.tga"
            width, height = 1024, 768
            size = context_gui.ELEVATOR_SCREEN_SIZES[0]
            left = (width - size[0]) // 2
            top = (height - size[1]) // 2
            patterns = [
                (left, top, *size),
                (left + 8, top + 35, 56, 241),
                (left + 108, top + 18, 117, 258),
            ]
            write_tga(path, width, height, [], patterns)

            self.assertTrue(context_gui.tga_elevator_content_is_visible(path))
            self.assertEqual(
                context_gui.contextual_content_check("Elevator", {"verified": True, "absolutePath": str(path)}),
                (True, "elevator_controls_visible"),
            )

    def test_dialog_box_accepts_prompt_and_two_answer_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "dialog-box.tga"
            width, height = 1024, 768
            left = (width - context_gui.DIALOGBOX_SCREEN_SIZE[0]) // 2
            top = (height - context_gui.DIALOGBOX_SCREEN_SIZE[1]) // 2
            patterns = [
                (left, top, *context_gui.DIALOGBOX_SCREEN_SIZE),
                (left + 40, top + 99, 250, 50),
            ]
            rectangles = [
                (left + 65, top + 35, 170, 9, (164, 131, 20)),
                (left + 75, top + 107, 150, 7, (164, 131, 20)),
                (left + 75, top + 131, 150, 7, (164, 131, 20)),
            ]
            write_tga(path, width, height, rectangles, patterns)

            self.assertTrue(context_gui.tga_dialog_box_content_is_visible(path))
            self.assertEqual(
                context_gui.contextual_content_check("DialogBox", {"verified": True, "absolutePath": str(path)}),
                (True, "dialog_box_prompt_visible"),
            )

    def test_live_context_oracles_reject_blank_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blank-context.tga"
            write_tga(path, 1024, 768, [])

            self.assertFalse(context_gui.tga_radio_content_is_visible(path))
            self.assertFalse(context_gui.tga_elevator_content_is_visible(path))
            self.assertFalse(context_gui.tga_dialog_box_content_is_visible(path))

    def test_centered_context_screens_accept_required_regions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            for screen, size in context_gui.CONTEXT_SCREEN_SIZES.items():
                with self.subTest(screen=screen):
                    width, height = 1024, 768
                    left = (width - size[0]) // 2
                    top = (height - size[1]) // 2
                    patterns = [
                        (left, top, size[0], 20),
                        (left, top + size[1] - 20, size[0], 20),
                    ]
                    rectangles = []
                    for region, kind, _pixels, minimum_width, minimum_height in context_gui.CONTEXT_SCREEN_REGIONS[screen]:
                        region_left, region_top, region_right, region_bottom = region
                        if kind == "texture":
                            patterns.append((left + region_left, top + region_top,
                                             region_right - region_left, region_bottom - region_top))
                        else:
                            color = (0, 255, 0) if kind == "green" else (164, 131, 20)
                            rectangles.append((left + region_left + 2, top + region_top + 2,
                                               minimum_width + 5, minimum_height + 5, color))
                    path = Path(temp_dir) / f"{screen}.tga"
                    write_tga(path, width, height, rectangles, patterns)

                    self.assertTrue(context_gui.tga_centered_context_screen_is_visible(path, screen))
                    self.assertEqual(
                        context_gui.contextual_content_check(
                            screen, {"verified": True, "absolutePath": str(path)}
                        ),
                        (True, f"{screen.lower()}_context_visible"),
                    )

    def test_centered_context_screens_reject_blank_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blank.tga"
            write_tga(path, 1024, 768, [])
            for screen in context_gui.CONTEXT_SCREEN_SIZES:
                with self.subTest(screen=screen):
                    self.assertFalse(context_gui.tga_centered_context_screen_is_visible(path, screen))


class LiveContextFlowTests(unittest.TestCase):
    def test_radio_opens_through_normal_self_use_then_captures_and_hides(self) -> None:
        observation = {
            "hasChosen": True,
            "hasMap": False,
            "screen": {"screens": []},
            "inventory": [{"id": 55, "protoId": "radio", "hasRadio": True, "canUse": True}],
        }
        with (
            patch.object(context_gui, "call_tool", side_effect=[observation, successful_command("queued")]) as call_tool,
            patch.object(context_gui, "wait_for_observation", return_value={"screen": {"screens": ["Radio"]}}),
            patch.object(context_gui, "capture_screen", return_value={"verified": True}),
            patch.object(context_gui, "hide_screen", return_value={"ok": True, "message": "hidden"}) as hide_screen,
        ):
            entry = context_gui.run_radio(object(), "screens", 0, 1000)

        self.assertEqual(entry["status"], "passed")
        self.assertTrue(entry["verified"])
        self.assertEqual(call_tool.call_args_list[1].args[1], "tla_use_item")
        use_arguments = call_tool.call_args_list[1].args[2]
        self.assertEqual(use_arguments["itemId"], 55)
        self.assertNotIn("targetId", use_arguments)
        self.assertNotIn("auxId", use_arguments)
        hide_screen.assert_called_once_with(ANY, "Radio", 1000)

    def test_radio_without_owned_radio_is_a_safe_skip(self) -> None:
        observation = {
            "hasChosen": True,
            "hasMap": True,
            "screen": {"screens": []},
            "inventory": [{"id": 56, "protoId": "vic_radio"}],
        }
        with patch.object(context_gui, "call_tool", return_value=observation) as call_tool:
            entry = context_gui.run_radio(object(), "screens", 0, 1000)

        self.assertEqual(entry["status"], "skipped")
        self.assertEqual(entry["reason"], "no_owned_radio")
        self.assertEqual(call_tool.call_count, 1)

    def test_elevator_without_open_screen_or_trigger_is_a_safe_skip(self) -> None:
        observation = {"hasChosen": True, "hasMap": True, "screen": {"screens": []}}
        with patch.object(context_gui, "call_tool", return_value=observation) as call_tool:
            entry = context_gui.run_elevator(object(), "screens", 0, 1000, None)

        self.assertEqual(entry["status"], "skipped")
        self.assertEqual(entry["reason"], "elevator_trigger_hex_required")
        self.assertEqual(call_tool.call_count, 1)

    def test_elevator_moves_to_explicit_trigger_then_captures_without_answering(self) -> None:
        observation = {"hasChosen": True, "hasMap": True, "screen": {"screens": []}}
        with (
            patch.object(context_gui, "call_tool", side_effect=[observation, successful_command("queued")]) as call_tool,
            patch.object(context_gui, "wait_for_observation", return_value={"screen": {"screens": ["Elevator"]}}),
            patch.object(context_gui, "capture_screen", return_value={"verified": True}),
            patch.object(context_gui, "hide_screen", return_value={"ok": True, "message": "hidden"}) as hide_screen,
        ):
            entry = context_gui.run_elevator(object(), "screens", 0, 1000, (44, 73))

        self.assertEqual(entry["status"], "passed")
        self.assertTrue(entry["verified"])
        self.assertEqual(entry["source"], "trigger_hex")
        self.assertEqual(call_tool.call_args_list[1].args[1], "tla_move_to_hex")
        movement_arguments = call_tool.call_args_list[1].args[2]
        self.assertEqual((movement_arguments["x"], movement_arguments["y"]), (44, 73))
        self.assertNotIn("answerIndex", movement_arguments)
        self.assertNotIn("answerId", movement_arguments)
        self.assertNotIn("tla_ui_answer", [entry.args[1] for entry in call_tool.call_args_list])
        hide_screen.assert_called_once_with(ANY, "Elevator", 1000)

    def test_already_open_elevator_is_captured_without_movement(self) -> None:
        observation = {"screen": {"screens": ["GuiScreen::Elevator"]}}
        with (
            patch.object(context_gui, "call_tool", return_value=observation) as call_tool,
            patch.object(context_gui, "wait_for_observation", return_value=observation),
            patch.object(context_gui, "capture_screen", return_value={"verified": True}),
            patch.object(context_gui, "hide_screen", return_value={"ok": True, "message": "hidden"}),
        ):
            entry = context_gui.run_elevator(object(), "screens", 0, 1000, None)

        self.assertEqual(entry["status"], "passed")
        self.assertEqual(entry["source"], "already_active")
        self.assertEqual(call_tool.call_count, 1)

    def test_dialog_box_uses_fixture_snapshot_session_and_safe_answer(self) -> None:
        observation = {"hasChosen": True, "screen": {"screens": []}}
        prompt_observation = {
            "screen": {"screens": ["DialogBox"]},
            "uiPrompt": {
                "active": True,
                "kind": "dialog_box",
                "dialogBoxSession": 321,
                "buttons": [
                    {"index": 0, "id": "answer_0", "enabled": True, "dangerous": True},
                    {"index": 1, "id": "answer_1", "enabled": True, "dangerous": False},
                ],
            },
        }
        closed_observation = {"screen": {"screens": []}, "uiPrompt": {"active": False}}
        with (
            patch.object(
                context_gui,
                "call_tool",
                side_effect=[observation, successful_command("qa_dialog_box_requested"), successful_command("ui_answered")],
            ) as call_tool,
            patch.object(
                context_gui,
                "wait_for_observation",
                side_effect=[prompt_observation, closed_observation],
            ) as wait_for_observation,
            patch.object(context_gui, "capture_screen", return_value={"verified": True}),
            patch.object(context_gui, "hide_screen", return_value={"ok": True}) as hide_screen,
        ):
            entry = context_gui.run_dialog_box(object(), "screens", 0, 1000)

        self.assertEqual(entry["status"], "passed")
        self.assertTrue(entry["verified"])
        self.assertEqual(
            [tool_call.args[1] for tool_call in call_tool.call_args_list],
            ["tla_observe", "tla_qa_show_dialog_box", "tla_ui_answer"],
        )
        answer_arguments = call_tool.call_args_list[2].args[2]
        self.assertEqual(answer_arguments["answerIndex"], 1)
        self.assertEqual(answer_arguments["answerId"], "answer_1")
        self.assertEqual(answer_arguments["expectedSession"], 321)
        open_predicate = wait_for_observation.call_args_list[0].args[1]
        close_predicate = wait_for_observation.call_args_list[1].args[1]
        self.assertTrue(open_predicate(prompt_observation))
        self.assertFalse(open_predicate({"screen": {"screens": ["DialogBox"]}, "uiPrompt": {"active": False}}))
        self.assertTrue(close_predicate(closed_observation))
        self.assertFalse(close_predicate(prompt_observation))
        hide_screen.assert_not_called()

    def test_dialog_box_disabled_qa_is_a_clear_skip(self) -> None:
        observation = {"hasChosen": True, "screen": {"screens": []}}
        with (
            patch.object(
                context_gui,
                "call_tool",
                side_effect=[observation, failed_command("qa_commands_disabled")],
            ) as call_tool,
            patch.object(context_gui, "wait_for_observation") as wait_for_observation,
            patch.object(context_gui, "hide_screen") as hide_screen,
        ):
            entry = context_gui.run_dialog_box(object(), "screens", 0, 1000)

        self.assertEqual(entry["status"], "skipped")
        self.assertEqual(entry["reason"], "qa_commands_disabled")
        self.assertEqual(call_tool.call_count, 2)
        wait_for_observation.assert_not_called()
        hide_screen.assert_not_called()


class ReportSemanticsTests(unittest.TestCase):
    def test_live_contexts_are_supported_default_screens(self) -> None:
        self.assertEqual(len(context_gui.DEFAULT_SCREENS), 9)
        self.assertIn("Radio", context_gui.DEFAULT_SCREENS)
        self.assertIn("Elevator", context_gui.DEFAULT_SCREENS)
        self.assertIn("DialogBox", context_gui.DEFAULT_SCREENS)
        self.assertIn("Radio", context_gui.SUPPORTED_SCREENS)
        self.assertIn("Elevator", context_gui.SUPPORTED_SCREENS)
        self.assertIn("DialogBox", context_gui.SUPPORTED_SCREENS)
        self.assertIn("Radio", context_gui.CONTEXT_REQUIREMENTS)
        self.assertIn("Elevator", context_gui.CONTEXT_REQUIREMENTS)
        self.assertIn("DialogBox", context_gui.CONTEXT_REQUIREMENTS)

    def test_modal_name_falls_back_to_raw_bridge_active_screen(self) -> None:
        self.assertEqual(
            context_gui.active_modal_name({"screen": {"modalActive": True, "active": "GuiScreen::DialogBox"}}),
            "GuiScreen::DialogBox",
        )
        self.assertEqual(
            context_gui.active_modal_name({"screen": {"modalActive": False, "active": "GuiScreen::Game"}}),
            "",
        )

    def test_real_context_flows_dispatch_and_require_all_controls_skips(self) -> None:
        with (
            patch.object(
                context_gui,
                "run_radio",
                return_value={"screen": "Radio", "status": "skipped", "verified": False},
            ) as run_radio,
            patch.object(
                context_gui,
                "run_elevator",
                return_value={"screen": "Elevator", "status": "passed", "verified": True},
            ) as run_elevator,
            patch.object(
                context_gui,
                "run_dialog_box",
                return_value={"screen": "DialogBox", "status": "passed", "verified": True},
            ) as run_dialog_box,
        ):
            without_requirement = context_gui.run_playtest(
                client=object(),
                screens=["Radio", "Elevator", "DialogBox"],
                output_relative="screens",
                settle_ms=0,
                timeout_ms=1000,
                pickup_item_id="",
                require_all=False,
                elevator_trigger_hex=(44, 73),
            )
            with_requirement = context_gui.run_playtest(
                client=object(),
                screens=["Radio", "Elevator", "DialogBox"],
                output_relative="screens",
                settle_ms=0,
                timeout_ms=1000,
                pickup_item_id="",
                require_all=True,
                elevator_trigger_hex=(44, 73),
            )

        self.assertTrue(without_requirement["verified"])
        self.assertFalse(with_requirement["verified"])
        self.assertEqual(run_radio.call_count, 2)
        self.assertEqual(run_elevator.call_count, 2)
        self.assertEqual(run_dialog_box.call_count, 2)
        self.assertEqual(run_elevator.call_args.args[-1], (44, 73))


if __name__ == "__main__":
    unittest.main()
