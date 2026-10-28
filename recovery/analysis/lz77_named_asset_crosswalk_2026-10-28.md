# Prioritized LZ77 assets — named cross-reference (2026-10-28)

## Result

I cross-referenced the **158 highest-priority LZ77 candidates** from the local scan against the US-version offset manifest in the public Metroid Fusion decompilation project `metroidret/mf`. **133 candidates match a named manifest offset exactly; 25 remain unresolved in that manifest.** This is a substantial improvement over interpreting raw bytes only.

- ROM hash: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`
- Candidate rule: exact pointer reference plus at least 8 KiB decompressed output.
- Upstream metadata: [`database.json`](https://github.com/metroidret/mf/blob/main/database.json) — used only to cross-reference offset and extraction path. No source code or binary assets were copied.
- The upstream repo declares the MIT license. The naming crosswalk remains a hypothesis about how the game uses each asset until confirmed by execution.

## Matched categories

| Category | Exact offset matches |
|---|---:|
| `tilesets` | 84 |
| `new_file_intro` | 22 |
| `ending` | 17 |
| `menus` | 7 |
| `Blob_6101b8_612e48.bin` | 1 |
| `sa_x_close_up` | 1 |
| `Blob_6131c8_63a19c.bin` | 1 |

## Confirmed names worth pursuing first

| ROM offset | Manifest path | Why this matters |
|---|---|---|
| `0x3EF960` | `tilesets/0_bg.gfx.lz` | Background tiles for tileset 0 |
| `0x3F6C34` | `tilesets/19.gfx.lz` | Named graphics set |
| `0x42011C` | `tilesets/16.gfx.lz` | Named graphics set, referenced from a clustered resource table |
| `0x590C9C` | `menus/title_screen/objects.gfx.lz` | Title-screen objects |
| `0x593274` | `menus/title_screen/logo.gfx.lz` | Title-screen logo |
| `0x605D08` | `menus/title_screen/space_background.gfx.lz` | Title-screen space background |
| `0x56A254` | `menus/pause_screen/bg.gfx.lz` | Pause-screen background |
| `0x56F71C` | `menus/pause_screen/obj.gfx.lz` | Pause-screen objects |
| `0x59DB08` | `new_file_intro/hornoad_encounter_obj.gfx.lz` | New-file intro: encounter objects |
| `0x5A44CC` | `new_file_intro/hornoad_encounter_bg.gfx.lz` | New-file intro: encounter background |
| `0x5C9B4C` | `new_file_intro/suit_removal_surgery.gfx.lz` | Intro/cutscene graphics |
| `0x5DB5CC` | `new_file_intro/samus_reborn_bg_bottom.gfx.lz` | Intro/cutscene background layer |
| `0x5EDF70` | `new_file_intro/samus_monologue_bg.gfx.lz` | Intro/cutscene background |
| `0x60093C` | `new_file_intro/samus_sitting.gfx.lz` | Intro/cutscene graphics |
| `0x72F2E0` | `sa_x_close_up/graphics.gfx.lz` | SA-X close-up scene |
| `0x74EB50` | `ending/space_bg.gfx.lz` | Ending sequence |
| `0x761A88` | `ending/ending_0_top.gfx.lz` | Ending image segment 0, top |
| `0x767278` | `ending/ending_0_bottom.gfx.lz` | Ending image segment 0, bottom |
| `0x7944E4` | `ending/results_english_text.gfx.lz` | Ending-results text graphics |
| `0x797D08` | `ending/results_spanish_text.gfx.lz` | Spanish ending-results text graphics |

The complete list of all matched and unmatched P1 offsets is in the JSON crosswalk alongside this report.

## What this proves — and what it doesn't

- **Proven by offset match:** the public US-version manifest assigns these exact offsets to the listed extraction paths.
- **Strong lead:** names such as `tilesets/16.gfx.lz`, `menus/title_screen/logo.gfx.lz` and `new_file_intro/suit_removal_surgery.gfx.lz` make it possible to focus the next work on meaningful assets instead of anonymous byte sequences.
- **Not yet proven:** which code path loads the resource in the runtime, exact palette/tilemap pairing, and whether a replacement at that location can be made safely. Those require the corresponding table/loader analysis and emulator validation.

## Unresolved P1 offsets

`0x65C468`, `0x65FC24`, `0x6238F4`, `0x62B5F4`, `0x663EAC`, `0x679420`, `0x67D7CC`, `0x6150E8`, `0x61B89C`, `0x626738`, `0x66B524`, `0x73422C`, `0x577024`, `0x578750`, `0x675098`, `0x58340C`, `0x57C0C4`, `0x742FB4`, `0x667C18`, `0x66EC18`, `0x6186A4`, `0x6217A8`, `0x6724C0`, `0x73DC20`, `0x582BBC`

## Next technical operation

Correlate these named resources with their source-pointer clusters and the game code that loads them. Start with the title screen and the `new_file_intro` group because both can be separated into known graphic resources; then validate one resource in mGBA before changing bytes.
