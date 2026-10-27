$ErrorActionPreference = "Stop"
$Root = (& git rev-parse --show-toplevel 2>$null)
if (-not $Root) { $Root = (Get-Location).Path }
Set-Location $Root
Write-Host "=== 1/3: Agent skills for GitHub Copilot ==="
& "$Root\tools\install_project_skills.ps1"
if ($LASTEXITCODE -ne 0) { throw "Project skills installation failed." }
Write-Host "=== 2/3: Scrapling research environment ==="
& "$Root\tools\install_scrapling.ps1"
if ($LASTEXITCODE -ne 0) { throw "Scrapling installation failed." }
Write-Host "=== 3/3: REA + OmniRoute + ComfyUI ==="
& "$Root\tools\install_ai_stack.ps1"
if ($LASTEXITCODE -ne 0) { throw "AI stack installation failed." }
Write-Host "All requested software installation steps completed. This does not mean image generation is tested."
Write-Host "For Stable Diffusion weights (4.27 GB): .\tools\install_ai_stack.ps1 -WithModel"
