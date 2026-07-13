from __future__ import annotations

import unittest

from Tools.ScriptQuality.validate_scripts import check_item_trigger_location_sync, classify, mask_to


def validate(source: str):
    code = mask_to(source, classify(source), "c")
    return check_item_trigger_location_sync("Scripts/Test.fos", code, source)


class ItemTriggerLocationSyncTests(unittest.TestCase):
    def test_reports_missing_async_and_sync(self) -> None:
        violations = validate(
            "[[ItemTrigger]]\n"
            "void Transit(Critter cr, StaticItem trigger, bool entered, mdir dir)\n"
            "{\n"
            "    Location loc = cr.GetMap().GetLocation();\n"
            "}\n"
        )

        self.assertEqual(len(violations), 1)
        self.assertIn("[[Async]]", violations[0].message)
        self.assertIn("explicit Sync cover", violations[0].message)

    def test_reports_async_without_sync(self) -> None:
        violations = validate(
            "[[Async]]\n"
            "[[ItemTrigger]]\n"
            "void Transit(Critter cr, StaticItem trigger, bool entered, mdir dir)\n"
            "{\n"
            "    Location? loc = Game.GetLocation(Content::Location::test);\n"
            "}\n"
        )

        self.assertEqual(len(violations), 1)
        self.assertNotIn("[[Async]]", violations[0].message)
        self.assertIn("explicit Sync cover", violations[0].message)

    def test_accepts_async_trigger_with_sync_cover(self) -> None:
        violations = validate(
            "[[Async]] [[ItemTrigger]]\n"
            "void Transit(Critter cr, StaticItem trigger, bool entered, mdir dir)\n"
            "{\n"
            "    if (!Sync::LockCritterWithMapAndLocation(cr)) return;\n"
            "    Location loc = cr.GetMap().GetLocation();\n"
            "}\n"
        )

        self.assertEqual(violations, [])

    def test_ignores_non_trigger_and_comments(self) -> None:
        violations = validate(
            "void Helper(Critter cr) { Location loc = cr.GetMap().GetLocation(); }\n"
            "[[ItemTrigger]]\n"
            "void Plain(Critter cr, StaticItem trigger, bool entered, mdir dir)\n"
            "{\n"
            "    // Location loc = cr.GetMap().GetLocation();\n"
            "}\n"
        )

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
