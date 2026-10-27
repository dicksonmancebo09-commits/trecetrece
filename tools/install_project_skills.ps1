$ErrorActionPreference = "Stop"
$Root = (& git rev-parse --show-toplevel 2>$null)
if (-not $Root) { $Root = (Get-Location).Path }
Set-Location $Root
foreach ($cmd in @("node", "npx", "git")) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "Missing required command: $cmd" }
}

function Install-ProjectSkill([string]$Repository, [string]$Skill) {
  $Target = Join-Path $Root ".github\skills\$Skill\SKILL.md"
  if (Test-Path $Target) { Write-Host "[skills] Already installed: $Skill"; return }
  Write-Host "[skills] Installing $Skill from $Repository for GitHub Copilot..."
  & npx --yes skills add $Repository --skill $Skill --agent github-copilot --copy --yes
  if ($LASTEXITCODE -ne 0) { throw "Skill installer failed: $Skill" }
  if (-not (Test-Path $Target)) { throw "Expected skill file was not created: $Target" }
}

Install-ProjectSkill "DietrichGebert/ponytail" "ponytail"
Install-ProjectSkill "blader/humanizer" "humanizer"
Install-ProjectSkill "pbakaus/impeccable" "impeccable"
Install-ProjectSkill "nextlevelbuilder/ui-ux-pro-max-skill" "ui-ux-pro-max"
Write-Host "All four Copilot skills are present in .github\skills."
