# Quick start

Two ways to run the model. Path A needs only Ollama; Path B needs Python.
Path C (build from source) is in [`reproduction.md`](reproduction.md).

## Path A — Ollama + GGUF (recommended)

### 1. Get the GGUF and Modelfile

```bash
bash scripts/download_model.sh
```

This downloads the released Q8_0/F16 GGUF files and the Modelfile into
`models/ZhenLM-140M-SFT-v2e-GGUF/`. It requires the `hf` CLI
(`pip install -U huggingface_hub`). If you built the model locally,
the file is `out/gguf/ZhenLM-140M-SFT-v2e-Q8_0.gguf` and the
Modelfile is `out/Modelfile-ZhenLM-140M-SFT-v2e`.

### 2. Start Ollama

```bash
OLLAMA_MODELS=$HOME/.ollama/models OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

Check it:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama list
```

### 3. Create the model

```bash
( cd models/ZhenLM-140M-SFT-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create zhenlm-140m-sft-v2e-q8 \
  -f Modelfile-ZhenLM-140M-SFT-v2e-q8 )
```

If you only have the F16 GGUF, create the Q8 variant with Ollama:

```bash
( cd models/ZhenLM-140M-SFT-v2e-GGUF && \
  OLLAMA_HOST=127.0.0.1:11435 ollama create zhenlm-140m-sft-v2e-q8 \
  -f Modelfile-ZhenLM-140M-SFT-v2e-f16 -q q8_0 )
```

### 4. Run the local chat page

```bash
bash scripts/run_demo.sh          # http://127.0.0.1:7860
```

The demo binds to `127.0.0.1` by default and has **no authentication**.
Only expose it on a network you trust (`BIND=0.0.0.0` is possible but unsafe).

### 5. Or call the API directly

```bash
curl -s http://127.0.0.1:11435/api/chat -d '{
  "model": "zhenlm-140m-sft-v2e-q8",
  "messages": [{"role": "user", "content": "请用一句话介绍杭州。"}],
  "stream": false,
  "options": {"temperature": 0.3, "top_p": 0.9}
}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["message"]["content"])'
```

Expected style: a short Chinese answer. The model is a 140M learning
artifact; do not expect ChatGPT-level answers.

## Path B — Hugging Face `transformers`

This assumes `bash scripts/setup.sh` has created `.venv-pre`; otherwise
replace `.venv-pre/bin/python` with your own Python 3.12 interpreter.

```bash
uv pip install --python .venv-pre/bin/python -r requirements-hf.txt
.venv-pre/bin/python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

repo = "lynxpurr/ZhenLM-140M-SFT-v2e"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.float16)
model.eval()

messages = [{"role": "user", "content": "请用一句话介绍杭州。"}]
inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
PY
```

For reproducible comparisons use greedy (`do_sample=False`) and the same
chat template. The tokenizer's `apply_chat_template` is already configured
with the training template:

```
<|im_start|>user
{content}<|im_end|>
<|im_start|>assistant
```

## Path C — build from source

Full pipeline: data download → tokenizer → 3B-token shards → pre-training →
SFT → evaluation → GGUF. See [`reproduction.md`](reproduction.md).
Budget: ~38 GB download, ~145 GB disk, one 16 GB GPU.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Ollama is not reachable` | Start `ollama serve` with `OLLAMA_HOST=127.0.0.1:11435` |
| `model ... not found` | Run `ollama create ...` from the GGUF/Modelfile |
| Output repeats or rambles | Use greedy or lower temperature; 140M is small |
| Q4 output is much worse | Expected: Q4_K_M is not faithful for v2e; use Q8_0/F16 |
| `transformers` cannot find the model | Check the HF repo name; the model repositories are public |
| `apply_chat_template` missing | Use the tokenizer files shipped with the model (not a generic tokenizer) |
| Slow on CPU | Use GGUF + llama.cpp/Ollama; 140M is small but CPU generation is still slower than GPU |
| Math/translation answers are wrong | Expected; see the capability limits in the README |

## What to try

- Short answer: `请用一句话介绍杭州。`
- Calibration: `请告诉我 2045 年世界杯的冠军。` (2045 is not a World Cup year; it should say so)
- Translation: `把这句话翻译成英文：我爱机器学习。` (works for trained patterns)
- Math: `17 加 6 等于多少？` (likely wrong — the model does not do arithmetic)
- Format: `用一句话解释什么是光合作用。` (short answer, may miss the exact format)
- Identity: `你是谁？` (it often answers "minimind" — a known SFT-data artifact)

The demo is for observing behavior, not for benchmarking. For numbers, use
[`evaluation.md`](evaluation.md).