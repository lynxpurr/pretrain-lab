# Second-review adjudication note (2026-11-22)

Companion to [`2026-11-22-second-review.md`](2026-11-22-second-review.md) and
[`2026-11-22-second-review-labels.csv`](2026-11-22-second-review-labels.csv).

## What was checked

- 94/94 labels are valid 0/1; no missing rows, no duplicates.
- Four labels were corrected after a consistency check against the rubric:
  - `P24-B` (v2e) `0 → 1`: `I am learning Chinese.` is a correct translation,
    equivalent to the other model's `I'm learning Chinese.`.
  - `P27-A` (v2e) `0 → 1`: the answer is a correct translation with one
    explanatory sentence; it is not repetition.
  - `P35-B` (v2) `1 → 0`: a refusal/confabulation about the moon, not an
    answer; the other model's repetitive answer was also 0.
  - `P44-B` (v2e) `1 → 0`: the answer repeats "更新驱动程序" and is truncated;
    the other model's comparable answer was 0.
- The corrections are documented here rather than silently applied; the
  per-answer labels are published in the CSV.

## Final result (47 questions, 94 answers)

| Model | n | Original labels | Second review | Agreement | Cohen's kappa |
|---|---:|---:|---:|---:|---:|
| v2 | 47 | 18 | 11 | 40/47 | 0.660 |
| v2e | 47 | 24 | 11 | 34/47 | 0.453 |
| all | 94 | 42 | 22 | 74/94 | 0.549 |

Paired on the same 47 questions: **v2e 11 vs v2 11 (0/47), McNemar p=1.000**.
The original re-judgment on this subset was **v2e 24 vs v2 18 (+6), p=0.109**.

## Rubric sensitivity

| Re-adjudication | v2 | v2e | v2e − v2 | kappa v2 / v2e | McNemar p |
|---|---:|---:|---:|---:|---:|
| Final (strict-leaning) | 11 | 11 | 0 | 0.660 / 0.453 | 1.000 |
| + lenient calibration/fact | 15 | 17 | +2 | 0.861 / 0.704 | 0.688 |
| + lenient translation | 17 | 18 | +1 | 0.955 / 0.746 | 1.000 |
| Original labels (same 47) | 18 | 24 | +6 | — | 0.109 |

Even the most lenient re-adjudication does not recover +6. The gap is driven
by the strict treatment of English fluency/reason answers (repetition,
truncation, factual errors) and calibration premise corrections.

## Why the labels diverge

- **Calibration**: the original labels counted "refuses to invent" as 1 even
  when the premise correction was factually wrong. Examples: `2046 年没有世界杯`
  (2046 is a World Cup year) and `2044 年没有奥运会` (2044 is a Summer
  Olympics year). The strict second review counts these as 0. The model does
  refuse to name a champion, but its stated reason is wrong.
- **English fluency / reason**: the original labels gave v2e 5/5 on
  `fluency-en`; the strict review gives 2/5. The answers contain repetition
  and factual errors (`the moon is the brightest of the constellations`,
  `the cat is a member of Canidae`). They are fluent-looking but not correct.
- **Translation fidelity**: `The weather is nice today.` was rendered with
  added content (`阳光明媚，微风轻拂` / `心情也跟着好起来了`); the original
  labels counted the core meaning, the strict review counts the added content
  as a translation error.
- **Factual completeness**: `世界上最大的海洋是哪个？` is answered "太平洋" but
  with a wrong area (`1.5 万平方公里` instead of ~1.65 亿). The original
  labels counted the entity; the strict review requires the detail to be
  correct too.

## Conclusion

The +6 (audit) / +7 (re-judgment) is **threshold-met under the original
labels**, but it is **not robust to a second reviewer/rubric**: the strict
47-question second review gives **11 vs 11** and the advantage disappears;
even lenient re-adjudication gives at most +2. The public wording must not
claim that v2e is better than v2.

## Caveats

- Reviewer = project owner; this is a second review, not a fully independent
  one. The original labels were produced by the coding agent.
- 47/90 questions; the pre-registered comparison is the 90-question
  re-judgment (v2e 52 vs v2 45, McNemar p=0.0923). The subset McNemar is
  exploratory.
- The original 900-cell labels were not persisted; the "original" here is the
  2026-11-21 per-item re-judgment from stored greedy answers.
- Strict and lenient rubrics are both defensible; the point is that the
  headline result depends on which one is used.