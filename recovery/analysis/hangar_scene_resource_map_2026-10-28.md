# Escena del hangar BSL: flujo y recursos localizados (2026-10-28)

## Objetivo

Localizar el punto de la introducción en el que la nave aterriza en el hangar, separar los recursos que usa y preparar una prueba controlada para entrar directamente a esa escena. Este documento usa nombres y direcciónes de un manifiesto de la versión estadounidense y del código de referencia de una descompilación pública; **no representa una ejecución de la ROM modificada**.

## Ruta del estado

En la referencia de código, `NewFileIntroHandler()` procesa `gSubGameMode1`:

| Estado | Rutina | Función narrativa |
|---:|---|---|
| 0 | `NewFileIntroInit()` | Inicialización |
| 1 | temporizador de 100 frames | Pausa inicial |
| 2 | `NewFileIntroSr388Preview()` | Vista previa de SR388 |
| 3 | `NewFileIntroInSr388()` | Acción en SR388 |
| 4 | `NewFileIntroSamusShipFlying()` | Nave de Samus en vuelo |
| 5 | `NewFileIntroSamusFainting()` | Samus se desmaya |
| 6 | `NewFileIntroSamusDrifting()` | Samus a la deriva |
| 7 | `NewFileIntroSamusFound()` | Samus encontrada |
| 8 | `NewFileIntroSamusGettingCured()` | Procedimiento médico |
| 9 | `NewFileIntroSamusCured()` | Samus curada |
| 10 | `NewFileIntroArrivingAtBsl()` | Llegada a la estación |
| **11** | `NewFileIntroLandingOnBsl()` | **Aterrizaje en el hangar** |
| 12 | guardado/fundido final | Cierre de la introducción |

El estado 11 es el objetivo más cercano a “cuando la nave entra al hangar”. La escena tiene inicialización propia y datos específicos de la puerta y sus luces; no es simplemente un fotograma del fondo anterior.

## Recursos de la escena

| Offset ROM | Recurso identificado | Rol |
|---|---|---|
| `0x5F7190` | `new_file_intro/landing_on_bsl_bg.gfx.lz` | Gráficos del fondo del hangar |
| `0x5FAB54` | `new_file_intro/landing_on_bsl_obj.gfx.lz` | Gráficos de objetos/sprites |
| `0x5FF708` | `new_file_intro/landing_on_bsl_bg.pal` | Paleta del fondo |
| `0x5FFD08` | `new_file_intro/landing_on_bsl_obj.pal` | Paleta de objetos |
| `0x5FFF08` | `new_file_intro/landing_on_bsl_space.tm.lz` | Tilemap del espacio |
| `0x60030C` | `new_file_intro/landing_on_bsl_hangar.tm.lz` | Tilemap del hangar |
| `0x598898` | `new_file_intro/samus_ship_flying_text.tm.lz` | Tilemap de texto compartido |
| `0x5E116C` | `new_file_intro/approaching_bsl_obj.gfx.lz` | Objetos de la escena de aproximación |
| `0x5F5254` | `new_file_intro/approaching_bsl_obj.pal` | Paleta de la aproximación |
| `0x5E8A10` | `new_file_intro/space_map_bg` | Fondo/mapa de la aproximación a BSL |
| `0x5EDF70` | `new_file_intro/samus_monologue_bg.gfx.lz` | Fondo de monólogo previo |
| `0x60BCA4` | `new_file_intro/bsl_space_bg.gfx.lz` | Fondo espacial anterior |
| `0x612E48` | `new_file_intro/bsl_space_bg.pal` | Paleta de ese fondo |

Los nombres de fichero y offsets se contrastaron con `database.json` del repositorio de referencia. La tabla completa con tamaño declarado y procedencia está en el JSON junto a este informe.

## Dónde y cómo se cargan

La rutina de inicialización de aterrizaje referencia explícitamente estos recursos y destinos:

| Recurso | Destino de vídeo GBA | Base conocida |
|---|---|---|
| `landing_on_bsl_obj.gfx.lz` | `0x06010000` (VRAM de objetos) | `LZ77UncompVram(..., VRAM_OBJ)` |
| `landing_on_bsl_obj.pal` | `0x05000200` (paleta de objetos) | `DMA3_COPY_32(..., PALRAM_OBJ, ...)` |
| `landing_on_bsl_bg.gfx.lz` | `0x06000000` (VRAM de fondos) | `LZ77UncompVram(..., VRAM_BASE)` |
| `landing_on_bsl_hangar.tm.lz` | `0x0600F000` | `VRAM_BASE + 0xF000` |
| `landing_on_bsl_space.tm.lz` | `0x0600F800` | `VRAM_BASE + 0xF800` |
| `samus_ship_flying_text.tm.lz` | `0x0600E000` | `VRAM_BASE + 0xE000` |
| `landing_on_bsl_bg.pal` | `0x05000000` (paleta de fondos) | `DMA3_COPY_32(..., PALRAM_BASE, ...)` |

La enumeración de OAM de aterrizaje incluye nave, puerta, luces de puerta, humo y elementos de desplazamiento. Esto confirma que los gráficos, las paletas y los mapas deben cargarse desde la rutina real de aterrizaje.

## Parche candidato, todavía no aprobado como build jugable

En la copia de ROM con SHA-256 `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`, la rutina de control comienza en el offset `0x87708`. En la ruta de archivo nuevo, después de la inicialización, hay una instrucción Thumb `MOVS r0, #1` en `0x8777E`, seguida por el almacenamiento de `gSubGameMode1`. Cambiar el inmediato de 1 a 11 haría que el selector entre directamente en el estado 11 tras pasar por esa inicialización:

- Antes: offset `0x8777E`, bytes `01 20` (`MOVS r0, #1`).
- Candidato: bytes `0B 20` (`MOVS r0, #11`).
- Cambio único esperado: byte `0x8777E`, de `0x01` a `0x0B`.

El script `scripts/build_hangar_entry_test.py` comprueba la identidad exacta de la ROM, los bytes de contexto y que el resultado difiera en un solo byte. Por defecto solo muestra el plan; `--apply` genera una ROM de prueba fuera del repositorio, bajo `private-roms/rea-analysis/`. **Este candidato no se considera verificado hasta comprobar en mGBA el arranque desde una partida nueva, el aterrizaje, el guardado y el retorno al juego.** No aplicarlo a una ROM de hash distinto.

## Fuentes de referencia

- [Control de la introducción](https://github.com/metroidret/mf/blob/main/src/new_file_intro.c)
- [Datos gráficos y mapas de la introducción](https://github.com/metroidret/mf/blob/main/src/data/new_file_intro_data.c)
- [Manifiesto de offsets de la versión US](https://github.com/metroidret/mf/blob/main/database.json)
- [Tipos de objetos de la escena del hangar](https://github.com/metroidret/mf/blob/main/include/constants/new_file_intro.h)

Estas referencias se usan para asignar nombres y entender el flujo, no como prueba de que la ROM de prueba ya funciona.
