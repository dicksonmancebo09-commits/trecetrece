# Sector Cero — análisis y código editable (entrega directa en Git)

Este directorio ya está dentro de la rama `agent/rea-editable-analysis`; no necesitas descargar un ZIP.

## Incorporarlo en tu Codespace

Desde el Codespace existente:

```bash
cd /workspaces/trecetrece
git status --short
git fetch origin agent/rea-editable-analysis
git switch --track origin/agent/rea-editable-analysis
```

Si `git status --short` muestra cambios locales que no quieres perder, no cambies de rama todavía; guarda esos cambios antes.

## Pruebas del código editable

```bash
cd /workspaces/trecetrece
cc -std=c11 -Wall -Wextra -Werror \
  recovery/src/reconstructed/game_mode_dispatch.c \
  recovery/tests/test_game_mode_dispatch.c \
  -o /tmp/sector_cero_dispatch_test
/tmp/sector_cero_dispatch_test
```

## Ejecutar preflight y REA

```bash
cd /workspaces/trecetrece
bash recovery/scripts/run_rea_analysis.sh \
  "/workspaces/gba/Metroid Fusion (USA, Australia).gba"
```

El informe y los artefactos derivados quedan bajo `private-roms/rea-analysis/`, no en `recovery/`. No se copia ni modifica la ROM.

## Qué significa este resultado

Los archivos C son un modelo parcial del arranque y del mapa de estados, no una recompilación completa ni jugable del título original. Los offsets de entrada y la tabla de despacho se han comprobado estáticamente; el comportamiento completo necesita REA/Ghidra en ARMv4T y comparación con mGBA.


## Informe estático de toda la ROM (2026-10-28)

- [Informe humano del barrido completo](analysis/full_rom_static_scan_2026-10-28.md)
- [Resumen de resultados en JSON](analysis/full_rom_static_scan_2026-10-28.json)

El informe recorre los 8 MiB e incluye cabecera/hash, arranque ARM/Thumb, los 15 destinos del despachador, referencias a la ventana de ROM, candidatos LZ77 decodificados, segmentos ASCII y entropía por ventanas. Es análisis estático de bytes; no debe confundirse con una descompilación semántica completa, ni con una ejecución REA/Ghidra/mGBA, que siguen pendientes.


## Siguiente fase: catalogar recursos comprimidos

- [Cola de prioridad LZ77](analysis/lz77_priority_queue_2026-10-28.md)
- [Script reproducible de catálogo](scripts/catalog_lz77_assets.py)
- [Pruebas unitarias del decodificador](tests/test_lz77_catalog.py)

El catálogo identifica streams candidatos y referencias de punteros; no cambia la ROM ni da por hecho que cada bloque sea un gráfico. Para generarlo en el Codespace:

```bash
cd /workspaces/trecetrece
python3 recovery/scripts/catalog_lz77_assets.py \
  "/workspaces/gba/Metroid Fusion (USA, Australia).gba"
```

Los resultados se guardan en `private-roms/rea-analysis/assets/`, excluido del repositorio. La prioridad inmediata es clasificar los primeros candidatos con formatos 4bpp/8bpp y paletas BGR555, y después encontrar las rutinas que los consumen. No modificar offsets hasta identificar el recurso y su uso.
