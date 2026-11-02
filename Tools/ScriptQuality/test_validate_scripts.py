from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from Tools.ScriptQuality.validate_scripts import (
    SEVERITY_ERROR,
    check_component_null_probe,
    check_item_static_signature,
    check_legacy_item_kind,
    classify,
    derive_component_names,
    derive_entity_components,
    fix_file,
    mask_to,
)


def validate_item_static(source: str):
    code = mask_to(source, classify(source), "c")
    return check_item_static_signature("Scripts/Test.fos", code, source)


def code_of(source: str) -> str:
    return mask_to(source, classify(source), "c")


def validate_null_probe(source: str, components: set[str]):
    return check_component_null_probe("Scripts/Test.fos", code_of(source), source, components)


def validate_legacy_item_kind(source: str):
    return check_legacy_item_kind("Scripts/Test.fos", code_of(source), source, derive_entity_components(source))


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


class ComponentNullProbeTests(unittest.TestCase):
    GRID_DECLARATION = "///@ Property Item Common bool Grid Component\n"

    def test_component_names_include_declared_markers(self) -> None:
        source = (
            self.GRID_DECLARATION
            + "///@ Property Critter Server bool Bulletin Component // комментарий\n"
            + "///@ Property Item Common bool IsFlag Mutable\n"
            + "void F(Critter cr)\n{\n    bool a = cr.HasDialogContext;\n}\n"
        )

        self.assertEqual(derive_component_names(code_of(source), source), {"Grid", "Bulletin", "DialogContext"})

    def test_non_entity_receiver_is_not_a_probe(self) -> None:
        source = (
            self.GRID_DECLARATION
            + "bool Handler(Gui::Object obj)\n"
            + "{\n"
            + "    Gui::Object? o = Gui::GetHoveredObject();\n"
            + "    if (o != null && o.Grid != null) {\n"
            + "        return true;\n"
            + "    }\n"
            + "    return obj.Grid == null;\n"
            + "}\n"
        )

        self.assertEqual(validate_null_probe(source, derive_component_names(code_of(source), source)), [])

    def test_entity_receiver_is_flagged(self) -> None:
        source = (
            self.GRID_DECLARATION
            + "void Gui(Gui::Object it)\n"
            + "{\n"
            + "}\n"
            + "void F()\n"
            + "{\n"
            + "    Item? it = Game.GetItem(ZERO_IDENT);\n"
            + "    if (it != null && it.Grid == null) {\n"
            + "    }\n"
            + "}\n"
        )

        violations = validate_null_probe(source, derive_component_names(code_of(source), source))

        self.assertEqual([(v.check, v.line, v.severity) for v in violations], [("component-null-probe", 8, SEVERITY_ERROR)])

    def test_ternary_and_bitwise_operands_are_not_declarations(self) -> None:
        source = (
            "void F(Item item, bool flag, int mask)\n"
            "{\n"
            "    Item? other = flag ? item : null;\n"
            "    Critter? pick = (flag ? item : other);\n"
            "    bool bits = (mask & item) != 0;\n"
            "    bool both = flag && item != null;\n"
            "    if (item.Grid != null) {\n"
            "    }\n"
            "}\n"
        )

        self.assertEqual([v.line for v in validate_null_probe(source, {"Grid"})], [7])

    def test_foreach_and_reference_declarations_are_recognized(self) -> None:
        source = (
            "void F(Gui::Object[] & objects, Gui::Object &in first, Gui::Object& second)\n"
            "{\n"
            "    for (Gui::Object? o : objects) {\n"
            "        if (o.Grid != null || first.Grid != null || second.Grid != null) {\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

        self.assertEqual(validate_null_probe(source, {"Grid"}), [])

    def test_undeclared_or_compound_receiver_is_flagged(self) -> None:
        source = (
            "void F()\n"
            "{\n"
            "    if (unknown.Grid != null) {\n"
            "    }\n"
            "    if (GetObject().Grid != null || holder.Value.Grid == null) {\n"
            "    }\n"
            "    auto guessed = Pick();\n"
            "    if (guessed.Grid != null) {\n"
            "    }\n"
            "}\n"
        )

        self.assertEqual([v.line for v in validate_null_probe(source, {"Grid"})], [3, 5, 5, 8])

    def test_fix_rewrites_only_entity_receivers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Test.fos"
            path.write_bytes(b"void F(Gui::Object o, Item it)\r\n{\r\n    bool a = o.Grid != null;\r\n    bool b = it.Grid == null;\r\n}\r\n")

            fix_file(path, {"Grid"})

            self.assertEqual(path.read_bytes(), b"void F(Gui::Object o, Item it)\r\n{\r\n    bool a = o.Grid != null;\r\n    bool b = !it.HasGrid;\r\n}\r\n")


class LegacyItemKindTests(unittest.TestCase):
    DECLARATIONS = (
        "///@ Property Item Common bool Weapon Component\n"
        "///@ Property Item Server bool Lockpick Component // маркер отмычки\n"
        "///@ Property Critter Server bool Bulletin Component\n"
    )

    def test_entity_components_come_from_declarations(self) -> None:
        self.assertEqual(
            derive_entity_components(self.DECLARATIONS + "///@ Property Item Common bool IsFlag Mutable\n"),
            {"Item": {"Weapon", "Lockpick"}, "Critter": {"Bulletin"}},
        )

    def test_reports_retired_kind_identifiers_in_code(self) -> None:
        source = (
            "void F(Item item, Critter cr)\n"
            "{\n"
            "    if (item.Type == ItemType::Misc) {\n"
            "    }\n"
            "    Item[] keys = cr.GetItems(ItemProperty::Type, 7);\n"
            "}\n"
        )

        violations = validate_legacy_item_kind(source)

        self.assertEqual([(v.check, v.line, v.severity) for v in violations],
                         [("legacy-item-kind", 3, SEVERITY_ERROR), ("legacy-item-kind", 5, SEVERITY_ERROR)])

    def test_reports_retired_kind_metadata(self) -> None:
        source = (
            "///@ Enum ItemType Misc = 5\n"
            "///@ Property Item Common ItemType Type Mutable PublicSync Persistent\n"
        )

        self.assertEqual([v.line for v in validate_legacy_item_kind(source)], [1, 2])

    def test_reports_flat_field_of_declared_component(self) -> None:
        source = (
            self.DECLARATIONS
            + "///@ Property Item Common int32 Weapon_MaxAmmoCount Mutable PublicSync Persistent\n"
            + "///@ Property Item Server dict<hstring, int32> Lockpick_Points Mutable Persistent\n"
            + "///@ Property Item Common int32 Weapon.MaxAmmoCount Mutable PublicSync Persistent\n"
            + "///@ Property Critter Server int32 Weapon_Skill Mutable\n"
            + "///@ Property Item Common int32 Radio_Channel Mutable\n"
            + "///@ Property Critter Server int32 Bulletin_Board Mutable\n"
        )

        violations = validate_legacy_item_kind(source)

        self.assertEqual([v.line for v in violations], [4, 5, 9])
        self.assertIn("Weapon.MaxAmmoCount", violations[0].message)

    def test_ignores_comments_strings_and_component_enum_spellings(self) -> None:
        source = (
            self.DECLARATIONS
            + "// Прежний енум ItemType и свойство ItemProperty::Type удалены\n"
            + "/* breadcrumb: item.Type == ItemType::Ammo */\n"
            + "int GetItemType(int idx)\n"
            + "{\n"
            + "    string s = \"ItemType\";\n"
            + "    int field = ItemProperty::Weapon_MaxAmmoCount;\n"
            + "    return idx;\n"
            + "}\n"
        )

        self.assertEqual(validate_legacy_item_kind(source), [])


if __name__ == "__main__":
    unittest.main()
