# Tarea 1 — Línea base visual

**Fecha:** 27 de octubre de 2026  
**Estado:** auditoría de archivos terminada; falta una captura original obtenida en ejecución.  
**Cambios de ROM en esta tarea:** ninguno.

## 1. ROM base de referencia

Archivo de trabajo local: `Metroid Fusion (USA, Australia).gba`

- Tamaño: 8.388.608 bytes (8 MiB).
- Código GBA: `AMTE`.
- Título de cabecera: `METROID4USA`.
- Checksum de cabecera: `0x98`, coincide con el valor calculado.
- SHA-256: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.
- La sonda estática lee la palabra inicial `0xEA00002E`, decodificada como salto ARM desde `0x08000000` hasta `0x080000C0` (offset de archivo `0xC0`). Es una comprobación del punto de entrada, no una comprensión del código completo.

Esta versión será la **base maestra de solo lectura**. Las versiones de proyecto se mantienen como referencias separadas.

## 2. Versiones anteriores auditadas

| Archivo | SHA-256 | Bytes distintos respecto a la base | Alcance conocido |
|---|---|---:|---|
| ROM original | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` | 0 | Base maestra. |
| v0.8 | `de4217c5df5e7b7d57d9bb43555a2f4ee3b62bf873b65817e768340911569850` | 42.634 | Incluye los cambios de música descritos en el paquete v0.8. |
| v0.9 visual | `54f3291e54fdca088d440ef2dd51f41dc2c80b17c195956f633660ab790e3b00` | 50.666 | Prueba previa de fondo BG3 en Main Deck room 1. |
| v1.0 Urban Opening | `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5` | 59.501 | Prueba visual de room 0; no es una transformación completa. |

Todos los archivos revisados tienen 8 MiB y código `AMTE`. El recuento de bytes distintos sirve para comparar archivos, no equivale a la cantidad de recursos gráficos cambiados.

Los informes previos no acreditan una prueba de ejecución confirmada en MAGE o emulador.

## 3. Inventario visual disponible

- `Villa_Duarte_BG3_extracted_from_ROM.png` — 256 × 512: atlas de tiles BG3 extraído de la ROM; no es una captura de la sala.
- `Villa_Duarte_MainDeck_room1_CC0_preview.png` — 544 × 384: composición de prueba con arte CC0.
- `Villa_Duarte_MainDeck_room1_palette_preview.png` — 544 × 384: variante comparativa de paleta.
- `Villa_Duarte_v1.0_actual_ROM_full_room.png` — 544 × 224: reconstrucción del mapa de room 0 en la ROM v1.0.
- `Villa_Duarte_v1.0_actual_ROM_opening_preview.png` — 720 × 480: preview ampliado de room 0.
- `CC0_Pico8_City_tiles.png` — 215 × 134: fuente de tiles urbanos CC0.
- `Villa_Duarte_CC0_Adapted_BG3Palette_8x8.png` — 256 × 128: atlas 8×8 adaptado a una paleta de referencia.
- `Villa_Duarte_Tileset_MAGE_DRAFT.png` — 256 × 128: borrador; no demuestra que se haya importado correctamente en MAGE.

Las previews de room 1 y la reconstrucción v1.0 están etiquetadas como propuestas o reconstrucciones: **no son capturas verificadas de una sesión de juego**.

## 4. Sala benchmark provisional

**Selección de trabajo: `AREA_MAIN_DECK`, room index 1 — Docking Bays.**

La elegimos porque ya existen un atlas BG3 extraído, una composición con tiles CC0 y una variante de paleta. Así podemos comparar y reutilizar el trabajo de investigación previo sin tomar la sala inicial ya modificada como referencia visual nueva.

Antes de editar, falta abrir la ROM base en una herramienta compatible y obtener una captura reproducible de la sala original. En esta sesión, `MAGE`, `mGBA` y `Ghidra` no aparecieron como comandos en `PATH`; podrían existir en otra ubicación, pero no se han ejecutado aquí.

## 5. Pasado, presente y futuro

- **Pasado:** v0.8 documenta cambios de música; v0.9 prueba un fondo BG3 de room 1; v1.0 transforma la apariencia de room 0. Ninguno debe tratarse como una transformación completa del juego.
- **Presente:** la ROM base y los prototipos están identificados por SHA-256. La sonda GBA pasó 4/4 pruebas unitarias con fixtures sintéticos; eso prueba la herramienta, no la jugabilidad.
- **Futuro:** conseguir la vista original de Docking Bays, comparar su mapa y paleta, preparar un A/B pequeño y validar la primera modificación con herramienta/emulador. Después se propagará el sistema al resto de áreas.

## Resultado

**Completado:** verificación básica de la ROM base, registro de hashes, auditoría de recursos y elección provisional de Docking Bays como benchmark.  
**Pendiente:** captura original en ejecución y confirmación en herramienta compatible. No se modificó la ROM durante la Tarea 1.
