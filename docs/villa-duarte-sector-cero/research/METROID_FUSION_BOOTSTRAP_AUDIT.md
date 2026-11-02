# Metroid Fusion AMTE — bootstrap audit

Audit date: 2026-11-02  
Target: Metroid Fusion USA/Australia (GBA, game code `AMTE`)  
Status: **partial static confirmation; no ROM modifications**

## Scope and provenance

This record combines:
1. ROM identity and bytes reported from the user's local Codespace.
2. Targeted Ghidra 12.1.4 disassembly using `ARM:LE:32:v4t:default`.
3. Arithmetic decoding of the ARMv4T/Thumb branch encodings shown below.

The ROM itself, extracted assets, patches, Ghidra database, and generated reports are not stored in this public repository.

Recorded ROM identity:

| Field | Value |
|---|---|
| Size | 8,388,608 bytes (8 MiB) |
| Game code | `AMTE` |
| SHA-256 | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` |
| Ghidra | 12.1.4 |
| Ghidra language | `ARM:LE:32:v4t:default` |
| Mapping base | `0x08000000` |
| Import | Raw Binary |
| Automatic full-ROM analysis | Disabled during the targeted import |

The hash and identity match the repository's existing [ROM inventory](../../../recovery/analysis/rom_inventory.json).

## 1. GBA entry

The first little-endian word is `0xEA00002E`, with bytes:

```text
file offset 0x000000 / bus address 0x08000000
2E 00 00 EA
```

Ghidra decoded it as:

```asm
08000000  B 0x080000C0
```

This entry branch and its destination were confirmed in the user's Ghidra session.

## 2. ARM-mode bootstrap — Ghidra-confirmed window

Ghidra decoded the following instructions:

| Bus address | File offset | Bytes | Ghidra result |
|---|---:|---|---|
| `080000C0` | `00C0` | `12 00 A0 E3` | `MOV r0,#0x12` |
| `080000C4` | `00C4` | `00 F0 29 E1` | `MSR CPSR_cf,r0` |
| `080000C8` | `00C8` | `28 D0 9F E5` | `LDR sp,[0x080000F8]` |
| `080000CC` | `00CC` | `1F 00 A0 E3` | `MOV r0,#0x1F` |
| `080000D0` | `00D0` | `00 F0 29 E1` | `MSR CPSR_cf,r0` |
| `080000D4` | `00D4` | `18 D0 9F E5` | `LDR sp,[0x080000F4]` |
| `080000D8` | `00D8` | `1C 10 9F E5` | `LDR r1,[0x080000FC]` |
| `080000DC` | `00DC` | `20 00 8F E2` | `ADR r0,0x08000104` |
| `080000E0` | `00E0` | `00 00 81 E5` | `STR r0,[r1,#0x0]` |

The CPSR mode values are:
- `0x12`: IRQ mode.
- `0x1F`: System mode.

The literal words at file offsets `0xF4` through `0x100`, read little-endian from the supplied `xxd` output, are:

| File offset | Value | Interpretation |
|---|---|---|
| `0xF4` | `0x03007E60` | System-mode SP value loaded at `0x080000D4` |
| `0xF8` | `0x03007FA0` | IRQ-mode SP value loaded at `0x080000C8` |
| `0xFC` | `0x03007FFC` | Address receiving the handler pointer |
| `0x100` | `0x08000231` | Pointer used for ARM-to-Thumb interworking |

The `0x03007FFC` location is the conventional GBA IWRAM IRQ-vector pointer. The startup sequence writes `0x08000104` to that location. The target at `0x08000104` is therefore identified as the registered IRQ-handler entry; its complete behavior has not yet been audited.

## 3. ARM-to-Thumb handoff — byte-derived, awaiting Ghidra confirmation

The raw bytes reported for file offsets `0xE4`–`0xF0` are:

```text
14 10 9F E5  0F E0 A0 E1  11 FF 2F E1  F2 FF FF EA
```

Their ARM encodings decode to the following sequence:

