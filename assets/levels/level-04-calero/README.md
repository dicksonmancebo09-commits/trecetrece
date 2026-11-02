# L04 — Calero

**Salas asignadas:** 39  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

Zona de trabajo y transformación: talleres, construcciones, maquinaria, persianas metálicas, neumáticos, piezas, generadores y corredores térmicos. La identidad debe ser de talleres y obras del barrio, no de una fábrica futurista genérica.

**Paleta de trabajo:** azul acero / óxido / ocre / cemento oscuro / señales de seguridad.  
**Iluminación:** Exterior neutro, interior cálido y reflejos puntuales en metal.

## Presupuesto de salas

Talleres 8 · obras 7 · plataformas mecánicas 6 · generadores/energía 5 · corredores térmicos 4 · interiores de taller 3 · élites 3 · control/seguridad 2 · secreto 1.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Portón enrollable
- banco de trabajo
- neumáticos
- estanterías
- compresor
- elevador
- andamio
- bloques y columnas
- vigas
- generador
- cuadro eléctrico
- tubería caliente
- válvula
- rejilla de ventilación
- señales de seguridad.

## Capas de composición

00 perfiles de tejado/andamio · 01 paredes de bloque/hormigón · 02 persianas y herramientas · 03 maquinaria/plataformas · 04 conducciones/energía · 05 suelo industrial y zonas de peligro.

## Regla de composición y lectura

Las máquinas peligrosas deben tener ciclos y zonas de impacto legibles. Los restos de construcción no deben confundirse con plataformas sólidas. El color de advertencia se reserva para interacción/peligro.

## Dependencias y producción

Paquete nuevo. Crear un tileset modular con elementos robustos repetibles y un set pequeño de animaciones ambientales (ventilador, luz de generador, pistón); no alterar hitboxes hasta auditar sala.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.

## Atlas modular L04 v0.1

- [Atlas SVG editable](level-04-atlas-v0.1.svg)
- [Metadatos de 64 módulos y paleta](level-04-atlas-v0.1.json)

**Estado comprobado:** biblioteca SVG conceptual de 256 × 256 px, 64 módulos de 32 × 32 px; todavía sin PNG indexado, exportación 4bpp, tilemaps por sala ni integración ROM.
