# Evaluation

The project treats evaluation as the main artifact, not an afterthought.
This page documents the test sets, the scoring protocol, the headline
numbers, and the caveats you should apply before quoting them.

## 1. Test sets

| Set | File | Size | Purpose |
|---|---|---|---|
| Dev | `data/eval/tests.json` | 18 questions / 13 tags | iteration only; used during data development |
| Holdout v2 | `data/eval/tests-holdout.json` | 30 questions | first unseen check (2026-11-20) |
| Holdout v3 | `data/eval/tests-holdout-v3.json` | **90 questions** (30 old + 60 new) | capability acceptance (2026-11-21) |

Holdout v3 includes three capability blocks:

- **Math: 14 questions** — multi-operand, multi-step, two-digit, order-swapped,
  English, and word problems.
- **Translation: 14 questions** — both directions × three instruction
  patterns + idiom probes.
- **Calibration: 6 questions** — future events (2044–2046) where the correct
  behavior is to refuse to invent or to correct the premise.

Question schema:

```json
{"id": "holdout3-math-add", "prompt": "17 加 6 等于多少？", "expect_any": ["23"], "tag": "math"}
```

## 2. Protocol

- **Decoding**: greedy (`temperature=0`), same chat template, same tokenizer
  for every model. The demo uses T=0.3, but it is a separate display setting
  and is not mixed into the comparison table.
- **Keyword score**: `expect_any` substring match (normalized).
- **Manual score**: per-question binary judgment (1 = semantically correct /
  complete; 0 = wrong, fabricated, refusal, echo, or repetition garbage).
  The 90×10 = 900 cells were judged by the same agent that wrote the
  questions — a known bias, see §6.
- **Degeneration**: distinct-2 and rep-4 (4-gram repetition rate).
- **Perplexity**: two protocols (all tokens vs assistant-supervised tokens),
  plus language splits via `tools/eval_lang.py`.

## 3. Headline results (holdout v3, 90 questions)

| Model | Keyword | Manual | Δ (manual−keyword) | FP | FN | rep-4 ↓ | distinct-2 ↑ |
|---|---|---|---|---|---|---|---|
| base | 25 | **12** | −13 | 13 | 0 | 0.738 | 0.217 |
| v1 | 61 | **47** | −14 | 17 | 3 | 0.248 | 0.604 |
| v2 | 61 | **47** | −14 | 17 | 3 | 0.168 | 0.727 |
| v2b | 55 | 44 | −11 | 14 | 3 | 0.167 | 0.731 |
| v2c | 54 | 45 | −9 | 11 | 2 | 0.163 | 0.720 |
| v2d | 59 | 48 | −11 | 14 | 3 | 0.159 | 0.741 |
| **v2e (deployed)** | 59 | **53** | −6 | **8** | 2 | **0.138** | **0.753** |
| LoRA r8 | 53 | 43 | −10 | 13 | 3 | 0.347 | 0.543 |
| LoRA r12 | 54 | 42 | −12 | 14 | 2 | 0.309 | 0.567 |
| LoRA r12 2ep | 56 | 48 | −8 | 12 | 4 | 0.283 | 0.601 |

> **2026-11-21 re-judgment**: the original per-item labels were not persisted;
> a full re-judgment from the stored greedy answers gives **v2e 52 vs v2 45
> (+7)**. The audit aggregate above (53 vs 47) is kept for comparison. See
> §6 and §6.1 for the second-review sensitivity.
>
> **2026-11-22 second review**: a blinded 47-question subset gives **v2e 11
> vs v2 11** (kappa 0.660/0.453; paired p=1.000). The +6/+7 is
> rubric-sensitive; see §6.1.

The keyword score is a "mention detector", not a correctness detector.
The manual score is the primary number. The gap is largest for base and v1
(echo/repetition tricks), smallest for v2e.

## 4. Capability blocks

| Block | Best result | Verdict |
|---|---|---|
| Math (14) | 0–3 / 14 (v2e 1, v2 2, lora12 3) | ✗ **lookup-table, not arithmetic** |
| Translation (14) | 0–5 / 14 (v2/v2e 5) | ✗ **sentence-pattern level, not general translation** |
| Calibration (6) | 5–6/6 under the original lenient labels; strict second review 1–3/6 | ⚠️ **rubric-sensitive**: refuses to invent, but premise corrections are often factually wrong (2044/2046 are event years) |

### Math details

- Unseen combinations are wrong across the board: `17+6`→19, `100−37`→37,
  `34+28`→46/56/42, `50−18`→42/45, `23×5`→56/40/45, `3×13`→63/56/35.
- Multi-step: `(5+4)×2`, `12−5+3`, `20−8+6` — no correct answers.
- Two bright spots: the word problem "Xiaoming has 12 apples, eats 5" is
  solved by 7/10 versions (single-digit subtraction in a narrative);
  English `9+6=15` is answered correctly only by v2d/v2e.
- Conclusion: the dev `8`/`42` results are memory + a narrow lookup table,
  not arithmetic.

### Translation details

