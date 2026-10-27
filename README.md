# trecetrece

Repositorio de trabajo para investigar herramientas, organizar recursos con licencia compatible y desarrollar un videojuego original de acción/plataformas con identidad dominicana.

**Título oficial del juego: LATINO AMÉRICA Zector Cero.**  
La dirección artística se inspira en Villa Duarte y sus barrios de Santo Domingo Este. «Villa Duarte — Sector Cero» aparece en documentos previos como nombre provisional o etiqueta de desarrollo; no es el título oficial vigente.

## Documentación y continuidad

> **Aviso de build:** la v1.3 ha sido retirada como candidata funcional tras el informe de crash y pantalla inicial ilegible. La causa exacta del crash sigue sin reproducirse en emulador.

- [Estado de continuidad del proyecto — LATINO AMÉRICA Zector Cero](docs/villa-duarte-sector-cero/PROJECT_STATE_HANDOFF.md)
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

## Regla de trabajo

Metroid Fusion es una referencia de estudio para comprender estructura, ritmo, mapas y mecánicas. El objetivo a largo plazo es crear un juego propio, no distribuir una ROM modificada. **No subir a este repositorio ROMs comerciales, ROMs derivadas, parches IPS/BPS/UPS ni sprites, música, mapas o código propietario copiados de juegos comerciales.**

Los enlaces a herramientas y repositorios externos documentan fuentes de investigación; no implican afiliación ni aprobación de sus autores.

> **Aviso:** este repositorio está configurado como público. Los documentos y nombres de archivo que se añadan a una rama pueden ser visibles públicamente, aunque no contengan el material del juego.

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
