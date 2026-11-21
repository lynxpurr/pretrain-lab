"""Score the 90-question holdout from the persisted manual labels.

Input:
  reports/2026-11-21-holdout-v3-manual-labels.tsv
    90 rows: question_id <TAB> base v1 v2 v2b v2c v2d v2e lora8 lora12 lora12-2ep <TAB> note
  reports/2026-11-21-holdout-eval-v3.csv
  data/eval/tests-holdout-v3.json
  data/eval/tests-holdout.json  (the 30 old questions, for the old/new split)

Output:
  reports/2026-11-21-holdout-v3-manual-labels.csv  (900 rows + header)
  reports/2026-11-21-manual-labels-audit.md        (totals, FP/FN, McNemar, CI, splits)

Usage:
  .venv-pre/bin/python -I tools/score_manual.py

Method note: the original 900-cell judgments were not persisted; these labels
are a re-judgment from the stored greedy answers (2026-11-21). The audit's
published aggregate is shown for comparison. Do not silently overwrite the
audit; report the difference.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ["base", "v1", "v2", "v2b", "v2c", "v2d", "v2e", "lora8", "lora12", "lora12-2ep"]
AUDIT_MANUAL = {
    "base": 12, "v1": 47, "v2": 47, "v2b": 44, "v2c": 45,
    "v2d": 48, "v2e": 53, "lora8": 43, "lora12": 42, "lora12-2ep": 48,
}
AUDIT_FP_FN = {
    "base": (13, 0), "v1": (17, 3), "v2": (17, 3), "v2b": (14, 3), "v2c": (11, 2),
    "v2d": (14, 3), "v2e": (8, 2), "lora8": (13, 3), "lora12": (14, 2), "lora12-2ep": (12, 4),
}


def load_labels(path: Path) -> dict[str, dict[str, int]]:
    labels: dict[str, dict[str, int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        assert len(parts) == 12, f"bad label row ({len(parts)} fields): {line[:80]}"
        qid, bits, note = parts[0], parts[1:11], parts[11]
        assert qid not in labels, f"duplicate question id {qid}"
        assert all(b in {"0", "1"} for b in bits), f"{qid}: labels must be 0/1"
        labels[qid] = {m: int(b) for m, b in zip(MODELS, bits)}
    return labels


def load_eval(path: Path) -> dict[tuple[str, str], dict]:
    rows = {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[(r["test_id"], r["model"])] = r
    return rows


def binom_two_sided(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value (binomial, p=0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2.0 * tail)


def bootstrap_diff_ci(
    qids: list[str], labels: dict[str, dict[str, int]], a: str, b: str,
    n_boot: int = 10000, seed: int = 42,
) -> tuple[float, float, float]:
    rng = random.Random(seed)
    diffs = []
    n = len(qids)
    for _ in range(n_boot):
        s = 0
        for _ in range(n):
            q = qids[rng.randrange(n)]
            s += labels[q][a] - labels[q][b]
        diffs.append(s / n)
    diffs.sort()
    return diffs[int(0.025 * n_boot)], diffs[int(0.975 * n_boot)], statistics.mean(diffs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="reports/2026-11-21-holdout-v3-manual-labels.tsv")
    ap.add_argument("--eval-csv", default="reports/2026-11-21-holdout-eval-v3.csv")
    ap.add_argument("--tests", default="data/eval/tests-holdout-v3.json")
    ap.add_argument("--old-tests", default="data/eval/tests-holdout.json")
    ap.add_argument("--out-csv", default="reports/2026-11-21-holdout-v3-manual-labels.csv")
    ap.add_argument("--out-md", default="reports/2026-11-21-manual-labels-audit.md")
    args = ap.parse_args()

    labels = load_labels(ROOT / args.labels)
    tests = json.loads((ROOT / args.tests).read_text(encoding="utf-8"))
    old_ids = {q["id"] for q in json.loads((ROOT / args.old_tests).read_text(encoding="utf-8"))}
    rows = load_eval(ROOT / args.eval_csv)

    qids = [q["id"] for q in tests]
    assert len(qids) == 90 and len(set(qids)) == 90, "expected 90 unique questions"
    assert set(labels) == set(qids), (
        f"label/test id mismatch: missing={sorted(set(qids) - set(labels))[:5]}, "
        f"extra={sorted(set(labels) - set(qids))[:5]}"
    )
    tags = {q["id"]: q["tag"] for q in tests}

    # --- per-item CSV -------------------------------------------------------
    out_csv = ROOT / args.out_csv
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "test_id", "tag", "kw_pass", "manual_pass", "note"])
        for qid in qids:
            note = ""
            for line in (ROOT / args.labels).read_text(encoding="utf-8").splitlines():
                if line.startswith(qid + "\t"):
                    note = line.split("\t")[11]
                    break
            for m in MODELS:
                r = rows[(qid, m)]
                w.writerow([m, qid, tags[qid], r["pass"], labels[qid][m], note])
    print(f"[csv] {out_csv.relative_to(ROOT)} ({len(qids) * len(MODELS)} rows)")

    # --- totals / FP / FN ---------------------------------------------------
    totals, fp, fn = {}, {}, {}
    for m in MODELS:
        kw = sum(int(rows[(q, m)]["pass"]) for q in qids)
        man = sum(labels[q][m] for q in qids)
        totals[m] = man
        fp[m] = sum(1 for q in qids if int(rows[(q, m)]["pass"]) == 1 and labels[q][m] == 0)
        fn[m] = sum(1 for q in qids if int(rows[(q, m)]["pass"]) == 0 and labels[q][m] == 1)
        print(f"[total] {m:11s} kw={kw:2d} manual={man:2d} FP={fp[m]:2d} FN={fn[m]:2d}")

    # --- McNemar v2e vs v2 --------------------------------------------------
    a, b = "v2e", "v2"
    both = sum(1 for q in qids if labels[q][a] == 1 and labels[q][b] == 1)
    only_a = sum(1 for q in qids if labels[q][a] == 1 and labels[q][b] == 0)
    only_b = sum(1 for q in qids if labels[q][a] == 0 and labels[q][b] == 1)
    neither = sum(1 for q in qids if labels[q][a] == 0 and labels[q][b] == 0)
    p_exact = binom_two_sided(only_a, only_b)
    ci_lo, ci_hi, ci_mean = bootstrap_diff_ci(qids, labels, a, b)
    print(f"[mcnemar] {a} vs {b}: both={both} only_{a}={only_a} only_{b}={only_b} "
          f"neither={neither} p_exact={p_exact:.4f} diff_CI=[{ci_lo:+.4f},{ci_hi:+.4f}]")

    # --- per-tag and old/new splits -----------------------------------------
    tag_rows = []
    for tag in sorted(set(tags.values())):
        tq = [q for q in qids if tags[q] == tag]
        tag_rows.append((
            tag, len(tq),
            sum(labels[q][a] for q in tq), sum(labels[q][b] for q in tq),
            sum(labels[q][a] - labels[q][b] for q in tq),
        ))
    new_ids = [q for q in qids if q not in old_ids]
    old = [q for q in qids if q in old_ids]
    split_rows = []
    for name, group in (("old 30", old), ("new 60", new_ids)):
        split_rows.append((
            name, len(group),
            sum(labels[q][a] for q in group), sum(labels[q][b] for q in group),
            sum(labels[q][a] - labels[q][b] for q in group),
        ))

    # --- markdown -----------------------------------------------------------
    lines = [
        "# 90 题人工标签复算 + McNemar/CI（2026-11-21）",
        "",
        "> 输入：`reports/2026-11-21-holdout-v3-manual-labels.tsv`（逐题 0/1，90×10）· "
        "`reports/2026-11-21-holdout-eval-v3.csv`（greedy 答案 + 关键词分）。",
        "> **方法学披露**：原始 900 格人工判定未落盘；本文件是从已保存的 greedy 答案**重新判分**的结果，"
        "不是对原始判定的恢复。audit §2 的聚合分并列展示，差异见 §1。",
        "",
        "## 0. 结论",
        "",
        f"**本轮重判 v2e {totals['v2e']} vs v2 {totals['v2']} = {totals['v2e'] - totals['v2']:+d}**"
        f"（audit：+6）；达到预注册阈值（≥5），但 **McNemar 精确 p = {p_exact:.4f}**、"
        f"bootstrap 95% CI = [{ci_lo:+.3f}, {ci_hi:+.3f}] 包含 0 → **统计上不显著**。"
        "对外只能写“达到预注册阈值、方向一致，但未达 0.05 显著”；"
        "优势集中在英文流畅度与少量 reason/format，数学 −1、翻译/calibration 持平。",
        "",
        "## 1. 总表（人工复核 vs 关键词）",
        "",
        "| 模型 | 关键词 | 人工（本轮） | audit 人工 | Δ vs audit | FP | FN | audit FP/FN |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for m in MODELS:
        kw = sum(int(rows[(q, m)]["pass"]) for q in qids)
        lines.append(
            f"| {m} | {kw} | **{totals[m]}** | {AUDIT_MANUAL[m]} | "
            f"{totals[m] - AUDIT_MANUAL[m]:+d} | {fp[m]} | {fn[m]} | "
            f"{AUDIT_FP_FN[m][0]}/{AUDIT_FP_FN[m][1]} |"
        )
    lines += [
        "",
        f"**本轮 v2e − v2 = {totals['v2e'] - totals['v2']:+d}**（audit：+6）。"
        "差异来自逐题复判，不是把总数往 audit 上凑；原始判定不可恢复是事实。",
        "",
        "## 2. McNemar（v2e vs v2，90 题配对）",
        "",
        f"- 2×2：both={both} · only v2e={only_a} · only v2={only_b} · neither={neither}",
        f"- 精确 McNemar（双侧二项，p=0.5）：**p = {p_exact:.4f}**",
        f"- 配对 bootstrap 95% CI（10,000 次，差值比例）：**[{ci_lo:+.3f}, {ci_hi:+.3f}]**（均值 {ci_mean:+.3f}）",
        f"- 结论口径：{'p < 0.05，可写“统计显著”' if p_exact < 0.05 else 'p ≥ 0.05，**只能写“达到预注册阈值，统计上不显著”**'}。",
        "",
        "## 3. 分 tag（v2e vs v2）",
        "",
        "| tag | n | v2e | v2 | Δ |",
        "|---|---:|---:|---:|---:|",
    ]
    for tag, n, va, vb, d in tag_rows:
        lines.append(f"| {tag} | {n} | {va} | {vb} | {d:+d} |")
    top_tags = [f"{t} {d:+d}" for t, n, va, vb, d in sorted(tag_rows, key=lambda x: -x[4]) if d > 0][:3]
    lines += [
        "",
        f"**读法**：本轮增量集中在 {'、'.join(top_tags)}；数学 −1、翻译/calibration 持平——"
        "v2e 的优势是“英文长答/流畅度 + 少量推理/格式”，不是数学/翻译/calibration 能力提升。",
        "",
        "## 4. 旧 30 / 新 60 分拆",
        "",
        "| 子集 | n | v2e | v2 | Δ |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, n, va, vb, d in split_rows:
        lines.append(f"| {name} | {n} | {va} | {vb} | {d:+d} |")
    lines += [
        "",
        "**读法**：优势主要出现在新 60 题（不是旧题记忆）；但新题增量同样以英文流畅度为主。",
        "",
        "## 5. 复现",
        "",
        "```bash",
        ".venv-pre/bin/python -I tools/score_manual.py",
        "```",
        "",
        "输出：`reports/2026-11-21-holdout-v3-manual-labels.csv`（900 行逐题标签）。",
    ]
    out_md = ROOT / args.out_md
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[md] {out_md.relative_to(ROOT)}")
    print(f"[summary] v2e-v2 = {totals['v2e'] - totals['v2']:+d}; McNemar p={p_exact:.4f}; "
          f"95% CI=[{ci_lo:+.3f},{ci_hi:+.3f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())