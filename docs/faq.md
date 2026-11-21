# FAQ

### Why 140M parameters?

The goal was a complete from-scratch lifecycle on one 16 GB consumer GPU,
not a competitive model. 140M (d768/L16/H12) gives ~52k tokens/s and a
16-hour pre-training run; a 1B model would not fit the time/GPU budget.
The report compares the result to GPT-2 124M-level capability, not to
modern chat models.

### Why is the math so bad? Did you fix it?

The dev set showed `3+5=8` and `7×6=42`, but those were memory + a narrow
lookup table. On unseen combinations (`13×5`, `17+6`, `100−37`, `3×13`) the
model is wrong across versions. The 14-question capability block scores
0–3/14. The data-side "fixes" did not create arithmetic ability; 140M
parameters and 3B tokens are not enough for reliable multi-digit arithmetic.
This is disclosed, not hidden.

### Why not deploy LoRA?

LoRA r=8/r=12 saves memory (9.74 GB vs 12.05 GB) and forgets less, but
1 epoch underfits: val 1.8253/1.8054 vs 1.6038 for full fine-tuning.
Rank r8→r12 buys only −0.020; 1→2 epochs buys only −0.013; the gap to full
fine-tuning remains ~0.19. LoRA is suitable for domain increments, not the
first alignment of a from-scratch base model. The 2-epoch run improves
capability (holdout 42→48) but still does not close the gap.

### Why Q8_0 instead of Q4_K_M?

Q4_K_M is smaller (103 MB) but **not faithful** for v2e: it loses the newly
learned behavior (math 42→72, translation reverts to English). Q8_0 (174 MB)
preserves it; F16 (326 MB) is bit-for-bit faithful in the 5/5 spot check.
This is the "quantization eats weak memories" effect: the new behavior
conflicts with the base prior, and quantization noise lets the prior win.

### What is the "+6"/"+7"? Is it statistically significant?

On the 90-question holdout, the original audit gave v2e 53/90 vs v2 47/90
(+6). A 2026-11-21 per-item re-judgment from the stored answers gives
v2e 52/90 vs v2 45/90 (+7). Both meet the pre-registered threshold (≥5).

However, the paired McNemar exact test on the re-judgment is **p = 0.0923**
(not significant at 0.05), and the bootstrap 95% CI [0.000, 0.156] includes
0. The advantage is concentrated in English fluency (v2e 5/5 vs v2 0/5);
math is −1 and translation/calibration are tied. Read it as **"directionally
better, threshold met, not statistically established"**, not as a large or
certain improvement. The earlier 30-question "23 vs 23" was underpowered.

### Is it production-ready?

No. It has no safety tuning, no RLHF, no long context (1024 tokens), no
factuality guarantee, and weak math/translation. It is a learning/research
artifact and a local demo.

### Can I use it commercially?

The code and model weights are Apache-2.0; documentation and eval sets are
CC BY 4.0. Upstream data licenses (FineWeb-Edu ODC-BY 1.0 + Common Crawl
ToU; minimind_dataset Apache-2.0) still apply. Read `NOTICE` and
`data/LICENSE`, and make your own legal assessment. The model may reproduce
or paraphrase training data; outputs are your responsibility.

### Can I run it on CPU?

Inference: yes, via GGUF + llama.cpp/Ollama. It is a 140M model, so CPU
generation is viable though slower than GPU. Training: not practically;
the full pipeline assumes a CUDA GPU with ~12 GB peak memory.

### Why Chinese and English? Why these datasets?

The target was a bilingual small model. English uses FineWeb-Edu
(sample-10BT), Chinese uses minimind's `pretrain_t2t`; both are public and
permissively licensed for this use. The 60/40 token mix was chosen to keep
Chinese coverage while giving English enough volume to learn fluency.
A language-split validation showed the English upsample did not dilute
Chinese (±0.15% supervised PPL vs v2).

### How was the evaluation contamination found?

While documenting the "dedup hard gate", a standalone checker
(`tools/check_eval_leak.py`) was run against the historical data. It found
that early SFT extras had copied evaluation prompts (e.g., the 2027 World
Cup question), and that the original in-build assertion had a
`len(prompt) >= 8` guard that skipped short prompts. The assertion and the
checker were fixed, the residues were disclosed, and v2e is labelled
"partially clean" (2 residues; clean subset 15/16). See
`reports/2026-11-20-eval-leak-recheck.md`.

### Why is there no public demo?

Hosting a 140M model is cheap but a public, unauthenticated chat endpoint
adds abuse and maintenance risk. The local demo runs in two minutes with
Ollama; a hosted Space may be added later. If you expose the demo, set a
bind address you trust and add rate limiting — the built-in server has no
authentication.

### What's next?

The 900 per-question labels and the McNemar/bootstrap analysis are already
published. The remaining items are an independent second review of a subset
of the labels and, optionally after v1.0, a fully clean `v2f` rebuild. See
[CHANGELOG.md](../CHANGELOG.md) and the release notes. Contributions and
corrections are welcome, especially on evaluation methodology.

### How can I contribute?

Open an issue with the exact command, checkpoint, and expected vs actual
output. For evaluation changes, include the dedup check result and a
positive control. Please do not add evaluation prompts to training data —
that is the exact failure this project spent days fixing.