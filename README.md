# trecetrece

Repositorio de trabajo para investigar herramientas, organizar recursos con licencia compatible y desarrollar un videojuego original de acción/plataformas con identidad dominicana. Nombre de trabajo: **Villa Duarte — Sector Cero** (relacionado con la línea creativa Barrio Z).

## Documentación del proyecto

- [Resumen y estado actual](docs/villa-duarte-sector-cero/README.md)
- [Herramientas y repositorios de referencia](docs/villa-duarte-sector-cero/research/TOOLS_AND_REPOSITORIES.md)
- [Notas técnicas de la ROM de referencia](docs/villa-duarte-sector-cero/research/ROM_TECHNICAL_NOTES.md)
- [Dirección artística, procedencia y licencias](docs/villa-duarte-sector-cero/research/ART_DIRECTION_AND_LICENSES.md)
- [Bitácora de investigación y pruebas](docs/villa-duarte-sector-cero/WORKLOG.md)
- [Auditoría de los archivos existentes](docs/villa-duarte-sector-cero/REPOSITORY_AUDIT.md)
- [Registro de fuentes y verificación](docs/villa-duarte-sector-cero/research/RESEARCH_REGISTER.md)
- [Instalar REA en Codespaces](docs/villa-duarte-sector-cero/research/REA_CODESPACES_SETUP.md)
- [Flujo de R.E. para Metroid Fusion](docs/villa-duarte-sector-cero/research/METROID_REA_WORKFLOW.md)
- [Agente Metroid RE](.github/agents/metroid-re.agent.md)
- [Sonda de metadatos GBA](tools/metroid_gba_probe.py)

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
