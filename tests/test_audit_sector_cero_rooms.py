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

    def test_pinned_room_entry_mismatch_fails(self):
        registry, manifest, sheets, master = fixture()
        source_reference = {
            "rooms": [
                {
                    "room_id": "L01_R001",
                    "source_game_area": "Main Deck",
                    "source_room_index_0based": 0,
                    "source_room_index_1based": 1,
                    "room_entry": {
                        "map_coordinate": {"x": 2, "y": 3},
                        "tileset_entry_index": 5,
                        "bg0_data_symbol": "bg0",
                        "bg1_data_symbol": "bg1",
                        "bg2_data_symbol": "bg2",
                        "clipdata_symbol": "clip",
                        "bg3_data_symbol": "bg3",
                    },
                    "tileset_entry": {"resource_indices": {"tile_graphics": 1}},
                },
                {
                    "room_id": "L01_R002",
                    "source_game_area": "Main Deck",
                    "source_room_index_0based": 1,
                    "source_room_index_1based": 2,
                    "room_entry": {
                        "map_coordinate": {"x": 4, "y": 5},
                        "tileset_entry_index": 6,
                        "bg0_data_symbol": "bg0",
                        "bg1_data_symbol": "bg1",
                        "bg2_data_symbol": "bg2",
                        "clipdata_symbol": "clip",
                        "bg3_data_symbol": "bg3",
                    },
                    "tileset_entry": {"resource_indices": {"tile_graphics": 2}},
                },
            ]
        }
        registry["rooms"][0]["source"].update({
            "source_game_area": "Main Deck",
            "room_index_0based": 0, "room_index_1based": 1,
            "map_coordinate": {"x": 2, "y": 3}, "tileset_entry_index": 5,
            "resource_indices": {"tile_graphics": 1},
            "bg0_data": "bg0", "bg1_data": "bg1", "bg2_data": "bg2",
            "clipdata_data": "clip", "bg3_data": "bg3",
        })
        registry["rooms"][1]["source"].update({
            "source_game_area": "Main Deck",
            "room_index_0based": 1, "room_index_1based": 2,
            "map_coordinate": {"x": 4, "y": 5}, "tileset_entry_index": 6,
            "resource_indices": {"tile_graphics": 2},
            "bg0_data": "bg0", "bg1_data": "bg1", "bg2_data": "bg2",
            "clipdata_data": "clip", "bg3_data": "bg3",
        })
        result = audit.audit_data(
            registry, manifest, sheets, master,
            expected_level_counts={"L01": 2},
            expected_batch_counts={1: 2},
            source_reference=source_reference,
        )
        self.assertEqual(result["source_reference_checks"]["records"], 2)
        self.assertEqual(result["source_reference_checks"]["index_matches"], 2)
        self.assertEqual(result["status"], "PASS")
        registry["rooms"][0]["source"]["tileset_entry_index"] = 999
        result = audit.audit_data(
            registry, manifest, sheets, master,
            expected_level_counts={"L01": 2},
            expected_batch_counts={1: 2},
            source_reference=source_reference,
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("tileset_matches" in item for item in result["errors"]))

    def test_missing_master_room_fails(self):
        registry, manifest, sheets, master = fixture()
        result = audit.audit_data(registry, manifest, sheets, ["L01_R001"], expected_level_counts={"L01": 2}, expected_batch_counts={1: 2})
        self.assertTrue(any("Master/registry mismatch" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
