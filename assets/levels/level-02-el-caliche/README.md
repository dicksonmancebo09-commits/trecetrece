# L02 — El Caliche

**Salas asignadas:** 54  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

Nivel de compresión espacial: callejones estrechos, muros próximos, ventanas enrejadas, puertas protegidas, escalones, bajantes, drenajes y pasajes laterales. La tensión viene de la geometría y las líneas de visión, no de llenar el fondo de basura.

**Paleta de trabajo:** ladrillo apagado / salmón erosionado / cemento / verde pálido / azul sombra.  
**Iluminación:** Luz cortada; entrada cálida y fondo frío, con alto contraste de silueta.

## Presupuesto de salas

Red de callejones 11 · interiores de viviendas 9 · drenajes/canales 7 · rejas/seguridad 8 · cuartos de servicio 6 · persecución/emboscada 5 · refugios 3 · pasajes secretos 3 · élites/combate 2.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Paredes de bloque
- esquinas de callejón
- reja de ventana
- portón
- puerta metálica
- bajante
- medidor
- escalón
- cuneta
- tapa de registro
- bolsa/cubo discreto
- pasaje lateral
- puerta de servicio.

## Capas de composición

00 tejados y cielo en tiras · 01 fachadas izquierda/derecha · 02 huecos y rejas · 03 tuberías/cableado · 04 suelo irregular y drenaje · 05 props de escala peatonal · 06 zonas de sombra.

## Regla de composición y lectura

Mantener un corredor jugable legible y un contraste estable detrás del personaje. No convertir las rejas en plataformas falsas. Evitar callejón idéntico repetido en todas las 54 salas.

## Dependencias y producción

El atlas existente assets/tiles/scenario-02 es la base inicial. Completar interiores, drenajes y variantes de esquina; mantener su PNG indexado y paleta como borrador hasta revisar a escala nativa.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.
