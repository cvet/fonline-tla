#!/usr/bin/env python3
"""Static drift checks between the script bridge and its MCP-facing semantic contract."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "Scripts" / "AiControl.fos"
SMOKE_PATH = PROJECT_ROOT / "Tools" / "AiControlMcp" / "smoke_ai_control_mcp.py"
sys.path.insert(0, str(PROJECT_ROOT / "Tools" / "AiControlMcp"))

import ai_control_mcp  # noqa: E402


def script_source() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8-sig")


def available_action_types(source: str) -> set[str]:
    start = source.index("string AvailableActionsJson()")
    end = source.index("// --- Параметры", start)
    declaration = source[start:end].split("string[] entries", 1)[0]
    return set(re.findall(r'"([a-z][a-z0-9_]*)"', declaration))


def handled_action_types(source: str) -> set[str]:
    return set(re.findall(r'type\s*==\s*"([a-z][a-z0-9_]*)"', source))


def tool_schema(name: str) -> dict:
    return next(tool["inputSchema"] for tool in ai_control_mcp.tool_list() if tool["name"] == name)


class AiControlScriptContractTests(unittest.TestCase):
    def test_every_advertised_script_action_has_a_handler(self) -> None:
        source = script_source()
        missing = sorted(available_action_types(source) - handled_action_types(source))
        self.assertEqual(missing, [], f"AiControl advertises unsupported commands: {missing}")

    def test_every_handled_script_action_is_advertised(self) -> None:
        source = script_source()
        missing = sorted(handled_action_types(source) - available_action_types(source))
        self.assertEqual(missing, [], f"AiControl hides supported commands from availableActions: {missing}")

    def test_qa_text_pack_lookup_uses_baked_active_language_text(self) -> None:
        source = script_source()
        start = source.index('if (type == "qa_get_text_pack")')
        end = source.index('if (type == "qa_format_tags")', start)
        command = source[start:end]

        self.assertIn("if (!Settings.AiControl.AllowQaCommands)", command)
        self.assertIn('message = "invalid_text_id"', command)
        self.assertIn('TextPackKey(TextPackName::Text, "" + intArg)', command)
        self.assertIn('message = "text=<" + text + ">"', command)
        self.assertNotIn("Game.Sync", command)

    def test_semantic_ui_prompt_is_observed_and_executable(self) -> None:
        source = script_source()
        self.assertIn('RawMember("uiPrompt", UiPromptJson(activeScreen))', source)
        self.assertIn('if (type == "ui_answer")', source)
        self.assertIn('"ui_answer",', source[source.index("string AvailableActionsJson()"):])

    def test_dialog_box_confirmation_metadata_is_not_reported_as_safe_choice(self) -> None:
        source = script_source()
        self.assertIn("Dialogbox::GetDialogBoxAnswerRole(dialogBox.DialogType, i)", source)
        self.assertIn("Dialogbox::IsDialogBoxAnswerDangerous(dialogBox.DialogType, i)", source)

    def test_context_screen_command_is_observed_by_catalog(self) -> None:
        source = script_source()
        self.assertIn('if (type == "show_context_screen")', source)
        self.assertIn('"show_context_screen",', source[source.index("string AvailableActionsJson()"):])

    def test_visible_critters_expose_proto_and_dialog_identity_for_quest_tracing(self) -> None:
        source = script_source()
        critter_json = source[source.index("string CritterJson(Critter cr)"):]
        critter_json = critter_json[:critter_json.index("string MapItemsJson()")]
        self.assertIn('StringMember("protoId", string(cr.ProtoId))', critter_json)
        self.assertIn('StringMember("dialogId", dialogId)', critter_json)
        self.assertIn('BoolMember("isNoTalk", cr.IsNoTalk)', critter_json)
        self.assertIn('IntMember("talkDistance", talkDistance)', critter_json)

    def test_qa_property_reads_echo_the_request_identity(self) -> None:
        source = script_source()
        self.assertIn(
            "AiControlQaGetProp(CritterProperty prop, int32 requestId)", source
        )
        self.assertIn(
            "AiControlReceiveQaProp(CritterProperty prop, int32 value, int32 requestId)",
            source,
        )
        self.assertIn('IntMember("requestId", requestId)', source)

    def test_qa_property_writes_acknowledge_the_correlated_request(self) -> None:
        source = script_source()
        self.assertIn(
            "AiControlQaSetProp(CritterProperty prop, int32 value, int32 requestId)",
            source,
        )
        self.assertIn(
            "AiControlReceiveQaPropSet(CritterProperty prop, int32 value, int32 requestId)",
            source,
        )
        self.assertIn('StringMember("type", "qa_prop_set")', source)
        self.assertIn("AiControlQaSetProp(prop, intArg, hexX)", source)

    def test_normal_dialog_path_emits_qa_diagnostics_without_bypassing_dialogs(self) -> None:
        source = script_source()
        drop_menu_source = (PROJECT_ROOT / "Scripts" / "DropMenuHandler.fos").read_text(
            encoding="utf-8-sig"
        )
        self.assertIn("AiControlReceiveTalkDiagnostic", source)
        self.assertIn('StringMember("type", "talk_diagnostic")', source)
        self.assertIn("Entity[] heldEntities = Sync::SurvivingSnapshot();", drop_menu_source)
        self.assertIn("Dialogs::RunDialog(cr, npc, false);", drop_menu_source)
        self.assertIn("Sync::Restore(heldEntities)", drop_menu_source)
        self.assertNotIn("ignoreDistance : true", drop_menu_source)

    def test_timed_item_mode_reaches_the_bridge(self) -> None:
        payload = ai_control_mcp.typed_command_payload("tla_use_item", {"itemId": 7, "useMode": "timer:61"})
        self.assertEqual(payload["stringArg"], "timer:61")

    def test_timed_item_mode_accepts_only_canonical_bounded_seconds(self) -> None:
        for seconds in (1, 599):
            with self.subTest(seconds=seconds):
                payload = ai_control_mcp.typed_command_payload("tla_use_item", {"itemId": 7, "useMode": f"timer:{seconds}"})
                self.assertEqual(payload["stringArg"], f"timer:{seconds}")

        invalid_modes = (
            "timer:0",
            "timer:600",
            "timer:01",
            "timer:+1",
            " timer:1",
            "timer:1 ",
            "timer:12x",
            "timer:1suffix",
            "timer:" + "9" * 1000,
        )
        for use_mode in invalid_modes:
            with self.subTest(use_mode=use_mode[:32]):
                with self.assertRaisesRegex(ValueError, "canonical timer"):
                    ai_control_mcp.typed_command_payload("tla_use_item", {"itemId": 7, "useMode": use_mode})

    def test_timed_item_mode_is_strict_in_the_script(self) -> None:
        source = script_source()
        self.assertIn("bool TryParseTimerUseMode(string value, int& seconds)", source)
        self.assertIn("if (secondsText.isEmpty() || secondsText.length() > 3)", source)
        self.assertIn('if (digit < "0" || digit > "9")', source)
        self.assertIn('secondsText != "" + parsedSeconds', source)
        self.assertIn('message = "invalid_timer_target"', source)

    def test_use_item_rejects_ambiguous_targets(self) -> None:
        with self.assertRaisesRegex(ValueError, "at most one"):
            ai_control_mcp.typed_command_payload("tla_use_item", {"itemId": 7, "targetId": 8, "auxId": 9})

    def test_timer_mode_rejects_every_explicit_target(self) -> None:
        for target in ({"targetId": 8}, {"auxId": 9}):
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, "self-only"):
                    ai_control_mcp.typed_command_payload("tla_use_item", {"itemId": 7, "useMode": "timer:30", **target})

    def test_use_item_schema_models_exclusive_target_modes(self) -> None:
        schema = tool_schema("tla_use_item")
        self.assertEqual(len(schema["oneOf"]), 4)
        use_mode = schema["properties"]["useMode"]
        self.assertEqual(use_mode["maxLength"], 9)
        self.assertIn("[1-5][0-9]{2}", use_mode["pattern"])

    def test_ui_answer_requires_a_real_answer_selector(self) -> None:
        schema = tool_schema("tla_ui_answer")
        self.assertEqual(schema["anyOf"], [{"required": ["answerIndex"]}, {"required": ["answerId"]}])
        self.assertEqual(schema["properties"]["answerId"]["pattern"], "^(?:answer_[0-9]+|level_[0-9]+)$")
        with self.assertRaisesRegex(ValueError, "answerIndex or answerId"):
            ai_control_mcp.typed_command_payload("tla_ui_answer", {})
        for answer_id in ("", "   ", "vault_level_2"):
            with self.subTest(answer_id=answer_id):
                with self.assertRaisesRegex(ValueError, "answer_N or level_N"):
                    ai_control_mcp.typed_command_payload("tla_ui_answer", {"answerId": answer_id})

    def test_ui_answer_forwards_dialog_box_session(self) -> None:
        payload = ai_control_mcp.typed_command_payload(
            "tla_ui_answer", {"answerIndex": 1, "answerId": "answer_1", "expectedSession": 42})
        self.assertEqual(payload, {"type": "ui_answer", "intArg": 1, "stringArg": "answer_1", "auxId": 42})

        candidate = ai_control_mcp.ui_prompt_answer_candidate(
            {"index": 1, "id": "answer_1", "text": "Yes"}, {"kind": "dialog_box", "dialogBoxSession": 42})
        self.assertEqual(candidate["arguments"]["expectedSession"], 42)
        for invalid_session in (0, 0x1_0000_0000, "42"):
            with self.subTest(invalid_session=invalid_session):
                with self.assertRaisesRegex(ValueError, "expectedSession"):
                    ai_control_mcp.typed_command_payload(
                        "tla_ui_answer", {"answerIndex": 1, "expectedSession": invalid_session})

    def test_dialog_box_session_is_verified_before_dispatch(self) -> None:
        source = script_source()
        self.assertIn("ExecuteUiPromptAnswer(int requestedIndex, string answerId, ident expectedSession", source)
        self.assertIn('message = "ui_prompt_session_required"', source)
        self.assertIn("expectedSession.value != int64(dialogBox.Session)", source)
        self.assertIn("ExecuteUiPromptAnswer(intArg, stringArg, auxId, message)", source)

    def test_elevator_map_target_is_converted_to_answer_index(self) -> None:
        map_proto_id = "contract_elevator_source"
        previous = ai_control_mcp.AUTHORED_ELEVATOR_TRIGGER_CACHE.get(map_proto_id)
        ai_control_mcp.AUTHORED_ELEVATOR_TRIGGER_CACHE[map_proto_id] = [
            {
                "triggerEntry": "elevator",
                "hex": {"x": 10, "y": 20},
                "hexes": [{"x": 10, "y": 20}],
                "levels": ["floor_one", "floor_two", "floor_three"],
            }
        ]
        try:
            options = ai_control_mcp.local_elevator_trigger_options(
                {
                    "hasMap": True,
                    "map": {"protoId": map_proto_id},
                    "chosen": {"hex": {"x": 9, "y": 20}},
                },
                {"targetMapProtoId": "floor_two"},
            )
            follow_up = options[0]["followUp"]
            self.assertEqual(follow_up["arguments"], {"answerIndex": 1})
            self.assertEqual(follow_up["options"][1], {"answerIndex": 1, "mapProtoId": "floor_two", "preferred": True})
            self.assertTrue(all("answerId" not in option for option in follow_up["options"]))
            self.assertEqual(ai_control_mcp.authored_elevator_target_answer_index(map_proto_id, "floor_three", 3), 2)
        finally:
            if previous is None:
                ai_control_mcp.AUTHORED_ELEVATOR_TRIGGER_CACHE.pop(map_proto_id, None)
            else:
                ai_control_mcp.AUTHORED_ELEVATOR_TRIGGER_CACHE[map_proto_id] = previous

    def test_skill_box_ownership_is_an_assertion_not_authority(self) -> None:
        inferred = ai_control_mcp.context_screen_command({"screen": "SkillBox", "itemId": 7})
        self.assertEqual(inferred["intArg"], -1)
        self.assertEqual(ai_control_mcp.context_screen_command({"screen": "SkillBox", "itemId": 7, "isInventory": True})["intArg"], 1)
        self.assertEqual(ai_control_mcp.context_screen_command({"screen": "SkillBox", "itemId": 7, "isInventory": False})["intArg"], 0)
        with self.assertRaisesRegex(ValueError, "boolean ownership assertion"):
            ai_control_mcp.context_screen_command({"screen": "SkillBox", "itemId": 7, "isInventory": "false"})

        source = script_source()
        self.assertIn("targetItem.Ownership == ItemOwnership::CritterInventory && targetItem.CritterId == Chosen.Id", source)
        self.assertIn('message = "item_ownership_mismatch"', source)

    def test_qa_dialog_box_fixture_is_a_typed_test_only_tool(self) -> None:
        self.assertEqual(ai_control_mcp.typed_command_payload("tla_qa_show_dialog_box", {}), {"type": "qa_show_dialog_box"})
        self.assertEqual(ai_control_mcp.typed_command_type_for_tool("tla_qa_show_dialog_box"), "qa_show_dialog_box")
        self.assertIn("tla_qa_show_dialog_box", ai_control_mcp.typed_command_tool_names())
        self.assertTrue(ai_control_mcp.agent_run_forbidden_tool("tla_qa_show_dialog_box"))
        self.assertEqual(ai_control_mcp.command_catalog_entry("qa_show_dialog_box")["required"], [])

        schema = tool_schema("tla_qa_show_dialog_box")
        self.assertNotIn("required", schema)
        self.assertIn('"tla_qa_show_dialog_box"', SMOKE_PATH.read_text(encoding="utf-8"))

    def test_qa_dialog_box_fixture_uses_guarded_server_contract(self) -> None:
        source = script_source()
        self.assertIn("///@ RemoteCall Server AiControlQaShowDialogBox()", source)
        self.assertIn('if (type == "qa_show_dialog_box")', source)
        self.assertIn('CurPlayer.ServerCall.AiControlQaShowDialogBox()', source)
        self.assertIn('"qa_show_dialog_box"};', source[source.index("string AvailableActionsJson()"):])

        start = source.index("void AiControlQaShowDialogBox(Player player)")
        end = source.index("void AiControlQaTeleportGlobal(Player player)", start)
        fixture = source[start:end]
        self.assertIn("if (!Settings.AiControl.AllowQaCommands)", fixture)
        self.assertIn("cr == null || !Sync::Lock(cr)", fixture)
        self.assertIn("if (cr.DialogBoxPending)", fixture)
        self.assertIn("Dialogbox::ClearPendingDialogBox(cr)", fixture)
        self.assertIn("cr.LastDialogBoxShownTick + Dialogbox::NEXT_DIALOG_CALL", fixture)
        self.assertIn("Dialogbox::RunDialogBox(cr, DialogBoxType::AskFollowGlobalGroupRuler, 2", fixture)


if __name__ == "__main__":
    unittest.main()
