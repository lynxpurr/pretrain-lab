"""Print a compact per-question review sheet for the 90-question holdout.

Usage (from the repository root):
    .venv-pre/bin/python -I tools/review_holdout.py --start 0 --end 10
    .venv-pre/bin/python -I tools/review_holdout.py --start 10 --end 20 --max-chars 420

The output is designed for manual calibration: one block per question, with the
prompt, expected answers, and each model's greedy answer (truncated), plus the
keyword pass and rep-4. It does not modify anything.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "data" / "eval" / "tests-holdout-v3.json"
CSV = ROOT / "reports" / "2026-11-21-holdout-eval-v3.csv"
MODELS = ["base", "v1", "v2", "v2b", "v2c", "v2d", "v2e", "lora8", "lora12", "lora12-2ep"]


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.lower())


def compact(text: str, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 80] + " … " + text[-60:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=10)
    ap.add_argument("--max-chars", type=int, default=360)
    args = ap.parse_args()

    tests = json.loads(TESTS.read_text(encoding="utf-8"))
    rows: dict[tuple[str, str], dict] = {}
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["test_id"], r["model"])] = r

    for i in range(args.start, min(args.end, len(tests))):
        q = tests[i]
        print(f"\n### Q{i + 1:02d} {q['id']} [{q['tag']}]")
        print(f"prompt: {q['prompt']}")
        print(f"expect: {q['expect_any']}")
        np = norm(q["prompt"])
        for m in MODELS:
            r = rows[(q["id"], m)]
            ans = r["answer"]
            echo = "ECHO?" if np and np in norm(ans) else ""
            print(f"- {m:11s} K={r['pass']} rep4={r['rep4']:>5s} {echo:5s} | {compact(ans, args.max_chars)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())