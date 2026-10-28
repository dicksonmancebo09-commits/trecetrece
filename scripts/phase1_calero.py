#!/usr/bin/env python3
"""Phase 1: repalette the Metroid Fusion Main Deck palette for Calero at night.

The base ROM is a pinned v0.9 visual build and is read-only. This script writes
only a new output ROM and JSON report. It does not edit tiles, maps, code,
pointers, collision data, sprites, or the source file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

# Paths are relative to the repository root; override them on the command line
# if the local working folder uses a different layout.
BASE_ROM = Path("roms/fusion.gba")
BUILD_ROM = Path("build/sector_cero_fase1.gba")
REPORT = Path("build/fase1_report.json")

ROM_BASE = 0x08000000
ROM_SIZE_BYTES = 8 * 1024 * 1024
EXPECTED_BASE_SHA256 = "54f3291e54fdca088d440ef2dd51f41dc2c80b17c195956f633660ab790e3b00"
EXPECTED_GAME_CODE = "AMTE"
EXPECTED_TITLE = "METROID4USA"
PALETTE_TABLE_OFFSET = 0x46B494
PALETTE_ROW_INDEX = 1  # Bank 0 is all-zero/reserved in the measured v0.9 palette table.
PALETTE_OFFSET = PALETTE_TABLE_OFFSET + PALETTE_ROW_INDEX * 32  # 0x46B4B4
PALETTE_TABLE_ROWS = 14
PALETTE_COLOR_COUNT = 16
PALETTE_BYTES = PALETTE_COLOR_COUNT * 2

# 16 entries, RGB888. Entries 0-6 preserve the colors present in the supplied
# snippet. Entries 7-15 complete the row as a first-pass Calero night palette.
# Palette pixel index 0 is transparent in GBA 4bpp; the first color entry is retained as black.
PAL_CALERO_ROW0: list[tuple[int, int, int]] = [
    (0, 0, 0),          #  0: negro base; los píxeles con índice 0 son transparentes en 4bpp
    (8, 8, 24),         #  1: noche profunda
    (40, 38, 36),       #  2: bloque de hormigón oscuro
    (72, 68, 64),       #  3: bloque de hormigón medio
    (112, 108, 100),    #  4: bloque de hormigón claro
    (48, 48, 56),       #  5: zinc oscuro
    (88, 88, 96),       #  6: zinc claro
    (124, 128, 140),   #  7: borde metálico frío
    (24, 36, 56),      #  8: sombra azul de acero
    (44, 68, 88),      #  9: pared azul gastada
    (64, 92, 108),     # 10: azul grisáceo desaturado
    (24, 56, 48),      # 11: verde urbano oscuro
    (64, 88, 68),      # 12: pintura verde gastada
    (112, 64, 48),     # 13: metal oxidado / ladrillo
    (176, 120, 56),    # 14: luz cálida de farola
    (188, 172, 144),   # 15: reflejo cálido de pared
]

PALETTE_LABELS = [
    "negro base de BG",
    "noche profunda",
    "hormigón oscuro",
    "hormigón medio",
    "hormigón claro",
    "zinc oscuro",
    "zinc claro",
    "borde metálico frío",
    "sombra azul de acero",
    "pared azul gastada",
    "azul grisáceo desaturado",
    "verde urbano oscuro",
    "pintura verde gastada",
    "metal oxidado / ladrillo",
    "luz cálida de farola",
    "reflejo cálido de pared",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rgb555(r: int, g: int, b: int) -> int:
    """Convert RGB888 to the GBA 15-bit color word (R bits 0-4, G 5-9, B 10-14)."""
    if any(not 0 <= component <= 255 for component in (r, g, b)):
        raise ValueError(f"RGB channels must be 0..255; received {(r, g, b)}")
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def from555(value: int) -> tuple[int, int, int]:
    """Convert a GBA 15-bit color word to 8-bit RGB channel values."""
    value &= 0x7FFF
    return (
        (value & 0x1F) << 3,
        ((value >> 5) & 0x1F) << 3,
        ((value >> 10) & 0x1F) << 3,
    )


def pal_row_bytes(colors_rgb: Sequence[tuple[int, int, int]]) -> bytes:
    """Encode exactly 16 RGB colors as 32 little-endian GBA palette bytes."""
    if len(colors_rgb) != PALETTE_COLOR_COUNT:
        raise ValueError(f"exactly {PALETTE_COLOR_COUNT} colors are required; got {len(colors_rgb)}")
    out = bytearray(PALETTE_BYTES)
    for index, (r, g, b) in enumerate(colors_rgb):
        struct.pack_into("<H", out, index * 2, rgb555(r, g, b))
    return bytes(out)


def decode_palette(raw: bytes, labels: Sequence[str] | None = None) -> list[dict[str, Any]]:
    if len(raw) != PALETTE_BYTES:
        raise ValueError(f"palette must be {PALETTE_BYTES} bytes; got {len(raw)}")
    colors = []
    for index in range(PALETTE_COLOR_COUNT):
        value = struct.unpack_from("<H", raw, index * 2)[0]
        colors.append({
            "index": index,
            "label": labels[index] if labels is not None else f"original color index {index}",
            "word_hex": f"0x{value:04X}",
            "rgb888": list(from555(value)),
        })
    return colors


def header_info(data: bytes) -> dict[str, Any]:
    if len(data) < 0xC0:
        raise ValueError(f"file is too short for a complete GBA header: {len(data)} bytes")
    title = data[0xA0:0xAC].split(b"\0", 1)[0].decode("ascii", errors="replace").strip()
    code = data[0xAC:0xB0].decode("ascii", errors="replace")
    maker = data[0xB0:0xB2].decode("ascii", errors="replace")
    actual = data[0xBD]
    expected = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return {
        "title": title,
        "game_code": code,
        "maker_code": maker,
        "size_bytes": len(data),
        "header_complement_actual": f"0x{actual:02X}",
        "header_complement_expected": f"0x{expected:02X}",
        "header_complement_valid": actual == expected,
    }


def validate_base(data: bytes, expected_sha256: str) -> dict[str, Any]:
    """Fail closed unless the exact expected v0.9 ROM is supplied."""
    if len(data) != ROM_SIZE_BYTES:
        raise ValueError(f"unexpected ROM size: expected {ROM_SIZE_BYTES} bytes, got {len(data)}")
    header = header_info(data)
    if header["title"] != EXPECTED_TITLE:
        raise ValueError(f"unexpected ROM title: expected {EXPECTED_TITLE!r}, got {header['title']!r}")
    if header["game_code"] != EXPECTED_GAME_CODE:
        raise ValueError(f"unexpected game code: expected {EXPECTED_GAME_CODE}, got {header['game_code']}")
    if not header["header_complement_valid"]:
        raise ValueError("base ROM header complement checksum is invalid")
    actual_sha = sha256_bytes(data)
    expected_sha = expected_sha256.strip().lower()
    if len(expected_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_sha):
        raise ValueError("--expected-base-sha256 must be a 64-character hexadecimal SHA-256")
    if actual_sha.lower() != expected_sha:
        raise ValueError(
            "base ROM SHA-256 mismatch; refusing to guess which revision this is. "
            f"Expected {expected_sha}; got {actual_sha}."
        )
    palette_table_bytes = PALETTE_TABLE_ROWS * PALETTE_BYTES
    if PALETTE_TABLE_OFFSET < 0 or PALETTE_TABLE_OFFSET + palette_table_bytes > len(data):
        raise ValueError("tileset palette table lies outside ROM bounds")
    if PALETTE_OFFSET < PALETTE_TABLE_OFFSET or PALETTE_OFFSET + PALETTE_BYTES > PALETTE_TABLE_OFFSET + palette_table_bytes:
        raise ValueError("selected palette row lies outside the tileset palette table")
    bank0 = data[PALETTE_TABLE_OFFSET:PALETTE_TABLE_OFFSET + PALETTE_BYTES]
    if any(bank0):
        raise ValueError(
            f"expected documented all-zero/reserved bank 0 at 0x{PALETTE_TABLE_OFFSET:X}; "
            "the base revision or resource mapping may differ"
        )
    existing = data[PALETTE_OFFSET:PALETTE_OFFSET + PALETTE_BYTES]
    words = struct.unpack("<16H", existing)
    if sum(word != 0 for word in words) < 8 or len(set(words)) < 8:
        raise ValueError(
            f"palette row {PALETTE_ROW_INDEX} at 0x{PALETTE_OFFSET:X} looks blank or implausible; refusing to patch"
        )
    if any(word & 0x8000 for word in words):
        raise ValueError(
            f"0x{PALETTE_OFFSET:X} does not look like a raw 15-bit palette: at least one word has bit 15 set"
        )
    return {
        "sha256": actual_sha,
        "header": header,
        "palette_before_hex": existing.hex(),
        "palette_table_bank0_hex": bank0.hex(),
        "palette_before": decode_palette(existing),
    }


def make_repalette(base: bytes, palette_bytes: bytes, offset: int = PALETTE_OFFSET) -> tuple[bytes, bytes]:
    """Return a new ROM plus old palette bytes. The input byte string is untouched."""
    if len(palette_bytes) != PALETTE_BYTES:
        raise ValueError(f"palette payload must be exactly {PALETTE_BYTES} bytes")
    if offset < 0 or offset + len(palette_bytes) > len(base):
        raise ValueError("palette offset is outside the ROM")
    old_palette = base[offset:offset + len(palette_bytes)]
    output = bytearray(base)
    output[offset:offset + len(palette_bytes)] = palette_bytes
    return bytes(output), old_palette


def atomic_write(path: Path, payload: bytes, *, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; use --force to replace it")
    handle = tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False)
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() and not force:
            raise FileExistsError(f"{path} appeared while writing; refusing to replace it")
        os.replace(temp_path, path)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def create_report(
    base: bytes,
    output: bytes,
    base_path: Path,
    output_path: Path,
    base_metadata: dict[str, Any],
    before_palette: bytes,
    palette_bytes: bytes,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    changed_palette_bytes = sum(a != b for a, b in zip(before_palette, palette_bytes))
    header_out = header_info(output)
    changed_positions = [
        PALETTE_OFFSET + index
        for index, (old_byte, new_byte) in enumerate(zip(before_palette, palette_bytes))
        if old_byte != new_byte
    ]
    changed_ranges: list[dict[str, Any]] = []
    for position in changed_positions:
        if not changed_ranges or position > changed_ranges[-1]["end_exclusive"]:
            changed_ranges.append({
                "start": position,
                "end_exclusive": position + 1,
                "start_hex": f"0x{position:X}",
                "end_exclusive_hex": f"0x{position + 1:X}",
                "changed_bytes": 1,
            })
        else:
            changed_ranges[-1]["end_exclusive"] = position + 1
            changed_ranges[-1]["end_exclusive_hex"] = f"0x{position + 1:X}"
            changed_ranges[-1]["changed_bytes"] += 1

    return {
        "tool": "phase1_calero.py",
        "phase": 1,
        "name": "Main Deck → Calero (noche urbana dominicana)",
        "mode": "dry-run" if dry_run else "build-new-rom",
        "source_rom": str(base_path),
        "source_size_bytes": len(base),
        "source_sha256": base_metadata["sha256"],
        "source_header": base_metadata["header"],
        "output_rom": str(output_path),
        "output_size_bytes": len(output),
        "output_sha256": sha256_bytes(output),
        "rom_base_bus_address": f"0x{ROM_BASE:08X}",
        "palette": {
            "purpose": "Main Deck tileset 61 palette row; row 0 is a preserved all-zero/reserved bank",
            "palette_table_offset": f"0x{PALETTE_TABLE_OFFSET:X}",
            "native_palette_bank_index": PALETTE_ROW_INDEX,
            "rom_offset": f"0x{PALETTE_OFFSET:X}",
            "bus_address": f"0x{ROM_BASE + PALETTE_OFFSET:08X}",
            "byte_length": PALETTE_BYTES,
            "entries": PALETTE_COLOR_COUNT,
            "changed_bytes_inside_palette": changed_palette_bytes,
            "before_hex": before_palette.hex(),
            "after_hex": palette_bytes.hex(),
            "before_colors": decode_palette(before_palette),
            "after_colors": decode_palette(palette_bytes, PALETTE_LABELS),
        },
        "build_delta": {
            "changed_byte_count": sum(a != b for a, b in zip(base, output)),
            "changed_range_count": len(changed_ranges),
            "changed_ranges": changed_ranges,
            "allowed_write_range": {
                "start": PALETTE_OFFSET,
                "end_exclusive": PALETTE_OFFSET + PALETTE_BYTES,
                "start_hex": f"0x{PALETTE_OFFSET:X}",
                "end_exclusive_hex": f"0x{PALETTE_OFFSET + PALETTE_BYTES:X}",
            },
            "all_bytes_outside_palette_unchanged": (
                base[:PALETTE_OFFSET] == output[:PALETTE_OFFSET]
                and base[PALETTE_OFFSET + PALETTE_BYTES:] == output[PALETTE_OFFSET + PALETTE_BYTES:]
            ),
        },
        "output_header": header_out,
        "warnings": [
            "La ROM base se lee; nunca se modifica in situ.",
            "Solo se sustituyen 32 bytes de paleta. No cambia geometría, tilemap, colisiones, código ni sprites.",
            "En tiles 4bpp GBA, el índice de píxel 0 es transparente; la entrada 0 se conserva como negro base, pero no controla por sí sola la transparencia de toda la capa.",
            "La tabla de paleta del tileset 61 empieza en 0x46B494; la fila 0 de 32 bytes está totalmente a cero en la ROM v0.9 y se conserva. Esta fase modifica la fila/banco 1 en 0x46B4B4.",
            "El render visual en mGBA sigue pendiente; revisar que la paleta retocada produce el contraste esperado y no oscurece otros cuartos que compartan el tileset 61.",
            "El informe estático no garantiza que la paleta elegida mejore la lectura visual ni que la ROM se haya probado en el emulador.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a Calero-night palette candidate without modifying the base ROM.")
    parser.add_argument("--base", type=Path, default=BASE_ROM, help=f"pinned v0.9 base ROM (default: {BASE_ROM})")
    parser.add_argument("--output", type=Path, default=BUILD_ROM, help=f"new ROM path (default: {BUILD_ROM})")
    parser.add_argument("--report", type=Path, default=REPORT, help=f"JSON report path (default: {REPORT})")
    parser.add_argument(
        "--expected-base-sha256",
        default=EXPECTED_BASE_SHA256,
        help="exact SHA-256 required for the base ROM; defaults to the known v0.9 visual build",
    )
    parser.add_argument("--dry-run", action="store_true", help="validate and report, but do not write a ROM")
    parser.add_argument("--force", action="store_true", help="allow replacing existing output/report files")
    args = parser.parse_args(argv)

    try:
        base_path = args.base.resolve()
        output_path = args.output.resolve()
        report_path = args.report.resolve()
        if base_path == output_path or base_path == report_path or output_path == report_path:
            raise ValueError("base, output ROM, and JSON report must be three distinct paths")
        existing = [report_path] + ([] if args.dry_run else [output_path])
        existing = [path for path in existing if path.exists()]
        if existing and not args.force:
            raise FileExistsError(
                "output already exists: " + ", ".join(str(path) for path in existing)
                + "; use --force to replace it"
            )

        base = base_path.read_bytes()
        base_metadata = validate_base(base, args.expected_base_sha256)
        palette_bytes = pal_row_bytes(PAL_CALERO_ROW0)
        output, before_palette = make_repalette(base, palette_bytes)

        # Guard: this phase is palette-only. Assert the output differs nowhere else.
        if output[:PALETTE_OFFSET] != base[:PALETTE_OFFSET]:
            raise AssertionError("bytes before palette range changed unexpectedly")
        if output[PALETTE_OFFSET + PALETTE_BYTES:] != base[PALETTE_OFFSET + PALETTE_BYTES:]:
            raise AssertionError("bytes after palette range changed unexpectedly")
        if header_info(output) != base_metadata["header"]:
            raise AssertionError("GBA header changed during palette-only build")

        report = create_report(
            base, output, base_path, output_path, base_metadata, before_palette, palette_bytes,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            atomic_write(output_path, output, force=args.force)
        report_payload = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        atomic_write(report_path, report_payload, force=args.force)
        print(json.dumps({
            "status": "dry-run-ok" if args.dry_run else "build-created",
            "source": str(base_path),
            "source_sha256": base_metadata["sha256"],
            "output": None if args.dry_run else str(output_path),
            "output_sha256": sha256_bytes(output),
            "report": str(report_path),
            "palette_table_offset": f"0x{PALETTE_TABLE_OFFSET:X}",
            "palette_bank_index": PALETTE_ROW_INDEX,
            "palette_offset": f"0x{PALETTE_OFFSET:X}",
            "palette_bus_address": f"0x{ROM_BASE + PALETTE_OFFSET:08X}",
            "changed_palette_bytes": report["palette"]["changed_bytes_inside_palette"],
            "all_bytes_outside_palette_unchanged": report["build_delta"]["all_bytes_outside_palette_unchanged"],
            "header_checksum_valid": report["output_header"]["header_complement_valid"],
        }, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, AssertionError, struct.error) as exc:
        print(f"phase1_calero.py: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
