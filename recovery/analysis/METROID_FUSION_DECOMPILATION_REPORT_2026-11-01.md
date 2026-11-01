# Informe de investigación y descompilación de Metroid Fusion (USA/Australia)

**Fecha de recopilación:** 1 de noviembre de 2026  
**Proyecto de destino:** LATINO AMÉRICA Zector Cero  
**Rama del repositorio de trabajo:** `agent/rea-editable-analysis`  
**Naturaleza del documento:** análisis técnico basado en la ROM identificada, informes estáticos del proyecto y contraste con el código fuente de referencia de Metroid Fusion. No es una descompilación completa generada por REA.

---

## 0. Resumen ejecutivo y límites de la investigación

Este informe reúne el conocimiento técnico disponible sobre la arquitectura de Metroid Fusion: arranque, ciclo principal, modos, Samus, física, colisiones, salas, puertas, eventos, sprites, IA, proyectiles, SA-X, introducción, HUD, menús, texto, audio, guardado y recursos gráficos.

Se consultó el árbol actual del repositorio comunitario `metroidret/mf`, cuya rama `main` apuntaba al commit `de76565c897c05838503717db9aa2adfe92aeba3` (31-10-2026). El README de ese proyecto declaraba 3.265 de 3.607 funciones descompiladas (90,51 %) y 84,34 % de los bytes de datos aún no incorporados a blobs. El propio proyecto advierte que su descompilación **no es shiftable y no debe utilizarse directamente como base de modificación**.

**Importante:** REA no se ejecutó realmente contra la ROM privada en esta sesión. No existe un Evidence ID de REA, una sesión Ghidra abierta ni pseudocódigo extraído por REA para esta ROM. La documentación oficial de REA sobre raw-binary indica que su arquitectura genérica `arm` selecciona `ARM:LE:32:v7` y empieza en estado A32. Eso no representa correctamente, por sí solo, un binario GBA ARM7TDMI/ARMv4T que mezcla ARM y Thumb. Por tanto, este documento no atribuye a REA un trabajo que no se ha realizado.

Los fragmentos explicativos y los nombres de funciones de los apartados siguientes proceden de la fuente de referencia comunitaria. Las direcciones, offsets y hash de la ROM objetivo solo se marcan como confirmados cuando ya constan en los informes estáticos existentes del proyecto. La coincidencia con una fuente de referencia no prueba por sí sola que toda función haya sido reidentificada y validada en la ROM privada.

### Escala de confianza

- **Confirmado en la ROM objetivo:** metadatos, bytes, offsets o referencias contrastados en el análisis de la ROM AMTE.
- **Referencia decomp:** estructura, función o lógica descrita por el repositorio comunitario.
- **Correlación fuerte:** coincide una referencia de offset/recurso con el manifiesto US y la estructura esperada.
- **Pendiente de REA/Ghidra:** falta obtener evidencia de la ROM objetivo con lenguaje, dirección y referencias cruzadas correctas.
- **Pendiente de ejecución:** falta validación real en mGBA o hardware.

---

## 1. Identidad y mapa inicial de memoria

