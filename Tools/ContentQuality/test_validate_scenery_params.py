#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_scenery_params as validator  # noqa: E402 - import the sibling tool under test.


class SceneryParamsValidatorTests(unittest.TestCase):
    def validate(self, map_text: str) -> validator.ValidationResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            maps_root = project_root / "Maps"
            maps_root.mkdir()
            (maps_root / "synthetic.fomap").write_text(map_text, encoding="utf-8")
            return validator.validate_project(project_root)

    def test_parser_keeps_item_fields_section_local(self) -> None:
        result = self.validate(
            "[ProtoMap]\n"
            "$Name = synthetic\n\n"
            "[Item]\n"
            "$Proto = Trigger\n"
            "Hex = 10 20\n"
            "SceneryParams = 5\n"
            "TriggerScript = Trigger::Warn\n\n"
            "[Critter]\n"
            "SceneryParams = broken\n\n"
            "[Item]\n"
            "$Proto = generic_1\n"
            "Hex = 30 40\n"
            "SceneryParams = klam_bboard\n"
            "StaticScript = Scenery::Dialog\n"
        )

        self.assertEqual(result.item_sections, 2)
        self.assertEqual(result.contract_items, 2)
        self.assertEqual(result.errors, [])

    def test_all_supported_current_forms_pass(self) -> None:
        result = self.validate(
            "[ProtoMap]\n"
            "$Name = synthetic\n\n"
            "[Item]\n"
            "$Proto = Trigger\n"
            "SceneryParams = 2 1 Content::Map::q_silo1 q_silo2 0\n"
            "TriggerScript = Trigger::Elevator\n\n"
            "[Item]\n"
            "$Proto = Trigger\n"
            "SceneryParams = 6 sad_level1 Content::Map::sad_level2 sad_level3 sad_level4\n"
            "TriggerScript = Trigger::Elevator4\n\n"
            "[Item]\nSceneryParams = 99\nTriggerScript = Trigger::AttackStop\n\n"
            "[Item]\nSceneryParams = @113\nTriggerScript = Trigger::DoorOpen\n\n"
            "[Item]\nSceneryParams = @2\nTriggerScript = Silo::Transit\n\n"
            "[Item]\nSceneryParams = 1 -80 20\nStaticScript = EnergyBarier::Terminal\n\n"
            "[Item]\nSceneryParams = 100\nStaticScript = SeAndroid::Boxes\n\n"
            "[Item]\nSceneryParams = 1 1 1 1 1\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 333 8040 8042 60 100\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = @17 1\nStaticScript = Scenery::DoorControl\n\n"
            "[Item]\nSceneryParams = Content::Dialog::geck_comp_inner\nStaticScript = Scenery::Dialog\n\n"
            "[Item]\nSceneryParams = klam_bboard\nStaticScript = Scenery::Dialog\n\n"
            "[Item]\nSceneryParams = 0\nStaticScript = Scenery::Dialog\n"
        )

        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_elevator_checks_arity_numbers_ids_sentinel_and_map_count(self) -> None:
        result = self.validate(
            "[ProtoMap]\n$Name = synthetic\n\n"
            "[Item]\nSceneryParams = entry 1 map_a map_b 0\nTriggerScript = Trigger::Elevator\n\n"
            "[Item]\nSceneryParams = 2 4 map_a 0 map_c\nTriggerScript = Trigger::Elevator\n\n"
            "[Item]\nSceneryParams = 2 1 Content::Dialog::wrong map_b 0\nTriggerScript = Trigger::Elevator\n\n"
            "[Item]\nSceneryParams = 6 map_a map_b map_c\nTriggerScript = Trigger::Elevator4\n"
        )

        codes = [finding.code for finding in result.errors]
        self.assertIn("integer", codes)
        self.assertIn("sentinel-order", codes)
        self.assertIn("map-count", codes)
        self.assertIn("map-id", codes)
        self.assertIn("arity", codes)

    def test_numeric_contracts_reject_noncanonical_and_out_of_range_values(self) -> None:
        result = self.validate(
            "[ProtoMap]\n$Name = synthetic\n\n"
            "[Item]\nSceneryParams = 04\nTriggerScript = Trigger::Warn\n\n"
            "[Item]\nSceneryParams = @x\nTriggerScript = Silo::Transit\n\n"
            "[Item]\nSceneryParams = -1 101 -101\nStaticScript = EnergyBarier::Terminal\n\n"
            "[Item]\nSceneryParams = 101\nStaticScript = SeAndroid::Boxes\n\n"
            "[Item]\nSceneryParams = 333 9000 8000 0 -1\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 0 8040 8042 10 30\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 333 0 8042 10 30\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 333 8040 8042 61 30\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 333 8040 8042 10 101\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 0 0 0\nStaticScript = EnergyBarier::Terminal\n\n"
            "[Item]\nSceneryParams = 0\nTriggerScript = Trigger::Warn\n\n"
            "[Item]\nSceneryParams = @17 2\nStaticScript = Scenery::DoorControl\n"
        )

        codes = [finding.code for finding in result.errors]
        self.assertGreaterEqual(codes.count("integer"), 2)
        self.assertIn("range", codes)
        self.assertIn("text-order", codes)

    def test_runtime_numeric_boundaries_match_consumers(self) -> None:
        valid = self.validate(
            "[ProtoMap]\n$Name = synthetic\n\n"
            "[Item]\nSceneryParams = 1\nTriggerScript = Trigger::DialogNpc\n\n"
            "[Item]\nSceneryParams = 1 -100 100\nStaticScript = EnergyBarier::Terminal\n\n"
            "[Item]\nSceneryParams = 1 1 1 1 1\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 2147483647 1 2147483647 60 100\nTriggerScript = NpcDialog::NpcDialog\n"
        )
        self.assertEqual(valid.errors, [])

        invalid = self.validate(
            "[ProtoMap]\n$Name = synthetic\n\n"
            "[Item]\nSceneryParams = 0\nTriggerScript = Trigger::DialogNpc\n\n"
            "[Item]\nSceneryParams = 0 -100 100\nStaticScript = EnergyBarier::Terminal\n\n"
            "[Item]\nSceneryParams = 1 1 1 0 1\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 1 1 1 61 1\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 1 1 1 1 0\nTriggerScript = NpcDialog::NpcDialog\n\n"
            "[Item]\nSceneryParams = 1 1 1 1 101\nTriggerScript = NpcDialog::NpcDialog\n"
        )
        self.assertEqual(len(invalid.errors), 6)
        self.assertTrue(all(finding.code == "range" for finding in invalid.errors))

    def test_dialog_form_is_typed_and_transfer_contract_is_warning_only(self) -> None:
        result = self.validate(
            "[ProtoMap]\n$Name = synthetic\n\n"
            "[Item]\nSceneryParams = Content::Map::not_a_dialog\nStaticScript = Scenery::Dialog\n\n"
            "[Item]\n"
            "$Proto = generic_1\n"
            "Hex = 5 6\n"
            "SceneryParams = Content::Map::v13_3 2 5\n"
            "StaticScript = Scenery::TransferToMap\n"
        )

        self.assertEqual([finding.code for finding in result.errors], ["dialog-id"])
        self.assertEqual([finding.code for finding in result.warnings], ["ambiguous-transfer"])

    def test_cli_warning_does_not_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            maps_root = project_root / "Maps"
            maps_root.mkdir()
            (maps_root / "synthetic.fomap").write_text(
                "[ProtoMap]\n$Name = synthetic\n\n"
                "[Item]\nSceneryParams = 0 4 13\nStaticScript = Scenery::TransferToMap\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = validator.main([str(project_root), "--summary"])

        self.assertEqual(exit_code, 0)
        self.assertIn("0 error(s), 1 warning(s)", output.getvalue())

    def test_cli_schema_error_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            maps_root = project_root / "Maps"
            maps_root.mkdir()
            (maps_root / "synthetic.fomap").write_text(
                "[ProtoMap]\n$Name = synthetic\n\n"
                "[Item]\nSceneryParams = not-a-role\nTriggerScript = Trigger::Attack\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = validator.main([str(project_root), "--summary"])

        self.assertEqual(exit_code, 1)
        self.assertIn("1 error(s), 0 warning(s)", output.getvalue())


if __name__ == "__main__":
    unittest.main()
