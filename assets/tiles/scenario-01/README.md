# Escenario 01 — catálogo del atlas de tiles y objetos

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Escenario:** 01 · Entrada al Barrio  
**Versión:** v0.1 · editable, no probado dentro del juego

## Archivos

- [Atlas editable 256 × 256](scenario-01-villa-duarte-tiles.svg)
- [Vista previa de montaje a coordenadas nativas 240 × 160](scenario-01-native-preview.svg)
- [Metadatos JSON de la cuadrícula y paleta](tile-atlas-metadata.json)
- [Estado global / guía de los siete escenarios](../../../../docs/villa-duarte-sector-cero/SEVEN_SCENARIO_VISUAL_IDENTITIES.md)

## Especificación

- Lienzo nativo: **256 × 256 píxeles SVG**.
- Cuadrícula lógica: **8 × 8 px por tile**, 32 columnas × 32 filas.
- Origen de coordenadas: esquina superior izquierda, (0,0).
- Índice de tile: `index = tile_y * 32 + tile_x`.
- Sprites/módulos grandes están alineados a múltiplos de 8 px y pueden cruzar varios tiles.
- El SVG conserva la transparencia fuera de las siluetas y puede editarse directamente.
- La paleta de 16 colores es un **borrador para fijar la identidad**, no una confirmación de compatibilidad con la paleta original de Metroid Fusion. Antes de importar a ROM hay que comprobar paletas compartidas, compresión, tilemaps y dependencias de la sala real.
- Los gráficos están diseñados a una escala pixel-art nominal; todavía deben comprobarse junto a jugador, enemigos, colisiones y plataformas en una escena jugable.

## Paleta de trabajo

| Índice provisional | Nombre | HEX |
|---:|---|---|
| 0 | Transparente | `#00000000` |
| 1 | outline | `#172336` |
| 2 | shadow | `#26394A` |
| 3 | darkConcrete | `#4F5C61` |
| 4 | midConcrete | `#7C817A` |
| 5 | concrete | `#B5AD9A` |
| 6 | cream | `#E2D6BA` |
| 7 | coral | `#C75D4B` |
| 8 | coralLight | `#E18365` |
| 9 | ochre | `#D69A45` |
| 10 | teal | `#448A80` |
| 11 | mint | `#76B7A1` |
| 12 | glass | `#31586D` |
| 13 | sky | `#87B8C3` |
| 14 | foliage | `#3D7750` |
| 15 | highlight | `#F4D18A` |

El índice 0 queda reservado a transparencia en el flujo de trabajo. Los índices y colores deben remapearse si la herramienta de importación o la ROM requieren otra organización.

## Regiones del atlas

Los límites se expresan en píxeles nativos, como `x, y, ancho, alto`.

| Región | Rectángulo | Contenido |
|---|---|---|
| Fachadas pintadas | `0,0,256,32` | Rellenos de coral, ocre, teal y hormigón; variaciones de borde y luz. |
| Enlucido / bloque visto | `0,32,256,32` | Textura de pared, juntas y pintura gastada. |
| Ventanas | `0,64,256,32` | Módulos de 16 × 16 px, variantes con cristal y divisiones. |
| Puertas, persianas y rejas | `0,96,256,24` | Módulos de 16 × 24 px, puertas de colores, metal y rejería. |
| Rótulos ficticios | `0,128,256,16` | Módulos de 32 × 16 px, incluido rótulo pixelado de colmado. |
| Toldos y mostradores | `0,144,256,16` | Módulos de 32 × 16 px con bandas y frentes comerciales. |
| Vegetación / postes pequeños | `0,160,256,24` | Módulos de 16 × 24 px para macetas, arbustos y variaciones de vegetación. |
| Cable aéreo | `0,184,256,8` | Tira de cable segmentada en tiles de 8 × 8 px. |
| Aceras | `0,192,256,16` | Baldosas de cemento con variaciones de juntas. |
| Bordillo | `0,208,256,8` | Borde horizontal con cara superior, frontal y sombra. |
| Cimiento / base de fachada | `0,216,256,8` | Baldosas oscuras para transición entre pared y acera. |
| Asfalto | `0,224,256,16` | Tiles oscuros con textura sutil. |
| Objetos de calle | `0,240,256,16` | Moto pequeña, cajas, barril, cubo, rejilla, neumático y elementos menores. |

## Índices y coordenadas

Los tiles de 8 × 8 están numerados por fila de izquierda a derecha:
- Fila 0 contiene índices 0–31.
- Fila 1 contiene índices 32–63.
- …
- Fila 31 contiene índices 992–1023.

Los módulos de 16 × 16 ocupan 2 × 2 tiles; los de 16 × 24 ocupan 2 × 3; los de 32 × 16 ocupan 4 × 2. Para extraerlos, usar las coordenadas de región y módulo del SVG, sin escalar de forma fraccional.

## Uso inicial en el montaje

1. Capas de fondo: cielo y siluetas lejanas (por generar en el paso siguiente).
2. Fachadas y módulos de ventana/puerta.
3. Rótulo de colmado, toldo y mostradores.
4. Cables, postes y vegetación.
5. Aceras y bordillos.
6. Asfalto y objetos de primer plano.
7. Personaje, enemigos, colisiones y salidas se añaden en una pasada aparte, sin incorporarlos al fondo como píxeles fijos.

## Estado y criterios de aceptación

- [x] Atlas vectorial editable creado con retícula lógica de 8 × 8.
- [x] Paleta provisional anotada.
- [x] Regiones y dimensiones de módulos documentadas.
- [ ] Validar que las formas no dependan de antialiasing al exportar a PNG.
- [ ] Extraer PNG de prueba sin reescalar y comprobar la paleta efectiva.
- [ ] Comparar con los tiles y paletas reales de la sala benchmark.
- [ ] Asegurar que la transparencia e índices se preservan en la herramienta de importación.
- [ ] Probar una escena en emulador o motor antes de declarar compatibilidad ROM.
