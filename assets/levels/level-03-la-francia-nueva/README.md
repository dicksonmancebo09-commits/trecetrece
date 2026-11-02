# L03 — La Francia Nueva

**Salas asignadas:** 61  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

La respiración del mapa: calles más amplias, aceras continuas, casas de varias plantas, vehículos estacionados, entradas de garaje, patios y pequeños espacios verdes. Debe sentirse más abierta que El Caliche sin parecer una avenida genérica.

**Paleta de trabajo:** menta / turquesa / azul cielo / crema / amarillo solar / asfalto azul grisáceo.  
**Iluminación:** Día claro, aire abierto y sombras de árboles o aleros.

## Presupuesto de salas

Calles residenciales 14 · cruces/carriles 10 · interiores multinivel 8 · patios/garajes 7 · parques/plazoletas 6 · servicios de calle 5 · rutas elevadas 4 · rescate/briefing 3 · historia/élite 3 · secreto 1.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Fachadas residenciales anchas
- casas de dos y tres niveles
- portones de garaje
- verja frontal
- acera y bordillo
- cruce/calle lateral
- coches estacionados
- árbol puntual
- marquesina doméstica
- patio
- parada y señalética ficticia.

## Capas de composición

00 cielo y copas puntuales · 01 horizonte residencial · 02 fachadas variadas · 03 vehículos/garajes/patios · 04 acera y calzada · 05 elementos interactivos de cruce.

## Regla de composición y lectura

La vía principal debe leerse de un vistazo; no usar vehículos como obstáculos invisibles. Las casas deben variar en altura y acabado; no clonar el mismo módulo en serie.

## Dependencias y producción

Paquete nuevo. Crear atlas 256x256 indexado de módulos de 8x8 con piezas compuestas 16x16/32x16; separar fachadas anchas, garajes, vehículos y vegetación.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.


## Lote 03 — hoja conceptual de 87 salas

- [Hoja visual SVG — lote 03](./level-03-05-room-sheet-lote-03-v0.1.svg)
- [Registro JSON — lote 03](../../../data/world/sector-cero-room-batch-03-v1.json)
- [Documento de producción — lote 03](../../../docs/villa-duarte-sector-cero/ROOM_BATCH_03_LA_FRANCIA_CALERO_PUEBLO_NUEVO.md)

El lote cubre 28 salas de La Francia Nueva, 39 de Calero y 20 de Pueblo Nuevo. Es una composición visual conceptual; no representa todavía mapas de ROM jugables.

## Atlas modular L03 v0.1

- [Atlas SVG editable](level-03-atlas-v0.1.svg)
- [Metadatos de 64 módulos y paleta](level-03-atlas-v0.1.json)

**Estado comprobado:** biblioteca SVG conceptual de 256 × 256 px, 64 módulos de 32 × 32 px; todavía sin PNG indexado, exportación 4bpp, tilemaps por sala ni integración ROM.
