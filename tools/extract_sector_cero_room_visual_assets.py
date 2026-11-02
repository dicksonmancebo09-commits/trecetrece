#!/usr/bin/env python3
"""Extract the referenced tileset, palette, tilemap and animation assets for 382 rooms.

Run from project root with the SHA-pinned clean USA/Australia ROM and the
zector-cero room-source bundle. Keep extracted binary data under private-roms/.
"""
from __future__ import annotations
import argparse, csv, json, re, shutil, zipfile
from collections import Counter, defaultdict
from pathlib import Path

from gba_rom_audit import gba_lz77_decompress, sha256_bytes

BASE_SHA256 = "a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8"
V17_SHA256 = "66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf"
ROM_SIZE = 0x800000
FIELD_SUFFIX = {"Gfx": ".gfx.lz", "Pal": ".pal", "Bg_Gfx": "_bg.gfx.lz", "Tilemap": ".tm"}
SYMBOL_RE = re.compile(r"sTileset_(\d+)_(Gfx|Pal|Bg_Gfx|Tilemap)$")

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, required=True)
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--bundle-dir", type=Path, required=True)
    ap.add_argument("--v17", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("private-roms/room-visual-assets"))
    ap.add_argument("--zip", type=Path, default=Path("private-roms/room-visual-assets.zip"))
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    rom, v17 = args.rom.read_bytes(), args.v17.read_bytes()
    base_sha, v17_sha = sha256_bytes(rom), sha256_bytes(v17)
    if len(rom) != ROM_SIZE or base_sha != BASE_SHA256:
        raise SystemExit(f"Base ROM mismatch: size={len(rom)} sha256={base_sha}")
    if len(v17) != ROM_SIZE or v17_sha != V17_SHA256:
        raise SystemExit(f"v1.7 ROM mismatch: size={len(v17)} sha256={v17_sha}")
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    db_file = args.bundle_dir / "database.json"
    if sha256_bytes(db_file.read_bytes()) != bundle["source"]["database_sha256"]:
        raise SystemExit("database.json hash mismatch")
    db = {e["path"]: e for e in json.loads(db_file.read_text(encoding="utf-8")) if e.get("addr", {}).get("us")}

    entries = bundle["tileset_tables"]["sTilesetEntries"]
    usage = Counter()
    rooms_by_tileset = defaultdict(list)
    for area, table in bundle["room_entries"].items():
        for index, row in table["entries"].items():
            tid = int(row["tileset"], 0)
            usage[tid] += 1
            rooms_by_tileset[tid].append({"area": area, "room_index_0based": int(index)})

    static_refs = {}
    tileset_usage = []
    for tid, room_count in sorted(usage.items()):
        entry = entries[str(tid)]
        row = {
            "tileset_index": tid, "room_count": room_count,
            "rooms": rooms_by_tileset[tid],
            "animated_tileset": int(entry["animatedTileset"], 0),
            "animated_palette": int(entry["animatedPalette"], 0),
        }
        for field in ("pTileGraphics", "pPalette", "pBackgroundGraphics", "pTilemap"):
            symbol = entry[field]
            match = SYMBOL_RE.fullmatch(symbol)
            if not match:
                raise ValueError(f"Unexpected tileset symbol: {symbol}")
            number, kind = match.groups()
            path = f"tilesets/{number}{FIELD_SUFFIX[kind]}"
            if path not in db:
                raise ValueError(f"Missing database asset {path} ({symbol})")
            row[field] = {"symbol": symbol, "path": path}
            static_refs.setdefault(path, []).append({"tileset_index": tid, "field": field})
        tileset_usage.append(row)

    palette_src = (args.bundle_dir / "source/src/data/animated_palette_data.c").read_text(encoding="utf-8")
    palette_table = palette_src.split("const struct AnimatedPaletteData sAnimatedPaletteEntries", 1)[1]
    palette_sources = {}
    for match in re.finditer(r"\[(\d+)\]\s*=\s*\{(.*?)\}", palette_table, re.S):
        source_id = re.search(r"\.pPalette\s*=\s*sAnimatedPal_(\d+)", match.group(2))
        if source_id:
            palette_sources[int(match.group(1))] = int(source_id.group(1))
    animated_palette_ids = sorted({
        row["animated_palette"] for row in tileset_usage if row["animated_palette"] > 0
    })
    animation_palette_refs = {}
    for animation_id in animated_palette_ids:
        source_id = palette_sources.get(animation_id)
        if source_id is None:
            raise ValueError(f"No animated palette data row for ID {animation_id}")
        path = f"tilesets/animated_palettes/{source_id}.pal"
        if path not in db:
            raise ValueError(f"Missing animated palette data file {path}")
        animation_palette_refs.setdefault(path, []).append(animation_id)

    animated_tileset_ids = sorted({
        row["animated_tileset"] for row in tileset_usage if row["animated_tileset"] > 0
    })
    global_paths = [
        "common/common_tilemap.tt", "common/common_tiles.gfx", "common/common_tiles.pal",
        "common/hatch_flashing.pal", "common/unlocked_hatch_flashing.pal",
        "rooms/background_empty.bin", "animated_tiles/tiles.gfx",
        "animated_tiles/tanks.gfx", "animated_tiles/liquids.gfx",
    ]
    all_paths = set(static_refs) | set(animation_palette_refs) | set(global_paths)
    missing = sorted(path for path in all_paths if path not in db)
    if missing:
        raise ValueError("Missing referenced assets: " + ", ".join(missing))

    out = args.out.resolve()
    if out.exists():
        if not args.overwrite:
            raise SystemExit(f"Output exists; pass --overwrite: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    assets, ranges, changes = [], [], []
    raw_total = decoded_total = 0
    for path in sorted(all_paths):
        entry = db[path]
        offset = int(entry["addr"]["us"], 0)
        size = int(entry["count"], 0) * int(entry["size"])
        end = offset + size
        if offset < 0 or end > len(rom):
            raise ValueError(f"Asset range outside ROM: {path}")
        raw = rom[offset:end]
        raw_dir = out / "raw" / path
        raw_dir.parent.mkdir(parents=True, exist_ok=True)
        raw_dir.write_bytes(raw)
        decoded_info = None
        if path.endswith(".lz"):
            decoded, consumed = gba_lz77_decompress(raw)
            decoded_path = out / "decoded" / path.removesuffix(".lz")
            decoded_path.parent.mkdir(parents=True, exist_ok=True)
            decoded_path.write_bytes(decoded)
            decoded_info = {
                "path": str(decoded_path.relative_to(out)), "bytes": len(decoded),
                "compressed_bytes_consumed": consumed,
                "trailing_bytes": len(raw) - consumed,
                "sha256": sha256_bytes(decoded),
            }
            decoded_total += len(decoded)
        other = v17[offset:end]
        diff = sum(a != b for a, b in zip(raw, other))
        if diff:
            changes.append({
                "path": path, "rom_offset": f"0x{offset:X}", "bytes_different": diff,
                "base_sha256": sha256_bytes(raw), "v1_7_sha256": sha256_bytes(other),
            })
        ranges.append((offset, end, path))
        raw_total += size
        assets.append({
            "path": path, "rom_offset": f"0x{offset:X}", "size_bytes": size,
            "sha256": sha256_bytes(raw), "decoded_lz77": decoded_info,
            "v1_7_different_bytes": diff,
            "tileset_references": static_refs.get(path, []),
            "animated_palette_ids": animation_palette_refs.get(path, []),
        })

    overlaps = []
    ordered = sorted(ranges)
    for previous, current in zip(ordered, ordered[1:]):
        if current[0] < previous[1] and (previous[0], previous[1]) != (current[0], current[1]):
            overlaps.append({"previous": previous, "current": current})
    if overlaps:
        raise SystemExit(f"Partial resource range overlaps: {len(overlaps)}")

    report = {
        "schema": "zector-cero.room-visual-assets.v1",
        "source": bundle["source"],
        "roms": {"base_sha256": base_sha, "v1_7_sha256": v17_sha},
        "summary": {
            "rooms_using_tilesets": sum(usage.values()),
            "unique_tileset_entries_used": len(usage),
            "distinct_static_resource_paths": len(static_refs),
            "animated_tileset_ids_used": animated_tileset_ids,
            "animated_palette_ids_used": animated_palette_ids,
            "animated_palette_asset_paths": len(animation_palette_refs),
            "global_resources": len(global_paths),
            "total_distinct_asset_files": len(all_paths),
            "raw_asset_bytes": raw_total, "lz77_decoded_asset_bytes": decoded_total,
            "v1_7_assets_with_byte_differences": len(changes),
            "v1_7_different_asset_bytes": sum(c["bytes_different"] for c in changes),
            "partial_range_overlaps": 0,
        },
        "tileset_usage": tileset_usage,
        "animated_palette_source_mapping": {str(k): v for k, v in sorted(palette_sources.items())},
        "assets": assets, "v1_7_changes": changes,
        "notes": [
            "Extracted only from the SHA-pinned user-supplied clean base ROM.",
            "v1.7 compared byte-for-byte at the same database offsets and lengths.",
            "Animated sequences are preserved as source data but are not rendered/played.",
            "No ROM file is modified.",
        ],
    }
    (out / "room-visual-assets-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (out / "tileset-usage.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tileset_index", "room_count", "animated_tileset", "animated_palette", "tile_gfx", "palette", "bg_gfx", "tilemap"])
        for row in tileset_usage:
            w.writerow([row["tileset_index"], row["room_count"], row["animated_tileset"], row["animated_palette"],
                        row["pTileGraphics"]["path"], row["pPalette"]["path"],
                        row["pBackgroundGraphics"]["path"], row["pTilemap"]["path"]])
    (out / "README.txt").write_text(
        f"Used tileset entries: {len(usage)} across 382 rooms\n"
        f"Distinct resources: {len(all_paths)}; raw bytes: {raw_total}\n"
        "Raw resources are in raw/; LZ77 decoded resources are in decoded/.\n",
        encoding="utf-8",
    )
    args.zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for file in sorted(out.rglob("*")):
            if file.is_file():
                z.write(file, file.relative_to(out.parent))
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    print(args.zip)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
