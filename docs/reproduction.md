# Reproduction

This document reproduces the full pipeline from raw data to the deployed
GGUF. It is intentionally explicit: the project's value is the evidence,
not just the final weights.

## Hardware and environment

| Item | Value used |
|---|---|
| GPU | NVIDIA RTX 5070 Ti 16 GB (sm_120) |
| CPU / RAM | 96 GB RAM |
| Disk | ~145 GB free (data 37.9 GB + shards 6 GB + checkpoints ~73 GB + outputs) |
| OS | Linux |
| Python | 3.12.13 (uv-managed) |
| PyTorch | 2.11.0+cu128 |
| CUDA | 12.8+ (required for sm_120) |

CPU-only users can run inference (GGUF/Ollama) but not the full training
pipeline. A smaller GPU may work with a smaller micro-batch; the 140M
configuration used micro-batch 8 × gradient accumulation 8 × 1024 tokens.

## 0. Setup

```bash
git clone https://github.com/lynxpurr/pretrain-lab.git
cd pretrain-lab
bash scripts/setup.sh
```

`setup.sh` creates `.venv-pre`, installs the CUDA 12.8 PyTorch wheel when
`nvidia-smi` is available (CPU wheel otherwise), and verifies the imports.
For the HF export verification only:

```bash
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
```

## 1. Data

```bash
bash scripts/download_data.sh
```

Downloads:

- `HuggingFaceFW/fineweb-edu` → `sample/10BT/*.parquet` (~27.9 GB)
- `jingyaogong/minimind_dataset` → `pretrain_t2t.jsonl`, `sft_t2t_mini.jsonl`,
  `dpo.jsonl` (~10.1 GB)

Then verifies `data/raw/SHA256SUMS` (17 files). The manifest is the
authoritative pin; `HF_REVISION` defaults to `main`, so set it to a commit
hash if you need a frozen upstream snapshot.

In mainland China:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

## 2. Tokenizer (32k BPE, ~4.5 min)

```bash
.venv-pre/bin/python -I tools/train_tokenizer.py
```

Expected: vocab 32,000; specials `<|endoftext|>`=0, `<|im_start|>`=1,
`<|im_end|>`=2; held-out compression ≈ zh 1.841 / en 4.226 chars/token.
The tokenizer files land in `data/tokenizer-32k/`.

## 3. 3B-token memmap shards (~21 min)

```bash
.venv-pre/bin/python -I tools/build_shards.py
```

Expected: 3,000,000,000 tokens (English 60% / Chinese 40%), six 1 GB shards
plus a 4M-token validation shard, `data/shards/meta.json`, and
`SHA256SUMS`. Check:

```bash
cd data/shards && sha256sum -c SHA256SUMS
```

## 4. Pre-training (140M × 3B, ~16 h)

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/train.py \
  --run-name main140m --data-dir data/shards \
  --n-embd 768 --n-layer 16 --n-head 12 --block-size 1024 \
  --batch-size 8 --grad-accum 8 \
  --base-lr 6e-4 --warmup 500 --min-lr-frac 0.1 --weight-decay 0.1 --grad-clip 1.0 \
  --target-tokens 3e9 --max-minutes 1800 \
  --eval-every 500 --eval-iters 40 --eval-batch-size 16 \
  --sample-every 2000 --sample-tokens 80 \
  --ckpt-every 1000 --keep-ckpts 0 \
  --out-dir out/main140m \
  --notes "140M x 3B pre-training"
```

Expected: 45,777 steps · 16h07m41s · validation loss **2.7709** ·
~52,171 tok/s · peak ~10.5 GB. `--max-minutes 1800` is a safety bound;
the actual run is ~16 h. `--ckpt-every 1000` produces 46 checkpoints
(~73 GB); use `--keep-ckpts 3` or a larger interval if you don't need the
full lineage.

The first-step anchor should be near `ln(32000) = 10.3735` (the observed
140M deviation was +0.17). A value far above 10.6 or near 0 means a data /
vocab / batching problem; stop and check before training.

## 5. SFT data (v2e, ~5 min)

```bash
.venv-pre/bin/python -I tools/gen_sft_v2_extra.py
.venv-pre/bin/python -I tools/build_sft_v2.py \
  --listy-keep-den 5 --protect-math-short --en-refusal-keep-den 2 \
  --en-helpful-upsample 5 --concise-repeat 3 --translate-upsample 3 \
  --long-answer-keep-den 2 --format-repeat 3 --translate-ex-repeat 6 \
  --math-upsample 2 --en-flu-no-upsample \
  --out-dir data/sft-mix-v2e
