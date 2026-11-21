#!/usr/bin/env bash
# Verify local release artifacts before uploading to Hugging Face / GitHub.
#
#   bash scripts/verify_release.sh            # full check (includes HF load)
#   bash scripts/verify_release.sh --skip-hf  # skip the transformers load
#
# Checks:
#   1. required release files exist
#   2. RELEASE_SHA256SUMS (5 files) matches
#   3. canonical GGUF vs staged upload copies are byte-identical
#   4. GGUF metadata: Q8_0 file_type 7 / F16 file_type 1 / 147 tensors
#   5. MODEL_CARD.en.md is the single source and matches the HF card copy
#   6. HF export loads with the expected parameter count and chat template
#
# This script is for the repository owner before upload; it needs the local
# (gitignored) out/ directory. It is not part of the public quick start.
set -euo pipefail
cd "$(dirname "$0")/.."

SKIP_HF=0
if [ "${1:-}" = "--skip-hf" ]; then
  SKIP_HF=1
fi

PY=".venv-pre/bin/python"
if [ ! -x "$PY" ]; then
  PY="python3"
fi

HF_DIR="out/hf-sft-v2e"
GGUF_DIR="out/gguf"
STAGE_DIR="out/hf-gguf-release"

fail() { echo "[verify] ERROR: $*" >&2; exit 1; }
ok() { echo "[verify] OK: $*"; }

# 1. required files ---------------------------------------------------------
for f in \
  "$HF_DIR/model.safetensors" "$HF_DIR/config.json" "$HF_DIR/tokenizer.json" \
  "$HF_DIR/tokenizer_config.json" "$HF_DIR/special_tokens_map.json" \
  "$HF_DIR/generation_config.json" "$HF_DIR/README.md" "$HF_DIR/LICENSE" \
  "$HF_DIR/NOTICE" "$HF_DIR/DATA_LICENSE.md" "$HF_DIR/last.pt" \
  "$GGUF_DIR/pretrain-lab-140m-sft-v2e-Q8_0.gguf" \
  "$GGUF_DIR/pretrain-lab-140m-sft-v2e-f16.gguf" \
  "$STAGE_DIR/README.md" \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-Q8_0.gguf" \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-f16.gguf" \
  "$STAGE_DIR/Modelfile-sft-v2e-q8" "$STAGE_DIR/Modelfile-sft-v2e-f16" \
  "$STAGE_DIR/LICENSE" "$STAGE_DIR/NOTICE"; do
  [ -f "$f" ] || fail "missing $f"
done
ok "required files present"

# 2. release manifest -------------------------------------------------------
sha256sum -c RELEASE_SHA256SUMS
ok "RELEASE_SHA256SUMS"

# 3. staged upload copies ---------------------------------------------------
cmp -s "$GGUF_DIR/pretrain-lab-140m-sft-v2e-Q8_0.gguf" \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-Q8_0.gguf" || fail "staged Q8 GGUF differs"
cmp -s "$GGUF_DIR/pretrain-lab-140m-sft-v2e-f16.gguf" \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-f16.gguf" || fail "staged F16 GGUF differs"
ok "staged GGUF copies match"

# 4. GGUF metadata ----------------------------------------------------------
"$PY" -I - \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-Q8_0.gguf" \
  "$STAGE_DIR/pretrain-lab-140m-sft-v2e-f16.gguf" <<'PY'
import sys
from collections import Counter
from gguf import GGUFReader

checks = [(sys.argv[1], 7, "8"), (sys.argv[2], 1, "1")]
for path, file_type, qtype in checks:
    reader = GGUFReader(path)
    actual_type = reader.fields["general.file_type"].contents()
    types = Counter(str(t.tensor_type) for t in reader.tensors)
    assert actual_type == file_type, (path, "file_type", actual_type)
    assert len(reader.tensors) == 147, (path, "tensors", len(reader.tensors))
    assert types[qtype] == 114 and types["0"] == 33, (path, types)
    print(f"[verify] OK: {path.split('/')[-1]} file_type={actual_type} tensors=147")
PY

# 5. model card single source ----------------------------------------------
cmp -s MODEL_CARD.en.md "$HF_DIR/README.md" || \
  fail "out/hf-sft-v2e/README.md is not a copy of MODEL_CARD.en.md"
ok "model card synced from MODEL_CARD.en.md"

# 6. HF export loads --------------------------------------------------------
if [ "$SKIP_HF" -eq 1 ]; then
  echo "[verify] SKIP HF load (--skip-hf)"
elif "$PY" -c "import transformers" >/dev/null 2>&1; then
  "$PY" -I - <<'PY'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

repo = "out/hf-sft-v2e"
tok = AutoTokenizer.from_pretrained(repo, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    repo, dtype=torch.float16, local_files_only=True
).eval()
params = sum(p.numel() for p in model.parameters())
assert params == 137_847_552, params
assert tok.chat_template, "missing chat template"

messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(
    messages, add_generation_prompt=True, return_tensors="pt"
)
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=8, do_sample=False)
text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(f"[verify] OK: HF export loads, params={params}, sample={text.strip()[:60]!r}")
PY
else
  echo "[verify] SKIP HF load (transformers not installed; install requirements-hf.txt)"
fi

echo
echo "[verify] all local release checks passed."
echo
echo "Next (after 'hf auth login' as lynxpurr):"
echo "  hf upload lynxpurr/pretrain-lab-140m-sft-v2e out/hf-sft-v2e"
echo "  hf upload lynxpurr/pretrain-lab-140m-sft-v2e-GGUF out/hf-gguf-release"
echo
echo "Then verify from a clean directory:"
echo "  bash scripts/download_model.sh"
echo "  bash scripts/reproduce_eval.sh"