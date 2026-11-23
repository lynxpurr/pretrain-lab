#!/usr/bin/env python3
"""Build the v2g capability-block review kit (20 questions: translate 14 + calibration 6).

Two answers per question — v2e (baseline) and v2g (candidate) — with A/B order
randomized per question using a fixed seed. Output goes to review/v2g/
(gitignored):

    README.md    rubric card + how to fill
    kit.csv      answer_id,question_id,tag,prompt,answer   (blinded)
    labels.csv   answer_id,label,note                      (reviewer fills 0/1)
    .key.csv     answer_id,model,test_id,tag,greedy_pass   (do not open before labeling)

Why this subset: translation and calibration are the two blocks v2g targets,
and they carry the frozen acceptance criteria (AC7). Having the reviewer score
both models' answers on the same 20 questions gives a paired, blinded read of
the change instead of a same-agent comparison.

Run from the repository root:
    python -I tools/build_v2g_review_kit.py \
        --v2e-csv reports/2026-11-21-holdout-eval-v3.csv \
        --v2g-csv reports/2026-11-23-v2g-holdout-eval.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

TESTS = Path("data/eval/tests-holdout-v3.json")
BLOCKS = ("translate", "calibration")
SEED = 20261123


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v2e-csv", default="reports/2026-11-21-holdout-eval-v3.csv")
    ap.add_argument("--v2g-csv", default="reports/2026-11-23-v2g-holdout-eval.csv")
    ap.add_argument("--tests", default=str(TESTS))
    ap.add_argument("--out-dir", default="review/v2g")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    out = Path(args.out_dir)
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"[abort] {out} 已存在（--force 覆盖）")
        return 1
    out.mkdir(parents=True, exist_ok=True)

    tests = {t["id"]: t for t in json.loads(Path(args.tests).read_text(encoding="utf-8"))}
    rows_e = {(r["model"], r["test_id"]): r for r in read_csv(Path(args.v2e_csv))}
    rows_g = {(r["model"], r["test_id"]): r for r in read_csv(Path(args.v2g_csv))}

    qids = [tid for tid, t in tests.items() if t["tag"] in BLOCKS]
    missing = [q for q in qids if ("v2e", q) not in rows_e or ("v2g", q) not in rows_g]
    if missing:
        print(f"[abort] 缺少答案：{missing[:10]}")
        return 1
    print(f"[kit] {len(qids)} 题（translate {sum(tests[q]['tag']=='translate' for q in qids)} / "
          f"calibration {sum(tests[q]['tag']=='calibration' for q in qids)}）× 2 答案")

    rng = random.Random(SEED)
    kit, labels, key = [], [], []
    for qid in qids:
        t = tests[qid]
        pair = [("v2e", rows_e[("v2e", qid)]), ("v2g", rows_g[("v2g", qid)])]
        rng.shuffle(pair)
        for slot, (model, row) in zip(("A", "B"), pair):
            aid = f"{qid}-{slot}"
            ans = (row.get("answer") or "").strip()
            kit.append([aid, qid, t["tag"], t["prompt"], ans])
            labels.append([aid, "", ""])
            key.append([aid, model, qid, t["tag"], row.get("pass", "")])

    for name, header, data in (
        ("kit.csv", ["answer_id", "question_id", "tag", "prompt", "answer"], kit),
        ("labels.csv", ["answer_id", "label", "note"], labels),
        ("key.csv", ["answer_id", "model", "test_id", "tag", "greedy_pass"], key),
    ):
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(data)

    (out / "README.md").write_text(
        "# v2g capability review kit（20 题，40 条答案）\n\n"
        "**只标 `labels.csv`**：每条给 `0` 或 `1`，可写 note。不要打开 `key.csv`（揭盲后再看）。\n"
        "`kit.csv` 按题排好：同一题下 A/B 两条答案，顺序已随机，不告诉你哪条来自哪个模型。\n\n"
        "## 判定口径（严格 rubric，与 2026-11-22 第二复核一致）\n\n"
        "### 翻译（14 题：en→zh 7 / zh→en 7）\n"
        "- **1** = 译文语义正确且完整，方向正确，不添加原文没有的内容，不夹带原文/解释/客套话。\n"
        "- **0** = 错译、漏译、方向反、添加原文没有的信息、回声（原样返回源句）、拒答、乱码/复读。\n"
        "- 专名/习语只要语义正确即可算 1；拼写小错不扣分。\n\n"
        "### calibration（6 题：未来事件，2044/2046/2048/2050）\n"
        "- **1** = 承认该赛事在该年确实举办（年份与真实周期相符）+ 明确说结果尚未产生/无法确定 + 不编造。\n"
        "- **0** = 声称「{year} 年没有{event}」或说不举办、编造冠军/得主/城市、只拒答不解释、含糊其辞。\n"
        "- 注意：答「结果未定」是正确；答「没有这个世界杯/奥运会」是事实错误，记 0。\n\n"
        "## 标完以后\n\n"
        "告诉 agent 或运行 `python -I tools/score_v2g_review.py`，会输出按模型/能力块/方向的分数。\n",
        encoding="utf-8",
    )
    print(f"[done] {out}/README.md · kit.csv({len(kit)}) · labels.csv · key.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())