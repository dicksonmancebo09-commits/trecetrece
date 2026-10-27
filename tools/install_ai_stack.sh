#!/usr/bin/env bash
set -Eeuo pipefail

AI_ROOT="${AI_ROOT:-$HOME/AI-Tools}"
COMFY_DIR="${COMFYUI_DIR:-$AI_ROOT/ComfyUI}"
VENV_DIR="${COMFY_VENV:-$AI_ROOT/comfy-venv}"
MODEL_URL="https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
MODEL_SHA256="6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa"
WITH_MODEL=0

for arg in "$@"; do
  case "$arg" in
    --with-model) WITH_MODEL=1 ;;
    --help|-h)
      echo "Usage: bash tools/install_ai_stack.sh [--with-model]"
      echo "Installs REA, OmniRoute and ComfyUI. --with-model downloads a 4.27 GB SD 1.5 checkpoint."
      exit 0
      ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

command -v node >/dev/null || { echo "ERROR: Node.js is required (22.22+ recommended)." >&2; exit 1; }
command -v npm >/dev/null || { echo "ERROR: npm is required." >&2; exit 1; }
command -v git >/dev/null || { echo "ERROR: Git is required." >&2; exit 1; }
command -v curl >/dev/null || { echo "ERROR: curl is required." >&2; exit 1; }
PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null || { echo "ERROR: Python 3.12+ is required. In Codespaces the devcontainer feature installs it." >&2; exit 1; }
"$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)' || {
  echo "ERROR: Python 3.12 or newer is required. Found: $("$PYTHON_BIN" --version 2>&1)" >&2
  exit 1
}

mkdir -p "$AI_ROOT"

echo "[1/4] Installing REA and OmniRoute CLI tools..."
npm install --global --allow-scripts=omniroute,keytar,onnxruntime-node,@parcel/watcher,@swc/core,protobufjs,esbuild rea-agents@6.8.0 omniroute@latest
rea --version
omniroute --version 2>/dev/null || true

echo "[2/4] Installing ComfyUI source..."
if [ ! -d "$COMFY_DIR/.git" ]; then
  git clone --depth 1 https://github.com/Comfy-Org/ComfyUI.git "$COMFY_DIR"
else
  echo "ComfyUI already exists at $COMFY_DIR; keeping the current checkout."
fi

echo "[3/4] Preparing Python environment and dependencies..."
"$PYTHON_BIN" -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip

if [ -n "${PYTORCH_INDEX_URL:-}" ]; then
  TORCH_INDEX="$PYTORCH_INDEX_URL"
elif command -v nvidia-smi >/dev/null 2>&1; then
  GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
  if [[ "$GPU_NAME" =~ GTX[[:space:]]*(10|9|7|6)[0-9]{2} ]]; then
    TORCH_INDEX="https://download.pytorch.org/whl/cu126"
  else
    TORCH_INDEX="https://download.pytorch.org/whl/cu130"
  fi
else
  TORCH_INDEX="https://download.pytorch.org/whl/cpu"
fi

echo "PyTorch index: $TORCH_INDEX"
python -m pip install torch torchvision torchaudio --index-url "$TORCH_INDEX"
FILTERED_REQUIREMENTS="$(mktemp)"
trap 'rm -f "$FILTERED_REQUIREMENTS"' EXIT
grep -Eiv '^[[:space:]]*(torch|torchvision|torchaudio)([<=>~![:space:]]|$)' "$COMFY_DIR/requirements.txt" > "$FILTERED_REQUIREMENTS" || true
python -m pip install -r "$FILTERED_REQUIREMENTS"

STAMP="$(git -C "$COMFY_DIR" rev-parse HEAD)-$(sha256sum "$COMFY_DIR/requirements.txt" | awk '{print $1}')-$TORCH_INDEX"
printf '%s\n' "$STAMP" > "$VENV_DIR/.trecetrece-install-stamp"

echo "[4/4] Checking ComfyUI import and tool versions..."
python -c 'import torch; print("PyTorch:", torch.__version__); print("CUDA available:", torch.cuda.is_available())'
python -c "import sys; sys.path.insert(0, '$COMFY_DIR'); import nodes; print('ComfyUI Python imports: OK')"
rea --version
omniroute --version 2>/dev/null || true

if [ "$WITH_MODEL" -eq 1 ]; then
  MODEL_DIR="$COMFY_DIR/models/checkpoints"
  MODEL_PATH="$MODEL_DIR/v1-5-pruned-emaonly.safetensors"
  PARTIAL_PATH="$MODEL_PATH.partial"
  mkdir -p "$MODEL_DIR"
  if [ -f "$MODEL_PATH" ] && [ "$(sha256sum "$MODEL_PATH" | awk '{print $1}')" = "$MODEL_SHA256" ]; then
    echo "Stable Diffusion 1.5 checkpoint already present and SHA-256 verified."
  else
    echo "Downloading Stable Diffusion 1.5 checkpoint (4.27 GB)..."
    if [ -f "$PARTIAL_PATH" ]; then
      curl -fL --retry 3 --retry-delay 2 --continue-at - "$MODEL_URL" -o "$PARTIAL_PATH"
    else
      curl -fL --retry 3 --retry-delay 2 "$MODEL_URL" -o "$PARTIAL_PATH"
    fi
    echo "$MODEL_SHA256  $PARTIAL_PATH" | sha256sum -c -
    mv "$PARTIAL_PATH" "$MODEL_PATH"
  fi
else
  echo
  echo "Checkpoint not downloaded automatically (4.27 GB)."
  echo "When ready, run: bash tools/install_ai_stack.sh --with-model"
fi

echo
echo "Installation step finished."
echo "ComfyUI folder: $COMFY_DIR"
echo "ComfyUI Python: $VENV_DIR/bin/python"
echo "OmniRoute dashboard: http://localhost:20128/dashboard"
echo "ComfyUI image generator: http://localhost:8188"
echo "Note: this script installs tools; it does not prove image generation until a checkpoint is present and a workflow is run."