| Bus address | Encoding interpretation | Consequence |
|---|---|---|
| `080000E4` | `LDR r1,[pc,#0x14]` | Reads the pointer at `0x08000100` |
| `080000E8` | `MOV lr,pc` | Sets LR to `0x080000F0` (ARM PC is instruction address + 8) |
| `080000EC` | `BX r1` | Branches through `0x08000231`, selecting Thumb state |
| `080000F0` | `B 0x080000C0` | Return continuation if the Thumb routine returns to LR |

This interpretation is consistent with the GBA ARM7TDMI interworking rules, but this particular range is marked byte-decoded until the committed Ghidra audit prints it.

## 4. Initial Thumb control flow — calculated, awaiting Ghidra confirmation

The bytes at file offset `0x230` are:

```text
70 B5 00 F0 B1 FA 96 E2
```

The pointer `0x08000231` has bit zero set; its Thumb instruction address is `0x08000230`.

Using the ARMv4T Thumb two-halfword `BL` encoding and Thumb PC-relative branch rules:

| File offset | Halfword(s) | Calculated target | Status |
|---|---|---|---|
| `0x232` | `F000 FAB1` | `0x08000798` | Encoding-derived; Ghidra verification pending |
| `0x236` | `E296` | `0x08000766` | Encoding-derived; Ghidra verification pending |

The unconditional branch at `0x08000236` means bytes at `0x238` and beyond are not assumed to be sequentially reachable from this path. They may be another code region or data; an independent reference is needed before classifying them.

## 5. What is and is not established

**Confirmed by the supplied Ghidra output**
- The ROM maps at `0x08000000` under `ARM:LE:32:v4t`.
- The first instruction branches to `0x080000C0`.
- The ARM startup window from `0x080000C0` through `0x080000E0` decodes as listed above.
- The exact ROM hash, size, and game code match the recorded inventory.

**Derived from the supplied raw bytes, not yet confirmed by the new Ghidra Thumb pass**
- The ARM handoff at `0x080000E4`–`0x080000EC`.
- The pointer at `0x08000100` leading to Thumb address `0x08000230`.
- Thumb `BL` and `B` targets `0x08000798` and `0x08000766`.

**Not yet established**
- The complete IRQ handler behavior.
- The meaning of the first Thumb `BL` target and branch destination.
- The main game loop, frame scheduler, player logic, room loader, and enemy update routines.
- Runtime behavior under an emulator/debugger.
- Any editable reconstruction or reproducible game build.

## 6. Automated local audit

The repository now contains:
- `tools/metroid_bootstrap_probe.py`: read-only identity, literal, ARM branch, Thumb `BL`, and Thumb `B` byte verifier.
- `recovery/ghidra_scripts/MetroidFusionBootstrapAudit.java`: targeted ARM and Thumb disassembly script. It checks the Ghidra language ID before decoding.
- `recovery/scripts/run_ghidra_bootstrap_audit.sh`: one-command wrapper that runs the byte verifier and then Ghidra against the existing local project.

Run from the Codespace terminal:

```bash
bash recovery/scripts/run_ghidra_bootstrap_audit.sh \
  "/workspaces/gba/Metroid Fusion (USA, Australia).gba"
```

The wrapper requires the exact recorded SHA-256 and AMTE identity, refuses to process a ROM located inside the repository, and expects the existing project `~/AI-Tools/ghidra-projects/MetroidFusion_AMTE_ARMv4T`.

Generated JSON and logs are written under:

```text
~/AI-Tools/ghidra-projects/reports/
```

The scripts only read the ROM. Ghidra saves disassembly annotations in the local project database; the original ROM is not rewritten.

## 7. External reference boundary

The public [Metroid Fusion decompilation](https://github.com/metroidret/mf) is a useful research reference, but its README explicitly says it is not shiftable and must not be used as a base for another project. It is therefore not treated as a drop-in source tree or as proof of the local ROM's instruction flow.

The generic REA raw-binary path also has a limitation: its `arm` option maps to `ARM:LE:32:v7`, not GBA ARMv4T. The local exact lane remains direct Ghidra import with `ARM:LE:32:v4t`.
