#!/usr/bin/env python3
"""Score the blinded second-review kit against the original labels.

Reads:
    review/labels.csv   filled by the reviewer (answer_id,label,note)
    review/.key.csv     answer_id -> model / question / original label

Writes:
    reports/<date>-second-review.md
    reports/<date>-second-review-labels.csv

Run from the repository root:
    python -I tools/score_review.py
    python -I tools/score_review.py --reviewer "colleague"
"""
from __future__ import annotations

import argparse
import csv
import datetime
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cohen_kappa(pairs: list[tuple[int, int]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    agree = sum(a == b for a, b in pairs)
    po = agree / n
    p1_orig = sum(a == 1 for a, _ in pairs) / n
    p1_second = sum(b == 1 for _, b in pairs) / n
    pe = p1_orig * p1_second + (1 - p1_orig) * (1 - p1_second)
    if pe == 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def mcnemar_exact(only_first: int, only_second: int) -> float:
    """Two-sided exact McNemar p-value (binomial, p=0.5)."""
    n = only_first + only_second
    if n == 0:
        return 1.0
    k = min(only_first, only_second)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def fmt(value: float | int | str) -> str:
    if isinstance(value, float):
        if math.isnan(value):
            return "n/a"
        return f"{value:.3f}"
    return str(value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="review/labels.csv")
    ap.add_argument("--key", default="review/.key.csv")
    ap.add_argument("--reviewer", default="project owner (second reviewer)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--out", default="")
    ap.add_argument("--csv-out", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    labels_path = ROOT / args.labels
    key_path = ROOT / args.key
    out_path = ROOT / (args.out or f"reports/{args.date}-second-review.md")
    csv_out_path = ROOT / (
        args.csv_out or f"reports/{args.date}-second-review-labels.csv"
    )

    if not labels_path.exists():
        print(f"missing {labels_path}; run tools/build_review_kit.py first", file=sys.stderr)
        return 1
    if not key_path.exists():
        print(f"missing {key_path}; run tools/build_review_kit.py first", file=sys.stderr)
        return 1
    for path in (out_path, csv_out_path):
        if path.exists() and not args.force:
            print(f"{path} exists; pass --force or choose a new output path", file=sys.stderr)
            return 1

    key = {row["answer_id"]: row for row in read_csv(key_path)}
    labels = read_csv(labels_path)
    if len(labels) != len(key):
        print(f"expected {len(key)} label rows, found {len(labels)}", file=sys.stderr)
        return 1
    seen: set[str] = set()
    missing: list[str] = []
    bad: list[str] = []
    for row in labels:
        answer_id = row["answer_id"]
        if answer_id in seen:
            print(f"duplicate answer_id: {answer_id}", file=sys.stderr)
            return 1
        seen.add(answer_id)
        if answer_id not in key:
            print(f"unknown answer_id: {answer_id}", file=sys.stderr)
            return 1
        value = (row.get("label") or "").strip()
        if value not in {"0", "1"}:
            missing.append(answer_id)
        if value not in {"", "0", "1"}:
            bad.append(f"{answer_id}={value}")
    if bad:
        print(f"invalid labels (must be 0/1): {', '.join(bad)}", file=sys.stderr)
        return 1
    if missing:
        preview = ", ".join(missing[:12])
        print(
            f"{len(missing)} labels still empty (first: {preview}); fill labels.csv first",
            file=sys.stderr,
        )
        return 1

    records: list[dict] = []
    for row in labels:
        answer_id = row["answer_id"]
        meta = key[answer_id]
        records.append(
            {
                "answer_id": answer_id,
                "pair_id": meta["pair_id"],
                "question_id": meta["question_id"],
                "tag": meta["tag"],
                "model": meta["model"],
                "original": int(meta["original_label"]),
                "second": int(row["label"]),
                "note": (row.get("note") or "").strip(),
            }
        )

    models = sorted({r["model"] for r in records})
    pairs_by_model: dict[str, list[dict]] = {m: [] for m in models}
    for r in records:
        pairs_by_model[r["model"]].append(r)

    # Per-model summary
    model_rows: list[str] = []
    overall_pairs: list[tuple[int, int]] = []
    confusion: dict[str, dict[str, int]] = {}
    for model in models:
        rows = pairs_by_model[model]
        pairs = [(r["original"], r["second"]) for r in rows]
        overall_pairs.extend(pairs)
        agree = sum(a == b for a, b in pairs)
        both1 = sum(a == 1 and b == 1 for a, b in pairs)
        only_orig = sum(a == 1 and b == 0 for a, b in pairs)
        only_second = sum(a == 0 and b == 1 for a, b in pairs)
        both0 = sum(a == 0 and b == 0 for a, b in pairs)
        confusion[model] = {
            "both1": both1,
            "only_orig": only_orig,
            "only_second": only_second,
            "both0": both0,
        }
        model_rows.append(
            f"| {model} | {len(rows)} | {sum(a for a, _ in pairs)} | "
            f"{sum(b for _, b in pairs)} | {agree}/{len(rows)} | "
            f"{fmt(cohen_kappa(pairs))} |"
        )
    all_agree = sum(a == b for a, b in overall_pairs)
    model_rows.append(
        f"| **all** | {len(overall_pairs)} | "
        f"{sum(a for a, _ in overall_pairs)} | "
        f"{sum(b for _, b in overall_pairs)} | {all_agree}/{len(overall_pairs)} | "
        f"{fmt(cohen_kappa(overall_pairs))} |"
    )

    # Per-block scores (original vs second) per model
    block_order = ["math", "translate", "calibration", "other"]
    block_rows: list[str] = []
    for block in block_order:
        block_rows.append(f"### {block}")
        block_rows.append("")
        block_rows.append("| Model | n | Original | Second | Agreement |")
        block_rows.append("|---|---:|---:|---:|---:|")
        for model in models:
            rows = [
                r
                for r in pairs_by_model[model]
                if (r["tag"] == block) or (block == "other" and r["tag"] not in {"math", "translate", "calibration"})
            ]
            if not rows:
                continue
            agree = sum(r["original"] == r["second"] for r in rows)
            block_rows.append(
                f"| {model} | {len(rows)} | {sum(r['original'] for r in rows)} | "
                f"{sum(r['second'] for r in rows)} | {agree}/{len(rows)} |"
            )
        block_rows.append("")

    # Paired v2e vs v2 on the same 40 questions
    paired: dict[str, dict[str, int]] = {}
    for r in records:
        paired.setdefault(r["pair_id"], {})[r["model"]] = r["second"]
    assert all(len(v) == 2 for v in paired.values()), "each pair must have both models"
    n_pairs = len(paired)

    def pair_counts() -> tuple[int, int, int, int]:
        both = only_v2e = only_v2 = neither = 0
        for v in paired.values():
            a, b = v["v2e"], v["v2"]
            if a == 1 and b == 1:
                both += 1
            elif a == 1 and b == 0:
                only_v2e += 1
            elif a == 0 and b == 1:
                only_v2 += 1
            else:
                neither += 1
        return both, only_v2e, only_v2, neither

    both, only_v2e, only_v2, neither = pair_counts()
    p_second = mcnemar_exact(only_v2e, only_v2)

    # Original re-judgment on the same pairs
    orig_by_pair: dict[str, dict[str, int]] = {}
    for r in records:
        orig_by_pair.setdefault(r["pair_id"], {})[r["model"]] = r["original"]
    both_o = only_v2e_o = only_v2_o = neither_o = 0
    for v in orig_by_pair.values():
        a, b = v["v2e"], v["v2"]
        if a == 1 and b == 1:
            both_o += 1
        elif a == 1 and b == 0:
            only_v2e_o += 1
        elif a == 0 and b == 1:
            only_v2_o += 1
        else:
            neither_o += 1
    p_original = mcnemar_exact(only_v2e_o, only_v2_o)

    # Appendix: per-question labels
    appendix_by_pair: dict[str, dict] = {}
    for r in records:
        appendix_by_pair.setdefault(
            r["pair_id"],
            {
                "pair_id": r["pair_id"],
                "question_id": r["question_id"],
                "tag": r["tag"],
            },
        )
        appendix_by_pair[r["pair_id"]][f"{r['model']}_original"] = r["original"]
        appendix_by_pair[r["pair_id"]][f"{r['model']}_second"] = r["second"]
    appendix_rows = [
        f"| {r['pair_id']} | `{r['question_id']}` | {r['tag']} | "
        f"{r.get('v2_original', '')} | {r.get('v2_second', '')} | "
        f"{r.get('v2e_original', '')} | {r.get('v2e_second', '')} |"
        for r in sorted(appendix_by_pair.values(), key=lambda x: x["pair_id"])
    ]

    report = f"""# Second-review agreement ({n_pairs}-question subset)

- Date: {args.date}
- Reviewer: {args.reviewer}
- Scope: 14 math + 14 translate + 6 calibration + 5 fluency-en + 5 reason + fact-zh + format + fact-en; models v2 and v2e; greedy answers from `reports/2026-11-21-holdout-eval-v3.csv`.
- Blinding: A/B order randomized per question (seed 20261122); the reviewer was asked not to open `.key.csv` until all labels were complete.
- This is a **second review**, not a fully independent one: the reviewer is the project owner and the original labels were produced by the coding agent. The {n_pairs}-question subset is smaller than the pre-registered 90-question comparison; subset McNemar is exploratory.

## Agreement with the original labels

| Model | n | Original | Second review | Agreement | Cohen's kappa |
|---|---:|---:|---:|---:|---:|
{chr(10).join(model_rows)}

### Confusion (original vs second review)

| Model | both 1 | only original 1 | only second 1 | both 0 |
|---|---:|---:|---:|---:|
""" + "\n".join(
        f"| {m} | {c['both1']} | {c['only_orig']} | {c['only_second']} | {c['both0']} |"
        for m, c in confusion.items()
    ) + f"""

## Per-block scores

{chr(10).join(block_rows)}

## Paired comparison (same {n_pairs} questions)

| | Second review | Original re-judgment |
|---|---:|---:|
| both correct | {both} | {both_o} |
| only v2e correct | {only_v2e} | {only_v2e_o} |
| only v2 correct | {only_v2} | {only_v2_o} |
| neither | {neither} | {neither_o} |
| v2e − v2 | {only_v2e - only_v2:+d}/{n_pairs} | {only_v2e_o - only_v2_o:+d}/{n_pairs} |
| McNemar exact p | {fmt(p_second)} | {fmt(p_original)} |

The original 90-question comparison is the pre-registered result
(v2e 52 vs v2 45, McNemar p=0.0923). This table is a {n_pairs}-question
subset check and must not replace it.

## Appendix: per-question labels

| Pair | Question | Tag | v2 orig | v2 second | v2e orig | v2e second |
|---|---|---|---|---|---:|---:|
{chr(10).join(appendix_rows)}
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    with csv_out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "answer_id",
                "pair_id",
                "question_id",
                "tag",
                "model",
                "original_label",
                "second_label",
                "note",
            ],
        )
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "answer_id": r["answer_id"],
                    "pair_id": r["pair_id"],
                    "question_id": r["question_id"],
                    "tag": r["tag"],
                    "model": r["model"],
                    "original_label": r["original"],
                    "second_label": r["second"],
                    "note": r["note"],
                }
            )

    print("Second-review summary")
    for model in models:
        rows = pairs_by_model[model]
        print(
            f"  {model:4s} n={len(rows):2d} "
            f"original={sum(r['original'] for r in rows):2d} "
            f"second={sum(r['second'] for r in rows):2d} "
            f"kappa={fmt(cohen_kappa([(r['original'], r['second']) for r in rows]))}"
        )
    print(f"  paired v2e-v2: {only_v2e - only_v2:+d}/{n_pairs}, McNemar p={fmt(p_second)}")
    print(f"wrote {out_path if not out_path.is_relative_to(ROOT) else out_path.relative_to(ROOT)}")
    print(f"wrote {csv_out_path if not csv_out_path.is_relative_to(ROOT) else csv_out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())