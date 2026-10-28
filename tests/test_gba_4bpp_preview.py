"""Synthetic tests for the GBA 4bpp tile PNG previewer."""
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "gba_4bpp_preview.py"
SPEC = spec_from_file_location("gba_4bpp_preview", SCRIPT)
assert SPEC and SPEC.loader
preview = module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


def png_chunks(data):
    pos = 8
    chunks = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        chunks.append((tag, payload))
        pos += length + 12
        if tag == b"IEND":
            break
    return chunks


class Gba4bppPreviewTests(unittest.TestCase):
    def test_renders_one_tile_and_skips_prefix(self):
        # Each 0x21 byte is two 4bpp pixels: index 1 then index 2.
        raw = b"HEAD" + bytes([0x21] * 32)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "tile.png"
            result = preview.render_4bpp_atlas(
                raw, output, skip_bytes=4, columns=1, scale=1
            )
            png = output.read_bytes()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        chunks = png_chunks(png)
        ihdr = next(payload for tag, payload in chunks if tag == b"IHDR")
        width, height, bit_depth, colour_type, *_ = struct.unpack(">IIBBBBB", ihdr)
        self.assertEqual((width, height, bit_depth, colour_type), (8, 8, 8, 2))
        scanlines = zlib.decompress(b"".join(payload for tag, payload in chunks if tag == b"IDAT"))
        self.assertEqual(scanlines[:7], bytes([0, 17, 17, 17, 34, 34, 34]))
        self.assertEqual(result["tile_count"], 1)
        self.assertEqual(result["tile_data_bytes"], 32)

    def test_rejects_non_tile_aligned_payload(self):
        with self.assertRaises(ValueError):
            preview.render_4bpp_atlas(b"\x00" * 33, Path("/tmp/unused.png"))

    def test_rejects_unsafe_canvas_size(self):
        with self.assertRaises(ValueError):
            preview.render_4bpp_atlas(bytes(32 * 8), Path("/tmp/unused.png"), columns=1, scale=8, max_pixels=10)

    def test_rejects_skip_beyond_input(self):
        with self.assertRaises(ValueError):
            preview.render_4bpp_atlas(bytes(32), Path("/tmp/unused.png"), skip_bytes=33)


if __name__ == "__main__":
    unittest.main()
