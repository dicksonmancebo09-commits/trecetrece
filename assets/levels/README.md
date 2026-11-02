# Paquetes de diseño de los siete niveles

Los siete paquetes siguen la distribución del atlas creativo. Cada directorio contiene la dirección artística, paleta de trabajo, módulos gráficos, capas de composición y presupuesto de salas de su barrio.

| Nivel | Barrio | Salas | Paquete |
|---|---|---:|---|
| L01 | Villa Duarte | 87 | [Diseño L01](level-01-villa-duarte/README.md) · [Atlas gráfico v0.2](level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.svg) |
| L02 | El Caliche | 54 | [Diseño L02](level-02-el-caliche/README.md) |
| L03 | La Francia Nueva | 61 | [Diseño L03](level-03-la-francia-nueva/README.md) · [Atlas SVG v0.1](level-03-la-francia-nueva/level-03-atlas-v0.1.svg) |
| L04 | Calero | 39 | [Diseño L04](level-04-calero/README.md) · [Atlas SVG v0.1](level-04-calero/level-04-atlas-v0.1.svg) |
| L05 | Pueblo Nuevo | 48 | [Diseño L05](level-05-pueblo-nuevo/README.md) · [Atlas SVG v0.1](level-05-pueblo-nuevo/level-05-atlas-v0.1.svg) |
| L06 | Los Molinos | 52 | [Diseño L06](level-06-los-molinos/README.md) · [Atlas SVG v0.1](level-06-los-molinos/level-06-atlas-v0.1.svg) |
| L07 | Simónico | 41 | [Diseño L07](level-07-simonico/README.md) · [Atlas SVG v0.1](level-07-simonico/level-07-atlas-v0.1.svg) |

## Registro maestro

- [Plan de siete niveles y 382 salas](../../docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md)
- [Registro estructurado de todas las salas](../../data/world/sector-cero-room-registry-v1.json)
- [Grafo de puertas de la estructura de referencia](../../data/world/sector-cero-source-door-graph-v1.json)

## Reglas comunes

- Pixel art GBA a escala nativa; la ampliación se usa solo para revisión.
- Mantener por separado los planos de fondo, arquitectura, props, suelo/plataformas y elementos interactivos.
- Los fondos, paletas y tilesets compartidos deben auditarse por todos sus consumidores antes de editarlos.
- Los atlas existentes de Villa Duarte y El Caliche son borradores de producción; no se declaran integrados a la ROM.
- Los niveles 3–7 tienen dirección artística y familias modulares especificadas, pero sus atlas gráficos aún deben producirse.
- La geometría, las colisiones, los enemigos, los eventos y las animaciones deben asignarse sala por sala; no se deducen solo del concepto visual.


## Estado de atlas — auditoría 02-11-2026

- L01: atlas SVG v0.2 + JSON de módulos; exportación PNG indexada/4bpp pendiente.
- L02: atlas SVG y exportaciones PNG descritas en [su paquete](../tiles/scenario-02/README.md); prueba en ROM pendiente.
- L03–L07: atlas SVG v0.1 + JSON, 64 módulos de 32 × 32 px por barrio; exportación PNG indexada/4bpp y composición por sala pendientes.

Los atlas SVG son bibliotecas editables; no son tilemaps ni mapas de las 382 salas. Informe de estado: [auditoría de producción 02-11-2026](../../docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md).
