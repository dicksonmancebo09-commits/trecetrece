# Bitácora de trabajo

## 2026-10-23 a 2026-10-25 — preparación del proyecto

- Se inició trabajo en el repositorio trecetrece con imágenes y referencias visuales de proyecto.
- En la rama main revisada posteriormente, el archivo asset juego barrio z tenía 1 byte y no contenía material útil; el inventario completo no mostraba archivos llamados REA o MAGE.

## Fecha exacta no verificada — prototipo de sala inicial

- Se produjo una prueba de integración visual con ambientación urbana dominicana.
- Resultado real: sustitución gráfica de una sola sala (sala 0 de MAIN_DECK), no de todo el juego.
- En el proceso se identificó que una iteración anterior tenía referencias de gráficos inadecuadas; el prototipo posterior restauró desde la ROM original los dos punteros erróneos que se habían identificado.
- Se realizaron comprobaciones estáticas, pero no se confirmó una prueba de ejecución en MAGE ni en emulador.
- Conclusión: conservar la prueba como registro histórico local, no tratarla como versión estable ni continuar de forma automática por el mismo método.

## 2026-10-27 — documentación y cambio de método

- Se inspeccionó el árbol público de main: 14 archivos, compuesto por README.md, un placeholder llamado asset juego barrio z y varias imágenes watermarked_img_*.jpg.
- No aparece una carpeta/archivo llamado REA en la rama revisada. Es posible que el elemento esté local, en otra rama o en otro repositorio; aún no está identificado.
- Se decidió documentar referencias, licencias, alcance técnico y limitaciones sin subir ROMs, parches ni recursos comerciales.
- **Estado:** no realizar más cambios a la ROM hasta que se defina el nuevo procedimiento.

## Plantilla para nuevas pruebas

Para cada cambio futuro:
1. Objetivo y motivo.
2. Archivo/base/version utilizados.
3. Herramienta y versión.
4. Recurso exacto modificado y ubicación.
5. Hipótesis antes del cambio.
6. Resultado esperado y resultado observado.
7. Prueba de ejecución y evidencia.
8. Método de reversión.
9. Licencia y procedencia de cualquier recurso nuevo.


## 2026-10-27 — objetivo global de ROM y regla de veracidad

- El alcance del proyecto se actualiza explícitamente: la meta es transformar visualmente la ROM completa, no detenerse en la sala inicial. La primera sala será solo una prueba de calibración; tras aprobar el método, se propagará por todas las categorías y salas con matriz de cobertura.
- El entorno de trabajo contiene la ROM base local de 8 MiB. La sonda de solo lectura confirmó código `AMTE`, título de cabecera `METROID4USA.`, checksum de cabecera `0x98` válido y SHA-256 `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.
- También están presentes localmente los prototipos v0.8, v0.9 visual y v1.0 urban opening. Sus hashes y los límites de conocimiento están en `ROM_VISUAL_COVERAGE.md`; no se publicó ningún binario en el repositorio.
- Se actualiza el agente para estudiar antes de actuar el **pasado** (versiones anteriores y errores), el **presente** (archivos y herramientas realmente accesibles) y el **futuro** (regresiones, compatibilidad, reversión y pruebas necesarias).
- Regla operativa: jamás decir que una aplicación se abrió o que el juego funciona sin evidencia. Distinguir archivos generados, validación estática, prueba en herramienta y prueba en juego.


## 2026-10-27 — Tarea 1: línea base visual

- Se identificó la ROM original recibida por tamaño, código `AMTE`, checksum de cabecera y SHA-256; la sonda GBA pasó 4/4 pruebas unitarias con fixtures sintéticos.
- Se compararon los hashes y diferencias byte a byte de las versiones v0.8, v0.9 visual y v1.0 Urban Opening frente a la base.
- Se auditaron los previews gráficos existentes y se distinguieron expresamente de capturas de juego ejecutado.
- Benchmark visual provisional seleccionado: `AREA_MAIN_DECK`, room index 1 (Docking Bays), por la disponibilidad del atlas BG3, preview CC0 y variante de paleta.
- No se modificó ningún archivo ROM ni recurso visual durante esta tarea. La captura original en emulador/MAGE queda pendiente porque esas herramientas no aparecieron en el PATH de esta sesión.
- Informe: [BASELINE_VISUAL_TAREA_01.md](BASELINE_VISUAL_TAREA_01.md).

## 2026-10-27 — identidad visual de los siete escenarios

- Se fijó como título oficial **LATINO AMÉRICA Zector Cero** y se organizó una primera familia visual de siete zonas diferenciadas.
- Se añadió el atlas editable [`assets/concept/latino-america-zector-cero-seven-scenarios.svg`](../../assets/concept/latino-america-zector-cero-seven-scenarios.svg), con las siete escenas conceptuales, dos paneles de sistema visual y una paleta provisional.
- Se añadió la guía [`SEVEN_SCENARIO_VISUAL_IDENTITIES.md`](SEVEN_SCENARIO_VISUAL_IDENTITIES.md), que define atmósfera, composición, paleta, elementos clave y función narrativa de cada zona.
- Las referencias consultadas respaldan rasgos generales de los callejones de El Caliche y las vías residenciales de La Francia Nueva; el resto de escenarios se etiqueta como composición creativa pendiente de referencias locales más concretas.
- Se enlazaron los nuevos artefactos desde el README y el estado de continuidad, y se sincronizaron los títulos de la Biblia Visual y del Plan Maestro.
- **Estado real:** documentación y atlas vectorial guardados en GitHub; el SVG pasó una comprobación estructural de etiquetas. El arte no se ha dividido en tiles nativos, no se ha integrado en la ROM y no se ha probado en emulador.
- Próximo paso: concretar la referencia técnica de cada zona y desglosar el escenario 1 en tiles originales manteniendo una copia intacta del recurso base.

## 2026-10-27 — Paso 2: descomposición del escenario 1

- Se creó `assets/tiles/scenario-01/scenario-01-villa-duarte-tiles.svg`: atlas editable de 256 × 256 px, con cuadrícula lógica de 8 × 8 (32 × 32 celdas) y regiones documentadas para fachadas, paredes gastadas, ventanas, puertas/persianas/rejas, letreros ficticios, toldos, vegetación, cableado, aceras, bordillo, cimiento, asfalto y objetos de calle.
- Se creó `scenario-01-layered-composition.svg`, con nueve capas editables: fondo, silueta urbana lejana, fachadas, aberturas, comercio, cableado/postes, vegetación, suelo y objetos/jugador de referencia.
- Se creó `scenario-01-native-preview.svg`, con coordenadas de composición de 240 × 160 y vista de lectura ampliada 4×; exportar a 240 × 160 para inspección nativa.
- Se añadió `tile-atlas-metadata.json` con paleta de 15 colores visibles más marcador de transparencia de la fuente, coordenadas de regiones y estados de validación; el catálogo explica que el marcador alfa no es directamente un índice de transparencia GBA para fondos.
- Validación estática realizada a través del contenido versionado: los tres SVG tienen etiquetas equilibradas; los colores visibles usados pertenecen a la paleta de trabajo; el JSON es válido y registra 1.024 celdas de 8 × 8 posibles.
- **Límite importante:** todavía no se ha probado el SVG en Inkscape u otro editor, no se han exportado/inspeccionado PNGs a escala nativa, no se ha contrastado con una captura ejecutada de la sala y no se ha modificado ni probado la ROM.
- Próximo paso: validar exportación y transparencia y cotejar el atlas con la sala real antes de intentar una integración ROM.
