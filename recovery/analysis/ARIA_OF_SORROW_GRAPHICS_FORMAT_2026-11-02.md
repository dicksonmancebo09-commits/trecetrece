# Formato gráfico y compresión — Castlevania: Aria of Sorrow (GBA)

**Fecha:** 2 de noviembre de 2026  
**ROM analizada:** Castlevania - Aria of Sorrow (Europe) (En,Fr,De)  
**Código de cabecera:** A2CP  
**Tamaño:** 8.388.608 bytes (8 MiB)  
**SHA-256:** `5e53bad137852c55280964c08f8f4a6622ddf332fa0108722a26d462e1f8a92a`

## Dictamen

El formato comprimido que se puede demostrar en el motor de Aria of Sorrow es **Nintendo BIOS LZ77/LZ10 (`0x10`)**, descomprimido mediante la rutina BIOS `LZ77UnCompWram` (SWI `0x11`). La decompilación pública muestra descriptores de recursos con dimensiones/campos de modo y un puntero a los datos; según el tipo del descriptor, el motor copia datos sin compresión o llama a LZ77. Esto confirma que LZ77 forma parte de la canalización real de recursos, no que cualquier secuencia `0x10` encontrada dentro de la ROM sea un tileset.

El barrido europeo guardado en los artefactos de esta conversación encontró **481 candidatos LZ77 heurísticos**, no 13 bloques verificados. La lista es una búsqueda de cabeceras que se dejan descomprimir con tamaños plausibles; todavía no demuestra referencias desde tablas, consumidores ni función visual. Por tanto, 481 no debe convertirse en 481 tilesets. La cifra de 13 puede venir de un filtro o agrupación diferente que no está documentado en el JSON disponible.

## Evidencia del escaneo europeo

| Dato | Resultado |
|---|---:|
| ROM | Europe (En,Fr,De), `CASTLEVANIA2`, código `A2CP` |
| Tamaño | 8 MiB |
| SHA-256 | `5e53bad137852c55280964c08f8f4a6622ddf332fa0108722a26d462e1f8a92a` |
| Candidatos LZ77 | 481 |
| Candidatos alineados | 4 bytes |
| Tamaño mínimo de salida del filtro | 32 bytes |
| Tamaño máximo de salida del filtro | 262.144 bytes |
| Candidatos con `(salida - 4) % 32 == 0` | 448 / 481 |

Las salidas más frecuentes del barrido incluyen 8.196 bytes (185 candidatos), 2.052 (108), 4.100 (49), 4.068 (17), 4.084 (17), 8.132 (16), 8.164 (14) y 16.388 (11). Al quitar los primeros cuatro bytes decodificados —como hace el generador de previsualizaciones— muchos tamaños quedan alineados a múltiplos de 32 bytes. **Esto es una pista compatible con datos de tiles 4bpp**, ya que un tile GBA de 8×8 a 4bpp ocupa 32 bytes; no identifica por sí sola ni la profundidad de color ni la función de un bloque.

Los cuatro candidatos con previsualizaciones guardadas son:

| Offset ROM | Salida declarada | Bytes tras quitar 4 | Observación |
|---:|---:|---:|---|
| `0x501708` | 16.388 | 16.384 | 4bpp provisional, vista 384×768 |
| `0x590894` | 8.196 | 8.192 | 4bpp provisional, vista 384×384 |
| `0x5D09D0` | 8.164 | 8.160 | 4bpp provisional, vista 384×384 |
| `0x5DACC8` | 8.132 | 8.128 | 4bpp provisional, vista 384×384 |

Las imágenes de contacto se generaron asignando tonos grises a índices de nibble 0–15. **No se recuperó la paleta original**, ni se ha demostrado que cada previsualización sea un tileset. Los cuatro bytes retirados tampoco están demostrados como una cabecera interna universal: se conservan como hipótesis de trabajo hasta contrastarlos con los descriptores reales.

## Evidencia del motor en la decompilación pública

