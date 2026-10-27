#!/usr/bin/env python3
"""Generate the mGBA Lua trace from the central GBA lab profile.

Generated Lua is written only inside the Git-ignored private-roms/diagnostics/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VALID_GBA_KEYS = {"A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L"}
PLACEHOLDER_RE = re.compile(r"__[A-Z0-9_]+__")


def lua_number(value: str | int) -> str:
    return f"0x{value:X}" if isinstance(value, int) else f"0x{int(value, 0):X}"


def render_trace(config: dict[str, Any], template: str, output_directory: str | None = None) -> str:
    trace = config.get("emulator", {}).get("lua_trace")
    if not isinstance(trace, dict):
        raise ValueError("config must define emulator.lua_trace")
    if int(trace.get("sample_interval_frames", 0)) <= 0:
        raise ValueError("sample_interval_frames must be greater than zero")
    if int(trace.get("stop_after_frame", 0)) <= 0:
        raise ValueError("stop_after_frame must be greater than zero")

    capture_frames = trace.get("capture_frames")
    if not isinstance(capture_frames, list) or not capture_frames:
        raise ValueError("capture_frames must be a non-empty array")
    if any(not isinstance(frame, int) or frame < 0 for frame in capture_frames):
        raise ValueError("capture_frames must contain non-negative integers")

    input_steps = trace.get("auto_input_steps", [])
    rendered_steps = []
    for row in input_steps:
        key = str(row.get("key", "")).upper()
        if key not in VALID_GBA_KEYS:
            raise ValueError(f"Unsupported GBA key in Lua trace: {key!r}")
        start = int(row["start_frame"])
        end = int(row["end_frame_exclusive"])
        if start < 0 or end <= start:
            raise ValueError(f"Invalid frame range for key {key}: {start}..{end}")
        rendered_steps.append(
            f"    {{ start_frame = {start}, end_frame_exclusive = {end}, key = C.GBA_KEY.{key} }},"
        )
    step_literal = "{\n" + "\n".join(rendered_steps) + "\n}" if rendered_steps else "{}"
    capture_literal = "{ " + ", ".join(str(x) for x in capture_frames) + " }"

    memory = trace.get("memory_addresses", {})
    required_memory = {
        "gMainGameMode", "gSubGameMode1", "gSubGameMode2",
        "DISPCNT", "BG1CNT", "BG2CNT", "BG3CNT", "VCOUNT", "KEYINPUT"
    }
    if not required_memory.issubset(memory):
        missing = sorted(required_memory.difference(memory))
        raise ValueError(f"memory_addresses missing: {', '.join(missing)}")
    memory_literal = "{\n" + "\n".join(
        f"    {name} = {lua_number(memory[name])}," for name in sorted(required_memory)
    ) + "\n}"

    values = {
        "__OUT_DIR_LUA__": json.dumps(str(output_directory or trace.get("output_directory", "private-roms/diagnostics"))),
        "__AUTO_INPUT_LUA__": "true" if trace.get("auto_input_enabled_by_default", False) else "false",
        "__SAMPLE_INTERVAL_FRAMES__": str(int(trace["sample_interval_frames"])),
        "__STOP_AFTER_FRAME__": str(int(trace["stop_after_frame"])),
        "__CAPTURE_FRAMES_LUA__": capture_literal,
        "__AUTO_INPUT_STEPS_LUA__": step_literal,
        "__MEMORY_ADDRESSES_LUA__": memory_literal,
    }
    rendered = template
    for marker, value in values.items():
        rendered = rendered.replace(marker, value)
    remaining = PLACEHOLDER_RE.findall(rendered)
    if remaining:
        raise ValueError(f"Unexpanded placeholders remain: {', '.join(sorted(set(remaining)))}")
    return rendered


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Render a configured mGBA Lua trace into the private diagnostics directory.")
    parser.add_argument("--config", type=Path, default=root / "config" / "gba_lab.json")
    parser.add_argument("--template", type=Path, default=root / "tools" / "mgba" / "trace_gba.lua.in")
    parser.add_argument("--output", type=Path, default=root / "private-roms" / "diagnostics" / "mgba-trace-generated.lua")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        template = args.template.read_text(encoding="utf-8")
        output = args.output.resolve()
        private_diag = (root / "private-roms" / "diagnostics").resolve()
        if not output.is_relative_to(private_diag):
            raise ValueError("Generated Lua must be saved under private-roms/diagnostics/ (ignored by Git).")
        rendered = render_trace(config, template, str(output.parent))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Generated mGBA trace: {output}")
        print(f"Sample interval: {config['emulator']['lua_trace']['sample_interval_frames']} frames")
        print(f"Capture frames: {config['emulator']['lua_trace']['capture_frames']}")
        print(f"Automated input enabled by default: {config['emulator']['lua_trace']['auto_input_enabled_by_default']}")
        print("Load it via mGBA GUI > Tools > Scripting > Load Script on a build with Lua scripting enabled.")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"generate_mgba_lua_trace: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
