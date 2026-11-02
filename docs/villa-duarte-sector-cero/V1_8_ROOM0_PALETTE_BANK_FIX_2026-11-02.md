# v1.8 candidata — corrección del banco de paleta de L01_R001

**Fecha:** 2 de noviembre de 2026  
**Base:** v1.7, SHA-256 `66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf`  
**Salida local privada:** `LATINO_AMERICA_Zector_Cero_v1.8_TILESET_PALETTE_FIX.gba`  
**SHA-256 candidato:** `3bc764355012268d4ac6ef315bb9bb09ac0e5405d1c456bb506d1fdbe862af89`

## Hallazgo y evidencia

La auditoría anterior de v1.7 comprobó cabecera, bytes de arranque, punteros, descompresión, longitudes, transparencia y mapas BG. No comprobó si el banco de paleta de la tabla custom era compatible con el orden de carga del motor.

La fuente upstream fijada `metroidret/mf@de76565c897c05838503717db9aa2adfe92aeba3`, en `src/room.c`, muestra que `RoomLoadTileset` copia primero la paleta del tileset a los bancos BG 2–15 y después copia las tres primeras filas de `sCommonTilesPal` a los bancos 0–2. `include/gba/memory.h` declara `PAL_ROW=16` colores y `PAL_ROW_SIZE=32` bytes. Por tanto, el banco 2 se sobrescribe con la tercera fila de la paleta común.

La tabla custom activa de `L01_R001` en v1.7 (`0x7B0000`) contiene 384 metatiles y 1.536 subtiles; todos sus 1.536 words usan el banco 2. Esos words referencian los tiles gráficos 192–560. La tabla original `tilesets/61.tm` usa bancos 0, 1, 3 y 4, y no usa el banco 2. La paleta custom v1.7 (`tilesets/76.pal`, offset `0x46B494`) consta de 14 filas idénticas, así que el banco 3 (fila 1 del recurso) conserva los mismos colores custom.

## Cambio candidato

La v1.8 cambia únicamente los bits de banco de paleta 12–15 de los 1.536 words de la tabla custom, de 2 a 3:

- Rango editado: `0x7B0002–0x7B0C01`.
- Bytes modificados: **1.536** (un byte por subtile word).
- Índices de tiles, bits H/V flip y estructura de la tabla: preservados.
- BG1, BG2, clipdata, GFX, paleta, título, punteros y restantes bytes: sin cambios.
- Checksum de cabecera: permanece válido (`0x6D`).

La ROM v1.7 original no se sobrescribe. La candidata se construyó con hash base exacto y aserciones de bytes/banco de paleta.

## Render estático comparado con el motor

Se generaron dos reconstrucciones de `L01_R001` aplicando el orden de carga de paletas descrito en la fuente:

- v1.7: banco 2 toma la fila común 2, porque la escritura de la paleta común ocurre después de la paleta del tileset.
- v1.8: banco 3 toma la fila 1 del recurso custom de tileset 76.

Ambas usan los mismos mapas BG activos, la tabla de metatiles y 369 tiles gráficos; ambas tienen 0 referencias de tile fuera de rango. Son renders estáticos, no capturas del emulador.

## Automatización

Se añadieron:
- `tools/fix_v17_room0_palette_bank.py`: corrector SHA-pinned; se niega a editar cualquier ROM que no sea la v1.7 exacta.
- `tests/test_fix_v17_room0_palette_bank.py`: valida que solo cambien los bits de banco, y rechaza tablas mixtas o mal formadas.
- `tools/gba_rom_audit.py`: ahora puede verificar bancos de paleta esperados mediante `expected_palette_banks`.
- `tools/render_v18_room0.py`: renderiza la sala inicial usando el banco visible tras el orden de carga.
- Perfil `zector_cero_v1_8_palette_fix` en `config/gba_lab.json`.

El workflow [GBA diagnostic toolchain](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41513304274) completó la instalación de mGBA, validación CLI/sintaxis y todas las suites, incluidas las pruebas del nuevo corrector y la validación del perfil v1.8. El job estaba finalizando limpieza al consultar el estado; todos los pasos de prueba aparecían como `success`.

## Estado

<badge> Candidata estática — runtime pendiente </badge>

No se ejecutó una sesión del juego con la ROM privada. Que GitHub Actions instale mGBA no significa que haya probado esta ROM: los binarios privados no se envían al runner. Antes de aprobar v1.8 hay que ejecutar la ROM en mGBA/VBA-M y comprobar título, START, llegada al hangar, carga de L01_R001, colores, transparencia, sprites, colisiones y puerta de salida.

Esta corrección solo afecta a la tabla gráfica de L01_R001. **No integra las otras 381 salas.**
