# Escenario 02 — Callejones del Caliche

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Zona de inspiración:** El Caliche, Villa Duarte, Santo Domingo Este  
**Versión:** v0.1 · vectorial editable · no integrado en ROM

## Archivos

- [Atlas modular de tiles (SVG editable, 256 × 256)](scenario-02-el-caliche-tiles.svg)
- [Atlas modular exportado (PNG indexado, 256 × 256)](scenario-02-el-caliche-tiles.png)
- [Composición por capas (SVG editable, 240 × 160 de coordenadas)](scenario-02-layered-composition.svg)
- [Vista previa nativa (SVG)](scenario-02-native-preview.svg)
- [Vista previa rasterizada nativa (PNG indexado, 240 × 160)](scenario-02-native-preview.png)
- [Metadatos y paleta (JSON)](tile-atlas-metadata.json)

## Dirección visual

Esta zona se diferencia del escenario inicial por compresión espacial, fachadas muy próximas, rejas densas, pintura erosionada, superficies de bloque expuestas y una boca de callejón más oscura al fondo. La luz se filtra en bandas desde arriba; la calzada continúa horizontalmente para permitir una lectura de juego lateral clara.

El objetivo no es convertir a los vecinos ni al deterioro urbano en caricatura. La escena toma como referencia la forma de las calles, los materiales, las rejas y las fachadas que muestran las fuentes consultadas. Las imágenes de prensa se usan solo para observar; no se copian fotografías, personas ni grafitis identificables.

## Especificación del atlas

- Lienzo: **256 × 256 px**, sin escalado en el archivo maestro.
- Retícula lógica: **8 × 8 px**, 32 columnas × 32 filas.
- Índice de tile: `index = tile_y * 32 + tile_x`, origen superior izquierdo.
- Grupos de módulos mayores: ventanas 16 × 16; puertas, rejas y bajantes 16 × 24; aleros 32 × 16.
- Paleta de trabajo: **15 colores visibles**, con alfa en huecos del SVG.
- El alfa de origen no equivale automáticamente a una entrada concreta de paleta GBA. La semántica de transparencia cambia según el recurso sea BG, sprite/OBJ y la herramienta que lo importe.

## Regiones

| Región | Rectángulo (x,y,w,h) | Uso |
|---|---|---|
| Paredes pintadas y gastadas | `0,0,256,64` | Coral apagado, rosa polvo, verde pálido, hormigón y sombras. |
| Ventanas | `0,64,256,32` | Marcos y variantes con cristales y rejas. |
| Puertas | `0,96,256,24` | Entradas de vivienda, puertas antiguas y persianas. |
| Rejas y portones | `0,120,256,24` | Módulos metálicos para ventanas o accesos. |
| Aleros y barandas | `0,144,256,16` | Perfiles de balcón, escalón y borde de pared. |
| Pintura gastada | `0,160,256,24` | Parches, bloques expuestos y manchas. |
| Bajantes y cajas | `0,184,256,24` | Tuberías, conducciones y cajas de servicio. |
| Cableado | `0,208,256,8` | Segmentos repetibles de 8 × 8. |
| Bordillo | `0,216,256,8` | Borde de acera. |
| Pavimento | `0,224,256,16` | Asfalto y juntas partidas. |
| Objetos de calle | `0,240,256,16` | Drenaje, cubo, maceta, escombro, caja y escalón. |

## Composición por capas

El SVG de composición define once capas separables: fondo, tejados lejanos, pasaje al fondo, fachadas izquierda y derecha, huecos, rejas, cableado, desgaste, suelo y objetos. El protagonista que aparece como referencia es un marcador original de composición, no un sprite definitivo.

## Referencias de observación

- [Hoy — El Caliche de Villa Duarte](https://hoy.com.do/el-pais/el-caliche-de-villa-duarte-la-otra-cara-del-crecimiento-economico_762790.html): se observan pasaje estrecho, fachadas pintadas, bloques, rejas y pavimento irregular.
- [Diario Libre — Fundación busca fondos para transformar El Caliche](https://www.diariolibre.com/actualidad/ciudad/fundacion-busca-fondos-para-transformar-el-sector-el-caliche-de-villa-duarte-MG11174899): se observan fachadas, ventanas protegidas con rejas y escala peatonal.

Estas fuentes apoyan rasgos visuales generales, pero no dan permiso automático para redistribuir sus fotografías. El arte del juego se construye de nuevo con geometría original.

## Estado de validación

- [x] Atlas SVG creado.
- [x] Composición separada en 11 capas SVG.
- [x] Paleta provisional y coordenadas documentadas.
- [x] Exportación PNG a 256 × 256 y 240 × 160 creada con dimensiones exactas.
- [x] Comprobar que no aparecen colores antialias fuera de la paleta: el atlas usa 15 colores visibles y transparencia de origen; la vista usa los mismos 15 colores, sin alfa.
- [ ] Revisar manualmente la composición en un editor gráfico y compararla con la captura real de una sala y su sistema de colisiones.
- [ ] Importar en herramienta compatible y probar en juego/emulador.
- [ ] Mapear de forma segura las paletas GBA; no sobrescribir la ROM original.

## Próximo paso

Validar los archivos en el editor/exportador y revisar la composición a 240 × 160. Después se cotejará con una sala original antes de adaptar sus módulos a una prueba jugable.
