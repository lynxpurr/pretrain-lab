# Second-review agreement (47-question subset)

> Adjudication: four labels were corrected after a consistency check; see
> [`2026-11-22-second-review-adjudication.md`](2026-11-22-second-review-adjudication.md).

- Date: 2026-11-22
- Reviewer: project owner (second reviewer)
- Scope: 14 math + 14 translate + 6 calibration + 5 fluency-en + 5 reason + fact-zh + format + fact-en; models v2 and v2e; greedy answers from `reports/2026-11-21-holdout-eval-v3.csv`.
- Blinding: A/B order randomized per question (seed 20261122); the reviewer was asked not to open `.key.csv` until all labels were complete.
- This is a **second review**, not a fully independent one: the reviewer is the project owner and the original labels were produced by the coding agent. The 47-question subset is smaller than the pre-registered 90-question comparison; subset McNemar is exploratory.

## Agreement with the original labels

| Model | n | Original | Second review | Agreement | Cohen's kappa |
|---|---:|---:|---:|---:|---:|
| v2 | 47 | 18 | 11 | 40/47 | 0.660 |
| v2e | 47 | 24 | 11 | 34/47 | 0.453 |
| **all** | 94 | 42 | 22 | 74/94 | 0.549 |

### Confusion (original vs second review)

| Model | both 1 | only original 1 | only second 1 | both 0 |
|---|---:|---:|---:|---:|
| v2 | 11 | 7 | 0 | 29 |
| v2e | 11 | 13 | 0 | 23 |

## Per-block scores

### math

| Model | n | Original | Second | Agreement |
|---|---:|---:|---:|---:|
| v2 | 14 | 2 | 2 | 14/14 |
| v2e | 14 | 1 | 1 | 14/14 |

### translate

| Model | n | Original | Second | Agreement |
|---|---:|---:|---:|---:|
| v2 | 14 | 5 | 3 | 12/14 |
| v2e | 14 | 5 | 4 | 13/14 |

### calibration

| Model | n | Original | Second | Agreement |
|---|---:|---:|---:|---:|
| v2 | 6 | 6 | 3 | 3/6 |
| v2e | 6 | 6 | 1 | 1/6 |

### other

| Model | n | Original | Second | Agreement |
|---|---:|---:|---:|---:|
| v2 | 13 | 5 | 3 | 11/13 |
| v2e | 13 | 12 | 5 | 6/13 |


## Paired comparison (same 47 questions)

| | Second review | Original re-judgment |
|---|---:|---:|
| both correct | 7 | 16 |
| only v2e correct | 4 | 8 |
| only v2 correct | 4 | 2 |
| neither | 32 | 21 |
| v2e − v2 | +0/47 | +6/47 |
| McNemar exact p | 1.000 | 0.109 |

The original 90-question comparison is the pre-registered result
(v2e 52 vs v2 45, McNemar p=0.0923). This table is a 47-question
subset check and must not replace it.

## Appendix: per-question labels

