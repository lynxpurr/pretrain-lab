#!/usr/bin/env bash
# Reproduce the released model's dev-set and 90-question holdout evaluation.
#
#   bash scripts/reproduce_eval.sh [checkpoint.pt]
#
# Default checkpoint: out/sft-v2e/last.pt
# The released .pt checkpoint is published on Hugging Face together with the
# HF/safetensors format (the GGUF path is for inference only).
set -euo pipefail
cd "$(dirname "$0")/.."

CKPT="${1:-out/sft-v2e/last.pt}"
DATE="${DATE:-$(date +%Y-%m-%d)}"

if [ ! -f "$CKPT" ]; then
  echo "[eval] checkpoint not found: $CKPT" >&2
  echo "       Download the released last.pt via scripts/download_model.sh, or pass a path." >&2
  exit 1
fi

mkdir -p reports

echo "[eval] dev set (18 questions + PPL)"
.venv-pre/bin/python -I tools/eval.py \
  --ckpt "v2e=$CKPT" --out "reports/${DATE}-eval-dev.md"
.venv-pre/bin/python -I tools/eval_format.py \
  --csv "reports/${DATE}-eval-dev.csv" \
  --out "reports/${DATE}-eval-dev-rubric.md"

echo "[eval] holdout v3 (90 questions, skip PPL)"
.venv-pre/bin/python -I tools/eval.py \
  --ckpt "v2e=$CKPT" \
  --tests data/eval/tests-holdout-v3.json \
  --skip-ppl \
  --out "reports/${DATE}-holdout-v3.md"

echo "[eval] done: reports/${DATE}-eval-dev.{md,csv} + reports/${DATE}-holdout-v3.{md,csv}"