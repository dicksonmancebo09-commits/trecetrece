import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_hangar_entry_test.py"
SPEC = importlib.util.spec_from_file_location("build_hangar_entry_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestHangarEntryPatch(unittest.TestCase):
    def make_rom(self):
        data = bytearray(MODULE.ROM_SIZE)
        data[MODULE.PATCH_OFFSET:MODULE.PATCH_OFFSET + 4] = MODULE.OLD_CONTEXT
        data[0xA0:0xBD] = bytes([1] * (0xBD - 0xA0))
        data[0xBD] = (-1 - sum(data[0xA0:0xBD])) & 0xFF
        return bytes(data)

    def test_patch_changes_only_immediate_byte(self):
        base = self.make_rom()
        patched = MODULE.patch_bytes(base)
        self.assertEqual(len(patched), len(base))
        differences = [i for i, (a, b) in enumerate(zip(base, patched)) if a != b]
        self.assertEqual(differences, [MODULE.PATCH_OFFSET])
        self.assertEqual(patched[MODULE.PATCH_OFFSET:MODULE.PATCH_OFFSET + 4], MODULE.NEW_CONTEXT)
        self.assertEqual(patched[0xBD], base[0xBD])

    def test_wrong_context_is_refused(self):
        base = bytearray(self.make_rom())
        base[MODULE.PATCH_OFFSET] = 0x02
        with self.assertRaisesRegex(ValueError, "context"):
            MODULE.patch_bytes(bytes(base))

    def test_wrong_size_is_refused(self):
        with self.assertRaisesRegex(ValueError, "8 MiB"):
            MODULE.patch_bytes(b"too short")


if __name__ == "__main__":
    unittest.main()
