import json
import unittest
from pathlib import Path

from tools.check_localization_es419 import validate


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "localization" / "es-419" / "dialogue.json"


class TestSpanishCaribbeanLocalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_pack_passes_static_validation(self):
        self.assertEqual(validate(self.data), [])

    def test_has_seven_scenarios_and_regional_voices(self):
        scenarios = {entry["scenario"] for entry in self.data["dialogue"]}
        speakers = {entry["speaker"] for entry in self.data["dialogue"]}
        self.assertEqual(scenarios, set(range(1, 8)))
        self.assertTrue({"yeyo", "majo", "lazaro", "lia", "kade"}.issubset(speakers))

    def test_patois_and_regional_markers_have_consistent_speakers(self):
        by_id = {entry["id"]: entry for entry in self.data["dialogue"]}
        self.assertEqual(by_id["S01_KADE_001"]["speaker"], "kade")
        self.assertEqual(by_id["S02_LAZARO_001"]["speaker"], "lazaro")
        self.assertEqual(by_id["S02_LIA_001"]["speaker"], "lia")
        self.assertEqual(by_id["S06_CHAVA_001"]["speaker"], "chava")
        self.assertFalse(by_id["S06_CHAVA_001"]["enabled_by_default"])


if __name__ == "__main__":
    unittest.main()
