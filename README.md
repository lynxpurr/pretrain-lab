# pretrain-lab

**A 137.8M-parameter Chinese–English language model trained from random initialization on one 16GB GPU — and an honest account of what it can't do.**

This is not a competitive open model. It is a complete, reproducible case study:
tokenizer → 3B-token pre-training → six SFT iterations → LoRA ablations →
GGUF/Ollama deployment, with every run's evidence in [`reports/`](reports/).
The most useful part is the evaluation story: we found our own evaluation
contamination, fixed the deduplication checker, built a 90-question holdout,
and report the failures (math, translation) instead of hiding them. A
47-question second review also failed to reproduce our own claimed v2e
advantage (11 vs 11); we report that too.

- **Model**: 137,847,552 params · d_model 768 · 16 layers · 12 heads · RoPE + RMSNorm + SwiGLU + tied embeddings · 32k BPE · context 1024
- **Pre-training**: 3.0B tokens (English 60% FineWeb-Edu / Chinese 40% minimind) · 16h07m41s · validation loss **2.7709**
- **SFT**: 250M tokens, assistant-only mask, six variants · deployed **v2e** (val 1.6065, repetition-4 **0.055**)
- **Hardware**: one RTX 5070 Ti 16GB · single-GPU, local
- **Deployment**: Q8_0 GGUF (174 MB) → Ollama → zero-dependency local chat page

## Quick start

> The Hugging Face repositories are created as part of the v1.0 release. If
> `scripts/download_model.sh` cannot find them yet, build from source
> ([`docs/reproduction.md`](docs/reproduction.md)) or use the local release
> files under `out/gguf/`.

### Option A — Ollama + GGUF (fastest, no Python training stack)

```bash
bash scripts/download_model.sh          # downloads the GGUF + Modelfile from Hugging Face
( cd models/pretrain-lab-140m-sft-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \
  -f Modelfile-sft-v2e-q8 )
bash scripts/run_demo.sh                # http://127.0.0.1:7860
```

### Option B — Hugging Face `transformers`

```bash
# after `bash scripts/setup.sh` (or use your own Python 3.12 environment)
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
.venv-pre/bin/python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
repo = "lynxpurr/pretrain-lab-140m-sft-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16)
messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
PY
```

### Option C — build everything from source

See [`docs/reproduction.md`](docs/reproduction.md). Full pipeline: ~38 GB data
download, ~21 min shards, ~16 h pre-training, ~1 h 20 m per SFT run.

## Results (honest)

All numbers are greedy decoding, same chat template, same tokenizer.
The dev set is for iteration; the 90-question holdout is for acceptance.
`rep-4` = 4-gram repetition rate (lower is better).

| Model | Dev 18 | Holdout 90 (manual) | rep-4 ↓ | Notes |
|---|---|---|---|---|
| base (pre-training) | 6/18 | 12/90 | 0.738 | no instruction following |
| SFT v1 | 16/18 | 47/90 | 0.248 | clean baseline |
| SFT v2 | 15/18 | 47/90 | 0.168 | calibration/translation fixed, math regressed |
| SFT v2e (deployed) | **17/18**\* | **53/90** | **0.138** | \*2 known residues; clean subset **15/16** |
| LoRA r=12, 2 epochs | 15/18 | 48/90 | 0.283 | not deployed |

> Manual scores in the table are the original audit. A 2026-11-21 per-item
> re-judgment gives v2e **52** vs v2 **45** (+7); the paired McNemar test is
> **p = 0.0923** (not significant at 0.05). A 2026-11-22 second review of a
> 47-question subset did **not** reproduce the advantage: v2e **11 vs 11**
> (kappa 0.660/0.453; paired p=1.000). The +6/+7 is rubric-sensitive; see
> [`docs/evaluation.md`](docs/evaluation.md) §6.1.

**Capability blocks (14 math / 14 translation / 6 calibration):**

| Block | Best result | Verdict |
|---|---|---|
| Math | 0–3 / 14 | ✗ lookup-table, **not arithmetic** (`13×5`, `17+6`, `100−37` all wrong) |
| Translation | 0–5 / 14 | ✗ sentence-pattern level, **not general translation** (zh→en simple sentences work; en→zh mostly fails) |
| Calibration | 5–6 / 6 (lenient); 1–3 / 6 (strict second review) | ⚠️ refuses to invent, but premise corrections are often factually wrong (2044/2046 are event years) |

v2e vs v2 on the 90-question manual score: the original audit is **+6/90**
(53 vs 47); a 2026-11-21 per-item re-judgment is **+7/90** (52 vs 45). Both
meet the pre-registered threshold (≥5) **under the original labels**, but the
paired McNemar test is **not significant at 0.05**: p = 0.0923, bootstrap
95% CI [0.000, 0.156] (lower bound ≈0).

A 2026-11-22 second review of a 47-question subset **did not reproduce the
advantage**: v2e **11 vs v2 11** (0/47; Cohen's kappa 0.660 for v2 and 0.453
for v2e against the original labels; paired McNemar p=1.000). Even a lenient
re-adjudication gives at most +2. The +6/+7 is therefore **rubric-sensitive
and not a robust capability improvement**; do not read it as "v2e is better".
The earlier 30-question "no difference" was underpowered. See
[`docs/evaluation.md`](docs/evaluation.md) §6.1 and
[`reports/2026-11-22-second-review-adjudication.md`](reports/2026-11-22-second-review-adjudication.md).

## What it can't do

