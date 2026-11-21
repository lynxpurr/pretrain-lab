#!/usr/bin/env python3
"""Interactive labeler for the blinded second-review kit.

Reads ``review/answers.csv`` (prompt + answer; no model names) and updates
``review/labels.csv`` after every entry, so you can stop and resume.

Run from the repository root:
    python -I tools/label_review.py
    python -I tools/label_review.py --limit 32   # one batch, then stop
    python -I tools/label_review.py --start P20-A

Inputs: 1 = correct/complete, 0 = wrong/fabricated/refusal/echo/garbage,
s = skip for now, q = save and quit. The note is optional.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEP = "─" * 72


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_labels(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["answer_id", "label", "note"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", default="review/answers.csv")
    ap.add_argument("--labels", default="review/labels.csv")
    ap.add_argument("--limit", type=int, default=0, help="stop after N new labels")
    ap.add_argument("--start", default="", help="answer_id to start at")
    args = ap.parse_args()

    answers_path = ROOT / args.answers
    labels_path = ROOT / args.labels
    if not answers_path.exists():
        print(f"missing {answers_path}; run tools/build_review_kit.py first", file=sys.stderr)
        return 1

    answers = read_csv(answers_path)
    answer_ids = [row["answer_id"] for row in answers]
    if labels_path.exists():
        labels = read_csv(labels_path)
        by_id = {row["answer_id"]: row for row in labels}
    else:
        by_id = {aid: {"answer_id": aid, "label": "", "note": ""} for aid in answer_ids}

    missing = [aid for aid in answer_ids if aid not in by_id]
    for aid in missing:
        by_id[aid] = {"answer_id": aid, "label": "", "note": ""}

    start = 0
    if args.start:
        if args.start not in by_id:
            print(f"unknown --start {args.start}", file=sys.stderr)
            return 1
        start = answer_ids.index(args.start)
    else:
        for i, aid in enumerate(answer_ids):
            if (by_id[aid].get("label") or "").strip() not in {"0", "1"}:
                start = i
                break
        else:
            print("all answers are already labeled; run tools/score_review.py")
            return 0

    done = sum(
        1 for aid in answer_ids if (by_id[aid].get("label") or "").strip() in {"0", "1"}
    )
    added = 0
    current_pair = ""

    print(f"{done}/{len(answer_ids)} labeled; starting at {answer_ids[start]}")
    print("1 = correct/complete, 0 = wrong/fabricated/refusal/echo/garbage, s = skip, q = quit")

    try:
        for i in range(start, len(answer_ids)):
            row = answers[i]
            aid = row["answer_id"]
            label = (by_id[aid].get("label") or "").strip()
            if label in {"0", "1"}:
                continue
            if args.limit and added >= args.limit:
                break

            if row["pair_id"] != current_pair:
                current_pair = row["pair_id"]
                print()
                print(SEP)
                print(f"{current_pair} · {row['prompt']}")
                print(SEP)
            print()
            print(f"[{i + 1}/{len(answer_ids)}] {aid}")
            print(row["answer"])
            print()

            while True:
                choice = input("label [1/0/s/q]: ").strip().lower()
                if choice == "q":
                    raise KeyboardInterrupt
                if choice == "s":
                    print("skipped")
                    break
                if choice in {"0", "1"}:
                    note = input("note (optional): ").strip()
                    by_id[aid]["label"] = choice
                    by_id[aid]["note"] = note
                    write_labels(labels_path, [by_id[x] for x in answer_ids])
                    added += 1
                    break
                print("enter 1, 0, s, or q")
    except (KeyboardInterrupt, EOFError):
        write_labels(labels_path, [by_id[x] for x in answer_ids])
        print("\nsaved; rerun the same command to resume")
        return 0

    write_labels(labels_path, [by_id[x] for x in answer_ids])
    done = sum(
        1 for aid in answer_ids if (by_id[aid].get("label") or "").strip() in {"0", "1"}
    )
    print()
    print(f"{done}/{len(answer_ids)} labeled")
    if done == len(answer_ids):
        print("all done; run: .venv-pre/bin/python -I tools/score_review.py")
    else:
        print("rerun the same command to resume")
    return 0


if __name__ == "__main__":
    sys.exit(main())