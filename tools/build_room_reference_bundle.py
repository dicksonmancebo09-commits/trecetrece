#!/usr/bin/env python3
"""Build a reproducible, ROM-free source bundle for the 382 Sector Cero rooms."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, re, sys, urllib.request
from pathlib import Path
from typing import Any

SOURCE_REPO = "metroidret/mf"
SOURCE_COMMIT = "de76565c897c05838503717db9aa2adfe92aeba3"
RAW = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/"
AREAS = {
    "Main Deck": "main_deck", "Sector 1": "sector_1", "Sector 2": "sector_2",
    "Sector 3": "sector_3", "Sector 4": "sector_4", "Sector 5": "sector_5",
    "Sector 6": "sector_6",
}
LAYER_RE = re.compile(
    r"const\s+u8\s+(?P<symbol>\w+_(?P<layer>Clipdata|Bg0|Bg1|Bg2|Bg3))"
    r"\s*\[\s*(?P<declared_bytes>\d+)\s*\]\s*=\s*\{"
    r"\s*(?P<width>\d+)\s*,\s*//\s*Room width"
    r"\s*(?P<height>\d+)\s*,\s*//\s*Room height",
    re.IGNORECASE | re.DOTALL,
)
SPRITE_RE = re.compile(
    r"const\s+u8\s+(?P<symbol>\w+_Spriteset(?P<variant>\d+))"
    r"\s*\[\s*ENEMY_ROOM_DATA_ARRAY_SIZE\(\s*(?P<declared_entries>\d+)\s*\)\s*\]"
    r"\s*=\s*\{(?P<body>.*?)\};", re.IGNORECASE | re.DOTALL,
)
SPRITE_ROW_RE = re.compile(
    r"^\s*(?P<x>\d+)\s*,\s*(?P<y>\d+)\s*,\s*(?P<flags>[^,\n]+(?:\|[^,\n]+)*)\s*,?\s*$",
    re.MULTILINE,
)

def fetch(path: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(RAW + path, headers={"User-Agent": "ZectorCero-ReferenceBundle/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def parse_fields(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"\s*\.(\w+)\s*=\s*(.*?)\s*,?\s*$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().rstrip(",")
    return out

def extract_table(source: str, declaration: str) -> str | None:
    pos = source.find(declaration)
    if pos < 0:
        return None
    start = source.find("{", pos)
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start + 1:i]
    raise ValueError(f"Unclosed initializer: {declaration}")

def parse_designated_entries(table: str) -> dict[int, dict[str, str]]:
    return {
        int(m.group(1)): parse_fields(m.group(2))
        for m in re.finditer(r"\[\s*(\d+)\s*\]\s*=\s*\{([^{}]*)\}", table, re.DOTALL)
    }

def parse_struct_array(table: str) -> list[dict[str, str]]:
    return [v for block in re.findall(r"\{([^{}]*)\}", table, re.DOTALL) if (v := parse_fields(block))]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=Path("private-roms/room-reference-bundle"))
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    root, out = args.repo_root.resolve(), args.out.resolve()
    meta_path = root / "data/world/sector-cero-reference-room-metadata-v1.json"
    registry_path = root / "data/world/sector-cero-room-registry-v1.json"
    if not meta_path.is_file() or not registry_path.is_file():
        raise FileNotFoundError("Expected project room metadata and registry JSON.")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    metadata_rooms, registry_rooms = metadata.get("rooms", []), registry.get("rooms", [])
    if len(metadata_rooms) != 382 or len(registry_rooms) != 382:
        raise ValueError(f"Expected exactly 382 metadata and registry rooms; got {len(metadata_rooms)}, {len(registry_rooms)}")
    reg_by_id = {r["room_id"]: r for r in registry_rooms}
    if len(reg_by_id) != 382:
        raise ValueError("Duplicate room IDs in registry.")

    db_raw = fetch("database.json")
    db = json.loads(db_raw)
    db_by_path = {e["path"]: e for e in db if isinstance(e.get("addr"), dict) and e["addr"].get("us")}

    def load_room(meta: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
        rid, area = meta["room_id"], str(meta["source_game_area"])
        folder, idx = AREAS[area], int(meta["source_room_index_0based"])
        path = f"src/data/rooms/{folder}/{folder}_{idx}.c"
        raw = fetch(path)
        actual_hash = sha(raw)
        expected_hash = meta.get("source_file_sha256")
        if expected_hash and actual_hash != expected_hash:
            raise ValueError(f"{rid}: source C hash mismatch")
        source = raw.decode("utf-8")
        decls: dict[str, dict[str, Any]] = {}
        for m in LAYER_RE.finditer(source):
            layer = m.group("layer").lower()
            decls[layer] = {
                "symbol": m.group("symbol"),
                "declared_array_bytes": int(m.group("declared_bytes")),
                "width_blocks": int(m.group("width")),
                "height_blocks": int(m.group("height")),
            }
        if "clipdata" not in decls:
            raise ValueError(f"{rid}: missing Clipdata declaration")
        width, height = decls["clipdata"]["width_blocks"], decls["clipdata"]["height_blocks"]
        if width != meta["dimensions_blocks"]["width"] or height != meta["dimensions_blocks"]["height"]:
            raise ValueError(f"{rid}: dimensions differ from checked metadata")
        if any(v["width_blocks"] != width or v["height_blocks"] != height for v in decls.values()):
            raise ValueError(f"{rid}: inconsistent layer dimensions")
        rle = {}
        for layer in ("clipdata", "bg0", "bg1", "bg2"):
            decl = decls.get(layer)
            if not decl:
                continue
            asset_path = f"rooms/{folder}/{folder}_{idx}_{layer}.rle"
            entry = db_by_path.get(asset_path)
            if entry is None:
                raise ValueError(f"{rid}: missing database asset {asset_path}")
            payload = int(entry["count"], 0) * int(entry["size"])
            expected_payload = int(decl["declared_array_bytes"]) - 2
            if payload != expected_payload:
                raise ValueError(f"{rid}: {layer} payload length {payload} != C length {expected_payload}")
            offset = int(entry["addr"]["us"], 0)
            if offset < 0 or offset + payload > 0x800000:
                raise ValueError(f"{rid}: {layer} ROM range is outside 8 MiB")
            rle[layer] = {
                "database_path": asset_path, "rom_offset": offset, "rom_offset_hex": f"0x{offset:X}",
                "compressed_payload_bytes": payload,
                "declared_array_bytes_including_dimensions": int(decl["declared_array_bytes"]),
                "dimensions_prefix_hex": bytes([width, height]).hex(),
                "source_symbol": decl["symbol"], "encoding": "metroid_two_lane_rle_u16",
            }
        spritesets = []
        for m in SPRITE_RE.finditer(source):
            placements = [{
                "x_blocks": int(row.group("x")), "y_blocks": int(row.group("y")),
                "flags_expression": row.group("flags").strip(),
            } for row in SPRITE_ROW_RE.finditer(m.group("body"))]
            spritesets.append({
                "variant": int(m.group("variant")), "symbol": m.group("symbol"),
                "declared_array_entries": int(m.group("declared_entries")),
                "placements": placements, "placement_count": len(placements),
            })
        scrolls = [{
            "symbol": m.group(1), "source_body": m.group(2).strip()
        } for m in re.finditer(r"const\s+u8\s+(\w+_Scrolls)\[[^\]]+\]\s*=\s*\{(.*?)\};", source, re.DOTALL)]
        rec = {
            "room_id": rid, "level_id": reg_by_id[rid].get("level_id"),
            "production_batch": reg_by_id[rid].get("production_batch"),
            "source_game_area": area, "source_area_folder": folder,
            "source_room_index_1based": int(meta["source_room_index_1based"]),
            "source_room_index_0based": idx, "source_file": path,
            "source_file_sha256": actual_hash,
            "dimensions_blocks": {"width": width, "height": height},
            "dimensions_pixels": {"width": width * 16, "height": height * 16},
            "layer_declarations": decls, "rle_layers": rle,
            "spritesets": spritesets, "scrolls": scrolls,
        }
        return rec, raw

    loaded: dict[str, tuple[dict[str, Any], bytes]] = {}
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(load_room, m): m for m in metadata_rooms}
        for f in concurrent.futures.as_completed(futures):
            m = futures[f]
            try:
                rec, raw = f.result()
                loaded[rec["room_id"]] = (rec, raw)
            except Exception as exc:
                errors.append(f"{m.get('room_id')}: {exc}")
    if errors:
        raise RuntimeError(f"{len(errors)} room source failures: " + " | ".join(errors[:12]))
    if len(loaded) != 382:
        raise RuntimeError(f"Only {len(loaded)} of 382 room sources were loaded.")
    records = [loaded[k][0] for k in sorted(loaded)]

    support_paths = [
        "src/data/rooms_data.c", "src/data/connection_data.c", "src/data/event_data.c",
        "src/data/clipdata_data.c", "src/data/clipdata_types_tilemap.c",
        "src/room.c", "src/clipdata.c", "src/connection.c",
        "include/structs/room.h", "include/structs/clipdata.h", "include/structs/connection.h",
        "include/constants/clipdata.h", "include/constants/connection.h",
    ]
    support_blobs = {p: fetch(p).decode("utf-8") for p in support_paths}
    rooms_src = support_blobs["src/data/rooms_data.c"]
    room_entries, doors = {}, {}
    for area, folder in AREAS.items():
        entry_name = "sMainDeckRoomEntries" if area == "Main Deck" else f"sSector{area.split()[-1]}RoomEntries"
        table = extract_table(rooms_src, f"const struct RoomEntryRom {entry_name}")
        if table is None:
            raise ValueError(f"Missing room entry table {entry_name}")
        room_entries[area] = {"symbol": entry_name, "entries": {
            str(k): v for k, v in parse_designated_entries(table).items()
        }}
        door_name = "sMainDeckDoors" if area == "Main Deck" else f"sSector{area.split()[-1]}Doors"
        door_table = extract_table(rooms_src, f"const struct Door {door_name}")
        if door_table is None:
            raise ValueError(f"Missing door table {door_name}")
        doors[area] = {"symbol": door_name, "records": parse_struct_array(door_table)}

    tileset_tables = {}
    for m in re.finditer(r"const\s+struct\s+TilesetEntry\s+(\w+)\[[^\]]+\]\s*=\s*\{", rooms_src):
        name = m.group(1)
        table = extract_table(rooms_src, f"const struct TilesetEntry {name}")
        if table is not None:
            tileset_tables[name] = parse_designated_entries(table)

    conn_src = support_blobs["src/data/connection_data.c"]
    conn_tables = {}
    for name in ("sAreaConnections", "sEventBasedConnections"):
        table = extract_table(conn_src, f"const u8 {name}[")
        if table is not None:
            conn_tables[name] = table

    asset_paths = {layer["database_path"] for rec in records for layer in rec["rle_layers"].values()}
    expected_asset_paths = {
        e["path"] for e in db
        if re.match(r"^rooms/(main_deck|sector_[1-6])/.+_(clipdata|bg[0-2])\.rle$", e.get("path", ""))
    }
    if asset_paths != expected_asset_paths:
        raise ValueError(
            f"RLE database coverage mismatch: mapped={len(asset_paths)}, expected={len(expected_asset_paths)}, "
            f"missing={sorted(expected_asset_paths-asset_paths)[:5]}, extra={sorted(asset_paths-expected_asset_paths)[:5]}"
        )

    out.mkdir(parents=True, exist_ok=True)
    (out / "source" / "room_c").mkdir(parents=True, exist_ok=True)
    for rec in records:
        (out / "source" / "room_c" / f"{rec['room_id']}.c").write_bytes(loaded[rec["room_id"]][1])
    (out / "database.json").write_bytes(db_raw)
    for path, body in support_blobs.items():
        dest = out / "source" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    summary = {
        "rooms": len(records),
        "rle_layers": sum(len(r["rle_layers"]) for r in records),
        "rle_database_paths_covered": len(asset_paths),
        "room_entry_tables": len(room_entries),
        "door_records": sum(len(v["records"]) for v in doors.values()),
        "tileset_tables": {k: len(v) for k, v in tileset_tables.items()},
        "support_source_files": len(support_blobs),
    }
    bundle = {
        "schema": "zector-cero.room-source-bundle.v1",
        "source": {"repository": SOURCE_REPO, "commit": SOURCE_COMMIT, "database_sha256": sha(db_raw)},
        "summary": summary, "rooms": records, "room_entries": room_entries,
        "doors_by_area": doors, "tileset_tables": {
            k: {str(i): v for i, v in rows.items()} for k, rows in tileset_tables.items()
        },
        "connection_tables_source": conn_tables, "scope_note":
        "Contains source declarations and ROM offsets/lengths only. No ROM bytes, extracted proprietary assets or patches are included.",
    }
    (out / "room-source-bundle.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "README.txt").write_text(
        "Zector Cero room source bundle\n"
        f"Upstream: {SOURCE_REPO}@{SOURCE_COMMIT}\n"
        f"Rooms: {len(records)}; BG/clipdata RLE assets: {summary['rle_layers']}\n"
        "No ROM bytes are included. Use only with the matching user-supplied clean ROM.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"build_room_reference_bundle: ERROR: {exc}", file=sys.stderr)
        raise
