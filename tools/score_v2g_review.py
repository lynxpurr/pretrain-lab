#!/usr/bin/env python3
"""Score the v2g capability review kit (20 questions × 2 blinded answers).

Reads review/v2g/labels.csv (reviewer-filled 0/1) and review/v2g/.key.csv,
writes reports/<date>-v2g-capability-review.md plus a labels copy in reports/.

Reported per model: translation total, en→zh, zh→en, calibration; plus the
keyword (greedy) pass count for comparison. Missing/illegal labels abort.

Run from the repository root:
    python -I tools/score_v2g_review.py --reviewer "project owner (blind)"
"""
from __future__ import annotations

import argparse
import csv
import datetime
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def block_of(test_id: str, tag: str) -> str:
    if tag == "translate":
        if "en2zh" in test_id:
            return "translate_en2zh"
        if "zh2en" in test_id:
            return "translate_zh2en"
        return "translate"
    return tag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="review/v2g/labels.csv")
    ap.add_argument("--key", default="review/v2g/key.csv")
    ap.add_argument("--reviewer", default="project owner (blind capability-block review)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--out", default="")
    ap.add_argument("--csv-out", default="")
    args = ap.parse_args()

    labels = read_csv(Path(args.labels))
    key = {r["answer_id"]: r for r in read_csv(Path(args.key))}
    bad = [r["answer_id"] for r in labels if r.get("label", "").strip() not in ("0", "1")]
    if bad:
        print(f"[abort] 还有 {len(bad)} 条未标或标签非法：{bad[:8]}")
        return 1

    per_model: dict[str, dict[str, int]] = {}
    per_model_total: dict[str, int] = {}
    per_model_greedy: dict[str, int] = {}
    for r in labels:
        aid = r["answer_id"]
        k = key[aid]
        model, tag = k["model"], k["tag"]
        b = block_of(k["test_id"], tag)
        d = per_model.setdefault(model, {})
        d[b] = d.get(b, 0) + int(r["label"])
        per_model_total[model] = per_model_total.get(model, 0) + int(r["label"])
        per_model_greedy[model] = per_model_greedy.get(model, 0) + int(k.get("greedy_pass") or 0)

    n_q: dict[str, int] = {}
    qids_by_block: dict[str, set[str]] = {}
    for k in key.values():
        qids_by_block.setdefault(block_of(k["test_id"], k["tag"]), set()).add(k["test_id"])
    for b, s in qids_by_block.items():
        n_q[b] = len(s)
    lines = [
        f"# v2g capability-block review（{args.date}）",
        "",
        f"> Reviewer: **{args.reviewer}** · blinding: 每题 A/B 顺序随机（seed 20261123）· "
        f"rubric: 严格口径（见 `review/v2g/README.md`）· 证据: `reports/{args.date}-v2g-capability-labels.csv`",
        "",
        f"| 模型 | 翻译 总 ({n_q['translate_en2zh']+n_q['translate_zh2en']}) | "
        f"en→zh ({n_q['translate_en2zh']}) | zh→en ({n_q['translate_zh2en']}) | "
        f"calibration ({n_q['calibration']}) | 关键词分（同 20 题） |",
        "|---|---|---|---|---|---|",
    ]
    for model in ("v2e", "v2g"):
        d = per_model.get(model, {})
        tr = d.get("translate_en2zh", 0) + d.get("translate_zh2en", 0)
        lines.append(
            f"| {model} | **{tr}/{n_q['translate_en2zh']+n_q['translate_zh2en']}** | "
            f"{d.get('translate_en2zh', 0)}/{n_q['translate_en2zh']} | "
            f"{d.get('translate_zh2en', 0)}/{n_q['translate_zh2en']} | "
            f"**{d.get('calibration', 0)}/{n_q['calibration']}** | {per_model_greedy.get(model, 0)}/20 |"
        )

    lines += ["", "## 逐题（人工分 / 关键词分）", "", "| 题 | block | v2e | v2g |", "|---|---|---|---|"]
    by_q: dict[str, dict[str, int]] = {}
    for r in labels:
        k = key[r["answer_id"]]
        q = k["test_id"]
        by_q.setdefault(q, {"block": block_of(q, k["tag"])})[k["model"]] = int(r["label"])
    for q, v in by_q.items():
        lines.append(f"| {q} | {v['block']} | {v.get('v2e', '-')} | {v.get('v2g', '-')} |")

    out = Path(args.out or f"reports/{args.date}-v2g-capability-review.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    csv_out = Path(args.csv_out or f"reports/{args.date}-v2g-capability-labels.csv")
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["answer_id", "model", "test_id", "tag", "block", "label", "note"])
        for r in labels:
            k = key[r["answer_id"]]
            w.writerow([r["answer_id"], k["model"], k["test_id"], k["tag"],
                        block_of(k["test_id"], k["tag"]), r["label"], r.get("note", "")])
    print(f"[done] {out} · {csv_out}")
    for model in ("v2e", "v2g"):
        d = per_model.get(model, {})
        print(f"  {model}: translate {d.get('translate_en2zh',0)+d.get('translate_zh2en',0)}/{n_q['translate_en2zh']+n_q['translate_zh2en']} "
              f"(en2zh {d.get('translate_en2zh',0)}/{n_q['translate_en2zh']}, zh2en {d.get('translate_zh2en',0)}/{n_q['translate_zh2en']}) · "
              f"calibration {d.get('calibration',0)}/{n_q['calibration']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())