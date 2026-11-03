#!/usr/bin/env python3
"""Reconcile technical sheets and master-plan coordinates with pinned RoomEntry metadata.

This is a metadata-only operation. It does not extract compressed map or clipdata
payloads, patch a ROM, or certify runtime behavior.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/world/sector-cero-room-registry-v1.json"
DEFAULT_REFERENCE = ROOT / "data/world/sector-cero-room-entry-reference-v1.json"
DEFAULT_SHEETS = ROOT / "data/world/sector-cero-room-technical-sheets-v1.json"
DEFAULT_MASTER = ROOT / "docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md"
DEFAULT_AUDIT = ROOT / "docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md"
DEFAULT_CSV = ROOT / "recovery/analysis/ROOM_ENTRY_REFERENCE_CROSSWALK_2026-11-03.csv"
EXPECTED = 382
CORRECTION_HEADING = "## Reconciliación de RoomEntry — 3 de noviembre de 2026"


def _consumer_counts(reference_rooms: list[dict[str, Any]]) -> tuple[Counter, Counter]:
    resources: Counter = Counter()
    symbols: Counter = Counter()
    for room in reference_rooms:
        entry = room["room_entry"]
        pairs = [("tileset_entry_index", entry["tileset_entry_index"])]
        pairs.extend(room["tileset_entry"]["resource_indices"].items())
        for key, value in pairs:
            resources[(key, value)] += 1
        for field, data in room.get("data_references", {}).items():
            symbol = data.get("symbol")
            if symbol:
                symbols[(field, symbol)] += 1
    return resources, symbols


def reconcile_technical_sheets(
    sheets: dict[str, Any],
    reference: dict[str, Any],
) -> dict[str, Any]:
    sheets_rooms = sheets.get("rooms", [])
    reference_rooms = reference.get("rooms", [])
    if len(sheets_rooms) != EXPECTED or len(reference_rooms) != EXPECTED:
        raise ValueError("Technical sheets and RoomEntry reference must each contain 382 rooms.")
    sheet_ids = [str(room.get("room_id", "")) for room in sheets_rooms]
    reference_ids = [str(room.get("room_id", "")) for room in reference_rooms]
    if len(set(sheet_ids)) != EXPECTED or len(set(reference_ids)) != EXPECTED:
        raise ValueError("Duplicate room IDs found in technical sheets or reference metadata.")
    ref_by_id = {room["room_id"]: room for room in reference_rooms}
    if set(sheet_ids) != set(reference_ids):
        raise ValueError("Technical-sheet IDs do not exactly match RoomEntry reference IDs.")

    resource_consumers, symbol_consumers = _consumer_counts(reference_rooms)
    for sheet in sheets_rooms:
        ref = ref_by_id[sheet["room_id"]]
        fields = ref["room_entry"]
        tileset = ref["tileset_entry"]
        source = sheet.setdefault("source", {})
        source.update({
            "map_coordinate": fields["map_coordinate"],
            "room_index_0based": ref["source_room_index_0based"],
            "room_index_1based": ref["source_room_index_1based"],
            "tileset_entry_index": fields["tileset_entry_index"],
            "room_effect": fields["visual_effect"],
            "bg0_property": fields["bg0_property"],
            "bg1_property": fields["bg1_property"],
            "bg2_property": fields["bg2_property"],
            "bg3_property": fields["bg3_property"],
            "bg0_data": fields["bg0_data_symbol"],
            "bg1_data": fields["bg1_data_symbol"],
            "bg2_data": fields["bg2_data_symbol"],
            "clipdata_data": fields["clipdata_symbol"],
            "bg3_data": fields["bg3_data_symbol"],
            "bg3_scrolling": fields["bg3_scrolling"],
            "transparency": fields["transparency"],
            "music_track": fields["music_track"],
            "resource_indices": tileset["resource_indices"],
            "resource_symbols": tileset["resource_symbols"],
            "default_spriteset_id": fields["default_spriteset_id"],
            "first_spriteset_event": fields["first_spriteset_event"],
            "first_spriteset_id": fields["first_spriteset_id"],
            "second_spriteset_event": fields["second_spriteset_event"],
            "second_spriteset_id": fields["second_spriteset_id"],
            "source_reference_entry": {
                "source_array": ref["provenance"]["room_entry_array"],
                "source_index": ref["source_room_index_0based"],
                "entry_fields": fields,
                "tileset_entry": tileset,
                "data_references": ref.get("data_references", {}),
                "commit": ref["provenance"]["commit"],
            },
            "reference_entry_audit": "verified_against_pinned_decomp_entry",
        })

        sheet["shared_resource_consumers"] = {}
        for key, value in [
            ("tileset_entry_index", fields["tileset_entry_index"]),
            *tileset["resource_indices"].items(),
        ]:
            sheet["shared_resource_consumers"][key] = {
                "index": value,
                "room_consumers": resource_consumers[(key, value)],
            }
        sheet["shared_resource_consumers"]["source_data_symbols"] = {}
        for field, data in ref.get("data_references", {}).items():
            symbol = data.get("symbol")
            if symbol:
                sheet["shared_resource_consumers"]["source_data_symbols"][field] = {
                    "symbol": symbol,
                    "room_consumers": symbol_consumers[(field, symbol)],
                }

        extraction = sheet.setdefault("extraction", {})
        extraction["source_room_entry"] = fields
        extraction["data_references"] = ref.get("data_references", {})
        if ref.get("scroll_data") is not None:
            extraction["scroll_data_reference"] = ref["scroll_data"]

        status = sheet.setdefault("status", {})
        status["source_reference_entry"] = "verified_against_pinned_decomp_commit"
        status["resource_declaration_lengths"] = "populated_where_room_header_declares_size"
        status["exact_rom_match"] = "not_checked"
        # Preserve already-extracted dimensions/layer declarations; they are independent
        # metadata from each room source file, not derived from this RoomEntry lookup.

    sheets["created_date"] = "2026-11-03"
    sheets["source_code_reference"] = reference.get("source", {})
    sheets["status"] = (
        "reference_room_entry_fields_reconciled_reference_dimensions_populated_"
        "full_maps_collision_contents_and_private_rom_match_pending"
    )
    sheets["scope_note"] = (
        str(sheets.get("scope_note", "")).rstrip()
        + " RoomEntry coordinates, tileset entries and resource references were "
          "reconciled using the correct zero-based C room index and a pinned "
          "decompilation commit. Existing dimension/layer declarations were preserved. "
          "This does not decode map payloads or verify the user's private ROM."
    )
    return sheets


def sync_master_coordinates(master_text: str, registry: dict[str, Any]) -> tuple[str, int]:
    coordinates = {
        room["room_id"]: room["source"]["map_coordinate"]
        for room in registry.get("rooms", [])
    }
    if len(coordinates) != EXPECTED:
        raise ValueError("Registry must contain 382 unique room IDs before updating master coordinates.")
    row_re = re.compile(
        r"^(\|\s*`(L\d{2}_R\d{3})`\s*\|\s*\d+\s*\|[^\n]*?\|[^\n]*?\|\s*)"
        r"\(\s*\d+\s*,\s*\d+\s*\)(\s*\|)$",
        re.MULTILINE,
    )
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        room_id = match.group(2)
        coordinate = coordinates.get(room_id)
        if coordinate is None:
            return match.group(0)
        changed += 1
        return f"{match.group(1)}({coordinate['x']}, {coordinate['y']}){match.group(3)}"

    updated = row_re.sub(replace, master_text)
    if changed != EXPECTED:
        raise ValueError(f"Expected to reconcile 382 master-plan coordinate rows; updated {changed}.")
    old_method = (
        "3. El rol de sala es una asignación creativa inicial basada en el mapa estratégico: "
        "orden de `map_y`, después `map_x` y finalmente índice original. "
        "Las coordenadas no demuestran conexiones físicas ni puertas."
    )
    new_method = (
        "3. Los roles y nombres son asignaciones creativas iniciales y se conservan como borrador. "
        "La auditoría del 3 de noviembre corrigió las coordenadas y los recursos del cruce CSV "
        "anterior usando el índice C real `room_index_0based`; por tanto, la distribución "
        "geográfica de roles debe revisarse con las coordenadas corregidas antes de fijar mapas. "
        "Las coordenadas no demuestran conexiones físicas ni puertas."
    )
    updated = updated.replace(old_method, new_method)
    section = (
        "\n\n## Corrección técnica de índice de sala — 3 de noviembre de 2026\n\n"
        "El cruce CSV del 2 de noviembre tenía desplazados respecto a las entradas C los campos "
        "de posición, tileset y recursos. Se corrigieron los 382 registros enlazando cada ID con "
        "`sAreaRoomEntryPointers[area][room_index_0based]` y resolviendo "
        "`sTilesetEntries[tileset]` en el commit "
        "`de76565c897c05838503717db9aa2adfe92aeba3` de `metroidret/mf`. "
        "Nuevo cruce: [CSV de RoomEntry corregido](../../recovery/analysis/"
        "ROOM_ENTRY_REFERENCE_CROSSWALK_2026-11-03.csv) y [registro JSON](../../data/world/"
        "sector-cero-room-entry-reference-v1.json). Los roles creativos se conservan, pero "
        "su distribución geográfica debe revisarse de nuevo. Esta reconciliación no equivale "
        "a una verificación binaria de la ROM privada.\n"
    )
    if "## Corrección técnica de índice de sala — 3 de noviembre de 2026" not in updated:
        updated += section
    return updated, changed


def write_reference_csv(reference: dict[str, Any], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "room_id", "level_id", "neighborhood", "source_area",
        "room_index_0based", "room_index_1based", "map_x", "map_y",
        "tileset_entry_index", "bg0_property", "bg1_property", "bg2_property",
        "bg3_property", "bg0_data_symbol", "bg1_data_symbol", "bg2_data_symbol",
        "clipdata_symbol", "bg3_data_symbol", "bg3_scrolling", "transparency",
        "visual_effect", "music_track", "tile_graphics_resource", "palette_resource",
        "background_graphics_resource", "tilemap_resource", "animated_tileset",
        "animated_palette", "default_spriteset_id", "default_sprite_records",
        "first_spriteset_event", "first_spriteset_id", "first_sprite_records",
        "second_spriteset_event", "second_spriteset_id", "second_sprite_records",
        "bg0_bytes", "bg1_bytes", "bg2_bytes", "clipdata_bytes", "bg3_bytes",
        "source_commit",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for room in reference.get("rooms", []):
            fields = room["room_entry"]
            resources = room["tileset_entry"]["resource_indices"]
            data = room.get("data_references", {})
            row = {
                "room_id": room["room_id"],
                "level_id": room["level_id"],
                "neighborhood": room["neighborhood"],
                "source_area": room["source_game_area"],
                "room_index_0based": room["source_room_index_0based"],
                "room_index_1based": room["source_room_index_1based"],
                "map_x": fields["map_coordinate"]["x"],
                "map_y": fields["map_coordinate"]["y"],
                "tileset_entry_index": fields["tileset_entry_index"],
                "bg0_property": fields["bg0_property"],
                "bg1_property": fields["bg1_property"],
                "bg2_property": fields["bg2_property"],
                "bg3_property": fields["bg3_property"],
                "bg0_data_symbol": fields["bg0_data_symbol"],
                "bg1_data_symbol": fields["bg1_data_symbol"],
                "bg2_data_symbol": fields["bg2_data_symbol"],
                "clipdata_symbol": fields["clipdata_symbol"],
                "bg3_data_symbol": fields["bg3_data_symbol"],
                "bg3_scrolling": fields["bg3_scrolling"],
                "transparency": fields["transparency"],
                "visual_effect": fields["visual_effect"],
                "music_track": fields["music_track"],
                "tile_graphics_resource": resources["tile_graphics"],
                "palette_resource": resources["palette"],
                "background_graphics_resource": resources["background_graphics"],
                "tilemap_resource": resources["tilemap"],
                "animated_tileset": resources["animated_tileset"],
                "animated_palette": resources["animated_palette"],
                "default_spriteset_id": fields["default_spriteset_id"],
                "default_sprite_records": (data.get("default_sprites") or {}).get("element_count"),
                "first_spriteset_event": fields["first_spriteset_event"],
                "first_spriteset_id": fields["first_spriteset_id"],
                "first_sprite_records": (data.get("event_sprites_1") or {}).get("element_count"),
                "second_spriteset_event": fields["second_spriteset_event"],
                "second_spriteset_id": fields["second_spriteset_id"],
                "second_sprite_records": (data.get("event_sprites_2") or {}).get("element_count"),
                "bg0_bytes": (data.get("bg0") or {}).get("byte_count"),
                "bg1_bytes": (data.get("bg1") or {}).get("byte_count"),
                "bg2_bytes": (data.get("bg2") or {}).get("byte_count"),
                "clipdata_bytes": (data.get("clipdata") or {}).get("byte_count"),
                "bg3_bytes": (data.get("bg3") or {}).get("byte_count"),
                "source_commit": room["provenance"]["commit"],
            }
            writer.writerow(row)
    return len(reference.get("rooms", []))


def append_audit_note(path: Path, reference: dict[str, Any]) -> None:
    heading = "## Reconciliación de metadatos RoomEntry — 3 de noviembre de 2026"
    old = path.read_text(encoding="utf-8") if path.exists() else "# Auditoría de producción\n"
    if heading in old:
        return
    summary = reference.get("summary", {})
    note = f"""
