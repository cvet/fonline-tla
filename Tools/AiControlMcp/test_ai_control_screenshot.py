#!/usr/bin/env python3
"""Focused pure-Python checks for verified screenshots and new typed bridge commands."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ai_control_mcp as mcp  # noqa: E402 - add the sibling tool directory for unittest module discovery.
import tla_barter_playtest as barter_playtest  # noqa: E402
import tla_gui_screenshot_test as gui_screenshots  # noqa: E402
import tla_mechanics_playtest as mechanics  # noqa: E402
import tla_quest_runner as quests  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]


def raw_tga(width: int, height: int, pixels: bytes, pixel_depth: int = 32, image_type: int = 2) -> bytes:
    header = bytearray(18)
    header[2] = image_type
    header[12] = width & 0xFF
    header[13] = (width >> 8) & 0xFF
    header[14] = height & 0xFF
    header[15] = (height >> 8) & 0xFF
    header[16] = pixel_depth
    header[17] = 0x20 | (8 if pixel_depth == 32 else 0)
    return bytes(header) + pixels


def write_test_tga(path: Path,
                   width: int,
                   height: int,
                   rectangles: list[tuple[int, int, int, int, tuple[int, int, int]]]) -> None:
    pixels = bytearray([0, 0, 0, 255]) * (width * height)
    for x, y, rect_width, rect_height, (red, green, blue) in rectangles:
        row = bytes([blue, green, red, 255]) * rect_width
        for row_y in range(y, y + rect_height):
            offset = (row_y * width + x) * 4
            pixels[offset:offset + len(row)] = row
    with path.open("wb") as stream:
        stream.write(raw_tga(width, height, b""))
        stream.write(pixels)


def write_patterned_test_tga(
    path: Path,
    width: int,
    height: int,
    patterned_rectangles: list[tuple[int, int, int, int]],
    solid_rectangles: list[tuple[int, int, int, int, tuple[int, int, int]]] | None = None,
) -> None:
    pixels = bytearray([0, 0, 0, 255]) * (width * height)
    for x, y, rect_width, rect_height in patterned_rectangles:
        for offset_y in range(rect_height):
            for offset_x in range(rect_width):
                red = ((offset_x * 3 + offset_y) % 16) * 16
                green = ((offset_x + offset_y * 5) % 16) * 16
                blue = ((offset_x * 7 + offset_y * 3) % 16) * 16
                pixel_offset = ((y + offset_y) * width + x + offset_x) * 4
                pixels[pixel_offset:pixel_offset + 4] = bytes([blue, green, red, 255])
    for x, y, rect_width, rect_height, (red, green, blue) in solid_rectangles or []:
        row = bytes([blue, green, red, 255]) * rect_width
        for row_y in range(y, y + rect_height):
            offset = (row_y * width + x) * 4
            pixels[offset:offset + len(row)] = row
    with path.open("wb") as stream:
        stream.write(raw_tga(width, height, b""))
        stream.write(pixels)


class ScreenshotPathTests(unittest.TestCase):
    def test_default_and_relative_paths_stay_in_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            default_path = mcp.resolve_engine_screenshot_path(root, None)
            custom_path = mcp.resolve_engine_screenshot_path(root, "Workspace/AiControlScreenshots/custom.tga")

            self.assertTrue(default_path.is_relative_to(root.resolve()))
            self.assertEqual(default_path.suffix, ".tga")
            self.assertEqual(custom_path, (root / "Workspace/AiControlScreenshots/custom.tga").resolve())

    def test_rejects_wrong_extension_and_workspace_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(ValueError, "end with .tga"):
                mcp.resolve_engine_screenshot_path(root, "frame.png")
            with self.assertRaisesRegex(ValueError, "inside the workspace"):
                mcp.resolve_engine_screenshot_path(root, "../frame.tga")
            with self.assertRaisesRegex(ValueError, "must be a string"):
                mcp.resolve_engine_screenshot_path(root, 123)


class TgaInspectionTests(unittest.TestCase):
    def test_reads_true_color_header_payload_hash_and_color_stats(self) -> None:
        data = raw_tga(
            2,
            2,
            bytes(
                [
                    0, 0, 0, 255,
                    0, 0, 255, 255,
                    0, 255, 0, 255,
                    255, 0, 0, 255,
                ]
            ),
        )

        result = mcp.inspect_uncompressed_true_color_tga(data)

        self.assertEqual(result["width"], 2)
        self.assertEqual(result["height"], 2)
        self.assertEqual(result["pixelDepth"], 32)
        self.assertEqual(result["payloadBytes"], 16)
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["colorStats"]["sampledPixels"], 4)
        self.assertFalse(result["blankLike"])

    def test_marks_single_color_frame_blank_like(self) -> None:
        data = raw_tga(2, 2, bytes([10, 20, 30, 255] * 4))
        self.assertTrue(mcp.inspect_uncompressed_true_color_tga(data)["blankLike"])

    def test_sparse_text_on_black_background_is_not_blank_like(self) -> None:
        pixels = bytearray([0, 0, 0, 255] * (64 * 64))
        for pixel_index in (65, 66, 67, 129, 131, 193, 194, 195):
            offset = pixel_index * 4
            pixels[offset : offset + 4] = bytes([255, 255, 255, 255])
        self.assertFalse(mcp.inspect_uncompressed_true_color_tga(raw_tga(64, 64, bytes(pixels)))["blankLike"])

    def test_rejects_compressed_or_truncated_payload(self) -> None:
        with self.assertRaisesRegex(ValueError, "uncompressed true-color"):
            mcp.inspect_uncompressed_true_color_tga(raw_tga(1, 1, bytes([0, 0, 0, 255]), image_type=10))
        with self.assertRaisesRegex(ValueError, "payload is truncated"):
            mcp.inspect_uncompressed_true_color_tga(raw_tga(2, 2, bytes([0, 0, 0, 255])))


class GuiScreenshotContentTests(unittest.TestCase):
    def test_credits_rejects_version_overlay_without_credit_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "version-only.tga"
            write_test_tga(path, 1024, 768, [(48, 8, 240, 12, (255, 255, 255))])
            ok, message = gui_screenshots.capture_content_check(
                "Credits",
                {"verified": True, "absolutePath": str(path),
                 "colorStats": {"blackRatio": 0.999302, "uniqueColorBuckets": 4}},
            )

            self.assertFalse(ok)
            self.assertEqual(message, "credits_text_not_visible")

    def test_credits_rejects_blank_tga(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blank.tga"
            write_test_tga(path, 1024, 768, [])
            ok, message = gui_screenshots.capture_content_check(
                "Credits",
                {"verified": True, "path": str(path)},
            )

            self.assertFalse(ok)
            self.assertEqual(message, "credits_text_not_visible")

    def test_credits_accepts_visible_text_at_1024x768(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "credits-1024x768.tga"
            write_test_tga(path, 1024, 768, [(392, 724, 240, 18, (64, 255, 32))])
            ok, message = gui_screenshots.capture_content_check(
                "Credits",
                {"verified": True, "absolutePath": str(path)},
            )

            self.assertTrue(ok)
            self.assertEqual(message, "credits_text_visible")

    def test_credits_accepts_same_pixel_size_text_at_3840x2160(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "credits-3840x2160.tga"
            write_test_tga(path, 3840, 2160, [(1800, 2116, 240, 18, (64, 255, 32))])
            ok, message = gui_screenshots.capture_content_check(
                "GuiScreen::Credits",
                {"verified": True, "absolutePath": str(path)},
            )

            self.assertTrue(ok)
            self.assertEqual(message, "credits_text_visible")

    def test_fixboy_rejects_empty_recipe_panel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixboy-empty.tga"
            write_test_tga(path, 1024, 768, [(20, 20, 100, 20, (255, 0, 0))])
            ok, message = gui_screenshots.capture_content_check(
                "FixBoy",
                {"verified": True, "absolutePath": str(path)},
            )

            self.assertFalse(ok)
            self.assertEqual(message, "fixboy_recipe_list_not_visible")

    def test_fixboy_accepts_visible_recipe_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixboy-recipes.tga"
            write_test_tga(path, 1024, 768, [(290, 225, 120, 12, (220, 20, 10))])
            ok, message = gui_screenshots.capture_content_check(
                "GuiScreen::FixBoy",
                {"verified": True, "absolutePath": str(path)},
            )

            self.assertTrue(ok)
            self.assertEqual(message, "fixboy_recipe_list_visible")

    def test_centered_screens_accept_content_in_their_required_regions(self) -> None:
        green = (80, 255, 0)
        gold = (164, 131, 20)
        cases = {
            "Options": ((640, 480), [
                (50, 40, 80, 50, green),
                (250, 50, 120, 50, green),
                (490, 440, 50, 10, green),
            ], "options_controls_visible"),
            "Inventory": ((499, 377), [(300, 60, 80, 70, green)], "inventory_stats_visible"),
            "Character": ((640, 480), [
                (40, 50, 70, 60, green),
                (200, 50, 70, 50, green),
                (380, 40, 120, 70, green),
            ], "character_stats_visible"),
            "PipBoy": ((640, 480), [(350, 120, 140, 90, green)], "pipboy_content_visible"),
            "Menu": ((164, 144), [
                (40, 25, 45, 10, gold),
                (40, 61, 45, 10, gold),
                (30, 97, 60, 10, gold),
            ], "menu_buttons_visible"),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            for screen, (screen_size, relative_rectangles, success_message) in cases.items():
                with self.subTest(screen=screen):
                    path = Path(temp_dir) / f"{screen}.tga"
                    screen_left = (1024 - screen_size[0]) // 2
                    screen_top = (768 - screen_size[1]) // 2
                    rectangles = [
                        (screen_left + x, screen_top + y, width, height, color)
                        for x, y, width, height, color in relative_rectangles
                    ]
                    write_test_tga(path, 1024, 768, rectangles)

                    ok, message = gui_screenshots.capture_content_check(
                        f"GuiScreen::{screen}",
                        {"verified": True, "absolutePath": str(path)},
                    )

                    self.assertTrue(ok)
                    self.assertEqual(message, success_message)

    def test_centered_screens_reject_empty_or_solid_map_like_frames(self) -> None:
        failure_messages = {
            "Options": "options_controls_not_visible",
            "Inventory": "inventory_stats_not_visible",
            "Character": "character_stats_not_visible",
            "PipBoy": "pipboy_content_not_visible",
            "Menu": "menu_buttons_not_visible",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            for screen, failure_message in failure_messages.items():
                for variant, rectangles in (
                    ("empty", []),
                    ("map", [(0, 0, 1024, 768, (164, 131, 20) if screen == "Menu" else (80, 255, 0))]),
                ):
                    with self.subTest(screen=screen, variant=variant):
                        path = Path(temp_dir) / f"{screen}-{variant}.tga"
                        write_test_tga(path, 1024, 768, rectangles)

                        ok, message = gui_screenshots.capture_content_check(
                            screen,
                            {"verified": True, "absolutePath": str(path)},
                        )

                        self.assertFalse(ok)
                        self.assertEqual(message, failure_message)

    def test_barter_panels_accept_rendered_items_and_totals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "barter.tga"
            screen_left = (1024 - gui_screenshots.BARTER_SCREEN_SIZE[0]) // 2
            screen_top = (768 - gui_screenshots.BARTER_SCREEN_SIZE[1]) // 2
            patterned_rectangles = [
                (screen_left + left, screen_top + top, right - left, bottom - top)
                for left, top, right, bottom in gui_screenshots.BARTER_ITEM_RECTS
            ]
            solid_rectangles = [
                (screen_left + left + 9, screen_top + top + 2, 20, 7, (180, 180, 180))
                for left, top, _right, _bottom in gui_screenshots.BARTER_COST_RECTS
            ]
            write_patterned_test_tga(path, 1024, 768, patterned_rectangles, solid_rectangles)

            self.assertTrue(gui_screenshots.tga_barter_panels_are_visible(path))

    def test_barter_panels_reject_empty_items_or_map_like_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            empty_path = root / "barter-empty.tga"
            screen_left = (1024 - gui_screenshots.BARTER_SCREEN_SIZE[0]) // 2
            screen_top = (768 - gui_screenshots.BARTER_SCREEN_SIZE[1]) // 2
            costs = [
                (screen_left + left + 9, screen_top + top + 2, 20, 7, (180, 180, 180))
                for left, top, _right, _bottom in gui_screenshots.BARTER_COST_RECTS
            ]
            write_patterned_test_tga(empty_path, 1024, 768, [], costs)

            map_path = root / "barter-map.tga"
            write_patterned_test_tga(map_path, 1024, 768, [(0, 0, 1024, 768)], costs)

            self.assertFalse(gui_screenshots.tga_barter_panels_are_visible(empty_path))
            self.assertFalse(gui_screenshots.tga_barter_panels_are_visible(map_path))

    def test_barter_runner_rejects_a_verified_but_visually_empty_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)
            output = workspace_root / "screens"
            output.mkdir()
            write_test_tga(output / "barter.tga", 1024, 768, [])
            with mock.patch.object(barter_playtest, "call_tool", return_value={"verified": True}):
                with self.assertRaisesRegex(barter_playtest.SmokeError, "does not show all barter item panels"):
                    barter_playtest.capture_screenshot(
                        mock.sentinel.client,
                        {},
                        workspace_root,
                        output,
                        "barter.tga",
                        0,
                        1000,
                        require_barter_panels=True,
                    )

    def test_fixboy_capture_uses_minimum_settle_time(self) -> None:
        self.assertEqual(gui_screenshots.capture_settle_ms("FixBoy", 250), 1500)
        self.assertEqual(gui_screenshots.capture_settle_ms("GuiScreen::FixBoy", 2500), 2500)
        self.assertEqual(gui_screenshots.capture_settle_ms("Inventory", 250), 250)

    def test_unknown_screens_require_explicit_generic_opt_in(self) -> None:
        self.assertEqual(
            gui_screenshots.capture_content_check("CustomScreen", {"verified": True}),
            (False, "content_oracle_unsupported"),
        )
        self.assertEqual(
            gui_screenshots.capture_content_check("CustomScreen", {"verified": True}, allow_generic=True),
            (True, "generic_capture_verified"),
        )


class VerifiedCaptureTests(unittest.TestCase):
    def test_removes_stale_file_forces_completion_wait_and_verifies_new_tga(self) -> None:
        class FakeBridge:
            def __init__(self, workspace_root: Path) -> None:
                self.workspace_root = workspace_root
                self.host = "127.0.0.1"
                self.port = 43011
                self.token = ""
                self.events_cursor = 0
                self.calls: list[tuple[str, dict[str, object]]] = []

            def request(self, method: str, params: dict[str, object] | None = None) -> dict[str, object]:
                arguments = params or {}
                self.calls.append((method, arguments))
                if method == "act":
                    target = Path(str(arguments["stringArg"]))
                    self.assert_target_was_removed(target)
                    target.write_bytes(
                        raw_tga(
                            2,
                            2,
                            bytes([0, 0, 0, 255, 0, 0, 255, 255, 0, 255, 0, 255, 255, 0, 0, 255]),
                        )
                    )
                    return {"jsonrpc": "2.0", "id": 1, "result": {"accepted": True, "commandSeq": 7}}
                if method == "events":
                    event = {"type": "command_completed", "commandSeq": 7, "success": True, "message": "saved"}
                    return {"jsonrpc": "2.0", "id": 2, "result": {"events": [{"seq": 1, "event": event}], "latestSeq": 1}}
                raise AssertionError(f"Unexpected fake bridge method: {method}")

            @staticmethod
            def assert_target_was_removed(target: Path) -> None:
                if target.exists():
                    raise AssertionError("stale screenshot target was not removed before act")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "Workspace" / "AiControlScreenshots" / "capture.tga"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"stale")
            bridge = FakeBridge(root)

            response = mcp.save_verified_engine_screenshot(
                bridge,
                {"path": "Workspace/AiControlScreenshots/capture.tga", "settleMs": 0, "waitForCompletion": False},
            )
            result = response["result"]

            self.assertTrue(result["verified"])
            self.assertTrue(result["removedPrevious"])
            self.assertEqual(result["relativePath"], "Workspace/AiControlScreenshots/capture.tga")
            self.assertEqual([method for method, _ in bridge.calls], ["act", "events"])


class TypedCommandTests(unittest.TestCase):
    def test_new_typed_commands_have_catalog_entries_and_payloads(self) -> None:
        catalog_types = {entry["type"] for entry in mcp.COMMAND_CATALOG}
        self.assertTrue({"use_skill", "craft", "barter_transfer", "barter_offer", "barter_return_dialog", "close_dialog"} <= catalog_types)

        self.assertEqual(
            mcp.typed_command_payload("tla_use_skill", {"skill": "SkillRepair", "itemId": 17}),
            {"type": "use_skill", "stringArg": "SkillRepair", "itemId": 17},
        )
        self.assertEqual(
            mcp.typed_command_payload(
                "tla_use_skill",
                {"skill": "SkillScience", "sceneryProtoId": "computer_terminal", "x": 12, "y": 34},
            ),
            {
                "type": "use_skill",
                "stringArg": "SkillScience",
                "sceneryProtoId": "computer_terminal",
                "x": 12,
                "y": 34,
            },
        )
        self.assertEqual(mcp.typed_command_payload("tla_craft", {"craftId": 3}), {"type": "craft", "intArg": 3})
        self.assertEqual(
            mcp.typed_command_payload(
                "tla_barter_transfer",
                {"itemId": 42, "source": "trader_inventory", "count": 2},
            ),
            {"type": "barter_transfer", "itemId": 42, "stringArg": "trader_inventory", "intArg": 2},
        )
        self.assertEqual(mcp.typed_command_payload("tla_barter_offer", {}), {"type": "barter_offer"})
        self.assertEqual(mcp.typed_command_payload("tla_barter_return_dialog", {}), {"type": "barter_return_dialog"})
        self.assertEqual(mcp.typed_command_payload("tla_close_dialog", {}), {"type": "close_dialog"})

    def test_new_typed_command_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "provided together"):
            mcp.typed_command_payload("tla_use_skill", {"skill": "SkillRepair", "x": 1})
        with self.assertRaisesRegex(ValueError, "require sceneryProtoId"):
            mcp.typed_command_payload("tla_use_skill", {"skill": "SkillRepair", "x": 1, "y": 2})
        with self.assertRaisesRegex(ValueError, "requires x and y"):
            mcp.typed_command_payload(
                "tla_use_skill",
                {"skill": "SkillScience", "sceneryProtoId": "computer_terminal"},
            )
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            mcp.typed_command_payload("tla_use_skill", {"skill": "SkillRepair", "targetId": 1, "itemId": 2})
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            mcp.validate_action_command({"type": "use_skill", "stringArg": "SkillScience", "targetId": 1, "sceneryProtoId": "terminal", "x": 2, "y": 3})
        with self.assertRaisesRegex(ValueError, "at least 1"):
            mcp.typed_command_payload("tla_craft", {"craftId": 0})
        with self.assertRaisesRegex(ValueError, "source must be one of"):
            mcp.typed_command_payload(
                "tla_barter_transfer",
                {"itemId": 42, "source": "inventory", "count": 1},
            )

    def test_event_catalog_uses_bridge_screen_event_name(self) -> None:
        event_types = {entry["type"] for entry in mcp.EVENT_CATALOG}
        self.assertIn("screen_change", event_types)
        self.assertNotIn("screen_changed", event_types)

    def test_screenshot_tool_is_optional_path_and_forced_wait(self) -> None:
        tools = {tool["name"]: tool for tool in mcp.tool_list()}
        screenshot_schema = tools["tla_save_screenshot"]["inputSchema"]
        self.assertNotIn("path", screenshot_schema.get("required", []))
        self.assertNotIn("waitForCompletion", screenshot_schema["properties"])
        self.assertIn("settleMs", screenshot_schema["properties"])
        show_description = tools["tla_show_screen"]["description"]
        self.assertIn("Options", show_description)
        self.assertNotIn("GameOptions", show_description)

        use_skill_schema = tools["tla_use_skill"]["inputSchema"]
        self.assertIn("sceneryProtoId", use_skill_schema["properties"])
        self.assertIn("tla_barter_return_dialog", tools)
        typed_tools = {entry["name"]: entry["commandType"] for entry in mcp.schema_payload("commands")["typedTools"]}
        self.assertEqual(typed_tools["tla_barter_return_dialog"], "barter_return_dialog")

    def test_barter_return_dialog_uses_current_transfer_session(self) -> None:
        source = (REPO_ROOT / "Scripts" / "AiControl.fos").read_text(encoding="utf-8")
        command_start = source.index('if (type == "barter_return_dialog")')
        command_body = source[command_start : command_start + 650]

        self.assertIn("!HasCurPlayer || !HasChosen", command_body)
        self.assertIn("Chosen.TransferType != TransferTypes::CritBarter", command_body)
        self.assertIn("ResumeDialogFromBarter(Chosen.TransferContainerId, Chosen.TransferSession)", command_body)
        available_start = source.index("string AvailableActionsJson()")
        self.assertIn('"barter_return_dialog"', source[available_start : available_start + 2200])


class BridgeContractSourceTests(unittest.TestCase):
    def test_receive_items_event_serializes_declared_context(self) -> None:
        source = (REPO_ROOT / "Scripts" / "AiControl.fos").read_text(encoding="utf-8")
        event_start = source.index('StringMember("type", "receive_items")')
        event_body = source[event_start : event_start + 300]
        self.assertIn('IntMember("context", int(contextParam))', event_body)

    def test_scenery_proto_has_end_to_end_native_transport(self) -> None:
        script_source = (REPO_ROOT / "Scripts" / "AiControl.fos").read_text(encoding="utf-8")
        native_source = (REPO_ROOT / "SourceExt" / "ClientAiBridge.cpp").read_text(encoding="utf-8")

        self.assertIn('command.SceneryProtoId = GetJsonString(params, "sceneryProtoId")', native_source)
        self.assertIn("sceneryProtoId = command.SceneryProtoId", native_source)
        self.assertIn("CurPlayer.ServerCall.UseSkill(skill, skillTargetCr, itemId, sceneryPid", script_source)

    def test_barter_observation_serializes_int64_pricing_metadata(self) -> None:
        source = (REPO_ROOT / "Scripts" / "AiControl.fos").read_text(encoding="utf-8")
        barter_start = source.index("string BarterJson()")
        barter_body = source[barter_start : barter_start + 1800]

        self.assertIn('IntMember("coefficient", ClientItems::BarterCoefficient)', barter_body)
        self.assertIn('BoolMember("masterTrader", ClientItems::BarterHasMasterTrader)', barter_body)
        self.assertIn('Int64Member("playerOfferTotal"', barter_body)
        self.assertIn('Int64Member("traderOfferTotal"', barter_body)
        self.assertIn("string Int64Member(string name, int64 value)", source)

        barter_fields = set(mcp.schema_payload("observation")["sharedShapes"]["barter"])
        self.assertTrue({"coefficient", "masterTrader", "playerOfferTotal", "traderOfferTotal"} <= barter_fields)


class RunnerModalContractTests(unittest.TestCase):
    class FakeBridge:
        def __init__(self, observation: dict) -> None:
            self.observation = observation
            self.commands: list[tuple[str, dict]] = []

        def observe_safe(self) -> dict:
            return self.observation

        def act(self, command_type: str, **params) -> dict:
            self.commands.append((command_type, params))
            return {}

    def test_mechanics_routes_dialog_and_nondialog_modal_semantically(self) -> None:
        with mock.patch.object(mechanics.time, "sleep"):
            dialog_bridge = self.FakeBridge({"dialog": {"active": True}, "screen": {"modalActive": True}})
            self.assertTrue(mechanics.close_modal(dialog_bridge))
            modal_bridge = self.FakeBridge({"dialog": {"active": False}, "screen": {"modalActive": True}})
            self.assertTrue(mechanics.close_modal(modal_bridge))

        self.assertEqual([command for command, _ in dialog_bridge.commands], ["close_dialog", "clear_actions"])
        self.assertEqual([command for command, _ in modal_bridge.commands], ["close_screen", "clear_actions"])

    def test_quest_runner_routes_dialog_and_nondialog_modal_semantically(self) -> None:
        with mock.patch.object(quests.time, "sleep"):
            dialog_bridge = self.FakeBridge({"dialog": {"active": True}, "screen": {"modalActive": True}})
            quests.close_dialog(dialog_bridge)
            modal_bridge = self.FakeBridge({"dialog": {"active": False}, "screen": {"modalActive": True}})
            quests.close_dialog(modal_bridge)

        self.assertEqual([command for command, _ in dialog_bridge.commands], ["close_dialog", "clear_actions"])
        self.assertEqual([command for command, _ in modal_bridge.commands], ["close_screen", "clear_actions"])


if __name__ == "__main__":
    unittest.main()
