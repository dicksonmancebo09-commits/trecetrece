param([switch]$WithBrowsers)
$ErrorActionPreference = "Stop"
$AiRoot = Join-Path $HOME "AI-Tools"
$VenvDir = Join-Path $AiRoot "research-venv"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3 is required." }
New-Item -ItemType Directory -Force -Path $AiRoot | Out-Null
if (-not (Test-Path (Join-Path $VenvDir "Scripts\python.exe"))) { & python -m venv $VenvDir }
$Py = Join-Path $VenvDir "Scripts\python.exe"
& $Py -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $Py -m pip install "scrapling[fetchers]"
if ($LASTEXITCODE -ne 0) { throw "Scrapling install failed." }
& $Py -c "import scrapling; from scrapling.fetchers import Fetcher, DynamicFetcher; print('Scrapling import OK')"
if ($LASTEXITCODE -ne 0) { throw "Scrapling import verification failed." }
if ($WithBrowsers) {
  & (Join-Path $VenvDir "Scripts\scrapling.exe") install
  if ($LASTEXITCODE -ne 0) { throw "Scrapling browser installation failed." }
} else { Write-Host "Browser binaries not downloaded. Rerun with -WithBrowsers for JS-rendered websites." }
Write-Host "Scrapling environment: $VenvDir"
