# trecetrece

Repositorio de trabajo para investigar herramientas, organizar recursos con licencia compatible y desarrollar un videojuego original de acción/plataformas con identidad dominicana.

**Título oficial del juego: LATINO AMÉRICA Zector Cero.**  
La dirección artística se inspira en Villa Duarte y sus barrios de Santo Domingo Este. «Villa Duarte — Sector Cero» aparece en documentos previos como nombre provisional o etiqueta de desarrollo; no es el título oficial vigente.

## Documentación y continuidad

> **Aviso de build:** la v1.3 ha sido retirada como candidata funcional tras el informe de crash y pantalla inicial ilegible. La causa exacta del crash sigue sin reproducirse en emulador.

- [Estado de continuidad del proyecto — LATINO AMÉRICA Zector Cero](docs/villa-duarte-sector-cero/PROJECT_STATE_HANDOFF.md)
- [Memoria de continuidad — tres conversaciones recientes (02-11-2026)](docs/villa-duarte-sector-cero/MEMORIA_CONTINUIDAD_TRES_CONVERSACIONES_2026-11-02.md)
- [Prueba 01 de ROM — integridad de Urban Opening v1.0](docs/villa-duarte-sector-cero/TEST_01_ROM_INTEGRITY.md)
- [v1.2 — sustitución real de recursos de título](docs/villa-duarte-sector-cero/REAL_TITLE_RESKIN_V1_2.md)
- [v1.3 — título real y primer escenario conectado al mapa](docs/villa-duarte-sector-cero/ROOM0_RESKIN_V1_3.md)
- [Auditoría de fallos v1.3 — no usar como build funcional](docs/villa-duarte-sector-cero/POSTMORTEM_V1_3.md)
- [v1.4 — correcciones de coherencia gráfica](docs/villa-duarte-sector-cero/V1_4_RENDER_FIX.md)
- [v1.5 — corrección real del desbordamiento de título y transparencia](docs/villa-duarte-sector-cero/V1_5_ACTUAL_RENDER_FIX.md)
- [Candidata v1.1 QA Viewer — prueba visual nativa, alcance y hashes](docs/villa-duarte-sector-cero/QA_VIEWER_V1_1.md)
- [Vista de referencia de la sala v1.0 (reconstrucción, no captura de emulador)](assets/test-builds/test-01/v1.0-urban-opening-room-reconstruction.png)
- [Identidad visual de los siete escenarios](docs/villa-duarte-sector-cero/SEVEN_SCENARIO_VISUAL_IDENTITIES.md)
- [Atlas vectorial editable de los siete escenarios](assets/concept/latino-america-zector-cero-seven-scenarios.svg)
- [Paquete de producción del escenario 1 — tiles, capas y catálogo](assets/tiles/scenario-01/README.md)
- [Paquete de producción del escenario 2 — Callejones del Caliche](assets/tiles/scenario-02/README.md)
- [Paquete de localización español latinoamericano — es-419](localization/es-419/README.md)
- [Guía de voz y jerga caribeña](localization/es-419/VOICE_AND_SLANG_GUIDE.md)
- [Diálogos originales de muestra](localization/es-419/dialogue.json)
- [Glosario regional](localization/es-419/glossary.json)
- [Validador de localización](tools/check_localization_es419.py) y [pruebas unitarias](tests/test_localization_es419.py)
- [Atlas modular de tiles del escenario 1](assets/tiles/scenario-01/scenario-01-villa-duarte-tiles.svg)
- [Composición del escenario 1 por capas](assets/tiles/scenario-01/scenario-01-layered-composition.svg)
- [Concepto vectorial editable de la primera calle](assets/concept/latino-america-zector-cero-villa-duarte-street.svg)
- [Resumen y estado actual](docs/villa-duarte-sector-cero/README.md)
- [Herramientas y repositorios de referencia](docs/villa-duarte-sector-cero/research/TOOLS_AND_REPOSITORIES.md)
- [Notas técnicas de la ROM de referencia](docs/villa-duarte-sector-cero/research/ROM_TECHNICAL_NOTES.md)
- [Biblia visual de Villa Duarte y sus barrios](docs/villa-duarte-sector-cero/VILLA_DUARTE_VISUAL_BIBLE.md)
- [Dirección artística, procedencia y licencias](docs/villa-duarte-sector-cero/research/ART_DIRECTION_AND_LICENSES.md)
- [Bitácora de investigación y pruebas](docs/villa-duarte-sector-cero/WORKLOG.md)
- [Auditoría de los archivos existentes](docs/villa-duarte-sector-cero/REPOSITORY_AUDIT.md)
- [Registro de fuentes y verificación](docs/villa-duarte-sector-cero/research/RESEARCH_REGISTER.md)
- [Instalar REA en Codespaces](docs/villa-duarte-sector-cero/research/REA_CODESPACES_SETUP.md)
- [Flujo de R.E. para Metroid Fusion](docs/villa-duarte-sector-cero/research/METROID_REA_WORKFLOW.md)
- [Agente Metroid RE](.github/agents/metroid-re.agent.md)
- [Sonda de metadatos GBA](tools/metroid_gba_probe.py)
- [Instalar mGBA y diagnosticar ROMs en Codespaces](docs/villa-duarte-sector-cero/MGBA_CODESPACES_SETUP.md)
- [Instalación de Stable Diffusion, OmniRoute, skills y Scrapling](docs/villa-duarte-sector-cero/AI_IMAGE_GENERATION_SETUP.md)

