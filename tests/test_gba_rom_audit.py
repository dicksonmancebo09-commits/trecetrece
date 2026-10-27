from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "gba_rom_audit.py"
SPEC = importlib.util.spec_from_file_location("gba_rom_audit", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def synthetic_gba(title: bytes = b"TEST ROM", code: bytes = b"TEST", size: int = 0x200) -> bytes:
    data = bytearray(size)
    data[0xA0:0xAC] = title[:12].ljust(12, b"\0")
    data[0xAC:0xB0] = code[:4].ljust(4, b"\0")
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBC] = 0
    data[0xBD] = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return bytes(data)


class TestGbaRomAudit(unittest.TestCase):
    def test_header_complement(self):
        info = audit.header_info(synthetic_gba(), "synthetic.gba")
        self.assertTrue(info["header"]["complement_valid"])
        self.assertEqual(info["header"]["title"], "TEST ROM")
        self.assertEqual(info["header"]["game_code"], "TEST")

    def test_changed_ranges_counts_bytes_and_groups(self):
        before = bytes(64)
        after = bytearray(before)
        for offset in (1, 2, 10, 30):
            after[offset] = 0xAA
        count, ranges = audit.changed_ranges(before, bytes(after))
        self.assertEqual(count, 4)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]["start"], 1)
        self.assertEqual(ranges[0]["end_exclusive"], 11)
        self.assertEqual(ranges[0]["changed_bytes"], 3)
        self.assertEqual(ranges[1]["start"], 30)

    def test_gba_lz77_literal_stream_decodes(self):
        stream = bytes([0x10, 0x03, 0x00, 0x00, 0x00, ord("A"), ord("B"), ord("C")])
        decoded, consumed = audit.gba_lz77_decompress(stream)
        self.assertEqual(decoded, b"ABC")
        self.assertEqual(consumed, len(stream))

    def test_gba_lz77_rejects_truncated_stream(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            audit.gba_lz77_decompress(bytes([0x10, 0x03, 0x00, 0x00, 0x00, ord("A")]))

    def test_room_rle_map_decodes_interleaved_lanes(self):
        # 2x2 map. Lane 0 contains [1, 2, 3, 4]; lane 1 contains four zero high bytes.
        stream = bytes([
            2, 2,
            1, 4, 1, 2, 3, 4, 0,
            1, 4, 0, 0, 0, 0, 0
        ])
        width, height, values, consumed = audit.gba_room_rle_decompress_map(
            stream, 0, len(stream)
        )
        self.assertEqual((width, height), (2, 2))
        self.assertEqual(values, [1, 2, 3, 4])
        self.assertEqual(consumed, len(stream))

    def test_room_rle_map_rejects_truncated_run(self):
        stream = bytes([2, 2, 1, 4, 1, 2])
        with self.assertRaisesRegex(ValueError, "truncated"):
            audit.gba_room_rle_decompress_map(stream, 0, len(stream))

    def test_no_changes(self):
        data = synthetic_gba()
        count, ranges = audit.changed_ranges(data, data)
        self.assertEqual(count, 0)
        self.assertEqual(ranges, [])

    def test_audit_profiles_check_expected_bytes_and_protected_ranges(self):
        base = bytearray(synthetic_gba(size=512))
        target = bytearray(base)
        target[0x120:0x124] = bytes.fromhex("78563412")
        target[0x130:0x134] = (0x08000180).to_bytes(4, "little")
        target[0x150:0x158] = bytes([0x10, 0x03, 0x00, 0x00, 0x00, ord("A"), ord("B"), ord("C")])
        target_path_bytes = bytes(target)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base_path = root / "base.gba"
            target_path = root / "candidate.gba"
            config_path = root / "config.json"
            report_path = root / "audit.json"
            base_path.write_bytes(base)
            target_path.write_bytes(target_path_bytes)
            config_path.write_text(json.dumps({
                "profiles": {
                    "test": {
                        "size_bytes": 512,
                        "title": "TEST ROM",
                        "game_code": "TEST",
                        "header_complement": f"0x{target[0xBD]:02X}",
                        "expected_bytes": [{"offset": "0x120", "bytes_le": "78563412", "description": "test pointer"}],
                        "pointer_checks": [{
                            "file_offset": "0x130",
                            "expected_target_bus_address": "0x08000180",
                            "purpose": "synthetic pointer test"
                        }],
                        "resource_ranges": [{
                            "name": "synthetic-lz77",
                            "offset": "0x150",
                            "used_bytes": 8,
                            "reserved_bytes": 16,
                            "encoding": "gba_lz77",
                            "expected_uncompressed_bytes": 3
                        }],
                        "must_match_reference_ranges": [{"offset": "0x100", "length": "0x10", "description": "reserved bytes"}]
                    }
                }
            }), encoding="utf-8")
            import argparse
            args = argparse.Namespace(
                config=config_path,
                profile="test",
                rom=target_path,
                baseline=base_path,
                report=report_path,
                ignore_profile_sha=False
            )
            report = audit.run(args)
            self.assertEqual(report["errors"], [], msg=json.dumps(report["errors"], indent=2))
            self.assertTrue(report["summary"]["passed"])
            self.assertEqual(report["delta"]["changed_byte_count"], 13)
            self.assertEqual(report["resources"][0]["decoded_bytes"], 3)
            self.assertEqual(report["pointer_checks"][0]["actual_target"], "0x08000180")
            self.assertTrue(report["pointer_checks"][0]["target_within_rom"])
            self.assertTrue(report_path.parent.exists())

    def test_invalid_expected_bytes_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rom_path = root / "candidate.gba"
            cfg_path = root / "config.json"
            rom = synthetic_gba(size=512)
            rom_path.write_bytes(rom)
            cfg_path.write_text(json.dumps({
                "profiles": {
                    "test": {
                        "size_bytes": 512,
                        "expected_bytes": [{"offset": "0x120", "bytes_le": "ffffffff"}]
                    }
                }
            }), encoding="utf-8")
            import argparse
            args = argparse.Namespace(
                config=cfg_path,
                profile="test",
                rom=rom_path,
                baseline=None,
                report=None,
                ignore_profile_sha=False
            )
            report = audit.run(args)
            self.assertFalse(report["summary"]["passed"])
            self.assertEqual(report["summary"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
