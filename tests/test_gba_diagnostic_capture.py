"""Tests for mGBA window selection/capture safeguards."""
import importlib.util
import struct
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "run_gba_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("run_gba_diagnostic", SCRIPT)
assert SPEC and SPEC.loader
diag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diag)


class DiagnosticCaptureTests(unittest.TestCase):
    def test_parse_shell_geometry(self):
        self.assertEqual(
            diag.parse_window_geometry("WINDOW=4194321\nX=1\nY=2\nWIDTH=480\nHEIGHT=320\nSCREEN=0\n"),
            (480, 320),
        )

    def test_parse_geometry_rejects_missing_or_bad_values(self):
        self.assertIsNone(diag.parse_window_geometry("WINDOW=1\nX=0\nY=0\n"))
        self.assertIsNone(diag.parse_window_geometry("WIDTH=x\nHEIGHT=320\n"))

    def test_png_dimensions_requires_valid_png_header(self):
        self.assertIsNone(diag.png_dimensions(b"not a PNG"))
        self.assertIsNone(diag.png_dimensions(b"\x89PNG\r\n\x1a\n" + bytes(16)))

    def test_png_dimensions_reads_ihdr(self):
        header = (
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">IIBBBBB", 480, 320, 8, 2, 0, 0, 0)
        )
        self.assertEqual(diag.png_dimensions(header), (480, 320))

    def test_detects_menu_bar_screenshot_dimensions(self):
        header = (
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">IIBBBBB", 480, 22, 8, 2, 0, 0, 0)
        )
        self.assertEqual(diag.png_dimensions(header), (480, 22))
        width, height = diag.png_dimensions(header)
        self.assertFalse(width >= 240 and height >= 160)


if __name__ == "__main__":
    unittest.main()