## Diagnóstico GBA

- mGBA se instala automáticamente al crear/reconstruir el Codespace; instalador manual: `bash tools/install_gba_emulator.sh`.
- Para capturar el arranque y el estado después de START: `bash tools/run_gba_diagnostic.sh private-roms/ROM.gba`.
- Los resultados se guardan en `private-roms/diagnostics/` y no incluyen la ROM.
- La prueba de GitHub Actions valida la instalación y sintaxis de las herramientas; no ejecuta ROMs privadas que no están en el repositorio.

## Uso del agente Metroid RE

Abre Codespaces, selecciona el agente **Metroid RE** en el selector de agentes de Copilot y utiliza como primer paso:

```bash
python3 -m unittest discover -s tests -v
python3 tools/metroid_gba_probe.py private-roms/MetroidFusion.gba --json
```

La segunda orden necesita una ROM colocada localmente y excluida de Git. La sonda solo informa metadatos; el análisis del código requiere REA y Ghidra configurados.

## Principios de desarrollo y gestión de recursos

El desarrollo de **LATINO AMÉRICA Zector Cero** debe avanzar por todas las vías técnicas y creativas disponibles: investigación, ingeniería inversa autorizada, diseño de recursos originales, automatización, edición de builds privados, integración, depuración y pruebas. Las herramientas de referencia no deben convertirse en una barrera artificial para el progreso.

Metroid Fusion se utiliza como base de estudio técnico y referencia de estructura, ritmo, mapas y mecánicas. Los builds de trabajo pueden analizarse y modificarse en el entorno privado del desarrollador. Para mantener el repositorio público limpio y evitar redistribuir material comercial, no se versionan aquí ROMs comerciales, ROMs derivadas, parches binarios ni assets propietarios copiados. Los recursos originales del proyecto y los scripts/herramientas sí pueden versionarse según sus licencias.

Los enlaces a herramientas y repositorios externos documentan fuentes de investigación; no implican afiliación ni aprobación de sus autores.

> **Visibilidad:** este repositorio es público. Antes de publicar, verificar que los archivos no contengan ROMs, datos binarios propietarios, credenciales ni material privado.

## Plan de niveles y salas

- [Plan maestro de siete barrios y 382 salas](docs/villa-duarte-sector-cero/LEVEL_ROOM_MASTER_PLAN_V2.md).
- [Registro estructurado de las 382 salas](data/world/sector-cero-room-registry-v1.json).
- Asignación: 87 Villa Duarte · 54 El Caliche · 61 La Francia Nueva · 39 Calero · 48 Pueblo Nuevo · 52 Los Molinos · 41 Simónico.

## Transformación visual

- [Plan maestro de transformación visual](docs/villa-duarte-sector-cero/VISUAL_TRANSFORMATION_PLAN.md)
- [Matriz de cobertura visual de toda la ROM](docs/villa-duarte-sector-cero/ROM_VISUAL_COVERAGE.md)
- [Tarea 1: línea base visual](docs/villa-duarte-sector-cero/BASELINE_VISUAL_TAREA_01.md)
- [Agente Metroid RE Visual Lab](.github/agents/metroid-re.agent.md)

## Herramientas de IA para el proyecto

- Instalación completa: `bash tools/install_all_tools.sh` (Linux/Codespaces) o `.\\tools\\install_all_tools.ps1` (Windows).
- Arrancar ComfyUI y OmniRoute: `bash tools/start_ai_stack.sh`.
- Modelo de Stable Diffusion de 4.27 GB: instalar opcionalmente con `bash tools/install_ai_stack.sh --with-model`.
- Instalación completa con checkpoint y navegadores de Scrapling: `bash tools/install_all_tools.sh --with-model --with-browsers`.
- [Guía de instalación](docs/villa-duarte-sector-cero/AI_IMAGE_GENERATION_SETUP.md).

- [v1.6 — limpieza del título y salto directo al hangar](docs/villa-duarte-sector-cero/V1_6_TITLE_AND_INTRO_FLOW.md)
- [v1.7 — corrección del flujo de título y hangar](docs/villa-duarte-sector-cero/V1_7_TITLE_HANGAR_FIX.md)

## ROM editing toolchain (private builds only)

