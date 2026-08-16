#!/usr/bin/env python3
"""Focused tests for the native ptr/nptr ABI gate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_nullable as validator  # noqa: E402


class NativeAbiValidationTests(unittest.TestCase):
    def validate(self, text: str) -> list[str]:
        return validator.validate_native_text(Path("fixture.cpp"), text)

    def test_export_method_rejects_raw_return_receiver_and_argument(self) -> None:
        errors = self.validate(
            """\
///@ ExportMethod
FO_SCRIPT_API Critter* Server_Game_Find(ServerEngine* engine, Item* item);
"""
        )

        self.assertEqual(len(errors), 3)
        self.assertTrue(any("Critter*" in error for error in errors))
        self.assertTrue(any("ServerEngine*" in error for error in errors))
        self.assertTrue(any("Item*" in error for error in errors))

    def test_export_method_accepts_ptr_and_nptr(self) -> None:
        errors = self.validate(
            """\
///@ ExportMethod
FO_SCRIPT_API nptr<Critter> Server_Game_Find(ptr<ServerEngine> engine, ptr<Item> item);
"""
        )

        self.assertEqual(errors, [])

    def test_unannotated_fo_script_api_still_rejects_raw_handles(self) -> None:
        errors = self.validate("FO_SCRIPT_API Item* NativeBridge(Critter* cr);\n")

        self.assertEqual(len(errors), 2)
        self.assertTrue(all("FO_SCRIPT_API signature" in error for error in errors))

    def test_internal_raw_pointers_and_setup_bakers_hook_are_allowed(self) -> None:
        errors = self.validate(
            "Critter* FindInternal(Item* item);\n\n"
            "///@ EngineHook\n"
            "FO_SCRIPT_API void SetupBakersHook(const_span<string> names, "
            "vector<unique_ptr<BaseBaker>>& bakers, BakingContext* context);\n"
        )

        self.assertEqual(errors, [])

    def test_export_ref_type_checks_only_members_named_by_export_list(self) -> None:
        errors = self.validate(
            """\
///@ ExportRefType Server RefCounted Export = GetDemand, Current
class DialogAnswer
{
public:
    auto GetDemand(int32_t index) -> DialogAnswerReq*;
    DialogAnswerReq* GetInternal(int32_t index);
    Critter* Current {};
    Item* InternalItem {};
};
"""
        )

        self.assertEqual(len(errors), 2)
        self.assertTrue(any("DialogAnswerReq*" in error and "GetDemand" in error for error in errors))
        self.assertTrue(any("Critter*" in error and "Current" in error for error in errors))
        self.assertFalse(any("InternalItem" in error or "GetInternal" in error for error in errors))

    def test_find_and_check_func_reject_nested_raw_template_arguments(self) -> None:
        errors = self.validate(
            r'''\
auto first = engine.FindFunc<void, Critter*, vector<Item*>>(name);
auto second = engine.CheckFunc<bool, ptr<Critter>, nptr<Item>>(name);
auto third = engine.CheckFunc<Map*, ptr<Critter>>(name);
auto fourth = engine.CheckFunc<void, Location*>(name);
auto forwarded = engine.FindFunc<TRet, Args...>(name);
// engine.CheckFunc<void, Map*>(commented_out);
const auto example = "FindFunc<void, Location*>(not_code)";
const auto raw_example = R"cpp(CheckFunc<void, Player*>(not_code))cpp";
const auto raw_export = R"cpp(///@ ExportMethod
FO_SCRIPT_API Critter* Server_Game_NotCode(ServerEngine* engine))cpp";
'''
        )

        self.assertEqual(len(errors), 4)
        self.assertTrue(any("Critter*" in error for error in errors))
        self.assertTrue(any("Item*" in error for error in errors))
        self.assertTrue(any("Map*" in error and "CheckFunc" in error for error in errors))
        self.assertTrue(any("Location*" in error and "CheckFunc" in error for error in errors))

    def test_legacy_fo_nullable_is_rejected(self) -> None:
        errors = self.validate(
            """\
///@ ExportMethod
FO_SCRIPT_API void Server_Game_Find(ptr<ServerEngine> engine, FO_NULLABLE Item item);
"""
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("obsolete FO_NULLABLE", errors[0])


if __name__ == "__main__":
    unittest.main()