| Campo | Resultado registrado |
|---|---|
| Juego | Metroid Fusion |
| Región | USA/Australia |
| Título de cabecera | `METROID4USA` |
| Código de juego | `AMTE` |
| Tamaño | 8.388.608 bytes (8 MiB) |
| SHA-256 | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` |
| SHA-1 | `ca33f4348c2c05dd330d37b97e2c5a69531dfe87` |
| Checksum de cabecera | `0x98`, válido según el inventario |
| Dirección de carga de ROM | `0x08000000` |
| Primera instrucción | `0xEA00002E` (ARM branch) |
| Destino del primer salto | `0x080000C0` |
| Puntero de entrada Thumb observado | `0x08000231` |
| Código Thumb alineado | `0x08000230` |
| Variable de modo principal | RAM `0x03000BDE` |
| Tabla de despacho | offset ROM `0x278` |
| Entradas de modo observadas | 15 |

El hash debe usarse como identidad de la ROM. Cualquier otra revisión o traducción requiere volver a calcular hash, tamaño, cabecera y offsets antes de reutilizar el análisis.

### 1.1 Arquitectura

GBA utiliza CPU ARM7TDMI, arquitectura ARMv4T. En este juego hay código ARM y Thumb y transiciones entre ambos estados. No se debe convertir automáticamente todo el rango de ROM en código A32: los datos comprimidos, tablas, mapas, paletas, tilemaps y bloques de audio también viven en el espacio de ROM.

La dirección GBA de ROM empieza en `0x08000000`; para una dirección virtual dentro de esa ventana, el offset de archivo correspondiente es normalmente:

```text
file_offset = gba_address - 0x08000000
```

Esta relación solo es válida para direcciones dentro de la ventana ROM y no debe aplicarse a RAM, VRAM, OAM o registros IO.

---

## 2. Arranque y ciclo principal

### 2.1 Inicialización

La referencia comunitaria identifica `InitializeGame()` como la rutina de inicialización, invocada al comienzo de `AgbMain()`. El bootstrap configura el entorno ARM/GBA y transfiere la ejecución a la lógica del juego.

Puntos de interés del análisis objetivo:
- rama inicial ARM desde `0x08000000`;
- ejecución de inicialización en `0x080000C0`;
- establecimiento de la entrada Thumb `0x08000230`;
- ubicación de la variable de modo principal en `0x03000BDE`;
- tabla de modos observada en offset `0x278`.

**Pendiente:** reconstruir con Ghidra el tramo completo de inicialización, vector de interrupciones, IRQ/VBlank, pila de modos y todos los destinos llamados antes de entrar en `AgbMain`.

### 2.2 Esquema funcional de AgbMain

La función de referencia `AgbMain()` sigue este flujo por frame:

1. Ejecuta `InitializeGame()`.
2. Limpia la marca de trabajo del frame.
3. Actualiza el audio.
4. Comprueba si se pidió reiniciar el juego.
5. Actualiza la entrada de botones.
6. Comprueba la combinación de reinicio.
7. Incrementa contadores de frame de 8 y 16 bits.
8. Despacha por `gMainGameMode`.
9. Actualiza la lógica específica del modo activo.
10. Cede el ritmo de ejecución a la sincronización de vídeo/frame.

No es un bucle genérico donde toda la lógica se ejecuta siempre. El modo principal selecciona diferentes handlers: título, selección/intro de nueva partida, juego, pausa, cutscene, close-up del SA-X, borrado de SRAM, game over, final, créditos, demo y debug.

### 2.3 Tabla de 15 modos

El inventario estático del proyecto registra 15 destinos en el despachador del offset `0x278`. Las etiquetas son nombres descriptivos reconstruidos; no son cadenas originales almacenadas en la ROM.

| ID | Etiqueta de trabajo | Dirección destino registrada |
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

**Qué falta:** pseudocódigo de la ROM objetivo para cada destino, límites exactos de funciones, llamadas y transiciones de estado. Los destinos son un índice para Ghidra/REA, no un decomp terminado.

---

## 3. Juego activo: InGameHandler

La referencia `src/in_game.c` define `InGameHandler()` y muestra varios subestados internos:

- inicialización y carga de datos genéricos;
- transición/fundido al abrir una sala;
- juego normal;
- carga de sala;
- secuencia especial del ascensor del SA-X;
- estado de muerte;
- movimiento de depuración/no-clip.

Durante el estado de juego, la secuencia de alto nivel es:

1. Procesar demo/entrada si corresponde.
2. Escribir registros de vídeo.
3. Procesar botón de pausa.
4. Si el movimiento está permitido, actualizar física de Samus y datos de colisión.
5. Actualizar timer y otras rutinas de estado.
6. Actualizar gráficos/paletas animados de la sala.
7. Actualizar sprites y su IA.
8. Actualizar scroll y cámara.
9. Actualizar proyectiles.
10. Dibujar HUD.
11. Actualizar partículas.
12. Dibujar proyectiles y sprites en orden de prioridad.
13. Dibujar Samus.
14. Reiniciar slots OAM y actualizar estado de sala.

Esto revela un orden sensible: física/colisión no se puede separar de clipdata y sala; las IA pueden depender del estado de Samus y de la sala; los recursos gráficos se copian a VRAM en etapas coordinadas con VBlank/DMA.

Referencia: [src/in_game.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/in_game.c).

---

## 4. Samus: estructura, estados, movimiento y física

### 4.1 Estructura de datos

La referencia define `struct SamusData` con, entre otros, estos campos:

| Campo | Uso conocido |
|---|---|
| `pose` | estado/pose actual |
| `turning` | giro pendiente |
| `forcedMovement` | movimiento impuesto por acciones |
| `walljumpTimer` | ventana temporal de wall jump |
| `invincibilityTimer` | invulnerabilidad |
| `speedboostingCounter` | carga/estado de speed booster |
| `armCannonDirection` | dirección del cañón |
| `weaponHighlighted` | arma destacada |
| `newProjectile` | petición de proyectil |
| `cooldownTimer` | temporizador de enfriamiento |
| `chargeBeamCounter` | carga del beam |
| `direction` | dirección |
| `xPosition/yPosition` | posición |
| `xVelocity/yVelocity` | velocidad |
| `slopeType` | tipo de pendiente |
| `standingStatus` | suelo, enemigo, aire o sin control |
| `currentAnimationFrame` | frame de animación |
| `drawDistance* ` | márgenes/dimensiones de dibujado |

La estructura `Equipment` contiene energía, misiles, bombas de energía, estado de beams, armas, traje, nivel de seguridad, mapas descargados y estado de baja energía.

### 4.2 Poses

La enumeración de referencia contiene estados como:
- de pie, giro, disparo, correr, aire, aterrizar;
- agacharse, morph ball, rodar, unmorph;
- salto giratorio, wall jump, space jump, screw attack;
- colgarse de salientes y escaleras;
- shinespark;
- guardar, recargar, interactuar con pads y descargar habilidades;
- congelado, daño, knockback, morir;
- ser agarrada por jefes como Zazabi, Yakuza u Omega Metroid.

También existen valores especiales de solicitud de cambio de pose, que no equivalen a poses normales.

### 4.3 Actualización de física

`SamusUpdatePhysics()` consulta el clipdata bajo Samus para detectar agua, lava, ácido u otros efectos que ralentizan. Según el entorno y el estado del traje:
- puede activar la marca de agua/subacuático;
- reduce aceleración y límites de velocidad en situaciones ralentizadas;
- cambia aceleración/gravedad y topes de velocidad;
- adapta el comportamiento cuando Speed Booster está activo;
- avanza timers/animaciones;
- llama al handler de pose actual mediante una tabla de funciones;
- actualiza distancia de dibujo/estado en suelo;
- integra velocidad y posición.

`SamusUpdate()` gestiona daño ambiental, timers, carga de armas, shinespark, pose, disparo y selección de funciones de animación. `SamusUpdateCollisionData()` compara posiciones anteriores y nuevas para actualizar datos de colisión.

### 4.4 Movimiento especial y ambiente

Funciones de referencia destacadas:
- `SamusApplyXAcceleration`
- `SamusChangeVelocityOnSlope`
- `SamusBombBounce`
- `SamusCheckNewProjectile`
- `SamusHazardDamage`
- `SamusAimCannonStanding`
- `SamusAimCannonMidAir`
- handlers de correr, salto, morph ball, wall jump, ladder, shinespark y daño.

**Impacto para Sector Cero:** cambiar solo sprites de Samus no basta. Las hitboxes, frames, poses, cañón, OAM y estados están conectados a la lógica de movimiento y colisión. Un nuevo personaje debe conservar compatibilidad de dimensiones, puntos de anclaje y transición entre poses.

Referencia: [src/samus.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/samus.c), [include/structs/samus.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/samus.h), [include/constants/samus.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/constants/samus.h).

---

## 5. Salas, tilesets, fondos y clipdata

### 5.1 Estructura de sala

La referencia `struct RoomEntry` relaciona:
- número de tileset;
- propiedades de BG0–BG3;
- scroll;
- transparencia;
- puntero de datos de enemigos;
- eventos que cambian spriteset;
- posición de mapa;
- efecto visual y efecto dañino;
- música;
- tamaños de BG;
- tileset y paleta animados.

La sala, por tanto, no es únicamente un tilemap. Es un paquete de datos que determina gráficos, colisiones, enemigos, música, efectos, scroll, eventos y conexiones.

### 5.2 Carga de sala

Funciones principales de referencia:
- `RoomLoad`
- `RoomLoadTileset`
- `RoomLoadEntry`
- `RoomLoadBackgrounds`
- `RoomLoadScrollsAndEventBasedEffects`
- `RoomLoadDoors`
- `RoomSetInitialTilemap`
- `RoomUpdateAnimatedGraphicsAndPalette`
- `RoomUpdateVerticalTilemap`
- `RoomUpdateHorizontalTilemap`
- `RoomCopyVerticalTilemap`
- `RoomCopyHorizontalTilemap`

Hay al menos tres capas conceptuales distintas que deben inventariarse por sala: gráficos/tilemap de fondo, clipdata de colisión/acciones y datos de sprites/puertas/eventos. No se debe reconstruir una sala modificando solamente el tilemap gráfico.

### 5.3 Compresión

La referencia incluye:
- LZ77 para gráficos y mapas;
- un descompresor RLE particular de las salas;
- copias DMA hacia VRAM;
- recursos animados que se actualizan durante el juego.

El script del proyecto ha detectado streams LZ77 y candidatos por puntero. Un stream comprimido solo se identifica con certeza cuando su puntero y rutina consumidora se correlacionan.

### 5.4 Clipdata y colisiones

`ClipdataProcess(y, x)`:
1. comprueba límites de la sala;
2. transforma coordenadas subpixel a coordenadas de bloque;
3. obtiene el índice de clipdata;
4. detecta si hay una acción temporal sobre el tile (hacer sólido, quitar sólido, proyectil, etc.);
5. determina si la acción se atribuye a actor sprite o no-sprite;
6. resuelve tipo de colisión desde tablas;
7. construye coordenadas locales dentro del bloque;
8. invoca la función de colisión activa.

`struct CollisionData` conserva tipo, coordenadas subpixel, actor, tile X/Y y campos auxiliares. `gClipdataCodePointer` selecciona el código de colisión para el modo actual.

**Consecuencia de edición:** si una fachada, piso, escalera o puerta cambia visualmente, el clipdata debe seguir coincidiendo con la geometría del escenario. Un tile de dibujo no garantiza que el bloque sea caminable.

Referencias: [src/room.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/room.c), [src/clipdata.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/clipdata.c), [include/structs/room.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/room.h), [include/structs/clipdata.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/clipdata.h).

---

## 6. Puertas, conexiones y eventos

### 6.1 Puertas

`struct Door` contiene:
- tipo;
- sala de origen;
- rango X/Y de entrada;
- índice de puerta de destino;
- desplazamiento X/Y de salida.

`ConnectionCheckEnterDoor(y, x)` busca las puertas de la zona actual, verifica sala y rango de coordenadas, resuelve destinos especiales/eventuales, inicia la carga/transición de sala y puede activar cutscenes o cambios de música.

`ConnectionCheckAreaConnection(y, x)` resuelve conexiones entre áreas, cambia `gCurrentArea`, identifica la puerta de destino y activa fundidos/cutscenes/eventos.

### 6.2 Eventos y progresión

`EventSet(event)` actualiza el contador de evento y puede:
- cambiar niveles de seguridad;
- bloquear o restaurar compuertas;
- disparar señales de audio;
- conceder habilidades o armas;
- actualizar efectos ligados a la progresión.

La enumeración de eventos incluye navegación, entradas a salas, descargas de armas/habilidades, cortes de energía, estabilizadores, encuentros con SA-X y progresión entre zonas.

**Impacto:** la progresión no depende solo de la posición del jugador. Hay flags/eventos que cambian puertas, salas, efectos y conversaciones. Al sustituir una sala hay que preservar el identificador y los eventos o documentar un nuevo enlace.

Referencias: [src/connection.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/connection.c), [src/event.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/event.c), [include/structs/connection.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/connection.h), [include/constants/event.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/constants/event.h).

---

## 7. Sprites, enemigos y su IA

### 7.1 Estructura y slots

La referencia define `MAX_AMOUNT_OF_SPRITES = 24` y un `struct SpriteData` con:
- status y tipo;
- posición Y/X;
- coordenadas de trabajo;
- hitbox;
- escala y salud;
- frame de animación y puntero OAM;
- duración de animación;
- ID, slot de sala, slot de gráficos y fila de paleta;
- prioridad de BG/dibujo;
- pose, colisión con Samus, timers y campos auxiliares.

`SpriteLoadRoomSprites()` lee registros de tres bytes por enemigo: posición Y, posición X y slot del spriteset. Un valor `0xFF` en Y termina la lista. La sala no suele almacenar una estructura larga por instancia: referencia el spriteset y coordenadas.

### 7.2 Ciclo de IA

`SpriteUpdate()`:
1. gestiona debris;
2. revisa si Samus está en una pose que detiene parte de las actualizaciones;
3. comprueba colisión Samus-sprite;
4. itera los slots activos;
5. copia el sprite actual a una estructura de trabajo;
6. actualiza RNG y stun;
7. llama al puntero IA primario o secundario según propiedades;
8. actualiza soporte de Samus, animación y visibilidad;
9. copia el resultado de vuelta al array global.

Las funciones de dibujado y carga son separadas:
- `SpriteDrawAll`
- `SpriteDraw`
- `SpriteLoadAllData`
- `SpriteLoadSpriteset`
- `SpriteLoadGfx`
- `SpriteLoadPal`
- `SpriteInitPrimary`
- `SpriteSpawnSecondary`
- `SpriteSpawnPrimary`
- `SpriteSpawnNewXParasite`

### 7.3 Catálogo de módulos de IA de referencia

El árbol actual consultado contiene 105 archivos bajo `src/sprites_AI/`. Incluye, entre otros:

| Familia | Archivos representativos |
|---|---|
| Enemigos de patrulla/voladores | `geemer`, `geega`, `waver`, `ripper`, `skree`, `zeela`, `zoro`, `zozoro` |
| Criaturas de sectores/agua | `ch oot` (nombre de archivo `choot`), `skultera`, `sova`, `dessgeega`, `sidehopper`, `yameba` |
| Enemigos grandes | `arachnus`, `serris`, `nightmare`, `yakuza`, `zazabi`, `ridley`, `omega_metroid`, `nettori` |
| Parásitos X/Core X | `x_parasite`, `blue_x`, `core_x`, `mega_x`, `beam_core_x` |
| SA-X | `sa_x`, `sa_x_arc`, `sa_x_boss`, `sa_x_lab`, `sa_x_monster`, `sa_x_noc`, `sa_x_omega`, `sa_x_tro_1`, `sa_x_tro_2` |
| Interactivos/ambientales | `gate`, `elevator_pad`, `save_pad`, `recharge_pad`, `navigation_pad`, `security_pad`, `atmospheric_stabilizer`, `movable_platform` |

La tabla no enumera todos los módulos ni certifica apariciones en el ROM objetivo; el catálogo exacto está en el árbol de referencia.

**Para crear patrulleros de Sector Cero:** conviene conservar el ciclo de slot/IA/animación/hitbox y reemplazar primero su recurso gráfico y su comportamiento de forma independiente. No conviene editar únicamente el PNG de referencia: deben mantenerse dimensiones de OAM, pivotes, hitbox, paleta y estados.

Referencias: [src/sprite.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sprite.c), [src/sprite_util.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sprite_util.c), [src/sprites_AI/](https://github.com/metroidret/mf/tree/de76565c897c05838503717db9aa2adfe92aeba3/src/sprites_AI), [include/structs/sprite.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/sprite.h).

---

## 8. Jefes, SA-X y X

Los jefes no son simples sprites grandes: tienen IA especializada, fases, vulnerabilidad, hitboxes, efectos, eventos y a veces secuencias de cutscene independientes.

Módulos relevantes:
- Arachnus: `src/sprites_AI/arachnus.c`
- Serris: `serris.c`
- Nightmare: `nightmare.c`
- Yakuza: `yakuza.c`
- Zazabi: `zazabi.c`
- Ridley y pre-spawn: `ridley.c`, `ridley_pre_spawn.c`
- Nettori: `nettori.c`
- Omega Metroid: `omega_metroid.c`, `omega_metroid_husk.c`
- Core X y variantes: `core_x.c`, `beam_core_x.c`, `mega_x.c`

### 8.1 SA-X

La lógica del SA-X aparece repartida entre:
- `src/sa_x.c`: poses, posición, gráficos y secuencias especiales;
- `src/sa_x_close_up.c`: modo de primer plano;
- `src/sprites_AI/sa_x*.c`: comportamiento específico por escenario y forma;
- datos gráficos y de animación separados.

Entre las funciones documentadas figuran `SaXSetPose`, `SaXUpdatePosition`, `SaXUpdateGraphicsAndDraw` y handlers de la escena del ascensor.

### 8.2 Parásitos X

El ciclo global de enemigos incluye spawn, daño, absorción/transformación y objetos resultantes. Se apoyan en tablas de tipo y estado y no deben confundirse con los sprites normales de ambiente.

**Pendiente:** correlacionar cada IA y boss con IDs, funciones y offsets del ROM AMTE mediante un import Ghidra válido y sus tablas de punteros.

Referencias: [src/sa_x.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sa_x.c), [src/sa_x_close_up.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sa_x_close_up.c), [src/sprites_AI/](https://github.com/metroidret/mf/tree/de76565c897c05838503717db9aa2adfe92aeba3/src/sprites_AI).

---

## 9. Proyectiles, armas y daño

La referencia define 16 slots máximos de proyectil. `struct ProjectileData` mantiene:
- status;
- puntero OAM;
- posición X/Y;
- frame y duración de animación;
- tipo y dirección;
- paleta;
- fase de movimiento;
- parte/slot primario;
- hitbox;
- timer.

La enumeración de tipos incluye:
- beam normal, Charge, Wide, Plasma y Wave;
- variantes cargadas;
- misil normal, Super, Ice y Diffusion;
- flare;
- bomba y Power Bomb;
- Diffusion Flake.

`ProjectileInit()` busca un slot libre, asigna estado de existencia/visibilidad, posición, dirección, tipo y campos de animación. Las rutinas de daño distinguen beam, misiles, hielo, bombas y vulnerabilidades particulares de sprites. Existe lógica separada para impacto contra bloques sólidos y contra sprites.

**Implicación para el mod:** un cambio visual en un misil o beam debe conservar la estructura de frames, el ancho/alto de OAM y el orden de dibujado. Si se cambia el comportamiento, hay que estudiar el sistema de daño, los límites por categoría, estados de carga y el impacto en clipdata.

Referencias: [src/projectile.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/projectile.c), [include/structs/projectile.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/structs/projectile.h), [include/constants/projectile.h](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/include/constants/projectile.h).

---

## 10. Cámara, scroll, efectos y renderizado

El scroll está separado en funciones para:
- procesar desplazamiento general;
- scroll horizontal/vertical;
- modos de cámara front-wide;
- scroll sin límites durante debug;
- desplazamiento de BG0/BG3;
- posiciones de haze y efectos;
- elementos específicos como la sombra de Nightmare o el planeta SR388.

El juego combina BG0–BG3, OBJ/OAM, DMA, paletas, animación gráfica y VBlank. Los recursos no deben editarse ignorando sus destinos VRAM y sus tiempos de transferencia.

Módulos de referencia:
- `src/scroll.c`
- `src/display.c`
- `src/dma.c`
- `src/animated_graphics.c`
- `src/animated_palette.c`
- `src/color_effects.c`
- `src/color_fading.c`
- `src/haze.c`
- `src/particle.c`
- `src/screen_shake.c`

---

## 11. HUD, mapas, menús e interfaz

### 11.1 HUD

Funciones como `HudDrawEnergy`, `HudDrawMissiles`, `HudDrawPowerBombs`, `HudUpdateGfx` y `HudDrawOam` gestionan valores y gráficos del HUD. Los iconos y números dependen de datos y paletas distintos.

### 11.2 Mapa y pausa

La pantalla de pausa contiene:
- handler general;
- secuencias de entrada/salida;
- mapa de área;
- icono de ubicación de Samus;
- tiles visitados;
- objetos recogidos;
- descarga de mapa;
- nivel de seguridad, tiempo de juego y contadores de tanques;
- conversaciones con la computadora/navegación.

### 11.3 Título

El título tiene inicialización, animación de entrada, objetos OAM, prompt Press Start, selección de idioma y fade. Esto importa para la sustitución de logo y fondo: el logo no es solo una imagen plana; se compone de tiles/objetos y comportamiento.

Referencias: [src/hud.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/hud.c), [src/menus/pause_screen.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/menus/pause_screen.c), [src/menus/pause_screen_map.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/menus/pause_screen_map.c), [src/menus/title_screen.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/menus/title_screen.c).

---

## 12. Introducción, secuencias narrativas y hangar BSL

### 12.1 Estados de introducción

`NewFileIntroHandler()` recorre:
0. inicializar y parar audio;
1. espera de 100 frames;
2. vista previa de SR388;
3. escena en SR388;
4. nave de Samus en vuelo;
5. Samus se desmaya;
6. Samus a la deriva;
7. Samus encontrada;
8. tratamiento médico;
9. Samus curada;
10. llegada a BSL;
11. aterrizaje en hangar;
12. fundido y guardado de introducción.

Si la introducción ya fue completada en el archivo de guardado, el handler puede finalizar sin repetirla. El estado 12 procesa el guardado en varias etapas, por lo que saltar escenas requiere conservar estado de guardado, temporizadores y variables de escena.

### 12.2 Recursos del hangar

La referencia y el crosswalk identifican:

| Offset ROM | Recurso |
|---|---|
| `0x5F7190` | `landing_on_bsl_bg.gfx.lz` |
| `0x5FAB54` | `landing_on_bsl_obj.gfx.lz` |
| `0x5FF708` | paleta de fondo |
| `0x5FFD08` | paleta de objetos |
| `0x5FFF08` | tilemap del espacio |
| `0x60030C` | tilemap del hangar |
| `0x598898` | tilemap de texto de la nave compartido |

La inicialización de aterrizaje:
- cambia configuración de interrupciones y VBlank;
- limpia RAM no relacionada con gameplay;
- descomprime OBJ y BG a VRAM;
- copia paletas a PALRAM;
- carga tilemaps del hangar, espacio y texto;
- configura scroll y BGCNT;
- crea OAM para scroll de BG, luces, puerta y efectos;
- desactiva/habilita capas de pantalla según la secuencia;
- instala el VBlank específico de la escena.

### 12.3 Prueba experimental anterior

En la ROM identificada se generó una ROM candidata con un byte cambiado en el offset `0x8777E`: de `0x01` a `0x0B`, buscando que el selector de introducción pase al estado 11 tras inicializar.

El informe de esa prueba registró:
- ROM de entrada SHA-256: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`;
- salida SHA-256: `7ef453a3d1cace1e8ffb263cee4c2a7a199598f9e578973a9f99ddb6eb19fea8`;
- cabecera válida;
- un byte modificado;
- estado declarado: candidato estático, no validado en ejecución.

