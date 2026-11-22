# Historical notes

This repository keeps its full commit history, including the original
day-by-day development log. Commit messages are chronological records; they
are not rewritten when later evidence changes a conclusion. The
authoritative results are in [REPORT.md](REPORT.md),
[docs/evaluation.md](docs/evaluation.md), and the model card.

## Day labels and dates

`day-N` in early commit messages is the original plan unit, not a calendar
day. The plan dates shifted during the project; the work was executed on
2026-11-18 → 11-20. Public docs use dates, not day numbers.

## Corrections to early claims

| Early commit message | Final reading |
|---|---|
| `day-12: ... 53 vs 47 达显著阈值` | Audit +6; per-item re-judgment 52 vs 45 (+7); paired McNemar **p=0.0923**, bootstrap 95% CI [0.000, 0.156] → **not significant at 0.05**. A 2026-11-22 second review of a 47-question subset **did not reproduce the advantage** (v2e 11 vs v2 11; kappa 0.660/0.453). See REPORT §13/§13.1 and `docs/evaluation.md` §6.1. |
| `day-8: v2e ... 五项判据全过` | Dev-set literal reading. The Day 11 recheck found 2 residual contamination cases (v2e 17/18 with 2 residues; clean subset 15/16); math/translation do not generalize on the holdout. See REPORT §5.1/§5.2. |
| `day-8: ... 去污后 0 撞车 / 干净` | The first checker had a `len(prompt) >= 8` false negative; the corrected checker and 90-question holdout are authoritative. See `reports/2026-11-20-eval-leak-recheck.md`. |
| `day-1/0: 手写 model.py / A 手写为主` | Final public wording: **self-contained implementation, AI-assisted, human-verified**. See the Implementation note in README.md. |
| `day-8/10: 部署切 v2 / v2e` | Deployment mentions are chronological; the final deployment is **v2e-q8** (since 2026-11-20). |
| `init: original plan / internal project references` | `day-N` is the original plan unit; internal planning references are kept for provenance, not public entry points. |
| `pretrain-lab-140m-sft-v2e` / `pretrain-lab-sft-v2e-q8` | Public model family renamed to **ZhenLM-140M** on 2026-11-22 (`ZhenLM-140M-SFT-v2e`; Ollama `zhenlm-140m-sft-v2e-q8`). Artifact SHA256 values and historical reports are unchanged. |

## What is not affected

The model artifacts, evaluation sets, 900 per-item labels, and the final
deployment are unchanged. The public model family was renamed to
**ZhenLM-140M** on 2026-11-22; artifact bytes/SHA256 are unchanged. This file
only explains how to read old commit messages and artifact names; it does not
change the results.