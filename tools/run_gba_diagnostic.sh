#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Uso: bash tools/run_gba_diagnostic.sh private-roms/ROM.gba [private-roms/diagnostics/NOMBRE]"
  exit 2
fi

ROM="$(realpath "$1")"
if [[ ! -f "$ROM" ]]; then
  echo "No se encuentra la ROM: $ROM" >&2
  exit 2
fi

case "$ROM" in
  "$ROOT"/private-roms/*) ;;
  *)
    echo "Por seguridad, guarda una copia local en private-roms/ (está excluido de Git)." >&2
    exit 2
    ;;
esac

MGBA_BIN="$(command -v mgba-qt 2>/dev/null || command -v mgba 2>/dev/null || true)"
if [[ -z "$MGBA_BIN" && -x /usr/games/mgba-qt ]]; then MGBA_BIN=/usr/games/mgba-qt; fi
if [[ -z "$MGBA_BIN" && -x /usr/games/mgba ]]; then MGBA_BIN=/usr/games/mgba; fi
if [[ -z "$MGBA_BIN" ]]; then
  echo "No se localiza mGBA. Ejecuta: bash tools/install_gba_emulator.sh" >&2
  exit 3
fi

for required in xvfb-run xdotool import identify zip python3; do
  if ! command -v "$required" >/dev/null 2>&1; then
    echo "Falta '$required'. Ejecuta: bash tools/install_gba_emulator.sh" >&2
    exit 3
  fi
done

if [[ $# -eq 2 ]]; then
  OUT_REL="$2"
else
  OUT_REL="private-roms/diagnostics/$(basename "$ROM" .gba)-$(date -u +%Y%m%dT%H%M%SZ)"
fi
case "$OUT_REL" in
  private-roms/diagnostics/*) ;;
  *)
    echo "La carpeta de resultados debe estar dentro de private-roms/diagnostics/." >&2
    exit 2
    ;;
esac

OUT_DIR="$ROOT/$OUT_REL"
ZIP_PATH="$ROOT/$OUT_REL.zip"
mkdir -p "$OUT_DIR"

ROM_BASENAME="$(basename "$ROM")"
ROM_SHA="$(sha256sum "$ROM" | awk '{print $1}')"
MGBA_VERSION="$("$MGBA_BIN" --version 2>&1 | head -n 3 || true)"

printf '%s\n' "$MGBA_VERSION" > "$OUT_DIR/emulator-version.txt"
printf '%s  %s\n' "$ROM_SHA" "$ROM_BASENAME" > "$OUT_DIR/rom-sha256.txt"
python3 "$ROOT/tools/metroid_gba_probe.py" "$ROM" --json > "$OUT_DIR/rom-header.json" 2> "$OUT_DIR/header-probe.stderr" || true

cat > "$OUT_DIR/README.txt" <<EOF
Diagnóstico mGBA — salida local
ROM: $ROM_BASENAME
SHA-256: $ROM_SHA
Emulador: $MGBA_VERSION

Archivos:
- 01-start.png: escritorio virtual unos segundos después de abrir la ROM.
- 02-after-start.png: escritorio virtual después de enviar Enter/START una vez.
- emulator.log: mensajes de mGBA.
- rom-header.json: metadatos de cabecera y sonda estática.
- runtime-status.txt: estado del proceso del emulador en cada captura.

Importante:
Que el proceso de mGBA siga vivo NO demuestra que el juego funcione.
Las capturas no validan todavía colisiones, movimiento, puertas, transiciones
ni jugabilidad completa. Este ZIP no incluye la ROM.
EOF

export GBA_DIAG_ROM="$ROM"
export GBA_DIAG_OUT="$OUT_DIR"
export GBA_DIAG_BIN="$MGBA_BIN"

set +e
xvfb-run -a --server-args="-screen 0 1280x960x24" bash -c '
  set -u
  export QT_QPA_PLATFORM=xcb
  export QT_OPENGL=software
  export LIBGL_ALWAYS_SOFTWARE=1
  export SDL_AUDIODRIVER=dummy

  "$GBA_DIAG_BIN" -l 15 "$GBA_DIAG_ROM" > "$GBA_DIAG_OUT/emulator.log" 2>&1 &
  emu_pid=$!
  echo "pid=$emu_pid" > "$GBA_DIAG_OUT/runtime-status.txt"

  sleep 5
  if kill -0 "$emu_pid" 2>/dev/null; then
    echo "initial_capture: emulator process alive after 5 seconds" >> "$GBA_DIAG_OUT/runtime-status.txt"
  else
    echo "initial_capture: emulator process exited before 5 seconds" >> "$GBA_DIAG_OUT/runtime-status.txt"
  fi

  import -window root "$GBA_DIAG_OUT/01-start.png" 2>> "$GBA_DIAG_OUT/capture.log" || true

  window_id="$(xdotool search --onlyvisible --pid "$emu_pid" 2>/dev/null | tail -n 1 || true)"
  if [[ -n "$window_id" ]]; then
    xdotool windowactivate --sync "$window_id" 2>/dev/null || true
    xdotool key --clearmodifiers --window "$window_id" Return 2>/dev/null || xdotool key --clearmodifiers Return 2>/dev/null || true
  else
    xdotool key --clearmodifiers Return 2>/dev/null || true
  fi

  sleep 5
  if kill -0 "$emu_pid" 2>/dev/null; then
    echo "after_start_capture: emulator process alive after second 5-second window" >> "$GBA_DIAG_OUT/runtime-status.txt"
  else
    echo "after_start_capture: emulator process exited before second capture" >> "$GBA_DIAG_OUT/runtime-status.txt"
  fi

  import -window root "$GBA_DIAG_OUT/02-after-start.png" 2>> "$GBA_DIAG_OUT/capture.log" || true

  kill "$emu_pid" 2>/dev/null || true
  wait "$emu_pid" 2>/dev/null || true
'
RUN_STATUS=$?
set -e

if [[ "$RUN_STATUS" -ne 0 ]]; then
  echo "La sesión xvfb/mGBA devolvió código $RUN_STATUS." >> "$OUT_DIR/runtime-status.txt"
fi

for image_file in "$OUT_DIR/01-start.png" "$OUT_DIR/02-after-start.png"; do
  if [[ -f "$image_file" ]]; then
    identify "$image_file" >> "$OUT_DIR/image-dimensions.txt" 2>&1 || true
  else
    echo "MISSING: $(basename "$image_file")" >> "$OUT_DIR/image-dimensions.txt"
  fi
done

(
  cd "$ROOT"
  zip -rq "$ZIP_PATH" "$OUT_REL"
)

echo
echo "Diagnóstico guardado en: $OUT_DIR"
echo "Paquete para compartir: $ZIP_PATH"
echo "El ZIP no contiene la ROM. Comparte ese ZIP para revisar capturas y logs."
