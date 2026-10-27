param()

$ErrorActionPreference = "Stop"
$AiRoot = Join-Path $HOME "AI-Tools"
$ComfyDir = Join-Path $AiRoot "ComfyUI"
$VenvDir = Join-Path $AiRoot "comfy-venv"
$LogDir = Join-Path $AiRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Py = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Get-Command omniroute -ErrorAction SilentlyContinue)) { throw "OmniRoute missing. Run .\tools\install_ai_stack.ps1 first." }
if (-not (Test-Path $Py) -or -not (Test-Path (Join-Path $ComfyDir "main.py"))) { throw "ComfyUI missing. Run .\tools\install_ai_stack.ps1 first." }

$ListeningPorts = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty LocalPort -Unique)
if (20128 -notin $ListeningPorts) {
  Start-Process -FilePath "omniroute" -WorkingDirectory $AiRoot -Environment @{ BROWSER = "none" } -RedirectStandardOutput (Join-Path $LogDir "omniroute.log") -RedirectStandardError (Join-Path $LogDir "omniroute.err.log")
} else { Write-Host "OmniRoute already listening on port 20128." }

if (8188 -notin $ListeningPorts) {
  $args = @((Join-Path $ComfyDir "main.py"), "--listen", "0.0.0.0", "--port", "8188")
  $cuda = & $Py -c "import torch; print('1' if torch.cuda.is_available() else '0')"
  if ($cuda.Trim() -ne "1") { $args += "--cpu" }
  Start-Process -FilePath $Py -WorkingDirectory $ComfyDir -ArgumentList $args -RedirectStandardOutput (Join-Path $LogDir "comfyui.log") -RedirectStandardError (Join-Path $LogDir "comfyui.err.log")
} else { Write-Host "ComfyUI already listening on port 8188." }

Write-Host "OmniRoute dashboard: http://localhost:20128/dashboard"
Write-Host "OmniRoute API: http://localhost:20128/v1"
Write-Host "ComfyUI: http://localhost:8188"
if (-not (Test-Path (Join-Path $ComfyDir "models\checkpoints\v1-5-pruned-emaonly.safetensors"))) {
  Write-Warning "No default Stable Diffusion checkpoint. Rerun .\tools\install_ai_stack.ps1 -WithModel to download 4.27 GB."
}
Write-Host "Logs: $LogDir"
