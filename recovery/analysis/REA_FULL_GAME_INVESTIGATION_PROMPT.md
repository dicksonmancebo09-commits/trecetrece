# Encargo para el agente REA — auditoría integral de Metroid Fusion

> **Alcance de solo lectura:** las restricciones de este documento se aplican únicamente a esta tarea de investigación REA/Ghidra. No son una política general del proyecto ni autorizan a bloquear la producción. El PR [#7 — Autorizar transformación visual de toda la ROM](https://github.com/dicksonmancebo09-commits/trecetrece/pull/7) se fusionó el 27-10-2026 y el agente vigente `.github/agents/metroid-re.agent.md` autoriza expresamente la modificación de copias de la ROM cuando el usuario lo solicita. Para tareas de producción y edición, sigue ese mandato; no reutilices la prohibición de este encargo de investigación como regla general.

Trabaja sobre la ROM privada del usuario:
`/workspaces/gba/Metroid Fusion (USA, Australia).gba`

Objetivo: construir el expediente técnico más completo posible de Metroid Fusion para apoyar LATINO AMÉRICA Zector Cero. Lee primero:
- `recovery/analysis/METROID_FUSION_MASTER_DOSSIER.md`
- `recovery/docs/REA_FULL_ROM_TO_EDITABLE_CODE.md`
- `docs/villa-duarte-sector-cero/research/METROID_REA_WORKFLOW.md`
- `recovery/analysis/full_rom_static_scan_2026-10-28.md`
- `recovery/analysis/lz77_named_asset_crosswalk_2026-10-28.md`
- `recovery/analysis/hangar_scene_resource_map_2026-10-28.md`

## Restricciones no negociables
1. No modificar la ROM, no generar parches, no importar ROMs ni assets extraídos al repo.
2. No sobreescribir el original ni la copia backup.
3. Mantener resultados REA, Ghidra, capturas, snapshots y pseudocódigo completo bajo `private-roms/rea-analysis/`, excluido por Git.
4. Toda conclusión lleva hash, dirección virtual, offset de archivo, bytes/rango, provider/lenguaje y Evidence ID o referencia reproducible.
5. Diferenciar resultado REA, resultado Ghidra, referencia comunitaria y observación mGBA.
6. No declarar un decomp “completo” si hay funciones o datos desconocidos.
7. No desensamblar datos, paletas, tablas o LZ77 como si fueran código.
8. No tratar un error de provider o una falta de Ghidra como evidencia de que no hay funciones.

## Fase A — preflight
Ejecuta y conserva salidas:
```bash
rea --version --json
rea doctor --json
rea providers --json
rea capabilities --json
sha256sum "/workspaces/gba/Metroid Fusion (USA, Australia).gba"
stat -c '%n %s bytes' "/workspaces/gba/Metroid Fusion (USA, Australia).gba"
```
Confirma que hash sea `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`. Si cambia, detente y registra nueva identidad; no reutilices offsets automáticamente. Confirma que Ghidra provider realmente está disponible. Instalar REA no demuestra que Ghidra esté instalada.

## Fase B — arquitectura y admisión
La ROM es GBA ARM7TDMI/ARMv4T y mezcla ARM y Thumb.
La vía raw-binary genérica ARM de REA usa `ARM:LE:32:v7` y empieza en A32. Úsala únicamente como triage. No presentes un resultado ARMv7 como evidencia final de instrucciones Thumb/ARMv4T.
Para cobertura completa, si Ghidra está disponible, crea también una importación Raw Binary independiente con:
- language `ARM:LE:32:v4t`
- little-endian
- base de mapeo `0x08000000`
- verifica la rama inicial `0xEA00002E` y el destino `0x080000C0`
- sigue BX/interworking y delimita correctamente rangos ARM y Thumb
No cambies el archivo fuente. Documenta si el workflow REA no puede establecer ARMv4T; no simules que lo ha hecho.

## Fase C — inventario y mapa principal
- Obtener overview y lista completa de funciones con los mecanismos reales disponibles.
- Clasificar funciones como code, Thumb, wrapper, thunk, jump table, data, padding o unresolved.
- Confirmar el bootstrap, IRQ/VBlank, main loop, puntero Thumb, variable de modo y tabla de 15 modos del offset `0x278`.
- Para cada rutina importante, decompilar y guardar assembly, callers, callees, xrefs y estructuras.
- Construir un call graph desde la entrada y el dispatcher; cuantificar cobertura con denominador explícito.
- No extrapolar direcciones de la referencia community al ROM sin comprobar bytes.

## Fase D — investigación exhaustiva por áreas funcionales
Trabaja en lotes independientes, no con una búsqueda gigante. Orden obligatorio:
1. boot, IRQ/VBlank, frame loop y modos
2. input, Samus, animación, movimiento y física
3. clipdata, colisiones, bloques, salas, scroll, doors, connections
4. events, triggers, flags, progresión y escape
5. sprite tables, cada familia de enemy AI y sus datos
6. bosses, SA-X, X parasites
7. beam, missile, power bomb, projectiles, pickups, effects, particles
8. HUD, minimap, maps, menus, title, file select, intro, cutscenes, ending, credits
9. text, character maps, message boxes, audio, music, SFX
10. SRAM, save/load, demo and reset
11. graphics, palettes, tilemaps, LZ77 loaders, OAM, DMA and video setup

Por cada sistema crea una ficha Markdown con funciones/direcciones, pseudocódigo, assembly, referencias, structs/variables, recursos usados, confianza y open questions. Una función sólo se marca understood cuando callers/callees/datos/contexto respaldan la explicación.

## Fase E — datos y recursos
Cruza con `database.json` de `metroidret/mf` sólo como referencia externa. Empieza por los 158 candidatos LZ77 priorizados del crosswalk, incluidos los 133 offsets coincidentes. Busca consumidores/cargadores de los recursos antes de atribuirlos a una sala o pantalla. Vincula tileset, paleta, tilemap, OAM, animación, loader y dependencias. No sobrescribas offsets ni deduzcas que cada LZ77 es gráfico.

## Fase F — resultados y cobertura
Actualiza de forma incremental:
- `private-roms/rea-analysis/evidence/`
- `private-roms/rea-analysis/pseudocode/`
- `private-roms/rea-analysis/assembly/`
- `private-roms/rea-analysis/callgraphs/`
- `private-roms/rea-analysis/resources/`
- `private-roms/rea-analysis/coverage/`
- `private-roms/rea-analysis/unresolved/`

En el repo sólo versiona un resumen sin contenido binario ni dumps: `recovery/analysis/REA_FULL_GAME_PROGRESS.md`. Debe mostrar cobertura por sistema, archivos de evidencia locales, hashes, provider, language, funciones analizadas, porcentaje con denominador explicado, hallazgos, discrepancias y siguiente lote.

## Fase G — control de calidad
- Ejecuta tests de los parsers/herramientas del proyecto.
- Comprueba que los archivos privados siguen ignorados por Git.
- No uses capturas de escritorio como capturas de juego.
- No afirmes validación mGBA sin ver una captura de la ventana del emulador o debugger real.
- No modifiques la ROM en este encargo.

## Criterio final
Entrega un informe de investigación integral con:
- identidad del ROM
- mapa de memoria y código
- call graph
- funciones descompiladas y aún pendientes
- sistemas explicados
- catálogo de salas, enemigos, jefes, gráficos, mapas, paletas, texto y audio
- Evidence IDs, rangos, referencias cruzadas
- porcentaje real de cobertura por módulo y global
- limitaciones y tareas pendientes

Avanza todo lo que permita el entorno sin esperar aprobación entre las fases de solo lectura. Si una capacidad no existe, registra el bloqueo preciso y continúa con las partes independientes.
