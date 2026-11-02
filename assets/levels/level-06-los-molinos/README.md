# L06 — Los Molinos

**Salas asignadas:** 52  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

Encuentro entre río, puentes, fábricas, canales, bombas y estructuras abandonadas. Integra frío/almacenamiento y servicios industriales como subzonas dentro del mismo nivel.

**Paleta de trabajo:** cian oscuro / pizarra / verde industrial / óxido / ámbar de señalización.  
**Iluminación:** Azul grisáceo, humedad selectiva, focos cálidos y contrastes de escala industrial.

## Presupuesto de salas

Accesos al río 8 · puentes 7 · fábricas 8 · bloques industriales abandonados 7 · canales/bombas 6 · cámaras frías/servicio 5 · cintas/vías 4 · turbinas/generadores 3 · control/navegación 2 · jefes/minijefes 2.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Muro de canal
- agua en 2–3 tonos
- borde de muelle
- pilares y tablero de puente
- tubería
- bomba
- compuerta
- turbina
- cinta transportadora
- grúa/polipasto
- contenedor
- cámara fría
- rejilla con escarcha
- cuarto de control.

## Capas de composición

00 horizonte fluvial y puentes · 01 fábrica distante · 02 estructuras industriales · 03 pasarelas/canales · 04 bombas/tuberías/máquinas · 05 agua y reflejos · 06 cámara fría y servicio.

## Regla de composición y lectura

El agua debe distinguirse de un suelo transitable. Puentes y cintas requieren colisiones coherentes. No mezclar el motivo frío con el conjunto completo: es una zona funcional concreta.

## Dependencias y producción

Paquete nuevo. Preparar un subatlas industrial dividido en agua/puentes, maquinaria y cámara fría; animar agua y maquinaria solo tras confirmar recursos y sincronización.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.

## Atlas modular L06 v0.1

- [Atlas SVG editable](level-06-atlas-v0.1.svg)
- [Metadatos de 64 módulos y paleta](level-06-atlas-v0.1.json)

**Estado comprobado:** biblioteca SVG conceptual de 256 × 256 px, 64 módulos de 32 × 32 px; todavía sin PNG indexado, exportación 4bpp, tilemaps por sala ni integración ROM.
