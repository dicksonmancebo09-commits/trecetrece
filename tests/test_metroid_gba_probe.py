import unittest

from tools.metroid_gba_probe import ROM_BASE, analyze_bytes, decode_arm_branch


def make_test_rom() -> bytes:
    data = bytearray([0x00] * 0x200)
    # Entry instruction: B from 0x08000000 to 0x080000C0 (offset +0xB8).
    data[0:4] = (0xEA00002E).to_bytes(4, "little")
    data[0xA0:0xAC] = b"TEST ROM    "
    data[0xAC:0xB0] = b"AMTE"
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBC] = 0
    data[0xBD] = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return bytes(data)


class GbaProbeTests(unittest.TestCase):
    def test_decodes_arm_entry_branch(self):
        branch = decode_arm_branch(0xEA00002E, ROM_BASE)
        self.assertIsNotNone(branch)
        assert branch is not None
        self.assertEqual(branch["mnemonic"], "B")
        self.assertEqual(branch["target_address"], "0x080000C0")
        self.assertEqual(branch["target_file_offset"], 0xC0)

    def test_reports_amte_and_valid_header_checksum(self):
        result = analyze_bytes(make_test_rom(), "synthetic.gba")
        self.assertTrue(result["identification"]["looks_like_metroid_fusion_usa_australia"])
        self.assertTrue(result["gba"]["header_complement_valid"])
        self.assertTrue(result["read_only"])

    def test_reports_wrong_checksum_without_mutating_input(self):
        data = bytearray(make_test_rom())
        data[0xBD] ^= 0xFF
        before = bytes(data)
        result = analyze_bytes(bytes(data), "synthetic.gba")
        self.assertFalse(result["gba"]["header_complement_valid"])
        self.assertEqual(bytes(data), before)

    def test_rejects_short_file(self):
        with self.assertRaises(ValueError):
            analyze_bytes(b"too short")


if __name__ == "__main__":
    unittest.main()
