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

## Paquete de producción — Escenario 2: Callejones del Caliche

Recursos registrados en `assets/tiles/scenario-02/`:

- [Catálogo y especificaciones](../../assets/tiles/scenario-02/README.md)
- [Atlas SVG de tiles, 256 × 256](../../assets/tiles/scenario-02/scenario-02-el-caliche-tiles.svg)
- [Atlas PNG indexado, 256 × 256](../../assets/tiles/scenario-02/scenario-02-el-caliche-tiles.png)
- [Composición por 11 capas](../../assets/tiles/scenario-02/scenario-02-layered-composition.svg)
- [Vista previa SVG](../../assets/tiles/scenario-02/scenario-02-native-preview.svg)
- [Vista previa PNG nativa, 240 × 160](../../assets/tiles/scenario-02/scenario-02-native-preview.png)
- [Metadatos de paleta y cuadrícula](../../assets/tiles/scenario-02/tile-atlas-metadata.json)

**Validación realizada:** los SVG pasan una comprobación básica de estructura; el atlas exporta a 256 × 256 con 15 colores visibles y huecos alfa; la vista exporta a 240 × 160 con los mismos 15 colores y sin transparencia. Ambos PNG están guardados en el repositorio. No se ha probado el arte en Inkscape, en la ROM ni en un emulador, y no se declara compatibilidad GBA.

**Referencias observadas:** un reportaje de Hoy sobre El Caliche muestra un callejón angosto, fachadas pintadas, muros de bloque y pavimento irregular; Diario Libre aporta referencias de frentes domésticos y ventanas con rejas. Las fotos no se incorporan como texturas ni se copian directamente.

## Puerta de localización antes de probar la ROM

- **Estado auditado:** en el árbol de la rama `main` revisado el 27 de octubre de 2026 no se encontró una tabla de traducción ni un archivo de diálogos conectado a la ROM.
- Se creó una guía y un paquete original de voz en `localization/es-419/`: [README](../../localization/es-419/README.md), [guía de voz y jerga](../../localization/es-419/VOICE_AND_SLANG_GUIDE.md), [diálogo de muestra](../../localization/es-419/dialogue.json) y [glosario regional](../../localization/es-419/glossary.json).
- Se creó el validador [`tools/check_localization_es419.py`](../../tools/check_localization_es419.py) y [pruebas unitarias](../../tests/test_localization_es419.py). Resultado ejecutado fuera del editor del usuario: 27 entradas de diálogo, 81 líneas; las 81 cumplen el límite provisional de 28 caracteres; tres pruebas unitarias pasan.
- Las muestras priorizan español dominicano, con registros asignados a personajes cubanos, puertorriqueños y jamaiquinos; México, Colombia y Argentina se ofrecen como cameos opcionales. Los recursos son texto original de preproducción, **no se han insertado en la ROM**.
- **Bloqueo previo a la prueba de ROM:** falta localizar la traducción real instalada, identificar la tabla/encoding y mapear las cadenas reales con IDs confirmados. Hasta completar esta auditoría y comprobar cortes, tildes, signos, apóstrofos y tamaño de cuadro, no presentar una ejecución en emulador como prueba de localización. Las pruebas actuales validan únicamente los archivos JSON y su formato editorial.

## Punto técnico de partida documentado

Consultar:
- [Biblia visual de Villa Duarte](VILLA_DUARTE_VISUAL_BIBLE.md)
- [Plan maestro de transformación visual](VISUAL_TRANSFORMATION_PLAN.md)
- [Línea base visual — Tarea 1](BASELINE_VISUAL_TAREA_01.md)
- [Identidad visual de los siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md)

El informe de línea base documenta la ROM de referencia y prototipos anteriores por hash, pero indica que falta una captura original obtenida en ejecución y que no hay prueba confirmada en MAGE o emulador. No declarar la ROM modificada y verificada basándose únicamente en documentación o previews.

## Siguiente secuencia de trabajo

1. Seguir creando la identidad modular del escenario 3, La Francia Nueva, siguiendo la guía de siete escenarios y usando referencias documentales específicas.
2. Mantener los paquetes de los escenarios 1 y 2 como borradores editables; no convertirlos en tilesets ROM sin identificar primero los recursos reales de la sala objetivo.
3. Obtener una captura original reproducible de la sala técnica, abrir los recursos en una herramienta compatible y documentar mapa, tiles, paleta, compresión y dependencias.
4. Comparar los paquetes de arte con los recursos reales, hacer un mapeo pequeño y reversible y registrar diferencias visuales.
5. Solo entonces probar la escena en una herramienta/emulador, manteniendo la ROM original intacta.

## Regla de continuidad entre conversaciones

Antes de repetir decisiones, revisar este archivo, la [guía de siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md), la [Biblia Visual](VILLA_DUARTE_VISUAL_BIBLE.md), el [Plan Maestro](VISUAL_TRANSFORMATION_PLAN.md), la [Línea Base](BASELINE_VISUAL_TAREA_01.md) y el historial de commits. Actualizar este archivo cuando cambien el título, alcance, assets o estado de validación.
