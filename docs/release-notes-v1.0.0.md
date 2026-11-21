# pretrain-lab v1.0.0 — release notes

**2026-11-21** · [Repository](https://github.com/lynxpurr/pretrain-lab) ·
[Model card](https://github.com/lynxpurr/pretrain-lab/blob/develop/MODEL_CARD.en.md) ·
[Evaluation](https://github.com/lynxpurr/pretrain-lab/blob/develop/docs/evaluation.md) ·
[Full report](https://github.com/lynxpurr/pretrain-lab/blob/develop/REPORT.md)

## What this is

`pretrain-lab` is a **137,847,552-parameter** Chinese–English decoder-only
language model trained from random initialization on one RTX 5070 Ti 16 GB
GPU, plus a reproducible account of what it can and cannot do.

It is a learning/research artifact, not a competitive open model and not a
production system. The most useful part is the evaluation story: the project
found its own evaluation contamination, fixed a false-negative deduplication
checker, built a 90-question holdout, and reports the failures (math,
translation) alongside the wins.

## Headline results

| Item | Result |
|---|---|
| Model | 137,847,552 params · d_model 768 · 16 layers · 12 heads · RoPE + RMSNorm + SwiGLU + tied embeddings · 32k BPE · context 1024 |
| Pre-training | 3.0B tokens (English 60% FineWeb-Edu / Chinese 40% minimind) · 16h07m41s · val loss **2.7709** |
| SFT (deployed) | v2e · 250M tokens · val 1.6065 · repetition-4 **0.055** (lowest in the family) |
| Dev set | **17/18** with 2 known residues; clean subset **15/16** |
| Holdout (90 questions) | audit **53/90** vs v2 **47/90** (+6); per-item re-judgment **52 vs 45** (+7) |
| Significance | paired McNemar **p = 0.0923**; bootstrap 95% CI **[0.000, 0.156]** → **not significant at 0.05** |
| Capability blocks | math **0–3/14 ✗** (lookup table, not arithmetic) · translation **0–5/14 ✗** (sentence-pattern level) · calibration **5–6/6 ✓** |
| Deployment | Q8_0 GGUF 174 MB (default) · F16 326 MB (faithful) · **Q4_K_M is not faithful** |

The v2e advantage is concentrated in English fluency (5/5 vs 0/5); math is
−1 and translation/calibration are tied. Read it as **"meets the
pre-registered threshold, directionally better, not statistically
established"**.

## Assets

| File | Size | SHA256 (prefix) |
|---|---|---|
| `model.safetensors` (fp16, tied) | 262.9 MiB | `7d1c2f0c4657c2a2` |
| `pretrain-lab-140m-sft-v2e-Q8_0.gguf` | 174 MB | `8b64b66898eef9f5` |
| `pretrain-lab-140m-sft-v2e-f16.gguf` | 326 MB | `eee108223b9c0278` |
| `last.pt` (training checkpoint) | 1.6 GB | `984a25c4d59e36a4` |

- Weights: [lynxpurr/pretrain-lab-140m-sft-v2e](https://huggingface.co/lynxpurr/pretrain-lab-140m-sft-v2e)
- GGUF: [lynxpurr/pretrain-lab-140m-sft-v2e-GGUF](https://huggingface.co/lynxpurr/pretrain-lab-140m-sft-v2e-GGUF)
- Local manifest: [`RELEASE_SHA256SUMS`](https://github.com/lynxpurr/pretrain-lab/blob/develop/RELEASE_SHA256SUMS)

`last.pt` is for `tools/eval.py` / `scripts/reproduce_eval.sh`; it is not
needed for `transformers` or Ollama inference.

## Quick start

### Ollama + GGUF

```bash
bash scripts/download_model.sh
( cd models/pretrain-lab-140m-sft-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2e-q8 \
  -f Modelfile-sft-v2e-q8 )
bash scripts/run_demo.sh          # http://127.0.0.1:7860
```

### Hugging Face `transformers`

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

repo = "lynxpurr/pretrain-lab-140m-sft-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16).eval()

messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

Full pipeline (data → tokenizer → pre-training → SFT → GGUF):
[`docs/reproduction.md`](https://github.com/lynxpurr/pretrain-lab/blob/develop/docs/reproduction.md).

## What changed in this release

- HF fp16 export (tied embeddings) and standalone Q8_0 / F16 GGUF files;
  PyTorch vs HF greedy output matches 30/30 tokens; F16 GGUF matches the
  PyTorch checkpoint 5/5.
- Per-item manual labels for the 90-question holdout (900 cells) and a
  re-scoring / McNemar audit; public wording downgraded to "threshold met,
  not statistically significant".
- Reader-facing docs (README EN/ZH, quickstart, reproduction, evaluation,
  architecture, FAQ) and a lightweight CI (schema, leak-checker controls,
  link check, `compileall`).
- Internal process records are kept local and are not part of the public
  repository.

## Known limitations

- **Knowledge**: 3B tokens / 140M parameters ≈ GPT-2-level; it will
  hallucinate names, dates, and details. Do not use it as a knowledge source.
- **Math**: the dev `8`/`42` are memory + a narrow lookup table; unseen
  combinations (`13×5`, `17+6`, `100−37`) are wrong.
- **Translation**: only trained instruction patterns; en→zh mostly fails;
  `今天非常冷` is translated as "hot" by all versions (prior override).
- **Identity**: the SFT corpus comes from minimind; the model often
  identifies as "minimind" even with greedy decoding. Treat its
  self-description as unreliable.
- **Repetition**: v2e has the lowest rep-4 in the family, but long English
  answers can still repeat.
- **Context**: 1024 tokens; longer inputs are truncated.
- **Safety**: no safety tuning, no RLHF, no bias evaluation.

## Verification

```bash
sha256sum -c RELEASE_SHA256SUMS                 # 5/5 OK (local release files)
.venv-pre/bin/python -I tests/test_eval_schema.py
.venv-pre/bin/python -I tests/test_leak_checker.py
.venv-pre/bin/python -I tests/check_links.py
bash scripts/reproduce_eval.sh                  # dev + 90-question holdout
```

## Citation and license

```bibtex
@misc{pretrainlab2026,
  title  = {pretrain-lab: a 140M bilingual language model trained from scratch on one 16GB GPU},
  author = {lynxpurr},
  year   = {2026},
  url    = {https://github.com/lynxpurr/pretrain-lab},
  note   = {Apache-2.0; learning/research artifact}
}
```

Code and model weights are Apache-2.0; documentation and evaluation sets are
CC BY 4.0. Upstream data attributions are in
[`NOTICE`](https://github.com/lynxpurr/pretrain-lab/blob/develop/NOTICE).