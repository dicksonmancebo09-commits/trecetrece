from __future__ import annotations

import importlib.util
import struct
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "fix_v17_room0_palette_bank.py"
SPEC = importlib.util.spec_from_file_location("fix_v17_room0_palette_bank", MODULE_PATH)
assert SPEC and SPEC.loader
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)


class TestRoom0PaletteBankFix(unittest.TestCase):
    def test_changes_only_palette_bank_bits(self):
        words = [0x20F4, 0x2C5E, 0x2B7E, 0x2A7D]
        table = b"\x02\x00" + struct.pack("<4H", *words)
        fixed, report = patcher.change_metatile_palette_bank(table)
        fixed_words = list(struct.unpack("<4H", fixed[2:]))
        self.assertEqual([w >> 12 for w in fixed_words], [3, 3, 3, 3])
        self.assertEqual([w & 0x0FFF for w in fixed_words],
                         [w & 0x0FFF for w in words])
        self.assertEqual(fixed[:2], table[:2])
        self.assertEqual(report["banks_before"], [2])
        self.assertEqual(report["banks_after"], [3])

    def test_rejects_mixed_or_wrong_palette_banks(self):
        table = b"\x02\x00" + struct.pack("<2H", 0x20F4, 0x30F4)
        with self.assertRaisesRegex(ValueError, "Expected only palette bank"):
            patcher.change_metatile_palette_bank(table)

    def test_rejects_malformed_table(self):
        with self.assertRaisesRegex(ValueError, "2-byte header"):
            patcher.change_metatile_palette_bank(b"\x02\x00\xF4")

    def test_rejects_non_v17_rom_hash(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            patcher.change_room0_palette_bank(bytes(0x800000))


if __name__ == "__main__":
    unittest.main()
