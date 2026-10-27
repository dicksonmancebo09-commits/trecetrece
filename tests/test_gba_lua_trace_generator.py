from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "generate_mgba_lua_trace.py"
SPEC = importlib.util.spec_from_file_location("generate_mgba_lua_trace", MODULE)
assert SPEC and SPEC.loader
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)

CONFIG = json.loads((ROOT / "config" / "gba_lab.json").read_text(encoding="utf-8"))
TEMPLATE = (ROOT / "tools" / "mgba" / "trace_gba.lua.in").read_text(encoding="utf-8")


class TestLuaTraceGenerator(unittest.TestCase):
    def test_generates_complete_trace_without_placeholders(self):
        output_dir = "/tmp/trecetrece/private-roms/diagnostics"
        rendered = generator.render_trace(CONFIG, TEMPLATE, output_dir)
        self.assertNotRegex(rendered, r"__[A-Z0-9_]+__")
        self.assertIn('local OUT_DIR = "/tmp/trecetrece/private-roms/diagnostics"', rendered)
        self.assertIn("local AUTO_INPUT = false", rendered)
        self.assertIn("C.GBA_KEY.START", rendered)
        self.assertIn("0x3000BDE", rendered)
        self.assertIn("local STOP_AFTER_FRAME = 1800", rendered)

    def test_unconfigured_memory_address_fails_closed(self):
        config = json.loads(json.dumps(CONFIG))
        del config["emulator"]["lua_trace"]["memory_addresses"]["BG2CNT"]
        with self.assertRaisesRegex(ValueError, "memory_addresses missing"):
            generator.render_trace(config, TEMPLATE)

    def test_invalid_key_fails_closed(self):
        config = json.loads(json.dumps(CONFIG))
        config["emulator"]["lua_trace"]["auto_input_steps"][0]["key"] = "RESET"
        with self.assertRaisesRegex(ValueError, "Unsupported GBA key"):
            generator.render_trace(config, TEMPLATE)

    def test_capture_frames_must_be_non_empty(self):
        config = json.loads(json.dumps(CONFIG))
        config["emulator"]["lua_trace"]["capture_frames"] = []
        with self.assertRaisesRegex(ValueError, "capture_frames"):
            generator.render_trace(config, TEMPLATE)


if __name__ == "__main__":
    unittest.main()
