#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
ROM_INPUT="${1:-}"
if [[ -z "$ROM_INPUT" || ! -f "$ROM_INPUT" ]]; then
  echo "Uso: bash recovery/scripts/run_rea_analysis.sh '/ruta/Metroid Fusion.gba'" >&2
  echo "El archivo debe existir y ser una copia que tengas derecho a analizar." >&2
  exit 2
fi

OUT="$ROOT/private-roms/rea-analysis"
mkdir -p "$OUT"
ROM="$(realpath "$ROM_INPUT")"

# Guard against accidentally tracking analysis results or copying the ROM.
if ! git -C "$ROOT" check-ignore -q private-roms/rea-analysis/probe.json; then
  echo "ERROR: private-roms/rea-analysis no está excluido por Git." >&2
  echo "Añade /private-roms/ a .git/info/exclude y vuelve a ejecutar." >&2
  exit 3
fi

printf 'ROM: %s\n' "$ROM" | tee "$OUT/input-path.txt"
sha256sum "$ROM" | tee "$OUT/sha256.txt"
sha1sum "$ROM" | tee "$OUT/sha1.txt"
stat -c '%n %s bytes' "$ROM" | tee "$OUT/size.txt"

if [[ -f "$ROOT/tools/metroid_gba_probe.py" ]]; then
  python3 "$ROOT/tools/metroid_gba_probe.py" "$ROM" --json --output "$OUT/rom-probe.json"
else
  echo "No se encontró tools/metroid_gba_probe.py; se continúa con preflight." | tee "$OUT/probe-warning.txt"
fi

{
  echo "=== Node ==="
  node --version 2>&1 || true
  echo "=== REA ==="
  rea --version 2>&1 || true
  echo "=== REA doctor ==="
  rea doctor --json 2>&1 || true
  echo "=== REA providers ==="
  rea providers --json 2>&1 || true
} | tee "$OUT/rea-preflight.txt"

if ! command -v rea >/dev/null 2>&1; then
  echo "REA no está instalado; el informe de identidad se guardó, pero no se ejecutó la inspección." | tee "$OUT/RESULT.txt"
  exit 4
fi

# Run with the documented CLI shape, preserving stderr/stdout even on failure.
set +e
rea inspect "$ROM" \
  --target-format raw-binary \
  --architecture arm \
  --entry-point 0x08000000 \
  --provider ghidra \
  --json > "$OUT/rea-raw-arm-triage.json" 2> "$OUT/rea-raw-arm-triage.stderr.txt"
STATUS=$?
set -e
printf 'rea_inspect_exit=%s\n' "$STATUS" | tee "$OUT/RESULT.txt"
if [[ $STATUS -ne 0 ]]; then
  echo "La inspección REA falló; revisa rea-preflight.txt y rea-raw-arm-triage.stderr.txt." >&2
  exit "$STATUS"
fi
echo "Salida REA guardada en $OUT. La vía ARM genérica es preliminar: valida código con Ghidra ARM:LE:32:v4t."
