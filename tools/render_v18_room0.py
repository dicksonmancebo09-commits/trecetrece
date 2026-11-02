#!/usr/bin/env python3
"""Render v1.8 Main Deck room 0 using the engine-visible palette bank after the bank correction."""
from __future__ import annotations
import argparse, csv, json, struct
from pathlib import Path

from gba_rom_audit import gba_lz77_decompress, gba_room_rle_decompress_map, sha256_bytes

EXPECTED_V18_SHA256 = "3bc764355012268d4ac6ef315bb9bb09ac0e5405d1c456bb506d1fdbe862af89"
ROM_SIZE = 0x800000

def bgr555_to_rgb(value: int) -> tuple[int, int, int]:
    return ((value & 31) * 255 // 31, ((value >> 5) & 31) * 255 // 31, ((value >> 10) & 31) * 255 // 31)

def tile_image(gfx: bytes, tile_index: int, palette: list[tuple[int, int, int]], Image):
    if not 0 <= tile_index < len(gfx) // 32:
        raise ValueError(f"Graphics tile index outside tileset: {tile_index}")
    image = Image.new("RGB", (8, 8))
    px = image.load()
    base = tile_index * 32
    for y in range(8):
        for x in range(8):
            byte = gfx[base + y * 4 + x // 2]
            index = (byte >> 4) & 15 if x & 1 else byte & 15
            px[x, y] = palette[index]
    return image

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, required=True, help="User-supplied v1.7 ROM")
    ap.add_argument("--out", type=Path, required=True, help="Output directory")
    ap.add_argument("--scale", type=int, default=3, choices=range(1, 9))
    ap.add_argument("--clipdata-csv", type=Path, help="Optional original room clipdata CSV for diagnostic view")
    args = ap.parse_args()

    rom = args.rom.read_bytes()
    rom_sha = sha256_bytes(rom)
    if len(rom) != ROM_SIZE or rom_sha != EXPECTED_V18_SHA256:
        raise SystemExit(f"v1.8 identity mismatch: size={len(rom)} sha256={rom_sha}")
    expected_complement = (-sum(rom[0xA0:0xBD]) - 0x19) & 0xFF
    if rom[0xAC:0xB0] != b"LZC0" or rom[0xBD] != expected_complement:
        raise SystemExit("GBA header validation failed")

    gfx_compressed = rom[0x416E8C:0x416E8C + 2843]
    gfx, gfx_consumed = gba_lz77_decompress(gfx_compressed)
    if len(gfx) != 11808 or gfx_consumed != len(gfx_compressed):
        raise ValueError("Unexpected v1.7 room-0 graphics dimensions")
    palette_data = rom[0x46B494:0x46B494 + 448]
    if len(palette_data) != 448:
        raise ValueError("Unexpected room-0 palette length")
    palette_rows = [
        [bgr555_to_rgb(int.from_bytes(palette_data[row * 32 + i * 2:row * 32 + i * 2 + 2], "little"))
         for i in range(16)]
        for row in range(14)
    ]

    metatile_bytes = rom[0x7B0000:0x7B0000 + 3074]
    if metatile_bytes[:2] != b"\x02\x00":
        raise ValueError("Unexpected metatile table header")
    metatiles = struct.unpack("<1536H", metatile_bytes[2:3074])
    if len(metatiles) != 384 * 4:
        raise ValueError("Metatile table is not 384 four-subtile records")
    if sorted({(word >> 12) & 0x0F for word in metatiles}) != [3]:
        raise ValueError("Expected v1.8 room-0 metatiles to use engine-visible BG palette bank 3")
    blank_words = metatiles[383 * 4:384 * 4]
    if [(word & 0x3FF) for word in blank_words] != [560] * 4:
        raise ValueError("Transparent metatile 383 does not map to tile 560")
    if any(gfx[368 * 32:369 * 32]):
        raise ValueError("Transparent graphics tile 560 is not all zero")

    bg1_bytes = rom[0x7B2000:0x7B2000 + 22]
    bg2_bytes = rom[0x7B2400:0x7B2400 + 414]
    w1, h1, bg1_values, bg1_consumed = gba_room_rle_decompress_map(bg1_bytes, 0, len(bg1_bytes))
    w2, h2, bg2_values, bg2_consumed = gba_room_rle_decompress_map(bg2_bytes, 0, len(bg2_bytes))
    if (w1, h1) != (34, 14) or (w2, h2) != (34, 14):
        raise ValueError("Unexpected active BG map dimensions")
    if set(bg1_values) != {383}:
        raise ValueError("Active BG1 is not the expected transparent layer")
    if min(bg2_values) != 0 or max(bg2_values) != 304 or len(set(bg2_values)) != 305:
        raise ValueError("Active BG2 metatile range differs from the v1.7 profile")

    from PIL import Image, ImageDraw
    width, height = w2 * 16, h2 * 16
    canvas = Image.new("RGB", (width, height), (0, 0, 0))
    px = canvas.load()
    invalid = []
    tile_cache = {}
    for by in range(h2):
        for bx in range(w2):
            metatile_id = bg2_values[by * w2 + bx]
            words = metatiles[metatile_id * 4:metatile_id * 4 + 4]
            for word, (ox, oy) in zip(words, ((0, 0), (8, 0), (0, 8), (8, 8))):
                hardware_tile = word & 0x3FF
                local_tile = hardware_tile - 192
                if not 0 <= local_tile < 369:
                    invalid.append({"metatile": metatile_id, "hardware_tile": hardware_tile})
                    continue
                if local_tile not in tile_cache:
                    tile_cache[local_tile] = tile_image(gfx, local_tile, palette_rows[1], Image)
                tile = tile_cache[local_tile]
                tile_px = tile.load()
                hflip, vflip = bool(word & 0x400), bool(word & 0x800)
                for ty in range(8):
                    for tx in range(8):
                        sx = 7 - tx if hflip else tx
                        sy = 7 - ty if vflip else ty
                        px[bx * 16 + ox + tx, by * 16 + oy + ty] = tile_px[sx, sy]
    if invalid:
        raise ValueError(f"Invalid custom tile references: {invalid[:8]}")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    canvas.save(out / "L01_R001_v1.8_BG2_native.png")
    canvas.resize((width * args.scale, height * args.scale), Image.Resampling.NEAREST).save(
        out / "L01_R001_v1.8_BG2_render.png"
    )

    clipdata_diagnostic = None
    if args.clipdata_csv:
        rows = list(csv.reader(args.clipdata_csv.open(encoding="utf-8")))
        values = [[int(value, 16) for value in row] for row in rows]
        if len(values) != h2 or any(len(row) != w2 for row in values):
            raise ValueError("Clipdata CSV dimensions do not match 34x14")
        diagnostic = Image.new("RGB", (width, height), (24, 24, 24))
        draw = ImageDraw.Draw(diagnostic)
        color_map = {0: (24, 24, 24), 16: (205, 205, 205), 32: (80, 125, 190)}
        for y, row in enumerate(values):
            for x, value in enumerate(row):
                color = color_map.get(value, (160, 80, 160))
                draw.rectangle((x*16, y*16, (x+1)*16-1, (y+1)*16-1), fill=color)
                if value:
                    draw.text((x*16+4, y*16+4), f"{value:02X}",
                              fill=(0, 0, 0) if value == 16 else (255, 255, 255))
        diagnostic.resize((width * args.scale, height * args.scale), Image.Resampling.NEAREST).save(
            out / "L01_R001_clipdata_diagnostic.png"
        )
        clipdata_diagnostic = str(args.clipdata_csv)

    atlas = Image.new("RGB", (24 * 8, 16 * 8), (48, 48, 48))
    for tile_id in range(369):
        tile = tile_image(gfx, tile_id, palette_rows[1], Image)
        atlas.paste(tile, ((tile_id % 24) * 8, (tile_id // 24) * 8))
    atlas.resize((24*8*args.scale, 16*8*args.scale), Image.Resampling.NEAREST).save(
        out / "tileset_61_v1.7_atlas.png"
    )

    report = {
        "room_id": "L01_R001", "source_area": "Main Deck", "source_room_index_0based": 0,
        "rom_sha256": rom_sha, "native_image_dimensions_px": [width, height],
        "active_bg1": {"offset": "0x7B2000", "length": len(bg1_bytes), "unique_values": sorted(set(bg1_values)),
                       "decoded_cells": len(bg1_values), "bytes_consumed": bg1_consumed},
        "active_bg2": {"offset": "0x7B2400", "length": len(bg2_bytes), "unique_metatiles": len(set(bg2_values)),
                       "min_metatile": min(bg2_values), "max_metatile": max(bg2_values),
                       "decoded_cells": len(bg2_values), "bytes_consumed": bg2_consumed},
        "metatile_table": {"offset": "0x7B0000", "records": 384, "subtile_words": len(metatiles),
                           "tile_ids_min": min(word & 0x3FF for word in metatiles),
                           "tile_ids_max": max(word & 0x3FF for word in metatiles),
                           "palette_banks": [3], "transparent_metatile": 383, "transparent_tile": 560,
                           "transparent_tile_all_zero": True},
        "graphics": {"offset": "0x416E8C", "compressed_bytes": len(gfx_compressed),
                     "decompressed_bytes": len(gfx), "tiles": len(gfx) // 32},
        "palette": {"offset": "0x46B494", "bytes": len(palette_data), "loaded_banks": "2-15",
                    "used_palette_bank": 3, "palette_source_row": 1, "engine_order_accounted_for": True},
        "invalid_tile_references": len(invalid), "clipdata_diagnostic_input": clipdata_diagnostic,
        "scope_note": "Static reconstruction from active v1.8 maps and graphics using the bank that survives RoomLoadTileset palette writes. Not an mGBA screenshot; no sprites, camera state, animations or effects.",
    }
    (out / "render-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "README.txt").write_text(
        "L01_R001 static render from the actual v1.8 custom BG1/BG2 maps, metatile table, tileset graphics and engine-visible palette bank.\n"
        "Native size: 544x224 pixels (34x14 blocks). Bank 3 preserves the custom palette after common rows 0–2 are written. Not an mGBA screenshot.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
