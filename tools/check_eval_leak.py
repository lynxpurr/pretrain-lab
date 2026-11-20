"""check_eval_leak.py — 评测集去重硬门（Day 11 沉淀，来自 v2e 评测污染 + Day 10 holdout 复核）

用途：在"造数据/建评测集"之后、跑评测之前，检查评测集 prompt 是否与训练补充样本
或 SFT 源数据撞车。撞车 = 指标退化为记忆测试（v2~v2d 的教训）。

检查三层（normalize 后双向包含）：
  1) 评测集 vs 评测集（多个 --eval 之间，防 dev/holdout 互相泄漏）
  2) 评测集 vs 补充样本（--extra-dir 下所有 jsonl 的 user 内容）
  3) 评测集 vs SFT 源（--sft-source 的 user 内容；逐行流式，905k 行约 1 min）

用法（仓根）：
  .venv-pre/bin/python -I tools/check_eval_leak.py \
    --eval data/eval/tests-holdout.json --eval data/eval/tests.json \
    --extra-dir data/sft-extra-v2 \
    --sft-source data/raw/minimind_dataset/sft_t2t_mini.jsonl
  # 退出码 0 = 0 撞车；1 = 有撞车（打印 id / 来源 / 片段）

  # 只查构造阶段（跳过大文件，秒级）：
  ... --eval data/eval/tests-holdout.json --extra-dir data/sft-extra-v2 --skip-sft-source
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def norm(s: str) -> str:
    return re.sub(r"[\s\W_]+", "", s.lower(), flags=re.UNICODE)


def load_eval(paths: list[str]) -> list[tuple[str, str, str]]:
    out = []
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        for x in data:
            out.append((x["id"], x["prompt"], p))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", action="append", required=True, help="评测集 json（可重复）")
    ap.add_argument("--extra-dir", default="data/sft-extra-v2", help="补充样本目录（jsonl）")
    ap.add_argument("--sft-source", default="", help="SFT 源 jsonl（可选，user 内容全量流式）")
    ap.add_argument("--skip-sft-source", action="store_true")
    args = ap.parse_args()

    evals = load_eval(args.eval)
    ev = [(i, norm(p), src) for i, p, src in evals]
    print(f"[eval] {len(ev)} 题 / {len(args.eval)} 个文件")

    hits = 0
    print("== 1) eval vs eval ==")
    for a in range(len(ev)):
        for b in range(a + 1, len(ev)):
            ia, ha, sa = ev[a]
            ib, hb, sb = ev[b]
            if ha and hb and (ha in hb or hb in ha):
                print(f"HIT {ia} ({sa}) <-> {ib} ({sb})")
                hits += 1
    print(f"hits: {hits}")

    if args.extra_dir:
        print("== 2) eval vs extras ==")
        n0 = hits
        for p in sorted(Path(args.extra_dir).glob("*.jsonl")):
            for line in p.open(encoding="utf-8"):
                obj = json.loads(line)
                for m in obj.get("conversations", []):
                    if m.get("role") != "user":
                        continue
                    u = norm(m.get("content", ""))
                    for i, h, _ in ev:
                        if h and (h in u or u in h):
                            print(f"HIT {i} {p.name}: {m['content'][:60]}")
                            hits += 1
        print(f"hits: {hits - n0}")

    if args.sft_source and not args.skip_sft_source:
        print(f"== 3) eval vs sft source ({args.sft_source}) ==")
        n0 = hits
        with open(args.sft_source, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                obj = json.loads(line)
                for m in obj.get("conversations", []):
                    if m.get("role") != "user":
                        continue
                    u = norm(m.get("content", ""))
                    for i, h, _ in ev:
                        if h and h in u:
                            print(f"HIT {i} line {lineno}: {m['content'][:60]}")
                            hits += 1
        print(f"hits: {hits - n0}")

    print(f"[result] total hits = {hits} → {'FAIL（先改数据/题库）' if hits else 'PASS（0 撞车）'}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())