#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_gui_screens as generator  # noqa: E402 - import the sibling generator under test.


class EmitOnConstructTests(unittest.TestCase):
    def emit(self, obj: dict[str, object]) -> list[str]:
        lines: list[str] = []
        generator.emit_on_construct(lines, obj, is_root=False)
        return lines

    def test_on_draw_callback_enables_draw_callback(self) -> None:
        lines = self.emit({'$type': 'Panel', 'OnDraw': 'SetActive(true);'})

        self.assertIn('        SetHasOnDraw(true);', lines)

    def test_sibling_item_view_cell_prototype_stays_drawable_while_empty(self) -> None:
        lines = self.emit({'$type': 'ItemView', 'CellPrototype': '".Cell"'})

        self.assertIn('        SetHasOnDraw(true);', lines)

    def test_child_item_view_cell_prototype_does_not_add_draw_callback(self) -> None:
        lines = self.emit({'$type': 'ItemView', 'CellPrototype': '"Cell"'})

        self.assertNotIn('        SetHasOnDraw(true);', lines)


class FormatterDiscoveryTests(unittest.TestCase):
    def test_generator_uses_the_project_formatter_toolchain(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        formatter_dir = project_root / 'Tools' / 'Formatter'
        if str(formatter_dir) not in sys.path:
            sys.path.insert(0, str(formatter_dir))
        from format_project import discover_clang_format as discover_project_clang_format

        self.assertEqual(
            Path(generator.discover_clang_format(project_root)).resolve(),
            Path(discover_project_clang_format(project_root)).resolve(),
        )


if __name__ == '__main__':
    unittest.main()
