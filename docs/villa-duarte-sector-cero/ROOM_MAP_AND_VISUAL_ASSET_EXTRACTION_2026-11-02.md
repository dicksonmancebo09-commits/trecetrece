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

Las **1.214 capas RLE** se compararon byte a byte a los mismos offsets: **0 capas cambiadas; 0 bytes distintos**. v1.7 conserva los mapas BG/clipdata originales de las 382 salas.

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

## Herramientas reproducibles

- [Builder del bundle de referencia](../../tools/build_room_reference_bundle.py).
- [Extractor RLE de las 382 salas](../../tools/extract_sector_cero_room_maps.py).
- [Extractor de tilesets, paletas y animaciones](../../tools/extract_sector_cero_room_visual_assets.py).
- [Decodificador/auditor GBA](../../tools/gba_rom_audit.py).

## Automatización / CI

- Bundle completo de fuentes y tablas: [run 41508555361](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41508555361) — \`success\`.
- Diagnóstico GBA y pruebas del decodificador RLE: [run 41508099676](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41508099676) — \`success\`.
- Builder reproducible del bundle: \`tools/build_room_reference_bundle.py\`.
- Workflow: \`.github/workflows/sector-cero-room-reference-bundle.yml\`.
- Decodificador corregido: \`tools/gba_rom_audit.py\`; prueba 16-bit: \`tests/test_gba_rom_audit.py\`.

## Límite de alcance

Este hito recupera los mapas base comprimidos, las matrices de colisión/tiles y los recursos visuales que las salas referencian. **No significa que las 382 salas estén convertidas al arte urbano, recompuestas como tilemaps nuevos, integradas como salas personalizadas o probadas en ejecución.** La prueba runtime en mGBA/VBA-M sigue pendiente. El siguiente hito es renderizar una sala completa desde estos recursos como control de fidelidad, adaptar sus capas al atlas de barrio e integrar una sala vertical completa antes de escalar a los cinco lotes.
