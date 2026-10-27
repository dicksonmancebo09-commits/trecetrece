#!/usr/bin/env bash
set -Eeuo pipefail

AI_ROOT="${AI_ROOT:-$HOME/AI-Tools}"
COMFY_DIR="${COMFYUI_DIR:-$AI_ROOT/ComfyUI}"
VENV_DIR="${COMFY_VENV:-$AI_ROOT/comfy-venv}"
LOG_DIR="$AI_ROOT/logs"
mkdir -p "$LOG_DIR"

if ! command -v omniroute >/dev/null 2>&1; then
  echo "OmniRoute is not installed. Run: bash tools/install_ai_stack.sh" >&2
  exit 1
fi
if [ ! -x "$VENV_DIR/bin/python" ] || [ ! -f "$COMFY_DIR/main.py" ]; then
  echo "ComfyUI is not installed. Run: bash tools/install_ai_stack.sh" >&2
  exit 1
fi

if curl -fsS http://127.0.0.1:20128/dashboard >/dev/null 2>&1; then
  echo "OmniRoute already responds on port 20128."
else
  echo "Starting OmniRoute..."
  (cd "$AI_ROOT" && nohup omniroute > "$LOG_DIR/omniroute.log" 2>&1 &)
fi

if curl -fsS http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
  echo "ComfyUI already responds on port 8188."
else
  echo "Starting ComfyUI..."
  DEVICE_ARGS=()
  if ! "$VENV_DIR/bin/python" -c 'import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)' >/dev/null 2>&1; then
    DEVICE_ARGS+=(--cpu)
  fi
  (cd "$COMFY_DIR" && nohup env BROWSER=none "$VENV_DIR/bin/python" main.py --listen 0.0.0.0 --port 8188 "${DEVICE_ARGS[@]}" > "$LOG_DIR/comfyui.log" 2>&1 &)
fi

sleep 2
echo
echo "OmniRoute dashboard: http://localhost:20128/dashboard"
echo "OmniRoute OpenAI-compatible API: http://localhost:20128/v1"
echo "ComfyUI: http://localhost:8188"
if [ ! -f "$COMFY_DIR/models/checkpoints/v1-5-pruned-emaonly.safetensors" ]; then
  echo "WARNING: no default SD 1.5 checkpoint found; ComfyUI opens, but generation needs a model."
  echo "Download it with: bash tools/install_ai_stack.sh --with-model"
fi
echo "Logs: $LOG_DIR"
