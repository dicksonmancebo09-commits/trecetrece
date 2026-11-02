#!/usr/bin/env python3
"""Rasterize an authored SVG atlas to a deterministic 16-entry indexed PNG.

The renderer uses the palette recorded beside the SVG; it never invents colors
or performs an unconstrained quantization. The indexed PNG is an intermediate
asset for the repository's existing GBA 4bpp/LZ77 exporter.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

try:
    import cairosvg
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dependencies: python3 -m pip install Pillow CairoSVG") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hex_rgba(value: str) -> tuple[int, int, int, int]:
    raw = value.lstrip("#")
    if len(raw) == 6:
        raw += "FF"
    if len(raw) != 8:
        raise ValueError(f"Unsupported palette hex value: {value}")
    return tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4, 6))  # type: ignore[return-value]


def read_palette(metadata: dict[str, Any]) -> list[tuple[str, tuple[int, int, int, int]]]:
    entries = metadata.get("palette")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 16:
        raise ValueError("Metadata must declare between 1 and 16 palette entries")
    parsed = []
    for entry in sorted(entries, key=lambda x: int(x.get("index", 0))):
        parsed.append((str(entry.get("name", "")), hex_rgba(str(entry["hex"]))))
    if parsed[0][1][3] != 0:
        raise ValueError("Palette index 0 must be transparent (alpha 00)")
    return parsed


def render_indexed(svg_path: Path, metadata_path: Path, output_path: Path, max_distance: int = 120) -> dict[str, Any]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    palette = read_palette(metadata)
    rendered = cairosvg.svg2png(url=str(svg_path))
    with Image.open(io.BytesIO(rendered)) as opened:
        rgba = opened.convert("RGBA")
    if rgba.width % 8 or rgba.height % 8:
        raise ValueError(f"Atlas dimensions must be multiples of 8; got {rgba.size}")
    palette_rgb = [entry[1][:3] for entry in palette[1:]]
    if not palette_rgb:
        raise ValueError("Palette has no opaque colors")

    pixels: list[int] = []
    color_cache: dict[tuple[int, int, int, int], tuple[int, int]] = {}
    semitransparent_colour_count = 0
    max_error = 0
    exact_opaque_colors: set[tuple[int, int, int]] = set()
    used_indices: set[int] = set()
    for color in rgba.getdata():
        cached = color_cache.get(color)
        if cached is None:
            r, g, b, a = color
            if a == 0:
                cached = (0, 0)
            else:
                if a < 255:
                    semitransparent_colour_count += 1
                best_index = 1
                best_error_sq = None
                for index, candidate in enumerate(palette_rgb, start=1):
                    error_sq = (r - candidate[0]) ** 2 + (g - candidate[1]) ** 2 + (b - candidate[2]) ** 2
                    if best_error_sq is None or error_sq < best_error_sq:
                        best_error_sq = error_sq
                        best_index = index
                distance = int((best_error_sq or 0) ** 0.5)
                cached = (best_index, distance)
                exact_opaque_colors.add((r, g, b))
                max_error = max(max_error, distance)
            color_cache[color] = cached
        index, distance = cached
        if distance > max_distance:
            raise ValueError(
                f"Rendered colour {color} is {distance} RGB units from the declared palette "
                f"(limit {max_distance}); review antialiasing or metadata."
            )
        pixels.append(index)
        used_indices.add(index)

    indexed = Image.new("P", rgba.size)
    indexed.putdata(pixels)
    flat_palette: list[int] = []
    for _, (r, g, b, a) in palette:
        flat_palette.extend((r, g, b))
    while len(flat_palette) < 768:
        flat_palette.extend((0, 0, 0))
    indexed.putpalette(flat_palette[:768])
    indexed.info["transparency"] = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    indexed.save(output_path, format="PNG", optimize=False, transparency=0)
    out_bytes = output_path.read_bytes()
    report = {
        "format": "indexed-png-4bpp-ready",
        "source_svg": str(svg_path),
        "source_svg_sha256": sha256(svg_path.read_bytes()),
        "metadata_json": str(metadata_path),
        "dimensions_px": [rgba.width, rgba.height],
        "tile_dimensions_px": [8, 8],
        "tile_grid": [rgba.width // 8, rgba.height // 8],
        "tile_count": (rgba.width // 8) * (rgba.height // 8),
        "palette_entries": len(palette),
        "palette": [{"index": i, "name": name, "rgba": list(color)} for i, (name, color) in enumerate(palette)],
        "used_indices": sorted(used_indices),
        "distinct_opaque_rgb_colours": len(exact_opaque_colors),
        "distinct_semi_transparent_colours_mapped_to_solid_palette": semitransparent_colour_count,
        "maximum_rgb_distance_to_declared_palette": max_error,
        "output_png": str(output_path),
        "output_png_sha256": sha256(out_bytes),
        "validation": {
            "indexed_png_mode_p": indexed.mode == "P",
            "dimensions_multiple_of_8": True,
            "palette_entries_at_most_16": len(palette) <= 16,
            "transparent_index_zero": indexed.info.get("transparency") == 0,
            "gba_4bpp_exported": False,
            "rom_integrated": False,
            "emulator_tested": False,
        },
    }
    report_path = output_path.with_suffix(output_path.suffix + ".export.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="JSON array with svg, metadata and output paths")
    parser.add_argument("--max-distance", type=int, default=120, help="Maximum RGB Euclidean distance to a declared palette colour")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, list) or not manifest:
            raise ValueError("Manifest must be a non-empty JSON array")
        reports = []
        for entry in manifest:
            svg = Path(entry["svg"])
            metadata = Path(entry["metadata"])
            output = Path(entry["output"])
            reports.append(render_indexed(svg, metadata, output, args.max_distance))
        print(json.dumps({"rendered_atlases": len(reports), "reports": reports}, ensure_ascii=False, indent=2))
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"indexed atlas export failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
