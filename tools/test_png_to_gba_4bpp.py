#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from png_to_gba_4bpp import (
    encode_4bpp_tiles,
    decode_4bpp_tiles,
    rgb_to_bgr555,
    pack_palette_bgr555,
    read_indexed_pixels,
    gba_lz77_compress,
    gba_lz77_decompress,
    export_atlas,
)


class TestGba4bppEncoder(unittest.TestCase):
    def test_even_pixel_is_low_nibble(self) -> None:
        pixels = [0] * 64
        pixels[0:8] = [1, 2, 3, 4, 5, 6, 7, 8]
        encoded = encode_4bpp_tiles(pixels, 8, 8)
        self.assertEqual(encoded[:4], bytes([0x21, 0x43, 0x65, 0x87]))
        self.assertEqual(len(encoded), 32)

    def test_two_tiles_are_written_left_to_right(self) -> None:
        width, height = 16, 8
        pixels = [0] * (width * height)
        for y in range(height):
            for x in range(8):
                pixels[y * width + x] = 1
            for x in range(8, 16):
                pixels[y * width + x] = 2
        encoded = encode_4bpp_tiles(pixels, width, height)
        self.assertEqual(len(encoded), 64)
        self.assertEqual(encoded[:4], bytes([0x11] * 4))
        self.assertEqual(encoded[32:36], bytes([0x22] * 4))
        self.assertEqual(decode_4bpp_tiles(encoded, width, height), pixels)

    def test_palette_is_bgr555_little_endian(self) -> None:
        self.assertEqual(rgb_to_bgr555((255, 0, 0)), 0x001F)
        self.assertEqual(rgb_to_bgr555((0, 0, 255)), 0x7C00)
        palette = pack_palette_bgr555([(255, 0, 0), (0, 0, 255)])
        self.assertEqual(palette[:4], bytes([0x1F, 0x00, 0x00, 0x7C]))
        self.assertEqual(len(palette), 32)

    def test_transparent_source_pixels_map_to_index_zero(self) -> None:
        image = Image.new("P", (8, 8))
        palette = []
        for index in range(256):
            palette.extend((index, index, index))
        image.putpalette(palette)
        image.putdata([2] + [1] * 63)
        image.info["transparency"] = bytes([255, 255, 0] + [255] * 253)

        width, height, pixels, colors, has_alpha = read_indexed_pixels(image)
        self.assertTrue(has_alpha)
        self.assertEqual(pixels[0], 0)
        self.assertEqual(pixels[1], 1)
        self.assertEqual(width, 8)
        self.assertEqual(height, 8)
        self.assertEqual(len(colors), 16)

    def test_semitransparency_is_rejected(self) -> None:
        image = Image.new("P", (8, 8))
        palette = [0, 0, 0] * 256
        image.putpalette(palette)
        image.putdata([1] * 64)
        image.info["transparency"] = bytes([255, 128] + [255] * 254)
        with self.assertRaisesRegex(ValueError, "Semi-transparent"):
            read_indexed_pixels(image)

    def test_non_4bpp_palette_index_is_rejected(self) -> None:
        image = Image.new("P", (8, 8))
        image.putpalette([0, 0, 0] * 256)
        image.putdata([16] + [1] * 63)
        with self.assertRaisesRegex(ValueError, "indices above 15"):
            read_indexed_pixels(image)

    def test_lz77_round_trip_repetitive_and_mixed_data(self) -> None:
        sample = (b"VILLA-DUARTE-" * 300) + bytes(range(256)) * 4
        compressed = gba_lz77_compress(sample)
        self.assertEqual(compressed[0], 0x10)
        self.assertEqual(gba_lz77_decompress(compressed), sample)
        self.assertEqual(len(compressed) % 4, 0)

    def test_export_writes_tiles_palette_compressed_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "atlas.png"
            output = root / "private"
            image = Image.new("P", (16, 8))
            image.putpalette([0, 0, 0, 255, 0, 0] + [0, 0, 0] * 254)
            image.putdata([1] * 64 + [0] * 64)
            image.save(source, transparency=0)

            report = export_atlas(source, output, "scenario")
            self.assertTrue((output / "scenario.4bpp").is_file())
            self.assertTrue((output / "scenario.4bpp.lz").is_file())
            self.assertTrue((output / "scenario.bgr555.pal").is_file())
            self.assertTrue((output / "scenario.export.json").is_file())
            self.assertEqual(report["tile_count"], 2)
            self.assertEqual(report["tile_bytes"], 64)
            self.assertTrue(report["validation"]["4bpp_round_trip"])
            self.assertTrue(report["validation"]["lz77_round_trip"])
            stored = json.loads((output / "scenario.export.json").read_text())
            self.assertFalse(stored["validation"]["runtime_tested"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