| Pair | Question | Tag | v2 orig | v2 second | v2e orig | v2e second |
|---|---|---|---|---|---:|---:|
| P01 | `holdout-math-add2` | math | 0 | 0 | 0 | 0 |
| P02 | `holdout-math-mul2` | math | 0 | 0 | 0 | 0 |
| P03 | `holdout-math-sub` | math | 0 | 0 | 0 | 0 |
| P04 | `holdout3-math-mul-commute` | math | 0 | 0 | 0 | 0 |
| P05 | `holdout3-math-mul-4x15` | math | 1 | 1 | 0 | 0 |
| P06 | `holdout3-math-mul-23x5` | math | 0 | 0 | 0 | 0 |
| P07 | `holdout3-math-add-34-28` | math | 0 | 0 | 0 | 0 |
| P08 | `holdout3-math-sub-50-18` | math | 0 | 0 | 0 | 0 |
| P09 | `holdout3-math-multi-1` | math | 0 | 0 | 0 | 0 |
| P10 | `holdout3-math-multi-2` | math | 0 | 0 | 0 | 0 |
| P11 | `holdout3-math-multi-3` | math | 0 | 0 | 0 | 0 |
| P12 | `holdout3-math-repeat-add` | math | 0 | 0 | 0 | 0 |
| P13 | `holdout3-math-en` | math | 0 | 0 | 1 | 1 |
| P14 | `holdout3-math-word` | math | 1 | 1 | 0 | 0 |
| P15 | `holdout-trans-zh2en-hometown` | translate | 1 | 1 | 1 | 1 |
| P16 | `holdout-trans-en2zh-weather` | translate | 1 | 0 | 1 | 0 |
| P17 | `holdout-trans-en2zh-knowledge` | translate | 0 | 0 | 0 | 0 |
| P18 | `holdout3-trans-en2zh-dogs` | translate | 0 | 0 | 0 | 0 |
| P19 | `holdout3-trans-en2zh-time` | translate | 0 | 0 | 0 | 0 |
| P20 | `holdout3-trans-en2zh-books` | translate | 0 | 0 | 0 | 0 |
| P21 | `holdout3-trans-en2zh-meeting` | translate | 0 | 0 | 0 | 0 |
| P22 | `holdout3-trans-en2zh-idiom` | translate | 0 | 0 | 0 | 0 |
| P23 | `holdout3-trans-en2zh-life` | translate | 0 | 0 | 0 | 0 |
| P24 | `holdout3-trans-zh2en-learning` | translate | 1 | 1 | 1 | 1 |
| P25 | `holdout3-trans-zh2en-wait` | translate | 0 | 0 | 0 | 0 |
| P26 | `holdout3-trans-zh2en-hard` | translate | 0 | 0 | 0 | 0 |
| P27 | `holdout3-trans-zh2en-book` | translate | 1 | 1 | 1 | 1 |
| P28 | `holdout3-trans-zh2en-music` | translate | 1 | 0 | 1 | 1 |
| P29 | `holdout-calib-olympics` | calibration | 1 | 0 | 1 | 0 |
| P30 | `holdout-calib-winter` | calibration | 1 | 1 | 1 | 0 |
| P31 | `holdout-calib-ballon` | calibration | 1 | 1 | 1 | 1 |
| P32 | `holdout3-calib-wc2046` | calibration | 1 | 0 | 1 | 0 |
| P33 | `holdout3-calib-olympics2044` | calibration | 1 | 0 | 1 | 0 |
| P34 | `holdout3-calib-nobel2045` | calibration | 1 | 1 | 1 | 0 |
| P35 | `holdout-enflu-moon` | fluency-en | 0 | 0 | 1 | 0 |
| P36 | `holdout-enflu-cat` | fluency-en | 0 | 0 | 1 | 0 |
| P37 | `holdout3-enflu-birds` | fluency-en | 0 | 0 | 1 | 1 |
| P38 | `holdout3-enflu-morning` | fluency-en | 0 | 0 | 1 | 1 |
| P39 | `holdout3-enflu-horses` | fluency-en | 0 | 0 | 1 | 0 |
| P40 | `holdout-reason-keys` | reason | 0 | 0 | 0 | 0 |
| P41 | `holdout-reason-cold` | reason | 1 | 1 | 1 | 1 |
| P42 | `holdout3-reason-phone` | reason | 0 | 0 | 1 | 0 |
| P43 | `holdout3-reason-late` | reason | 0 | 0 | 1 | 0 |
| P44 | `holdout3-reason-slow` | reason | 1 | 0 | 1 | 0 |
| P45 | `holdout-fact-ocean` | fact-zh | 1 | 0 | 1 | 0 |
| P46 | `holdout-format-env` | format | 1 | 1 | 1 | 1 |
| P47 | `holdout-fact-canada` | fact-en | 1 | 1 | 1 | 1 |
