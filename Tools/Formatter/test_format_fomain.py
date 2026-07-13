from __future__ import annotations

import unittest

from Tools.Formatter.format_fomain import ConfigEntry, render_entry_block


class RenderEntryBlockTests(unittest.TestCase):
    def test_empty_value_has_no_trailing_whitespace(self) -> None:
        entry = ConfigEntry("Testing.Filter", "", [], 0)

        self.assertEqual(render_entry_block([entry]), ["Testing.Filter ="])

    def test_nonempty_value_keeps_spaces_around_separator(self) -> None:
        entry = ConfigEntry("Testing.Enabled", "False", [], 0)

        self.assertEqual(render_entry_block([entry]), ["Testing.Enabled = False"])


if __name__ == "__main__":
    unittest.main()
