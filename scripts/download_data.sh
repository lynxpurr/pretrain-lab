#!/usr/bin/env bash
# Download the raw pre-training corpora (37.9 GB) and verify fingerprints.
#
#   bash scripts/download_data.sh
#
# In mainland China you may need:
#   export HF_ENDPOINT=https://hf-mirror.com
#
# The SHA256SUMS manifest is the authoritative pin. Upstream repositories
# use "main" by default; set HF_REVISION to a commit hash for a frozen copy.
set -euo pipefail
cd "$(dirname "$0")/.."

HF_CLI="${HF_CLI:-hf}"
HF_REVISION="${HF_REVISION:-main}"

if ! command -v "$HF_CLI" >/dev/null 2>&1; then
  echo "[data] Hugging Face CLI not found ($HF_CLI)." >&2
  echo "       Install: uv pip install --python .venv-pre/bin/python huggingface-hub" >&2
  exit 1
fi

mkdir -p data/raw/fineweb-edu data/raw/minimind_dataset

echo "[data] downloading FineWeb-Edu sample-10BT (~27.9 GB)"
"$HF_CLI" download HuggingFaceFW/fineweb-edu \
  --repo-type dataset \
  --revision "$HF_REVISION" \
  --include "sample/10BT/*.parquet" \
  --local-dir data/raw/fineweb-edu

echo "[data] downloading minimind_dataset (~10.1 GB)"
"$HF_CLI" download jingyaogong/minimind_dataset \
  --repo-type dataset \
  --revision "$HF_REVISION" \
  --include "pretrain_t2t.jsonl" \
  --include "sft_t2t_mini.jsonl" \
  --include "dpo.jsonl" \
  --local-dir data/raw/minimind_dataset

echo "[data] verifying SHA256"
( cd data/raw && sha256sum -c SHA256SUMS )

echo "[data] done: $(du -sh data/raw | cut -f1) under data/raw/"