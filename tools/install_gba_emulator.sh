#!/usr/bin/env bash
set -Eeuo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Este instalador automático requiere Debian/Ubuntu con apt-get." >&2
  exit 2
fi

if [[ "$(id -u)" -ne 0 ]] && ! command -v sudo >/dev/null 2>&1; then
  echo "Se necesitan permisos de administrador (root o sudo)." >&2
  exit 2
fi

if [[ "$(id -u)" -eq 0 ]]; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y mgba-qt mgba-sdl xvfb xauth xdotool imagemagick openbox zip python3 lua5.4 coreutils
else
  sudo apt-get update
  sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y mgba-qt mgba-sdl xvfb xauth xdotool imagemagick openbox zip python3 lua5.4 coreutils
fi

MGBA_BIN="$(command -v mgba-qt 2>/dev/null || command -v mgba 2>/dev/null || true)"
if [[ -z "$MGBA_BIN" && -x /usr/games/mgba-qt ]]; then MGBA_BIN=/usr/games/mgba-qt; fi
if [[ -z "$MGBA_BIN" && -x /usr/games/mgba ]]; then MGBA_BIN=/usr/games/mgba; fi

if [[ -z "$MGBA_BIN" ]]; then
  echo "No se localizó el ejecutable después de instalar los paquetes." >&2
  exit 3
fi

echo "Emulador localizado: $MGBA_BIN"
"$MGBA_BIN" --version 2>&1 | head -n 3 || true
for required in xvfb-run xdotool import zip python3 luac5.4 openbox; do
  command -v "$required" >/dev/null 2>&1 || { echo "Falta el comando: $required" >&2; exit 4; }
done

echo "== Validando generación y sintaxis de la traza Lua =="
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
mkdir -p private-roms/diagnostics
python3 tools/generate_mgba_lua_trace.py
luac5.4 -p private-roms/diagnostics/mgba-trace-generated.lua
echo "Perfil, generador y sintaxis Lua verificados."
echo
echo "Instalación verificada. Esto no ejecuta ni valida una ROM."
echo "Uso: bash tools/run_gba_diagnostic.sh private-roms/ARCHIVO.gba"
