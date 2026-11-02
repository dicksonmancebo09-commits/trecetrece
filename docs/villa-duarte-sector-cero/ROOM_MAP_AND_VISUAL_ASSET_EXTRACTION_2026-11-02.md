# Extracción de mapas y recursos visuales — 2 de noviembre de 2026

**Proyecto:** LATINO AMÉRICA Zector Cero  
**ROM base:** Metroid Fusion USA/Australia, SHA-256 \`a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8\`  
**Candidata v1.7:** SHA-256 \`66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf\`  
**Fuente upstream:** \`metroidret/mf@de76565c897c05838503717db9aa2adfe92aeba3\`

## Resultado

Se extrajeron 382/382 salas y **1.214 capas RLE** de clipdata/BG desde la ROM base exacta. El decodificador se contrastó con \`RoomRleDecompress\` y se corrigió el tratamiento del marcador de RLE de 16 bits: el marcador se consume por separado y después se lee el contador big-endian de 16 bits.

| Capa | Mapas |
|---|---:|
| Clipdata | 382 |
| BG1 | 382 |
| BG2 | 381 |
| BG0 | 69 |
| **Total** | **1.214** |

**Controles:** 0 errores RLE; 0 solapamientos entre rangos; todas las matrices decodificadas contienen exactamente ancho × alto celdas. Se extrajeron 340.909 bytes comprimidos. Los dos arrays que contienen bytes después del terminador los conservan en el RLE original y los registran como reserva, no como error.

## Lotes de producción

Se cruzó cada sala con \`sector-cero-production-manifest-v1.json\`: 382 IDs técnicos únicos, 382 production IDs únicos, sin faltantes.

| Lote | Salas |
|---|---:|
| 1 | 87 |
| 2 | 87 |
| 3 | 87 |
| 4 | 87 |
| 5 | 34 |
| **Total** | **382** |

El resumen CSV incluye ID de producción, lote, barrio, nombre/rol editorial, dimensiones, tileset y capas presentes.

## Recursos visuales de las salas

Se identificaron **94 entradas de tileset usadas** por las 382 salas y se extrajeron 296 recursos binarios únicos: gráficos, paletas, tilemaps, fondos comunes y recursos de animación.

- Bytes raw extraídos: **1.039.036**.
- Bytes descomprimidos desde recursos LZ77: **1.332.160**.
- Paletas animadas activas: 31 recursos de datos.
- IDs de tileset animado utilizados: 1–13.

## Comparación base → v1.7

Los **1.214 bloques RLE de referencia** se compararon byte a byte en sus offsets originales: **0 bloques cambiados; 0 bytes distintos**. Esto prueba que el almacenamiento original de los mapas no fue sobrescrito. No significa que todos sigan siendo los mapas activos: v1.7 redirige expresamente BG1 y BG2 de Main Deck, sala fuente 0 (`L01_R001`), a mapas personalizados nuevos.

Para la sala inicial, los punteros verificados de v1.7 son `0x3C0014 → 0x087B0000` (tabla de metatiles), `0x3C2C58 → 0x087B2000` (BG1) y `0x3C2C5C → 0x087B2400` (BG2). Los mapas activos tienen 34 × 14 bloques: BG1 contiene únicamente el metatile transparente 383; BG2 usa 305 metatiles distintos, IDs 0–304. La tabla custom contiene 384 registros y los subtiles usan los índices gráficos 192–560. El metatile transparente 383 apunta al tile 560, cuyos 32 bytes son cero.

**Hallazgo posterior sobre la paleta:** aunque v1.7 carga la paleta de tileset en los bancos BG 2–15, el motor copia después las tres filas de paleta común a los bancos 0–2. El banco 2 queda sobrescrito. La tabla custom de v1.7 asigna banco 2 a los 1.536 subtiles; por tanto, su paleta personalizada no es la que queda visible según el orden de carga del código. La tabla original `tilesets/61.tm` utiliza bancos 0, 1, 3 y 4, nunca el 2. Esto no se detectó en la auditoría de 75 controles porque entonces no se comprobó la compatibilidad entre el banco de la tabla y el orden de carga de paletas.

Se creó una candidata v1.8 separada que cambia exclusivamente el campo de banco de paleta de esos 1.536 subtiles, de 2 a 3. El tileset palette file tiene 14 filas idénticas; el banco 3 accede a la fila 1 de la paleta custom, que sobrevive a la escritura final de las filas comunes 0–2. El SHA-256 de la candidata es `3bc764355012268d4ac6ef315bb9bb09ac0e5405d1c456bb506d1fdbe862af89`. La v1.7 original permanece intacta.

La reconstrucción estática corregida mantiene 544 × 224 píxeles nativos y 0 referencias de tiles inválidas. No es una captura de mGBA ni dibuja sprites, estado de cámara, animaciones o efectos. La corrección de banco sigue pendiente de prueba real en emulador.

Entre los 296 recursos visuales referenciados, dos sí cambian:

| Recurso | Offset | Bytes distintos |
|---|---:|---:|
| \`tilesets/61.gfx.lz\` | \`0x416E8C\` | 5.431 |
| \`tilesets/76.pal\` | \`0x46B494\` | 423 |
| **Total** | | **5.854** |

Ambos corresponden a la entrada de tileset 96 usada por Main Deck sala fuente 0, vinculada a \`L01_R001\`. Esa entrada señala \`sTileset_61_Gfx\` y \`sTileset_76_Pal\`, coherente con el reskin gráfico urbano de la sala inicial.

## Entregables locales

- \`ZECTOR_CERO_382_ROOM_EXTRACTION_2026-11-02.zip\`: 3.646 archivos con RLE, matrices U16LE, CSV y tablas globales. SHA-256: \`f7abff74e2c8be62092e27fbc20c3710a9c881603256b242a2c22f320b19592b\`.
- \`ZECTOR_CERO_ROOM_VISUAL_ASSETS_2026-11-02.zip\`: 416 archivos raw/LZ77 decodificados e índices. SHA-256: \`74e7e7e5f8d2bf191ed47c19d5be20cc4a48584aa54aef0ce87bd063e668cc0e\`.
- \`ZECTOR_CERO_382_ROOM_SOURCE_PACKAGE_2026-11-02.zip\`: paquete consolidado con los dos entregables y bundle de referencia. SHA-256: \`d514a95a2a5c03984f98a4fa13261c6462d22416593e7528275b8beda100231c\`.

Los binarios derivados permanecen fuera de Git. No se subieron ROM, saves ni dumps extraídos.

## Render de comparación del banco de paleta

- Comparación lado a lado: `L01_R001_palette_bank_comparison.png`.
- v1.7 con el banco 2 realmente visible tras el orden de carga: `L01_R001_v1.7_engine_palette.png`.
- v1.8 candidata con banco 3 y paleta custom: `L01_R001_v1.8_engine_palette.png`.
- Metadatos: `palette-bank-render-comparison.json`.

Estos son renders estáticos de BG2 de 544 × 224 px nativos. La comparación incorpora el orden de carga de paletas de `src/room.c`; no es una captura del emulador ni prueba de ejecución. La ROM candidata v1.8 y la comparación están en el paquete local `ZECTOR_CERO_v1_8_PALETTE_BANK_FIX_PACKAGE_2026-11-02.zip`.

Informe de la corrección: [v1.8 — conflicto del banco de paleta](V1_8_ROOM0_PALETTE_BANK_FIX_2026-11-02.md).

## Herramientas reproducibles

- [Builder del bundle de referencia](../../tools/build_room_reference_bundle.py).
- [Extractor RLE de las 382 salas](../../tools/extract_sector_cero_room_maps.py).
- [Extractor de tilesets, paletas y animaciones](../../tools/extract_sector_cero_room_visual_assets.py).
- [Renderizador estático de L01_R001 desde v1.7](../../tools/render_v17_room0.py).
- [Corrector guarded v1.7 → v1.8 del banco de paleta](../../tools/fix_v17_room0_palette_bank.py).
- [Renderizador estático de L01_R001 v1.8](../../tools/render_v18_room0.py).
- [Decodificador/auditor GBA](../../tools/gba_rom_audit.py).

## Automatización / CI

- Bundle completo de fuentes y tablas: [run 41508555361](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41508555361) — \`success\`.
- Diagnóstico GBA y pruebas del decodificador RLE: [run 41508099676](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41508099676) — \`success\`.
- Builder reproducible del bundle: \`tools/build_room_reference_bundle.py\`.
- Workflow: \`.github/workflows/sector-cero-room-reference-bundle.yml\`.
- Decodificador corregido: \`tools/gba_rom_audit.py\`; prueba 16-bit: \`tests/test_gba_rom_audit.py\`.

## Límite de alcance

Este hito recupera los mapas base comprimidos, las matrices de colisión/tiles y los recursos visuales que las salas referencian. También genera un render estático de `L01_R001` usando los mapas que realmente apunta v1.7. **No significa que las otras 381 salas estén convertidas al arte urbano, recompuestas como tilemaps nuevos o integradas como salas personalizadas.** La prueba runtime en mGBA/VBA-M sigue pendiente. El siguiente gate es ejecutar v1.7 en un entorno con acceso a la ROM, verificar título/START/hangar y validar esta sala en movimiento; después, iniciar la conversión de las demás salas por capas y lotes.
