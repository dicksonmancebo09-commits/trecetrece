# Estado de continuidad del proyecto — LATINO AMÉRICA Zector Cero

**Última actualización:** 27 de octubre de 2026  
**Repositorio canónico:** https://github.com/dicksonmancebo09-commits/trecetrece  
**Rama de trabajo:** `main`

## Identidad oficial

- **Título oficial del juego:** LATINO AMÉRICA Zector Cero.
- **Dirección artística:** barrios de Villa Duarte, Santo Domingo Este, República Dominicana.
- «Villa Duarte — Sector Cero» puede aparecer en documentación previa como nombre provisional; no sustituye el título oficial en materiales nuevos.
- La conversación es el canal para recibir directrices; el repositorio es la fuente compartida para documentos, artefactos, decisiones de diseño y estado del trabajo.

## Acuerdos creativos y técnicos

1. Las fachadas, rejas, balcones, colmados y talleres, callejones, aceras, cables, vehículos y vegetación se distribuyen según el lugar y la composición; no se amontonan como decoración.
2. El Caliche, La Francia Nueva, Calero, Pueblo Nuevo, Los Molinos y Simónico no son intercambiables. No atribuir rasgos concretos sin referencias que los respalden.
3. Metroid Fusion es una referencia técnica para estudiar mapas, habitaciones, sprites, animaciones y límites de ROM; sus salas no definen la estética final.
4. Los conceptos visuales no son escenarios integrados ni modificaciones de ROM.
5. No dar por completado un cambio hasta registrar el archivo/recurso y el nivel real de validación: generado, comprobado estáticamente, probado en herramienta o probado en juego.
6. Mantener copias originales y cambios pequeños y reversibles. No publicar ROMs comerciales, ROMs derivadas, parches ni recursos propietarios copiados.
7. Tras cada lote, actualizar el estado de continuidad y los enlaces de README para que una conversación posterior pueda retomarlo.

## Artefactos visuales versionados

- **Atlas editable de siete escenarios:** [assets/concept/latino-america-zector-cero-seven-scenarios.svg](../../assets/concept/latino-america-zector-cero-seven-scenarios.svg)
- **Guía de identidad visual por escenario:** [SEVEN_SCENARIO_VISUAL_IDENTITIES.md](SEVEN_SCENARIO_VISUAL_IDENTITIES.md)
- **Concepto vectorial de la primera calle:** [assets/concept/latino-america-zector-cero-villa-duarte-street.svg](../../assets/concept/latino-america-zector-cero-villa-duarte-street.svg)

El atlas presenta siete identidades con diferentes siluetas, colores, arquitectura y atmósferas: Entrada al Barrio; Callejones; Calle Residencial; Ruta de Talleres; Patios y Azoteas; Pasajes de Servicio; La Noche del Barrio. La guía distingue entre referencias observadas de El Caliche y La Francia Nueva, y escenarios compuestos creados para el juego. Los nombres y asignaciones de zona son decisiones creativas provisionales, no una cartografía histórica o una descripción oficial de cada sub-barrio.

**Estado:** documentos y arte vectorial guardados en GitHub; concepto visual v0.1. El SVG es editable, pero no está desglosado aún en tiles de juego ni validado a resolución nativa.

## Paso 2 — preparación del escenario 1

Paquete editable guardado en `assets/tiles/scenario-01/`:

- [Catálogo y especificación](../../assets/tiles/scenario-01/README.md).
- [Atlas modular 256 × 256](../../assets/tiles/scenario-01/scenario-01-villa-duarte-tiles.svg): cuadrícula lógica de 8 × 8, 32 × 32 celdas, módulos de fachada, ventanas, puertas/rejas, colmado, toldos, vegetación, cableado, acera, bordillo, asfalto y objetos.
- [Composición por capas](../../assets/tiles/scenario-01/scenario-01-layered-composition.svg): 9 grupos editables, con coordenadas de escena 240 × 160.
- [Vista de composición nativa](../../assets/tiles/scenario-01/scenario-01-native-preview.svg): viewBox 240 × 160, vista ampliada 4× para leer el montaje.
- [Metadatos](../../assets/tiles/scenario-01/tile-atlas-metadata.json): paleta provisional, cuadrícula, regiones y estado de validación.

**Comprobado:** los 3 SVG pasan una comprobación básica de estructura de etiquetas; la paleta de colores visibles coincide con los 15 colores documentados; el JSON se analiza y registra 1.024 celdas posibles en la cuadrícula.  
**Pendiente:** abrir en un editor gráfico, exportar PNG a resolución nativa, validar el remapeo de color y la transparencia según BG/OBJ, comparar con la paleta y tiles reales de la sala de referencia, y probar dentro del juego. No se ha modificado la ROM.

## Punto técnico de partida documentado

Consultar:
- [Biblia visual de Villa Duarte](VILLA_DUARTE_VISUAL_BIBLE.md)
- [Plan maestro de transformación visual](VISUAL_TRANSFORMATION_PLAN.md)
- [Línea base visual — Tarea 1](BASELINE_VISUAL_TAREA_01.md)
- [Identidad visual de los siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md)

El informe de línea base documenta la ROM de referencia y prototipos anteriores por hash, pero indica que falta una captura original obtenida en ejecución y que no hay prueba confirmada en MAGE o emulador. No declarar la ROM modificada y verificada basándose únicamente en documentación o previews.

## Siguiente secuencia de trabajo

1. Abrir y revisar la composición de 9 capas en un editor SVG compatible, comprobando la visibilidad y edición de cada capa.
2. Exportar el atlas y la composición a PNG con dimensiones nativas declaradas, sin interpolación ni deformación; inspeccionar color y transparencia.
3. Confirmar el recurso/sala de referencia y obtener una captura original reproducible.
4. Comparar las piezas del atlas con tiles, paletas y dependencias de esa sala, y adaptar el mapeo sin sobrescribir originales.
5. Probar una escena pequeña en herramienta/emulador antes de extender el sistema a más habitaciones.

## Regla de continuidad entre conversaciones

Antes de repetir decisiones, revisar este archivo, la [guía de siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md), la [Biblia Visual](VILLA_DUARTE_VISUAL_BIBLE.md), el [Plan Maestro](VISUAL_TRANSFORMATION_PLAN.md), la [Línea Base](BASELINE_VISUAL_TAREA_01.md) y el historial de commits. Actualizar este archivo cuando cambien el título, alcance, assets o estado de validación.
