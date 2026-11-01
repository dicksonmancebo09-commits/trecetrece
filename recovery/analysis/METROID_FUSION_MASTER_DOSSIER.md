# Expediente maestro de Metroid Fusion — investigación integral con REA

**Estado:** recopilatorio técnico inicial; la investigación REA exhaustiva todavía no se ha ejecutado sobre el Codespace del usuario.  
**ROM objetivo:** Metroid Fusion USA/Australia, código GBA `AMTE`.  
**Objetivo:** documentar de forma trazable el código, los datos, los sistemas y los recursos de la ROM para convertirla en una base técnicamente comprensible y editable para LATINO AMÉRICA Zector Cero.

> Este expediente separa cuatro fuentes: (1) observaciones de la ROM exacta, (2) resultados heurísticos de los scripts del proyecto, (3) referencias de la descompilación comunitaria y (4) conclusiones pendientes de REA/Ghidra/mGBA. No se debe convertir una referencia comunitaria en una afirmación sobre la ROM sin corroborar dirección, bytes y comportamiento.

---

## 1. Identidad de la ROM bajo estudio

| Campo | Valor registrado |
|---|---|
| Título de cabecera | `METROID4USA` |
| Código GBA | `AMTE` |
| Tamaño | 8.388.608 bytes (8 MiB) |
| SHA-256 | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` |
| SHA-1 | `ca33f4348c2c05dd330d37b97e2c5a69531dfe87` |
| Complemento de checksum | `0x98`, válido en la copia analizada |
| Entrada GBA | offset `0x000000`, dirección `0x08000000` |
| Instrucción inicial | `0xEA00002E`, salto ARM hacia `0x080000C0` |
| Entrada Thumb observada | puntero `0x08000231`, código alineado en `0x08000230` |

**Regla de identidad:** no aplicar offsets ni conclusiones de este expediente a una ROM de hash diferente sin repetir la identificación y las comprobaciones.

## 2. Estado real del trabajo

| Área | Evidencia actual | Estado |
|---|---|---|
| Identidad/cabecera | Hash, tamaño, cabecera y salto de entrada comprobados | Comprobado estáticamente |
| Arranque ARM/Thumb | Modelo parcial de inicialización y dirección de entrada Thumb | Observado parcialmente |
| Bucle principal | Resumen de flujo por frame derivado de la inspección estática y referencia C | Parcial; no reconstruido instrucción por instrucción |
| Tabla de modos | 15 destinos observados en offset `0x278` | Comprobado estáticamente |
| Código completo de cada modo | No reconstruido | Pendiente |
| Física/movimiento de Samus | Referencias en el proyecto decomp; no enlazadas exhaustivamente con la ROM usando REA | Pendiente |
| Salas, mapas y puertas | Candidatos y recursos nombrados; la totalidad no está verificada | Parcial |
| Enemigos/IA/jefes | Referencias comunitarias; falta mapa completo de dirección/bytes/funciones | Pendiente |
| Escenas y eventos | Flujo de nueva partida y recursos del hangar documentados por referencia | Parcial |
| Audio/música | Archivos de referencia; falta correlación completa con la ROM | Pendiente |
| Texto/localización | Recursos gráficos de texto nombrados parcialmente; falta tabla completa y punteros | Pendiente |
| Guardado/SRAM | Referencias de fuente disponibles; el flujo de la ROM objetivo no está auditado completamente | Pendiente |
| Descompilación REA de la ROM | No hay informe REA completo ejecutado/inspeccionado en esta conversación | Pendiente |
| Validación de juego completa | No existe evidencia de gameplay completo | No certificada |

## 3. Arranque y flujo global observado

### 3.1 Entrada y cambio de estado de CPU

- La primera palabra en `0x08000000` es una rama ARM que lleva a `0x080000C0`.
- El bootstrap observado configura pilas para IRQ/Sistema y coloca el handler de interrupción en RAM `0x03007FFC`.
- La transferencia por BX usa el puntero `0x08000231`, que indica ejecución Thumb en `0x08000230`.
- El modo principal se lee desde RAM `0x03000BDE`.
- La tabla de 15 destinos está en offset ROM `0x278`.

### 3.2 Tabla de modos de alto nivel

| ID | Etiqueta de trabajo | Destino ROM |
|---:|---|---:|
| 0 | TITLE | `0x080002B4` |
| 1 | IN_GAME | `0x08000448` |
| 2 | SOFT_RESET | `0x08000548` |
| 3 | MAP_SCREEN | `0x080004D0` |
| 4 | CUTSCENE | `0x0800054E` |
| 5 | SA_X_CLOSE_UP | `0x080005D0` |
| 6 | ERASE_SRAM_MENU | `0x080005E4` |
| 7 | FILE_SELECT_OR_INTRO | `0x080003AC` |
| 8 | GAME_OVER | `0x08000624` |
| 9 | ENDING | `0x0800069C` |
| 10 | DIED_FROM_SR388_COLLISION | `0x080006B0` |
| 11 | CREDITS | `0x080006D0` |
| 12 | DEMO | `0x080006E4` |
| 13 | UNKNOWN | `0x08000730` |
| 14 | DEBUG | `0x0800074C` |

Las etiquetas son nombres descriptivos de trabajo contrastados con la referencia de código; no son símbolos originales recuperados de la ROM. Las rutinas completas y sus transiciones aún requieren análisis por función.

### 3.3 Resumen provisional del frame

El resumen actual propone esta secuencia: limpieza de estado por frame, actualización de audio, comprobación de reinicio, lectura de entradas, incremento de contadores, lectura/despacho del modo principal y espera de VBlank. Debe tratarse como mapa de investigación hasta que REA/Ghidra y la traza del emulador la confirmen paso a paso.

## 4. Arquitectura del juego que debe recopilarse

La siguiente matriz es el índice de trabajo completo. Cada subsistema requiere: direcciones de función, pseudocódigo, ensamblador, callers/callees, estructuras de datos, recursos asociados, evidencia de ejecución, confianza y preguntas abiertas.

| Subsistema | Qué debe documentarse | Referencias de código externas útiles | Cobertura de la ROM objetivo |
|---|---|---|---|
| Arranque/AGB main | reset, stacks, IRQ, VBlank, inicialización HW | `src/agbmain.c`, `asm/crt0.s`, `asm/intr_main.s` | Parcial |
| Bucle principal/modos | frame loop, estado global, dispatch, reset | `src/agbmain.c`, `src/softreset.c` | Dispatch observado; lógica pendiente |
| Entrada/control | lectura de botones, debounce y acciones | `src/update_input.c`, `src/process_pause_press.c` | Pendiente |
| Samus | estados, animación, movimiento y habilidades | `src/samus.c`, `src/data/samus*` | Pendiente |
| Física | aceleración, velocidad, salto, gravedad, fricción | `src/samus.c`, `src/fixed_point.c` | Pendiente |
| Colisiones/clipdata | suelo, paredes, techos, daño, bloques | `src/bg_clip.c`, `src/clipdata.c`, `src/block.c` | Pendiente |
| Salas/cámara | carga de sala, scroll, conexiones, transiciones | `src/room.c`, `src/connection.c`, `src/scroll.c` | Parcial por datos |
| Eventos/progresión | flags, triggers, objetivos, secuencias | `src/event.c`, `src/event_checks.c`, `src/data/event_data.c` | Pendiente |
| Puertas/elevadores/estaciones | lógica y datos de puertas, pads, conexiones | `src/connection.c`, `src/data/sprites/gate.c`, datos de sprites | Pendiente |
| Enemigos/IA | instancias, estados, detección, ataque, daño y muerte | `src/sprites_AI/*.c`, `src/data/sprites/*.c` | Pendiente |
| Jefes | fases, patrones, vulnerabilidad, transiciones | IA de Arachnus, Serris, Nightmare, Yakuza, Zazabi, Ridley, Omega Metroid y otros | Pendiente |
| SA-X | apariciones, persecución, combate, escenas y formas | `src/sa_x.c`, `src/sa_x_close_up.c`, `src/sprites_AI/sa_x*.c` | Parcial por modos |
| Parásito X | spawn, absorción, drops, transformación | `src/x_parasite_util.c`, `src/sprites_AI/x_parasite.c` | Pendiente |
| Proyectiles/armas | disparo, misiles, bombas, haces, colisiones | `src/projectile.c`, `src/data/projectile_data.c` | Pendiente |
| Partículas/efectos | explosiones, humo, debris, screen shake y haze | `src/particle.c`, `src/sprite_debris.c`, `src/haze.c` | Pendiente |
| HUD/minimapa/mapa | energía, misiles, mapas, iconos, áreas | `src/hud.c`, `src/minimap.c`, `src/menus/pause_screen_map.c` | Pendiente |
| Menús/UI | título, selección, pausa, mapa, estado, borrado SRAM | `src/menus/title_screen.c`, `src/menus/pause_screen.c`, `src/status_screen.c` | Recursos parciales |
| Intro/cinemáticas | nueva partida, BSL, escenas y transiciones | `src/new_file_intro.c`, `src/title_intro.c`, `src/data/intro_data.c` | Hangar parcial |
| Demo/final/créditos | demo, final, escape y créditos | `src/demo.c`, `src/ending.c`, `src/escape.c` | Modos observados |
| Texto | strings, encoding, fuentes, punteros y ventanas | `src/text.c`, `src/location_text.c`, `src/data/text_data.c` | Pendiente |
| Audio/música | secuencias, SFX, drivers, tablas y eventos | `src/audio.c`, `src/music_wrappers.c`, `src/data/music_track_data.c` | Pendiente |
| SRAM/guardado | formato, slots, flags, checksums y resets | `src/sram/sram.c`, `src/sram_misc.c` | Pendiente |
| Gráficos/paletas | LZ77, tiles 4bpp, tilemaps, OAM, animaciones | `src/animated_graphics.c`, `src/animated_palette.c`, `src/data/tilesets/*` | Inventario heurístico parcial |
| DMA/display | VRAM, PALRAM, OAM, registers, fades y VBlank | `src/dma.c`, `src/display.c`, `src/color_effects.c` | Pendiente |

## 5. Cobertura de datos de la referencia comunitaria

La referencia pública `metroidret/mf` permite clasificar áreas que conviene inspeccionar. Las cantidades siguientes son conteos de archivos del árbol fuente consultado, **no resultados del análisis REA de la ROM del usuario ni conteos certificados de salas/entidades únicas**.

| Elemento de la referencia | Cantidad de archivos | Observación |
|---|---:|---|
| Archivos `.c` del árbol | 704 | Incluyen lógica y datos |
| Archivos `.h` bajo `include/` | 391 | Tipos, constantes, datos y declaraciones |
| Archivos de sala numerados | 382 | Main Deck y sectores 1–6 |
| Main Deck | 87 | Archivos de sala |
| Sector 1 | 54 | Archivos de sala |
| Sector 2 | 61 | Archivos de sala |
| Sector 3 | 39 | Archivos de sala |
| Sector 4 | 48 | Archivos de sala |
| Sector 5 | 52 | Archivos de sala |
| Sector 6 | 41 | Archivos de sala |
| Recursos de datos de sprites | 94 | `src/data/sprites/` |
| Módulos de IA de sprites | 105 | `src/sprites_AI/` |
| Archivos ensamblador | 11 | `asm/*.s` |

Esta estructura externa es un índice de consulta. Hay que verificar que cada nombre, dirección y formato corresponda a la ROM exacta por medio de offsets, hashes, referencias y pruebas.

## 6. Inventario estructural de la ROM objetivo ya registrado

El barrido estático completo existente analizó 8 MiB y registró:

- 55.984 palabras alineadas de 32 bits cuyo valor cae dentro de la ventana de ROM; 30.898 destinos únicos. Pueden existir coincidencias falsas.
- 464 streams LZ77 con decodificación completa, probando inicios alineados a 2 y 4 bytes.
- 386 de esos streams con al menos una referencia exacta entre las palabras-puntero escaneadas.
- 35.295 segmentos ASCII imprimibles de seis bytes o más, conteo mecánico que incluye falsos positivos.
- Entropía medida por bloques de 64 KiB.
- Relleno final `0xFF` desde offset `0x79ECC8`, con 398.136 bytes.

**No mezclar cifras de inventarios hechos con filtros diferentes.** El resumen antiguo de `rom_inventory.json` registra 468 candidatos LZ77 con salida mínima de `0x800` y 9.826 segmentos ASCII; el barrido de octubre utiliza criterios distintos. Ambos son métricas heurísticas, no un inventario definitivo.

## 7. Recursos con nombre ya cruzados

El crosswalk de 2026-10-28 comparó 158 candidatos prioritarios (referenciados por puntero y con al menos 8 KiB de salida descomprimida) contra `database.json` de la referencia US:

- 133 offsets coincidieron exactamente con un nombre de recurso del manifiesto.
- 25 offsets quedaron sin resolver.
- Coincidencias por grupo: 84 tilesets, 22 recursos de nueva partida/intro, 17 de final, 7 de menús y algunos blobs/escenas adicionales.

Ejemplos útiles:

| Offset | Recurso nombrado en el manifiesto |
|---|---|
| `0x3EF960` | `tilesets/0_bg.gfx.lz` |
| `0x3F6C34` | `tilesets/19.gfx.lz` |
| `0x42011C` | `tilesets/16.gfx.lz` |
| `0x590C9C` | `menus/title_screen/objects.gfx.lz` |
| `0x593274` | `menus/title_screen/logo.gfx.lz` |
| `0x605D08` | `menus/title_screen/space_background.gfx.lz` |
| `0x56A254` | `menus/pause_screen/bg.gfx.lz` |
| `0x56F71C` | `menus/pause_screen/obj.gfx.lz` |
| `0x59DB08` | `new_file_intro/hornoad_encounter_obj.gfx.lz` |
| `0x5A44CC` | `new_file_intro/hornoad_encounter_bg.gfx.lz` |
| `0x72F2E0` | `sa_x_close_up/graphics.gfx.lz` |
| `0x74EB50` | `ending/space_bg.gfx.lz` |
| `0x7944E4` | `ending/results_english_text.gfx.lz` |
| `0x797D08` | `ending/results_spanish_text.gfx.lz` |

**Qué demuestra:** el manifiesto público asigna esos offsets exactos a dichas rutas de extracción.  
**Qué no demuestra:** qué rutina consume el recurso, su paleta/tilemap real, su aparición en juego ni que pueda reemplazarse sin consecuencias.

## 8. Escena del hangar BSL: caso de estudio ya documentado

La referencia de código describe `NewFileIntroHandler()` con estados de 0 a 12. El estado 11 ejecuta `NewFileIntroLandingOnBsl()`, la escena del aterrizaje en el hangar.

| Offset | Recurso |
|---|---|
| `0x5F7190` | `landing_on_bsl_bg.gfx.lz` |
| `0x5FAB54` | `landing_on_bsl_obj.gfx.lz` |
| `0x5FF708` | paleta del fondo |
| `0x5FFD08` | paleta de objetos |
| `0x5FFF08` | tilemap del espacio |
| `0x60030C` | tilemap del hangar |
| `0x598898` | tilemap de texto compartido |

La inicialización de referencia carga los gráficos en VRAM de fondos/objetos, paletas en PALRAM y mapas en direcciones concretas de VRAM. El parche experimental de una instrucción que apunta al estado 11 se generó y pasó verificaciones estáticas, pero la sesión mGBA registrada no tiene evidencia visual utilizable: las imágenes capturadas eran del escritorio/barra de tareas. Por ello, **la escena del hangar no está validada**.

## 9. Cómo utilizar REA de forma correcta para esta ROM

### 9.1 Estado del entorno del proyecto

El script `tools/install_ai_stack.sh` instala `rea-agents@6.8.0`, pero instalar REA no instala automáticamente Ghidra. Antes de analizar hay que comprobar:

```bash
rea --version --json
rea doctor --json
rea providers --json
rea capabilities --json
```

No considerar que el proveedor está disponible hasta que `rea providers` lo confirme. La configuración documentada por REA para Ghidra requiere una instalación local de Ghidra 12.1.x y JDK 21 de 64 bits. La instalación debe confirmarse con `rea doctor` y `rea providers`.

### 9.2 Prueba raw-binary: solo triage

El script del proyecto `recovery/scripts/run_rea_analysis.sh` conserva hashes, identidad y preflight y llama a REA con:

```bash
rea inspect "$ROM" \
  --target-format raw-binary \
  --architecture arm \
  --entry-point 0x08000000 \
  --provider ghidra \
  --json
```

Esto proporciona una primera inspección A32 con mapeo de ROM. **No es una descompilación completa de GBA.** La documentación actual de REA indica que la familia ARM genérica utiliza `ARM:LE:32:v7`, empieza en estado ARM y no admite imágenes exclusivamente Thumb; GBA requiere ARM7TDMI/ARMv4T y mezcla instrucciones ARM y Thumb. Por tanto:
- conservar el resultado como triage preliminar;
- no etiquetar el firmware entero en A32 como funciones válidas;
- contrastar funciones/bytes que cambian de estado ARM/Thumb;
- para reconstrucción precisa de GBA, importar la ROM en Ghidra como Raw Binary, base `0x08000000`, little-endian, lenguaje `ARM:LE:32:v4t`, y seguir explícitamente las transiciones ARM/Thumb;
- usar REA para buscar, documentar y recorrer funciones/calls/xrefs donde su provider ofrezca evidencia válida.

### 9.3 Investigación de funciones y relaciones

Con el provider activo y la ROM abierta, el agente debe:
1. obtener el overview y el inventario de funciones;
2. identificar una función de entrada o un rango observado;
3. consultar nombre/símbolos/strings y sus xrefs;
4. obtener callers, callees y call graph;
5. solicitar pseudocódigo y ensamblador para funciones concretas;
6. guardar cada resultado como Evidence, incluyendo hash, offset, dirección, proveedor, lenguaje, fecha, evidencia y dudas;
7. no generar pseudocódigo para direcciones adivinadas;
8. repetir por subsistema y enlazar dependencias sin mezclar hallazgos de versiones diferentes.

Comandos de referencia de la CLI actual (repetir los flags raw en cada consulta cuando el target es raw-binary):

```bash
rea function "$ROM" 0x08000000 --target-format raw-binary --architecture arm --entry-point 0x08000000 --provider ghidra --json
rea decompile "$ROM" 0x080000C0 --target-format raw-binary --architecture arm --entry-point 0x08000000 --provider ghidra --json
rea xrefs "$ROM" 0x08000230 --target-format raw-binary --architecture arm --entry-point 0x08000000 --provider ghidra --json
rea search "$ROM" "NewFileIntro" --provider ghidra --json
```

Los selectores exactos y flags se deben verificar con `rea <comando> --help` en la versión instalada. El agente REA/MCP puede usar las operaciones nativas de sesión (overview, functions, pseudocode, assembly, callers/callees, references y batch decompilation) cuando estén disponibles.

### 9.4 No existe un único comando de “descompilar todo”

El trabajo debe ser por lotes y con control de tamaño:
- primero funciones de arranque, dispatcher y frame loop;
- luego input, Samus, física y colisiones;
- luego rooms, doors, scroll, maps y events;
- luego cada familia de sprites y bosses;
- después armas/proyectiles/efectos, HUD/menus, escenas, audio, texto y SRAM;
- al final, grafo de dependencias, referencias huérfanas y cobertura de datos.

La descompilación devuelve pseudocódigo y estructuras inferidas, no el código fuente original exacto.

## 10. Protocolo de trabajo exhaustivo por subsistema

Para cada subsistema se crea una ficha con estos campos obligatorios:

1. ID y nombre de subsistema.
2. Hash de la ROM y versión.
3. Dirección virtual y offset de archivo de cada función.
4. Arquitectura/estado de instrucciones (ARM o Thumb), lenguaje Ghidra y provider REA.
5. Bytes/rango real de la función y rango de cuerpo observado.
6. Pseudocódigo y ensamblador con referencias de Evidence.
7. Callers, callees, xrefs y datos/estructuras accedidas.
8. Strings, tablas, punteros y recursos que utiliza.
9. Sala/evento/enemigo donde se observa.
10. Captura/log de mGBA o debugger cuando aplique.
11. Confianza: confirmada, alta, media, baja o no resuelta.
12. Preguntas abiertas y prueba siguiente.
13. Riesgo de editar y dependencias compartidas.
14. Estado: descubierto, mapeado, entendido, correlacionado, validado en ejecución.

### Orden sugerido

| Fase | Contenido | Salida |
|---|---|---|
| 0 | Identidad ROM, Node, REA, Ghidra, provider y hashes | Preflight |
| 1 | Entrada, bootstrap, IRQ, VBlank y salto ARM/Thumb | Mapa de arranque |
| 2 | Main loop, modos, reset y estados generales | Call graph principal |
| 3 | Input, Samus, animaciones y física | Fichas de jugador |
| 4 | Clipdata, bloques, colisiones, salas, puertas, scroll y mapa | Catálogo de salas/transiciones |
| 5 | Sprites y AI de enemigos comunes | Catálogo por especie/estado |
| 6 | Jefes, SA-X y parásito X | Fichas de combate/encuentros |
| 7 | Haces, misiles, bombas, objetos, pickups y efectos | Matriz de recursos y lógica |
| 8 | Intro, eventos, narrativa, texto, pantallas y final | Fichas de secuencias |
| 9 | Audio, SFX, música y SRAM | Subsistemas de soporte |
| 10 | Grafo global, llamadas sin resolver, punteros y datos | Dossier consolidado |
| 11 | Comparación en mGBA con escenarios reproducibles | Evidencia dinámica |
| 12 | Matriz de cobertura y backlog de edición | Informe final |

## 11. Formato del registro REA

Cada lote produce archivos bajo `private-roms/rea-analysis/` (excluidos de Git). No subir la ROM ni dumps extraídos al repositorio público.

Estructura sugerida:

```text
private-roms/rea-analysis/
  identity/
  rea-preflight/
  evidence/
    boot/
    dispatcher/
    gameplay/
    rooms/
    sprites/
    bosses/
    events/
    ui-text/
    audio/
    sram/
  pseudocode/
  assembly/
  callgraphs/
  resources/
  coverage/
  unresolved/
  final/
```

Los documentos que no contengan bytes propietarios ni dumps pueden resumirse luego en `recovery/analysis/` y versionarse. Los resultados completos y binarios permanecen privados.

## 12. Criterios para declarar la recopilación completa

No declarar “recopilación completa” hasta cumplir todo lo siguiente:

- cada función detectada tiene clasificación: código, thunk, wrapper, datos, tabla, relleno o desconocida;
- la cobertura de funciones se calcula con un denominador documentado;
- cada modo principal tiene su flujo y dependencias;
- cada sistema de gameplay tiene funciones y estructuras asignadas;
- cada sala tiene ID, región, mapa, clipdata, conexiones y eventos;
- los recursos gráficos se correlacionan con punteros/cargadores y paletas;
- las familias de enemigos y jefes tienen sus funciones, estados y datos;
- texto, audio, SRAM, UI y escenas tienen rutas o límites documentados;
- las zonas ARM/Thumb se separan y la arquitectura correcta se comprueba;
- las discrepancias con la descompilación pública están registradas;
- se distinguen pseudocódigo estático y comportamiento observado en ejecución;
- toda incertidumbre queda documentada, no se rellena con suposiciones.

La cobertura puede ser completa como **índice de investigación** aunque queden funciones sin resolver, siempre que esos huecos aparezcan explícitamente. No puede llamarse descompilación completa si quedan rangos desconocidos sin clasificar.

## 13. Archivos del proyecto que forman la base actual

- `recovery/analysis/full_rom_static_scan_2026-10-28.md` y `.json`: barrido estático de los 8 MiB.
- `recovery/analysis/lz77_priority_queue_2026-10-28.md`: candidatos priorizados.
- `recovery/analysis/lz77_named_asset_crosswalk_2026-10-28.md` y `.json`: 158 candidatos, 133 matches exactos.
- `recovery/analysis/hangar_scene_resource_map_2026-10-28.md` y `.json`: flujo/recursos del hangar.
- `recovery/analysis/game_flow_overview.md`: mapa provisional del frame loop y modos.
- `recovery/src/reconstructed/boot_init.c`: observaciones del bootstrap.
- `recovery/src/reconstructed/game_mode_dispatch.c/.h`: tabla observada de modos.
- `recovery/scripts/run_rea_analysis.sh`: preflight e inspección preliminar REA.
- `recovery/scripts/catalog_lz77_assets.py`: catálogo LZ77 sin modificar ROM.

## 14. Referencias externas de investigación

- REA, CLI y herramientas: https://github.com/Opiuz/REA
- REA, análisis raw-binary: https://github.com/morluto/rea/blob/main/docs/raw-binary.md
- REA, CLI/Evidence: https://github.com/morluto/rea/blob/main/docs/cli.md
- Metroid Fusion Decomp: https://github.com/metroidret/mf
- Data decomp, offsets y recursos: https://github.com/metroidret/mf/blob/main/database.json
- Ghidra: https://github.com/NationalSecurityAgency/ghidra
- MAGE Themes: https://github.com/ConConner/MAGE-Themes

La descompilación comunitaria es una referencia en progreso. Su README reporta 3.265/3.607 funciones descompiladas y advierte que el proyecto no es shiftable y que no debe utilizarse directamente como base de una modificación. Comprobar el estado de esa cifra al realizar cada revisión.

---

**Conclusión actual:** ya existe una identificación robusta de la ROM, un mapa inicial del arranque, la tabla de modos y un primer inventario de recursos. Todavía falta ejecutar una investigación REA/Ghidra por funciones y subsistemas sobre la ROM exacta y correlacionarla con ejecución dinámica. Este documento es el índice y protocolo maestro para completar ese trabajo sin inventar cobertura.
