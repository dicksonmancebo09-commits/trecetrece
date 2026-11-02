#!/usr/bin/env python3
"""Unit tests for the narrow ARM/Thumb branch decoders in metroid_bootstrap_probe."""

from __future__ import annotations

import unittest

from metroid_bootstrap_probe import decode_arm_b, decode_thumb_bl, decode_thumb_b


class BranchDecoderTests(unittest.TestCase):
    def test_gba_header_branch_targets_bootstrap(self) -> None:
        result = decode_arm_b(0xEA00002E, 0x08000000)
        self.assertEqual(result["mnemonic"], "B")
        self.assertEqual(result["target_address"], "0x080000C0")

    def test_arm_return_branch_targets_bootstrap_loop(self) -> None:
        result = decode_arm_b(0xEAFFFFF2, 0x080000F0)
        self.assertEqual(result["target_address"], "0x080000C0")

    def test_thumb_bl_targets_08000798(self) -> None:
        target = decode_thumb_bl(0xF000, 0xFAB1, 0x08000232)
        self.assertEqual(target, 0x08000798)

    def test_thumb_unconditional_branch_targets_08000766(self) -> None:
        target = decode_thumb_b(0xE296, 0x08000236)
        self.assertEqual(target, 0x08000766)

    def test_thumb_negative_branch_sign_extension(self) -> None:
        # A short backward branch from the next instruction's PC.
        target = decode_thumb_b(0xE7FE, 0x08001000)
        self.assertEqual(target, 0x08001000)

    def test_invalid_thumb_bl_prefix_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_thumb_bl(0xE800, 0xF000, 0x08000232)

    def test_invalid_thumb_branch_opcode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_thumb_b(0xF000, 0x08000236)


if __name__ == "__main__":
    unittest.main(verbosity=2)
