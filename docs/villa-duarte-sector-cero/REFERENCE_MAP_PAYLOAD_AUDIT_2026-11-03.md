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
