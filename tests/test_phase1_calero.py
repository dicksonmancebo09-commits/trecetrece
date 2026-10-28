"""Unit tests for the guarded Calero Phase 1 palette-only ROM builder."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "phase1_calero.py"
SPEC = importlib.util.spec_from_file_location("phase1_calero", SCRIPT)
assert SPEC and SPEC.loader
phase = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(phase)


def synthetic_v09_rom() -> bytes:
    data = bytearray(phase.ROM_SIZE_BYTES)
    data[0xA0:0xAC] = b"METROID4USA\x00"
    data[0xAC:0xB0] = b"AMTE"
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBC] = 0
    data[0xBD] = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    # Palette bank 0 remains all-zero; bank 1 is a populated native palette row.
    data[phase.PALETTE_TABLE_OFFSET:phase.PALETTE_TABLE_OFFSET + phase.PALETTE_BYTES] = bytes(phase.PALETTE_BYTES)
    row1 = struct.pack("<16H", *[i * 0x101 for i in range(16)])
    data[phase.PALETTE_OFFSET:phase.PALETTE_OFFSET + phase.PALETTE_BYTES] = row1
    return bytes(data)


class Phase1CaleroTests(unittest.TestCase):
    def test_rgb555_channel_bit_layout(self):
        self.assertEqual(phase.rgb555(255, 0, 0), 0x001F)
        self.assertEqual(phase.rgb555(0, 255, 0), 0x03E0)
        self.assertEqual(phase.rgb555(0, 0, 255), 0x7C00)

    def test_rgb555_rejects_invalid_channel(self):
        with self.assertRaises(ValueError):
            phase.rgb555(-1, 0, 0)
        with self.assertRaises(ValueError):
            phase.rgb555(256, 0, 0)

    def test_palette_encodes_exactly_16_colors(self):
        encoded = phase.pal_row_bytes(phase.PAL_CALERO_ROW0)
        self.assertEqual(len(encoded), 32)
        self.assertEqual(len(phase.PAL_CALERO_ROW0), 16)
        self.assertEqual(struct.unpack_from("<H", encoded, 0)[0], 0)
        self.assertEqual(struct.unpack_from("<H", encoded, 2)[0], phase.rgb555(8, 8, 24))

    def test_palette_requires_exactly_16_colors(self):
        with self.assertRaises(ValueError):
            phase.pal_row_bytes(phase.PAL_CALERO_ROW0[:15])

    def test_make_repalette_changes_only_the_palette_region(self):
        base = bytes(range(256)) * 8
        replacement = phase.pal_row_bytes(phase.PAL_CALERO_ROW0)
        output, old = phase.make_repalette(base, replacement, offset=128)
        self.assertEqual(len(output), len(base))
        self.assertEqual(old, base[128:160])
        self.assertEqual(output[:128], base[:128])
        self.assertEqual(output[160:], base[160:])
        self.assertEqual(output[128:160], replacement)
        self.assertEqual(base[128:160], old)  # immutable original remains untouched

    def test_make_repalette_rejects_out_of_bounds_offset(self):
        with self.assertRaises(ValueError):
            phase.make_repalette(b"\x00" * 16, b"\x00" * 32, offset=4)

    def test_validate_base_accepts_exact_hash_and_header(self):
        base = synthetic_v09_rom()
        report = phase.validate_base(base, hashlib.sha256(base).hexdigest())
        self.assertEqual(report["header"]["game_code"], "AMTE")
        self.assertTrue(report["header"]["header_complement_valid"])

    def test_validate_base_rejects_wrong_hash(self):
        base = synthetic_v09_rom()
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            phase.validate_base(base, "0" * 64)

    def test_validate_base_rejects_wrong_revision_size(self):
        with self.assertRaisesRegex(ValueError, "unexpected ROM size"):
            phase.validate_base(b"\x00" * 0x200, "0" * 64)

    def test_dry_run_does_not_create_build_rom_or_modify_base(self):
        base = synthetic_v09_rom()
        base_hash = hashlib.sha256(base).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base_path = root / "roms" / "fusion.gba"
            output_path = root / "build" / "sector_cero_fase1.gba"
            report_path = root / "build" / "fase1_report.json"
            base_path.parent.mkdir(parents=True)
            base_path.write_bytes(base)
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = phase.main([
                    "--base", str(base_path),
                    "--output", str(output_path),
                    "--report", str(report_path),
                    "--expected-base-sha256", base_hash,
                    "--dry-run",
                ])
            self.assertEqual(exit_code, 0)
            self.assertFalse(output_path.exists())
            self.assertEqual(hashlib.sha256(base_path.read_bytes()).hexdigest(), base_hash)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "dry-run")
            self.assertTrue(report["build_delta"]["all_bytes_outside_palette_unchanged"])
            self.assertEqual(report["palette"]["rom_offset"], "0x46B4B4")
            self.assertEqual(report["palette"]["palette_table_offset"], "0x46B494")
            self.assertEqual(report["palette"]["native_palette_bank_index"], 1)

    def test_dry_run_refuses_wrong_base_hash_before_outputs(self):
        base = synthetic_v09_rom()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base_path = root / "fusion.gba"
            output_path = root / "candidate.gba"
            report_path = root / "report.json"
            base_path.write_bytes(base)
            with contextlib.redirect_stderr(io.StringIO()):
                exit_code = phase.main([
                    "--base", str(base_path),
                    "--output", str(output_path),
                    "--report", str(report_path),
                    "--expected-base-sha256", "0" * 64,
                    "--dry-run",
                ])
            self.assertEqual(exit_code, 2)
            self.assertFalse(output_path.exists())
            self.assertFalse(report_path.exists())
            self.assertEqual(base_path.read_bytes(), base)


if __name__ == "__main__":
    unittest.main()