- **Math**: it has memorized a few dev answers, not arithmetic. Expect wrong
  answers on unseen combinations.
- **Translation**: it learned a handful of instruction patterns; it is not a
  translation model. `Knowledge is power` often comes back in English.
- **Facts**: 140M / 3B tokens ≈ GPT-2-level knowledge; it will hallucinate
  names, dates, and details. Do not use it as a knowledge source.
- **Production**: no safety tuning, no RLHF, no long-context handling
  (1024 tokens), no guarantee of factual or stylistic quality.
- **Identity**: the SFT corpus comes from minimind; the model often
  identifies as "minimind" even with greedy decoding. Treat its
  self-description as unreliable.
- **Label sensitivity**: the holdout +6/+7 is threshold-met under the original
  labels but not robust to a stricter second review (v2e 11 vs v2 11). Do not
  quote the +7 as a settled capability win.

## The interesting part: evaluation methodology

1. **Contamination found and removed.** Early SFT "fixes" copied evaluation
   prompts into the training extras, so v2–v2d dev scores were partly memory.
   v1 is the clean baseline; v2e is "partially clean" (2 residues; clean
   subset 15/16).
2. **The checker itself had a false negative.** A `len(prompt) >= 8` guard
   skipped short prompts, so "0 collisions" was wrong. The fixed checker
   removes all non-word characters, has no length guard, and self-tests with
   a known collision. See `tools/check_eval_leak.py`.
3. **Holdout beats dev.** The 90-question holdout shows the dev ranking only
   partly reproduces; capability blocks (math/translation/calibration) replace
   single-question claims.
4. **Quantization fidelity matters.** Q4_K_M is not faithful for v2e
   (math 42→72, translation reverts); Q8_0 is the deployment default; F16 is
   bit-for-bit faithful in the 5/5 spot check.
5. **LoRA capacity curve.** r=8 → r=12 buys −0.020 validation loss;
   1 → 2 epochs buys −0.013; neither closes the 0.19 gap to full fine-tuning.
   LoRA is for domain increments, not first alignment.
6. **The win did not survive a second review.** A blinded 47-question second
   review gives v2e **11 vs v2 11** (kappa 0.660/0.453); even lenient
   re-adjudication gives at most +2. The +6/+7 is threshold-met under the
   original labels but rubric-sensitive, not a robust capability gain.

Read the full Chinese report: [`REPORT.md`](REPORT.md) ·
Model card: [`MODEL_CARD.en.md`](MODEL_CARD.en.md) / [`MODEL_CARD.md`](MODEL_CARD.md) ·
Evaluation details: [`docs/evaluation.md`](docs/evaluation.md).

## Reproduce

```bash
bash scripts/setup.sh                  # venv + torch 2.11.0+cu128 + deps
bash scripts/download_data.sh          # 37.9 GB, SHA256-verified
.venv-pre/bin/python -I tools/train_tokenizer.py   # 32k BPE, ~4.5 min
.venv-pre/bin/python -I tools/build_shards.py      # 3B-token memmap, ~21 min
# pre-training: 16 h; command in docs/reproduction.md
# SFT v2e: ~1 h 20 m; command in docs/reproduction.md
bash scripts/reproduce_eval.sh         # dev + 90-question holdout
```

Reproducibility evidence: v2e data rebuild is bit-for-bit (4/4 SHA256),
evaluation rows are byte-identical (18/18), and F16 GGUF matches PyTorch
5/5 in the spot check. See `reports/2026-11-20-day10-repro-check.md`.

## Repository map

| Path | What |
|---|---|
| `tools/` | model, training, SFT, LoRA, evaluation, GGUF, demo scripts |
| `data/eval/` | dev 18 + holdout 30 + holdout 90 question sets |
| `data/PROVENANCE.md` | data sources, licenses, SHA256 fingerprints |
| `reports/` | evidence: summaries, CSVs, raw logs (append-only) |
| `docs/` | quickstart, reproduction, evaluation, architecture, FAQ |
| `REPORT.md` | full project report (Chinese) |
| `HISTORY.md` | Historical commit-message notes (day labels, preliminary claims) |

| `MODEL_CARD.en.md` / `MODEL_CARD.md` | model card (English / Chinese) |

## Implementation note

AI-assisted code and documentation; human-directed scope, experiments,
evaluation, and release. Every headline claim was verified independently
(bit-for-bit data, byte-identical eval, F16 5/5, known-collision control,
McNemar).

## License and citation

- **Code and model weights**: Apache License 2.0 — see [`LICENSE`](LICENSE).
- **Documentation and evaluation sets**: CC BY 4.0 — see [`docs/LICENSE-CC-BY-4.0.txt`](docs/LICENSE-CC-BY-4.0.txt) and [`data/LICENSE`](data/LICENSE).
- **Upstream data**: FineWeb-Edu (ODC-BY 1.0, Common Crawl ToU) and
  minimind_dataset (Apache-2.0). See [`NOTICE`](NOTICE). The raw corpora are
  not redistributed.
- If you use this project, cite it via [`CITATION.cff`](CITATION.cff).

## Acknowledgements

Architecture and data-format ideas from
[minimind](https://github.com/jingyaogong/minimind) (Apache-2.0) and
[nanoGPT](https://github.com/karpathy/nanoGPT) (MIT);
GGUF layout conventions from [llama.cpp](https://github.com/ggml-org/llama.cpp) (MIT);
data from [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu)
and [minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset).

*This is a learning/research artifact. It is not affiliated with, endorsed by,
or a replacement for any of the above projects.*