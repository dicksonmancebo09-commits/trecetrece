# L05 — Pueblo Nuevo

**Salas asignadas:** 48  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

Topografía vertical: casas escalonadas, escaleras, recodos, terrazas, miradores, patios y depósitos de agua. El propio desnivel organiza la exploración y ofrece vistas hacia la ciudad.

**Paleta de trabajo:** violeta / índigo / melocotón / hormigón cálido / acentos turquesa.  
**Iluminación:** Hora azul y atardecer, luces domésticas en ventanas.

## Presupuesto de salas

Calles en ladera 10 · escaleras/recodos 8 · azoteas/terrazas 8 · miradores 5 · patios/interiores 4 · tanques/depósitos 4 · cisternas/servicio 3 · retos de movimiento 2 · rescate/checkpoint 2 · arena 1 · secreto 1.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Escalera de tramo corto/largo
- descanso
- rampa
- pretil
- terraza
- balcón superior
- tanque de agua
- cisterna
- antena
- tendedero
- mirador
- pasarela
- muro de contención
- portón de patio.

## Capas de composición

00 horizonte y vista panorámica · 01 ladera y casas escalonadas · 02 escaleras/rampas · 03 patios/terrazas/azoteas · 04 depósitos y antenas · 05 plataformas y barandas.

## Regla de composición y lectura

Distinguir altura visual de altura colisionable. Las caídas importantes deben tener ruta de retorno o recuperación. Las vistas panorámicas no deben reducir el contraste de plataformas.

## Dependencias y producción

Paquete nuevo. Construir primero kits de desnivel, escaleras, pretiles y casas por módulos; luego componer vistas panorámicas de fondo sin añadir geometría jugable falsa.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.

## Atlas modular L05 v0.1

- [Atlas SVG editable](level-05-atlas-v0.1.svg)
- [Metadatos de 64 módulos y paleta](level-05-atlas-v0.1.json)

**Estado comprobado:** biblioteca SVG conceptual de 256 × 256 px, 64 módulos de 32 × 32 px; todavía sin PNG indexado, exportación 4bpp, tilemaps por sala ni integración ROM.
