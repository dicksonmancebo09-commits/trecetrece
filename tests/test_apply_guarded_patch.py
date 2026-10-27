from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "apply_guarded_patch.py"
SPEC = importlib.util.spec_from_file_location("apply_guarded_patch", MODULE_PATH)
assert SPEC and SPEC.loader
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)


def synthetic_gba() -> bytes:
    data = bytearray(0x200)
    data[0xA0:0xAC] = b"TEST ROM".ljust(12, b"\0")
    data[0xAC:0xB0] = b"TEST"
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBC] = 0
    data[0xBD] = patcher.gba_header_complement(data)
    return bytes(data)


class TestGuardedPatch(unittest.TestCase):
    def manifest(self, base: bytes) -> dict:
        return {
            "patch_id": "unit-test",
            "base_sha256": hashlib.sha256(base).hexdigest(),
            "writes": [
                {
                    "offset": "0x120",
                    "expected_before_hex": "00010203",
                    "replacement_hex": "aabbccdd",
                    "purpose": "replace synthetic bytes"
                }
            ],
            "header": {"recalculate_complement": True},
            "expected_output": {"title": "TEST ROM", "game_code": "TEST"}
        }

    def test_applies_after_expected_bytes_and_rechecks_header(self):
        base = bytearray(synthetic_gba())
        base[0x120:0x124] = bytes.fromhex("00010203")
        base = bytes(base)
        out, report = patcher.apply_patch_bytes(base, self.manifest(base))
        self.assertEqual(out[0x120:0x124], bytes.fromhex("aabbccdd"))
        self.assertEqual(report["writes_applied"], 1)
        self.assertEqual(out[0xBD], patcher.gba_header_complement(out))
        self.assertNotEqual(hashlib.sha256(base).hexdigest(), report["output_sha256"])

    def test_rejects_wrong_base_hash(self):
        base = synthetic_gba()
        manifest = self.manifest(base)
        manifest["base_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            patcher.apply_patch_bytes(base, manifest)

    def test_rejects_wrong_expected_bytes(self):
        base = synthetic_gba()
        manifest = self.manifest(base)
        with self.assertRaisesRegex(ValueError, "Precondition failed"):
            patcher.apply_patch_bytes(base, manifest)

    def test_rejects_overlapping_writes(self):
        base = bytearray(synthetic_gba())
        base[0x120:0x126] = bytes.fromhex("000102030405")
        base = bytes(base)
        manifest = self.manifest(base)
        manifest["base_sha256"] = hashlib.sha256(base).hexdigest()
        manifest["writes"].append({
            "offset": "0x122",
            "expected_before_hex": "0203",
            "replacement_hex": "ffff",
            "purpose": "overlap must fail"
        })
        with self.assertRaisesRegex(ValueError, "Overlapping writes"):
            patcher.apply_patch_bytes(base, manifest)

    def test_rejects_writes_outside_rom(self):
        base = synthetic_gba()
        manifest = self.manifest(base)
        manifest["writes"][0]["offset"] = "0x1FF"
        manifest["writes"][0]["expected_before_hex"] = "00010203"
        manifest["writes"][0]["replacement_hex"] = "aabbccdd"
        with self.assertRaisesRegex(ValueError, "outside the ROM bounds"):
            patcher.apply_patch_bytes(base, manifest)


if __name__ == "__main__":
    unittest.main()
