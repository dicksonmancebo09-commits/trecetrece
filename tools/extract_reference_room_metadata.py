#!/usr/bin/env python3
"""Extract factual per-room dimensions/layer declarations from the pinned public decomp source.

No ROM, compressed tilemap, clipdata bytes, graphics or source C files are copied
into this repository. The output contains only dimensions, declared lengths,
sprite-set counts and source-file hashes for traceability.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_REPOSITORY = "metroidret/mf"
SOURCE_COMMIT = "de76565c897c05838503717db9aa2adfe92aeba3"
SOURCE_AREAS = {
    "Main Deck": "main_deck",
    "Sector 1": "sector_1",
    "Sector 2": "sector_2",
    "Sector 3": "sector_3",
    "Sector 4": "sector_4",
    "Sector 5": "sector_5",
    "Sector 6": "sector_6",
}
LAYER_RE = re.compile(
    r"const\\s+u8\\s+(?P<symbol>\\w+_(?P<layer>Clipdata|Bg0|Bg1|Bg2|Bg3))"
    r"\\s*\\[\\s*(?P<declared_bytes>\\d+)\\s*\\]\\s*=\\s*\\{"
    r"\\s*(?P<width>\\d+)\\s*,\\s*//\\s*Room width"
    r"\\s*(?P<height>\\d+)\\s*,\\s*//\\s*Room height",
    re.IGNORECASE | re.DOTALL,
)
SPRITE_RE = re.compile(
    r"const\\s+u8\\s+(?P<symbol>\\w+_Spriteset(?P<variant>\\d+))"
    r"\\s*\\[\\s*ENEMY_ROOM_DATA_ARRAY_SIZE\\(\\s*(?P<declared_entries>\\d+)\\s*\\)\\s*\\]"
    r"\\s*=\\s*\\{(?P<body>.*?)\\};",
    re.IGNORECASE | re.DOTALL,
)
SPRITE_ROW_RE = re.compile(r"^\\s*\\d+\\s*,\\s*\\d+\\s*,", re.MULTILINE)


def source_path(area: str, room_index_0based: int) -> str:
    try:
        folder = SOURCE_AREAS[area]
    except KeyError as exc:
        raise ValueError(f"Unsupported source area: {area}") from exc
    return f"src/data/rooms/{folder}/{folder}_{room_index_0based}.c"


def parse_room_source(source: str, room_id: str = "") -> dict[str, Any]:
    layers: dict[str, dict[str, int]] = {}
    for match in LAYER_RE.finditer(source):
        layer = match.group("layer").lower()
        layers[layer] = {
            "declared_array_bytes": int(match.group("declared_bytes")),
            "width_blocks": int(match.group("width")),
            "height_blocks": int(match.group("height")),
        }
    if "clipdata" not in layers:
        raise ValueError(f"{room_id or 'room'}: source file has no Clipdata dimensions")

    clip = layers["clipdata"]
    conflicts = [
        key for key, value in layers.items()
        if value["width_blocks"] != clip["width_blocks"]
        or value["height_blocks"] != clip["height_blocks"]
    ]
    spritesets = []
    for match in SPRITE_RE.finditer(source):
        body = match.group("body")
        spritesets.append({
            "variant": int(match.group("variant")),
            "declared_array_entries": int(match.group("declared_entries")),
            "actual_sprite_placements": len(SPRITE_ROW_RE.findall(body)),
        })
    spritesets.sort(key=lambda item: item["variant"])
    return {
        "dimensions_blocks": {
            "width": clip["width_blocks"],
            "height": clip["height_blocks"],
        },
        "dimensions_pixels": {
            "width": clip["width_blocks"] * 16,
            "height": clip["height_blocks"] * 16,
        },
        "layers": layers,
        "layer_dimension_conflicts": conflicts,
        "spriteset_variants": spritesets,
        "spriteset_placement_counts": {
            f"variant_{item['variant']}": item["actual_sprite_placements"]
            for item in spritesets
        },
    }


def fetch_source(path: str, timeout: int = 30, retries: int = 4) -> bytes:
    url = f"https://raw.githubusercontent.com/{SOURCE_REPOSITORY}/{SOURCE_COMMIT}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "ZectorCero-RoomMetadata-Audit/1.0"})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"Unable to fetch {url}: {last_error}")


def extract_registry(registry_path: Path, output_path: Path, sheets_path: Path | None = None, workers: int = 12) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rooms = registry.get("rooms")
    if not isinstance(rooms, list) or len(rooms) != 382:
        raise ValueError("Expected exactly 382 registry room records")

    def one(room: dict[str, Any]) -> dict[str, Any]:
        source = room["source"]
        path = source_path(str(source["source_game_area"]), int(source["room_index_0based"]))
        raw = fetch_source(path)
        text = raw.decode("utf-8")
        parsed = parse_room_source(text, str(room["room_id"]))
        parsed.update({
            "room_id": room["room_id"],
            "source_game_area": source["source_game_area"],
            "source_room_index_1based": source["room_index_1based"],
            "source_room_index_0based": source["room_index_0based"],
            "source_file": path,
            "source_file_sha256": hashlib.sha256(raw).hexdigest(),
            "source_file_bytes": len(raw),
        })
        return parsed

    extracted: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, room): room for room in rooms}
        for future in concurrent.futures.as_completed(futures):
            room = futures[future]
            try:
                extracted.append(future.result())
            except Exception as exc:  # surfaced in the final report; never silently skipped
                errors.append({"room_id": room.get("room_id", ""), "error": str(exc)})
    extracted.sort(key=lambda item: (item["room_id"]))
    if errors:
        raise RuntimeError(
            f"Extraction incomplete: {len(errors)} of 382 rooms failed; "
            + "; ".join(f"{item['room_id']}: {item['error']}" for item in errors[:8])
        )
    by_id = {item["room_id"]: item for item in extracted}
    if len(by_id) != 382:
        raise RuntimeError(f"Expected 382 unique room IDs in extraction; found {len(by_id)}")
    if any(item["layer_dimension_conflicts"] for item in extracted):
        bad = [item["room_id"] for item in extracted if item["layer_dimension_conflicts"]]
        raise RuntimeError(f"BG/clipdata dimension disagreements in: {bad[:12]}")

    report = {
        "schema": "zector_cero.reference_room_metadata.v1",
        "project": registry.get("project"),
        "source": {
            "repository": f"https://github.com/{SOURCE_REPOSITORY}",
            "commit": SOURCE_COMMIT,
            "method": "Read-only source declaration extraction; no ROM binary or room asset bytes stored.",
        },
        "room_count": len(extracted),
        "unique_room_ids": len(by_id),
        "rooms": extracted,
        "limits": [
            "Metadata comes from the pinned public decompilation source, not a byte-for-byte verification against the user's private ROM.",
            "Layer dimensions and declared array lengths are extracted; compressed map/collision contents are not copied.",
            "Sprite placement counts are extracted per declared spriteset; individual sprite coordinates and proprietary graphics are not stored.",
            "Event script behavior and runtime collision semantics still require exact-ROM inspection and emulator testing.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

    if sheets_path and sheets_path.is_file():
        sheets = json.loads(sheets_path.read_text(encoding="utf-8"))
        sheet_rooms = sheets.get("rooms", [])
        if len(sheet_rooms) != 382:
            raise ValueError("Technical sheets must contain exactly 382 rooms before merge")
        for sheet in sheet_rooms:
            ref_data = by_id.get(sheet["room_id"])
            if ref_data is None:
                raise ValueError(f"Missing extracted reference metadata for {sheet['room_id']}")
            sheet.setdefault("extraction", {})
            sheet["extraction"]["reference_dimensions_blocks"] = ref_data["dimensions_blocks"]
            sheet["extraction"]["reference_dimensions_pixels"] = ref_data["dimensions_pixels"]
            sheet["extraction"]["reference_layers"] = ref_data["layers"]
            sheet["extraction"]["reference_spritesets"] = ref_data["spriteset_variants"]
            sheet["extraction"]["reference_source_file"] = ref_data["source_file"]
            sheet["extraction"]["reference_source_file_sha256"] = ref_data["source_file_sha256"]
            sheet["status"]["reference_dimensions"] = "extracted_from_pinned_source"
            sheet["status"]["exact_rom_match"] = "not_checked"
            sheet["status"]["geometry"] = "reference_dimensions_extracted_full_room_geometry_pending"
            sheet["status"]["collision"] = "reference_clipdata_dimensions_extracted_collision_content_pending"
        sheets["status"] = "reference_dimensions_populated_exact_rom_geometry_and_collision_pending"
        sheets["reference_metadata_source"] = report["source"]
        sheets["room_count_with_reference_dimensions"] = len(sheet_rooms)
        sheets_path.write_text(json.dumps(sheets, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    return {
        "room_count": len(extracted),
        "unique_room_ids": len(by_id),
        "source_commit": SOURCE_COMMIT,
        "layers_present": {
            layer: sum(1 for item in extracted if layer in item["layers"])
            for layer in ("clipdata", "bg0", "bg1", "bg2", "bg3")
        },
        "spriteset_variants": {
            str(variant): sum(1 for item in extracted if any(s["variant"] == variant for s in item["spriteset_variants"]))
            for variant in (0, 1, 2, 3)
        },
        "source_dimension_conflicts": 0,
        "output": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("data/world/sector-cero-room-registry-v1.json"))
    parser.add_argument("--technical-sheets", type=Path, default=Path("data/world/sector-cero-room-technical-sheets-v1.json"))
    parser.add_argument("--output", type=Path, default=Path("data/world/sector-cero-reference-room-metadata-v1.json"))
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.workers <= 24:
        parser.error("--workers must be between 1 and 24")
    try:
        print(json.dumps(extract_registry(args.registry, args.output, args.technical_sheets, args.workers), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"room metadata extraction failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
