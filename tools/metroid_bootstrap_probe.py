#!/usr/bin/env python3
"""Read-only bootstrap verifier for the known Metroid Fusion AMTE study ROM.

This script validates ROM identity and decodes a narrow set of ARM/Thumb branch
encodings and literal pointers. It is not a general disassembler, does not
modify the ROM, and does not replace the targeted Ghidra audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROM_BASE = 0x08000000
EXPECTED_SIZE = 8 * 1024 * 1024
EXPECTED_GAME_CODE = "AMTE"
EXPECTED_SHA256 = "a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8"

EXPECTED_ARM_WORDS = {
    0x00C0: 0xE3A00012,  # mov r0, #0x12
    0x00C4: 0xE129F000,  # msr CPSR_cf, r0
    0x00C8: 0xE59FD028,  # ldr sp, [pc, #0x28]
    0x00CC: 0xE3A0001F,  # mov r0, #0x1f
    0x00D0: 0xE129F000,  # msr CPSR_cf, r0
    0x00D4: 0xE59FD018,  # ldr sp, [pc, #0x18]
    0x00D8: 0xE59F101C,  # ldr r1, [pc, #0x1c]
    0x00DC: 0xE28F0020,  # adr r0, 0x08000104
    0x00E0: 0xE5810000,  # str r0, [r1]
    0x00E4: 0xE59F1014,  # ldr r1, [pc, #0x14]
    0x00E8: 0xE1A0E00F,  # mov lr, pc
    0x00EC: 0xE12FFF11,  # bx r1
    0x00F0: 0xEAFFFFF2,  # b 0x080000c0
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], "little")


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 4], "little")


def sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def decode_arm_b(word: int, address: int) -> dict[str, Any]:
    """Decode an ARM A32 B/BL immediate using the ARM PC+8 rule."""
    if ((word >> 25) & 0b111) != 0b101:
        raise ValueError(f"Not an ARM B/BL immediate: 0x{word:08X}")
    imm24 = sign_extend(word & 0x00FFFFFF, 24)
    offset = imm24 << 2
    target = (address + 8 + offset) & 0xFFFFFFFF
    return {
        "mnemonic": "BL" if (word & (1 << 24)) else "B",
        "address": f"0x{address:08X}",
        "word_le": f"0x{word:08X}",
        "signed_offset": offset,
        "target_address": f"0x{target:08X}",
    }


def decode_thumb_bl(first: int, second: int, address: int) -> int:
    """Decode the ARMv4T two-halfword Thumb BL pair."""
    if (first & 0xF800) != 0xF000 or (second & 0xF800) != 0xF800:
        raise ValueError(
            f"Not an ARMv4T Thumb BL pair: 0x{first:04X}, 0x{second:04X}"
        )
    high = sign_extend(first & 0x07FF, 11) << 12
    low = (second & 0x07FF) << 1
    return (address + 4 + high + low) & 0xFFFFFFFF


def decode_thumb_b(halfword: int, address: int) -> int:
    """Decode a Thumb unconditional B (E000-E7FF)."""
    if (halfword & 0xF800) != 0xE000:
        raise ValueError(f"Not a Thumb unconditional B: 0x{halfword:04X}")
    offset = sign_extend(halfword & 0x07FF, 11) << 1
    return (address + 4 + offset) & 0xFFFFFFFF


def hex32(value: int) -> str:
    return f"0x{value & 0xFFFFFFFF:08X}"


def analyze(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"ROM file not found: {path}")

    data = path.read_bytes()
    if len(data) != EXPECTED_SIZE:
        raise ValueError(
            f"Expected {EXPECTED_SIZE} bytes (8 MiB), got {len(data)}."
        )

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(
            "SHA-256 does not match the recorded AMTE study image. "
            f"Expected {EXPECTED_SHA256}, got {digest}. "
            "Do not reuse these offsets on a different ROM."
        )

    game_code = data[0xAC:0xB0].decode("ascii", errors="replace")
    if game_code != EXPECTED_GAME_CODE:
        raise ValueError(f"Expected game code AMTE, got {game_code!r}.")

    entry_word = read_u32(data, 0)
    entry = decode_arm_b(entry_word, ROM_BASE)

    arm_checks = []
    for offset, expected in EXPECTED_ARM_WORDS.items():
        actual = read_u32(data, offset)
        arm_checks.append({
            "file_offset": f"0x{offset:04X}",
            "bus_address": hex32(ROM_BASE + offset),
            "word_le": f"0x{actual:08X}",
            "expected_word_le": f"0x{expected:08X}",
            "matches_expected": actual == expected,
        })

    # ARM LDR literal at 0x080000E4: PC is instruction address + 8.
    ldr_e4 = read_u32(data, 0xE4)
    ldr_imm = ldr_e4 & 0xFFF
    ldr_add = bool(ldr_e4 & (1 << 23))
    ldr_literal_address = ROM_BASE + 0xE4 + 8 + (ldr_imm if ldr_add else -ldr_imm)
    ldr_literal_offset = ldr_literal_address - ROM_BASE

    adr_dc = read_u32(data, 0xDC)
    adr_imm = adr_dc & 0xFFF
    adr_add = bool(adr_dc & (1 << 23))
    irq_handler_address = ROM_BASE + 0xDC + 8 + (adr_imm if adr_add else -adr_imm)

    system_stack = read_u32(data, 0xF4)
    irq_stack = read_u32(data, 0xF8)
    irq_vector_address = read_u32(data, 0xFC)
    thumb_entry_pointer = read_u32(data, 0x100)

    if not (0 <= ldr_literal_offset <= len(data) - 4):
        raise ValueError("The PC-relative LDR literal falls outside this ROM.")
    if ldr_literal_offset != 0x100:
        raise ValueError(
            f"Unexpected LDR literal offset: 0x{ldr_literal_offset:X}."
        )

    first_thumb = read_u16(data, 0x230)
    bl_first = read_u16(data, 0x232)
    bl_second = read_u16(data, 0x234)
    branch_halfword = read_u16(data, 0x236)

    bl_target = decode_thumb_bl(bl_first, bl_second, ROM_BASE + 0x232)
    branch_target = decode_thumb_b(branch_halfword, ROM_BASE + 0x236)

    arm_checks_ok = all(item["matches_expected"] for item in arm_checks)
    checks = {
        "sha256_matches_recorded_image": digest == EXPECTED_SHA256,
        "size_is_8_mib": len(data) == EXPECTED_SIZE,
        "game_code_is_amte": game_code == EXPECTED_GAME_CODE,
        "gba_entry_branch_targets_080000c0":
            entry["target_address"] == "0x080000C0",
        "all_recorded_arm_words_match_binary": arm_checks_ok,
        "ghidra_confirmed_arm_subset_matches_binary": all(
            item["matches_expected"] for item in arm_checks if int(item["file_offset"], 16) <= 0x00E0
        ),
        "irq_handler_adr_resolves_to_08000104": irq_handler_address == 0x08000104,
        "ldr_e4_literal_resolves_to_08000100": ldr_literal_address == 0x08000100,
        "irq_stack_literal_is_03007fa0": irq_stack == 0x03007FA0,
        "system_stack_literal_is_03007e60": system_stack == 0x03007E60,
        "irq_vector_literal_is_03007ffc": irq_vector_address == 0x03007FFC,
        "thumb_pointer_is_08000231": thumb_entry_pointer == 0x08000231,
        "thumb_bl_target_is_08000798": bl_target == 0x08000798,
        "thumb_branch_target_is_08000766": branch_target == 0x08000766,
    }

    return {
        "report_kind": "metroid_fusion_bootstrap_probe",
        "read_only": True,
        "source": str(path.resolve()),
        "rom": {
            "title": "METROID4USA",
            "game_code": game_code,
            "size_bytes": len(data),
            "sha256": digest,
        },
        "processor": {
            "target": "ARM7TDMI",
            "architecture": "ARMv4T",
            "ghidra_language": "ARM:LE:32:v4t",
            "endianness": "little",
            "analysis_scope": "targeted bootstrap windows only",
        },
        "entry": entry,
        "arm_bootstrap": {
            "ghidra_observed_range": ["0x080000C0", "0x080000E0"],
            "word_checks": arm_checks,
            "ghidra_confirmed_instruction_offsets": [
                "0x00C0", "0x00C4", "0x00C8", "0x00CC", "0x00D0",
                "0x00D4", "0x00D8", "0x00DC", "0x00E0"
            ],
            "later_arm_words_pending_ghidra_confirmation": [
                "0x00E4", "0x00E8", "0x00EC", "0x00F0"
            ],
            "mode_and_stack_setup": {
                "irq_mode_value": "0x12",
                "irq_stack_literal_file_offset": "0x00F8",
                "irq_stack_pointer": hex32(irq_stack),
                "system_mode_value": "0x1F",
                "system_stack_literal_file_offset": "0x00F4",
                "system_stack_pointer": hex32(system_stack),
            },
            "interrupt_vector_setup": {
                "literal_file_offset": "0x00FC",
                "vector_address": hex32(irq_vector_address),
                "handler_address_from_ADR": hex32(irq_handler_address),
                "store_instruction_address": "0x080000E0",
                "handler_code_analysis": "separate ARM window scheduled by Ghidra audit",
            },
            "interworking": {
                "ldr_instruction_address": "0x080000E4",
                "ldr_literal_address": hex32(ldr_literal_address),
                "ldr_literal_file_offset": f"0x{ldr_literal_offset:04X}",
                "thumb_entry_pointer": hex32(thumb_entry_pointer),
                "thumb_code_address": hex32(thumb_entry_pointer & ~1),
                "mov_lr_pc_address": "0x080000E8",
                "return_address": hex32(ROM_BASE + 0xF0),
                "bx_instruction_address": "0x080000EC",
                "post_return_arm_branch": "0x080000F0 -> 0x080000C0",
            },
        },
        "thumb_control_flow_from_encodings": {
            "entry_file_offset": "0x0230",
            "entry_bytes": data[0x230:0x238].hex(" ").upper(),
            "first_halfword": f"0x{first_thumb:04X}",
            "first_instruction_note": "Ghidra Thumb audit will decode this instruction.",
            "bl_pair": {
                "file_offset": "0x0232",
                "halfwords": [f"0x{bl_first:04X}", f"0x{bl_second:04X}"],
                "computed_target": hex32(bl_target),
                "status": "ARMv4T Thumb encoding calculation; verify in Ghidra output",
            },
            "unconditional_branch": {
                "file_offset": "0x0236",
                "halfword": f"0x{branch_halfword:04X}",
                "computed_target": hex32(branch_target),
                "status": "Thumb encoding calculation; verify in Ghidra output",
            },
            "windows_for_ghidra": [
                {"mode": "Thumb", "start": "0x08000230", "end": "0x08000237"},
                {"mode": "Thumb", "start": "0x08000766", "end": "0x08000785"},
                {"mode": "Thumb", "start": "0x08000798", "end": "0x080007B7"},
            ],
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "limitations": [
            "This is a narrow byte-level verifier, not a general ARM/Thumb disassembler.",
            "Thumb call and branch destinations are computed from instruction encodings and must be confirmed by the Ghidra Thumb audit.",
            "No execution emulation, full-ROM disassembly, asset extraction, patching, or ROM modification is performed.",
            "Do not transfer these findings to another ROM revision or hash.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only verifier for the recorded Metroid Fusion AMTE bootstrap."
    )
    parser.add_argument("rom", type=Path, help="Path to the local AMTE ROM")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path")
    args = parser.parse_args()

    try:
        report = analyze(args.rom)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    if args.json:
        sys.stdout.write(encoded)
    elif args.output:
        print(f"Report written to: {args.output}")
        print(f"All checks passed: {report['all_checks_pass']}")
    else:
        sys.stdout.write(encoded)

    return 0 if report["all_checks_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
