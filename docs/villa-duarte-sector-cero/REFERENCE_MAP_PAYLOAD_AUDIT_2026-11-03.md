# Auditoría de disponibilidad de mapas y clipdata — 3 de noviembre de 2026

**Proyecto:** LATINO AMÉRICA Zector Cero
**Alcance:** comprobar si la descompilación pública contiene los payloads comprimidos necesarios para reconstruir las salas.
**Estado:** bloqueo de datos binarios identificado; no se fabrican tilemaps ni colisiones.

## Evidencia comprobada

Se inspeccionó el fichero de referencia:

`src/data/rooms/main_deck/main_deck_81.c`

El fichero declara:
- `sMainDeck_81_Clipdata[76]`, dimensiones 19 × 14 bloques y contenido mediante `_INCBIN_U8("data/rooms/main_deck/main_deck_81_clipdata.rle")`.
- `sMainDeck_81_Bg2[164]`, contenido mediante `_INCBIN_U8("data/rooms/main_deck/main_deck_81_bg2.rle")`.
- `sMainDeck_81_Bg1[151]`, contenido mediante `_INCBIN_U8("data/rooms/main_deck/main_deck_81_bg1.rle")`.
- `sMainDeck_81_Bg0[14]`, contenido mediante `_INCBIN_U8("data/rooms/main_deck/main_deck_81_bg0.rle")`.
- `sMainDeck_81_Spriteset0`, con registros estáticos de posición y expresión de spriteset.

Se solicitaron los cuatro ficheros `.rle` de la ruta `data/rooms/main_deck/` del repositorio público `metroidret/mf`; los cuatro caminos devuelven 404 Not Found. La declaración C existe, pero los payloads binarios no están versionados en ese repositorio público.

## Qué permiten afirmar las fichas

- Dimensiones de referencia: **382/382** salas.
- Concordancia de dimensiones entre capas declaradas: **382/382**, sin conflictos.
- Posiciones de sprites de referencia: **2.150** registros en **469** variantes; 332 salas contienen filas de colocación estática y 50 no declaran filas estáticas.
- Las tablas RoomEntry y tileset permiten asociar coordenadas, recursos y símbolos de payload a los IDs de sala.

## Qué no puede reconstruirse con las fuentes disponibles

- El contenido de los mapas BG0–BG3 comprimidos.
- El tilemap o la distribución real de metatiles de cada sala.
- El contenido de clipdata y sus valores de colisión.
- Los estados de puertas y los cambios de destino por evento adaptados al nuevo trazado.
- La identidad binaria entre el código de referencia y la ROM privada concreta.

La longitud declarada de un array y las dimensiones de sala no contienen el mapa. Rellenarlo por intuición produciría un falso resultado de extracción.

## Requisitos para terminar el trabajo

1. Tener la ROM exacta del usuario en un espacio privado y comprobar tamaño, cabecera y SHA-256 mediante `tools/gba_rom_audit.py`. La ROM no debe subirse al repositorio público.
2. Extraer de esa ROM los payloads comprimidos BG y clipdata de cada sala, verificando offsets, tamaños, compresión y límites de recursos.
3. Decodificar BG maps y clipdata con dimensiones concordantes; conservar la capa de colisión separada del arte.
4. Mapear los metatiles fuente hacia los nuevos atlas L01–L07 y componer primero una sala vertical de prueba.
5. Aplicar el cambio sobre una copia privada con precondiciones hash-pinned y rangos sin solapamiento.
6. Probar en mGBA entradas/salidas, movimiento, colisiones, animaciones, paleta, transparencias, eventos y guardado antes de extender a otras salas.

## Estado de integración

`room_tilemap_created`: **0/382**.
`collision_content_extracted_from_private_rom`: **0/382**.
`rom_integration`: **0/382**.
`runtime_tested`: **0/382**.

Esto no invalida la producción ya superada: 382 IDs y lotes auditados, metadatos RoomEntry conciliados, dimensiones de referencia extraídas y siete atlas exportados a PNG indexado/4bpp/BGR555/LZ77. Delimita el punto donde hacen falta los bytes que no están en la fuente pública ni disponibles en este entorno.


## Actualización — payloads recuperados desde la ROM del usuario (03-11-2026)

La auditoría original de 404 describe correctamente que los payloads `.rle` no están en el árbol público de `metroidret/mf`. No debe interpretarse como que ya no se dispone de ellos para el proyecto: se recuperó la ROM base exacta desde la Biblioteca de archivos y se extrajeron directamente sus rangos.

- ROM base: `Metroid Fusion (USA, Australia).gba`, SHA-256 `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.
- Paquete fuente 382-salas: artifact de GitHub Actions run `41508555361`; hash de base de datos y hashes de 382 archivos C verificados.
- Extracción completada: **382 salas / 1.214 capas RLE**: clipdata 382, BG1 382, BG2 381, BG0 69.
- 340.909 bytes comprimidos; 0 errores RLE; 0 rangos solapados; 0 capas con diferencias en sus offsets originales al comparar v1.7.
- ZIP privado de extracción: `ZECTOR_CERO_382_ROOM_EXTRACTION_2026-11-03.zip`, SHA-256 `5663ef29ab795cc28737cab515c88b2dbe7ea785a1d49dc35354762cef13eb1f`. No se versiona en el repositorio público.

Los indicadores deben interpretarse así:

- `original_rle_layers_extracted`: **1214/1214**.
- `original_clipdata_payloads_extracted_from_clean_rom`: **382/382**.
- `custom_neighborhood_tilemaps_created`: **0/382**.
- `adapted_neighborhood_collision_layouts_created`: **0/382**.
- `rom_integration`: **0/382**.
- `runtime_tested`: **0/382**.

Por tanto, ya no hace falta recuperar ni extraer los mapas originales. La fase pendiente es reinterpretarlos y montarlos con el arte de los siete barrios, adaptar las colisiones/puertas y llevar el resultado a la ROM.
