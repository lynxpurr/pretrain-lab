# pretrain-lab

**ZhenLM-140M — a 137.8M-parameter Chinese–English language model trained from random initialization on one 16GB GPU.**

This is not a competitive open model. It is a complete, reproducible pipeline:
tokenizer → 3B-token pre-training → six SFT iterations → LoRA ablations →
GGUF/Ollama deployment, with every run's evidence in [`reports/`](reports/).
The evaluation section documents the contamination finding, the
deduplication-checker fix, the 90-question holdout, the 47-question second
review, and the failure modes (math, translation).

**Naming**: **ZhenLM** (真) is the model family; "140M" is the family label
(exact 137,847,552 params); the deployed SFT variant is **v2e**.
This repository is the `pretrain-lab` project.

- **Model**: **ZhenLM-140M** · 137,847,552 params · d_model 768 · 16 layers · 12 heads · RoPE + RMSNorm + SwiGLU + tied embeddings · 32k BPE · context 1024
- **Pre-training**: 3.0B tokens (English 60% FineWeb-Edu / Chinese 40% minimind) · 16h07m41s · validation loss **2.7709**
- **SFT**: 250M tokens, assistant-only mask, six variants · deployed **ZhenLM-140M-SFT-v2e** (val 1.6065, repetition-4 **0.055**)
- **Hardware**: one RTX 5070 Ti 16GB · single-GPU, local
- **Deployment**: Q8_0 GGUF (174 MB) → Ollama (`zhenlm-140m-sft-v2e-q8`) → zero-dependency local chat page

## Quick start

> The Hugging Face repositories are part of the v1.0 release. If they are not
> available yet, build from source ([`docs/reproduction.md`](docs/reproduction.md)).

### Ollama + GGUF (recommended)

```bash
bash scripts/download_model.sh
( cd models/ZhenLM-140M-SFT-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create zhenlm-140m-sft-v2e-q8 \
  -f Modelfile-ZhenLM-140M-SFT-v2e-q8 )
bash scripts/run_demo.sh                # http://127.0.0.1:7860
```

### Hugging Face `transformers`

```bash
# after `bash scripts/setup.sh` (or use your own Python 3.12 environment)
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
.venv-pre/bin/python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
repo = "lynxpurr/ZhenLM-140M-SFT-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16)
messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
PY
```

Build from source: [`docs/reproduction.md`](docs/reproduction.md) (~38 GB data,
~16 h pre-training).

## Results

All numbers are greedy decoding, same chat template and tokenizer. Dev is for
iteration; the 90-question holdout is for acceptance. `rep-4` = 4-gram
repetition rate (lower is better).

| Model | Dev 18 | Holdout 90 (manual) | rep-4 ↓ | Notes |
|---|---|---|---|---|
| base (pre-training) | 6/18 | 12/90 | 0.738 | no instruction following |
| SFT v1 | 16/18 | 47/90 | 0.248 | clean baseline |
| SFT v2 | 15/18 | 47/90 | 0.168 | calibration/translation fixed, math regressed |
| SFT v2e (deployed) | **17/18**\* | **53/90** | **0.138** | \*2 known residues; clean subset **15/16** |
| LoRA r=12, 2 epochs | 15/18 | 48/90 | 0.283 | not deployed |

> Manual scores are the original audit. The 2026-11-21 re-judgment gives
> v2e **52** vs v2 **45** (+7), but McNemar is **p = 0.0923** (not significant).
> A 2026-11-22 47-question second review did **not** reproduce the advantage:
> v2e **11 vs 11** (kappa 0.660/0.453; paired p=1.000), and even lenient
> re-adjudication gives at most +2. The +6/+7 is **rubric-sensitive**, not a
> robust capability gain. See [`docs/evaluation.md`](docs/evaluation.md) §6.1.

**Capability blocks** (14 math / 14 translation / 6 calibration):

| Block | Score | What it means |
|---|---|---|
| Math | 0–3 / 14 | lookup table, **not arithmetic** (`13×5`, `17+6`, `100−37` all wrong) |
| Translation | 0–5 / 14 | sentence-pattern level, **not general translation** (zh→en simple sentences; en→zh mostly fails) |
| Calibration | 5–6 / 6 lenient; 1–3 / 6 strict | refuses to invent, but premise corrections are often factually wrong (2044/2046 are event years) |

