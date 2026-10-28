#!/usr/bin/env python3
"""Catalog complete GBA BIOS LZ77 0x10 streams without modifying the ROM."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path

ROM_BASE = 0x08000000
ROM_END = 0x08800000
EXPECTED_SHA256 = "a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8"
DEFAULT_MAX_OUTPUT = 2 * 1024 * 1024

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def decode_lz77(data: bytes, offset: int, max_output: int):
    if offset + 4 > len(data) or data[offset] != 0x10:
        return None
    size = data[offset+1] | data[offset+2] << 8 | data[offset+3] << 16
    if size < 1 or size > max_output:
        return None
    src, out = offset + 4, bytearray()
    while len(out) < size:
        if src >= len(data):
            return None
        flags = data[src]
        src += 1
        for bit in range(7, -1, -1):
            if len(out) >= size:
                break
            if flags & (1 << bit):
                if src + 2 > len(data):
                    return None
                a, b = data[src], data[src+1]
                src += 2
                count = (a >> 4) + 3
                distance = (((a & 15) << 8) | b) + 1
                if distance > len(out):
                    return None
                for _ in range(count):
                    if len(out) >= size:
                        break
                    out.append(out[-distance])
            else:
                if src >= len(data):
                    return None
                out.append(data[src])
                src += 1
    return bytes(out), src - offset

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="path to the local ROM; read-only")
    parser.add_argument("--out-dir", default="private-roms/rea-analysis/assets")
    parser.add_argument("--allow-other-hash", action="store_true")
    parser.add_argument("--min-output", type=int, default=256)
    parser.add_argument("--max-output", type=int, default=DEFAULT_MAX_OUTPUT)
    args = parser.parse_args()
    rom_path = Path(args.rom).expanduser().resolve()
    raw = rom_path.read_bytes()
    rom_sha = digest(raw)
    if len(raw) != 8 * 1024 * 1024:
        raise SystemExit(f"Expected 8 MiB ROM, got {len(raw)} bytes")
    if rom_sha != EXPECTED_SHA256 and not args.allow_other_hash:
        raise SystemExit(f"SHA-256 mismatch: {rom_sha}; expected {EXPECTED_SHA256}. Check the ROM before using --allow-other-hash.")

    refs = defaultdict(list)
    for pos in range(0, len(raw)-3, 4):
        value = struct.unpack_from("<I", raw, pos)[0] & ~1
        if ROM_BASE <= value < ROM_END:
            refs[value - ROM_BASE].append(pos)

    candidates = []
    for offset in range(0, len(raw)-4, 2):
        if raw[offset] != 0x10:
            continue
        result = decode_lz77(raw, offset, args.max_output)
        if result is None:
            continue
        expanded, used = result
        if len(expanded) < args.min_output:
            continue
        source_refs = refs.get(offset, [])
        score = (100 + 3 * min(len(source_refs), 30) if source_refs else 0)
        score += 25 if len(expanded) >= 8192 else 0
        score += 15 if len(expanded) >= 32768 else 0
        score += 5 if len(expanded) % 32 == 0 else 0
        score += 2 if len(expanded) % 64 == 0 else 0
        if source_refs and len(expanded) >= 8192:
            priority = "P1"
        elif source_refs:
            priority = "P2"
        elif len(expanded) >= 8192:
            priority = "P3"
        else:
            priority = "P4"
        candidates.append({
            "offset": offset, "offset_hex": f"0x{offset:06X}",
            "bus_address": f"0x{ROM_BASE + offset:08X}",
            "compressed_size": used, "end_offset": offset + used,
            "decompressed_size": len(expanded),
            "compression_ratio": round(len(expanded) / used, 3),
            "compressed_sha256": digest(raw[offset:offset+used]),
            "decompressed_sha256": digest(expanded),
            "pointer_ref_count": len(source_refs),
            "pointer_source_offsets": [f"0x{x:06X}" for x in source_refs[:64]],
            "referenced_exactly": bool(source_refs),
            "4bpp_tile_aligned": len(expanded) % 32 == 0,
            "8bpp_tile_aligned": len(expanded) % 64 == 0,
            "priority": priority, "triage_score": score,
            "classification": "unclassified_compressed_resource"
        })
    candidates.sort(key=lambda c: (-c["triage_score"], -c["pointer_ref_count"],
                                   -c["decompressed_size"], c["offset"]))
    for index, candidate in enumerate(candidates, 1):
        candidate["candidate_id"] = f"LZ{index:03d}"
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = dict(sorted(Counter(c["priority"] for c in candidates).items()))
    manifest = {
        "report_kind": "gba_lz77_asset_triage_catalog",
        "rom_size_bytes": len(raw), "rom_sha256": rom_sha,
        "rom_sha256_matches_reference": rom_sha == EXPECTED_SHA256,
        "complete_candidates_min_output": args.min_output,
        "candidate_count": len(candidates), "priority_counts": counts,
        "priority_definition": {
            "P1": "exact pointer reference and expanded size >= 8 KiB",
            "P2": "exact pointer reference",
            "P3": "no exact pointer reference but expanded size >= 8 KiB",
            "P4": "other complete streams"
        },
        "limitations": [
            "A valid LZ77 stream can occur by chance in arbitrary bytes.",
            "Pointer-shaped words can be data rather than live references.",
            "Tile-aligned output size does not prove graphical use.",
            "Resource type/name needs contextual or runtime evidence."
        ],
        "candidates": candidates
    }
    (out_dir / "lz77_asset_catalog.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    fields = ["candidate_id", "priority", "offset_hex", "bus_address",
              "compressed_size", "decompressed_size", "compression_ratio",
              "pointer_ref_count", "4bpp_tile_aligned", "8bpp_tile_aligned",
              "triage_score", "compressed_sha256", "decompressed_sha256"]
    with (out_dir / "lz77_asset_catalog.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: c[k] for k in fields} for c in candidates)
    print(json.dumps({"rom_sha256": rom_sha, "candidate_count": len(candidates),
                      "priority_counts": counts,
                      "json": str(out_dir / "lz77_asset_catalog.json"),
                      "csv": str(out_dir / "lz77_asset_catalog.csv")}, indent=2))

if __name__ == "__main__":
    main()
