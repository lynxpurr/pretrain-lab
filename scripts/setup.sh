#!/usr/bin/env bash
# Create the project virtualenv and install the training/evaluation stack.
#
#   bash scripts/setup.sh
#
# Requirements:
#   - uv (https://docs.astral.sh/uv/)
#   - Python 3.12 (uv can download it)
#   - For CUDA training: NVIDIA driver + CUDA 12.8 compatible GPU (RTX 50 series)
#
# The script installs the CUDA 12.8 PyTorch wheel when nvidia-smi is present,
# otherwise the CPU wheel. Override with TORCH_INDEX=... if needed.
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
VENV="${VENV:-.venv-pre}"

if ! command -v uv >/dev/null 2>&1; then
  echo "[setup] uv not found. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "[setup] creating $VENV (Python $PYTHON_VERSION)"
  uv venv --python "$PYTHON_VERSION" "$VENV"
fi

if [ -n "${TORCH_INDEX:-}" ]; then
  INDEX="$TORCH_INDEX"
elif command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  INDEX="https://download.pytorch.org/whl/cu128"
else
  INDEX="https://download.pytorch.org/whl/cpu"
fi

echo "[setup] installing requirements (torch index: $INDEX)"
# Primary index = PyTorch (so torch resolves to the CUDA/CPU build); PyPI is
# the fallback for the other packages.
uv pip install --python "$VENV/bin/python" \
  --index-url "$INDEX" --extra-index-url https://pypi.org/simple \
  -r requirements.txt

echo "[setup] verifying"
"$VENV/bin/python" - <<'PY'
import torch, numpy, tokenizers, safetensors, gguf, matplotlib
print("torch      ", torch.__version__)
print("cuda       ", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device     ", torch.cuda.get_device_name(0))
print("numpy      ", numpy.__version__)
print("tokenizers ", tokenizers.__version__)
print("safetensors", safetensors.__version__)
print("gguf       ", gguf.__version__ if hasattr(gguf, "__version__") else "ok")
print("matplotlib ", matplotlib.__version__)
PY

echo "[setup] done. Optional HF stack: uv pip install --python $VENV/bin/python -r requirements-hf.txt"