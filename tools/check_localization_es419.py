#!/usr/bin/env python3
"""Validate the draft es-419 dialogue pack without touching or testing any ROM."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "localization" / "es-419" / "dialogue.json"


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta", {})
    dialogues = data.get("dialogue", [])
    characters = data.get("characters", [])
    ui = data.get("ui", {})

    if meta.get("locale") != "es-419":
        errors.append("meta.locale must be es-419")
    if meta.get("status") != "draft-not-in-ROM":
        errors.append("status must remain draft-not-in-ROM until the strings are integrated and tested")
    max_chars = meta.get("soft_max_chars_per_line", 28)
    if not isinstance(max_chars, int) or max_chars < 1:
        errors.append("soft_max_chars_per_line must be a positive integer")
        max_chars = 28

    character_ids = {c.get("id") for c in characters}
    if not character_ids:
        errors.append("no character profiles are defined")

    ids: set[str] = set()
    all_lines: list[tuple[str, int, str]] = []
    for entry in dialogues:
        entry_id = entry.get("id")
        if not entry_id:
            errors.append("dialogue entry without id")
        elif entry_id in ids:
            errors.append(f"duplicate dialogue id: {entry_id}")
        else:
            ids.add(entry_id)

        if entry.get("speaker") not in character_ids:
            errors.append(f"{entry_id}: speaker is not in characters")
        lines = entry.get("lines")
        if not isinstance(lines, list) or not lines:
            errors.append(f"{entry_id}: lines must be a non-empty array")
            continue
        for i, line in enumerate(lines, start=1):
            if not isinstance(line, str) or not line.strip():
                errors.append(f"{entry_id} line {i}: empty or non-string line")
                continue
            all_lines.append((entry_id, i, line))
            if len(line) > max_chars:
                errors.append(
                    f"{entry_id} line {i}: {len(line)} chars exceeds soft limit {max_chars}: {line!r}"
                )

    for key, value in ui.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            errors.append(f"invalid UI string: {key!r}")

    # Regional expressions with a deliberately identifiable speaker profile.
    speaker_rules = [
        (("wha' gwaan", "wha'appen", "rhaatid", "bless up", "walk good", "nuff cable", "nuff steps", "criss,"), "kade"),
        (("asere", "qué bolá", "fuácata", "mi ambia", "ñó,"), "lazaro"),
        (("acho,", "bendito,", "zumba,"), "lia"),
        (("no manches", "órale"), "chava"),
        (("parce,", "bacano"), "vale"),
        (("quilombo", "che,"), "che"),
    ]
    for entry in dialogues:
        folded = "\n".join(entry.get("lines", [])).casefold()
        speaker = entry.get("speaker")
        for markers, required_speaker in speaker_rules:
            if any(marker.casefold() in folded for marker in markers) and speaker != required_speaker:
                errors.append(f"{entry.get('id')}: regional marker belongs to {required_speaker}, not {speaker}")

    return errors


def main() -> int:
    if not DATA_PATH.is_file():
        print(f"ERROR: missing {DATA_PATH}", file=sys.stderr)
        return 2
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read localization JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    entries = data["dialogue"]
    line_count = sum(len(entry["lines"]) for entry in entries)
    print(f"OK: {len(entries)} dialogue entries, {len(data['characters'])} character profiles, {len(data['ui'])} UI strings.")
    print(f"OK: {line_count} manual dialogue lines fit the provisional {data['meta']['soft_max_chars_per_line']}-character limit.")
    print("OK: IDs are unique, speakers exist, and marked regional expressions match their character profiles.")
    print("NOTE: this checks localization data only. It does not verify ROM encoding, insertion, or in-game display.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
