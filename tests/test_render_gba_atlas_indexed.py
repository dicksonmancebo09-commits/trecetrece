from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "render_gba_atlas_indexed.py"
SPEC = importlib.util.spec_from_file_location("render_gba_atlas_indexed", MODULE)
assert SPEC and SPEC.loader
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class TestIndexedAtlasRenderer(unittest.TestCase):
    def test_palette_requires_transparent_index_zero(self):
        parsed = renderer.read_palette({"palette": [
            {"index": 0, "name": "transparent", "hex": "#00000000"},
            {"index": 1, "name": "ink", "hex": "#172336"},
        ]})
        self.assertEqual(len(parsed), 2)
        with self.assertRaisesRegex(ValueError, "index 0 must be transparent"):
            renderer.read_palette({"palette": [
                {"index": 0, "name": "ink", "hex": "#172336"},
            ]})

    def test_hex_rgb_and_rgba(self):
        self.assertEqual(renderer.hex_rgba("#172336"), (23, 35, 54, 255))
        self.assertEqual(renderer.hex_rgba("#00000000"), (0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
