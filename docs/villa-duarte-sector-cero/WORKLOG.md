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

## 2026-10-27 — Escenario 2: Callejones del Caliche

- Referencias de observación revisadas: [Hoy — El Caliche de Villa Duarte](https://hoy.com.do/el-pais/el-caliche-de-villa-duarte-la-otra-cara-del-crecimiento-economico_762790.html) y [Diario Libre — Fundación busca fondos para transformar El Caliche](https://www.diariolibre.com/actualidad/ciudad/fundacion-busca-fondos-para-transformar-el-sector-el-caliche-de-villa-duarte-MG11174899). Se usan para estudiar callejón, escala de fachadas, rejas, pintura y pavimento; no se incrustan ni copian imágenes periodísticas.
- Se creó el atlas `assets/tiles/scenario-02/scenario-02-el-caliche-tiles.svg` (256 × 256, rejilla 8 × 8), con 15 colores visibles y regiones para paredes, ventanas, puertas, rejas, aleros, parches de pintura, bajantes, cables, suelo y props.
- Se creó `scenario-02-layered-composition.svg` con 11 capas; `scenario-02-native-preview.svg`; `tile-atlas-metadata.json`; y el catálogo `README.md` dentro de `assets/tiles/scenario-02/`.
- Exportaciones PNG creadas y subidas mediante Git Data API: `scenario-02-el-caliche-tiles.png` (256 × 256, modo indexado, 16 entradas de paleta incluyendo marcador alfa) y `scenario-02-native-preview.png` (240 × 160, modo indexado, 15 colores).
- Comprobación estática: los SVG están equilibrados estructuralmente; se comprobó el tamaño exacto de ambas exportaciones y que no aparecen colores fuera de la paleta de trabajo. Los PNG se verificaron por tamaño, modo, conteo de color y alfa.
- **Estado real:** concepto/atlas modular editable guardado en GitHub y exportaciones rasterizadas verificadas. No se ha probado el archivo en un editor gráfico, no se ha adaptado a paletas/tilemaps de la ROM y no hay prueba en motor ni emulador. No se modificó la ROM.
- Próximo trabajo creativo: escenario 3 — Calle Residencial, con referencias específicas de La Francia Nueva. Mantener la validación de ROM como una fase técnica aparte.

## 2026-10-27 — Localización caribeña antes de probar la ROM

- La inspección del árbol público de `main` no encontró archivos de diálogo ni una tabla de traducción activa vinculada a la ROM. No se puede afirmar que el texto actualmente mostrado por la ROM haya sido revisado o modificado por esta tarea.
- Se creó `localization/es-419/VOICE_AND_SLANG_GUIDE.md`: voz dominicana como base y perfiles de habla separados para Cuba, Puerto Rico y Jamaica; México, Colombia y Argentina como cameos opcionales. El Patois/Patwa se trata como variedad criolla con contexto propio, no como español mal pronunciado.
- Se creó `localization/es-419/dialogue.json` con 27 entradas de diálogo original distribuidas entre siete escenarios, 81 líneas con saltos manuales y 10 cadenas UI sin jerga. Se marca expresamente `draft-not-in-ROM`.
- Se creó `localization/es-419/glossary.json` con 35 entradas regionales y referencias de consulta; y `localization/es-419/README.md` con el flujo de integración.
- Se añadió el validador `tools/check_localization_es419.py` y `tests/test_localization_es419.py`. Ejecutados en una copia de trabajo descargada de GitHub: validador OK, 27 entradas, 81 líneas dentro del límite editorial provisional de 28 caracteres, 3 pruebas unitarias aprobadas.
- Se actualizó el agente `.github/agents/metroid-re.agent.md` para exigir una auditoría de localización antes de cualquier prueba de ROM presentada como validación de texto.
- **Estado:** paquete textual original y pruebas estáticas versionados. No se ha inyectado texto ni se ha probado la ROM. Pendiente identificar el texto traducido real, su encoding, tabla de caracteres, compresión, terminadores, punteros y límites de caja antes de adaptar nada.

### Fuentes usadas para guía lingüística
- Academia Dominicana de la Lengua: https://academia.org.do/2016/06/02/el-diccionario-fraseologico-del-espanol-dominicano/
- Visit Jamaica, Patois: https://www.visitjamaica.com/discover-jamaica/people-heritage/language/
- UC3M, guía de Puerto Rico: https://www.uc3m.es/secretaria-virtual/media/secretaria-virtual/doc/archivo/doc_mne_puerto-rico_mayaguez_guia/manual-para-estudiantes-visitantes.pdf
- Cuban Spanish Academy: https://www.cubanspanishclasses.com/es/common-cuban-phrases/
- Academia Mexicana de la Lengua: https://academia.org.mx/consultas/consultas-frecuentes/item/no-mames
- Diccionario de Jergas de Habla Hispana: https://www.jergasdehablahispana.org/

## 2026-10-27 — Prueba 01 del prototipo ROM v1.0

- Se recuperaron de la biblioteca del usuario la ROM base `MetroidFusion_original_backup.gba`, el prototipo archivado `Villa_Duarte_Sector_Cero_v1.0_URBAN_OPENING.gba`, el parche `Villa_Duarte_Sector_Cero_v1.0_full.ips` y la reconstrucción de sala para referencia.
- Se aplicó el IPS de forma estática a la base de 8 MiB: 7.892 registros; 59.501 bytes distintos de la ROM base; salida de 8.388.608 bytes. El SHA-256 de salida `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5` coincide exactamente con el prototipo archivado. Se conserva código GBA `AMTE`, título de cabecera `METROID4USA` y checksum de cabecera `0x98`.
- Se guardó una versión optimizada del arte de sala como `assets/test-builds/test-01/v1.0-urban-opening-room-reconstruction.png` y se documentó el resultado en `TEST_01_ROM_INTEGRITY.md`.
- **No se ejecutó la ROM en mGBA/MAGE.** La imagen es una reconstrucción de sala a partir del mapa, no una captura de emulador. El paquete de descarga para el usuario contiene el IPS y la vista; no contiene la ROM completa y el IPS no se publica en el repositorio público.
- Esta build v1.0 es un prototipo previo y no contiene los nuevos escenarios 1/2 ni el paquete es-419. La prueba de ROM en ejecución sigue pendiente.

## 2026-10-27 — Candidata v1.1 QA Viewer

- Generada una ROM privada de 16 MiB basada en Urban Opening v1.0, con un visor de arranque para revisar dos escenas originales a resolución GBA.
- Controles declarados: L = Escenario 1, R = Escenario 2, START = intentar continuar al punto de entrada original v1.0.
- Verificación estática: dirección de entrada 0x08800000; dos frames de 76.800 bytes en BGR555; checksum de cabecera 0x98; el parche BPS vuelve a producir la ROM candidata byte por byte.
- Estado: **no probado en emulador**. No confundir este visor con la integración de los tilesets en los mapas reales o la inserción del paquete de diálogos en la rutina de texto.
- Entrega privada; no se publican ROM ni parche binario en este repositorio. Ver [QA_VIEWER_V1_1.md](QA_VIEWER_V1_1.md).

## 2026-10-27 — v1.2 Real Title Reskin

- Corregido el enfoque anterior: la QA Viewer v1.1 no se considera build de prueba válida.
- Se sustituyeron los recursos reales de fondo, logo y objetos de la pantalla de título dentro de la ROM; se actualizó el identificador de cabecera.
- Verificación estática: LZ77 round-trip, límites de recursos, checksum GBA y reaplicación de BPS. Emulador pendiente.
- La v1.2 mantiene los datos de reskin de la sala 0 agregados por la v1.0, pero no declara su apariencia probada en juego.
- Resto del juego sigue pendiente de reskin integral.

## 2026-10-27 — v1.3, título real + primer escenario

- Rehecha la tabla de metatiles y los mapas BG1/BG2 que cargan realmente Main Deck, sala 0; ya no se confía en el atlas urbano aislado con el mapeo de tiles original.
- Se usa el área de datos redirigida por los punteros de v1.0. El clipdata/collision map y el código de arranque se preservan.
- La reconstrucción gráfica procede de los datos escritos en la ROM; no es captura de emulador.
- Pendiente: prueba real en mGBA/MAGE y conversión de los otros mapas, player/enemigos, HUD, cinemáticas y diálogos.

## 2026-10-27 — Auditoría posterior a v1.3 tras reporte de crash

- El usuario reportó pantalla de título ilegible y bloqueo/crash. Se retira v1.3 como build funcional.
- Fallo visual demostrado: el tilemap de título usa banco de paleta 0, pero el código original carga la paleta de fondo en `PALRAM_BASE + 0x100` (bancos 8–15). La reconstrucción anterior usó incorrectamente la paleta como si empezara en el banco 0.
- Rectificación: las referencias a `0x087B0000`, `0x087B2000` y `0x087B2400` sí existen en la ROM; no es correcto afirmar que los nuevos mapas estaban desconectados.
- Las comprobaciones estáticas de tileset/table/RLE pasan, pero no demuestran que la ROM funcione. El crash aún no se ha reproducido en emulador y no se asigna una causa sin evidencia.
- Acción para la siguiente versión: corregir banco de paleta y hacer pruebas de aislamiento título/sala con mGBA/MAGE antes de entregar otra ROM. Ver [POSTMORTEM_V1_3.md](POSTMORTEM_V1_3.md).
