# Estado de continuidad del proyecto — LATINO AMÉRICA Zector Cero

**Última actualización:** 27 de octubre de 2026  
**Repositorio canónico:** https://github.com/dicksonmancebo09-commits/trecetrece  
**Rama de trabajo:** `main`

## Identidad oficial

- **Título oficial del juego:** LATINO AMÉRICA Zector Cero.
- **Dirección artística:** barrios de Villa Duarte, Santo Domingo Este, República Dominicana.
- **Villa Duarte — Sector Cero** puede aparecer en documentación antigua como nombre provisional o referencia de zona; no debe sustituir el título oficial en materiales nuevos.
- La inspiración debe proceder de barrios concretos y su arquitectura cotidiana. No convertir el juego en una ciudad latinoamericana genérica ni en cyberpunk por defecto.

## Acuerdos creativos y técnicos

1. Las fachadas, rejas, balcones, colmados y talleres, callejones, aceras, cables, vehículos y vegetación deben usarse según la zona y las referencias disponibles.
2. El Caliche, La Francia Nueva, Calero, Pueblo Nuevo, Los Molinos y Simonico no son intercambiables. No atribuir rasgos específicos sin referencias que lo respalden.
3. Metroid Fusion es una referencia técnica para estudiar mapas, habitaciones, sprites, animaciones y límites de la ROM; sus salas no determinan la estética final.
4. La primera calle conceptual es una propuesta de dirección artística, no un escenario ya integrado ni una modificación de ROM.
5. No dar por completado un cambio hasta registrar su archivo/recurso y el nivel real de validación: generado, comprobado estáticamente, probado en herramienta o probado en juego.
6. Mantener copias originales y cambios pequeños y reversibles. No publicar ROMs comerciales, ROMs derivadas, parches ni recursos propietarios copiados.
7. **Flujo acordado:** las directrices llegan por la conversación; los artefactos y cambios del proyecto se guardan en este repositorio como fuente compartida de continuidad. Informar rutas y commits al cerrar cada lote.

## Primer concepto visual versionado

- **Archivo editable:** [latino-america-zector-cero-villa-duarte-street.svg](../../assets/concept/latino-america-zector-cero-villa-duarte-street.svg)
- **Formato:** SVG vectorial editable, 1600 × 960.
- **Contenido:** título del juego, calle inspirada en Villa Duarte, colmado ficticio, fachadas, balcones/rejas, cables aéreos, vegetación, motor, personaje explorador original, paleta provisional y panel de estado.
- **Estado:** añadido a GitHub; concepto vectorial, no tileset final, no captura de emulador y no integrado en la ROM.
- El tablero rasterizado generado anteriormente en el chat no debe confundirse con este SVG editable; el recurso de trabajo versionado aquí es el SVG enlazado arriba.

## Punto técnico de partida documentado

Consultar:
- [Biblia visual de Villa Duarte](VILLA_DUARTE_VISUAL_BIBLE.md)
- [Plan maestro de transformación visual](VISUAL_TRANSFORMATION_PLAN.md)
- [Línea base visual — Tarea 1](BASELINE_VISUAL_TAREA_01.md)

El informe de línea base documenta la ROM de referencia y prototipos anteriores por hash, pero también indica que falta una captura original obtenida en ejecución y que no hay prueba confirmada en MAGE o emulador. Por tanto, todavía no se debe declarar modificada y verificada la ROM a partir de esas pruebas.

## Siguiente secuencia de trabajo

1. Revisar visualmente el SVG vectorial y preparar versiones por capas y piezas reutilizables.
2. Desglosar la calle en tiles originales: fachadas, puertas/ventanas/rejas, colmado y rótulos ficticios, cables/postes, vegetación, aceras y suelo.
3. Confirmar el recurso/sala técnica de la ROM y obtener una captura original reproducible.
4. Crear una primera escena/tileset pequeño, preservando el original, y revisar legibilidad a resolución nativa.
5. Validar el cambio en una herramienta o emulador antes de expandirlo a otras habitaciones.

## Regla de continuidad entre conversaciones

Usar este archivo como el estado compartido más reciente. Antes de repetir decisiones, revisar este archivo, la Biblia Visual, el Plan Maestro, la Línea Base y el historial de commits del repositorio. Actualizar este archivo cuando cambien el título, el alcance, los assets o el estado de validación.
