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
