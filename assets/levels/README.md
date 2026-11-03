# Paquetes de diseño de los siete niveles

Los siete paquetes siguen la distribución del atlas creativo. Cada directorio contiene la dirección artística, paleta de trabajo, módulos gráficos, capas de composición y presupuesto de salas de su barrio.

| Nivel | Barrio | Salas | Paquete |
|---|---|---:|---|
| L01 | Villa Duarte | 87 | [Diseño L01](level-01-villa-duarte/README.md) · [SVG v0.2](level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.svg) · [PNG indexado](level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2-indexed.png) |
| L02 | El Caliche | 54 | [Diseño L02](../tiles/scenario-02/README.md) · [PNG indexado](../tiles/scenario-02/scenario-02-el-caliche-tiles-audit-indexed.png) |
| L03 | La Francia Nueva | 61 | [Diseño L03](level-03-la-francia-nueva/README.md) · [SVG v0.1](level-03-la-francia-nueva/level-03-atlas-v0.1.svg) · [PNG indexado](level-03-la-francia-nueva/level-03-atlas-v0.1-indexed.png) |
| L04 | Calero | 39 | [Diseño L04](level-04-calero/README.md) · [SVG v0.1](level-04-calero/level-04-atlas-v0.1.svg) · [PNG indexado](level-04-calero/level-04-atlas-v0.1-indexed.png) |
| L05 | Pueblo Nuevo | 48 | [Diseño L05](level-05-pueblo-nuevo/README.md) · [SVG v0.1](level-05-pueblo-nuevo/level-05-atlas-v0.1.svg) · [PNG indexado](level-05-pueblo-nuevo/level-05-atlas-v0.1-indexed.png) |
| L06 | Los Molinos | 52 | [Diseño L06](level-06-los-molinos/README.md) · [SVG v0.1](level-06-los-molinos/level-06-atlas-v0.1.svg) · [PNG indexado](level-06-los-molinos/level-06-atlas-v0.1-indexed.png) |
| L07 | Simónico | 41 | [Diseño L07](level-07-simonico/README.md) · [SVG v0.1](level-07-simonico/level-07-atlas-v0.1.svg) · [PNG indexado](level-07-simonico/level-07-atlas-v0.1-indexed.png) |

## Registro maestro

- [Plan de siete niveles y 382 salas](../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md)
- [Registro estructurado de todas las salas](../../data/world/sector-cero-room-registry-v1.json)
- [Grafo de puertas de la estructura de referencia](../../data/world/sector-cero-source-door-graph-v1.json)

## Reglas comunes

- Pixel art GBA a escala nativa; la ampliación se usa solo para revisión.
- Mantener por separado los planos de fondo, arquitectura, props, suelo/plataformas y elementos interactivos.
- Los fondos, paletas y tilesets compartidos deben auditarse por todos sus consumidores antes de editarlos.
- Los atlas existentes de Villa Duarte y El Caliche son borradores de producción; no se declaran integrados a la ROM.
- Los niveles 3–7 tienen atlas SVG v0.1 editables; faltan PNG indexado/4bpp, composición por sala, colisiones e integración ROM.
- La geometría, las colisiones, los enemigos, los eventos y las animaciones deben asignarse sala por sala; no se deducen solo del concepto visual.


## Estado de atlas — auditoría 02-11-2026

- L01–L07: los siete atlas tienen PNG indexado de 256 × 256 px, retícula de 32 × 32 tiles y 16 entradas de paleta con transparencia en índice 0.
- Los siete se exportaron también a gráficos 4bpp (1.024 tiles × 32 bytes), paleta BGR555 de 32 bytes y LZ77; los siete informes registran round-trip 4bpp y LZ77 correctos.
- Los archivos 4bpp/BGR555/LZ77 se publicaron en el artifact [zector-cero-gba-atlas-exports](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41614610801). El artifact caduca el 17 de noviembre de 2026.

Los SVG son bibliotecas editables; los PNG indexados y binarios exportados siguen siendo atlases, no tilemaps de habitación ni mapas de las 382 salas. Los archivos `.4bpp`, `.4bpp.lz` y `.bgr555.pal` están además en el directorio `exports/` de cada nivel. No hay integración ROM. Informe de estado: [auditoría de producción](../../docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md).
## Conversión GBA automatizada

El workflow [Zector Cero — production asset export](../../.github/workflows/zector-cero-production-assets.yml) rasteriza los siete atlas declarados en [gba_atlas_export_manifest.json](../../config/gba_atlas_export_manifest.json) a PNG indexado y verifica cada uno con el conversor 4bpp/BGR555/LZ77. La salida binaria se publica como artifact de GitHub Actions; no altera la ROM.


## Datos técnicos de sprites por sala

- [CSV de 2.150 posiciones de sprites de referencia](../../recovery/analysis/ROOM_SPRITE_PLACEMENTS_2026-11-03.csv).
- Las coordenadas son valores crudos de los arrays del código de referencia. No se interpretan como píxeles ni como posiciones de enemigos originales sin convertir unidades y semántica del motor.
