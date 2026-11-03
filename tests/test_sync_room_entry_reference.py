from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "sync_room_entry_reference.py"
SPEC = importlib.util.spec_from_file_location("sync_room_entry_reference", MODULE)
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def fixture():
    reference = {
        "source": {"commit": "abc123"},
        "rooms": [
            {
                "room_id": f"L01_R{i:03d}", "level_id": "L01", "neighborhood": "Villa Duarte",
                "source_game_area": "Main Deck", "source_room_index_0based": i - 1,
                "source_room_index_1based": i,
                "room_entry": {
                    "map_coordinate": {"x": i, "y": 2}, "tileset_entry_index": 3,
                    "visual_effect": "EFFECT_NONE", "bg0_property": "BG_PROP_NONE",
                    "bg1_property": "BG_PROP_RLE_COMPRESSED", "bg2_property": "BG_PROP_RLE_COMPRESSED",
                    "bg3_property": "BG_PROP_NONE", "bg0_data_symbol": "bg0", "bg1_data_symbol": "bg1",
                    "bg2_data_symbol": "bg2", "clipdata_symbol": "clip", "bg3_data_symbol": "bg3",
                    "bg3_scrolling": 0, "transparency": 0, "music_track": "MUSIC_MAIN_DECK_AMBIENCE",
                    "default_spriteset_id": 1, "first_spriteset_event": "EVENT_NONE",
                    "first_spriteset_id": 0, "second_spriteset_event": "EVENT_NONE",
                    "second_spriteset_id": 0,
                },
                "tileset_entry": {
                    "resource_indices": {"tile_graphics": 2, "palette": 2, "background_graphics": 1,
                                         "tilemap": 2, "animated_tileset": 0, "animated_palette": 0},
                    "resource_symbols": {"tile_graphics": "gfx", "palette": "pal",
                                         "background_graphics": "bgfx", "tilemap": "tmap"},
                },
                "data_references": {"bg0": {"symbol": "bg0", "byte_count": 4}},
                "provenance": {"room_entry_array": "rooms[0]", "commit": "abc123"},
            }
            for i in (1, 2)
        ],
        "summary": {"source_entry_count": 2},
    }
    sheets = {"rooms": [
        {"room_id": f"L01_R{i:03d}", "source": {"map_coordinate": {"x": 0, "y": 0}},
         "extraction": {"reference_dimensions_blocks": {"width": 10, "height": 8}},
         "status": {"geometry": "reference_dimensions_extracted_full_room_geometry_pending"}}
        for i in (1, 2)
    ]}
    registry = {"rooms": [
        {"room_id": f"L01_R{i:03d}", "source": {"map_coordinate": {"x": i, "y": 2}}}
        for i in (1, 2)
    ]}
    return reference, sheets, registry


class TestRoomEntrySync(unittest.TestCase):
    def test_reconciles_technical_sheets_and_preserves_dimensions(self):
        reference, sheets, _ = fixture()
        result = sync.reconcile_technical_sheets(sheets, reference)
        self.assertEqual(result["rooms"][0]["source"]["tileset_entry_index"], 3)
        self.assertEqual(result["rooms"][0]["shared_resource_consumers"]["tile_graphics"]["room_consumers"], 2)
        self.assertEqual(result["rooms"][0]["extraction"]["reference_dimensions_blocks"]["width"], 10)

    def test_master_plan_coordinates_update(self):
        _, _, registry = fixture()
        text = "## Estado de todas las salas\n| `L01_R001` | 1 | Name | role | (99, 99) |\n| `L01_R002` | 2 | Name | role | (98, 98) |"
        updated, count = sync.sync_master_coordinates(text, registry)
        self.assertEqual(count, 2)
        self.assertIn("(1, 2)", updated)
        self.assertIn("(2, 2)", updated)

    def test_reference_id_mismatch_fails(self):
        reference, sheets, _ = fixture()
        reference["rooms"].pop()
        with self.assertRaisesRegex(ValueError, "each contain 382"):
            sync.reconcile_technical_sheets(sheets, reference)


if __name__ == "__main__":
    unittest.main()
