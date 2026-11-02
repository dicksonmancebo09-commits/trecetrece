#!/usr/bin/env python3
"""Structural audit for the 382-room LATINO AMÉRICA Zector Cero plan.

This checks design IDs, source indices, door targets, five-batch coverage and
technical-sheet coverage. It does not inspect a private ROM or claim gameplay QA.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/world/sector-cero-room-registry-v1.json"
MANIFEST_PATH = ROOT / "data/world/sector-cero-production-manifest-v1.json"
SHEETS_PATH = ROOT / "data/world/sector-cero-room-technical-sheets-v1.json"
MASTER_PATH = ROOT / "docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md"
EXPECTED_LEVEL_COUNTS = {
    "L01": 87, "L02": 54, "L03": 61, "L04": 39,
    "L05": 48, "L06": 52, "L07": 41,
}
EXPECTED_BATCH_COUNTS = {1: 87, 2: 87, 3: 87, 4: 87, 5: 34}


def extract_master_ids(markdown: str) -> list[str]:
    marker = "## Estado de todas las salas"
    if marker not in markdown:
        raise ValueError("Master plan has no 'Estado de todas las salas' section.")
    section = markdown.split(marker, 1)[1]
    # The room roster stores the design ID in the first column of each row.
    return re.findall(r"^\\|\\s*`(L\\d{2}_R\\d{3})`\\s*\\|", section, re.MULTILINE)


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def audit_data(
    registry: dict[str, Any],
    manifest: dict[str, Any],
    technical_sheets: dict[str, Any],
    master_ids: list[str],
    batch_documents: dict[int, dict[str, Any]] | None = None,
    expected_level_counts: dict[str, int] | None = None,
    expected_batch_counts: dict[int, int] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    expected_level_counts = expected_level_counts or EXPECTED_LEVEL_COUNTS
    expected_batch_counts = expected_batch_counts or EXPECTED_BATCH_COUNTS
    rooms = registry.get("rooms", [])
    ids = [str(room.get("room_id", "")) for room in rooms]
    id_set = set(ids)
    duplicates = _duplicates(ids)
    if len(rooms) != 382:
        errors.append(f"Expected 382 registry records; found {len(rooms)}.")
    if duplicates:
        errors.append(f"Duplicate registry room IDs: {duplicates[:12]}.")
    if len(id_set) != len(rooms):
        errors.append("Registry room IDs are not unique.")

    master_duplicates = _duplicates(master_ids)
    master_set = set(master_ids)
    if master_duplicates:
        errors.append(f"Duplicate IDs in master roster: {master_duplicates[:12]}.")
    missing_from_registry = sorted(master_set - id_set)
    missing_from_master = sorted(id_set - master_set)
    if missing_from_registry or missing_from_master:
        errors.append(
            "Master/registry mismatch: "
            f"missing_from_registry={missing_from_registry[:12]}, "
            f"missing_from_master={missing_from_master[:12]}."
        )

    levels = registry.get("levels", [])
    level_actual = Counter(str(room.get("level_id", "")) for room in rooms)
    level_counts = {}
    for level_id, expected in expected_level_counts.items():
        actual = level_actual.get(level_id, 0)
        level_counts[level_id] = {"expected": expected, "actual": actual}
        if actual != expected:
            errors.append(f"{level_id}: expected {expected} rooms, found {actual}.")
    declared_levels = {str(level.get("level_id")): int(level.get("room_count", -1)) for level in levels}
    for level_id, expected in expected_level_counts.items():
        if declared_levels.get(level_id) != expected:
            errors.append(f"{level_id}: registry level declaration is not {expected}.")

    source_indices: dict[str, list[int]] = defaultdict(list)
    bad_index_pairs = []
    for room in rooms:
        source = room.get("source", {})
        area = str(source.get("source_game_area", ""))
        one = source.get("room_index_1based")
        zero = source.get("room_index_0based")
        if isinstance(one, int):
            source_indices[area].append(one)
        if not isinstance(one, int) or not isinstance(zero, int) or one != zero + 1:
            bad_index_pairs.append(room.get("room_id"))
    if bad_index_pairs:
        errors.append(f"1-based/0-based source index mismatch in {len(bad_index_pairs)} rooms.")
    source_coverage = {}
    for level in levels:
        area = str(level.get("source_game_area", ""))
        expected = int(level.get("room_count", 0))
        values = source_indices.get(area, [])
        coverage_ok = sorted(values) == list(range(1, expected + 1))
        source_coverage[area] = {"expected": expected, "actual": len(values), "complete": coverage_ok}
        if not coverage_ok:
            errors.append(f"Source index coverage incomplete for {area}.")

    door_count = 0
    dangling_defaults = []
    dangling_overrides = []
    for room in rooms:
        for door in room.get("source_doors", []) or []:
            door_count += 1
            default = (door.get("default_destination") or {}).get("room_id")
            if default and default not in id_set:
                dangling_defaults.append((room.get("room_id"), door.get("door_index"), default))
            for override in door.get("event_overrides", []) or []:
                target = override.get("destination_room_id")
                if target and target not in id_set:
                    dangling_overrides.append((room.get("room_id"), door.get("door_index"), target))
    if dangling_defaults:
        errors.append(f"{len(dangling_defaults)} door default destinations point to unknown rooms.")
    if dangling_overrides:
        errors.append(f"{len(dangling_overrides)} event overrides point to unknown rooms.")

    batches = manifest.get("batches", [])
    batch_counts = {}
    assigned_ids: list[str] = []
    batch_mismatches = []
    for batch in batches:
        number = int(batch.get("batch", 0))
        entries = batch.get("rooms", [])
        batch_ids = [str(entry.get("room_id", "")) for entry in entries]
        batch_counts[number] = len(batch_ids)
        assigned_ids.extend(batch_ids)
        expected = expected_batch_counts.get(number)
        if expected is None or len(batch_ids) != expected or int(batch.get("room_count", len(batch_ids))) != expected:
            batch_mismatches.append(number)
        if len(set(batch_ids)) != len(batch_ids):
            errors.append(f"Batch {number} contains duplicate room IDs.")
        unknown = sorted(set(batch_ids) - id_set)
        if unknown:
            errors.append(f"Batch {number} contains unknown room IDs: {unknown[:8]}.")
    if set(batch_counts) != set(expected_batch_counts):
        errors.append(f"Expected batches 1–5; found {sorted(batch_counts)}.")
    if batch_mismatches:
        errors.append(f"Batch count mismatch in: {sorted(batch_mismatches)}.")
    if len(assigned_ids) != 382 or len(set(assigned_ids)) != 382:
        errors.append(f"Five batches must assign 382 unique rooms; found {len(assigned_ids)} assignments and {len(set(assigned_ids))} unique IDs.")
    if set(assigned_ids) != id_set:
        errors.append("Five-batch assignment does not exactly cover the room registry.")

    batch_document_checks = {}
    for number, document in (batch_documents or {}).items():
        doc_ids = [str(entry.get("id", "")) for entry in document.get("rooms", [])]
        manifest_batch = next((b for b in batches if int(b.get("batch", 0)) == number), None)
        expected_ids = [str(entry.get("room_id", "")) for entry in (manifest_batch or {}).get("rooms", [])]
        ok = doc_ids == expected_ids
        batch_document_checks[str(number)] = {"rooms": len(doc_ids), "matches_manifest": ok}
        if not ok:
            errors.append(f"Batch JSON {number} does not match the production manifest.")

    sheet_rooms = technical_sheets.get("rooms", [])
    sheet_ids = [str(room.get("room_id", "")) for room in sheet_rooms]
    sheet_duplicates = _duplicates(sheet_ids)
    if sheet_duplicates:
        errors.append(f"Duplicate technical sheets: {sheet_duplicates[:12]}.")
    if set(sheet_ids) != id_set or len(sheet_ids) != 382:
        errors.append("Technical sheets do not cover exactly the 382 registry rooms.")
    pending_geometry = sum(1 for room in sheet_rooms if (room.get("status") or {}).get("geometry") == "pending_rom_extract")
    pending_collision = sum(1 for room in sheet_rooms if (room.get("status") or {}).get("collision") == "pending_rom_extract")
    pending_runtime = sum(1 for room in sheet_rooms if (room.get("status") or {}).get("runtime_test") == "not_tested")
    if pending_geometry or pending_collision or pending_runtime:
        warnings.append(
            f"Technical work remains: geometry={pending_geometry}, "
            f"collision={pending_collision}, runtime_not_tested={pending_runtime}."
        )

    return {
        "status": "PASS" if not errors else "FAIL",
        "project": registry.get("project"),
        "registry_rooms": len(rooms),
        "registry_unique_ids": len(id_set),
        "master_roster_ids": len(master_ids),
        "master_roster_unique_ids": len(master_set),
        "master_registry_missing_from_registry": missing_from_registry,
        "master_registry_missing_from_master": missing_from_master,
        "duplicate_registry_ids": duplicates,
        "duplicate_master_ids": master_duplicates,
        "level_counts": level_counts,
        "source_index_coverage": source_coverage,
        "source_door_records": door_count,
        "dangling_default_destinations": len(dangling_defaults),
        "dangling_event_overrides": len(dangling_overrides),
        "batch_counts": batch_counts,
        "batch_document_checks": batch_document_checks,
        "technical_sheets": len(sheet_rooms),
        "pending_geometry_sheets": pending_geometry,
        "pending_collision_sheets": pending_collision,
        "runtime_not_tested_sheets": pending_runtime,
        "errors": errors,
        "warnings": warnings,
        "scope_boundary": "Structural data audit only; no private ROM bytes, emulator runtime or gameplay are tested.",
    }


def load_and_audit(root: Path = ROOT) -> dict[str, Any]:
    def load(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    registry = load(root / "data/world/sector-cero-room-registry-v1.json")
    manifest = load(root / "data/world/sector-cero-production-manifest-v1.json")
    sheets = load(root / "data/world/sector-cero-room-technical-sheets-v1.json")
    master_text = (root / "docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md").read_text(encoding="utf-8")
    batch_docs = {
        number: load(root / f"data/world/sector-cero-room-batch-{number:02d}-v1.json")
        for number in range(1, 6)
    }
    return audit_data(registry, manifest, sheets, extract_master_ids(master_text), batch_docs)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit 382 room IDs, source doors, five production batches and technical sheets.")
    parser.add_argument("--json-out", type=Path, help="Optional path for a machine-readable report.")
    parser.add_argument("--fail-on-pending", action="store_true", help="Return failure while geometry/collision/runtime work remains.")
    args = parser.parse_args()
    try:
        report = load_and_audit()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"AUDIT ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    if report["errors"]:
        return 1
    if args.fail_on_pending and (report["pending_geometry_sheets"] or report["pending_collision_sheets"] or report["runtime_not_tested_sheets"]):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
