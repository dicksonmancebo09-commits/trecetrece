#!/usr/bin/env python3
"""Read-only scanner and BIOS LZ77 (0x10) extractor/compressor for GBA data.

This tool never edits a ROM in place. Extraction writes a separate output file;
compression accepts a standalone input file and writes a new LZ77 stream.

Scan results are candidates, not proof of an actual game asset. Verify offsets
against pointers/tables and inspect the decoded content before integrating it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

DEFAULT_MAX_OUTPUT = 4 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decompress_lz77(
    data: bytes | bytearray | memoryview,
    offset: int = 0,
    *,
    max_output_size: int = DEFAULT_MAX_OUTPUT,
) -> tuple[bytes, int]:
    """Decode BIOS LZ77 type 0x10; return decoded bytes and consumed length."""
    if offset < 0 or offset + 4 > len(data):
        raise ValueError("LZ77 header is outside input bounds")
    if data[offset] != 0x10:
        raise ValueError(f"expected type 0x10 at 0x{offset:X}, found 0x{data[offset]:02X}")
    expected = int(data[offset + 1]) | (int(data[offset + 2]) << 8) | (int(data[offset + 3]) << 16)
    if expected == 0:
        raise ValueError("declared decompressed size is zero")
    if max_output_size < 1 or expected > max_output_size:
        raise ValueError(f"declared output size {expected} exceeds limit {max_output_size}")

    cursor = offset + 4
    out = bytearray()
    while len(out) < expected:
        if cursor >= len(data):
            raise ValueError(f"truncated flags byte at 0x{cursor:X}")
        flags = int(data[cursor])
        cursor += 1
        for bit in range(7, -1, -1):
            if len(out) >= expected:
                break
            if flags & (1 << bit):
                if cursor + 2 > len(data):
                    raise ValueError(f"truncated back-reference at 0x{cursor:X}")
                b1, b2 = int(data[cursor]), int(data[cursor + 1])
                cursor += 2
                length = (b1 >> 4) + 3
                distance = (((b1 & 0x0F) << 8) | b2) + 1
                if distance > len(out):
                    raise ValueError(
                        f"invalid distance {distance} with only {len(out)} output bytes"
                    )
                for _ in range(min(length, expected - len(out))):
                    out.append(out[-distance])
            else:
                if cursor >= len(data):
                    raise ValueError(f"truncated literal at 0x{cursor:X}")
                out.append(int(data[cursor]))
                cursor += 1
    return bytes(out), cursor - offset


def _insert_position(data: bytes, buckets: dict[bytes, list[int]], pos: int) -> None:
    if pos + 2 < len(data):
        buckets.setdefault(data[pos:pos + 3], []).append(pos)


def compress_lz77(data: bytes, *, max_candidates: int = 128) -> bytes:
    """Encode bytes as a valid GBA BIOS LZ77 0x10 stream using greedy matches."""
    size = len(data)
    if size == 0:
        raise ValueError("cannot encode an empty stream")
    if size > 0xFFFFFF:
        raise ValueError("GBA LZ77 header supports at most 0xFFFFFF bytes")
    if max_candidates < 1:
        raise ValueError("max_candidates must be >= 1")

    out = bytearray((0x10, size & 0xFF, (size >> 8) & 0xFF, (size >> 16) & 0xFF))
    buckets: dict[bytes, list[int]] = {}
    pos = 0
    while pos < size:
        flags_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(7, -1, -1):
            if pos >= size:
                break
            best_len = best_distance = 0
            if pos + 2 < size:
                positions = buckets.get(data[pos:pos + 3], [])
                checked = 0
                for candidate in reversed(positions):
                    distance = pos - candidate
                    if distance > 4096:
                        break
                    if distance <= 0:
                        continue
                    checked += 1
                    limit = min(18, size - pos)
                    length = 3
                    while length < limit and data[candidate + length] == data[pos + length]:
                        length += 1
                    if length > best_len:
                        best_len, best_distance = length, distance
                        if length == limit:
                            break
                    if checked >= max_candidates:
                        break
            if best_len >= 3:
                flags |= 1 << bit
                disp = best_distance - 1
                out.append(((best_len - 3) << 4) | ((disp >> 8) & 0x0F))
                out.append(disp & 0xFF)
                end = pos + best_len
                while pos < end:
                    _insert_position(data, buckets, pos)
                    pos += 1
            else:
                out.append(data[pos])
                _insert_position(data, buckets, pos)
                pos += 1
        out[flags_at] = flags
    return bytes(out)


def scan_lz77(
    data: bytes,
    *,
    alignment: int = 4,
    min_output_size: int = 32,
    max_output_size: int = DEFAULT_MAX_OUTPUT,
    max_candidates: int = 100_000,
) -> list[dict[str, Any]]:
    """Find plausible streams at aligned offsets. The result is heuristic."""
    if alignment < 1:
        raise ValueError("alignment must be >= 1")
    if min_output_size < 1:
        raise ValueError("min_output_size must be >= 1")
    if max_output_size < min_output_size:
        raise ValueError("max_output_size must be >= min_output_size")
    if max_candidates < 1:
        raise ValueError("max_candidates must be >= 1")

    rows: list[dict[str, Any]] = []
    checked = 0
    start = 0
    while start + 4 <= len(data):
        offset = data.find(b"\x10", start)
        if offset < 0:
            break
        start = offset + 1
        if offset % alignment:
            continue
        declared = data[offset + 1] | (data[offset + 2] << 8) | (data[offset + 3] << 16)
        if not min_output_size <= declared <= max_output_size:
            continue
        checked += 1
        if checked > max_candidates:
            break
        try:
            decoded, consumed = decompress_lz77(data, offset, max_output_size=max_output_size)
        except ValueError:
            continue
        rows.append({
            "offset": offset,
            "offset_hex": f"0x{offset:X}",
            "declared_output_bytes": declared,
            "compressed_bytes_consumed": consumed,
            "compression_ratio": round(consumed / declared, 4),
            "decoded_sha256": sha256_bytes(decoded),
        })
    return rows


def read_file(path: Path) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_bytes()


def command_extract(args: argparse.Namespace) -> int:
    source = read_file(args.input)
    decoded, consumed = decompress_lz77(source, args.offset, max_output_size=args.max_output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(decoded)
    print(json.dumps({
        "mode": "extract-only",
        "source": str(args.input.resolve()),
        "source_size_bytes": len(source),
        "source_sha256": sha256_bytes(source),
        "offset": args.offset,
        "offset_hex": f"0x{args.offset:X}",
        "compressed_bytes_consumed": consumed,
        "decoded_size_bytes": len(decoded),
        "decoded_sha256": sha256_bytes(decoded),
        "output": str(args.output.resolve()),
        "rom_modified": False,
    }, indent=2, ensure_ascii=False))
    return 0


def command_scan(args: argparse.Namespace) -> int:
    data = read_file(args.rom)
    candidates = scan_lz77(
        data,
        alignment=args.alignment,
        min_output_size=args.min_output,
        max_output_size=args.max_output,
        max_candidates=args.max_candidates,
    )
    result = {
        "mode": "read-only-scan",
        "rom": str(args.rom.resolve()),
        "rom_size_bytes": len(data),
        "rom_sha256": sha256_bytes(data),
        "alignment": args.alignment,
        "min_output_size": args.min_output,
        "max_output_size": args.max_output,
        "candidate_count": len(candidates),
        "warning": "Candidates are heuristic; verify pointers and decoded content before treating a match as a real asset.",
        "candidates": candidates,
    }
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


def command_compress(args: argparse.Namespace) -> int:
    source = read_file(args.input)
    encoded = compress_lz77(source, max_candidates=args.max_candidates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    decoded, consumed = decompress_lz77(encoded, max_output_size=max(len(source), 1))
    if decoded != source or consumed != len(encoded):
        raise ValueError("internal round-trip verification failed")
    print(json.dumps({
        "mode": "compress-to-new-file",
        "input": str(args.input.resolve()),
        "input_size_bytes": len(source),
        "input_sha256": sha256_bytes(source),
        "output": str(args.output.resolve()),
        "output_size_bytes": len(encoded),
        "output_sha256": sha256_bytes(encoded),
        "ratio": round(len(encoded) / len(source), 4),
        "round_trip_verified": True,
        "rom_modified": False,
    }, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect GBA BIOS LZ77 type 0x10 streams.")
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="extract a stream at a known file offset")
    extract.add_argument("input", type=Path, help="ROM or binary resource containing the stream")
    extract.add_argument("--offset", required=True, type=lambda value: int(value, 0), help="file offset, e.g. 0x123456")
    extract.add_argument("--output", required=True, type=Path, help="destination file for decoded bytes")
    extract.add_argument("--max-output", type=int, default=DEFAULT_MAX_OUTPUT, help="maximum decoded size (default: 4 MiB)")
    extract.set_defaults(func=command_extract)

    scan = sub.add_parser("scan", help="find plausible aligned streams without modifying the ROM")
    scan.add_argument("rom", type=Path)
    scan.add_argument("--alignment", type=int, default=4, help="candidate alignment (default: 4; use 1 for byte-wise scan)")
    scan.add_argument("--min-output", type=int, default=32, help="minimum declared decompressed size")
    scan.add_argument("--max-output", type=int, default=DEFAULT_MAX_OUTPUT, help="maximum declared decompressed size")
    scan.add_argument("--max-candidates", type=int, default=100_000, help="maximum candidate offsets tested")
    scan.add_argument("--report", type=Path, help="optional JSON report destination")
    scan.set_defaults(func=command_scan)

    compress = sub.add_parser("compress", help="compress a standalone file to a new LZ77 stream")
    compress.add_argument("input", type=Path)
    compress.add_argument("--output", required=True, type=Path)
    compress.add_argument("--max-candidates", type=int, default=128, help="match candidates tested per position")
    compress.set_defaults(func=command_compress)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError) as exc:
        print(f"lz77_tool: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
