# Changelog

> Historical commit messages use `day-N` labels and may contain preliminary
> claims; see [HISTORY.md](HISTORY.md) for the corrections.

All notable changes and results of `pretrain-lab` are recorded here.
The project follows a "evidence first" convention: every run has a summary
(`.md`), a curve (`.csv`), and a raw log (`.log`) under `reports/`.

> Release notes: [v1.0.0](docs/release-notes-v1.0.0.md).

## [Unreleased] — public release preparation (2026-11-21)

### Added
- `LICENSE` (Apache-2.0) · `NOTICE` (data/reference attributions) ·
  `CITATION.cff` · `CHANGELOG.md`.
- English `README.md` and Chinese `README.zh.md`; `docs/` quickstart,
  reproduction, evaluation, architecture, and FAQ pages.
- `requirements.txt` and `scripts/` for setup, data download, model
  download, demo, and evaluation.
- v2e Hugging Face export (fp16) and a standalone Q8_0 GGUF file.
- Per-item manual labels for the 90-question holdout
  (`reports/2026-11-21-holdout-v3-manual-labels.csv`, 900 rows) and a
  re-scoring/McNemar audit (`reports/2026-11-21-manual-labels-audit.md`).
- `HISTORY.md`: a correction table for old commit-message claims (day labels,
  +6, "five criteria", dedup, "hand-written", deployment).
- Lightweight CI: evaluation-set schema checks, leak-checker positive
  control, local link check, and `compileall`.
- A blinded second-review kit (`tools/build_review_kit.py`) and agreement
  scorer (`tools/score_review.py`) for a 47-question subset (94 answers).

### Changed
- Reader-facing docs are separated from the internal process record; the
  process record is kept local and is not part of the public repository.
- The local agent skill (`.zcode/skills/pretrain-lab/`) is untracked and
  gitignored; it remains a local-only private file. Git history is not
  rewritten, so the file is still visible in earlier commits.
- The Hugging Face quickstart snippets now pass the tokenizer output
  (`BatchEncoding`) to `generate(**inputs)` correctly for transformers 5.x;
  the example prompt uses a short factual question to avoid the known
  "minimind" identity artifact.
- Public wording downgraded: v2e vs v2 meets the pre-registered threshold
  (audit +6; re-judgment +7) but is **not statistically significant**
  (McNemar p=0.0923; 95% CI [0.000, 0.156]); the advantage is concentrated
  in English fluency.
- Public docs use dates; no day/duration selling points; AI disclosure is one
  Implementation note. Historical commit messages are not rewritten (see
  HISTORY.md). The repository is pushed; the remote README is current.

## [1.0.0] — project complete (2026-11-20; follow-up 2026-11-21)

### Model
- **137,847,552-parameter** decoder-only Transformer: d_model 768, 16 layers,
  12 heads, RoPE + RMSNorm + SwiGLU + tied embeddings, 32k BPE, context 1024.
- Pre-trained on **3.0B tokens** (English 60% FineWeb-Edu / Chinese 40%
  minimind) for 16h07m41s on one RTX 5070 Ti 16GB; validation loss 2.7709.
- SFT: 250M tokens, assistant-only mask, six full-parameter variants
  (v1, v2, v2b, v2c, v2d, v2e). Deployed model: **v2e** (val 1.6065,
  repetition-4 0.055, dev 17/18 with 2 known residues, clean subset 15/16).
- LoRA ablations: r=8 (1.20% trainable), r=12 (1.79%), and r=12 for
  2 epochs (val 1.7921). None deployed: rank and epochs each buy only
  −0.020 / −0.013 validation loss versus full fine-tuning.

### Evaluation
- Dev set: 18 questions / 13 tags; holdout v2: 30 questions; holdout v3:
  **90 questions** with math (14), translation (14), and calibration (6)
  capability blocks; three-layer bidirectional deduplication with 0 hits.
- 90-question manual calibration: base 12, v1 47, v2 47, v2b 44, v2c 45,
  v2d 48, **v2e 53**, LoRA r8 43, r12 42, r12-2ep 48.
- Capability verdicts: math **0–3/14 (✗, lookup-table not arithmetic)**;
  translation **0–5/14 (✗, sentence-pattern level)**; calibration
  **5–6/6 (✓, the only stable generalization)**.
- v2e vs v2: **+6/90**, meeting the pre-registered threshold (≥5);
  the earlier 30-question "no difference" was underpowered.
- Quantization: Q4_K_M is **not faithful** for v2e (math 42→72, translation
  reverts); Q8_0 is the deployment default; F16 is bit-for-bit faithful in
  the 5/5 spot check.

### Deployment
- GGUF F16 312MB / Q8_0 174MB; Ollama model `pretrain-lab-sft-v2e-q8`;
  zero-dependency local chat page on port 7860 (default temperature 0.3).

### Evidence
- 118 files under `reports/`, including day-by-day summaries, raw logs,
  loss curves, evaluation CSVs, holdout audits, and reproducibility checks.
- Data/checkpoint SHA256 fingerprints in `data/PROVENANCE.md` and
  `SHA256SUMS`; bit-for-bit v2e data rebuild (4/4) and byte-identical
  18/18 evaluation rows verified on 2026-11-20.

## Timeline

| Date | Milestone |
|---|---|
| 2026-11-18 | Environment, self-contained model implementation, char-level 20M loop, 32k BPE, 3B memmap shards, 140M probe (52,250 tok/s, gate ① PASS) |
| 2026-11-18 → 11-19 | 140M × 3B pre-training, 16h07m, val 2.7709 |
| 2026-11-19 | SFT v1 + evaluation framework; gate ② not triggered |
| 2026-11-19 | SFT v2/v2b, LoRA r8, GGUF/Ollama demo |
| 2026-11-19 → 11-20 | SFT v2c/v2d/v2e data iterations; evaluation contamination found and removed |
| 2026-11-20 | Deploy v2e-q8; final checks (reproducibility, 30-question holdout, LoRA r12) |
| 2026-11-20 | Deduplication false-negative fix; holdout v2 |
| 2026-11-21 | 90-question holdout, LoRA 2 epochs, language-split validation |

See [REPORT.md](REPORT.md) for the full narrative and
[reports/](reports/) for the evidence.