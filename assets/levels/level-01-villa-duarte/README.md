# L01 — Villa Duarte

**Salas asignadas:** 87  
**Estado:** dirección artística inicial y familias de módulos especificadas; atlas y composición nativa pendientes cuando se indica.

## Identidad visual

El corazón del recorrido. Fachadas de 2–3 alturas, balcones, rejas, colmados, talleres domésticos, motos, sillas, cableado y aceras. El hangar de cuarentena se trata como instalación logística camuflada en el tejido urbano.

**Paleta de trabajo:** #E7A53A / coral gastado / crema / azul petróleo / verde vegetal.  
**Iluminación:** Atardecer cálido, calle viva y escala humana.

## Presupuesto de salas

Hangar/cuarentena 4 · calle principal 12 · fachadas residenciales 14 · colmado/interiores 10 · balcones/azoteas 12 · telecom/energía 9 · servicio 8 · hubs de misión 8 · eventos/emboscada 4 · secretos/atajos 4 · set-pieces de combate 2.

La lista individual y el vínculo sala fuente→sala de diseño están en [LEVEL_ROOM_MASTER_PLAN_V2.md](../../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md) y en el [registro estructurado de 382 salas](../../../data/world/sector-cero-room-registry-v1.json).

## Módulos que se deben producir

- Fachada con balcón
- fachada con galería
- colmado ficticio
- persiana
- reja
- moto aparcada
- poste/cable
- caja de contador
- acera/asfalto
- pasaje trasero
- compuerta de hangar
- contenedores y luz de emergencia.

## Capas de composición

00 cielo y cables · 01 silueta de tejados · 02 fachadas · 03 balcones/rejas/aberturas · 04 comercios y props · 05 suelo/plataformas · 06 interacción y luces de cuarentena.

## Regla de composición y lectura

Evitar repetir el mismo edificio; el colmado no es adorno genérico: debe ser un nodo reconocible. El suelo y las plataformas se separan visualmente; luces de cuarentena solo en el prólogo.

## Dependencias y producción

El paquete existente assets/tiles/scenario-01 es la base visual editable. No duplicarlo ni declararlo integrado en ROM. Añadir un subatlas de hangar/logística y variantes residenciales.

- Resolución base del objetivo GBA: 240 × 160; assets dibujados en escala de pixel nativa y ampliados por nearest-neighbour solo para inspección.
- Tiles de fondo GBA: atlas indexado, paleta BGR555 y recursos comprimidos cuando corresponda. No asumir que el alfa del PNG equivale a transparencia de BG/OBJ.
- Cada sala tendrá plano de fondo, arquitectura, objetos, suelo/plataformas, colisiones y elementos interactivos separados en el inventario.
- No tocar recursos compartidos de la ROM hasta listar todos sus consumidores y sus punteros.
- No tratar este README, el atlas de concepto o el registro de salas como integración jugable.