\n\n{heading}

La comprobación de las 382 entradas `RoomEntryRom` detectó un desfase de un índice en
el CSV técnico anterior. La asociación se corrigió usando `room_index_0based` como
índice directo de la tabla de habitaciones y resolviendo el tileset mediante
`sTilesetEntries[98]`.

- Entradas RoomEntry conciliadas: **{summary.get("source_entry_count", 382)}/382**.
- Coordenadas corregidas: **{summary.get("corrected_coordinates", "n/d")}**.
- Entradas de tileset corregidas: **{summary.get("corrected_tileset", "n/d")}**.
- Propiedades BG0 corregidas: **{summary.get("corrected_bg0", "n/d")}**.
- Música corregida: **{summary.get("corrected_music", "n/d")}**.

Se conservan los roles creativos y lotes, pero la relación rol↔posición geográfica debe
revisarse porque el primer reparto utilizó coordenadas desplazadas. Este ajuste es de
metadatos del código de referencia: no compara bytes con la ROM privada y no extrae
los contenidos comprimidos BG/clipdata.

Archivos: [RoomEntry JSON](../../data/world/sector-cero-room-entry-reference-v1.json),
[RoomEntry CSV](../../recovery/analysis/ROOM_ENTRY_REFERENCE_CROSSWALK_2026-11-03.csv).
"""
    path.write_text(old.rstrip() + note, encoding="utf-8")


def sync_project(
    registry_path: Path,
    reference_path: Path,
    sheets_path: Path,
    master_path: Path,
    audit_path: Path,
    csv_path: Path,
) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    sheets = json.loads(sheets_path.read_text(encoding="utf-8"))
    merged = reconcile_technical_sheets(sheets, reference)
    master_text = master_path.read_text(encoding="utf-8")
    updated_master, master_rows = sync_master_coordinates(master_text, registry)
    merged["created_date"] = "2026-11-03"
    sheets_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    master_path.write_text(updated_master, encoding="utf-8")
    csv_rows = write_reference_csv(reference, csv_path)
    append_audit_note(audit_path, reference)
    return {
        "status": "PASS",
        "room_count": len(reference["rooms"]),
        "technical_sheets_reconciled": len(merged["rooms"]),
        "master_coordinate_rows_updated": master_rows,
        "crosswalk_csv_rows": csv_rows,
        "reference_source_commit": reference["source"]["commit"],
        "private_rom_checked": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--technical-sheets", type=Path, default=DEFAULT_SHEETS)
    parser.add_argument("--master-plan", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--audit-doc", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--csv-out", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    try:
        result = sync_project(
            args.registry, args.reference, args.technical_sheets,
            args.master_plan, args.audit_doc, args.csv_out,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"RoomEntry sync failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
