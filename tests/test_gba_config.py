from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "gba_lab.json").read_text(encoding="utf-8"))


def n(value: str | int) -> int:
    return value if isinstance(value, int) else int(value, 0)


class TestGbaLabConfig(unittest.TestCase):
    def test_known_profiles_are_pinned(self):
        profiles = CONFIG["profiles"]
        for name in ("metroid_fusion_us_clean", "urban_opening_v1_0", "zector_cero_v1_5", "zector_cero_v1_6", "zector_cero_v1_7"):
            profile = profiles[name]
            self.assertEqual(profile["size_bytes"], 8 * 1024 * 1024, name)
            self.assertRegex(profile["sha256"], r"^[0-9a-f]{64}$", name)
            self.assertEqual(len(profile["title"]) <= 12, True, name)
        self.assertIsNone(profiles["gba_candidate_unpinned"]["sha256"])

    def test_gba_tile_address_calculation_matches_config(self):
        room = CONFIG["gba_hardware"]["room0_v1_5"]
        char_base = n(room["bg_character_base"])
        gfx_address = n(room["tile_graphics_vram_offset"])
        computed_base = (gfx_address - char_base) // CONFIG["gba_hardware"]["background_4bpp"]["bytes_per_tile"]
        self.assertEqual(computed_base, room["local_tile_base_index"])
        self.assertEqual(room["transparent_tile_hardware_id"], room["local_tile_base_index"] + room["tile_count"] - 1)
        self.assertEqual(room["transparent_metatile_id"], 383)
        self.assertEqual(room["map_width_blocks"], 34)
        self.assertEqual(room["map_height_blocks"], 14)

    def test_title_reserved_ranges_do_not_overlap(self):
        title = CONFIG["gba_hardware"]["custom_title_v1_5"]
        ranges = [
            (n(title["map_rom_offset"]), n(title["map_reserved_length"]), "map"),
            (n(title["palette_rom_offset"]), n(title["palette_reserved_length"]), "palette"),
            (n(title["gfx_rom_offset"]), n(title["gfx_reserved_length"]), "gfx")
        ]
        for start, length, name in ranges:
            self.assertGreater(length, 0)
            self.assertGreaterEqual(start, 0)
            self.assertLess(start + length, 8 * 1024 * 1024)
        sorted_ranges = sorted(ranges)
        for current, next_range in zip(sorted_ranges, sorted_ranges[1:]):
            self.assertLessEqual(current[0] + current[1], next_range[0], f"{current[2]} overlaps {next_range[2]}")

    def test_known_build_resource_slots_fit_and_do_not_overlap(self):
        resources = CONFIG["profiles"]["zector_cero_v1_7"]["resource_ranges"]
        spans = []
        for item in resources:
            offset = n(item["offset"])
            used = int(item["used_bytes"])
            reserved = int(item["reserved_bytes"])
            self.assertGreater(used, 0, item["name"])
            self.assertGreaterEqual(reserved, used, item["name"])
            self.assertGreaterEqual(offset, 0, item["name"])
            self.assertLessEqual(offset + reserved, 8 * 1024 * 1024, item["name"])
            spans.append((offset, offset + reserved, item["name"]))
        spans.sort()
        for first, second in zip(spans, spans[1:]):
            self.assertLessEqual(first[1], second[0], f"{first[2]} overlaps {second[2]}")

    def test_room_map_resource_ranges_are_contiguous_and_consistent(self):
        profile = CONFIG["profiles"]["zector_cero_v1_7"]
        checks = profile["room_map_checks"]
        self.assertEqual(len(checks), 3)
        spans = []
        for item in checks:
            start = n(item["offset"])
            used = int(item["used_bytes"])
            reserved = n(item["reserved_bytes"])
            self.assertGreater(used, 0, item["name"])
            self.assertGreaterEqual(reserved, used, item["name"])
            self.assertLessEqual(start + reserved, 8 * 1024 * 1024, item["name"])
            spans.append((start, start + reserved, item["name"]))
        spans.sort()
        for first, second in zip(spans, spans[1:]):
            self.assertLessEqual(first[1], second[0], f"{first[2]} overlaps {second[2]}")
        bg1, bg2 = checks[1], checks[2]
        self.assertEqual((bg1["expected_width"], bg1["expected_height"]), (34, 14))
        self.assertEqual((bg2["expected_width"], bg2["expected_height"]), (34, 14))
        self.assertEqual(bg1["used_bytes"], 22)
        self.assertEqual(bg2["used_bytes"], 414)

    def test_all_configured_pointer_targets_fit_in_rom(self):
        for area in ("room0_v1_5", "custom_title_v1_5"):
            for row in CONFIG["gba_hardware"][area]["pointer_sites"]:
                target = n(row["expected_target_bus_address"])
                rom_offset = target - n(CONFIG["gba_hardware"]["rom_window_base"])
                self.assertGreaterEqual(rom_offset, 0, row["purpose"])
                self.assertLess(rom_offset, 8 * 1024 * 1024, row["purpose"])
                self.assertTrue(row["file_offset"].startswith("0x"))


if __name__ == "__main__":
    unittest.main()
