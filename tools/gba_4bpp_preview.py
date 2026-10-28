#!/usr/bin/env python3
"""Render raw GBA 4bpp tile data as a grayscale PNG atlas.

The renderer is format-focused: it visualizes tile layout, not the game's true
palette. For a compressed resource, extract it first with lz77_tool.py. If the
decoded data has a 4-byte container prefix, pass --skip-bytes 4 only after
confirming that prefix from the resource format or an observed block pattern.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
import zlib
from pathlib import Path


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    body = tag + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def render_4bpp_atlas(
    data: bytes,
    output: Path,
    *,
    skip_bytes: int = 0,
    columns: int = 16,
    scale: int = 3,
    max_pixels: int = 16_000_000,
) -> dict[str, object]:
    """Render sequential 8x8 GBA 4bpp tiles (32 bytes/tile) to an RGB PNG."""
    if skip_bytes < 0 or skip_bytes > len(data):
        raise ValueError("skip_bytes is outside the input range")
    if columns < 1 or columns > 128:
        raise ValueError("columns must be between 1 and 128")
    if scale < 1 or scale > 8:
        raise ValueError("scale must be between 1 and 8")
    if max_pixels < 1:
        raise ValueError("max_pixels must be positive")

    payload = data[skip_bytes:]
    if not payload:
        raise ValueError("no tile data remains after skip_bytes")
    if len(payload) % 32:
        raise ValueError(
            f"payload has {len(payload)} bytes after skip; 4bpp tiles require a multiple of 32"
        )

    tile_count = len(payload) // 32
    rows = math.ceil(tile_count / columns)
    native_width, native_height = columns * 8, rows * 8
    width, height = native_width * scale, native_height * scale
    if width * height > max_pixels:
        raise ValueError(
            f"atlas would be {width}x{height} ({width * height:,} pixels), "
            f"exceeding max_pixels={max_pixels:,}"
        )

    palette = [(index * 17, index * 17, index * 17) for index in range(16)]
    scanlines = bytearray()
    for tile_y in range(rows):
        for pixel_y in range(8):
            native_row: list[tuple[int, int, int]] = []
            for tile_x in range(columns):
                tile_index = tile_y * columns + tile_x
                if tile_index >= tile_count:
                    native_row.extend([palette[0]] * 8)
                    continue
                tile_start = tile_index * 32 + pixel_y * 4
                for pair_x in range(4):
                    value = payload[tile_start + pair_x]
                    native_row.append(palette[value & 0x0F])
                    native_row.append(palette[(value >> 4) & 0x0F])
            rgb = b"".join(bytes(color) for color in native_row)
            scaled_rgb = b"".join(rgb[x * 3:(x + 1) * 3] * scale for x in range(native_width))
            for _ in range(scale):
                scanlines.extend(b"\x00")
                scanlines.extend(scaled_rgb)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(scanlines), level=6))
        + _png_chunk(b"IEND", b"")
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(png)

    return {
        "input_bytes": len(data),
        "skip_bytes": skip_bytes,
        "tile_data_bytes": len(payload),
        "tile_count": tile_count,
        "columns": columns,
        "rows": rows,
        "native_size": [native_width, native_height],
        "output_size": [width, height],
        "scale": scale,
        "output": str(output.resolve()),
        "png_bytes": len(png),
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "palette": "grayscale index 0..15; not the source game's palette",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render sequential GBA 4bpp tiles to a PNG atlas.")
    parser.add_argument("input", type=Path, help="raw 4bpp data file, usually produced by lz77_tool.py extract")
    parser.add_argument("--output", required=True, type=Path, help="PNG destination")
    parser.add_argument("--skip-bytes", type=int, default=0, help="bytes to skip before tile data (default: 0)")
    parser.add_argument("--columns", type=int, default=16, help="tiles per row (default: 16)")
    parser.add_argument("--scale", type=int, default=3, help="nearest-neighbor scale 1..8 (default: 3)")
    parser.add_argument("--max-pixels", type=int, default=16_000_000, help="pixel-count memory guard")
    args = parser.parse_args()
    try:
        data = args.input.read_bytes()
        result = render_4bpp_atlas(
            data,
            args.output,
            skip_bytes=args.skip_bytes,
            columns=args.columns,
            scale=args.scale,
            max_pixels=args.max_pixels,
        )
    except (OSError, ValueError) as exc:
        print(f"gba_4bpp_preview: ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
