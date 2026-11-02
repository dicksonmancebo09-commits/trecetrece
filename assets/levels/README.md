# Paquetes de diseño de los siete niveles

Los siete paquetes siguen la distribución del atlas creativo. Cada directorio contiene la dirección artística, paleta de trabajo, módulos gráficos, capas de composición y presupuesto de salas de su barrio.

| Nivel | Barrio | Salas | Paquete |
|---|---|---:|---|
| L01 | Villa Duarte | 87 | [Diseño L01](level-01-villa-duarte/README.md) |
| L02 | El Caliche | 54 | [Diseño L02](level-02-el-caliche/README.md) |
| L03 | La Francia Nueva | 61 | [Diseño L03](level-03-la-francia-nueva/README.md) |
| L04 | Calero | 39 | [Diseño L04](level-04-calero/README.md) |
| L05 | Pueblo Nuevo | 48 | [Diseño L05](level-05-pueblo-nuevo/README.md) |
| L06 | Los Molinos | 52 | [Diseño L06](level-06-los-molinos/README.md) |
| L07 | Simónico | 41 | [Diseño L07](level-07-simonico/README.md) |

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