```

> **Known historical residue**: the exact v2e build in this repository
> still contains two brevity extras that collide with the dev set
> (`一年有几个月？` and `3 加 5 等于多少？`). The strict
> `assert_no_eval_leak` will therefore fail for a fresh v2e build; the
> historical build used `--skip-eval-leak-check`. This is disclosed in
> `REPORT.md` §5.1 and `reports/2026-11-20-eval-leak-recheck.md`.
> To build a fully clean dataset, replace those two lines in
> `tools/gen_sft_v2_extra.py` with non-colliding variants and drop the
> flag. The released model is v2e; a clean v2f is a possible follow-up.

Expected: 250,001,408 tokens · 244,142 blocks · list-type ratio ≤15% ·
assistant-only mask · 25% pre-training mix. Verify the mask and the
value range before training:

```bash
.venv-pre/bin/python - <<'PY'
import numpy as np
labels = np.memmap("data/sft-mix-v2e/train.labels.bin", dtype=np.int16, mode="r")
print("labels", labels.min(), labels.max())
assert labels.min() >= -100 and labels.max() < 32000
PY
```

## 6. SFT (v2e, ~1 h 20 m)

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv-pre/bin/python -I tools/sft.py \
  --init-from out/main140m/last.pt \
  --data-dir data/sft-mix-v2e \
  --run-name sft-v2e \
  --out-dir out/sft-v2e \
  --batch-size 8 --grad-accum 8 \
  --base-lr 1e-4 --warmup 100 --target-tokens 250e6 \
  --eval-every 250 --eval-iters 20 --eval-batch-size 8 \
  --sample-every 500 --ckpt-every 250
```

Expected: 3,815 steps · ~1h19m · SFT val **1.6065** · peak ~12.05 GB.
Check `EXIT:0` in the log; a nonzero exit or a stale `logs/<run>.exit`
means the run failed.

## 7. Evaluation

```bash
bash scripts/reproduce_eval.sh out/sft-v2e/last.pt
```

This runs the dev set (18 questions + PPL) and the 90-question holdout
(`--skip-ppl`), producing md + csv under `reports/`. Expected v2e:
dev 17/18 keyword (2 known residues; clean subset 15/16), holdout 90
manual 53/90, rep-4 0.055. See [`evaluation.md`](evaluation.md) for the
protocol and caveats.

## 8. GGUF / Ollama

```bash
.venv-pre/bin/python -I tools/export_gguf.py \
  --ckpt out/sft-v2e/last.pt \
  --out out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf \
  --name pretrain-lab-140m-sft-v2e
```

Create the Ollama model from the F16 GGUF:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e \
  -f out/Modelfile-sft-v2e
OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \
  -f out/Modelfile-sft-v2e -q q8_0
```

The q/k permutation is applied inside `export_gguf.py`; without it,
llama.cpp's RoPE sees misaligned q/k and the model repeats after the first
few tokens.

For a standalone Q8_0 GGUF file (the release asset), use the file produced
by `ollama create -q q8_0` or `llama-quantize` from the F16 GGUF. Verify it
with the `gguf` reader and a generation check before publishing.

| Released file | Size | SHA256 (prefix) |
|---|---|---|
| `out/hf-sft-v2e/model.safetensors` (fp16, tied) | 262.9 MiB | `7d1c2f0c4657c2a2` |
| `out/gguf/pretrain-lab-140m-sft-v2e-Q8_0.gguf` | 174 MB | `8b64b66898eef9f5` |
| `out/gguf/pretrain-lab-140m-sft-v2e-f16.gguf` | 326 MB | `eee108223b9c0278` |

Full export/verification evidence:
[`reports/2026-11-21-release-model-export.md`](../reports/2026-11-21-release-model-export.md).

## 9. Expected readings

| Stage | Reading |
|---|---|
| Pre-training val | 2.7709 |
| SFT val (v2e) | 1.6065 |
| Dev keyword | 17/18 (2 residues; clean subset 15/16) |
| Holdout 90 manual | 53/90 |
| rep-4 (v2e) | 0.055 |
| Pre-training time | 16h07m41s |
| SFT time | ~1h19m |
| Peak pre-training memory | ~10.5 GB |
| Peak SFT memory | ~12.05 GB |

## 10. Determinism and evidence

- The v2e data build was verified **bit-for-bit** (4/4 SHA256) on the same
  machine; the evaluation was byte-identical on 18/18 rows. This proves
  pipeline determinism for a fixed environment, not cross-machine
  portability. Record input fingerprints (data + tokenizer + checkpoint)
  with every run.
- Training uses three RNG streams (Python/NumPy/Torch) and resumes from
  them; `tokens_seen == step × tokens_per_step` is the resume invariant.
- Evidence convention: every run produces a summary `.md`, a curve `.csv`,
  and a raw `.log` under `reports/` (append-only).

## 11. Disk and time budget

| Item | Size / time |
|---|---|
| Raw data | 37.9 GB |
| Tokenizer | ~4 MB |
| 3B shards | ~6 GB |
| Pre-training checkpoints | ~73 GB (46 × 1.65 GB; optional) |
| SFT checkpoints | ~1.65 GB per run |
| Full pipeline wall-clock | ~30 GPU-hours (pre-training 16 h + SFT/LoRA/eval) |

If you only want to run the released model, skip sections 1–7 and use
[`quickstart.md`](quickstart.md).

## 12. Licenses

Upstream data licenses: FineWeb-Edu ODC-BY 1.0 (Common Crawl ToU) and
minimind_dataset Apache-2.0. See [`../NOTICE`](../NOTICE) and
[`../data/LICENSE`](../data/LICENSE). The raw corpora are not
redistributed in this repository.