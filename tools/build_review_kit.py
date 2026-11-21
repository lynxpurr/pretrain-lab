#!/usr/bin/env python3
"""Build a blinded second-review kit for the 90-question holdout.

The kit is written to ``review/`` (gitignored):

    review/README.md      instructions and rubric
    review/answers.md     blinded sheet: 40 prompts, two answers each (A/B)
    review/answers.csv    same data in CSV (reference, do not edit)
    review/labels.csv     fill this: answer_id,label,note
    review/.key.csv       answer_id -> model / question / original label

Selection (47 questions):
  - all 14 math
  - all 14 translate
  - all 6 calibration
  - all 5 fluency-en and all 5 reason
  - one each from fact-zh, format, fact-en

This deliberately includes the tags that carry the v2e-v2 increment
(fluency-en +5, reason +2, fact-zh +1, format +1) and the negative fact-en
item, so the second review can check the source of the +7 as well as the
capability blocks.

The two models are v2 and v2e. A/B order is randomized per question with a
fixed seed, so the sheet does not reveal which answer is the deployed model.

Run from the repository root:
    python -I tools/build_review_kit.py
    python -I tools/build_review_kit.py --force   # overwrite an unlabeled kit
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / "data/eval/tests-holdout-v3.json"
EVAL_CSV = ROOT / "reports/2026-11-21-holdout-eval-v3.csv"
MANUAL_CSV = ROOT / "reports/2026-11-21-holdout-v3-manual-labels.csv"

MODELS = ("v2", "v2e")
BLOCKS = ("math", "translate", "calibration")
EXTRAS = (("fluency-en", 5), ("reason", 5), ("fact-zh", 1), ("format", 1), ("fact-en", 1))
SEED = 20261122


def blockquote(text: str) -> str:
    lines = text.rstrip("\n").splitlines() or [""]
    return "\n".join("> " + line if line else ">" for line in lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="review")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    labels_path = out_dir / "labels.csv"
    if labels_path.exists() and not args.force:
        with labels_path.open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if any((r.get("label") or "").strip() for r in rows):
            print(
                f"{labels_path} already contains labels; pass --force to overwrite",
                file=sys.stderr,
            )
            return 1

    questions = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    by_tag: dict[str, list[dict]] = {}
    for q in questions:
        by_tag.setdefault(q["tag"], []).append(q)

    selected: list[dict] = []
    for tag in BLOCKS:
        assert by_tag.get(tag), f"missing tag {tag}"
        selected.extend(by_tag[tag])
    for tag, count in EXTRAS:
        assert by_tag.get(tag), f"missing tag {tag}"
        assert len(by_tag[tag]) >= count, f"{tag}: need {count}"
        selected.extend(by_tag[tag][:count])
    assert len(selected) == 47, len(selected)

    answers: dict[tuple[str, str], str] = {}
    with EVAL_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["model"] in MODELS:
                answers[(row["model"], row["test_id"])] = row["answer"]

    manual: dict[tuple[str, str], dict] = {}
    with MANUAL_CSV.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["model"] in MODELS:
                manual[(row["model"], row["test_id"])] = row

    missing = [
        (model, q["id"])
        for q in selected
        for model in MODELS
        if (model, q["id"]) not in answers or (model, q["id"]) not in manual
    ]
    assert not missing, f"missing answers/labels: {missing}"

    rng = random.Random(SEED)
    answer_rows: list[dict[str, str]] = []
    label_rows: list[dict[str, str]] = []
    key_rows: list[dict[str, str]] = []
    md: list[str] = [
        "# Second-review sheet (blinded)",
        "",
        "47 questions × 2 answers = 94 judgments. Fill `labels.csv`.",
        "Do not open `.key.csv` until all labels are complete.",
        "",
    ]

    for i, q in enumerate(selected, start=1):
        pair_id = f"P{i:02d}"
        order = list(MODELS)
        rng.shuffle(order)
        md.append(f"## {pair_id}")
        md.append("")
        md.append(f"**Prompt:** {q['prompt']}")
        md.append("")
        for j, model in enumerate(order):
            answer_id = f"{pair_id}-{'AB'[j]}"
            answer = answers[(model, q["id"])]
            original = manual[(model, q["id"])]
            answer_rows.append(
                {
                    "answer_id": answer_id,
                    "pair_id": pair_id,
                    "prompt": q["prompt"],
                    "answer": answer,
                }
            )
            label_rows.append({"answer_id": answer_id, "label": "", "note": ""})
            key_rows.append(
                {
                    "answer_id": answer_id,
                    "pair_id": pair_id,
                    "question_id": q["id"],
                    "tag": q["tag"],
                    "model": model,
                    "original_label": original["manual_pass"],
                    "original_note": original.get("note", ""),
                }
            )
            md.append(f"**Answer {'AB'[j]}**")
            md.append("")
            md.append(blockquote(answer))
            md.append("")
        md.append("---")
        md.append("")

    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "answers.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["answer_id", "pair_id", "prompt", "answer"]
        )
        writer.writeheader()
        writer.writerows(answer_rows)

    with labels_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["answer_id", "label", "note"])
        writer.writeheader()
        writer.writerows(label_rows)

    with (out_dir / ".key.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "answer_id",
                "pair_id",
                "question_id",
                "tag",
                "model",
                "original_label",
                "original_note",
            ],
        )
        writer.writeheader()
        writer.writerows(key_rows)

    (out_dir / "answers.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "README.md").write_text(
        f"""# Second-review kit (blinded)

This directory is **gitignored** and is not part of the public repository.

## What to do

1. Open `answers.md`: 47 prompts, each with **Answer A** and **Answer B**.
2. Fill `labels.csv`: one row per `answer_id`, `label` = `1` or `0`,
   optional `note`.
3. **Do not open `.key.csv`** until all 94 labels are filled. It maps A/B to
   models and contains the original labels.
4. Run:

   ```bash
   python -I tools/score_review.py
   ```

   This writes `reports/<date>-second-review.md` and
   `reports/<date>-second-review-labels.csv`.

## Rubric

- `1` = semantically correct and complete.
- `0` = wrong, fabricated, refusal where an answer is expected, echo of the
  prompt, or repetition garbage.

For calibration questions, a refusal or a correct premise correction counts
as `1` if it does not invent a concrete answer. For math, the number must be
correct. For translation, judge the meaning in the target language, not
keyword overlap.

## Scope and caveat

- 14 math + 14 translate + 6 calibration + 5 fluency-en + 5 reason +
  fact-zh + format + fact-en.
- Models: v2 and v2e, blinded and randomized per question.
- This is a **second review**, not a fully independent one: the reviewer is
  the project owner, and the original labels were produced by the coding
  agent. Report it as a second-review agreement check, not as external
  validation.

Estimated time: 40–55 minutes.
""",
        encoding="utf-8",
    )

    print(f"wrote {out_dir}/ (47 questions, 94 answers)")
    print("fill review/labels.csv, then run: python -I tools/score_review.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())