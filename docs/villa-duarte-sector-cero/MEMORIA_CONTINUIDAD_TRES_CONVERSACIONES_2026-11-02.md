# Memoria de continuidad — LATINO AMÉRICA Zector Cero

**Versión:** 1.0  
**Fecha de corte:** 2 de noviembre de 2026  
**Alcance:** resumen operativo de las tres conversaciones recientes relacionadas con la producción del juego.  
**Naturaleza del respaldo:** reconstrucción de decisiones, estado y pendientes a partir del contexto disponible y de los artefactos consultados en GitHub. No es una transcripción literal de los chats.

## 1. Fuente de verdad del proyecto

- Repositorio: https://github.com/dicksonmancebo09-commits/trecetrece
- Rama revisada: `agent/rea-editable-analysis`
- Título oficial: **LATINO AMÉRICA Zector Cero**.
- Dirección artística: barrios de Villa Duarte y otros sectores de Santo Domingo Este, con identidades diferenciadas para los siete niveles.
- Referencia técnica examinada: Metroid Fusion USA/Australia (`AMTE`, 8 MiB), sin convertir la ROM comercial en contenido distribuible.
- Regla de validación: separar siempre **planificado**, **creado**, **comprobado estáticamente**, **exportado**, **integrado en ROM** y **probado en emulador**. Un SVG o una ficha de referencia no equivalen a una sala jugable.

## 2. Las tres conversaciones de proyecto resumidas

### Conversación A — 2 de noviembre de 2026, «Continuar producción por lotes»

**Solicitud principal:** dejar de inventar nuevas salas y transformar las 382 planificadas en entregables reales. La auditoría solicitada debía:

1. cotejar los 382 identificadores con el registro maestro;
2. localizar duplicados y salas/puertas huérfanas;
3. completar las fichas técnicas individuales;
4. producir los atlas gráficos que faltaban;
5. preparar la integración y las pruebas en la ROM.

**Resultado que ahora consta en la rama:** el informe `PRODUCTION_AUDIT_2026-11-02.md`, el manifiesto de cinco lotes, las fichas técnicas y los atlas por nivel están versionados. El cierre de la auditoría distingue correctamente el control estructural del trabajo de integración: la ROM no se ha actualizado en este hito.

### Conversación B — 2 de noviembre de 2026, «Retomar ritmo de trabajo»

**Decisiones del usuario:**

- El objetivo permanece en **382 salas**, no se reduce a 87.
- Los 87 del primer lote son solo el primer tramo.
- Se pidió continuar los lotes 2, 3, 4 y 5 y recuperar el acceso a la herramienta Game Development Studio.

**Estado consolidado en el manifiesto actual:**

| Lote | Cantidad | Distribución |
|---|---:|---|
| 1 | 87 | 87 Villa Duarte |
| 2 | 87 | 54 El Caliche + 33 La Francia Nueva |
| 3 | 87 | 28 La Francia Nueva + 39 Calero + 20 Pueblo Nuevo |
| 4 | 87 | 28 Pueblo Nuevo + 52 Los Molinos + 7 Simónico |
| 5 | 34 | 34 Simónico |
| **Total** | **382** | **7 niveles** |

Comprobación adicional realizada sobre `sector-cero-production-manifest-v1.json`: 382 filas, 382 `production_id` distintos, 382 `room_id` distintos y ningún duplicado en la asignación conjunta. El acceso a Game Development Studio no queda acreditado como restaurado por los artefactos consultados; no debe darse por recuperado sin una comprobación separada.

### Conversación C — 28 de octubre de 2026, «Analizar ROM de Aria of Sorrow»

**Solicitud principal:** recopilar el trabajo de análisis con REA, investigar la estructura del juego y dejar documentación en GitHub.

**Precisión importante de alcance:** los documentos REA consultados en esta rama describen una investigación de **Metroid Fusion USA/Australia (`AMTE`)** como referencia técnica para Zector Cero. No hay evidencia suficiente en los artefactos consultados para afirmar que el análisis documentado cubra también una ROM de Aria of Sorrow. Mantener ambos títulos separados hasta verificar la ROM concreta y su hash.

**Entregables de referencia que sí existen:**

- `Codigo_base_reconstruido_Metroid_Fusion.docx` en la biblioteca, fechado el 1 de noviembre de 2026.
- `recovery/docs/REA_FULL_ROM_TO_EDITABLE_CODE.md` en GitHub.
- `docs/villa-duarte-sector-cero/research/METROID_REA_WORKFLOW.md` en GitHub.
- Archivos C descriptivos del arranque y despachador de modos. Son modelos de observaciones estáticas, no el código original íntegro ni una reconstrucción recompilable.

## 3. Estado verificado de la auditoría de producción

Fuente principal: [`PRODUCTION_AUDIT_2026-11-02.md`](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md).

| Área | Estado | Límite que debe conservarse |
|---|---|---|
| Registro de IDs | 382/382 cotejados según la auditoría | La verificación es contra el plan/registro de referencia, no contra la ROM local. |
| Lotes | 382/382 asignados en cinco lotes | El manifiesto prueba asignación, no construcción de 382 salas jugables. |
| Puertas | 898 registros; 0 destinos predeterminados y 0 variantes de evento sin destino inexistente | Es la topología de referencia extraída de `metroidret/mf`; falta contrastarla con la ROM exacta y adaptar rutas creativas. |
| Fichas técnicas | 382/382 enriquecidas con metadatos | No contienen todavía los mapas RLE reconstruidos, la matriz espacial completa de colisiones, entidades/eventos finales ni offsets verificados contra la ROM privada. |
| Atlas | Siete bibliotecas SVG en el repositorio | Los cinco SVG nuevos son bibliotecas conceptuales editables de 64 módulos cada una (320 módulos nuevos); no son mapas de sala ni tilesets integrados. |
| Exportación GBA | Herramientas y workflow versionados | No hay prueba confirmada de un workflow verde ni de artefactos indexados/4bpp/LZ77 publicados. |
| Integración ROM | No iniciada en binario en esta auditoría | Falta acceso a la ROM privada exacta, hash observado y extracción específica por sala. |
| Emulador | Pendiente | No se ejecutó la ROM en mGBA durante la auditoría. |

