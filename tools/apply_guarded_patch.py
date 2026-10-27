#!/usr/bin/env python3
"""Apply a guarded local ROM patch manifest to a new copy only.

The manifest is intended to remain private inside private-roms/ because offsets
and byte replacements may be derived from a commercial ROM. This script never
downloads ROMs and refuses to overwrite the base or an existing output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_offset(value: str | int) -> int:
    return value if isinstance(value, int) else int(value, 0)


def gba_header_complement(data: bytes | bytearray) -> int:
    if len(data) < 0xC0:
        raise ValueError("Base file is too small for a GBA header.")
    return (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF


def apply_patch_bytes(base: bytes, manifest: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    if len(base) < 0xC0:
        raise ValueError("Base file is too small for a GBA header.")
    expected_base_hash = str(manifest.get("base_sha256", "")).lower()
    actual_base_hash = sha256_bytes(base)
    if not expected_base_hash:
        raise ValueError("Manifest must pin base_sha256; unpinned patch application is forbidden.")
    if actual_base_hash != expected_base_hash:
        raise ValueError(
            f"Base SHA-256 mismatch: expected {expected_base_hash}, got {actual_base_hash}"
        )

    writes = manifest.get("writes")
    if not isinstance(writes, list) or not writes:
        raise ValueError("Manifest must contain a non-empty writes array.")
    normalized = []
    for index, write in enumerate(writes):
        try:
            offset = parse_offset(write["offset"])
            before = bytes.fromhex(str(write["expected_before_hex"]).replace(" ", ""))
            after = bytes.fromhex(str(write["replacement_hex"]).replace(" ", ""))
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid write entry #{index + 1}: {exc}") from exc
        if not before or not after:
            raise ValueError(f"Write entry #{index + 1} has an empty before/after byte string.")
        if len(before) != len(after):
            raise ValueError(f"Write entry #{index + 1} changes length; guarded in-place writes must be length-preserving.")
        if offset < 0 or offset + len(before) > len(base):
            raise ValueError(f"Write entry #{index + 1} is outside the ROM bounds.")
        normalized.append({
            "offset": offset,
            "before": before,
            "after": after,
            "purpose": str(write.get("purpose", "")),
            "source_index": index
        })

    normalized.sort(key=lambda row: row["offset"])
    last_end = -1
    for row in normalized:
        if row["offset"] < last_end:
            raise ValueError(f"Overlapping writes detected at file offset 0x{row['offset']:X}.")
        last_end = row["offset"] + len(row["before"])

    # Validate every precondition before applying any changes.
    for row in normalized:
        offset = row["offset"]
        actual = base[offset:offset + len(row["before"])]
        if actual != row["before"]:
            raise ValueError(
                f"Precondition failed at 0x{offset:X}: expected {row['before'].hex()}, got {actual.hex()}"
            )

    out = bytearray(base)
    changes = []
    for row in normalized:
        offset = row["offset"]
        out[offset:offset + len(row["after"])] = row["after"]
        changes.append({
            "offset": f"0x{offset:X}",
            "length": len(row["after"]),
            "before_hex": row["before"].hex(),
            "after_hex": row["after"].hex(),
            "purpose": row["purpose"]
        })

    header_policy = manifest.get("header", {})
    if header_policy.get("recalculate_complement", True):
        before_checksum = out[0xBD]
        out[0xBD] = gba_header_complement(out)
        checksum_updated = before_checksum != out[0xBD]
    else:
        checksum_updated = False

    expected_output = manifest.get("expected_output", {})
    title_expected = expected_output.get("title")
    code_expected = expected_output.get("game_code")
    actual_title = bytes(out[0xA0:0xAC]).split(b"\0", 1)[0].decode("ascii", errors="replace").strip()
    actual_code = bytes(out[0xAC:0xB0]).decode("ascii", errors="replace")
    if title_expected and actual_title != title_expected:
        raise ValueError(f"Output title mismatch: expected {title_expected!r}, got {actual_title!r}")
    if code_expected and actual_code != code_expected:
        raise ValueError(f"Output game code mismatch: expected {code_expected!r}, got {actual_code!r}")

    if out[0xBD] != gba_header_complement(out):
        raise ValueError("Output GBA header complement is invalid after patching.")
    actual_output_hash = sha256_bytes(out)
    pinned_output_hash = expected_output.get("sha256")
    if pinned_output_hash and actual_output_hash.lower() != str(pinned_output_hash).lower():
        raise ValueError(f"Output SHA-256 mismatch: expected {pinned_output_hash}, got {actual_output_hash}")

    report = {
        "tool": "apply_guarded_patch",
        "schema_version": 1,
        "patch_id": manifest.get("patch_id", "unnamed"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "new output only; preconditions checked before applying writes",
        "base_sha256": actual_base_hash,
        "output_sha256": actual_output_hash,
        "size_bytes": len(out),
        "title": actual_title,
        "game_code": actual_code,
        "header_complement": f"0x{out[0xBD]:02X}",
        "header_checksum_recalculated": checksum_updated,
        "writes_applied": len(changes),
        "changed_byte_count_before_checksum": sum(
            sum(1 for a, b in zip(row["before"], row["after"]) if a != b) for row in normalized
        ),
        "changes": changes,
        "output_written": False
    }
    return bytes(out), report


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a SHA-pinned, byte-guarded patch manifest to a new private ROM copy.")
    parser.add_argument("--base", required=True, type=Path, help="Base ROM (must be inside private-roms/)")
    parser.add_argument("--manifest", required=True, type=Path, help="Private JSON manifest (must be inside private-roms/)")
    parser.add_argument("--output", required=True, type=Path, help="New ROM path (must be inside private-roms/; must not exist)")
    parser.add_argument("--report", type=Path, help="Optional JSON report path (must be inside private-roms/)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    private_root = (root / "private-roms").resolve()
    try:
        base_path = args.base.resolve()
        manifest_path = args.manifest.resolve()
        output_path = args.output.resolve()
        report_path = args.report.resolve() if args.report else None
        for label, path in (("base", base_path), ("manifest", manifest_path), ("output", output_path)):
            if not path.is_relative_to(private_root):
                raise ValueError(f"{label} must be inside private-roms/ (ignored by Git).")
        if report_path and not report_path.is_relative_to(private_root):
            raise ValueError("report must be inside private-roms/.")
        if not base_path.is_file():
            raise FileNotFoundError(base_path)
        if not manifest_path.is_file():
            raise FileNotFoundError(manifest_path)
        if output_path.exists():
            raise FileExistsError(f"Refusing to overwrite existing output: {output_path}")
        if output_path == base_path:
            raise ValueError("Output path must differ from base path.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        patched, report = apply_patch_bytes(base_path.read_bytes(), manifest)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=output_path.parent, prefix=output_path.name + ".tmp.") as temp:
            temp.write(patched)
            temp.flush()
            os.fsync(temp.fileno())
            tmp_name = temp.name
        os.replace(tmp_name, output_path)
        report["output_written"] = True
        report["output_path"] = str(output_path)
        if report_path:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"apply_guarded_patch: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