El proyecto [testyourmine/cvaos](https://github.com/testyourmine/cvaos) se identifica en su README como una decompilación WIP de la versión **USA** de Aria of Sorrow. La ROM que compila allí declara SHA-1 `abd71fe01ebb201bcc133074db1dd8c5253776c7`; no coincide con la ROM europea A2CP de este análisis.

Rutas de código comprobadas:

- [`include/syscalls.h`](https://github.com/testyourmine/cvaos/blob/main/include/syscalls.h): declara `LZ77UnCompWram(const u32 *src, void *dest)`.
- [`asm/libagbsyscall.s`](https://github.com/testyourmine/cvaos/blob/main/asm/libagbsyscall.s): implementa `LZ77UnCompWram` con `swi #0x11`.
- [`src/code/code_08039340.c`, función `sub_08039748`](https://github.com/testyourmine/cvaos/blob/main/src/code/code_08039340.c): recorre descriptores de recursos; en el caso comprimido llama a `LZ77UnCompWram`, y en el otro caso copia los datos con DMA.
- [`include/structs/ewram.h`](https://github.com/testyourmine/cvaos/blob/main/include/structs/ewram.h): define `EwramData_unk19404_4`, un descriptor de ocho bytes con cuatro campos `u8` y un puntero a datos.

El descriptor tiene campos sin nombres semánticos resueltos. Otro tramo del código selecciona modos con valores 4, 8 y 16, pero el estado actual de la decompilación no permite afirmar con rigor que todos esos campos sean siempre bpp ni asignar cada modo a un tipo concreto de recurso. La conclusión segura es: **hay un loader de recursos con descriptores y dos rutas demostradas, copia directa y LZ77 BIOS**.

El formato BIOS LZ77 `0x10` tiene una cabecera de 32 bits: byte mágico `0x10` y longitud descomprimida en los 24 bits superiores; a continuación siguen grupos de flags y bloques literales o referencias de retroceso. La documentación técnica de BIOS describe además el uso de `LZ77UnCompWram` para destino en WRAM.

## Herramienta de edición disponible y bloqueo por región

[DSVEdit](https://github.com/LagoLunatic/DSVEdit) anuncia edición de salas, tiles, GFX, paletas, sprites y tilesets para Aria of Sorrow de GBA. Su README especifica que **para los juegos GBA sólo admite las versiones USA**. La ROM que estamos investigando es europea; no se debe abrir, exportar ni reimportar como si DSVEdit garantizara compatibilidad. Puede servir como referencia del modelo de datos y como ruta de trabajo si se adapta el soporte regional, pero no como solución validada para A2CP.

El repo `testyourmine/cvaos` también se construye contra la versión USA, así que sus offsets, tablas de punteros y símbolos no se deben aplicar directamente a la ROM europea. Sí podemos usar su loader para comprender el motor y después identificar la estructura equivalente en A2CP con un análisis separado.

## Qué falta para extraer tilesets reales

1. **Agrupar candidatos por referencias y consumidores.** Buscar punteros alineados que apunten al inicio de cada stream, y cruzarlos con tablas de descriptores, no sólo con firmas `0x10`.
2. **Identificar el descriptor de cada recurso.** Resolver campos de modo, dimensiones, longitud y destino; confirmar si el bloque incluye un pequeño encabezado de dimensiones antes del bitmap.
3. **Distinguir gráficos, tilemaps, mapas de colisión y otras estructuras.** Una salida múltiplo de 32 bytes puede ser 4bpp, pero también datos binarios no gráficos.
4. **Recuperar paletas reales.** Localizar datos BGR555 y referencias del loader; la previsualización gris no es una paleta recuperada.
5. **Recrear la composición del mapa.** Los tiles sueltos sin tilemap, atributos de tile, prioridades/capas y paleta no reconstruyen una sala.
6. **Validar en la ROM europea.** Comparar la pantalla extraída con A2CP en emulador; no transportar offsets del build USA.

## Decisión para Sector Cero

Aria of Sorrow puede ser una referencia de técnicas de compresión, descriptores y organización de recursos, pero **no se ha resuelto aún su mapa completo de tilesets ni se han extraído recursos listos para importar**. La base operativa inmediata sigue siendo Metroid Fusion, donde ya tenemos el cruce de 382 salas con sus entradas de tileset y recursos. No conviene mezclar offsets de una ROM USA con la europea ni mezclar formatos entre los dos juegos sin un adaptador explícito.

## Fuentes

- [Decompilación C de Aria of Sorrow (USA)](https://github.com/testyourmine/cvaos)
- [DSVEdit: editor de Aria of Sorrow GBA](https://github.com/LagoLunatic/DSVEdit)
- [BIOS GBA: LZ77UnCompWram y formato LZ10](https://docs.rs/gba/latest/src/gba/bios.rs.html)
- Artefacto del escaneo que sustenta las cifras: `castlevania-lz77-scan.json`, incluido en el ZIP de previsualizaciones generado durante esta conversación; no es un archivo versionado en este repositorio.

