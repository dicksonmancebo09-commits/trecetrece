#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
command -v node >/dev/null || { echo "ERROR: Node.js is required to install project skills." >&2; exit 1; }
command -v npx >/dev/null || { echo "ERROR: npx is required." >&2; exit 1; }

install_skill() {
  local repo="$1"
  local skill="$2"
  local target=".github/skills/$skill/SKILL.md"
  if [ -f "$target" ]; then
    echo "[skills] Already installed: $skill"
    return 0
  fi
  echo "[skills] Installing $skill from $repo for GitHub Copilot..."
  npx --yes skills add "$repo" --skill "$skill" --agent github-copilot --copy --yes
  if [ ! -f "$target" ]; then
    echo "ERROR: installer completed but expected skill file was not created: $target" >&2
    exit 1
  fi
}

install_skill "DietrichGebert/ponytail" "ponytail"
install_skill "blader/humanizer" "humanizer"
install_skill "pbakaus/impeccable" "impeccable"
install_skill "nextlevelbuilder/ui-ux-pro-max-skill" "ui-ux-pro-max"

echo "Project skills installed and verified:"
for skill in ponytail humanizer impeccable ui-ux-pro-max; do
  test -s ".github/skills/$skill/SKILL.md"
  printf ' - %s: %s bytes\n' "$skill" "$(wc -c < ".github/skills/$skill/SKILL.md" | tr -d ' ')"
done
