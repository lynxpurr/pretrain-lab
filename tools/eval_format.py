"""eval_format.py — Day 7: 评测扩展（格式/方向/拒答 rubric），与 eval.py 的关键词分并列

为什么需要：关键词判分只测"是否提到"，v1 实测会高估质量——
  - `math-mul` 含 42 但长篇解释，违反"只回答数字"；
  - `translate-en2zh` 用英文回答，关键词仍可能命中；
  - `en-fluency` 触发 "I'm sorry, but I can't provide…" 拒答模板；
  - `refuse-unknown` 编造 1958/2028 细节，但答案里可能含"没有官方"。
本脚本读 `eval.py` 的 CSV（model,test_id,tag,pass,answer），对指定题加格式断言，
输出 md 表；**不改 eval.py 的关键词分**（Day 6 定档协议保持不变）。

用法：
  .venv-pre/bin/python -I tools/eval_format.py --csv reports/2026-11-19-day7-eval.csv \
      --out reports/2026-11-19-day7-eval-rubric.md
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

LIST_LINE = re.compile(r"^\s*(?:\d{1,2}[.、)）]|[一二三四五六七八九十]+[、.])\s*\S")
CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")


def count_list(answer: str) -> int:
    return sum(1 for ln in answer.splitlines() if LIST_LINE.match(ln))


def check(test_id: str, answer: str) -> tuple[bool | None, str]:
    a = answer.strip()
    a_clean = re.sub(r"[*_`#]", "", a).strip()  # 去 Markdown 加粗/代码标记
    if test_id == "math-add":
        ok = bool(re.search(r"(?<!\d)8(?!\d)", a_clean))
        return ok, "算术正确（8）" if ok else "算术错误"
    if test_id == "math-mul":
        # 算术与格式分开：math-mul 的题面要求"只回答数字"，纯数字才算格式通过；
        # 句子形式但含 42 记为"算术正确但含解释"（v2b 的形态）。
        pure = bool(re.fullmatch(r"(42|四十二)[。.!！]?", a_clean))
        arith = bool(re.search(r"(?<!\d)42(?!\d)", a_clean)) or "四十二" in a_clean
        return pure, ("纯数字 42" if pure else ("算术正确但含解释" if arith else "算术错误或非纯数字"))
    if test_id == "list-3":
        # CSV 把换行替换成空格，这里按"行内编号"计数（1. / 2. / 3.）
        nums = set(re.findall(r"(?:^|\s)([1-9])[.、)）]\s", a))
        return len(nums) >= 3, f"行内编号项 {len(nums)} 条"
    if test_id == "def-ml":
        ok = len(a) <= 80 and count_list(a) == 0 and a.count("。") <= 2
        return ok, f"长度 {len(a)} / 列表 {count_list(a)} / 句号 {a.count('。')}"
    if test_id == "translate-en2zh":
        cjk = len(CJK.findall(a)); latin = len(LATIN.findall(a))
        ok = cjk >= 4 and cjk >= latin
        return ok, f"中文 {cjk} / 拉丁 {latin}"
    if test_id == "en-fluency":
        refusal = any(s in a.lower() for s in ("i'm sorry", "i am sorry", "can't provide",
                                               "cannot provide", "can't help", "cannot help"))
        ok = len(LATIN.findall(a)) >= 20 and not refusal
        return ok, "英文正文" if ok else ("拒答模板" if refusal else "英文过短")
    if test_id == "refuse-unknown":
        # "没有"/"不存在"也是合法承认（v2 的正确回答 = "2027 年没有世界杯"，
        # 原关键词表只有 无法/不知道/尚未/不能/还没，会误判；编造检查仍保留）
        admit = any(k in a for k in ("无法", "不知道", "尚未", "不能", "还没", "不存在", "没有"))
        fabricated = any(k in a for k in ("1958", "2028"))
        ok = admit and not fabricated
        note = []
        if not admit: note.append("无承认不知道")
        if fabricated: note.append("编造年份")
        return ok, "、".join(note) or "承认不知道且无编造"
    if test_id == "fact-months":
        ok = ("12" in a or "十二" in a) and not any(k in a for k in ("春季", "夏季", "秋季", "冬季"))
        return ok, "12 且无季节编造" if ok else "含季节编造"
    return None, ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.csv).open(encoding="utf-8")))
    models = []
    for r in rows:
        if r["model"] not in models:
            models.append(r["model"])

    out = ["# 评测 rubric 扩展（格式 / 方向 / 拒答）", "",
           f"来源：`{args.csv}`（由 eval.py 生成；关键词分不变，本表为并列的规则断言）", ""]
    for model in models:
        sub = [r for r in rows if r["model"] == model]
        out += [f"## {model}", "", "| test | 关键词 | rubric | 说明 | 输出（截断 100 字） |",
                "|---|---|---|---|---|"]
        n_ok = n_total = 0
        for r in sub:
            ok, note = check(r["test_id"], r["answer"])
            if ok is None:
                continue
            n_total += 1
            n_ok += int(ok)
            out.append(f"| {r['test_id']} | {'✅' if r['pass'] == '1' else '❌'} | "
                       f"{'✅' if ok else '❌'} | {note} | {r['answer'][:100].replace('|', '\\|')} |")
        out += ["", f"**rubric 通过 {n_ok}/{n_total}**", ""]
    Path(args.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[done] {args.out}")


if __name__ == "__main__":
    main()