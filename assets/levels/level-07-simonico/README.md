# L07 — Simónico

**Salas asignadas:** 41  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

Cierre urbano nocturno: arte urbano original, música, patios culturales, canchas, comercios cerrando, refugios de resistencia, callejones traseros, pasos inferiores y el laboratorio/núcleo escondido bajo el tejido urbano.

**Paleta de trabajo:** azul marino / morado / magenta / cian / ámbar cálido.  
**Iluminación:** Noche azul con ventanas cálidas y acentos magenta/cian controlados.

## Presupuesto de salas

Calles nocturnas 7 · corredores de arte urbano 6 · patios culturales/música 5 · refugios de resistencia 5 · azoteas/callejones traseros 4 · pasos inferiores/catacumbas 5 · laboratorio/núcleo 3 · antesala final 1 · arena final 1 · desenlace/escape 2 · secreto 2.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Persianas comerciales
- mural original
- cancha y aro
- patio cultural
- equipo de sonido
- refugio
- callejón trasero
- farola
- charco
- paso inferior
- verja
- puerta de laboratorio
- panel tecnológico
- núcleo final.

## Capas de composición

00 cielo nocturno y cableado · 01 fachadas y comercios · 02 murales/patios/cancha · 03 calle y azoteas · 04 paso inferior/catacumbas · 05 laboratorio y núcleo · 06 luces de objetivo.

## Regla de composición y lectura

El magenta no sustituye el contraste de gameplay. Los murales son inventados, no reproducciones de grafitis identificables. El laboratorio se revela como instalación clandestina integrada debajo de la ciudad.

## Dependencias y producción

Paquete nuevo. Crear por separado el kit de calle nocturna, cultura/resistencia y laboratorio oculto; mantener misma escala de pixel art que los otros seis niveles.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.
