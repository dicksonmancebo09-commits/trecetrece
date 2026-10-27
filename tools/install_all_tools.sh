#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
echo "=== 1/3: Agent skills for GitHub Copilot ==="
bash tools/install_project_skills.sh
echo
echo "=== 2/3: Scrapling research environment ==="
bash tools/install_scrapling.sh
echo
echo "=== 3/3: REA + OmniRoute + ComfyUI ==="
bash tools/install_ai_stack.sh
echo
echo "All requested software installation steps completed. This does not mean image generation is tested."
echo "For Stable Diffusion weights (4.27 GB): bash tools/install_ai_stack.sh --with-model"
