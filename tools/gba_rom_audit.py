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
