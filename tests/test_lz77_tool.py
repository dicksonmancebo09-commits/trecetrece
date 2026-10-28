"""Synthetic tests for tools/lz77_tool.py; no commercial ROM is required."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "tools" / "lz77_tool.py"
SPEC = importlib.util.spec_from_file_location("lz77_tool", SCRIPT)
lz = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(lz)


class Lz77ToolTests(unittest.TestCase):
    def test_literal_stream_decodes(self):
        stream = bytes([0x10, 3, 0, 0, 0, ord("A"), ord("B"), ord("C")])
        decoded, consumed = lz.decompress_lz77(stream)
        self.assertEqual(decoded, b"ABC")
        self.assertEqual(consumed, len(stream))

    def test_overlapping_backreference_decodes(self):
        stream = bytes([0x10, 18, 0, 0, 0x07, *([ord("A")] * 5), 0xD0, 0x00])
        decoded, _ = lz.decompress_lz77(stream)
        self.assertEqual(decoded, b"A" * 18)

    def test_rejects_wrong_type(self):
        with self.assertRaises(ValueError):
            lz.decompress_lz77(b"\x11\x03\x00\x00xxxx")

    def test_rejects_truncated_literal(self):
        with self.assertRaises(ValueError):
            lz.decompress_lz77(bytes([0x10, 1, 0, 0, 0]))

    def test_rejects_invalid_displacement(self):
        with self.assertRaises(ValueError):
            lz.decompress_lz77(bytes([0x10, 3, 0, 0, 0x80, 0, 0]))

    def test_enforces_output_size_limit(self):
        with self.assertRaises(ValueError):
            lz.decompress_lz77(bytes([0x10, 100, 0, 0]), max_output_size=64)

    def test_compressor_round_trips_data_families(self):
        fixtures = [
            b"ABCD" * 100,
            b"A" * 300,
            bytes(range(256)) * 2,
            b"short text with repeated short text with repeated short text",
            bytes((i * 37 + i // 11) & 0xFF for i in range(2048)),
        ]
        for source in fixtures:
            with self.subTest(length=len(source)):
                encoded = lz.compress_lz77(source)
                decoded, consumed = lz.decompress_lz77(
                    encoded, max_output_size=max(len(source), 1)
                )
                self.assertEqual(decoded, source)
                self.assertEqual(consumed, len(encoded))

    def test_compressed_stream_is_accepted_by_project_auditor(self):
        from tools.gba_rom_audit import gba_lz77_decompress

        source = b"Villa Duarte / Sector Cero " * 30
        encoded = lz.compress_lz77(source)
        decoded, consumed = gba_lz77_decompress(encoded)
        self.assertEqual(decoded, source)
        self.assertEqual(consumed, len(encoded))

    def test_empty_input_cannot_compress(self):
        with self.assertRaises(ValueError):
            lz.compress_lz77(b"")

    def test_scan_finds_aligned_candidate(self):
        stream = lz.compress_lz77(b"ABCD" * 32)
        rom = b"\xFF" * 16 + stream + b"\xFF" * 8
        found = lz.scan_lz77(rom, alignment=4, min_output_size=32)
        self.assertTrue(any(row["offset"] == 16 for row in found))

    def test_scan_respects_alignment(self):
        stream = lz.compress_lz77(b"ABCD" * 32)
        rom = b"X" + stream
        self.assertFalse(any(row["offset"] == 1 for row in lz.scan_lz77(rom, alignment=4)))
        self.assertTrue(any(row["offset"] == 1 for row in lz.scan_lz77(rom, alignment=1)))


if __name__ == "__main__":
    unittest.main()