The capability blocks are the acceptance unit; single-question fixes do not
generalize.

## Limits

- **Math**: memorized a few dev answers, not arithmetic.
- **Translation**: learned a handful of instruction patterns; `Knowledge is power` often comes back in English.
- **Knowledge**: 140M / 3B tokens ≈ GPT-2-level; it will hallucinate names, dates, and details.
- **Identity**: the SFT corpus comes from minimind; it often identifies as "minimind" even with greedy decoding.
- **Context / safety**: 1024 tokens; no safety tuning, no RLHF, no bias evaluation.

## Evaluation notes

- **Contamination**: early SFT "fixes" copied evaluation prompts into the
  training extras, so v2–v2d dev scores were partly memory. v1 is the clean
  baseline; v2e has 2 residues (clean subset 15/16).
- **Checker false negative**: the first dedup checker skipped short prompts;
  the current one removes non-word characters, has no length guard, and
  self-tests with a known collision ([`tools/check_eval_leak.py`](tools/check_eval_leak.py)).
- **Holdout + second review**: dev rankings only partly reproduce; the
  90-question holdout is the acceptance set, and a 47-question second review
  did not reproduce the +7 (11 vs 11). See [`docs/evaluation.md`](docs/evaluation.md) §6.1.
- **Quantization**: Q4_K_M is not faithful for v2e; Q8_0 is the default; F16
  is bit-for-bit in the 5/5 spot check.

## Reproduce

```bash
bash scripts/setup.sh
bash scripts/download_data.sh
.venv-pre/bin/python -I tools/train_tokenizer.py   # 32k BPE
.venv-pre/bin/python -I tools/build_shards.py      # 3B-token memmap
# pre-training / SFT commands: docs/reproduction.md
bash scripts/reproduce_eval.sh                     # dev + 90-question holdout
```

Reproducibility evidence: v2e data rebuild 4/4 SHA256, evaluation rows 18/18
byte-identical, F16 5/5. See `reports/2026-11-20-day10-repro-check.md`.

## Repository map

| Path | What |
|---|---|
| `tools/` | model, training, SFT, LoRA, evaluation, GGUF, demo |
| `data/eval/` | dev 18 + holdout 30 + holdout 90 question sets |
| `data/PROVENANCE.md` | data sources, licenses, SHA256 fingerprints |
| `reports/` | evidence: summaries, CSVs, raw logs (append-only) |
| `docs/` | quickstart, reproduction, evaluation, architecture, FAQ |
| `REPORT.md` / `HISTORY.md` | full report / historical commit-message notes |
| `MODEL_CARD.en.md` / `MODEL_CARD.md` | model card (English / Chinese) |

## Implementation note

AI-assisted code and documentation; human-directed scope, experiments,
evaluation, and release. Headline claims were verified independently
(bit-for-bit data, byte-identical eval, F16 5/5, known-collision control,
McNemar).

## License and citation

- **Code and model weights**: Apache License 2.0 — see [`LICENSE`](LICENSE).
- **Documentation and evaluation sets**: CC BY 4.0 — see [`docs/LICENSE-CC-BY-4.0.txt`](docs/LICENSE-CC-BY-4.0.txt) and [`data/LICENSE`](data/LICENSE).
- **Upstream data**: FineWeb-Edu (ODC-BY 1.0, Common Crawl ToU) and
  minimind_dataset (Apache-2.0). See [`NOTICE`](NOTICE).
- If you use this project, cite it via [`CITATION.cff`](CITATION.cff).

## Acknowledgements

Architecture and data-format ideas from
[minimind](https://github.com/jingyaogong/minimind) (Apache-2.0) and
[nanoGPT](https://github.com/karpathy/nanoGPT) (MIT); GGUF layout conventions
from [llama.cpp](https://github.com/ggml-org/llama.cpp) (MIT); data from
[FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) and
[minimind_dataset](https://huggingface.co/datasets/jingyaogong/minimind_dataset).

*This is a learning/research artifact. It is not affiliated with, endorsed by,
or a replacement for any of the above projects.*