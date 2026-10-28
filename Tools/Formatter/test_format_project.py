from __future__ import annotations

import unittest

from Tools.Formatter.format_project import fix_fos_nullable_suffix


class NullableReturnTests(unittest.TestCase):
    def test_qualified_parameter_keeps_nullable_return(self) -> None:
        for return_type, parameters in (
            ("Critter", "Testing::TestContext ctx, Map homeMap"),
            ("Map", "Testing::TestContext ctx, Worldmap::CFoundedEncounter fe"),
            ("NpcPlanes::NpcPlane", "Testing::TestContext ctx"),
            ("ProtoItem", "Critter cr, int slot = CritterItemSlot::Main"),
        ):
            with self.subTest(return_type=return_type):
                source = f"{return_type} ? MakeFixture({parameters})\n"
                expected = f"{return_type}? MakeFixture({parameters})\n"

                self.assertEqual(fix_fos_nullable_suffix(source), expected)
                self.assertEqual(fix_fos_nullable_suffix(expected), expected)

    def test_qualified_calls_in_ternary_remain_unchanged(self) -> None:
        for source in (
            "Condition ? Get(Testing::Value) : Other()\n",
            "Condition ? Get(flag ? first : second) : Other()\n",
            "    result = flag ? Testing::First() : Testing::Second();\n",
        ):
            with self.subTest(source=source):
                self.assertEqual(fix_fos_nullable_suffix(source), source)

    def test_plain_and_split_nullable_returns_still_work(self) -> None:
        self.assertEqual(fix_fos_nullable_suffix("Item ? Find()\r\n"), "Item? Find()\r\n")
        self.assertEqual(
            fix_fos_nullable_suffix("Map ?\n    Create(Testing::TestContext ctx)\n"),
            "Map? Create(Testing::TestContext ctx)\n",
        )


if __name__ == "__main__":
    unittest.main()
