#!/usr/bin/env python3
"""Export an indexed 8x8-tile PNG atlas to GBA 4bpp and BGR555 assets.

This exports graphics and a palette only. It deliberately does not invent a
room tilemap, change game pointers, patch a ROM, or decide BG/OBJ transparency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - exercised in CLI environments
    raise SystemExit(
        "Pillow is required. Install it with: python3 -m pip install Pillow"
    ) from exc


TILE_SIZE = 8
MAX_4BPP_COLORS = 16


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rgb_to_bgr555(rgb: tuple[int, int, int]) -> int:
    """Convert 8-bit RGB to GBA BGR555 (R in bits 0..4)."""
    r, g, b = (component >> 3 for component in rgb)
    return (b << 10) | (g << 5) | r


def pack_palette_bgr555(colors: list[tuple[int, int, int]]) -> bytes:
    if len(colors) > MAX_4BPP_COLORS:
        raise ValueError("A 4bpp palette cannot contain more than 16 colors.")
    padded = colors + [(0, 0, 0)] * (MAX_4BPP_COLORS - len(colors))
    output = bytearray()
    for color in padded:
        output.extend(rgb_to_bgr555(color).to_bytes(2, "little"))
    return bytes(output)


def _palette_rgb(image: Image.Image) -> list[tuple[int, int, int]]:
    raw = image.getpalette()
    if raw is None:
        raise ValueError("Indexed PNG has no palette.")
    colors = []
    for index in range(0, min(len(raw), 768), 3):
        colors.append((raw[index], raw[index + 1], raw[index + 2]))
    if not colors:
        raise ValueError("Indexed PNG palette is empty.")
    return colors


def read_indexed_pixels(
    image: Image.Image,
    transparent_index: int = 0,
) -> tuple[int, int, list[int], list[tuple[int, int, int]], bool]:
    """Read palette indices and map every fully transparent pixel to index 0."""
    if image.mode != "P":
        raise ValueError(
            f"Input must be an indexed PNG (mode P), got {image.mode!r}. "
            "Quantize deliberately before export; this tool will not invent a palette."
        )
    width, height = image.size
    if width == 0 or height == 0 or width % TILE_SIZE or height % TILE_SIZE:
        raise ValueError(
            f"Image dimensions must be positive multiples of 8; got {width}x{height}."
        )
    if not 0 <= transparent_index < MAX_4BPP_COLORS:
        raise ValueError("transparent_index must be between 0 and 15.")

    indices = list(image.getdata())
    palette = _palette_rgb(image)
    rgba = image.convert("RGBA")
    alpha_values = [pixel[3] for pixel in rgba.getdata()]
    if any(alpha not in (0, 255) for alpha in alpha_values):
        raise ValueError("Semi-transparent pixels are not supported; use alpha 0 or 255.")

    has_transparency = any(alpha == 0 for alpha in alpha_values)
    mapped = [
        transparent_index if alpha == 0 else index
        for index, alpha in zip(indices, alpha_values)
    ]

    used = sorted(set(mapped))
    if any(index >= MAX_4BPP_COLORS for index in used):
        raise ValueError(
            "The indexed PNG uses palette indices above 15. Remap it to a "
            "maximum of 16 explicit colors before GBA 4bpp export."
        )
    if any(index >= len(palette) for index in used):
        raise ValueError("A pixel references an undefined palette entry.")

    # GBA palette RAM always stores 16 RGB555 entries for a 4bpp bank.
    output_palette = [(0, 0, 0)] * MAX_4BPP_COLORS
    for index, color in enumerate(palette[:MAX_4BPP_COLORS]):
        output_palette[index] = color
    if has_transparency:
        output_palette[transparent_index] = (0, 0, 0)

    return width, height, mapped, output_palette, has_transparency


def encode_4bpp_tiles(indices: list[int], width: int, height: int) -> bytes:
    """Encode row-major 8x8 tiles; even x is the low nibble, odd x high nibble."""
    if width % TILE_SIZE or height % TILE_SIZE:
        raise ValueError("Width and height must be multiples of 8.")
    if len(indices) != width * height:
        raise ValueError("Pixel count does not match image dimensions.")
    if any(index < 0 or index > 15 for index in indices):
        raise ValueError("Every 4bpp pixel index must be in the range 0..15.")

    output = bytearray()
    for tile_y in range(0, height, TILE_SIZE):
        for tile_x in range(0, width, TILE_SIZE):
            for y in range(TILE_SIZE):
                row = (tile_y + y) * width + tile_x
                for x in range(0, TILE_SIZE, 2):
                    low = indices[row + x]
                    high = indices[row + x + 1]
                    output.append(low | (high << 4))
    return bytes(output)


def decode_4bpp_tiles(data: bytes, width: int, height: int) -> list[int]:
    """Inverse of encode_4bpp_tiles, used for round-trip QA."""
    expected = (width // TILE_SIZE) * (height // TILE_SIZE) * 32
    if width % TILE_SIZE or height % TILE_SIZE or len(data) != expected:
        raise ValueError("4bpp data length does not match the requested atlas size.")
    output = [0] * (width * height)
    cursor = 0
    for tile_y in range(0, height, TILE_SIZE):
        for tile_x in range(0, width, TILE_SIZE):
            for y in range(TILE_SIZE):
                row = (tile_y + y) * width + tile_x
                for x in range(0, TILE_SIZE, 2):
                    value = data[cursor]
                    cursor += 1
                    output[row + x] = value & 0x0F
                    output[row + x + 1] = (value >> 4) & 0x0F
    return output


def gba_lz77_compress(data: bytes) -> bytes:
    """Compress bytes using the GBA BIOS 0x10 LZ77 format."""
    if len(data) > 0xFFFFFF:
        raise ValueError("GBA BIOS LZ77 supports at most 0xFFFFFF output bytes.")
    header = bytes((0x10, len(data) & 0xFF, (len(data) >> 8) & 0xFF, (len(data) >> 16) & 0xFF))
    output = bytearray(header)
    positions: dict[bytes, list[int]] = {}
    cursor = 0

    def remember(position: int) -> None:
        if position + 2 >= len(data):
            return
        key = data[position:position + 3]
        bucket = positions.setdefault(key, [])
        bucket.append(position)
        # Keep the active 4 KiB window plus a small safety margin.
        cutoff = position - 4096
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)

    while cursor < len(data):
        flag_position = len(output)
        output.append(0)
        flags = 0
        payload = bytearray()

        for bit in range(8):
            if cursor >= len(data):
                break

            best_length = 0
            best_distance = 0
            if cursor + 2 < len(data):
                key = data[cursor:cursor + 3]
                candidates = positions.get(key, ())
                # Recent candidates are more likely to produce a useful match.
                for previous in reversed(candidates[-96:]):
                    distance = cursor - previous
                    if distance <= 0 or distance > 4096:
                        continue
                    max_length = min(18, len(data) - cursor)
                    length = 3
                    while length < max_length and data[previous + length] == data[cursor + length]:
                        length += 1
                    if length > best_length:
                        best_length = length
                        best_distance = distance
                        if length == max_length:
                            break

            if best_length >= 3:
                flags |= 1 << (7 - bit)
                encoded_distance = best_distance - 1
                payload.append(((best_length - 3) << 4) | ((encoded_distance >> 8) & 0x0F))
                payload.append(encoded_distance & 0xFF)
                for position in range(cursor, cursor + best_length):
                    remember(position)
                cursor += best_length
            else:
                payload.append(data[cursor])
                remember(cursor)
                cursor += 1

        output[flag_position] = flags
        output.extend(payload)

    # GBA decompression reads word-aligned streams.
    while len(output) & 3:
        output.append(0)
    return bytes(output)


def gba_lz77_decompress(data: bytes) -> bytes:
    """Small strict decoder for verifying the compressor's output."""
    if len(data) < 4 or data[0] != 0x10:
        raise ValueError("Not a GBA BIOS LZ77 0x10 stream.")
    output_size = data[1] | (data[2] << 8) | (data[3] << 16)
    output = bytearray()
    cursor = 4
    while len(output) < output_size:
        if cursor >= len(data):
            raise ValueError("Unexpected end of LZ77 flags.")
        flags = data[cursor]
        cursor += 1
        for bit in range(8):
            if len(output) >= output_size:
                break
            if flags & (1 << (7 - bit)):
                if cursor + 1 >= len(data):
                    raise ValueError("Unexpected end of LZ77 back-reference.")
                first, second = data[cursor], data[cursor + 1]
                cursor += 2
                length = (first >> 4) + 3
                distance = (((first & 0x0F) << 8) | second) + 1
                if distance > len(output):
                    raise ValueError("LZ77 back-reference precedes the output buffer.")
                for _ in range(length):
                    output.append(output[-distance])
                    if len(output) >= output_size:
                        break
            else:
                if cursor >= len(data):
                    raise ValueError("Unexpected end of LZ77 literal.")
                output.append(data[cursor])
                cursor += 1
    return bytes(output)


