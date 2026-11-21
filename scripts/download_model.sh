#!/usr/bin/env bash
# Download the released model weights (Hugging Face Hub).
#
#   bash scripts/download_model.sh
#
# The repositories below are the v1.0 release locations. Override them if you
# host the model under different names.
set -euo pipefail
cd "$(dirname "$0")/.."

HF_CLI="${HF_CLI:-hf}"
HF_REPO="${HF_REPO:-lynxpurr/pretrain-lab-140m-sft-v2e}"
HF_GGUF_REPO="${HF_GGUF_REPO:-lynxpurr/pretrain-lab-140m-sft-v2e-GGUF}"

if ! command -v "$HF_CLI" >/dev/null 2>&1; then
  echo "[model] '$HF_CLI' CLI not found. Install it with:" >&2
  echo "        pip install -U huggingface_hub" >&2
  exit 1
fi

mkdir -p models

echo "[model] downloading $HF_REPO"
"$HF_CLI" download "$HF_REPO" --local-dir "models/$(basename "$HF_REPO")"

echo "[model] downloading GGUF files from $HF_GGUF_REPO"
"$HF_CLI" download "$HF_GGUF_REPO" \
  --include "*.gguf" \
  --include "Modelfile*" \
  --local-dir "models/$(basename "$HF_GGUF_REPO")"

echo "[model] done."
echo "  HF weights : models/$(basename "$HF_REPO")"
echo "  Eval ckpt  : models/$(basename "$HF_REPO")/last.pt (only needed for tools/eval.py)"
echo "  GGUF files : models/$(basename "$HF_GGUF_REPO")"
echo
echo "Create an Ollama model from the Q8 GGUF (the Modelfile uses a relative FROM):"
echo "  ( cd models/$(basename "$HF_GGUF_REPO") && \\"
echo "    OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \\"
echo "    -f Modelfile-sft-v2e-q8 )"