- Parameter profile: [`config/gba_lab.json`](config/gba_lab.json).
- Read-only audit: [`tools/gba_rom_audit.py`](tools/gba_rom_audit.py).
- Guarded local patching: [`tools/apply_guarded_patch.py`](tools/apply_guarded_patch.py).
- Staged mGBA capture runner: [`tools/run_gba_diagnostic.py`](tools/run_gba_diagnostic.py).
- Config-driven low-level mGBA Lua trace: [`tools/generate_mgba_lua_trace.py`](tools/generate_mgba_lua_trace.py) and [template](tools/mgba/trace_gba.lua.in).
- Guarded patch and hardware parameter tests run in GitHub Actions: [latest workflow](https://github.com/dicksonmancebo09-commits/trecetrece/actions/workflows/gba-diagnostic-toolchain.yml).
- Setup and usage: [mGBA Codespaces guide](docs/villa-duarte-sector-cero/MGBA_CODESPACES_SETUP.md).

Los binarios privados de ROM, partidas y parches de trabajo se mantienen en `private-roms/` (excluido de Git); esto separa el material local del código y los assets originales del proyecto, sin impedir la edición y prueba local. GitHub Actions automatiza pruebas de herramientas y unit tests. La validación de gameplay se realiza ejecutando el build privado en mGBA u otro emulador compatible y revisando capturas/logs; registra el resultado real de cada prueba.



## Auditoría de producción — 02-11-2026

- [Informe de auditoría de las 382 salas](docs/villa-duarte-sector-cero/PRODUCTION_AUDIT_2026-11-02.md).
- [Manifiesto consolidado de los cinco lotes](data/world/sector-cero-production-manifest-v1.json).
- [382 fichas técnicas por sala](data/world/sector-cero-room-technical-sheets-v1.json), con dimensiones, declaraciones de capas y referencias RoomEntry reconciliadas con el commit fijado; los contenidos comprimidos BG/clipdata y el cotejo binario con la ROM privada siguen pendientes.
- [Cruce RoomEntry corregido (CSV)](recovery/analysis/ROOM_ENTRY_REFERENCE_CROSSWALK_2026-11-03.csv) y [registro JSON](data/world/sector-cero-room-entry-reference-v1.json).
- [2.150 posiciones de sprites de referencia (CSV)](recovery/analysis/ROOM_SPRITE_PLACEMENTS_2026-11-03.csv), sin copiar gráficos comerciales.
- [Sincronizador de fichas y coordenadas](tools/sync_room_entry_reference.py) y [pruebas unitarias](tests/test_sync_room_entry_reference.py).
- [Siete atlas exportados a PNG indexado y GBA 4bpp/BGR555/LZ77](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41616265371); [descargar paquete GBA](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41616265371).
- [Validador estructural automático](tools/audit_sector_cero_rooms.py) y [pruebas unitarias](tests/test_audit_sector_cero_rooms.py).
- [Puerta de integración GBA y prueba vertical](docs/villa-duarte-sector-cero/ROM_INTEGRATION_GATE_2026-11-02.md).
- [Auditoría de payloads BG/clipdata no disponibles en la fuente pública](docs/villa-duarte-sector-cero/REFERENCE_MAP_PAYLOAD_AUDIT_2026-11-03.md).
- [Siete atlas GBA exportados, run final 41616265371](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/41616265371).
- [Cruce corregido RoomEntry → tileset → recursos (CSV)](recovery/analysis/ROOM_ENTRY_REFERENCE_CROSSWALK_2026-11-03.csv).
- [Registro JSON de RoomEntry de las 382 salas](data/world/sector-cero-room-entry-reference-v1.json).
- [2.150 ubicaciones de sprites de referencia por sala](recovery/analysis/ROOM_SPRITE_PLACEMENTS_2026-11-03.csv).

**Estado:** IDs, lotes y referencias de puertas auditados; coordenadas y entradas de tileset reconciliadas con la fuente de referencia. Roles creativos pendientes de revisión espacial. No se ha aplicado un parche ROM ni se ha declarado una prueba de juego superada.
## Extracción técnica de referencia y exportación de atlas — 02-11-2026

- [Extractor de dimensiones BG/clipdata y recuentos de sprites por sala](tools/extract_reference_room_metadata.py), fijado al commit de referencia `de76565c897c05838503717db9aa2adfe92aeba3`.
- [Renderizador de SVG a PNG indexado](tools/render_gba_atlas_indexed.py) con las 16 entradas exactas declaradas por cada atlas.
- [Manifiesto de los siete atlas](config/gba_atlas_export_manifest.json).
- [Workflow de extracción y exportación](.github/workflows/zector-cero-production-assets.yml): genera 7 PNG indexados, pasa cada PNG por el conversor 4bpp/BGR555/LZ77 y publica esos binarios como artifact de CI.
- Los mapas binarios de clipdata `.rle` no se copian desde la fuente pública; su extracción espacial requiere la ROM exacta disponible en `private-roms/`.