### Atlas registrados

- L01 Villa Duarte: `assets/levels/level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.svg`.
- L02 El Caliche: paquete `assets/tiles/scenario-02/`.
- L03 La Francia Nueva: `assets/levels/level-03-la-francia-nueva/level-03-atlas-v0.1.svg`.
- L04 Calero: `assets/levels/level-04-calero/level-04-atlas-v0.1.svg`.
- L05 Pueblo Nuevo: `assets/levels/level-05-pueblo-nuevo/level-05-atlas-v0.1.svg`.
- L06 Los Molinos: `assets/levels/level-06-los-molinos/level-06-atlas-v0.1.svg`.
- L07 Simónico: `assets/levels/level-07-simonico/level-07-atlas-v0.1.svg`.

Los cinco atlas nuevos se describen como SVG de 256 × 256 px, 64 módulos compuestos de 32 × 32 px por atlas. Falta el paso reproducible de rasterizar, indexar paleta, convertir a 4bpp y comprobar round-trip/compresión con la automatización del repositorio.

## 4. Pendientes concretos y orden correcto

### P0 — acceso y validación de fuentes

- Conseguir acceso operativo al Codespace/entorno privado donde está la ROM; la conversación actual no tiene shell remoto ni acceso al archivo `private-roms/`.
- Ejecutar la auditoría local de la ROM exacta y guardar su SHA-256 observado. No reutilizar offsets si el hash no coincide con la referencia documentada.
- Comprobar en GitHub Actions la ejecución real del workflow de producción; el archivo YAML existe, pero su éxito no está acreditado en el informe.

### P1 — completar las fichas de integración

- Extraer y validar BG maps y clipdata/RLE de cada sala.
- Recuperar geometría de colisiones y coordenadas de entidades/sprites.
- Resolver eventos, puertas adaptadas, punteros y consumidores de recursos compartidos.
- Marcar por campo la procedencia: referencia comunitaria, ROM exacta, inferencia o valor pendiente.

### P2 — cerrar recursos gráficos GBA

- Exportar los siete atlas a PNG indexado con 16 entradas y transparencia correcta.
- Convertir a 4bpp/BGR555 y LZ77 mediante las herramientas versionadas.
- Conservar hashes, reportes de round-trip y artifacts de CI.
- Revisar los módulos a resolución nativa; no declarar arte final aprobado solo porque el SVG existe.

### P3 — integración vertical, no integración masiva

- Elegir una sala de prueba que tenga acceso, salida, paleta, tileset y datos de colisión entendidos.
- Crear una copia de ROM con hash de base y rangos de escritura comprobados; preservar la ROM original.
- Integrar solo esa sala y ejecutar el diagnóstico mGBA.
- Revisar capturas y logs de arranque, navegación, puertas, colisiones, transparencia, paleta, sprites y guardado.
- Solo después de superar esa prueba, extender a un conjunto pequeño de salas conectadas.

## 5. Estado del arranque y REA

- La v1.3 se retiró como candidata funcional tras reportes de pantalla/título defectuosos y bloqueo.
- Los documentos registran correcciones estáticas hasta v1.7, incluido el salto hacia el flujo del hangar y comprobaciones de checksum/BPS.
- La v1.7 tampoco debe etiquetarse como funcional: no se ha confirmado ejecución real de CPU/juego en mGBA.
- El C reconstruido documenta observaciones de arranque y 15 destinos del despachador, pero no implementa sus handlers ni el motor de salas.
- Para GBA debe validarse con Ghidra `ARM:LE:32:v4t`; el análisis genérico `arm` de REA puede seleccionar ARMv7 y no es evidencia final por sí solo.

## 6. Archivos y enlaces canónicos para retomar

- [README del repositorio](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/README.md)
- [Estado de continuidad del proyecto](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/docs/villa-duarte-sector-cero/PROJECT_STATE_HANDOFF.md)
- [Plan maestro de 382 salas](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md)
- [Registro de salas](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/data/world/sector-cero-room-registry-v1.json)
- [Manifiesto de cinco lotes](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/data/world/sector-cero-production-manifest-v1.json)
- [Fichas técnicas de 382 salas](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/data/world/sector-cero-room-technical-sheets-v1.json)
- [Grafo de puertas de referencia](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/data/world/sector-cero-source-door-graph-v1.json)
- [Auditoría de producción](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md)
- [Guía REA a código editable](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/recovery/docs/REA_FULL_ROM_TO_EDITABLE_CODE.md)
- [Flujo REA/Ghidra](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/docs/villa-duarte-sector-cero/research/METROID_REA_WORKFLOW.md)

## 7. Regla para próximas sesiones

No volver a diseñar ni renombrar salas por defecto. Primero leer esta memoria, el README, el manifiesto, las fichas y la auditoría. Mantener el objetivo en 382. Informar cada tarea con tres estados separados: **hecho y comprobado**, **creado pero no probado**, **pendiente por bloqueo externo**. No afirmar que una sala está integrada hasta que exista el binario actualizado y una prueba reproducible en emulador.
