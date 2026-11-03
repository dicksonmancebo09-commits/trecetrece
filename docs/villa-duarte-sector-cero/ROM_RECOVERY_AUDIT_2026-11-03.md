# Auditoría de recuperación y punto de partida real — 3 de noviembre de 2026

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Rama de trabajo:** `agent/rea-editable-analysis`  
**Objetivo:** dejar una base única, comprobada y sin bloqueos ficticios para continuar la producción.

## 1. Autorización para modificar la ROM

La transformación visual de toda la ROM está autorizada por el propio historial del proyecto. El PR [#7 — Autorizar transformación visual de toda la ROM y reforzar veracidad](https://github.com/dicksonmancebo09-commits/trecetrece/pull/7) se fusionó el **27-10-2026**. El agente vigente `.github/agents/metroid-re.agent.md` incluye el mandato explícito: la ROM completa puede modificarse cuando el usuario lo pide.

La regla «no modificar la ROM» que aparece en `recovery/analysis/REA_FULL_GAME_INVESTIGATION_PROMPT.md` pertenece únicamente a ese encargo de investigación REA de solo lectura. No es una regla general de producción y no invalida el PR #7 ni el mandato del agente.

## 2. Binarios recuperados y verificados

Los archivos se recuperaron de la Biblioteca de archivos de la conversación. No hace falta volver a pedirlos al usuario.

| Archivo | Tamaño | SHA-256 | Uso |
|---|---:|---|---|
| Metroid Fusion USA/Australia (base limpia) | 8.388.608 bytes | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` | Base maestra |
| `MetroidFusion_original_backup.gba` | 8.388.608 bytes | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` | Backup idéntico a la base |
| Zector Cero v1.7 Title/Hangar Fix | 8.388.608 bytes | `66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf` | Candidata de trabajo |
| `sector_cero_fase1_clean_base.gba` | 8.388.608 bytes | `b5a118eb4fc87988b521c2fe00df426d3dbdb2038d5367bbf498ed2bfa0dceee` | No es la base maestra; no intercambiar |

La candidata v1.8 se volvió a generar en una **copia nueva** a partir de v1.7. Cambió el campo de banco de paleta de 2 a 3 en las 1.536 entradas u16 de la tabla de metatiles de L01_R001, offset `0x7B0000`. Resultado estático: **1.536 bytes distintos**, tamaño 8 MiB, checksum de cabecera conservado y SHA-256 de salida `3bc764355012268d4ac6ef315bb9bb09ac0e5405d1c456bb506d1fdbe862af89`. Esta coincidencia reproduce el perfil v1.8 documentado en el repositorio. **No es una prueba en emulador.**

## 3. Extracción restaurada de las 382 salas

Se recuperó el artefacto de GitHub Actions `zector-cero-382-room-source-reference` (workflow run [41508555361](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41508555361), artifact ID `13171477787`). El paquete contiene `room-source-bundle.json`, `database.json` y los 382 archivos C fuente. Se verificó el hash de la base de datos y los hashes de los 382 archivos C frente al manifiesto.

Usando ese paquete y la ROM base exacta se regeneró el archivo privado de extracción:

- Salas: **382/382**.
- Capas RLE originales: **1.214/1.214**.
- Clipdata: **382**; BG1: **382**; BG2: **381**; BG0: **69**.
- Bytes comprimidos extraídos: **340.909**.
- Errores de decodificación: **0**.
- Rangos ROM solapados: **0**.
- Lotes: **87 + 87 + 87 + 87 + 34 = 382**.
- Comparación de los 1.214 rangos de capas originales contra v1.7: **0 capas con bytes distintos** en los offsets originales.

El ZIP resultante se conserva fuera del repositorio público porque contiene datos binarios derivados de la ROM. Archivo de esta sesión: `ZECTOR_CERO_382_ROOM_EXTRACTION_2026-11-03.zip`. SHA-256: `5663ef29ab795cc28737cab515c88b2dbe7ea785a1d49dc35354762cef13eb1f`. Incluye RLE, matrices U16LE, CSV por capa, resumen, tabla estructural y reporte de extracción. **La extracción se hizo; no hay que volver a pedir la ROM ni repetirla.**

## 4. Qué ya existe en GitHub

- 382 IDs y cinco lotes reconciliados.
- 382 fichas técnicas con metadatos de referencia.
- Grafo de puertas de referencia: 898 puertas, 34 enlaces inter-área y 60 variantes por evento; 958 aristas contando valores por defecto y overrides.
- 2.150 posiciones de sprites de referencia distribuidas por las 382 salas.
- Siete atlas de barrio exportados a PNG indexado, 4bpp, BGR555 y LZ77.
- Scripts de auditoría, extracción, exportación de atlas, render estático de L01_R001 y parche de banco de paleta.
- GitHub Actions recientes exitosos: run [41616637611](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41616637611) para exportaciones de atlas y run [41616423466](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41616423466) para instalación/validación de herramientas y tests.

Los conteos de posiciones de sprites son coordenadas/registros fuente, no sprites originales redibujados. Los siete atlas son bibliotecas de arte por barrio, no 382 composiciones de sala terminadas.

## 5. Qué falta de verdad para terminar el juego

Los datos base existen. Lo que falta es convertirlos en contenido jugable e integrarlo:

1. **Composición de las salas:** construir los tilemaps originales para las 382 salas a partir de los siete atlas y las dimensiones/mapas extraídos. Los mapas originales extraídos son referencia estructural; no son todavía las composiciones urbanas finales. Estado de tilemaps urbanos finales: **0/382**.
2. **Colisiones adaptadas:** usar las matrices de clipdata extraídas y crear/revisar las colisiones correspondientes al diseño nuevo. La extracción del clipdata original está hecha; las colisiones urbanas adaptadas y verificadas siguen pendientes: **0/382**.
3. **Puertas y progresión:** convertir el grafo de referencia en rutas de juego del nuevo trazado; definir qué puertas, condiciones y eventos cambian y probar que no haya salas aisladas ni bloqueos.
4. **Sprites y entidades:** las posiciones están inventariadas, pero falta transformar e integrar gráficamente protagonista, animaciones, enemigos, jefes, proyectiles, objetos y efectos.
5. **HUD y pantallas:** completar título/menús, mapa, pausa, indicadores, mensajes y demás interfaces que deban adoptar la identidad del juego.
6. **Constructor de ROM por lotes:** ampliar el flujo de parcheo de la sala inicial a recursos compartidos y salas múltiples, con hashes, comprobación de punteros, rangos, compresión, paletas y generación reproducible. El parche v1.8 solo corrige L01_R001; no es un integrador de 382 salas.
7. **Prueba runtime:** ejecutar la candidata en mGBA/MAGE y revisar arranque, movimiento, colisiones, puertas, animaciones, eventos, guardado y transiciones.

## 6. Qué impide la prueba desde esta sesión

- Python y los binarios de ROM están disponibles aquí; se han ejecutado auditorías y una edición binaria estática real.
- En este entorno no hay ejecutables `mGBA`, `Ghidra`/headless ni `MAGE`; tampoco hay acceso de terminal a un Codespace ya abierto.
- GitHub Actions sí instala mGBA en un runner efímero, pero los workflows actuales no cargan la ROM privada ni muestran una sesión de juego. Un job verde de instalación/tests no prueba gameplay.
- Ghidra/REA son necesarios para reconstruir o alterar lógica ARM/Thumb no documentada; **no son requisito para continuar la producción de mapas/tiles/sprites con los datos ya extraídos**.

El bloqueo operativo restante es el acceso a un emulador/editor ejecutable para validar visualmente y depurar el juego, no la falta de autorización, ROM base, registro de salas o referencias de recursos.

## 7. Regla de continuidad

No volver a solicitar la ROM base, v1.7 ni el paquete fuente de 382 salas: ya se recuperaron y se verificaron en esta sesión. No repetir la auditoría de IDs, las fichas técnicas, el crosswalk ni la extracción RLE salvo que cambie el hash de entrada. Continuar desde la fase de composición urbana por sala e integración por lotes, manteniendo el trabajo en `agent/rea-editable-analysis`.
