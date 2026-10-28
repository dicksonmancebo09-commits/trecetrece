#!/usr/bin/env python3
"""Build a guarded one-byte test variant that jumps to the BSL-hangar intro state.

This is a research patch candidate, not a validated gameplay build.
It never modifies the input ROM. No ROM or patch binary should be committed to Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED_SHA256 = "a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8"
ROM_SIZE = 8 * 1024 * 1024
PATCH_OFFSET = 0x8777E
OLD_CONTEXT = bytes.fromhex("01 20 08 80")
NEW_CONTEXT = bytes.fromhex("0B 20 08 80")
OUT_REL = Path("private-roms/rea-analysis/sector_cero_hangar_entry_test.gba")
REPORT_REL = Path("private-roms/rea-analysis/sector_cero_hangar_entry_test.json")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_header_checksum(data: bytes) -> int:
    # GBA logo/title header checksum: subtract the sum of 0xA0..0xBC and 0x19.
    return (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF


def validate_base(data: bytes) -> None:
    if len(data) != ROM_SIZE:
        raise ValueError(f"Expected an 8 MiB ROM, got {len(data)} bytes")
    actual = sha256(data)
    if actual != EXPECTED_SHA256:
        raise ValueError(f"ROM hash mismatch: {actual}; expected {EXPECTED_SHA256}")
    if data[PATCH_OFFSET:PATCH_OFFSET + len(OLD_CONTEXT)] != OLD_CONTEXT:
        actual_context = data[PATCH_OFFSET:PATCH_OFFSET + len(OLD_CONTEXT)].hex(" ")
        raise ValueError(f"Unexpected code context at 0x{PATCH_OFFSET:X}: {actual_context}")
    checksum = expected_header_checksum(data)
    if checksum != data[0xBD]:
        raise ValueError(f"Invalid GBA header checksum: actual 0x{data[0xBD]:02X}, expected 0x{checksum:02X}")


def patch_bytes(data: bytes) -> bytes:
    """Change only MOVS r0,#1 to MOVS r0,#11 at the guarded offset."""
    if len(data) != ROM_SIZE:
        raise ValueError("Input must be an 8 MiB GBA ROM")
    if data[PATCH_OFFSET:PATCH_OFFSET + len(OLD_CONTEXT)] != OLD_CONTEXT:
        raise ValueError("Patch refused: expected Thumb instruction/context does not match")
    out = bytearray(data)
    out[PATCH_OFFSET:PATCH_OFFSET + 2] = b"\x0B\x20"
    result = bytes(out)
    if sum(a != b for a, b in zip(data, result)) != 1:
        raise AssertionError("Internal guard failed: result must differ by exactly one byte")
    if result[PATCH_OFFSET:PATCH_OFFSET + len(NEW_CONTEXT)] != NEW_CONTEXT:
        raise AssertionError("Patched instruction bytes do not match expected state-11 encoding")
    checksum = expected_header_checksum(result)
    if checksum != result[0xBD]:
        raise AssertionError("GBA header checksum unexpectedly changed")
    return result


def find_repo_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start, capture_output=True, text=True, check=True
    )
    return Path(result.stdout.strip()).resolve()


def ensure_ignored(root: Path, relative: Path) -> None:
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(relative)],
        cwd=root, capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{relative} is not ignored by Git. Do not write the test ROM into a tracked directory."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", help="path to the untouched US/Australia Metroid Fusion ROM")
    parser.add_argument("--apply", action="store_true", help="write the guarded test ROM and private JSON report")
    args = parser.parse_args()

    input_path = Path(args.rom).expanduser().resolve()
    raw = input_path.read_bytes()
    validate_base(raw)
    patched = patch_bytes(raw)
    report = {
        "report_kind": "experimental_hangar_entry_patch",
        "status": "static_patch_candidate_not_runtime_validated",
        "source_rom": {
            "sha256": sha256(raw),
            "size_bytes": len(raw),
            "path": str(input_path)
        },
        "patch": {
            "offset": f"0x{PATCH_OFFSET:X}",
            "old_bytes": OLD_CONTEXT.hex(" "),
            "new_bytes": NEW_CONTEXT.hex(" "),
            "changed_byte_count": sum(a != b for a, b in zip(raw, patched)),
            "purpose": "after NewFileIntroInit on a new-file path, enter NewFileIntroHandler state 11 (landing on BSL)"
        },
        "output_sha256": sha256(patched),
        "header_checksum_valid": patched[0xBD] == expected_header_checksum(patched),
        "runtime_validation": "NOT PERFORMED; test in mGBA before using as a game build",
        "must_test": [
            "fresh save reaches landing-on-BSL/hangar scene",
            "scene assets and palette load correctly",
            "scene completes without softlock or black screen",
            "intro save flags and next game state remain valid",
            "completed-save behavior remains unchanged"
        ]
    }
    if not args.apply:
        print(json.dumps({**report, "output_path": str(OUT_REL), "mode": "plan_only"}, indent=2))
        return 0

    # Resolve the repository from this script's location; the ROM may live outside the repo.
    root = find_repo_root(Path(__file__).resolve().parent)
    ensure_ignored(root, OUT_REL)
    ensure_ignored(root, REPORT_REL)
    output = root / OUT_REL
    report_path = root / REPORT_REL
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(patched)
    report["output_path"] = str(output)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