La posterior captura automática de mGBA produjo imágenes de la barra de tareas/escritorio y no de la ventana del emulador. Por ello **no hay evidencia visual válida de que la escena del hangar haya aparecido**. Este parche no debe describirse como funcional.

Referencias: [src/new_file_intro.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/new_file_intro.c), [resource map del proyecto](https://github.com/dicksonmancebo09-commits/trecetrece/blob/agent/rea-editable-analysis/recovery/analysis/hangar_scene_resource_map_2026-10-28.md).

---

## 13. Texto, mensajes y localización

La referencia `src/text.c` muestra un renderer de caracteres que:
- obtiene ancho de glyph;
- lee gráficos de caracteres;
- compone pixels en buffers de destino;
- dibuja texto de localización;
- dibuja banners de mensaje;
- presenta mensajes de evento;
- limpia gráficos de texto en VRAM.

Las cadenas de gameplay, texto de navegación, banners de lugar, nombres y resultados pueden tener tablas y formatos distintos. El archivo de referencia `src/data/text_data.c` y las constantes de caracteres deben estudiarse junto a sus punteros, codificación y dimensiones de caja.

No basta con reemplazar una cadena ASCII dentro del ROM. Para traducir correctamente se necesita conocer encoding, glifos disponibles, terminadores, control codes, punteros, límites de cuadro y compresión. El paquete español de preproducción de Sector Cero no está demostrado como integrado en la ROM.

Referencia: [src/text.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/text.c).

---

## 14. Audio y música

El módulo de audio de referencia incluye:
- actualización de pistas;
- canales PCM/PSG;
- envolventes de volumen (attack, decay, sustain, release);
- comandos de secuencia como FINE, PEND, REPT, PRIO, KEYSH, VOICE, VOL, PAN, BEND, BENDR, LFOS y MOD;
- eventos de sonido asociados a rooms, transiciones, armas, enemigos y cutscenes.

La música no debe tratarse como un único bloque reemplazable sin tabla de secuencias, punteros, samples, instrumentos y relación con los eventos. Para un rediseño sonoro de Sector Cero se deberá inventariar música, SFX, samples y llamadas que los disparan.

Referencia: [src/audio.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/audio.c), [src/data/music_track_data.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/data/music_track_data.c).

---

## 15. Guardado y SRAM

La referencia incluye rutinas para:
- borrar SRAM;
- escribir el archivo más reciente;
- guardar una copia de respaldo;
- leer archivos a EWRAM;
- leer el header de SRAM;
- proceso de guardado de la introducción.

La introducción no solo reproduce una escena: después del aterrizaje entra en un proceso por etapas de guardado. Saltar directamente a gameplay puede alterar el estado de introducción completada o la estructura del archivo. Toda modificación del flujo debe probarse con archivo nuevo, archivo existente, guardado, carga y reinicio.

Referencias: [src/sram/sram.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sram/sram.c), [src/sram_misc.c](https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/src/sram_misc.c).

---

## 16. Inventario global de la descompilación comunitaria

Consulta del árbol de `metroidret/mf` en commit `de76565c897c05838503717db9aa2adfe92aeba3`:

| Elemento del árbol | Conteo consultado |
|---|---:|
| Rutas totales | 1.850 |
| Archivos C | 704 |
| Headers C | 398 |
| Archivos fuente de IA | 105 |
| Archivos fuente de datos de sprites | 94 |
| Archivos de datos de salas numeradas | 382 |
| Archivos ensamblador bajo `asm/` | 11 |

### Salas por área (conteo de archivos de referencia)

| Área | Archivos de sala |
|---|---:|
| Main Deck | 87 |
| Sector 1 / SRX | 54 |
| Sector 2 / TRO | 61 |
| Sector 3 / PYR | 39 |
| Sector 4 / AQA | 48 |
| Sector 5 / ARC | 52 |
| Sector 6 / NOC | 41 |
| **Total** | **382** |

No confundir “382 archivos de datos” con una cifra de salas únicas confirmada en la ROM: puede haber archivos auxiliares y formas de agrupación propias del proyecto.

---

## 17. Inventario estático existente de la ROM AMTE

El informe de escaneo del proyecto contiene un barrido completo de los 8 MiB y registra candidatos de:
- punteros a la ventana ROM;
- streams LZ77;
- punteros a datos comprimidos;
- segmentos ASCII;
- entropía por ventanas;
- padding final.

El catálogo y el crosswalk existentes ya priorizaron 158 candidatos LZ77 con referencia por puntero y tamaño descomprimido mínimo de 8 KiB. 133 offsets coinciden exactamente con nombres del manifiesto US de la referencia; 25 quedaron sin resolver.

Coincidencias de ejemplo:
- title screen: objetos, logo y fondo espacial;
- pause screen: BG y OBJ;
- intro: escenas del encuentro con Hornoad, cirugía, monólogo y aterrizaje BSL;
- SA-X close-up;
- ending/results.

Los números de candidatos dependen del filtro usado; el informe antiguo de rom_inventory y el escaneo posterior no tienen idénticos umbrales. No se deben fusionar sus conteos como si provinieran del mismo algoritmo.

Referencias del repositorio de trabajo:
- `recovery/analysis/full_rom_static_scan_2026-10-28.md`
- `recovery/analysis/rom_inventory.json`
- `recovery/analysis/lz77_priority_queue_2026-10-28.md`
- `recovery/analysis/lz77_named_asset_crosswalk_2026-10-28.md`
- `recovery/analysis/lz77_named_asset_crosswalk_2026-10-28.json`

---

## 18. Resultado específico sobre REA

### 18.1 Qué se pudo investigar

Se consultó documentación y código público del proyecto REA:
- instalación y configuración CLI;
- soporte del provider Ghidra;
- perfiles de análisis;
- arquitectura raw-binary;
- lenguaje y selección de arquitectura.

La documentación raw-binary de REA para ARM selecciona `ARM:LE:32:v7` y comienza en estado A32. No proporciona un selector raw-binary directo para `ARM:LE:32:v4t` con interworking ARM/Thumb. El provider Ghidra admite arquitecturas genéricas `arm`, pero esto no equivale a una importación GBA ARMv4T correcta.

### 18.2 Qué no se ejecutó

No se ejecutó:
- `rea inspect` sobre la ROM del usuario;
- `rea doctor` o `rea providers` en su Codespace;
- apertura de sesión REA/Ghidra;
- generación de Evidence IDs;
- batch decompilation;
- exportación de pseudocódigo desde el binario privado.

La herramienta GitHub disponible aquí permite inspeccionar y editar archivos del repositorio, pero no ejecutar la terminal privada del Codespace. No sería correcto inventar resultados de ejecución.

### 18.3 Ruta técnicamente válida

Para descompilar fielmente la ROM:
1. verificar hash y ROM exacta;
2. importar como Raw Binary en Ghidra;
3. base/mapeo GBA: `0x08000000`;
4. seleccionar lenguaje ARM little-endian ARMv4T (Ghidra: `ARM:LE:32:v4t`);
5. comprobar que el salto inicial lleva a `0x080000C0`;
6. marcar funciones ARM/Thumb e interworking explícitamente;
7. importar RAM, EWRAM, IWRAM, IO, VRAM, PALRAM, OAM y SRAM como bloques separados/no-file-backed cuando proceda;
8. analizar primero bootstrap, main loop y dispatcher;
9. seguir callers/callees/xrefs y clasificar datos vs código;
10. guardar Evidence/pseudocódigo y cruzar resultados con manifiesto de recursos y mGBA.

REA puede complementar la organización de evidencia, búsqueda, llamadas y documentación cuando su provider y arquitectura puedan interpretar el target con corrección. La limitación de arquitectura debe permanecer registrada hasta que REA ofrezca una ruta ARMv4T apropiada.

---

## 19. Cobertura y backlog de trabajo

| Subsistema | Investigación de referencia | Coincidencia ROM objetivo | REA/Ghidra en ROM | Ejecución |
|---|---|---|---|---|
| Header/entrada | Sí | Confirmada parcialmente | No | No |
| Bootstrap/IRQ | Sí | Parcial | No | No |
| Main loop/modos | Sí | Dispatch 15 destinos observado | No | No |
| Input | Sí | Pendiente | No | No |
| Samus/poses/física | Sí | Pendiente | No | No |
| Salas/tilesets | Sí | Inventario heurístico y crosswalk parcial | No | No |
| Clipdata/colisiones | Sí | Pendiente | No | No |
| Puertas/conexiones | Sí | Pendiente | No | No |
| Eventos/progresión | Sí | Pendiente | No | No |
| Enemigos/IA | Sí | Catálogo de referencia, punteros de ROM por correlacionar | No | No |
| Jefes/SA-X/X | Sí | Parcial por recursos nombrados | No | No |
| Proyectiles/armas | Sí | Pendiente | No | No |
| HUD/menús | Sí | Recursos nombrados parcialmente | No | No |
| Intro/hangar | Sí | Recursos de hangar y estado 11 correlacionados | No | Capturas previas inválidas |
| Texto | Sí | Recursos parciales | No | No |
| Audio | Sí | Pendiente | No | No |
| SRAM | Sí | Pendiente | No | No |
| Gráficos/paletas/OAM | Sí | 133 offsets de candidatos emparejados con manifiesto | No | No |

### Próximos lotes de investigación

1. Importación correcta Ghidra ARMv4T, RAM/VRAM y primera pasada de funciones.
2. Call graph global desde `0x080000C0` hasta `AgbMain`.
3. Despachador y transiciones de los 15 modos.
4. Samus/input/física/clipdata.
5. Catálogo por sala: entradas, puertas, mapa, clipdata, spriteset, tilemap, paletas, música y eventos.
6. Catálogo por spriteset y por familia de IA.
7. Cutscenes, texto, UI y SRAM.
8. Audio y recursos comprimidos.
9. Comparación dinámica en mGBA con capturas verificadas de la ventana real.

---

## 20. Referencias y procedencia

### Referencia comunitaria

Repositorio: https://github.com/metroidret/mf  
Commit consultado: `de76565c897c05838503717db9aa2adfe92aeba3`  
README/progreso: https://github.com/metroidret/mf/blob/de76565c897c05838503717db9aa2adfe92aeba3/README.md

La referencia declara licencia MIT. Revisar atribución/licencia en el repositorio antes de reutilizar código. Su README advierte que el decomp no es shiftable y no debe usarse directamente como base de modificación.

### REA

- REA: https://github.com/Opiuz/REA
- Instalación: https://github.com/Opiuz/REA/blob/main/docs/installation.md
- Investigación nativa: https://github.com/Opiuz/REA/blob/main/docs/native-investigation.md
- Raw-binary y limitaciones ARM: https://github.com/morluto/rea/blob/main/docs/raw-binary.md

### Ghidra

- Proyecto: https://github.com/NationalSecurityAgency/ghidra
- Para este target: lenguaje GBA ARM7TDMI/ARMv4T, endian little, base ROM `0x08000000`.

### Informes internos utilizados

- `recovery/analysis/rom_inventory.json`
- `recovery/analysis/full_rom_static_scan_2026-10-28.md`
- `recovery/analysis/lz77_named_asset_crosswalk_2026-10-28.md`
- `recovery/analysis/hangar_scene_resource_map_2026-10-28.md`
- `recovery/analysis/METROID_FUSION_MASTER_DOSSIER.md`
- `recovery/analysis/REA_FULL_GAME_INVESTIGATION_PROMPT.md`

---

## Conclusión

La investigación ya ofrece un mapa técnico útil para entender dónde intervenir: el loop principal coordina estados, Samus, salas, colisiones, sprites, proyectiles, HUD y renderizado; las salas agrupan gráficos, clipdata, puertas, eventos, sprites y música; los enemigos dependen de tablas de IA y recursos; la introducción y el guardado comparten una máquina de estados sensible.

**No existe todavía una descompilación íntegra y verificada de la ROM AMTE mediante REA.** Este documento reúne la investigación de la referencia comunitaria y la correlación con la ROM objetivo donde hay evidencia. El siguiente paso para convertirlo en un decomp propio es una importación ARMv4T real en Ghidra y la generación de Evidence por función, sin atribuir pseudocódigo de terceros a un análisis que no se ejecutó.
