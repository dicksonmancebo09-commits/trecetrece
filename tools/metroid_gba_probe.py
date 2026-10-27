#!/usr/bin/env python3
"""Read-only metadata probe for a Game Boy Advance ROM.

It does not disassemble or modify the input. Use the output as a first-pass
identity/header check, not as proof that the ROM is intact or safe to run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROM_BASE = 0x08000000
HEADER_MIN_SIZE = 0xC0
HEADER_TITLE_START = 0xA0
HEADER_CODE_START = 0xAC
HEADER_MAKER_START = 0xB0
HEADER_FIXED_OFFSET = 0xB2
HEADER_VERSION_OFFSET = 0xBC
HEADER_CHECKSUM_OFFSET = 0xBD

CONDITIONS = [
    "EQ", "NE", "CS/HS", "CC/LO", "MI", "PL", "VS", "VC",
    "HI", "LS", "GE", "LT", "GT", "LE", "AL", "NV",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_ascii(value: bytes) -> str:
    return "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in value).strip()


def decode_arm_branch(word: int, address: int = ROM_BASE) -> dict[str, Any] | None:
    """Decode an ARM B/BL immediate (not Thumb); return None for other opcodes."""
    if ((word >> 25) & 0b111) != 0b101:
        return None
    immediate = word & 0x00FFFFFF
    if immediate & 0x00800000:
        immediate -= 1 << 24
    offset = immediate << 2
    link = bool((word >> 24) & 1)
    target = (address + 8 + offset) & 0xFFFFFFFF
    return {
        "instruction_set": "ARM (32-bit)",
        "mnemonic": "BL" if link else "B",
        "condition": CONDITIONS[(word >> 28) & 0xF],
        "instruction_word_le": f"0x{word:08X}",
        "address": f"0x{address:08X}",
        "signed_offset": offset,
        "target_address": f"0x{target:08X}",
        "target_file_offset": target - ROM_BASE if target >= ROM_BASE else None,
    }


def analyze_bytes(data: bytes, source_name: str = "<memory>", sha256: str | None = None) -> dict[str, Any]:
    if len(data) < HEADER_MIN_SIZE:
        raise ValueError(
            f"File is too small for a complete GBA header: {len(data)} bytes; "
            f"need at least {HEADER_MIN_SIZE}."
        )

    title = clean_ascii(data[HEADER_TITLE_START:HEADER_CODE_START])
    game_code = clean_ascii(data[HEADER_CODE_START:HEADER_MAKER_START])
    maker_code = clean_ascii(data[HEADER_MAKER_START:HEADER_FIXED_OFFSET])
    complement_actual = data[HEADER_CHECKSUM_OFFSET]
    complement_expected = (-sum(data[0xA0:HEADER_CHECKSUM_OFFSET]) - 0x19) & 0xFF
    entry_word = int.from_bytes(data[0:4], "little")
    branch = decode_arm_branch(entry_word)
    if branch:
        offset = branch["target_file_offset"]
        branch["target_inside_file"] = isinstance(offset, int) and 0 <= offset < len(data)
    else:
        branch = {
            "instruction_set": "undetermined",
            "instruction_word_le": f"0x{entry_word:08X}",
            "note": "First word is not an ARM B/BL immediate according to the simple decoder.",
        }

    return {
        "probe": "metroid_gba_probe",
        "source": source_name,
        "read_only": True,
        "size_bytes": len(data),
        "size_mib": round(len(data) / (1024 * 1024), 3),
        "sha256": sha256 or hashlib.sha256(data).hexdigest(),
        "gba": {
            "title": title,
            "game_code": game_code,
            "maker_code": maker_code,
            "fixed_header_byte": f"0x{data[HEADER_FIXED_OFFSET]:02X}",
            "software_version": data[HEADER_VERSION_OFFSET],
            "header_complement_actual": f"0x{complement_actual:02X}",
            "header_complement_expected": f"0x{complement_expected:02X}",
            "header_complement_valid": complement_actual == complement_expected,
            "entry_word_le": f"0x{entry_word:08X}",
            "entry_branch": branch,
            "rom_bus_base": f"0x{ROM_BASE:08X}",
            "offset_to_bus_address_rule": "virtual_address = 0x08000000 + file_offset for the cartridge ROM window",
        },
        "identification": {
            "looks_like_metroid_fusion_usa_australia": game_code == "AMTE",
            "warning": "Header fields and checksum are clues, not cryptographic proof of authenticity or completeness.",
        },
        "warnings": [
            "This probe checks metadata only; it does not disassemble code or decode compressed data.",
            "GBA code uses ARM7TDMI/ARMv4T with ARM and Thumb states. Validate code in Ghidra with an appropriate language and confirmed execution mode.",
            "Do not upload commercial ROMs, ROM-derived binaries, or patches to the public repository.",
        ],
    }


def analyze_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Input ROM does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a regular file: {path}")
    size = path.stat().st_size
    if size < HEADER_MIN_SIZE:
        raise ValueError(f"File is too small for a GBA header ({size} bytes): {path}")
    with path.open("rb") as stream:
        data = stream.read()
    return analyze_bytes(data, str(path), sha256_file(path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only metadata probe for a GBA ROM; does not perform reverse engineering."
    )
    parser.add_argument("rom", type=Path, help="Path to a ROM that you are authorized to inspect")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--output", type=Path, help="Write report JSON to this path (never writes to the ROM)")
    args = parser.parse_args()

    try:
        report = analyze_file(args.rom)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    if args.json or not args.output:
        sys.stdout.write(encoded)
    else:
        print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
