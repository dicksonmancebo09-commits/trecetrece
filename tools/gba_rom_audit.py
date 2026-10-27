#!/usr/bin/env python3
"""Read-only GBA ROM audit: header, hash, byte assertions, protected ranges and delta.

Never patches a ROM. Intended to create an auditable pre-emulator report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROM_BASE = 0x08000000


def parse_int(value: str | int) -> int:
    return value if isinstance(value, int) else int(value, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gba_lz77_decompress(data: bytes) -> tuple[bytes, int]:
    """Decode the BIOS GBA LZ77 0x10 format; return bytes and source bytes consumed."""
    if len(data) < 4 or data[0] != 0x10:
        raise ValueError("not a GBA LZ77 stream (expected 0x10 header)")
    expected_size = data[1] | (data[2] << 8) | (data[3] << 16)
    cursor = 4
    output = bytearray()
    while len(output) < expected_size:
        if cursor >= len(data):
            raise ValueError(f"truncated LZ77 flags at input offset 0x{cursor:X}")
        flags = data[cursor]
        cursor += 1
        for bit in range(7, -1, -1):
            if len(output) >= expected_size:
                break
            if flags & (1 << bit):
                if cursor + 1 >= len(data):
                    raise ValueError(f"truncated LZ77 back-reference at input offset 0x{cursor:X}")
                b1, b2 = data[cursor], data[cursor + 1]
                cursor += 2
                length = (b1 >> 4) + 3
                displacement = (((b1 & 0x0F) << 8) | b2) + 1
                if displacement > len(output):
                    raise ValueError(
                        f"invalid LZ77 displacement {displacement} with only {len(output)} output bytes"
                    )
                for _ in range(length):
                    if len(output) >= expected_size:
                        break
                    output.append(output[-displacement])
            else:
                if cursor >= len(data):
                    raise ValueError(f"truncated LZ77 literal at input offset 0x{cursor:X}")
                output.append(data[cursor])
                cursor += 1
    return bytes(output), cursor


def gba_room_rle_decompress_map(
    data: bytes, offset: int, reserved_bytes: int
) -> tuple[int, int, list[int], int]:
    """Decode the game's two-plane RLE format into 16-bit room map entries.

    The room header stores width and height as two bytes. Each following RLE
    stream becomes one byte lane of the destination u16 map (first stream =
    low byte, second stream = high byte), matching RoomRleDecompress(type=1).
    Return width, height, tile/metatile IDs, and bytes consumed from offset.
    """
    if offset < 0 or reserved_bytes < 2 or offset + reserved_bytes > len(data):
        raise ValueError("room RLE range is outside ROM bounds")
    end = offset + reserved_bytes
    width, height = data[offset], data[offset + 1]
    expected_count = width * height
    if width == 0 or height == 0:
        raise ValueError(f"invalid room RLE dimensions {width}x{height}")
    cursor = offset + 2

    def take_u8() -> int:
        nonlocal cursor
        if cursor >= end:
            raise ValueError(f"truncated room RLE stream at 0x{cursor:X}")
        value = data[cursor]
        cursor += 1
        return value

    def take_bytes(count: int) -> list[int]:
        nonlocal cursor
        if count < 0 or cursor + count > end:
            raise ValueError(f"truncated room RLE literal at 0x{cursor:X} (length {count})")
        result = list(data[cursor:cursor + count])
        cursor += count
        return result

    def decode_lane() -> list[int]:
        first = take_u8()
        output: list[int] = []
        if first == 1:
            count = take_u8()
            while count != 0:
                if count & 0x80:
                    repeat_count = count & 0x7F
                    if repeat_count == 0:
                        raise ValueError("zero-length repeat run in room RLE stream")
                    value = take_u8()
                    output.extend([value] * repeat_count)
                else:
                    output.extend(take_bytes(count))
                if len(output) > expected_count:
                    raise ValueError(
                        f"room RLE lane overflow: {len(output)} entries; expected {expected_count}"
                    )
                count = take_u8()
        else:
            count = (first << 8) | take_u8()
            while count != 0:
                if count & 0x8000:
                    repeat_count = count & 0x7FFF
                    if repeat_count == 0:
                        raise ValueError("zero-length 16-bit repeat run in room RLE stream")
                    value = take_u8()
                    output.extend([value] * repeat_count)
                else:
                    output.extend(take_bytes(count))
                if len(output) > expected_count:
                    raise ValueError(
                        f"room RLE lane overflow: {len(output)} entries; expected {expected_count}"
                    )
                count = (take_u8() << 8) | take_u8()
        if len(output) != expected_count:
            raise ValueError(
                f"room RLE lane decoded {len(output)} entries; expected {expected_count}"
            )
        return output

    low = decode_lane()
    high = decode_lane()
    values = [lo | (hi << 8) for lo, hi in zip(low, high)]
    return width, height, values, cursor - offset


def header_info(data: bytes, name: str) -> dict[str, Any]:
    if len(data) < 0xC0:
        raise ValueError(f"{name}: file too short for GBA header ({len(data)} bytes)")
    actual = data[0xBD]
    expected = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
    return {
        "file": name,
        "size_bytes": len(data),
        "size_mib": round(len(data) / (1024 * 1024), 3),
        "sha256": sha256_bytes(data),
        "header": {
            "title": data[0xA0:0xAC].split(b"\0", 1)[0].decode("ascii", errors="replace").strip(),
            "game_code": data[0xAC:0xB0].decode("ascii", errors="replace"),
            "maker_code": data[0xB0:0xB2].decode("ascii", errors="replace"),
            "fixed_byte": f"0x{data[0xB2]:02X}",
            "software_version": data[0xBC],
            "complement_actual": f"0x{actual:02X}",
            "complement_expected": f"0x{expected:02X}",
            "complement_valid": actual == expected,
            "entry_word_le": f"0x{int.from_bytes(data[:4], 'little'):08X}"
        }
    }


def changed_ranges(before: bytes, after: bytes, merge_gap: int = 8) -> tuple[int, list[dict[str, Any]]]:
    if len(before) != len(after):
        return max(len(before), len(after)), [{
            "start": 0,
            "end_exclusive": min(len(before), len(after)),
            "start_hex": "0x0",
            "end_exclusive_hex": f"0x{min(len(before), len(after)):X}",
            "changed_bytes": None,
            "reason": "ROM sizes differ; region summary is not a byte-for-byte range report."
        }]
    indexes = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    if not indexes:
        return 0, []
    ranges: list[list[int]] = []
    start = prev = indexes[0]
    count = 1
    for idx in indexes[1:]:
        if idx - prev <= merge_gap:
            prev = idx
            count += 1
            continue
        ranges.append([start, prev + 1, count])
        start = prev = idx
        count = 1
    ranges.append([start, prev + 1, count])
    result = []
    for start, end, n in ranges:
        result.append({
            "start": start,
            "end_exclusive": end,
            "start_hex": f"0x{start:X}",
            "end_exclusive_hex": f"0x{end:X}",
            "changed_bytes": n,
            "span_bytes": end - start
        })
    return len(indexes), result


def run(args: argparse.Namespace) -> dict[str, Any]:
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.profile not in config.get("profiles", {}):
        raise ValueError(f"Unknown profile '{args.profile}' in {args.config}")
    profile = config["profiles"][args.profile]
    rom_path = args.rom.resolve()
    if not rom_path.is_file():
        raise FileNotFoundError(rom_path)
    rom = rom_path.read_bytes()
    report: dict[str, Any] = {
        "tool": "gba_rom_audit",
        "schema_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "read-only",
        "profile": args.profile,
        "profile_description": profile.get("description"),
        "rom": header_info(rom, str(rom_path)),
        "checks": [],
        "errors": [],
        "warnings": []
    }

    def check(name: str, ok: bool, expected: Any, actual: Any, severity: str = "error") -> None:
        row = {"name": name, "passed": bool(ok), "expected": expected, "actual": actual}
        report["checks"].append(row)
        if not ok:
            report["errors" if severity == "error" else "warnings"].append(row)

    header = report["rom"]["header"]
    check("minimum_gba_header", len(rom) >= 0xC0, ">= 192 bytes", len(rom))
    if "size_bytes" in profile and profile["size_bytes"] is not None:
        check("rom_size", len(rom) == int(profile["size_bytes"]), profile["size_bytes"], len(rom))
    if profile.get("title"):
        check("header_title", header["title"] == profile["title"], profile["title"], header["title"])
    if profile.get("game_code"):
        check("game_code", header["game_code"] == profile["game_code"], profile["game_code"], header["game_code"])
    if profile.get("header_complement"):
        check("header_complement_expected", header["complement_actual"].lower() == str(profile["header_complement"]).lower(),
              profile["header_complement"], header["complement_actual"])
    check("header_complement_calculated", header["complement_valid"], header["complement_expected"], header["complement_actual"])
    expected_sha = profile.get("sha256")
    if expected_sha and not args.ignore_profile_sha:
        check("profile_sha256", report["rom"]["sha256"].lower() == expected_sha.lower(), expected_sha, report["rom"]["sha256"])

    for assertion in profile.get("expected_bytes", []):
        offset = parse_int(assertion["offset"])
        expected = bytes.fromhex(assertion["bytes_le"].replace(" ", ""))
        actual = rom[offset:offset + len(expected)]
        check(
            f"bytes_at_{assertion['offset']}",
            actual == expected,
            assertion["bytes_le"].lower(),
            actual.hex(),
        )
        report["checks"][-1]["description"] = assertion.get("description", "")

        # Pin pointer targets independently of instruction-byte assertions.
    pointer_checks = profile.get("pointer_checks", [])
    report["pointer_checks"] = []
    for pointer in pointer_checks:
        site = parse_int(pointer["file_offset"])
        expected_target = parse_int(pointer["expected_target_bus_address"])
        actual_bytes = rom[site:site + 4] if site >= 0 else b""
        actual_target = int.from_bytes(actual_bytes, "little") if len(actual_bytes) == 4 else None
        mapped_offset = actual_target - ROM_BASE if actual_target is not None else None
        in_rom_window = mapped_offset is not None and 0 <= mapped_offset < len(rom)
        target_ok = actual_target == expected_target
        site_ok = site >= 0 and site + 4 <= len(rom)
        row = {
            "file_offset": f"0x{site:X}",
            "expected_target": f"0x{expected_target:08X}",
            "actual_target": f"0x{actual_target:08X}" if actual_target is not None else None,
            "target_file_offset": f"0x{mapped_offset:X}" if mapped_offset is not None else None,
            "target_within_rom": bool(in_rom_window),
            "purpose": pointer.get("purpose", "")
        }
        report["pointer_checks"].append(row)
        check(f"pointer_site_{site:X}_bounds", site_ok, "4 bytes inside ROM", len(actual_bytes))
        check(f"pointer_site_{site:X}_target", target_ok, f"0x{expected_target:08X}",
              f"0x{actual_target:08X}" if actual_target is not None else None)
        check(f"pointer_site_{site:X}_target_in_rom", in_rom_window,
              f"ROM window target within {len(rom)} bytes",
              {"target": f"0x{actual_target:08X}" if actual_target is not None else None,
               "mapped_offset": f"0x{mapped_offset:X}" if mapped_offset is not None else None})
    
# Resource bounds and GBA LZ77 sanity checks come from the selected build profile.
    resources = profile.get("resource_ranges", [])
    report["resources"] = []
    decoded_resources: dict[str, bytes] = {}
    allocated_ranges: list[tuple[int, int, str]] = []
    for resource in resources:
        name = str(resource.get("name", "unnamed-resource"))
        offset = parse_int(resource["offset"])
        used_bytes = int(resource["used_bytes"])
        reserved_bytes = int(resource["reserved_bytes"])
        encoding = str(resource.get("encoding", "raw")).lower()
        expected_unpacked = resource.get("expected_uncompressed_bytes")
        start_end_ok = offset >= 0 and used_bytes > 0 and reserved_bytes >= used_bytes and offset + reserved_bytes <= len(rom)
        check(
            f"resource_bounds_{name}",
            start_end_ok,
            {"offset": f"0x{offset:X}", "used_bytes": used_bytes, "reserved_bytes": reserved_bytes, "rom_size": len(rom)},
            {"offset": f"0x{offset:X}", "end_exclusive": f"0x{offset + reserved_bytes:X}",
             "used_bytes": used_bytes, "reserved_bytes": reserved_bytes}
        )
        resource_row: dict[str, Any] = {
            "name": name,
            "offset": f"0x{offset:X}",
            "used_bytes": used_bytes,
            "reserved_bytes": reserved_bytes,
            "encoding": encoding,
            "description": resource.get("description", ""),
            "bounds_valid": start_end_ok
        }
        if start_end_ok:
            allocated_ranges.append((offset, offset + reserved_bytes, name))
            block = rom[offset:offset + used_bytes]
            if encoding == "gba_lz77":
                try:
                    decoded, consumed = gba_lz77_decompress(block)
                    decoded_resources[name] = decoded
                    resource_row["decoded_bytes"] = len(decoded)
                    resource_row["compressed_bytes_consumed"] = consumed
                    resource_row["trailing_bytes_in_used_region"] = used_bytes - consumed
                    check(f"resource_lz77_{name}", True,
                          {"encoding": "gba_lz77", "expected_uncompressed_bytes": expected_unpacked},
                          {"encoding": "gba_lz77", "decoded_bytes": len(decoded), "consumed_bytes": consumed})
                    if expected_unpacked is not None:
                        check(f"resource_decoded_size_{name}", len(decoded) == int(expected_unpacked),
                              int(expected_unpacked), len(decoded))
                    if consumed != used_bytes:
                        check(f"resource_stream_length_{name}", False, used_bytes, consumed, severity="warning")
                except ValueError as exc:
                    resource_row["decode_error"] = str(exc)
                    check(f"resource_lz77_{name}", False, "valid complete GBA LZ77 stream", str(exc))
            elif encoding == "raw":
                resource_row["decoded_bytes"] = used_bytes
                if expected_unpacked is not None:
                    check(f"resource_raw_size_{name}", used_bytes == int(expected_unpacked),
                          int(expected_unpacked), used_bytes)
            else:
                check(f"resource_encoding_{name}", False, ["gba_lz77", "raw"], encoding)
        report["resources"].append(resource_row)

    # Structural checks for the room-0 map/table structures used by the build.
    room_checks = profile.get("room_map_checks", [])
    report["room_map_checks"] = []
    for room_check in room_checks:
        name = str(room_check.get("name", "unnamed-room-resource"))
        encoding = str(room_check.get("encoding", "")).lower()
        offset = parse_int(room_check["offset"])
        reserved_bytes = parse_int(room_check["reserved_bytes"])
        used_bytes = int(room_check["used_bytes"])
        bounds_ok = (
            offset >= 0 and used_bytes > 0 and reserved_bytes >= used_bytes
            and offset + reserved_bytes <= len(rom)
        )
        check(
            f"room_resource_bounds_{name}",
            bounds_ok,
            {"offset": f"0x{offset:X}", "used_bytes": used_bytes, "reserved_bytes": reserved_bytes},
            {"inside_rom": bounds_ok, "end_exclusive": f"0x{offset + reserved_bytes:X}"}
        )
        row: dict[str, Any] = {
            "name": name,
            "encoding": encoding,
            "offset": f"0x{offset:X}",
            "used_bytes": used_bytes,
            "reserved_bytes": reserved_bytes,
            "bounds_valid": bounds_ok
        }
        report["room_map_checks"].append(row)
        if not bounds_ok:
            continue
        allocated_ranges.append((offset, offset + reserved_bytes, name))

        if encoding == "gba_4bpp_metatile_table":
            header_bytes = int(room_check.get("header_bytes", 2))
            expected_header_word = room_check.get("expected_header_word")
            record_count = int(room_check["record_count"])
            entries_per_record = int(room_check["subtile_entries_per_record"])
            record_size = entries_per_record * 2
            table_data = rom[offset:offset + used_bytes]
            actual_header_word = (
                int.from_bytes(table_data[:2], "little")
                if header_bytes >= 2 and len(table_data) >= 2 else None
            )
            if expected_header_word is not None:
                check(
                    f"room_table_header_{name}",
                    actual_header_word == int(expected_header_word),
                    int(expected_header_word),
                    actual_header_word
                )
            table_payload_bytes = used_bytes - header_bytes
            expected_payload_bytes = record_count * record_size
            check(
                f"room_table_length_{name}",
                table_payload_bytes == expected_payload_bytes and header_bytes <= used_bytes,
                expected_payload_bytes,
                table_payload_bytes
            )
            payload_start = offset + header_bytes
            payload_end = offset + used_bytes
            if table_payload_bytes == expected_payload_bytes and payload_end <= len(rom):
                subtile_words = [
                    int.from_bytes(rom[pos:pos + 2], "little")
                    for pos in range(payload_start, payload_end, 2)
                ]
                tile_indices = [word & 0x03FF for word in subtile_words]
                tile_min = int(room_check["tile_index_min"])
                tile_max = int(room_check["tile_index_max"])
                bad_indices = [
                    {"entry": index, "word": f"0x{word:04X}", "tile_index": tile_indices[index]}
                    for index, word in enumerate(subtile_words)
                    if not tile_min <= tile_indices[index] <= tile_max
                ]
                row["record_count"] = record_count
                row["subtile_word_count"] = len(subtile_words)
                row["tile_index_min_actual"] = min(tile_indices) if tile_indices else None
                row["tile_index_max_actual"] = max(tile_indices) if tile_indices else None
                row["invalid_tile_index_count"] = len(bad_indices)
                row["first_invalid_tile_indices"] = bad_indices[:32]
                check(
                    f"room_table_tile_indices_{name}",
                    len(subtile_words) == record_count * entries_per_record and not bad_indices,
                    {"count": record_count * entries_per_record, "min": tile_min, "max": tile_max},
                    {"count": len(subtile_words), "min": row["tile_index_min_actual"],
                     "max": row["tile_index_max_actual"], "invalid_count": len(bad_indices)}
                )
                blank_id = room_check.get("transparent_metatile_id")
                blank_tile_index = room_check.get("transparent_tile_index")
                if blank_id is not None and blank_tile_index is not None:
                    blank_id = int(blank_id)
                    first_word_index = blank_id * entries_per_record
                    blank_words = subtile_words[first_word_index:first_word_index + entries_per_record]
                    blank_indices = [word & 0x03FF for word in blank_words]
                    row["transparent_metatile_id"] = blank_id
                    row["transparent_metatile_tile_indices"] = blank_indices
                    check(
                        f"transparent_metatile_{name}",
                        len(blank_words) == entries_per_record and all(x == int(blank_tile_index) for x in blank_indices),
                        [int(blank_tile_index)] * entries_per_record,
                        blank_indices
                    )

                    gfx_name = room_check.get("blank_tile_graphics_resource")
                    if gfx_name:
                        gfx = decoded_resources.get(str(gfx_name))
                        bytes_per_tile = int(room_check.get("bytes_per_tile", 32))
                        tile_base_index = int(room_check.get("tile_base_index", 0))
                        blank_local_index = int(room_check["blank_tile_local_index"])
                        blank_start = blank_local_index * bytes_per_tile
                        blank_data = gfx[blank_start:blank_start + bytes_per_tile] if gfx else b""
                        blank_ok = len(blank_data) == bytes_per_tile and not any(blank_data)
                        row["blank_tile_graphics_resource"] = str(gfx_name)
                        row["blank_tile_local_index"] = blank_local_index
                        row["blank_tile_hardware_index"] = tile_base_index + blank_local_index
                        row["blank_tile_graphics_bytes"] = len(blank_data)
                        check(
                            f"transparent_tile_graphics_{name}",
                            blank_ok and tile_base_index + blank_local_index == int(blank_tile_index),
                            {"local_tile": blank_local_index, "hardware_tile": int(blank_tile_index),
                             "byte_count": bytes_per_tile, "all_zero": True},
                            {"local_tile": blank_local_index,
                             "hardware_tile": tile_base_index + blank_local_index,
                             "byte_count": len(blank_data), "all_zero": len(blank_data) == bytes_per_tile and not any(blank_data),
                             "graphics_resource_available": gfx is not None}
                        )

        elif encoding == "metroid_room_rle_u16_map":
            try:
                width, height, values, consumed = gba_room_rle_decompress_map(rom, offset, reserved_bytes)
                row.update({
                    "width": width,
                    "height": height,
                    "entry_count": len(values),
                    "compressed_bytes_consumed": consumed,
                    "unique_value_count": len(set(values)),
                    "min_metatile_id": min(values) if values else None,
                    "max_metatile_id": max(values) if values else None,
                    "unique_values": sorted(set(values))[:512]
                })
                check(
                    f"room_rle_size_{name}",
                    consumed == used_bytes,
                    used_bytes,
                    consumed
                )
                expected_width = room_check.get("expected_width")
                expected_height = room_check.get("expected_height")
                if expected_width is not None or expected_height is not None:
                    dimensions_ok = (
                        (expected_width is None or width == int(expected_width))
                        and (expected_height is None or height == int(expected_height))
                    )
                    check(
                        f"room_rle_dimensions_{name}",
                        dimensions_ok,
                        {"width": expected_width, "height": expected_height},
                        {"width": width, "height": height}
                    )
                expected_count = width * height
                check(
                    f"room_rle_entry_count_{name}",
                    len(values) == expected_count,
                    expected_count,
                    len(values)
                )
                minimum = int(room_check.get("min_metatile_id", 0))
                maximum = int(room_check.get("max_metatile_id", 0xFFFF))
                invalid = [value for value in values if not minimum <= value <= maximum]
                check(
                    f"room_rle_metatile_range_{name}",
                    not invalid,
                    {"min": minimum, "max": maximum},
                    {"min_actual": min(values) if values else None,
                     "max_actual": max(values) if values else None,
                     "invalid_count": len(invalid)}
                )
                if "expected_unique_values" in room_check:
                    expected_unique = sorted(int(x) for x in room_check["expected_unique_values"])
                    check(
                        f"room_rle_unique_values_{name}",
                        sorted(set(values)) == expected_unique,
                        expected_unique,
                        sorted(set(values))
                    )
                if "expected_max_metatile_id" in room_check:
                    actual_max = max(values) if values else None
                    check(
                        f"room_rle_expected_max_{name}",
                        actual_max == int(room_check["expected_max_metatile_id"]),
                        int(room_check["expected_max_metatile_id"]),
                        actual_max
                    )
                if "expected_unique_count" in room_check:
                    actual_count = len(set(values))
                    check(
                        f"room_rle_unique_count_{name}",
                        actual_count == int(room_check["expected_unique_count"]),
                        int(room_check["expected_unique_count"]),
                        actual_count
                    )
            except (ValueError, IndexError) as exc:
                row["decode_error"] = str(exc)
                check(
                    f"room_rle_decode_{name}",
                    False,
                    "valid two-lane room RLE stream",
                    str(exc)
                )
        else:
            check(
                f"room_resource_encoding_{name}",
                False,
                ["gba_4bpp_metatile_table", "metroid_room_rle_u16_map"],
                encoding
            )

    for index, current in enumerate(sorted(allocated_ranges)):
        for following in sorted(allocated_ranges)[index + 1:]:
            if following[0] < current[1]:
                check(
                    f"resource_reservations_do_not_overlap_{current[2]}_{following[2]}",
                    False,
                    "non-overlapping reserved resource ranges",
                    {"first": {"name": current[2], "start": f"0x{current[0]:X}", "end": f"0x{current[1]:X}"},
                     "second": {"name": following[2], "start": f"0x{following[0]:X}", "end": f"0x{following[1]:X}"}}
                )

    baseline_path = args.baseline.resolve() if args.baseline else None
    if baseline_path:
        baseline = baseline_path.read_bytes()
        report["baseline"] = header_info(baseline, str(baseline_path))
        count, ranges = changed_ranges(baseline, rom)
        report["delta"] = {
            "changed_byte_count": count,
            "changed_range_count": len(ranges),
            "changed_ranges": ranges[:500],
            "ranges_truncated": len(ranges) > 500
        }
        check("same_size_as_baseline", len(baseline) == len(rom), len(baseline), len(rom))
        for region in profile.get("must_match_reference_ranges", []):
            offset = parse_int(region["offset"])
            length = parse_int(region["length"])
            a = baseline[offset:offset + length]
            b = rom[offset:offset + length]
            ok = len(a) == length and len(b) == length and a == b
            check(f"reference_range_{region['offset']}", ok,
                  {"length": length, "sha256": sha256_bytes(a), "description": region.get("description")},
                  {"length": len(b), "sha256": sha256_bytes(b)})
    elif profile.get("must_match_reference_ranges"):
        report["warnings"].append({
            "name": "reference_ranges_not_checked",
            "message": "This profile declares protected ranges; pass --baseline to compare them to a clean/reference ROM."
        })

    report["summary"] = {
        "passed": len(report["errors"]) == 0,
        "checks_total": len(report["checks"]),
        "checks_passed": sum(1 for c in report["checks"] if c["passed"]),
        "errors": len(report["errors"]),
        "warnings": len(report["warnings"]),
        "runtime_executed": False,
        "note": "Static audit only; it does not execute the ROM or certify gameplay."
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only, profile-driven GBA ROM audit")
    parser.add_argument("--rom", required=True, type=Path, help="ROM file to audit")
    parser.add_argument("--profile", required=True, help="Profile name from config/gba_lab.json")
    parser.add_argument("--config", type=Path, default=Path("config/gba_lab.json"))
    parser.add_argument("--baseline", type=Path, help="Clean/reference ROM used to compute delta and protected-range checks")
    parser.add_argument("--report", type=Path, help="Optional path to write the JSON report")
    parser.add_argument("--ignore-profile-sha", action="store_true",
                        help="Skip the pinned SHA-256 check (still reports the actual hash)")
    args = parser.parse_args()
    try:
        report = run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"gba_rom_audit: ERROR: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["summary"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
