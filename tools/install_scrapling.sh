#!/usr/bin/env bash
set -Eeuo pipefail

AI_ROOT="${AI_ROOT:-$HOME/AI-Tools}"
VENV_DIR="${SCRAPLING_VENV:-$AI_ROOT/research-venv}"
WITH_BROWSERS=0
for arg in "$@"; do
  case "$arg" in
    --with-browsers) WITH_BROWSERS=1 ;;
    --help|-h) echo "Usage: bash tools/install_scrapling.sh [--with-browsers]"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done
PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null || { echo "ERROR: Python 3 is required." >&2; exit 1; }
mkdir -p "$AI_ROOT"
"$PYTHON_BIN" -m venv "$VENV_DIR"
PY="$VENV_DIR/bin/python"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install 'scrapling[fetchers]'
"$PY" -c 'import scrapling; from scrapling.fetchers import Fetcher, DynamicFetcher; print("Scrapling import OK:", getattr(scrapling, "__version__", "version not exposed"))'
if [ "$WITH_BROWSERS" -eq 1 ]; then
  "$VENV_DIR/bin/scrapling" install
else
  echo "Browser binaries not downloaded by default. For JS-rendered pages run: bash tools/install_scrapling.sh --with-browsers"
fi
echo "Scrapling Python environment: $VENV_DIR"
echo "To use it: $PY -c 'from scrapling.fetchers import Fetcher'"
