from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "extract_reference_room_metadata.py"
SPEC = importlib.util.spec_from_file_location("extract_reference_room_metadata", MODULE)
assert SPEC and SPEC.loader
extractor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extractor)


SAMPLE = """
const u8 sSector1_1_Clipdata[76] = {
    19, // Room width
    14, // Room height
    _INCBIN_U8("data/rooms/sector_1/sector_1_1_clipdata.rle")
};
const u8 sSector1_1_Bg1[158] = {
    19, // Room width
    14, // Room height
    _INCBIN_U8("data/rooms/sector_1/sector_1_1_bg1.rle")
};
const u8 sSector1_1_Spriteset0[ENEMY_ROOM_DATA_ARRAY_SIZE(2)] = {
    10, 9, SSP_UNINFECTED_OR_BOSS | SPRITESET_IDX(0),
    ROOM_SPRITE_DATA_TERMINATOR
};
const u8 sSector1_1_Spriteset1[ENEMY_ROOM_DATA_ARRAY_SIZE(3)] = {
    10, 9, SPRITESET_IDX(1),
    12, 4, SPRITESET_IDX(2),
    ROOM_SPRITE_DATA_TERMINATOR
};
"""


class TestReferenceRoomMetadata(unittest.TestCase):
    def test_source_path(self):
        self.assertEqual(
            extractor.source_path("Main Deck", 12),
            "src/data/rooms/main_deck/main_deck_12.c",
        )
        self.assertEqual(
            extractor.source_path("Sector 6", 40),
            "src/data/rooms/sector_6/sector_6_40.c",
        )

    def test_parse_dimensions_layers_and_sprite_counts(self):
        result = extractor.parse_room_source(SAMPLE, "L02_R002")
        self.assertEqual(result["dimensions_blocks"], {"width": 19, "height": 14})
        self.assertEqual(result["dimensions_pixels"], {"width": 304, "height": 224})
        self.assertEqual(result["layers"]["clipdata"]["declared_array_bytes"], 76)
        self.assertEqual(result["layers"]["bg1"]["declared_array_bytes"], 158)
        self.assertEqual(result["spriteset_placement_counts"], {"variant_0": 1, "variant_1": 2})
        self.assertEqual(result["layer_dimension_conflicts"], [])

    def test_missing_clipdata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no Clipdata dimensions"):
            extractor.parse_room_source("const u8 sRoom_Bg1[10] = { 3, // Room width\n 4, // Room height };")

    def test_layer_dimension_mismatch_is_reported(self):
        source = SAMPLE.replace("19, // Room width\n    14, // Room height\n    _INCBIN_U8(\"data/rooms/sector_1/sector_1_1_bg1.rle\")",
                                "19, // Room width\n    13, // Room height\n    _INCBIN_U8(\"data/rooms/sector_1/sector_1_1_bg1.rle\")")
        result = extractor.parse_room_source(source)
        self.assertEqual(result["layer_dimension_conflicts"], ["bg1"])


if __name__ == "__main__":
    unittest.main()
