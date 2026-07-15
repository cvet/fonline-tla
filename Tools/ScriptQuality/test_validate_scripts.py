from __future__ import annotations

import unittest

from Tools.ScriptQuality.validate_scripts import (
    SEVERITY_ERROR,
    check_item_static_signature,
    check_item_trigger_location_sync,
    classify,
    mask_to,
)


def validate(source: str):
    code = mask_to(source, classify(source), "c")
    return check_item_trigger_location_sync("Scripts/Test.fos", code, source)


def validate_item_static(source: str):
    code = mask_to(source, classify(source), "c")
    return check_item_static_signature("Scripts/Test.fos", code, source)


class ItemStaticSignatureTests(unittest.TestCase):
    def test_accepts_exact_signature_with_neighboring_attributes_and_comments(self) -> None:
        violations = validate_item_static(
            "[[Async]]\n"
            "// Атрибут ItemStatic находится на соседней строке.\n"
            "[[ItemStatic]] /* комментарий перед функцией */\n"
            "bool Use(\n"
            "    Critter player,\n"
            "    StaticItem scenery, // допустимый комментарий между аргументами\n"
            "    Item ? item,\n"
            "    any skill)\n"
            "{\n"
            "    return true;\n"
            "}\n"
        )

        self.assertEqual(violations, [])

    def test_reports_each_signature_mismatch(self) -> None:
        invalid_sources = {
            "return type": "void Use(Critter cr, StaticItem scenery, Item? item, any skill)",
            "argument count": "bool Use(Critter cr, StaticItem scenery, Item? item)",
            "nullable critter": "bool Use(Critter? cr, StaticItem scenery, Item? item, any skill)",
            "nullable static item": "bool Use(Critter cr, StaticItem? scenery, Item? item, any skill)",
            "non-null item": "bool Use(Critter cr, StaticItem scenery, Item item, any skill)",
            "wrong fourth type": "bool Use(Critter cr, StaticItem scenery, Item? item, CritterProperty skill)",
        }

        for label, declaration in invalid_sources.items():
            with self.subTest(label=label):
                violations = validate_item_static(
                    "[[ItemStatic]]\n"
                    f"{declaration}\n"
                    "{\n"
                    "}\n"
                )

                self.assertEqual(len(violations), 1)
                self.assertEqual(violations[0].check, "item-static-signature")
                self.assertEqual(violations[0].severity, SEVERITY_ERROR)
                self.assertIn("bool NAME(Critter, StaticItem, Item?, any)", violations[0].message)

    def test_ignores_commented_attributes_and_other_callbacks(self) -> None:
        violations = validate_item_static(
            "// [[ItemStatic]]\n"
            "// void CommentedOut(Critter cr);\n"
            "/*\n"
            "[[ItemStatic]]\n"
            "void BlockCommented(Critter cr) {}\n"
            "*/\n"
            "[[ItemTrigger]]\n"
            "void Transit(Critter cr, StaticItem trigger, bool entered, mdir dir)\n"
            "{\n"
            "}\n"
        )

        self.assertEqual(violations, [])


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
