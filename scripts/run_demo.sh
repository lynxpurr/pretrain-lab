#!/usr/bin/env bash
# Start the local zero-dependency chat demo against Ollama.
#
#   bash scripts/run_demo.sh
#   BIND=0.0.0.0 PORT=7860 bash scripts/run_demo.sh   # expose on LAN (unsafe, no auth)
#
# Prerequisites:
#   1. Ollama running at OLLAMA_HOST (default 127.0.0.1:11435)
#   2. Model created from the released GGUF, e.g.:
#        ( cd models/pretrain-lab-140m-sft-v2e-GGUF && \
#          OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \
#          -f Modelfile-sft-v2e-q8 )
set -euo pipefail
cd "$(dirname "$0")/.."

OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11435}"
MODEL="${MODEL:-pretrain-lab-sft-v2e-q8}"
PORT="${PORT:-7860}"
BIND="${BIND:-127.0.0.1}"
export OLLAMA_HOST

if ! curl -s --max-time 3 "http://${OLLAMA_HOST}/api/tags" >/dev/null; then
  echo "[demo] Ollama is not reachable at http://${OLLAMA_HOST}" >&2
  echo "       Start it with:" >&2
  echo "       OLLAMA_MODELS=\$HOME/.ollama/models OLLAMA_HOST=${OLLAMA_HOST} ollama serve" >&2
  exit 1
fi

if ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx "${MODEL}:latest"; then
  echo "[demo] model ${MODEL} not found. Create it from the released GGUF first:" >&2
  echo "       ( cd models/pretrain-lab-140m-sft-v2e-GGUF && \\" >&2
  echo "         OLLAMA_HOST=${OLLAMA_HOST} ollama create ${MODEL} -f Modelfile-sft-v2e-q8 )" >&2
  echo "       See docs/quickstart.md for the full sequence." >&2
  exit 1
fi

echo "[demo] http://127.0.0.1:${PORT}  (bind=${BIND}, ollama=${OLLAMA_HOST}, model=${MODEL})"
exec .venv-pre/bin/python -I tools/app_stdlib.py \
  --model "$MODEL" --port "$PORT" --bind "$BIND"