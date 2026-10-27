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

## Punto técnico de partida documentado

Consultar:
- [Biblia visual de Villa Duarte](VILLA_DUARTE_VISUAL_BIBLE.md)
- [Plan maestro de transformación visual](VISUAL_TRANSFORMATION_PLAN.md)
- [Línea base visual — Tarea 1](BASELINE_VISUAL_TAREA_01.md)
- [Identidad visual de los siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md)

El informe de línea base documenta la ROM de referencia y prototipos anteriores por hash, pero indica que falta una captura original obtenida en ejecución y que no hay prueba confirmada en MAGE o emulador. No declarar la ROM modificada y verificada basándose únicamente en documentación o previews.

## Siguiente secuencia de trabajo

1. Revisar el atlas y refinar las siete identidades a partir de referencias específicas, especialmente para los sectores cuyo detalle local todavía no está documentado.
2. Desglosar el escenario 1 en capas y tiles originales: fachadas, puertas/ventanas/rejas, colmado y rótulos ficticios, cables/postes, vegetación, aceras y suelo.
3. Confirmar el recurso/sala de referencia y obtener una captura original reproducible.
4. Crear una pequeña escena/tileset, preservando los originales, y revisar lectura a resolución nativa.
5. Validar el cambio en herramienta o emulador antes de extenderlo al resto de áreas.

## Regla de continuidad entre conversaciones

Antes de repetir decisiones, revisar este archivo, la [guía de siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md), la [Biblia Visual](VILLA_DUARTE_VISUAL_BIBLE.md), el [Plan Maestro](VISUAL_TRANSFORMATION_PLAN.md), la [Línea Base](BASELINE_VISUAL_TAREA_01.md) y el historial de commits. Actualizar este archivo cuando cambien el título, alcance, assets o estado de validación.
