import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from catalog_lz77_assets import decode_lz77


class TestLz77Decoder(unittest.TestCase):
    def test_literal_bytes(self):
        stream = bytes([0x10, 3, 0, 0, 0x00, ord("A"), ord("B"), ord("C")])
        self.assertEqual(decode_lz77(stream, 0, 1024), (b"ABC", 8))

    def test_back_reference(self):
        # One literal A followed by a length-5, distance-1 reference.
        stream = bytes([0x10, 6, 0, 0, 0x40, ord("A"), 0x20, 0x00])
        self.assertEqual(decode_lz77(stream, 0, 1024), (b"AAAAAA", 8))

    def test_rejects_bad_distance(self):
        stream = bytes([0x10, 3, 0, 0, 0x80, 0x00, 0x00])
        self.assertIsNone(decode_lz77(stream, 0, 1024))

    def test_rejects_non_lz77(self):
        self.assertIsNone(decode_lz77(b"\x00\x01\x02\x03", 0, 1024))


if __name__ == "__main__":
    unittest.main()
