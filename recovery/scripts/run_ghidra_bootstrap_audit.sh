#!/usr/bin/env bash
# Run a narrow, reproducible Ghidra ARMv4T/Thumb audit against the local
# Metroid Fusion AMTE ROM. The ROM and all generated reports stay outside Git.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ROM_INPUT="${1:-/workspaces/gba/Metroid Fusion (USA, Australia).gba}"
GHIDRA="${GHIDRA_INSTALL_DIR:-$HOME/AI-Tools/ghidra_12.1.4_PUBLIC}"
PROJECTS="${GHIDRA_PROJECTS_DIR:-$HOME/AI-Tools/ghidra-projects}"
PROJECT="${GHIDRA_PROJECT_NAME:-MetroidFusion_AMTE_ARMv4T}"
PROJECT_PROGRAM="Metroid Fusion (USA, Australia).gba"

PROBE="$ROOT/tools/metroid_bootstrap_probe.py"
GHIDRA_SCRIPT="$ROOT/recovery/ghidra_scripts/MetroidFusionBootstrapAudit.java"
REPORT_DIR="$HOME/AI-Tools/ghidra-projects/reports"
REPORT="$REPORT_DIR/metroid-fusion-amte-bootstrap.json"
LOG="$REPORT_DIR/metroid-fusion-amte-ghidra-audit.log"

fail() {
  echo "ERROR: $*" >&2
  exit 2
}

command -v python3 >/dev/null 2>&1 || fail "python3 is required."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."

ROM="$(realpath "$ROM_INPUT")"
ROOT="$(realpath "$ROOT")"

[[ -f "$ROM" ]] || fail "ROM not found: $ROM"
case "$ROM" in
  "$ROOT"/*)
    fail "Keep the commercial ROM outside the Git repository. Current path: $ROM"
    ;;
esac

[[ -x "$GHIDRA/support/analyzeHeadless" ]] || fail "Ghidra analyzeHeadless not found: $GHIDRA"
[[ -f "$PROBE" ]] || fail "Missing byte-level verifier: $PROBE"
[[ -f "$GHIDRA_SCRIPT" ]] || fail "Missing Ghidra script: $GHIDRA_SCRIPT"
[[ -d "$PROJECTS/$PROJECT.rep" ]] || fail "Ghidra project repository not found: $PROJECTS/$PROJECT.rep"
[[ -f "$PROJECTS/$PROJECT.gpr" ]] || fail "Ghidra project file not found: $PROJECTS/$PROJECT.gpr"

mkdir -p "$REPORT_DIR"

echo "===== 1. READ-ONLY ROM IDENTITY AND BYTE CHECKS ====="
python3 "$PROBE" "$ROM" --json --output "$REPORT"

echo "===== 2. GHI DRA VERSION ====="
"$GHIDRA/support/analyzeHeadless" -version 2>&1 || true

echo "===== 3. TARGETED ARMv4T + THUMB AUDIT ====="
echo "ROM: $ROM"
echo "Project: $PROJECTS/$PROJECT"
echo "Ghidra script: $GHIDRA_SCRIPT"
echo "JSON report: $REPORT"
echo "Text log: $LOG"

"$GHIDRA/support/analyzeHeadless" \
  "$PROJECTS" \
  "$PROJECT" \
  -process "$PROJECT_PROGRAM" \
  -noanalysis \
  -scriptPath "$ROOT/recovery/ghidra_scripts" \
  -postScript MetroidFusionBootstrapAudit.java \
  2>&1 | tee "$LOG"

echo "===== 4. COMPLETE ====="
echo "Byte-level report: $REPORT"
echo "Ghidra trace: $LOG"
echo "The ROM was opened read-only; annotations were saved only in the Ghidra project."