def export_atlas(input_path: Path, output_dir: Path, prefix: str) -> dict:
    with Image.open(input_path) as image:
        width, height, pixels, palette, has_transparency = read_indexed_pixels(image)
    raw_tiles = encode_4bpp_tiles(pixels, width, height)
    # Verify the tile order/nibble encoding before writing any output.
    if decode_4bpp_tiles(raw_tiles, width, height) != pixels:
        raise AssertionError("Internal 4bpp round-trip failed.")
    palette_bytes = pack_palette_bgr555(palette)
    compressed = gba_lz77_compress(raw_tiles)
    if gba_lz77_decompress(compressed) != raw_tiles:
        raise AssertionError("Internal GBA LZ77 round-trip failed.")

    output_dir.mkdir(parents=True, exist_ok=True)
    tiles_path = output_dir / f"{prefix}.4bpp"
    compressed_path = output_dir / f"{prefix}.4bpp.lz"
    palette_path = output_dir / f"{prefix}.bgr555.pal"
    report_path = output_dir / f"{prefix}.export.json"

    tiles_path.write_bytes(raw_tiles)
    compressed_path.write_bytes(compressed)
    palette_path.write_bytes(palette_bytes)

    report = {
        "format": "gba-4bpp-tile-atlas",
        "source": str(input_path),
        "source_sha256": sha256(input_path.read_bytes()),
        "dimensions_px": [width, height],
        "tile_dimensions_px": [8, 8],
        "tile_grid": [width // 8, height // 8],
        "tile_count": (width // 8) * (height // 8),
        "tile_order": "row-major, top-to-bottom then left-to-right",
        "nibble_order": "even x in low nibble; odd x in high nibble",
        "pixel_indices_used": sorted(set(pixels)),
        "source_transparency_present": has_transparency,
        "transparency_note": (
            "Alpha-zero pixels map to palette index 0. For OBJ graphics this is "
            "the conventional transparent index. For BG graphics, verify the "
            "target layer's color-0/backdrop behavior before integration."
        ),
        "palette_format": "GBA BGR555, 16 little-endian 16-bit entries (32 bytes)",
        "tile_bytes": len(raw_tiles),
        "compressed_bytes": len(compressed),
        "compression": "GBA BIOS LZ77 type 0x10",
        "output_sha256": {
            "tiles": sha256(raw_tiles),
            "compressed_tiles": sha256(compressed),
            "palette": sha256(palette_bytes),
        },
        "validation": {
            "4bpp_round_trip": True,
            "lz77_round_trip": True,
            "rom_modified": False,
            "room_tilemap_created": False,
            "room_pointer_updated": False,
            "runtime_tested": False,
        },
        "next_required_work": [
            "Choose the exact target room and determine whether this atlas is BG or OBJ content.",
            "Create a room-specific tilemap that references only the required tiles.",
            "Resolve the target room's palette bank, tile base, VRAM allocation, and shared-resource consumers.",
            "Integrate on a private ROM copy with hash-pinned preconditions.",
            "Run the room in mGBA and inspect player path, collisions, transparency, and palette output.",
        ],
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("png", type=Path, help="Indexed PNG tile atlas")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory (prefer private-roms/)")
    parser.add_argument("--prefix", default=None, help="Output filename prefix (defaults to input stem)")
    args = parser.parse_args()

    try:
        if not args.png.is_file():
            raise FileNotFoundError(args.png)
        if args.png.suffix.lower() != ".png":
            raise ValueError("Input must be a PNG file.")
        report = export_atlas(args.png, args.output_dir, args.prefix or args.png.stem)
    except (OSError, ValueError, AssertionError) as exc:
        print(f"png_to_gba_4bpp: ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
