# Arquitectura del título de Metroid Fusion — logo en tres recursos

**Fecha:** 2 de noviembre de 2026  
**Referencia:** `metroidret/mf`, rama `main`, archivos `src/data/menus/title_screen.c`, `include/data/menus/title_screen.h` y `src/menus/title_screen.c`.

## Hallazgo

El logo de la pantalla de título no es un único bitmap ni un texto normal que baste con reemplazar en una tabla de cadenas. La referencia decompilada lo define como tres recursos independientes:

| Pieza | Símbolo | Fuente | Tamaño declarado | Papel |
|---|---|---|---:|---|
| Gráficos de tiles | `sTitleScreenLogoGfx` | `logo.gfx.lz` | 3.153 palabras = 12.612 bytes comprimidos | Píxeles de los tiles del logo |
| Tabla de tiles / mapa | `sTitleScreenLogoTileTable` | `logo.tt` | 597 palabras = 2.388 bytes comprimidos | Organización/colocación de tiles en la capa BG |
| Paleta | `sTitleScreenLogoPal` | `logo.pal` | 16 × 8 colores de 16 bits = 256 bytes | Colores indexados del logo |

El código de `TitleScreenInit()` carga los tres de forma separada:

- Descomprime `sTitleScreenLogoGfx` en `VRAM_BASE + BGCNT_VRAM_CHAR_SIZE * 2` (char base 2).
- Descomprime `sTitleScreenLogoTileTable` en `VRAM_BASE + BGCNT_VRAM_TILE_SIZE * 30` (screen block 30 del fondo).
- Copia `sTitleScreenLogoPal` a `PALRAM_BASE`.

El fondo principal usa BG1 con char base 2 y screen block 30; la capa inferior BG3 usa char base 0 y screen block 31. En consecuencia, sustituir sólo los píxeles y no el tilemap deja la composición anterior apuntando a tiles equivocados; cambiar sólo el mapa puede mostrar índices vacíos o datos incorrectos; cambiar sólo la paleta conserva la forma pero altera el color.

## Qué implica para “LATINO AMERICA SECTOR ZERO”

El reemplazo debe producir y validar al menos estos tres archivos binarios:

1. **`logo.gfx.lz` nuevo:** tiles 4bpp/8bpp según confirme el recurso real, con los glifos y ornamentos del nuevo título.
2. **`logo.tt` nuevo:** mapa de tiles consistente con el orden y los índices de los gráficos nuevos, dimensiones y posición dentro del fondo.
3. **`logo.pal` nuevo:** paletas indexadas compatibles con cada tile y los efectos de color usados por la pantalla.

También hay que comprobar la capacidad de VRAM y que el tamaño comprimido/descomprimido quepa en los rangos que usa el arranque. Si el logo ocupa más celdas que el original, no basta con escribir por encima: hay que ajustar tilemap, ubicación y límites de recursos.

Las palabras exactas son largas para un único rótulo GBA. Una composición viable es dos líneas —`LATINO AMERICA` y `SECTOR ZERO`—, pero la proporción y tipografía deben probarse a resolución 240×160 antes de codificar el tilemap. No se ha modificado la ROM en este informe.

## Elementos separados que no se deben confundir con el logo

- `sTitleScreenObjectsGfx` y `sTitleScreenObjectsPal` son gráficos/paleta de objetos OBJ, no el paquete BG del logo.
- `sTitleScreenPressStartPal` anima el color de “Press Start” en el objeto OAM; no es la paleta del logo.
- Los datos de copyright y otros objetos OAM se organizan aparte mediante estructuras `FrameData`.

Por eso una modificación completa de la identidad visual de la pantalla puede requerir revisar también copyright, `Press Start`, objetos y capas, pero el paquete central del logo son las tres piezas de la tabla anterior.

## Fuentes de código

- [Datos: `sTitleScreenLogoGfx`, `sTitleScreenLogoTileTable`, `sTitleScreenLogoPal`](https://github.com/metroidret/mf/blob/main/src/data/menus/title_screen.c)
- [Declaraciones y tamaños](https://github.com/metroidret/mf/blob/main/include/data/menus/title_screen.h)
- [Carga en VRAM, tilemap y paleta en `TitleScreenInit()`](https://github.com/metroidret/mf/blob/main/src/menus/title_screen.c)

## Estado

**Investigación de estructura completada; extracción, rediseño, recodificación y prueba mGBA pendientes.** La fuente comunitaria permite identificar con precisión los tres recursos y sus destinos de carga. Para aplicar offsets binarios a la ROM del proyecto hay que comprobar que la versión regional y la identidad de archivo coinciden con la referencia y después localizar los tres bloques en la ROM concreta.
