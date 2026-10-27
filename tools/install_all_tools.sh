#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
WITH_MODEL=0
WITH_BROWSERS=0
for arg in "$@"; do
  case "$arg" in
    --with-model) WITH_MODEL=1 ;;
    --with-browsers) WITH_BROWSERS=1 ;;
    --help|-h) echo "Usage: bash tools/install_all_tools.sh [--with-model] [--with-browsers]"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done
echo "=== 1/3: Agent skills for GitHub Copilot ==="
bash tools/install_project_skills.sh
echo
echo "=== 2/3: Scrapling research environment ==="
if [ "$WITH_BROWSERS" -eq 1 ]; then bash tools/install_scrapling.sh --with-browsers; else bash tools/install_scrapling.sh; fi
echo
echo "=== 3/3: REA + OmniRoute + ComfyUI ==="
if [ "$WITH_MODEL" -eq 1 ]; then bash tools/install_ai_stack.sh --with-model; else bash tools/install_ai_stack.sh; fi
echo
echo "All requested software installation steps completed. This does not mean image generation is tested."
echo "Verify ComfyUI via a generation workflow and OmniRoute via its dashboard."
