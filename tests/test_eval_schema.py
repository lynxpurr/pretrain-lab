"""Validate the evaluation sets: schema, counts, unique IDs, capability blocks.

Run from the repository root:
    python -I tests/test_eval_schema.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETS = {
    "data/eval/tests.json": 18,
    "data/eval/tests-holdout.json": 30,
    "data/eval/tests-holdout-v3.json": 90,
}


def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data, f"{path}: expected a non-empty list"
    return data


def main() -> int:
    all_ids: dict[str, set[str]] = {}
    for rel, expected_n in SETS.items():
        path = ROOT / rel
        assert path.exists(), f"missing {rel}"
        data = load(path)
        assert len(data) == expected_n, f"{rel}: {len(data)} questions, expected {expected_n}"
        ids: set[str] = set()
        for i, q in enumerate(data):
            assert isinstance(q, dict), f"{rel}[{i}]: not an object"
            for key in ("id", "prompt", "expect_any", "tag"):
                assert key in q, f"{rel}[{i}]: missing {key}"
            assert isinstance(q["id"], str) and q["id"], f"{rel}[{i}]: bad id"
            assert isinstance(q["prompt"], str) and q["prompt"].strip(), f"{rel}[{i}]: empty prompt"
            assert isinstance(q["expect_any"], list) and q["expect_any"], f"{rel}[{i}]: empty expect_any"
            assert all(isinstance(x, str) and x for x in q["expect_any"]), f"{rel}[{i}]: bad expect_any"
            assert isinstance(q["tag"], str) and q["tag"], f"{rel}[{i}]: bad tag"
            assert q["id"] not in ids, f"{rel}: duplicate id {q['id']}"
            ids.add(q["id"])
        all_ids[rel] = ids
        print(f"OK {rel}: {len(data)} questions, {len({q['tag'] for q in data})} tags")

    dev = all_ids["data/eval/tests.json"]
    h2 = all_ids["data/eval/tests-holdout.json"]
    h3 = all_ids["data/eval/tests-holdout-v3.json"]
    assert dev.isdisjoint(h3), f"dev/holdout v3 id overlap: {sorted(dev & h3)}"
    assert h2 <= h3, f"holdout v2 is not a subset of v3: {sorted(h2 - h3)}"

    v3 = load(ROOT / "data/eval/tests-holdout-v3.json")
    tags = {}
    for q in v3:
        tags[q["tag"]] = tags.get(q["tag"], 0) + 1
    assert tags.get("math", 0) >= 14, f"holdout v3 math block: {tags.get('math', 0)} < 14"
    assert tags.get("translate", 0) >= 14, f"holdout v3 translate block: {tags.get('translate', 0)} < 14"
    assert tags.get("calibration", 0) >= 6, f"holdout v3 calibration block: {tags.get('calibration', 0)} < 6"
    print("OK capability blocks:", {k: tags[k] for k in ("math", "translate", "calibration")})
    print(f"OK ids: unique within each set; dev disjoint from holdout v3; holdout v2 ⊆ v3 ({len(h2)} ⊆ {len(h3)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())