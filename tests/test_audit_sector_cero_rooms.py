from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "audit_sector_cero_rooms.py"
SPEC = importlib.util.spec_from_file_location("audit_sector_cero_rooms", MODULE)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def fixture():
    registry = {
        "project": "LATINO AMÉRICA Zector Cero",
        "levels": [{"level_id": "L01", "room_count": 2, "source_game_area": "Main Deck"}],
        "rooms": [
            {"room_id": "L01_R001", "level_id": "L01", "source": {"source_game_area": "Main Deck", "room_index_1based": 1, "room_index_0based": 0}, "source_doors": [{"door_index": 1, "default_destination": {"room_id": "L01_R002"}, "event_overrides": []}]},
            {"room_id": "L01_R002", "level_id": "L01", "source": {"source_game_area": "Main Deck", "room_index_1based": 2, "room_index_0based": 1}, "source_doors": []},
        ],
    }
    manifest = {
        "batches": [
            {"batch": 1, "room_count": 2, "rooms": [{"room_id": "L01_R001"}, {"room_id": "L01_R002"}]}
        ]
    }
    sheets = {"rooms": [{"room_id": "L01_R001", "status": {}}, {"room_id": "L01_R002", "status": {}}]}
    return registry, manifest, sheets, ["L01_R001", "L01_R002"]


class TestRoomAudit(unittest.TestCase):
    def test_clean_fixture_passes_structural_checks(self):
        registry, manifest, sheets, master = fixture()
        result = audit.audit_data(registry, manifest, sheets, master, expected_level_counts={"L01": 2}, expected_batch_counts={1: 2})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["source_door_records"], 1)

    def test_duplicate_room_id_fails(self):
        registry, manifest, sheets, master = fixture()
        registry["rooms"].append(dict(registry["rooms"][0]))
        result = audit.audit_data(registry, manifest, sheets, master, expected_level_counts={"L01": 2}, expected_batch_counts={1: 2})
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Duplicate registry room IDs" in item for item in result["errors"]))

    def test_dangling_door_target_fails(self):
        registry, manifest, sheets, master = fixture()
        registry["rooms"][0]["source_doors"][0]["default_destination"]["room_id"] = "L01_R999"
        result = audit.audit_data(registry, manifest, sheets, master, expected_level_counts={"L01": 2}, expected_batch_counts={1: 2})
        self.assertTrue(any("door default destinations" in item for item in result["errors"]))

    def test_missing_master_room_fails(self):
        registry, manifest, sheets, master = fixture()
        result = audit.audit_data(registry, manifest, sheets, ["L01_R001"], expected_level_counts={"L01": 2}, expected_batch_counts={1: 2})
        self.assertTrue(any("Master/registry mismatch" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
