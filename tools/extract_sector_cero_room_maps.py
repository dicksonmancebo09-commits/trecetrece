#!/usr/bin/env python3
"""Extract all 382 room BG/clipdata maps from the pinned user-supplied GBA ROM.

Run from the project root. Outputs should be kept under private-roms/ (gitignored).
"""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil, struct, zipfile
from collections import Counter
from pathlib import Path

from gba_rom_audit import gba_room_rle_decompress_map, sha256_bytes

BASE_SHA256 = "a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8"
V17_SHA256 = "66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf"
ROM_SIZE = 0x800000

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, required=True, help="Clean USA/Australia base ROM")
    ap.add_argument("--bundle", type=Path, required=True, help="room-source-bundle.json")
    ap.add_argument("--bundle-dir", type=Path, help="Bundle root; verifies database.json and source C hashes")
    ap.add_argument("--v17", type=Path, help="Optional v1.7 ROM for byte comparison")
    ap.add_argument("--out", type=Path, default=Path("private-roms/382-room-extraction"))
    ap.add_argument("--zip", type=Path, default=Path("private-roms/382-room-extraction.zip"))
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    rom = args.rom.read_bytes()
    base_sha = sha256_bytes(rom)
    if len(rom) != ROM_SIZE or base_sha != BASE_SHA256:
        raise SystemExit(f"Clean base mismatch: size={len(rom)} sha256={base_sha}")
    expected_header = (-sum(rom[0xA0:0xBD]) - 0x19) & 0xFF
    if rom[0xBD] != expected_header or rom[0xAC:0xB0] != b"AMTE":
        raise SystemExit("Clean base GBA header validation failed")

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    if bundle.get("schema") != "zector-cero.room-source-bundle.v1":
        raise SystemExit("Unsupported room source bundle schema")
    rooms = bundle.get("rooms", [])
    if len(rooms) != 382 or len({r["room_id"] for r in rooms}) != 382:
        raise SystemExit("Bundle must contain 382 unique room IDs")

    if args.bundle_dir:
        db_path = args.bundle_dir / "database.json"
        if sha256_bytes(db_path.read_bytes()) != bundle["source"]["database_sha256"]:
            raise SystemExit("database.json SHA-256 mismatch")
        for room in rooms:
            c_path = args.bundle_dir / "source" / "room_c" / f"{room['room_id']}.c"
            if sha256_bytes(c_path.read_bytes()) != room["source_file_sha256"]:
                raise SystemExit(f"Source C hash mismatch: {room['room_id']}")

    v17 = args.v17.read_bytes() if args.v17 else None
    v17_sha = sha256_bytes(v17) if v17 is not None else None
    if v17 is not None and (len(v17) != ROM_SIZE or v17_sha != V17_SHA256):
        raise SystemExit(f"v1.7 ROM mismatch: size={len(v17)} sha256={v17_sha}")

    out = args.out.resolve()
    if out.exists():
        if not args.overwrite:
            raise SystemExit(f"Output exists; pass --overwrite to replace: {out}")
        shutil.rmtree(out)
    maps_root = out / "maps"
    maps_root.mkdir(parents=True)
    room_entries = bundle.get("room_entries", {})
    rooms_out = []
    errors = []
    layer_counts = Counter()
    area_counts = Counter()
    batch_counts = Counter()
    total_payload = 0
    ranges = []
    v17_changes = []

    for room in sorted(rooms, key=lambda r: r["room_id"]):
        rid = room["room_id"]
        area = room["source_game_area"]
        idx = int(room["source_room_index_0based"])
        width = int(room["dimensions_blocks"]["width"])
        height = int(room["dimensions_blocks"]["height"])
        entry = room_entries.get(area, {}).get("entries", {}).get(str(idx))
        if entry is None:
            errors.append({"room_id": rid, "error": "missing RoomEntryRom entry"})
            continue
        summary = {
            "room_id": rid, "level_id": room.get("level_id"),
            "production_batch": room.get("production_batch"),
            "production_id": room.get("production_id"),
            "production_name": room.get("production_name"),
            "production_role": room.get("production_role"),
            "neighborhood": room.get("neighborhood"),
            "source_game_area": area, "source_room_index_0based": idx,
            "dimensions_blocks": {"width": width, "height": height},
            "dimensions_pixels": room["dimensions_pixels"],
            "tileset_entry": entry.get("tileset"),
            "bg0_prop": entry.get("bg0Prop"), "bg1_prop": entry.get("bg1Prop"),
            "bg2_prop": entry.get("bg2Prop"), "bg3_prop": entry.get("bg3Prop"),
            "map_position": {"x": entry.get("mapX"), "y": entry.get("mapY")},
            "spritesets": room.get("spritesets", []),
            "scrolls": room.get("scrolls", []), "layers": {},
        }
        room_dir = maps_root / rid
        room_dir.mkdir()
        for layer, spec in sorted(room.get("rle_layers", {}).items()):
            offset = int(spec["rom_offset"])
            size = int(spec["compressed_payload_bytes"])
            end = offset + size
            if offset < 0 or end > len(rom):
                errors.append({"room_id": rid, "layer": layer, "error": "ROM range out of bounds"})
                continue
            payload = rom[offset:end]
            raw = bytes((width, height)) + payload
            try:
                w2, h2, values, consumed = gba_room_rle_decompress_map(raw, 0, len(raw))
            except Exception as exc:
                errors.append({"room_id": rid, "layer": layer, "rom_offset": spec["rom_offset_hex"], "error": str(exc)})
                continue
            if (w2, h2) != (width, height) or len(values) != width * height or consumed > len(raw):
                errors.append({"room_id": rid, "layer": layer, "error": "decoded dimensions/cell count mismatch"})
                continue
            trailing = raw[consumed:]
            raw_file = room_dir / f"{layer}.rle"
            u16_file = room_dir / f"{layer}.u16le.bin"
            csv_file = room_dir / f"{layer}.csv"
            raw_file.write_bytes(raw)
            decoded = struct.pack("<" + "H" * len(values), *values)
            u16_file.write_bytes(decoded)
            with csv_file.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                for y in range(height):
                    writer.writerow([f"0x{x:04X}" for x in values[y * width:(y + 1) * width]])
            counts = Counter(values)
            stats = {
                "database_path": spec["database_path"],
                "rom_offset": spec["rom_offset_hex"],
                "compressed_payload_bytes": size,
                "decoded_cells": len(values),
                "rle_stream_bytes_consumed_including_dimensions": consumed,
                "trailing_reserved_bytes": len(trailing),
                "trailing_reserved_hex": trailing.hex(),
                "unique_value_count": len(counts),
                "min_value": min(values), "max_value": max(values),
                "top_values": [{"value": f"0x{k:04X}", "count": n} for k, n in counts.most_common(16)],
                "compressed_sha256": sha256_bytes(payload),
                "decoded_sha256": sha256_bytes(decoded),
                "outputs": {"rle": str(raw_file.relative_to(out)), "u16le": str(u16_file.relative_to(out)), "csv": str(csv_file.relative_to(out))},
            }
            summary["layers"][layer] = stats
            layer_counts[layer] += 1
            total_payload += size
            ranges.append((offset, end, rid, layer))
            if v17 is not None:
                other = v17[offset:end]
                diff = sum(a != b for a, b in zip(payload, other))
                if diff:
                    v17_changes.append({"room_id": rid, "layer": layer, "rom_offset": spec["rom_offset_hex"], "different_bytes": diff})
        if not summary["layers"]:
            errors.append({"room_id": rid, "error": "no RLE layers extracted"})
        rooms_out.append(summary)
        area_counts[area] += 1
        batch_counts[str(room.get("production_batch"))] += 1

    if errors:
        (out / "extraction-errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        raise SystemExit(f"Extraction failed with {len(errors)} errors; see {out/'extraction-errors.json'}")
    if len(rooms_out) != 382 or sum(layer_counts.values()) != int(bundle["summary"]["rle_layers"]):
        raise SystemExit("382-room / RLE layer coverage check failed")
    if dict(batch_counts) != {"1": 87, "2": 87, "3": 87, "4": 87, "5": 34}:
        raise SystemExit(f"Production batch counts mismatch: {dict(batch_counts)}")

    overlaps = []
    ordered = sorted(ranges)
    for prev, cur in zip(ordered, ordered[1:]):
        if cur[0] < prev[1]:
            overlaps.append({"previous": prev, "current": cur})
    if overlaps:
        raise SystemExit(f"RLE ROM ranges overlap: {len(overlaps)}")

    report = {
        "schema": "zector-cero.382-room-extraction.v1",
        "source": bundle["source"],
        "base_rom": {"size_bytes": len(rom), "sha256": base_sha, "game_code": rom[0xAC:0xB0].decode("ascii"), "header_complement_valid": True},
        "v1_7_comparison": None if v17 is None else {"sha256": v17_sha, "changed_mapped_room_layers": len(v17_changes), "changes": v17_changes},
        "summary": {
            "rooms_extracted": len(rooms_out), "rle_layers_extracted": sum(layer_counts.values()),
            "layer_counts": dict(layer_counts), "rooms_by_source_area": dict(area_counts),
            "production_batch_counts": dict(batch_counts),
            "compressed_payload_bytes_extracted": total_payload,
            "range_overlap_count": len(overlaps), "rle_decode_errors": 0,
        },
        "rooms": rooms_out,
    }
    (out / "room-extraction-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    structure = {
        "room_entries": bundle.get("room_entries", {}),
        "doors_by_area": bundle.get("doors_by_area", {}),
        "tileset_tables": bundle.get("tileset_tables", {}),
        "connection_tables_source": bundle.get("connection_tables_source", {}),
        "production_assignments": {
            r["room_id"]: {k: r.get(k) for k in ("production_batch", "production_id", "production_name", "production_role", "neighborhood")}
            for r in rooms
        },
    }
    (out / "room-structure-tables.json").write_text(json.dumps(structure, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "README.txt").write_text(
        "Zector Cero — extraction de mapas de 382 salas\n"
        f"Base SHA-256: {base_sha}\nSalas: 382; capas RLE: {sum(layer_counts.values())}\n"
        "Cada capa está en RLE original + U16LE + CSV. La ROM no fue modificada.\n",
        encoding="utf-8",
    )
    with (out / "room-summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["room_id", "production_id", "production_batch", "neighborhood", "production_name", "production_role", "level_id", "source_area", "source_index", "width_blocks", "height_blocks", "tileset_entry", "layers"])
        for r in rooms_out:
            w.writerow([r["room_id"], r["production_id"], r["production_batch"], r["neighborhood"], r["production_name"], r["production_role"], r["level_id"], r["source_game_area"], r["source_room_index_0based"], r["dimensions_blocks"]["width"], r["dimensions_blocks"]["height"], r["tileset_entry"], ";".join(sorted(r["layers"]))])
    args.zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(out.parent))
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    print(f"v1.7 mapped RLE changes: {len(v17_changes)}")
    print(args.zip)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