- zh→en simple sentences generalize to same-structure new sentences:
  `我爱我的家乡` 9/10, `我在学中文` 9/10, `这本书很有趣` 9/10,
  `我喜欢听音乐` 7/10.
- en→zh mostly fails: `The train leaves…`, `Dogs are loyal`,
  `Time is money`, idioms and long sentences echo English or produce garbage
  (v2 outputs Japanese for "dogs").
- Direction failure: `今天非常冷` is translated as **hot** by all versions
  (strong prior overrides the weak memory).
- `Translate into English: 请稍等一下` → "Sure! Please provide the text…"
  (the model treats it as a request, not an instruction).
- Conclusion: the exact instruction pairs taught a few sentence patterns,
  not the translation task.

### Calibration details

- The v2-family models refuse to invent future facts at 5–6/6 **under the
  original labels**, including 2044/2045/2046 events they never saw.
- Quality differs: v2d gives the cleanest refusal ("I cannot be certain…
  it has not happened yet"); v2e/v2 often use a premise-correction phrasing
  that is technically wrong for Olympic/World Cup years (2044/2046 are
  event years).
- **Strict second review (2026-11-22): v2 3/6, v2e 1/6.** The model often
  says `2046 年没有世界杯` (2046 is a World Cup year) or `2044 年没有奥运会`
  (2044 is a Summer Olympics year). It refuses to name a champion, but the
  stated reason is wrong. The calibration "✓" is therefore rubric-sensitive,
  not a clean capability win.
- base/v1/LoRA often fabricate concrete entities (cities, teams, names).

## 5. Keyword scoring pitfalls

**False positives** (keyword hit, manual 0):

- `fact-continent`: "about 70% of the land" — the "7" comes from "70%".
- `fact-everest-en`: answers "6.5 inches" — the "6" is a measurement, not
  the number of strings.
- `fact-mars`: all 10 versions "pass" only because they echo "red planet"
  from the prompt; none says iron/rust.
- `code-swap`: all 10 use `zip` nonsense; the keyword table is too loose.
- `summary-library/rain`: base echoes the input, which contains every keyword.

**False negatives** (keyword 0, manual 1):

- `fact-lightspeed`: **9/10 versions answer 299,792 (correct)**, but the
  `expect_any` list only had `30万`/`300000`/`三十万`/`3×10`. This is the
  largest systematic false negative: the knowledge is there, the score says no.
- `explain-democracy`: v2c says "citizen participation, free speech, social
  justice" — semantically right, but misses the exact words.
- `code-parity`: v2c writes a complete `is_even` function; the keyword table
  misses it.

Rules used in this project:

1. Numeric `expect_any` must cover common written forms (Arabic digits,
   thousands separators, scientific notation, spoken units).
2. Do not use a prompt word as the expected label (echo false positives).
3. Always report keyword and manual scores side by side.

## 6. Manual calibration and statistical caveats

- The original 900 cells (10 models × 90 questions) were not persisted. On
  2026-11-21 they were re-judged from the stored greedy answers; the
  per-item labels are in `reports/2026-11-21-holdout-v3-manual-labels.csv`
  (900 rows), and the recompute is in
  `reports/2026-11-21-manual-labels-audit.md`. This is a re-judgment, not a
  recovery of the original labels.
- Re-judgment totals: **v2e 52/90 vs v2 45/90 = +7** (the original audit
  was 53 vs 47 = +6). FP/FN: v2e 9/2, v2 19/3. The original aggregate is
  therefore not exactly reproducible; the per-item labels are published so
  others can audit the judgment.
- The pre-registered rule was: v2e − v2 ≥ 5/90 → "significantly better".
  Both the audit (+6) and the re-judgment (+7) meet the threshold **under the
  original labels**; see §6.1 for the second-review sensitivity.
- **McNemar exact test (re-judgment): p = 0.0923**; paired bootstrap 95% CI
  for the difference: **[0.000, 0.156]** (10,000 resamples), lower bound ≈0.
  **Not significant at 0.05.** The correct public wording is "meets the
  pre-registered threshold under the original labels; not statistically
  significant at 0.05; a strict 47-question second review did not reproduce
  the advantage (11 vs 11), so the improvement is not robust".
- The advantage is concentrated in **English fluency** (v2e 5/5 vs v2 0/5)
  and a few reason/format items; math is −1, translation/calibration are
  tied. It is not a general capability improvement. The old-30/new-60 split
  is +2/+5 — not driven by the old questions. **The second review (§6.1) did
  not reproduce this concentration**: under a strict rubric, the fluency-en
  answers contain repetition and factual errors (e.g. `the moon is the
  brightest of the constellations`, `the cat is a member of Canidae`), and
  the subset difference collapses to 0.
- For a single proportion with n = 90, the 95% interval is roughly ±9–10
  questions at p ≈ 0.5; the paired interval above is [0, +14] questions.
  The earlier note "±3–4 questions" was an approximation, not a standard CI.
- The 30-question holdout gave "23 vs 23"; that was **underpowered**, not
  evidence of equality. The lesson is: compute the interval before declaring
  "no difference".
- Other model-to-model comparisons are exploratory; only v2e vs v2 was
  pre-registered.

### Second-review kit and result (47 questions, 2026-11-22)

The original labels were produced by the same agent that wrote the questions
(a known bias). [`tools/build_review_kit.py`](../tools/build_review_kit.py)
builds a blinded 47-question kit (94 answers; v2 and v2e, A/B randomized) for
a second reviewer. [`tools/label_review.py`](../tools/label_review.py) is an
interactive labeler that saves after each answer, and
[`tools/score_review.py`](../tools/score_review.py) reports agreement and
Cohen's kappa against the published labels.

The second review was completed by the project owner. Four labels were
corrected after a consistency check; the per-answer labels are in
[`reports/2026-11-22-second-review-labels.csv`](../reports/2026-11-22-second-review-labels.csv),
and the adjudication is in
[`reports/2026-11-22-second-review-adjudication.md`](../reports/2026-11-22-second-review-adjudication.md).

| Model | n | Original | Second review | Agreement | Cohen's kappa |
|---|---:|---:|---:|---:|---:|
| v2 | 47 | 18 | 11 | 40/47 | 0.660 |
| v2e | 47 | 24 | 11 | 34/47 | 0.453 |
| all | 94 | 42 | 22 | 74/94 | 0.549 |

Paired on the same 47 questions: **v2e 11 vs v2 11 (0/47), McNemar p=1.000**;
the original re-judgment on this subset was **+6 (24 vs 18, p=0.109)**.

Rubric sensitivity:

| Re-adjudication | v2 | v2e | v2e − v2 | McNemar p |
|---|---:|---:|---:|---:|
| Final (strict-leaning) | 11 | 11 | 0 | 1.000 |
| + lenient calibration/fact | 15 | 17 | +2 | 0.688 |
| + lenient translation | 17 | 18 | +1 | 1.000 |
| Original labels (same 47) | 18 | 24 | +6 | 0.109 |

Even the most lenient re-adjudication does not recover +6. The main drivers
are calibration premise corrections (`2046 年没有世界杯`, `2044 年没有奥运会`),
English fluency/reason answers with repetition or factual errors, and
translation answers that add content. **The +6/+7 is threshold-met under the
original labels, but not robust to reviewer/rubric; do not read it as a
capability win.** This is a second review by the project owner, not a fully
independent one; the 47-question subset is smaller than the pre-registered
90-question comparison.

## 7. Reproduce

```bash
# dev set (18 questions + PPL)
.venv-pre/bin/python -I tools/eval.py \
  --ckpt v2e=out/sft-v2e/last.pt \
  --out reports/2026-11-21-eval-dev.md
.venv-pre/bin/python -I tools/eval_format.py \
  --csv reports/2026-11-21-eval-dev.csv \
  --out reports/2026-11-21-eval-dev-rubric.md

# 90-question holdout (skip PPL)
.venv-pre/bin/python -I tools/eval.py \
  --ckpt v2e=out/sft-v2e/last.pt \
  --tests data/eval/tests-holdout-v3.json \
  --skip-ppl \
  --out reports/2026-11-21-holdout-v3.md

# language-split validation (zh/en, all/supervised)
.venv-pre/bin/python -I tools/eval_lang.py \
  --ckpt v2e=out/sft-v2e/last.pt \
  --out reports/2026-11-21-langval.md
```

The release includes `last.pt` in the Hugging Face model repository for
`eval.py`, alongside the HF/safetensors weights. The GGUF path is for
inference, not for `eval.py`.

## 8. Adding a new evaluation set

1. Use the schema `{"id", "prompt", "expect_any", "tag"}`.
2. Write same-type variants, not the training/eval originals. For math,
   avoid operands already covered by the training extras; for calibration,
   avoid years already used in the extras.
3. Run the deduplication hard gate **before** freezing:

```bash
.venv-pre/bin/python -I tools/check_eval_leak.py \
  --eval data/eval/tests.json \
  --eval data/eval/tests-holdout.json \
  --eval data/eval/tests-holdout-v3.json \
  --extra-dir data/sft-extra-v2 \
  --sft-source data/raw/minimind_dataset/sft_t2t_mini.jsonl
```

`EXIT 1` means a collision (the known dev residues will show up; that is
expected). `EXIT 0` means zero collisions. **Before trusting a zero, feed a
known collision to the checker** — a checker that cannot catch a known
violation is useless. `build_sft_v2.py` has a built-in self-test for this.

4. Freeze the file and record its SHA256 in `data/eval/SHA256SUMS`.
5. Report keyword and manual scores; include FP/FN examples.

## 9. Limitations

- 140M parameters and 3B pre-training tokens: knowledge and reasoning are
  GPT-2-level at best; many "failures" are capacity, not data.
- The holdout was written by the same agent that saw the dev failures; the
  style bias is real.
- The original labels were produced by the coding agent. A 2026-11-22
  second review (project owner, 47 questions) did not reproduce the v2e
  advantage (11 vs 11; kappa 0.660/0.453). It is a second review, not a fully
  independent one.
- The model may reproduce facts from the pre-training/SFT sources; the
  evaluation cannot fully separate "learned ability" from "source knowledge".
- Single-turn, 1024-token context; no safety or bias evaluation.