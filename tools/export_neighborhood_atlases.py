#!/usr/bin/env python3
"""Render all seven original neighborhood SVG atlases to indexed PNG and GBA resources.

Exact palette mapping only: unexpected colors, partial alpha, incorrect dimensions,
or palettes over 16 entries stop the export instead of silently quantizing art.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from png_to_gba_4bpp import export_atlas  # noqa: E402

ATLAS_SOURCES = [
    {
        "id": "L01", "name": "Villa Duarte",
        "svg": "assets/levels/level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.svg",
        "metadata": "assets/levels/level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.json",
        "output": "assets/levels/level-01-villa-duarte/exports",
        "prefix": "l01-villa-duarte",
    },
    {
        "id": "L02", "name": "El Caliche",
        "svg": "assets/tiles/scenario-02/scenario-02-el-caliche-tiles.svg",
        "metadata": "assets/tiles/scenario-02/tile-atlas-metadata.json",
        "output": "assets/tiles/scenario-02/exports",
        "prefix": "l02-el-caliche",
    },
    {
        "id": "L03", "name": "La Francia Nueva",
        "svg": "assets/levels/level-03-la-francia-nueva/level-03-atlas-v0.1.svg",
        "metadata": "assets/levels/level-03-la-francia-nueva/level-03-atlas-v0.1.json",
        "output": "assets/levels/level-03-la-francia-nueva/exports",
        "prefix": "l03-la-francia-nueva",
    },
    {
        "id": "L04", "name": "Calero",
        "svg": "assets/levels/level-04-calero/level-04-atlas-v0.1.svg",
        "metadata": "assets/levels/level-04-calero/level-04-atlas-v0.1.json",
        "output": "assets/levels/level-04-calero/exports",
        "prefix": "l04-calero",
    },
    {
        "id": "L05", "name": "Pueblo Nuevo",
        "svg": "assets/levels/level-05-pueblo-nuevo/level-05-atlas-v0.1.svg",
        "metadata": "assets/levels/level-05-pueblo-nuevo/level-05-atlas-v0.1.json",
        "output": "assets/levels/level-05-pueblo-nuevo/exports",
        "prefix": "l05-pueblo-nuevo",
    },
    {
        "id": "L06", "name": "Los Molinos",
        "svg": "assets/levels/level-06-los-molinos/level-06-atlas-v0.1.svg",
        "metadata": "assets/levels/level-06-los-molinos/level-06-atlas-v0.1.json",
        "output": "assets/levels/level-06-los-molinos/exports",
        "prefix": "l06-los-molinos",
    },
    {
        "id": "L07", "name": "Simónico",
        "svg": "assets/levels/level-07-simonico/level-07-atlas-v0.1.svg",
        "metadata": "assets/levels/level-07-simonico/level-07-atlas-v0.1.json",
        "output": "assets/levels/level-07-simonico/exports",
        "prefix": "l07-simonico",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hex(value: str) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) == 6:
        return tuple(bytes.fromhex(value)) + (255,)  # type: ignore[return-value]
    if len(value) == 8:
        return tuple(bytes.fromhex(value))  # type: ignore[return-value]
    raise ValueError(f"Unsupported palette hex value: #{value}")


def metadata_palette(document: dict[str, Any]) -> list[dict[str, Any]]:
    palette = document.get("palette")
    if not isinstance(palette, list) or not palette:
        raise ValueError("Metadata has no palette array.")
    result = []
    for fallback_index, item in enumerate(palette):
        if not isinstance(item, dict) or "hex" not in item:
            raise ValueError(f"Malformed palette entry at index {fallback_index}.")
        entry = dict(item)
        entry["index"] = int(entry.get("index", fallback_index))
        entry["rgba"] = parse_hex(str(entry["hex"]))
        result.append(entry)
    result.sort(key=lambda item: item["index"])
    if [x["index"] for x in result] != list(range(len(result))):
        raise ValueError("Palette indices must be sequential starting at zero.")
    if len(result) > 16:
        raise ValueError(f"GBA 4bpp allows 16 palette entries; found {len(result)}.")
    if result[0]["rgba"][3] != 0:
        raise ValueError("Palette entry 0 must be the transparent index.")
    return result


def render_indexed(atlas: dict[str, str]) -> dict[str, Any]:
    svg_path = ROOT / atlas["svg"]
    metadata_path = ROOT / atlas["metadata"]
    output_dir = ROOT / atlas["output"]
    if not svg_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError(f"Missing SVG or metadata for {atlas['id']}: {svg_path}, {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    canvas = metadata.get("canvas", {})
    grid = metadata.get("grid", {})
    width = int(canvas.get("width_px", grid.get("canvas_width_px", 256)))
    height = int(canvas.get("height_px", grid.get("canvas_height_px", 256)))
    if (width, height) != (256, 256):
        raise ValueError(f"{atlas['id']}: expected 256x256, metadata declares {width}x{height}.")

    palette = metadata_palette(metadata)
    rgba_to_index: dict[tuple[int, int, int, int], int] = {}
    for item in palette:
        rgba = item["rgba"]
        if rgba[3] != 0 and rgba in rgba_to_index:
            raise ValueError(f"{atlas['id']}: duplicate opaque palette color {rgba}.")
        if rgba[3] != 0:
            rgba_to_index[rgba] = item["index"]

    rendered = cairosvg.svg2png(url=str(svg_path), output_width=width, output_height=height)
    from io import BytesIO
    with Image.open(BytesIO(rendered)) as source:
        rgba = source.convert("RGBA")
        if rgba.size != (width, height):
            raise ValueError(f"{atlas['id']}: rendered size is {rgba.size}, expected {(width, height)}.")
        pixels = list(rgba.getdata())

    indices: list[int] = []
    unknown: Counter[tuple[int, int, int, int]] = Counter()
    partial_alpha = 0
    for pixel in pixels:
        red, green, blue, alpha = pixel
        if alpha == 0:
            indices.append(0)
        elif alpha != 255:
            partial_alpha += 1
            indices.append(0)
        else:
            index = rgba_to_index.get(pixel)
            if index is None:
                unknown[pixel] += 1
                indices.append(0)
            else:
                indices.append(index)
    if partial_alpha:
        raise ValueError(f"{atlas['id']}: {partial_alpha} partially transparent pixels; palette conversion must not antialias.")
    if unknown:
        detail = sorted(((k, v) for k, v in unknown.items()), key=lambda x: -x[1])[:8]
        raise ValueError(f"{atlas['id']}: SVG contains colors outside declared palette: {detail}")

    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{atlas['prefix']}-indexed.png"
    indexed = Image.new("P", (width, height))
    rgb_palette = []
    for item in palette:
        rgb_palette.extend(item["rgba"][:3])
    rgb_palette.extend([0] * (768 - len(rgb_palette)))
    indexed.putpalette(rgb_palette)
    indexed.putdata(indices)
    indexed.info["transparency"] = 0
    indexed.save(png_path, format="PNG", optimize=False, transparency=0)

    export = export_atlas(png_path, output_dir, atlas["prefix"])
    used = sorted(set(indices))
    expected_tile_count = (width // 8) * (height // 8)
    if export["tile_count"] != expected_tile_count or export["tile_bytes"] != expected_tile_count * 32:
        raise AssertionError(f"{atlas['id']}: invalid 4bpp tile count or length.")
    if len(export["pixel_indices_used"]) > 16:
        raise AssertionError(f"{atlas['id']}: export exceeds 16 color indices.")

    report = {
        "project": "LATINO AMÉRICA Zector Cero",
        "level_id": atlas["id"],
        "neighborhood": atlas["name"],
        "source_svg": atlas["svg"],
        "source_svg_sha256": sha256(svg_path),
        "metadata_json": atlas["metadata"],
        "indexed_png": str(png_path.relative_to(ROOT)),
        "indexed_png_sha256": sha256(png_path),
        "dimensions_px": [width, height],
        "tile_grid": [width // 8, height // 8],
        "tile_count": expected_tile_count,
        "palette_entries": len(palette),
        "used_palette_indices": used,
        "unknown_colors": 0,
        "partial_alpha_pixels": 0,
        "outputs": {
            "4bpp": f"{atlas['output']}/{atlas['prefix']}.4bpp",
            "4bpp_lz77": f"{atlas['output']}/{atlas['prefix']}.4bpp.lz",
            "bgr555_palette": f"{atlas['output']}/{atlas['prefix']}.bgr555.pal",
            "conversion_report": f"{atlas['output']}/{atlas['prefix']}.export.json",
        },
        "validation": {
            "exact_declared_palette": True,
            "no_partial_alpha": True,
            "indexed_png": True,
            "4bpp_round_trip": export["validation"]["4bpp_round_trip"],
            "lz77_round_trip": export["validation"]["lz77_round_trip"],
            "rom_modified": False,
            "tilemap_created": False,
            "runtime_tested": False,
        },
    }
    report_path = output_dir / f"{atlas['prefix']}-atlas-validation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", choices=[a["id"] for a in ATLAS_SOURCES], help="Export only selected level(s); repeat as needed.")
    parser.add_argument("--json-out", type=Path, help="Optional combined export report path.")
    args = parser.parse_args()
    selected = [a for a in ATLAS_SOURCES if not args.only or a["id"] in args.only]
    reports = []
    try:
        for atlas in selected:
            report = render_indexed(atlas)
            reports.append(report)
            print(f"{report['level_id']} {report['neighborhood']}: {report['tile_count']} tiles, {report['palette_entries']} palette entries, 4bpp and LZ77 round-trips OK.")
        combined = {"status": "PASS", "atlas_count": len(reports), "atlases": reports}
        if args.json_out:
            path = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, AssertionError) as exc:
        print(f"export_neighborhood_atlases: ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
