#!/usr/bin/env python3
"""Create a guarded v1.8 candidate by correcting L01_R001's BG palette bank.

This tool never overwrites the supplied v1.7 input. It verifies the exact input
SHA-256 and the full 384-record metatile table before making the smallest
length-preserving change.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_V17_SHA256 = "66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf"
EXPECTED_V18_SHA256 = "3bc764355012268d4ac6ef315bb9bb09ac0e5405d1c456bb506d1fdbe862af89"
TABLE_OFFSET = 0x7B0000
TABLE_USED_BYTES = 3074
TABLE_RESERVED_BYTES = 0x2000
TABLE_RECORDS = 384
SUBTILES_PER_RECORD = 4
HEADER_WORD = 2
OLD_PALETTE_BANK = 2
NEW_PALETTE_BANK = 3

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def change_room0_palette_bank(data: bytes) -> tuple[bytes, dict]:
    """Pure guarded transform; returns candidate bytes and an auditable report."""
    if len(data) != 0x800000:
        raise ValueError(f"Expected an 8 MiB GBA ROM, got {len(data)} bytes")
    actual_sha = sha256(data)
    if actual_sha != EXPECTED_V17_SHA256:
        raise ValueError(
            f"v1.7 SHA-256 mismatch: expected {EXPECTED_V17_SHA256}, got {actual_sha}"
        )
    if data[0xAC:0xB0] != b"LZC0" or data[0xBD] != 0x6D:
        raise ValueError("Input GBA header does not match the pinned v1.7 profile")
    if data[0xBD] != ((-sum(data[0xA0:0xBD]) - 0x19) & 0xFF):
        raise ValueError("Input GBA header complement is invalid")

    original = data[TABLE_OFFSET:TABLE_OFFSET + TABLE_USED_BYTES]
    if len(original) != TABLE_USED_BYTES:
        raise ValueError("Room-0 metatile table is truncated")
    actual_header = int.from_bytes(original[:2], "little")
    if actual_header != HEADER_WORD:
        raise ValueError(f"Unexpected room-0 metatile header: {actual_header}")
    word_count = TABLE_RECORDS * SUBTILES_PER_RECORD
    if len(original[2:]) != word_count * 2:
        raise ValueError("Room-0 metatile table has an unexpected record length")
    words = list(struct.unpack("<" + "H" * word_count, original[2:]))
    actual_banks = sorted({(word >> 12) & 0xF for word in words})
    if actual_banks != [OLD_PALETTE_BANK]:
        raise ValueError(
            f"Expected all 1,536 subtile words to use bank 2; found {actual_banks}"
        )

    patched_words = [
        (word & 0x0FFF) | (NEW_PALETTE_BANK << 12)
        for word in words
    ]
    if any((old & 0x0FFF) != (new & 0x0FFF) for old, new in zip(words, patched_words)):
        raise AssertionError("Tile index or flip bits changed unexpectedly")
    patched_table = original[:2] + struct.pack("<" + "H" * word_count, *patched_words)

    output = bytearray(data)
    output[TABLE_OFFSET:TABLE_OFFSET + TABLE_USED_BYTES] = patched_table
    # The edit is outside the GBA header checksum coverage (0xA0–0xBC).
    if output[0xBD] != data[0xBD]:
        raise AssertionError("Header checksum changed unexpectedly")
    result = bytes(output)
    result_sha = sha256(result)
    if result_sha != EXPECTED_V18_SHA256:
        raise ValueError(
            f"Candidate SHA-256 differs from pinned v1.8 output: {result_sha}"
        )
    check_words = struct.unpack("<" + "H" * word_count,
                                result[TABLE_OFFSET + 2:TABLE_OFFSET + TABLE_USED_BYTES])
    if sorted({(word >> 12) & 0xF for word in check_words}) != [NEW_PALETTE_BANK]:
        raise AssertionError("Palette bank correction did not round-trip")

    changed = sum(a != b for a, b in zip(data, result))
    if changed != word_count:
        raise AssertionError(f"Expected exactly {word_count} changed bytes, found {changed}")
    report = {
        "patch_id": "ZC_V18_ROOM0_PALETTE_BANK_FIX",
        "base_sha256": actual_sha,
        "output_sha256": result_sha,
        "size_bytes": len(result),
        "table_offset": f"0x{TABLE_OFFSET:X}",
        "table_used_bytes": TABLE_USED_BYTES,
        "table_reserved_bytes": f"0x{TABLE_RESERVED_BYTES:X}",
        "records": TABLE_RECORDS,
        "subtile_words": word_count,
        "palette_bank_before": actual_banks,
        "palette_bank_after": [NEW_PALETTE_BANK],
        "tile_index_and_flip_bits_preserved": True,
        "changed_bytes": changed,
        "header_complement_preserved": True,
        "runtime_tested": False,
    }
    return result, report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path,
                        help="Exact user-supplied v1.7 ROM")
    parser.add_argument("--output", required=True, type=Path,
                        help="New output ROM; must not exist")
    parser.add_argument("--report", type=Path,
                        help="Optional JSON report")
    args = parser.parse_args()
    if args.base.resolve() == args.output.resolve():
        raise ValueError("Output path must differ from input path")
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite output: {args.output}")
    candidate, report = change_room0_palette_bank(args.base.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(candidate)
    report["output_path"] = str(args.output.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
