param(
  [switch]$WithModel
)

$ErrorActionPreference = "Stop"
$AiRoot = Join-Path $HOME "AI-Tools"
$ComfyDir = Join-Path $AiRoot "ComfyUI"
$VenvDir = Join-Path $AiRoot "comfy-venv"
$ModelUrl = "https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
$ModelSha256 = "6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa"

foreach ($commandName in @("node", "npm", "git", "python", "curl.exe")) {
  if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
    throw "Missing command '$commandName'. Install Node.js 22+, Git, Python 3.12+, and curl, then rerun this script."
  }
}
$pythonVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$pythonVersion -lt [version]"3.12") { throw "Python 3.12+ required. Found $pythonVersion." }

New-Item -ItemType Directory -Force -Path $AiRoot | Out-Null
Write-Host "[1/4] Installing REA and OmniRoute..."
& npm install --global rea-agents@6.8.0 omniroute@latest
if ($LASTEXITCODE -ne 0) { throw "npm global installation failed." }
& rea --version
& omniroute --version

Write-Host "[2/4] Installing ComfyUI source..."
if (-not (Test-Path (Join-Path $ComfyDir ".git"))) {
  & git clone --depth 1 https://github.com/Comfy-Org/ComfyUI.git $ComfyDir
  if ($LASTEXITCODE -ne 0) { throw "ComfyUI clone failed." }
} else {
  Write-Host "ComfyUI already exists at $ComfyDir; keeping current checkout."
}

Write-Host "[3/4] Preparing Python venv and dependencies..."
if (-not (Test-Path $VenvDir)) { & python -m venv $VenvDir }
$Py = Join-Path $VenvDir "Scripts\python.exe"
& $Py -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

$GpuName = ""
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
  $GpuName = ((& nvidia-smi --query-gpu=name --format=csv,noheader 2>$null | Select-Object -First 1) -as [string]).Trim()
}
$TorchIndex = "https://download.pytorch.org/whl/cpu"
if ($GpuName) {
  if ($GpuName -match 'GTX\s*(10|9|7|6)[0-9]{2}') {
    $TorchIndex = "https://download.pytorch.org/whl/cu126"
  } else {
    $TorchIndex = "https://download.pytorch.org/whl/cu130"
  }
}
Write-Host "Detected GPU: $(if ($GpuName) { $GpuName } else { 'none; CPU mode' })"
Write-Host "PyTorch index: $TorchIndex"
& $Py -m pip install torch torchvision torchaudio --index-url $TorchIndex
if ($LASTEXITCODE -ne 0) { throw "PyTorch install failed. Check GPU/driver compatibility and the official ComfyUI install guide." }

$Filtered = Join-Path $env:TEMP "trecetrece-comfy-requirements.txt"
Get-Content (Join-Path $ComfyDir "requirements.txt") |
  Where-Object { $_ -notmatch '^\s*(torch|torchvision|torchaudio)([<=>~!\s]|$)' } |
  Set-Content -Encoding utf8 $Filtered
& $Py -m pip install -r $Filtered
if ($LASTEXITCODE -ne 0) { throw "ComfyUI dependency installation failed." }

Write-Host "[4/4] Verifying Python imports..."
& $Py -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
if ($LASTEXITCODE -ne 0) { throw "Torch import check failed." }
$env:COMFYUI_PATH = $ComfyDir
& $Py -c "import sys,os; sys.path.insert(0, os.environ['COMFYUI_PATH']); import nodes; print('ComfyUI Python imports: OK')"
if ($LASTEXITCODE -ne 0) { throw "ComfyUI import check failed." }
& rea --version
& omniroute --version

if ($WithModel) {
  $ModelDir = Join-Path $ComfyDir "models\checkpoints"
  New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
  $ModelPath = Join-Path $ModelDir "v1-5-pruned-emaonly.safetensors"
  $Partial = "$ModelPath.partial"
  if ((Test-Path $ModelPath) -and ((Get-FileHash $ModelPath -Algorithm SHA256).Hash.ToLowerInvariant() -eq $ModelSha256)) {
    Write-Host "Stable Diffusion 1.5 checkpoint already present and verified."
  } else {
    Write-Host "Downloading Stable Diffusion 1.5 checkpoint (4.27 GB)..."
    & curl.exe -fL --retry 3 --retry-delay 2 $ModelUrl -o $Partial
    if ($LASTEXITCODE -ne 0) { throw "Model download failed." }
    $ActualHash = (Get-FileHash $Partial -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualHash -ne $ModelSha256) { Remove-Item $Partial -Force; throw "Model SHA-256 mismatch; downloaded file was removed." }
    Move-Item -Force $Partial $ModelPath
  }
} else {
  Write-Host "Checkpoint not downloaded automatically (4.27 GB). Rerun with -WithModel when ready."
}

Write-Host ""
Write-Host "Installation script completed."
Write-Host "ComfyUI: $ComfyDir"
Write-Host "OmniRoute dashboard: http://localhost:20128/dashboard"
Write-Host "ComfyUI image generator: http://localhost:8188"
Write-Host "This verifies imports only; generate a test image before marking the generator operational."
